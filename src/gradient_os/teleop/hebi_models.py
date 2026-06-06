"""Data models for HEBI Mobile I/O teleop."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np
from scipy.spatial.transform import Rotation as R

QuaternionOrder = Literal["wxyz", "xyzw"]
TeleopMode = Literal["velocity_jog", "absolute_pose"]


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


def _xyz_payload(values: np.ndarray) -> dict[str, float]:
    return {
        "x": float(values[0]),
        "y": float(values[1]),
        "z": float(values[2]),
    }


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


@dataclass(frozen=True)
class MappingConfig:
    rate_hz: float = 25.0
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

    @property
    def period_s(self) -> float:
        return 1.0 / max(1.0, self.rate_hz)


@dataclass
class BridgeConfig:
    api_host: str = "http://127.0.0.1:4000"
    family: str = "HEBI"
    name: str = "mobileIO"
    rate_hz: float = 25.0
    teleop_mode: TeleopMode = "velocity_jog"
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

    def __post_init__(self) -> None:
        if self.teleop_mode not in ("velocity_jog", "absolute_pose"):
            raise ValueError("teleop_mode must be velocity_jog or absolute_pose")

    @property
    def period_s(self) -> float:
        return 1.0 / max(1.0, self.rate_hz)

    def mapping_config(self) -> MappingConfig:
        return MappingConfig(
            rate_hz=self.rate_hz,
            axis_deadzone=self.axis_deadzone,
            translation_scale=self.translation_scale,
            rotation_scale=self.rotation_scale,
            phone_axis_map=self.phone_axis_map,
            invert_x=self.invert_x,
            invert_y=self.invert_y,
            invert_z=self.invert_z,
            invert_roll=self.invert_roll,
            invert_pitch=self.invert_pitch,
            invert_yaw=self.invert_yaw,
            linear_kp=self.linear_kp,
            angular_kp=self.angular_kp,
            linear_deadband_m=self.linear_deadband_m,
            angular_deadband_deg=self.angular_deadband_deg,
            max_target_offset_m=self.max_target_offset_m,
            max_target_rotation_deg=self.max_target_rotation_deg,
            max_linear_m_s=self.max_linear_m_s,
            max_angular_deg_s=self.max_angular_deg_s,
            max_gripper_deg_s=self.max_gripper_deg_s,
            filter_alpha=self.filter_alpha,
        )


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
