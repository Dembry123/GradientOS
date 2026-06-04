"""Runtime bridge from HEBI Mobile I/O to GradientOS jog commands."""

from __future__ import annotations

import datetime
import json
import os
import time
from typing import Any

import numpy as np

from .gradient_jog_client import GradientJogApiClient
from .hebi_mobile_io_device import _create_mobile_io, _gripper_button_axis, _read_phone_pose
from .hebi_models import BridgeConfig, JogCommand, PhonePose, RobotToolPose, TargetDelta, _xyz_payload
from .phone_mapping import SpatialPhoneMapper


class HebiMobileIOBridge:
    """Runtime bridge from HEBI Mobile I/O to GradientOS jog commands."""

    def __init__(self, config: BridgeConfig) -> None:
        self.config = config
        self.mapper = SpatialPhoneMapper(config.mapping_config())
        self.client = GradientJogApiClient(
            config.api_host,
            timeout_s=config.request_timeout_s,
            dry_run=config.dry_run,
        )
        self.mobile_io = None
        self.enabled = False
        self.last_pose: PhonePose | None = None
        self.last_robot_pose: RobotToolPose | None = None
        self.last_robot_pose_poll = 0.0
        self.last_robot_pose_log = 0.0
        self.next_reconnect_attempt = 0.0
        self.last_reconnect_log = 0.0
        self.phone_pose_reference: PhonePose | None = None
        self.phone_pose_sequence = 0
        self.last_phone_pose_publish = 0.0
        self.last_phone_pose_publish_log = 0.0
        self.phone_pose_publish_suppressed_until = 0.0
        self.last_diagnostic_log = 0.0
        self.diagnostic_log_count = 0
        self.diagnostic_log_handle = None

    def _close_diagnostic_log(self) -> None:
        if self.diagnostic_log_handle is not None:
            try:
                self.diagnostic_log_handle.flush()
                self.diagnostic_log_handle.close()
            except Exception:
                pass
        self.diagnostic_log_handle = None

    def _diagnostic_log_file(self):
        if self.diagnostic_log_handle is not None:
            return self.diagnostic_log_handle
        path = self.config.diagnostic_log_path
        if path is None:
            os.makedirs("diagnostics/jog_motion", exist_ok=True)
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join("diagnostics", "jog_motion", f"phone_bridge_{stamp}.jsonl")
        else:
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
        self.config.diagnostic_log_path = path
        self.diagnostic_log_handle = open(path, "a", buffering=8192)
        print(f"[teleop] diagnostic JSONL log -> {path}")
        return self.diagnostic_log_handle

    def _write_diagnostic_log(self, payload: dict[str, Any], *, now: float, force: bool = False) -> None:
        if not self.config.diagnostic_log:
            return
        interval = max(0.0, self.config.diagnostic_log_interval_s)
        if not force and now - self.last_diagnostic_log < interval:
            return
        self.last_diagnostic_log = now
        try:
            handle = self._diagnostic_log_file()
            handle.write(json.dumps(payload, separators=(",", ":")) + "\n")
            self.diagnostic_log_count += 1
            if force or self.diagnostic_log_count % 50 == 0:
                handle.flush()
        except Exception as exc:
            if now - self.last_phone_pose_publish_log >= self.config.log_interval_s:
                print(f"[teleop] diagnostic log skipped: {exc}")
                self.last_phone_pose_publish_log = now

    def connect(self, *, announce_mode: bool = True) -> None:
        self.mobile_io = _create_mobile_io(self.config)
        print(
            "[HEBI] Connected to Mobile I/O "
            f"family={self.config.family!r} name={self.config.name!r}."
        )
        if announce_mode:
            if self.config.dry_run:
                print("[GradientOS] Dry-run mode: no robot motion will be sent. Use --live to command the API.")
            else:
                print(f"[GradientOS] Live mode: sending jog commands to {self.config.api_host}.")

    def _poll_robot_pose(
        self,
        *,
        force: bool = False,
        now: float | None = None,
    ) -> RobotToolPose | None:
        if self.config.dry_run:
            return None

        sample_time = time.monotonic() if now is None else now
        interval = max(0.0, self.config.robot_pose_poll_interval_s)
        if (
            not force
            and self.last_robot_pose is not None
            and sample_time - self.last_robot_pose_poll < interval
        ):
            return self.last_robot_pose

        self.last_robot_pose_poll = sample_time
        try:
            pose = self.client.get_tool_pose()
        except Exception as exc:
            if sample_time - self.last_robot_pose_log >= self.config.log_interval_s:
                print(f"[GradientOS] Could not read /info/pose; using estimated teleop delta: {exc}")
                self.last_robot_pose_log = sample_time
            return self.last_robot_pose

        if pose is not None:
            self.last_robot_pose = pose
        return self.last_robot_pose

    def _try_reconnect(self, now: float) -> bool:
        if not self.config.auto_reconnect or now < self.next_reconnect_attempt:
            return False

        self.next_reconnect_attempt = now + max(0.1, self.config.reconnect_interval_s)
        try:
            self.connect(announce_mode=False)
        except Exception as exc:
            if now - self.last_reconnect_log >= self.config.log_interval_s:
                print(f"[HEBI] Waiting to reconnect Mobile I/O: {exc}")
                self.last_reconnect_log = now
            return False

        self.enabled = False
        self.last_pose = None
        self.last_robot_pose = None
        self.last_robot_pose_poll = 0.0
        return True

    def _publish_phone_pose(
        self,
        pose: PhonePose,
        *,
        now: float,
        enabled: bool,
        target: TargetDelta | None = None,
        target_pose: RobotToolPose | None = None,
        visual_pose: RobotToolPose | None = None,
        command: JogCommand | None = None,
    ) -> None:
        if not self.config.publish_phone_pose:
            return
        if now < self.phone_pose_publish_suppressed_until:
            return

        interval = max(0.0, self.config.phone_pose_publish_interval_s)
        if now - self.last_phone_pose_publish < interval:
            return
        self.last_phone_pose_publish = now

        if self.phone_pose_reference is None:
            self.phone_pose_reference = pose
        reference = self.phone_pose_reference
        self.phone_pose_sequence += 1

        payload = {
            "source": "hebi_mobile_io",
            "sequence": self.phone_pose_sequence,
            "enabled": enabled,
            **pose.as_debug_payload(),
            "reference_position_m": _xyz_payload(reference.position_m),
            "delta_m": _xyz_payload(pose.position_m - reference.position_m),
        }
        if target is not None:
            payload["target_linear_m"] = _xyz_payload(target.linear_m)
            payload["target_angular_deg"] = _xyz_payload(target.angular_deg)
        if visual_pose is not None:
            visual_quat = visual_pose.orientation.as_quat()
            visual_euler_deg = visual_pose.orientation.as_euler("xyz", degrees=True)
            payload["visual_position_m"] = _xyz_payload(visual_pose.position_m)
            payload["visual_orientation_quat_xyzw"] = {
                "x": float(visual_quat[0]),
                "y": float(visual_quat[1]),
                "z": float(visual_quat[2]),
                "w": float(visual_quat[3]),
            }
            payload["visual_orientation_euler_deg"] = _xyz_payload(visual_euler_deg)
        if target_pose is not None:
            target_quat = target_pose.orientation.as_quat()
            target_euler_deg = target_pose.orientation.as_euler("xyz", degrees=True)
            payload["target_position_m"] = _xyz_payload(target_pose.position_m)
            payload["target_orientation_quat_xyzw"] = {
                "x": float(target_quat[0]),
                "y": float(target_quat[1]),
                "z": float(target_quat[2]),
                "w": float(target_quat[3]),
            }
            payload["target_orientation_euler_deg"] = _xyz_payload(target_euler_deg)
        if command is not None:
            payload["command_linear_m_s"] = _xyz_payload(command.linear_m_s)
            payload["command_angular_deg_s"] = _xyz_payload(command.angular_deg_s)

        self._write_diagnostic_log(payload, now=now)

        try:
            self.client.post_diagnostic("/teleop/phone-pose", payload)
        except Exception as exc:
            self.phone_pose_publish_suppressed_until = now + max(0.5, self.config.log_interval_s)
            if now - self.last_phone_pose_publish_log >= self.config.log_interval_s:
                print(f"[teleop] phone pose visualization publish skipped: {exc}")
                self.last_phone_pose_publish_log = now

    def _release(self) -> None:
        if not self.enabled:
            return
        print("[teleop] release: deadman false, zero velocity, stop jog")
        errors: list[str] = []
        try:
            release_steps = [
                ("deadman false", lambda: self.client.set_deadman(False)),
                ("zero velocity", self.client.zero),
            ]
            if self.config.stop_on_release:
                release_steps.append(("jog stop", self.client.stop))
            for label, action in release_steps:
                try:
                    action()
                except Exception as exc:
                    errors.append(f"{label}: {exc}")
        finally:
            self.enabled = False
            self.last_pose = None
        if errors:
            print(f"[teleop] release warnings: {'; '.join(errors)}")

    def _enable(self, pose: PhonePose, now: float) -> bool:
        robot_pose = self._poll_robot_pose(force=True, now=now)
        if not self.config.dry_run and robot_pose is None:
            if now - self.last_robot_pose_log >= self.config.log_interval_s:
                print("[teleop] waiting for GradientOS /info/pose before enabling")
                self.last_robot_pose_log = now
            return False

        print("[teleop] enable: latching phone pose, robot pose, and starting jog")
        self.mapper.reset(pose, reference_robot_pose=robot_pose)
        self.phone_pose_reference = pose
        self.client.start()
        self.client.zero()
        self.client.set_deadman(True)
        self.enabled = True
        self.last_pose = pose
        return True

    def run(self) -> int:
        self.connect()
        period = self.config.period_s
        last_loop = time.monotonic()
        last_feedback = last_loop
        last_log = 0.0

        try:
            while True:
                loop_start = time.monotonic()
                dt = loop_start - last_loop
                last_loop = loop_start

                if self.mobile_io is None:
                    if self._try_reconnect(loop_start):
                        last_feedback = loop_start
                    elapsed = time.monotonic() - loop_start
                    if elapsed < period:
                        time.sleep(period - elapsed)
                    continue

                mobile_io = self.mobile_io
                try:
                    got_feedback = bool(mobile_io.update(timeout_ms=0))
                except Exception as exc:
                    print(f"[HEBI] Mobile I/O update failed; releasing and reconnecting: {exc}")
                    self._release()
                    self.mobile_io = None
                    self.next_reconnect_attempt = loop_start
                    continue

                if got_feedback:
                    last_feedback = loop_start
                    if mobile_io.get_button_state(self.config.quit_button):
                        print("[teleop] quit button pressed")
                        break
                    pose = _read_phone_pose(mobile_io, self.config)
                    if pose is not None:
                        self.last_pose = pose

                feedback_age = loop_start - last_feedback
                stale = feedback_age > self.config.stale_timeout_s
                if stale and self.enabled:
                    print(f"[teleop] feedback stale for {feedback_age:.2f}s; releasing deadman")
                    self._release()
                if stale and self.config.auto_reconnect and feedback_age >= self.config.reconnect_after_stale_s:
                    print(f"[HEBI] Feedback stale for {feedback_age:.2f}s; scanning for Mobile I/O again")
                    self._release()
                    self.mobile_io = None
                    self.next_reconnect_attempt = loop_start
                    continue

                enable_held = bool(mobile_io.get_button_state(self.config.enable_button)) and not stale
                if self.last_pose is not None and not (enable_held and self.enabled):
                    self._publish_phone_pose(
                        self.last_pose,
                        now=loop_start,
                        enabled=enable_held,
                    )
                if enable_held:
                    if self.last_pose is None:
                        if loop_start - last_log >= self.config.log_interval_s:
                            print("[teleop] waiting for valid ARKit pose from Mobile I/O")
                            last_log = loop_start
                    elif not self.enabled:
                        self._enable(self.last_pose, loop_start)
                    else:
                        axis_value = float(mobile_io.get_axis_state(self.config.gripper_axis))
                        button_axis_value = _gripper_button_axis(mobile_io, self.config)
                        if button_axis_value != 0.0:
                            axis_value = button_axis_value
                        robot_pose = self._poll_robot_pose(now=loop_start)
                        target = self.mapper.target_delta(self.last_pose)
                        target_pose = self.mapper.target_tool_pose_from_delta(target)
                        visual_pose = self.mapper.visual_tool_pose_from_phone(self.last_pose)
                        command = self.mapper.command_for_pose(
                            self.last_pose,
                            dt_s=dt,
                            gripper_axis_value=axis_value,
                            robot_pose=robot_pose,
                        )
                        self._publish_phone_pose(
                            self.last_pose,
                            now=loop_start,
                            enabled=True,
                            target=target,
                            target_pose=target_pose,
                            visual_pose=visual_pose,
                            command=command,
                        )
                        self.client.set_deadman(True)
                        self.client.send_velocity(command)
                        self.client.send_gripper_velocity(command)
                        if loop_start - last_log >= self.config.log_interval_s:
                            print(
                                "[teleop] cmd "
                                f"lin={np.round(command.linear_m_s, 4)} m/s "
                                f"ang={np.round(command.angular_deg_s, 1)} deg/s "
                                f"grip={command.gripper_deg_s:.1f} deg/s"
                            )
                            last_log = loop_start
                elif self.enabled:
                    self._release()

                elapsed = time.monotonic() - loop_start
                if elapsed < period:
                    time.sleep(period - elapsed)
        except KeyboardInterrupt:
            print("\n[teleop] interrupted")
        finally:
            self._release()
            self._close_diagnostic_log()
            self.client.close()
        return 0
