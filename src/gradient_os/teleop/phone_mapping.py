"""Phone-pose to robot jog command mapping."""

from __future__ import annotations

import numpy as np
from scipy.spatial.transform import Rotation as R

from .hebi_models import BridgeConfig, JogCommand, MappingConfig, PhonePose, RobotToolPose, TargetDelta


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


class SpatialPhoneMapper:
    """Maps ARKit pose deltas to bounded GradientOS jog velocity commands."""

    def __init__(self, config: BridgeConfig | MappingConfig) -> None:
        self.config = config.mapping_config() if isinstance(config, BridgeConfig) else config
        self.reference_pose: PhonePose | None = None
        self.reference_robot_pose: RobotToolPose | None = None
        self.orientation_reference_pose: PhonePose | None = None
        self.orientation_reference_robot_pose: RobotToolPose | None = None
        self.axis_map_matrix = _axis_map_matrix(self.config.phone_axis_map)
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
        if reference_robot_pose is not None and self.orientation_reference_pose is None:
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
