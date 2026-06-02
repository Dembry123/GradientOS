"""HEBI Mobile I/O to GradientOS realtime jog bridge.

This module follows LeRobot's phone-teleop pattern for iOS:

* HEBI Mobile I/O supplies ARKit pose plus B/A channel controls.
* B1 is the deadman/enable input.
* B2 opens the gripper, B4 closes it, and A3 can still act as a velocity-like gripper input.
* GradientOS remains the motion authority through the existing jog API.

The CLI defaults to dry-run mode so phone discovery and mapping can be tested
before sending any motion command to hardware. Pass ``--live`` to command the
configured GradientOS API.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np
import requests
from scipy.spatial.transform import Rotation as R


QuaternionOrder = Literal["wxyz", "xyzw"]


def _vector3(value: Any, name: str) -> np.ndarray:
    arr = np.asarray(value, dtype=float).reshape(-1)
    if arr.size != 3:
        raise ValueError(f"{name} must contain 3 values, got {arr.size}")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains non-finite values")
    return arr.astype(float)


def _rotation_from_quaternion(value: Any, order: QuaternionOrder) -> R:
    arr = np.asarray(value, dtype=float).reshape(-1)
    if arr.size != 4:
        raise ValueError(f"orientation must contain 4 values, got {arr.size}")
    if not np.all(np.isfinite(arr)):
        raise ValueError("orientation contains non-finite values")
    if order == "wxyz":
        quat_xyzw = np.array([arr[1], arr[2], arr[3], arr[0]], dtype=float)
    else:
        quat_xyzw = arr.astype(float)
    norm = float(np.linalg.norm(quat_xyzw))
    if norm <= 1e-9:
        raise ValueError("orientation quaternion norm is zero")
    return R.from_quat(quat_xyzw / norm)


def _clip_vector_norm(values: np.ndarray, max_norm: float) -> np.ndarray:
    if max_norm <= 0:
        return np.zeros_like(values)
    norm = float(np.linalg.norm(values))
    if norm <= max_norm or norm <= 1e-12:
        return values
    return values * (max_norm / norm)


def _clip_target_vector_norm(values: np.ndarray, max_norm: float) -> np.ndarray:
    if not np.isfinite(max_norm) or max_norm <= 0:
        return values
    return _clip_vector_norm(values, max_norm)


def _deadzone(value: float, threshold: float) -> float:
    if abs(value) <= threshold:
        return 0.0
    return value


def _deadzone_vector_norm(values: np.ndarray, threshold: float) -> np.ndarray:
    if threshold <= 0:
        return values
    norm = float(np.linalg.norm(values))
    if norm <= threshold:
        return np.zeros_like(values)
    if norm <= 1e-12:
        return values
    return values * ((norm - threshold) / norm)


def _xyz_payload(values: np.ndarray) -> dict[str, float]:
    return {
        "x": float(values[0]),
        "y": float(values[1]),
        "z": float(values[2]),
    }


def _axis_map_matrix(spec: str) -> np.ndarray:
    """Return matrix mapping phone-local xyz components into robot xyz components."""
    compact = spec.strip().lower().replace(" ", "")
    if "," in compact:
        tokens = compact.split(",")
    else:
        tokens = list(compact)
    if len(tokens) != 3:
        raise ValueError("phone axis map must specify three output axes, e.g. 'y,-x,z'")

    matrix = np.zeros((3, 3), dtype=float)
    used_axes: set[str] = set()
    axis_index = {"x": 0, "y": 1, "z": 2}
    for out_index, token in enumerate(tokens):
        if not token:
            raise ValueError("phone axis map contains an empty axis token")
        sign = 1.0
        if token[0] in ("+", "-"):
            sign = -1.0 if token[0] == "-" else 1.0
            token = token[1:]
        if token not in axis_index:
            raise ValueError(f"phone axis map token must be x, y, or z; got {token!r}")
        if token in used_axes:
            raise ValueError(f"phone axis map reuses phone axis {token!r}")
        used_axes.add(token)
        matrix[out_index, axis_index[token]] = sign
    return matrix


@dataclass(frozen=True)
class PhonePose:
    """ARKit phone pose sampled from HEBI Mobile I/O."""

    position_m: np.ndarray
    orientation: R

    @classmethod
    def from_hebi(
        cls,
        position: Any,
        orientation: Any,
        *,
        quaternion_order: QuaternionOrder = "wxyz",
    ) -> "PhonePose":
        return cls(
            position_m=_vector3(position, "position"),
            orientation=_rotation_from_quaternion(orientation, quaternion_order),
        )

    def as_debug_payload(self) -> dict[str, Any]:
        quat = self.orientation.as_quat()
        euler_deg = self.orientation.as_euler("xyz", degrees=True)
        return {
            "position_m": _xyz_payload(self.position_m),
            "orientation_quat_xyzw": {
                "x": float(quat[0]),
                "y": float(quat[1]),
                "z": float(quat[2]),
                "w": float(quat[3]),
            },
            "orientation_euler_deg": _xyz_payload(euler_deg),
        }


@dataclass(frozen=True)
class RobotToolPose:
    """GradientOS tool pose sampled from the API."""

    position_m: np.ndarray
    orientation: R

    @classmethod
    def from_api_payload(cls, payload: dict[str, Any]) -> "RobotToolPose":
        try:
            position = payload["position_m"]
            orientation = payload["orientation_euler_deg"]
            position_xyz = [position["x"], position["y"], position["z"]]
            euler_xyz_deg = [orientation["roll"], orientation["pitch"], orientation["yaw"]]
        except (KeyError, TypeError) as exc:
            raise ValueError(f"Malformed /info/pose payload: {payload!r}") from exc

        return cls(
            position_m=_vector3(position_xyz, "position_m"),
            orientation=R.from_euler(
                "xyz",
                _vector3(euler_xyz_deg, "orientation_euler_deg"),
                degrees=True,
            ),
        )


@dataclass(frozen=True)
class TargetDelta:
    """Desired robot-space end-effector delta relative to the hold start pose."""

    linear_m: np.ndarray
    angular_deg: np.ndarray


@dataclass
class BridgeConfig:
    api_host: str = "http://127.0.0.1:4000"
    family: str = "HEBI"
    name: str = "mobileIO"
    rate_hz: float = 25.0
    lookup_wait_s: float = 1.0
    stale_timeout_s: float = 0.35
    request_timeout_s: float = 0.45
    enable_button: int = 1
    quit_button: int = 8
    gripper_open_button: int = 2
    gripper_close_button: int = 4
    gripper_axis: int = 3
    axis_deadzone: float = 0.08
    translation_scale: float = 1.0
    rotation_scale: float = 1.0
    phone_axis_map: str = "y,-x,z"
    invert_x: bool = False
    invert_y: bool = False
    invert_z: bool = False
    invert_roll: bool = False
    invert_pitch: bool = False
    invert_yaw: bool = False
    linear_kp: float = 3.0
    angular_kp: float = 4.0
    linear_deadband_m: float = 0.004
    angular_deadband_deg: float = 0.75
    max_target_offset_m: float = float("inf")
    max_target_rotation_deg: float = float("inf")
    max_linear_m_s: float = 0.08
    max_angular_deg_s: float = 45.0
    max_gripper_deg_s: float = 45.0
    filter_alpha: float = 0.35
    quaternion_order: QuaternionOrder = "wxyz"
    dry_run: bool = True
    stop_on_release: bool = True
    robot_pose_poll_interval_s: float = 0.08
    publish_phone_pose: bool = True
    phone_pose_publish_interval_s: float = 0.05
    auto_reconnect: bool = True
    reconnect_interval_s: float = 1.0
    reconnect_after_stale_s: float = 1.5
    calibrate_phone_frame: bool = False
    setup_mobile_ui: bool = False
    list_devices: bool = False
    log_interval_s: float = 1.0
    diagnostic_log: bool = False
    diagnostic_log_interval_s: float = 0.1
    diagnostic_log_path: str | None = None

    @property
    def period_s(self) -> float:
        return 1.0 / max(1.0, self.rate_hz)


@dataclass
class JogCommand:
    linear_m_s: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=float))
    angular_deg_s: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=float))
    gripper_deg_s: float = 0.0

    def as_payload(self) -> dict[str, float]:
        return {
            "vx": float(self.linear_m_s[0]),
            "vy": float(self.linear_m_s[1]),
            "vz": float(self.linear_m_s[2]),
            "v_roll": float(self.angular_deg_s[0]),
            "v_pitch": float(self.angular_deg_s[1]),
            "v_yaw": float(self.angular_deg_s[2]),
        }


class SpatialPhoneMapper:
    """Maps ARKit pose deltas to bounded GradientOS jog velocity commands."""

    def __init__(self, config: BridgeConfig) -> None:
        self.config = config
        self.reference_pose: PhonePose | None = None
        self.reference_robot_pose: RobotToolPose | None = None
        self.orientation_reference_pose: PhonePose | None = None
        self.orientation_reference_robot_pose: RobotToolPose | None = None
        self.phone_to_robot_orientation: R | None = None
        self.axis_map_matrix = _axis_map_matrix(config.phone_axis_map)
        self.estimated_linear_m = np.zeros(3, dtype=float)
        self.estimated_angular_deg = np.zeros(3, dtype=float)
        self.filtered_linear_m_s = np.zeros(3, dtype=float)
        self.filtered_angular_deg_s = np.zeros(3, dtype=float)

    def reset(
        self,
        reference_pose: PhonePose,
        *,
        reference_robot_pose: RobotToolPose | None = None,
    ) -> None:
        self.reference_pose = reference_pose
        self.reference_robot_pose = reference_robot_pose
        if reference_robot_pose is not None and self.phone_to_robot_orientation is None:
            self.phone_to_robot_orientation = (
                reference_robot_pose.orientation * reference_pose.orientation.inv()
            )
            self.orientation_reference_pose = reference_pose
            self.orientation_reference_robot_pose = reference_robot_pose
        self.estimated_linear_m[:] = 0.0
        self.estimated_angular_deg[:] = 0.0
        self.filtered_linear_m_s[:] = 0.0
        self.filtered_angular_deg_s[:] = 0.0

    def _map_phone_vector_to_robot(self, values: np.ndarray) -> np.ndarray:
        return self.axis_map_matrix @ values

    def _translation_signs(self) -> np.ndarray:
        return np.array(
            [
                -1.0 if self.config.invert_x else 1.0,
                -1.0 if self.config.invert_y else 1.0,
                -1.0 if self.config.invert_z else 1.0,
            ],
            dtype=float,
        )

    def _rotation_signs(self) -> np.ndarray:
        return np.array(
            [
                -1.0 if self.config.invert_roll else 1.0,
                -1.0 if self.config.invert_pitch else 1.0,
                -1.0 if self.config.invert_yaw else 1.0,
            ],
            dtype=float,
        )

    def target_delta(self, current_pose: PhonePose) -> TargetDelta:
        if self.reference_pose is None:
            raise RuntimeError("mapper has no reference pose")

        linear = self.visual_linear_delta(current_pose)
        linear = _clip_target_vector_norm(linear, self.config.max_target_offset_m)

        target_orientation = self._target_orientation_from_phone(current_pose)
        if self.reference_robot_pose is not None and target_orientation is not None:
            relative_rotation = self.reference_robot_pose.orientation.inv() * target_orientation
            angular_deg = np.rad2deg(relative_rotation.as_rotvec())
        else:
            phone_rotvec = self._mapped_phone_rotation_delta(current_pose)
            angular_rad = phone_rotvec * self._rotation_signs() * self.config.rotation_scale
            angular_deg = np.rad2deg(angular_rad)
        angular_deg = _clip_target_vector_norm(angular_deg, self.config.max_target_rotation_deg)

        return TargetDelta(linear_m=linear, angular_deg=angular_deg)

    def _mapped_phone_rotation_delta(self, current_pose: PhonePose) -> np.ndarray:
        if self.orientation_reference_pose is not None:
            relative_rotation = self.orientation_reference_pose.orientation.inv() * current_pose.orientation
        elif self.reference_pose is not None:
            relative_rotation = self.reference_pose.orientation.inv() * current_pose.orientation
        else:
            raise RuntimeError("mapper has no reference pose")
        return self._map_phone_vector_to_robot(relative_rotation.as_rotvec())

    def _target_orientation_from_phone(self, current_pose: PhonePose) -> R | None:
        if self.orientation_reference_robot_pose is None:
            return None
        mapped_rotvec = (
            self._mapped_phone_rotation_delta(current_pose)
            * self._rotation_signs()
            * self.config.rotation_scale
        )
        return self.orientation_reference_robot_pose.orientation * R.from_rotvec(mapped_rotvec)

    def visual_linear_delta(self, current_pose: PhonePose) -> np.ndarray:
        if self.reference_pose is None:
            raise RuntimeError("mapper has no reference pose")
        world_delta = current_pose.position_m - self.reference_pose.position_m
        phone_delta = self.reference_pose.orientation.inv().apply(world_delta)
        robot_delta = self._map_phone_vector_to_robot(phone_delta)
        return robot_delta * self._translation_signs() * self.config.translation_scale

    def visual_tool_pose_from_phone(self, current_pose: PhonePose) -> RobotToolPose | None:
        if self.reference_robot_pose is None:
            return None
        visual_position = self.reference_robot_pose.position_m + self.visual_linear_delta(current_pose)
        target_orientation = self._target_orientation_from_phone(current_pose)
        if target_orientation is not None:
            visual_orientation = target_orientation
        else:
            visual_orientation = self.reference_robot_pose.orientation
        return RobotToolPose(position_m=visual_position, orientation=visual_orientation)

    def target_tool_pose_from_delta(self, target: TargetDelta) -> RobotToolPose | None:
        if self.reference_robot_pose is None:
            return None
        target_position = self.reference_robot_pose.position_m + target.linear_m
        target_orientation = self.reference_robot_pose.orientation * R.from_rotvec(
            np.deg2rad(target.angular_deg)
        )
        return RobotToolPose(position_m=target_position, orientation=target_orientation)

    def _actual_robot_delta(
        self,
        robot_pose: RobotToolPose | None,
    ) -> tuple[np.ndarray, np.ndarray] | None:
        if robot_pose is None or self.reference_robot_pose is None:
            return None

        linear_m = robot_pose.position_m - self.reference_robot_pose.position_m
        relative_rotation = self.reference_robot_pose.orientation.inv() * robot_pose.orientation
        angular_deg = np.rad2deg(relative_rotation.as_rotvec())
        return linear_m, angular_deg

    def command_for_pose(
        self,
        current_pose: PhonePose,
        *,
        dt_s: float,
        gripper_axis_value: float,
        robot_pose: RobotToolPose | None = None,
    ) -> JogCommand:
        dt = min(max(dt_s, self.config.period_s * 0.25), 0.2)
        target = self.target_delta(current_pose)

        actual_delta = self._actual_robot_delta(robot_pose)
        if actual_delta is not None:
            actual_linear_m, actual_angular_deg = actual_delta
            self.estimated_linear_m = actual_linear_m.copy()
            self.estimated_angular_deg = actual_angular_deg.copy()
        else:
            actual_linear_m = self.estimated_linear_m
            actual_angular_deg = self.estimated_angular_deg

        linear_error = target.linear_m - actual_linear_m
        angular_error = target.angular_deg - actual_angular_deg
        linear_error = _deadzone_vector_norm(linear_error, self.config.linear_deadband_m)
        angular_error = _deadzone_vector_norm(angular_error, self.config.angular_deadband_deg)

        desired_linear = _clip_vector_norm(
            linear_error * self.config.linear_kp,
            self.config.max_linear_m_s,
        )
        desired_angular = _clip_vector_norm(
            angular_error * self.config.angular_kp,
            self.config.max_angular_deg_s,
        )

        alpha = min(max(self.config.filter_alpha, 0.0), 1.0)
        self.filtered_linear_m_s = (
            alpha * desired_linear + (1.0 - alpha) * self.filtered_linear_m_s
        )
        self.filtered_angular_deg_s = (
            alpha * desired_angular + (1.0 - alpha) * self.filtered_angular_deg_s
        )
        if np.linalg.norm(desired_linear) <= 1e-12 and np.linalg.norm(self.filtered_linear_m_s) < 5e-4:
            self.filtered_linear_m_s[:] = 0.0
        if np.linalg.norm(desired_angular) <= 1e-12 and np.linalg.norm(self.filtered_angular_deg_s) < 0.05:
            self.filtered_angular_deg_s[:] = 0.0

        self.estimated_linear_m += self.filtered_linear_m_s * dt
        self.estimated_angular_deg += self.filtered_angular_deg_s * dt

        gripper_axis = _deadzone(gripper_axis_value, self.config.axis_deadzone)
        gripper_rate = float(
            np.clip(
                gripper_axis * self.config.max_gripper_deg_s,
                -self.config.max_gripper_deg_s,
                self.config.max_gripper_deg_s,
            )
        )

        return JogCommand(
            linear_m_s=self.filtered_linear_m_s.copy(),
            angular_deg_s=self.filtered_angular_deg_s.copy(),
            gripper_deg_s=gripper_rate,
        )


class GradientJogApiClient:
    """Thin HTTP client for GradientOS jog endpoints."""

    def __init__(self, api_host: str, *, timeout_s: float, dry_run: bool) -> None:
        self.api_host = api_host.rstrip("/")
        self.timeout_s = timeout_s
        self.dry_run = dry_run
        self.session = requests.Session()

    def close(self) -> None:
        self.session.close()

    def _post(self, path: str, payload: dict[str, Any] | None = None) -> None:
        if self.dry_run:
            suffix = f" {payload}" if payload else ""
            print(f"[dry-run] POST {path}{suffix}")
            return
        response = self.session.post(
            f"{self.api_host}{path}",
            json=payload,
            timeout=self.timeout_s,
        )
        response.raise_for_status()

    def _get(self, path: str) -> dict[str, Any] | None:
        if self.dry_run:
            return None
        response = self.session.get(
            f"{self.api_host}{path}",
            timeout=self.timeout_s,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError(f"GET {path} returned non-object JSON: {payload!r}")
        return payload

    def post_diagnostic(self, path: str, payload: dict[str, Any]) -> None:
        response = self.session.post(
            f"{self.api_host}{path}",
            json=payload,
            timeout=min(self.timeout_s, 0.2),
        )
        response.raise_for_status()

    def start(self) -> None:
        self._post("/control/jog/start")

    def stop(self) -> None:
        self._post("/control/jog/stop")

    def set_deadman(self, enabled: bool) -> None:
        self._post("/control/jog/deadman", {"enabled": enabled})

    def send_velocity(self, command: JogCommand) -> None:
        self._post("/control/jog/velocity", command.as_payload())

    def send_gripper_velocity(self, command: JogCommand) -> None:
        self._post(
            "/control/jog/gripper-velocity",
            {"rate_deg_s": command.gripper_deg_s},
        )

    def zero(self) -> None:
        self.send_velocity(JogCommand())
        self._post("/control/jog/gripper-velocity", {"rate_deg_s": 0.0})

    def get_tool_pose(self) -> RobotToolPose | None:
        payload = self._get("/info/pose")
        if payload is None:
            return None
        return RobotToolPose.from_api_payload(payload)


def _import_hebi():
    try:
        import hebi  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Missing optional dependency 'hebi-py'. Install it with "
            "`uv pip install -e '.[phone]'` or `pip install hebi-py`."
        ) from exc
    return hebi


def _create_mobile_io(config: BridgeConfig):
    hebi = _import_hebi()
    lookup = hebi.Lookup()
    if config.lookup_wait_s > 0:
        time.sleep(config.lookup_wait_s)

    if config.list_devices:
        print("[HEBI] Discovered devices:")
        for entry in lookup.entrylist:
            family = getattr(entry, "family", "?")
            name = getattr(entry, "name", "?")
            ip = getattr(entry, "ip_address", "?")
            print(f"  - family={family!r} name={name!r} ip={ip}")

    mobile_io = hebi.util.create_mobile_io(
        lookup,
        family=config.family,
        name=config.name,
    )
    if mobile_io is None:
        raise RuntimeError(
            f"Could not find HEBI Mobile I/O family={config.family!r} "
            f"name={config.name!r}. Open the app on the same LAN and check "
            "the iOS Mobile I/O settings."
        )

    if config.setup_mobile_ui:
        try:
            mobile_io.resetUI()
            mobile_io.add_text("B1: hold to move", blocking=False)
            mobile_io.add_text("Release + hold B1 again: recenter", blocking=False)
            mobile_io.add_text("B2/B4: gripper open/close", blocking=False)
            mobile_io.add_text("B8: quit bridge", blocking=False)
        except Exception as exc:
            print(f"[HEBI] UI setup skipped: {exc}")

    return mobile_io


def _read_button_state(mobile_io: Any, button_index: int) -> bool:
    if button_index <= 0:
        return False
    try:
        return bool(mobile_io.get_button_state(button_index))
    except Exception:
        return False


def _gripper_button_axis(mobile_io: Any, config: BridgeConfig) -> float:
    open_held = _read_button_state(mobile_io, config.gripper_open_button)
    close_held = _read_button_state(mobile_io, config.gripper_close_button)
    if open_held == close_held:
        return 0.0
    return 1.0 if open_held else -1.0


def _read_phone_pose(mobile_io: Any, config: BridgeConfig) -> PhonePose | None:
    try:
        return PhonePose.from_hebi(
            mobile_io.position,
            mobile_io.orientation,
            quaternion_order=config.quaternion_order,
        )
    except Exception:
        return None


class HebiMobileIOBridge:
    """Runtime bridge from HEBI Mobile I/O to GradientOS jog commands."""

    def __init__(self, config: BridgeConfig) -> None:
        self.config = config
        self.mapper = SpatialPhoneMapper(config)
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


def _sample_mobile_io_pose(
    mobile_io: Any,
    config: BridgeConfig,
    *,
    duration_s: float = 0.35,
) -> PhonePose:
    deadline = time.monotonic() + max(0.05, duration_s)
    last_pose: PhonePose | None = None
    while time.monotonic() < deadline:
        try:
            mobile_io.update(timeout_ms=20)
        except Exception:
            pass
        pose = _read_phone_pose(mobile_io, config)
        if pose is not None:
            last_pose = pose
        time.sleep(0.02)
    if last_pose is None:
        raise RuntimeError("No valid ARKit pose received from Mobile I/O.")
    return last_pose


def _print_sample_delta(label: str, reference: PhonePose, sample: PhonePose) -> None:
    delta = sample.position_m - reference.position_m
    axis_names = np.array(["x", "y", "z"])
    dominant_index = int(np.argmax(np.abs(delta)))
    dominant_axis = axis_names[dominant_index]
    sign = "+" if delta[dominant_index] >= 0 else "-"
    relative_rotation = reference.orientation.inv() * sample.orientation
    euler_deg = relative_rotation.as_euler("xyz", degrees=True)
    print(
        f"[calibration] {label:<14} "
        f"delta_m={np.round(delta, 4)} "
        f"dominant={sign}{dominant_axis} "
        f"rot_xyz_deg={np.round(euler_deg, 1)}"
    )


@dataclass(frozen=True)
class CalibrationPrompt:
    label: str
    instruction: str


CALIBRATION_PROMPTS: tuple[CalibrationPrompt, ...] = (
    CalibrationPrompt("left", "Move the phone LEFT from your perspective"),
    CalibrationPrompt("right", "Move the phone RIGHT from your perspective"),
    CalibrationPrompt("up", "Move the phone UP"),
    CalibrationPrompt("down", "Move the phone DOWN"),
    CalibrationPrompt("forward", "Move the phone FORWARD / away from you"),
    CalibrationPrompt("back", "Move the phone BACK / toward you"),
    CalibrationPrompt("yaw left", "Yaw the phone LEFT"),
    CalibrationPrompt("yaw right", "Yaw the phone RIGHT"),
    CalibrationPrompt("pitch up", "Pitch the top edge UP"),
    CalibrationPrompt("pitch down", "Pitch the top edge DOWN"),
    CalibrationPrompt("roll left", "Roll the phone LEFT"),
    CalibrationPrompt("roll right", "Roll the phone RIGHT"),
)


def run_phone_frame_calibration(config: BridgeConfig) -> int:
    """Interactive no-motion calibration helper for phone-frame discovery."""

    config.dry_run = True
    config.publish_phone_pose = True
    print("[calibration] Connecting to HEBI Mobile I/O. No robot motion will be commanded.")
    mobile_io = _create_mobile_io(config)
    client = GradientJogApiClient(
        config.api_host,
        timeout_s=config.request_timeout_s,
        dry_run=False,
    )
    sequence = 0

    def publish(label: str, pose: PhonePose, reference: PhonePose) -> None:
        nonlocal sequence
        sequence += 1
        payload = {
            "source": f"hebi_mobile_io_calibration:{label}",
            "sequence": sequence,
            "enabled": False,
            **pose.as_debug_payload(),
            "reference_position_m": _xyz_payload(reference.position_m),
            "delta_m": _xyz_payload(pose.position_m - reference.position_m),
        }
        try:
            client.post_diagnostic("/teleop/phone-pose", payload)
        except Exception as exc:
            print(f"[calibration] API visualization publish skipped: {exc}")

    try:
        input("[calibration] Hold the phone in your neutral driving pose, then press Enter.")
        reference = _sample_mobile_io_pose(mobile_io, config)
        publish("neutral", reference, reference)
        print("[calibration] Neutral pose captured. Keep the API/web UI open to see the phone cuboid.")

        for step in CALIBRATION_PROMPTS:
            input(
                f"[calibration] Return to neutral for '{step.label}', hold still, "
                "then press Enter."
            )
            step_reference = _sample_mobile_io_pose(mobile_io, config)
            publish(f"{step.label} reference", step_reference, step_reference)
            input(f"[calibration] {step.instruction}, hold still, then press Enter.")
            sample = _sample_mobile_io_pose(mobile_io, config)
            publish(step.label, sample, step_reference)
            _print_sample_delta(step.label, step_reference, sample)

        print("[calibration] Done. Use the dominant axes/signs above to choose --phone-axis-map and any --invert-* flags.")
        return 0
    except KeyboardInterrupt:
        print("\n[calibration] interrupted")
        return 130
    finally:
        client.close()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bridge HEBI Mobile I/O iPhone ARKit pose into GradientOS realtime jog.",
    )
    parser.add_argument("--api-host", default="http://127.0.0.1:4000")
    parser.add_argument("--family", default="HEBI")
    parser.add_argument("--name", default="mobileIO")
    parser.add_argument("--rate-hz", type=float, default=25.0)
    parser.add_argument("--lookup-wait-s", type=float, default=1.0)
    parser.add_argument("--stale-timeout-s", type=float, default=0.35)
    parser.add_argument("--request-timeout-s", type=float, default=0.45)
    parser.add_argument("--enable-button", type=int, default=1)
    parser.add_argument("--quit-button", type=int, default=8)
    parser.add_argument("--gripper-open-button", type=int, default=2)
    parser.add_argument("--gripper-close-button", type=int, default=4)
    parser.add_argument("--gripper-axis", type=int, default=3)
    parser.add_argument("--axis-deadzone", type=float, default=0.08)
    parser.add_argument("--translation-scale", type=float, default=1.0)
    parser.add_argument("--rotation-scale", type=float, default=1.0)
    parser.add_argument(
        "--phone-axis-map",
        default="y,-x,z",
        help=(
            "Map phone-local axes into robot axes as robot_x,robot_y,robot_z. "
            "Default y,-x,z means phone forward -> robot +X and phone right -> robot -Y."
        ),
    )
    parser.add_argument("--invert-x", action="store_true", help="Invert mapped robot X translation.")
    parser.add_argument("--invert-y", action="store_true", help="Invert mapped robot Y translation.")
    parser.add_argument("--invert-z", action="store_true", help="Invert mapped robot Z translation.")
    parser.add_argument("--invert-roll", action="store_true", help="Invert mapped robot roll.")
    parser.add_argument("--invert-pitch", action="store_true", help="Invert mapped robot pitch.")
    parser.add_argument("--invert-yaw", action="store_true", help="Invert mapped robot yaw.")
    parser.add_argument("--linear-kp", type=float, default=3.0)
    parser.add_argument("--angular-kp", type=float, default=4.0)
    parser.add_argument("--linear-deadband-m", type=float, default=0.004)
    parser.add_argument("--angular-deadband-deg", type=float, default=0.75)
    parser.add_argument(
        "--max-target-offset-m",
        type=float,
        default=float("inf"),
        help="Optional robot target offset limit in meters; <=0 or inf means unlimited.",
    )
    parser.add_argument(
        "--max-target-rotation-deg",
        type=float,
        default=float("inf"),
        help="Optional robot target rotation limit in degrees; <=0 or inf means unlimited.",
    )
    parser.add_argument("--max-linear-m-s", type=float, default=0.08)
    parser.add_argument("--max-angular-deg-s", type=float, default=45.0)
    parser.add_argument("--max-gripper-deg-s", type=float, default=45.0)
    parser.add_argument("--filter-alpha", type=float, default=0.35)
    parser.add_argument("--quaternion-order", choices=("wxyz", "xyzw"), default="wxyz")
    parser.add_argument("--list-devices", action="store_true")
    parser.add_argument("--setup-mobile-ui", action="store_true")
    parser.add_argument("--no-stop-on-release", action="store_true")
    parser.add_argument("--robot-pose-poll-interval-s", type=float, default=0.08)
    parser.add_argument("--no-publish-phone-pose", action="store_true")
    parser.add_argument("--phone-pose-publish-interval-s", type=float, default=0.05)
    parser.add_argument("--no-auto-reconnect", action="store_true")
    parser.add_argument("--reconnect-interval-s", type=float, default=1.0)
    parser.add_argument("--reconnect-after-stale-s", type=float, default=1.5)
    parser.add_argument(
        "--calibrate-phone-frame",
        action="store_true",
        help="Run an interactive no-motion phone-frame calibration wizard.",
    )
    parser.add_argument("--live", action="store_true", help="Send commands to the GradientOS API.")
    parser.add_argument("--log-interval-s", type=float, default=1.0)
    parser.add_argument(
        "--diagnostic-log",
        action="store_true",
        help="Write low-rate phone/target/command JSONL diagnostics under diagnostics/jog_motion.",
    )
    parser.add_argument("--diagnostic-log-interval-s", type=float, default=0.1)
    parser.add_argument("--diagnostic-log-path", default=None)
    return parser


def config_from_args(args: argparse.Namespace) -> BridgeConfig:
    return BridgeConfig(
        api_host=args.api_host,
        family=args.family,
        name=args.name,
        rate_hz=args.rate_hz,
        lookup_wait_s=args.lookup_wait_s,
        stale_timeout_s=args.stale_timeout_s,
        request_timeout_s=args.request_timeout_s,
        enable_button=args.enable_button,
        quit_button=args.quit_button,
        gripper_open_button=args.gripper_open_button,
        gripper_close_button=args.gripper_close_button,
        gripper_axis=args.gripper_axis,
        axis_deadzone=args.axis_deadzone,
        translation_scale=args.translation_scale,
        rotation_scale=args.rotation_scale,
        phone_axis_map=args.phone_axis_map,
        invert_x=args.invert_x,
        invert_y=args.invert_y,
        invert_z=args.invert_z,
        invert_roll=args.invert_roll,
        invert_pitch=args.invert_pitch,
        invert_yaw=args.invert_yaw,
        linear_kp=args.linear_kp,
        angular_kp=args.angular_kp,
        linear_deadband_m=args.linear_deadband_m,
        angular_deadband_deg=args.angular_deadband_deg,
        max_target_offset_m=args.max_target_offset_m,
        max_target_rotation_deg=args.max_target_rotation_deg,
        max_linear_m_s=args.max_linear_m_s,
        max_angular_deg_s=args.max_angular_deg_s,
        max_gripper_deg_s=args.max_gripper_deg_s,
        filter_alpha=args.filter_alpha,
        quaternion_order=args.quaternion_order,
        dry_run=not args.live,
        stop_on_release=not args.no_stop_on_release,
        robot_pose_poll_interval_s=args.robot_pose_poll_interval_s,
        publish_phone_pose=not args.no_publish_phone_pose,
        phone_pose_publish_interval_s=args.phone_pose_publish_interval_s,
        auto_reconnect=not args.no_auto_reconnect,
        reconnect_interval_s=args.reconnect_interval_s,
        reconnect_after_stale_s=args.reconnect_after_stale_s,
        calibrate_phone_frame=args.calibrate_phone_frame,
        setup_mobile_ui=args.setup_mobile_ui,
        list_devices=args.list_devices,
        log_interval_s=args.log_interval_s,
        diagnostic_log=args.diagnostic_log,
        diagnostic_log_interval_s=args.diagnostic_log_interval_s,
        diagnostic_log_path=args.diagnostic_log_path,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    config = config_from_args(args)
    try:
        if config.calibrate_phone_frame:
            return run_phone_frame_calibration(config)
        return HebiMobileIOBridge(config).run()
    except Exception as exc:
        print(f"[teleop] ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
