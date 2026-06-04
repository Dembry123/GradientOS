"""Interactive phone-frame calibration for HEBI Mobile I/O teleop."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import numpy as np

from .gradient_jog_client import GradientJogApiClient
from .hebi_mobile_io_device import _create_mobile_io, _read_phone_pose
from .hebi_models import BridgeConfig, PhonePose, _xyz_payload


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
