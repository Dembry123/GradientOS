"""Shared kinematics utilities for GradientOS IK backends."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial.transform import Rotation as R

from ..arm_controller import utils

try:
    from scipy.optimize import lsq_linear
except Exception:  # pragma: no cover - SciPy is a project dependency.
    lsq_linear = None


class BackendUnavailable(RuntimeError):
    """Raised when the requested IK backend cannot be constructed."""


@dataclass(frozen=True)
class DifferentialResult:
    """One differential IK step with explicit units."""

    q_next: np.ndarray
    dq: np.ndarray
    qdot: np.ndarray


END_EFFECTOR_OFFSET = np.array([0.180, 0.0, 0.0], dtype=float)

URDF_JOINTS = (
    ((0.0, 0.0, 0.0843), (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
    ((0.0, 0.0, 0.04315), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
    ((0.0, 0.0, 0.19715), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
    ((0.176556, 0.0, 0.0455), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
    ((0.05515, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
    ((0.0773, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
)
URDF_TOOL_TRANSLATION = (0.180, 0.0, 0.0)
URDF_JOINT_LIMITS_RAD = np.array(
    [
        [-1.5708, 1.5708],
        [-1.5708, 1.5708],
        [-1.5708, 1.5708],
        [-3.1416, 3.1416],
        [-1.8326, 2.0944],
        [-3.1416, 3.1416],
    ],
    dtype=float,
)


def canonical_backend_name(name: str | None) -> str:
    value = (name or "ikfast").strip().lower()
    aliases = {
        "quik": "quik",
        "numeric": "quik",
        "pyquik": "quik",
        "trac_ik": "trac",
        "trac-ik": "trac",
        "damped": "dls",
        "damped_least_squares": "dls",
        "qpdiff": "qp",
        "differential-qp": "qp",
    }
    return aliases.get(value, value)


def joint_limits() -> np.ndarray:
    limits = getattr(utils, "LOGICAL_JOINT_LIMITS_RAD", None)
    try:
        arr = np.asarray(limits, dtype=float)
        if arr.shape == (6, 2) and np.all(np.isfinite(arr)):
            return arr
    except Exception:
        pass
    return URDF_JOINT_LIMITS_RAD.copy()


def as_joint_vector(joint_angles) -> np.ndarray:
    arr = np.asarray(joint_angles if joint_angles is not None else np.zeros(6), dtype=float).reshape(-1)
    if arr.size != 6:
        raise ValueError(f"Expected 6 joint angles, got {arr.size}.")
    if not np.all(np.isfinite(arr)):
        raise ValueError("Joint angle vector contains non-finite values.")
    return arr


def as_rotation_matrix(target_orientation_matrix) -> np.ndarray:
    if target_orientation_matrix is None:
        return np.identity(3)
    arr = np.asarray(target_orientation_matrix, dtype=float)
    if arr.size != 9:
        raise ValueError(f"Orientation matrix must contain 9 values, got {arr.size}.")
    return arr.reshape(3, 3)


def translation_matrix(xyz) -> np.ndarray:
    out = np.eye(4)
    out[:3, 3] = np.asarray(xyz, dtype=float)
    return out


def rotation_matrix_from_rpy(rpy) -> np.ndarray:
    out = np.eye(4)
    out[:3, :3] = R.from_euler("xyz", np.asarray(rpy, dtype=float)).as_matrix()
    return out


def axis_rotation_matrix(axis, angle_rad: float) -> np.ndarray:
    axis_arr = np.asarray(axis, dtype=float)
    norm = float(np.linalg.norm(axis_arr))
    if norm <= 1e-12:
        raise ValueError("Joint axis norm is zero.")
    out = np.eye(4)
    out[:3, :3] = R.from_rotvec(axis_arr / norm * float(angle_rad)).as_matrix()
    return out


def urdf_fk_matrix(joint_angles) -> np.ndarray:
    q = as_joint_vector(joint_angles)
    transform = np.eye(4)
    for angle, (xyz, rpy, axis) in zip(q, URDF_JOINTS):
        transform = (
            transform
            @ translation_matrix(xyz)
            @ rotation_matrix_from_rpy(rpy)
            @ axis_rotation_matrix(axis, float(angle))
        )
    return transform @ translation_matrix(URDF_TOOL_TRANSLATION)


def pose_error_vector(current_pose: np.ndarray, target_position, target_orientation_matrix) -> np.ndarray:
    target_position_arr = np.asarray(target_position, dtype=float).reshape(3)
    target_rotation = as_rotation_matrix(target_orientation_matrix)
    position_error = target_position_arr - current_pose[:3, 3]
    orientation_error = R.from_matrix(target_rotation @ current_pose[:3, :3].T).as_rotvec()
    return np.concatenate([position_error, orientation_error])


def pose_error_norms(current_pose: np.ndarray, target_position, target_orientation_matrix) -> tuple[float, float]:
    error = pose_error_vector(current_pose, target_position, target_orientation_matrix)
    return float(np.linalg.norm(error[:3])), float(np.linalg.norm(error[3:]))


def finite_difference_jacobian(fk_func, joint_angles, *, eps: float = 1e-5) -> np.ndarray:
    q = as_joint_vector(joint_angles)
    base_pose = fk_func(q)
    if base_pose is None:
        raise RuntimeError("FK failed while computing numerical Jacobian.")
    base_pose = np.asarray(base_pose, dtype=float).reshape(4, 4)
    jacobian = np.zeros((6, q.size), dtype=float)
    for index in range(q.size):
        q_plus = q.copy()
        q_plus[index] += eps
        pose_plus = fk_func(q_plus)
        if pose_plus is None:
            raise RuntimeError("FK failed while computing numerical Jacobian.")
        pose_plus = np.asarray(pose_plus, dtype=float).reshape(4, 4)
        jacobian[:3, index] = (pose_plus[:3, 3] - base_pose[:3, 3]) / eps
        delta_r = pose_plus[:3, :3] @ base_pose[:3, :3].T
        jacobian[3:, index] = R.from_matrix(delta_r).as_rotvec() / eps
    return jacobian


def bounded_joint_step(q: np.ndarray, max_joint_step_rad: float) -> tuple[np.ndarray, np.ndarray]:
    limits = joint_limits()
    lower = np.maximum(limits[:, 0] - q, -max_joint_step_rad)
    upper = np.minimum(limits[:, 1] - q, max_joint_step_rad)
    return lower, upper


def dls_joint_step(
    *,
    fk_func,
    current_q,
    pose_error,
    damping: float = 0.04,
    max_joint_step_rad: float = 0.08,
) -> np.ndarray:
    q = as_joint_vector(current_q)
    jacobian = finite_difference_jacobian(fk_func, q)
    system = jacobian @ jacobian.T + (float(damping) ** 2) * np.eye(6)
    dq = jacobian.T @ np.linalg.solve(system, np.asarray(pose_error, dtype=float).reshape(6))
    norm_inf = float(np.max(np.abs(dq)))
    if norm_inf > max_joint_step_rad:
        dq = dq * (max_joint_step_rad / norm_inf)
    lower, upper = bounded_joint_step(q, max_joint_step_rad)
    return np.clip(dq, lower, upper)


def qp_joint_step(
    *,
    fk_func,
    current_q,
    pose_error,
    damping: float = 0.01,
    max_joint_step_rad: float = 0.08,
) -> np.ndarray:
    if lsq_linear is None:
        raise BackendUnavailable("SciPy lsq_linear is unavailable; cannot run qp IK backend.")
    q = as_joint_vector(current_q)
    jacobian = finite_difference_jacobian(fk_func, q)
    regularizer = np.sqrt(max(float(damping), 1e-12)) * np.eye(q.size)
    lhs = np.vstack([jacobian, regularizer])
    rhs = np.concatenate([np.asarray(pose_error, dtype=float).reshape(6), np.zeros(q.size)])
    lower, upper = bounded_joint_step(q, max_joint_step_rad)
    result = lsq_linear(lhs, rhs, bounds=(lower, upper), max_iter=40, lsmr_tol="auto")
    if not result.success and not np.all(np.isfinite(result.x)):
        raise RuntimeError(f"QP differential step failed: {result.message}")
    return np.asarray(result.x, dtype=float)


def differential_result_from_dq(current_q, dq, dt: float) -> DifferentialResult:
    q = as_joint_vector(current_q)
    dq_arr = np.asarray(dq, dtype=float).reshape(6)
    q_next = np.clip(q + dq_arr, joint_limits()[:, 0], joint_limits()[:, 1])
    actual_dq = q_next - q
    qdot = actual_dq / dt if dt > 1e-9 else np.zeros_like(actual_dq)
    return DifferentialResult(q_next=q_next, dq=actual_dq, qdot=qdot)


def error_from_target_or_twist(
    *,
    fk_func,
    current_q,
    target_position=None,
    target_orientation_matrix=None,
    twist=None,
    dt=0.04,
) -> np.ndarray:
    if twist is not None:
        twist_arr = np.asarray(twist, dtype=float).reshape(6)
        return np.concatenate([twist_arr[:3] * dt, twist_arr[3:] * dt])
    pose = fk_func(as_joint_vector(current_q))
    return pose_error_vector(pose, target_position, target_orientation_matrix)


def iterative_differential_ik(
    *,
    method: str,
    fk_func,
    target_position,
    target_orientation_matrix,
    initial_joint_angles,
    max_iterations: int = 120,
    pos_tolerance_m: float = 0.0015,
    rot_tolerance_rad: float = np.deg2rad(1.2),
) -> np.ndarray | None:
    q = as_joint_vector(initial_joint_angles)
    q = np.clip(q, joint_limits()[:, 0], joint_limits()[:, 1])
    target_rotation = as_rotation_matrix(target_orientation_matrix)
    for _ in range(max_iterations):
        current_pose = fk_func(q)
        if current_pose is None:
            return None
        current_pose = np.asarray(current_pose, dtype=float).reshape(4, 4)
        position_error_m, rotation_error_rad = pose_error_norms(
            current_pose,
            target_position,
            target_rotation,
        )
        if position_error_m <= pos_tolerance_m and rotation_error_rad <= rot_tolerance_rad:
            return q
        error = pose_error_vector(current_pose, target_position, target_rotation)
        dq = (
            qp_joint_step(fk_func=fk_func, current_q=q, pose_error=error)
            if method == "qp"
            else dls_joint_step(fk_func=fk_func, current_q=q, pose_error=error)
        )
        if float(np.linalg.norm(dq)) <= 1e-8:
            break
        q = np.clip(q + dq, joint_limits()[:, 0], joint_limits()[:, 1])
    current_pose = fk_func(q)
    if current_pose is None:
        return None
    position_error_m, rotation_error_rad = pose_error_norms(
        np.asarray(current_pose, dtype=float).reshape(4, 4),
        target_position,
        target_rotation,
    )
    if position_error_m <= pos_tolerance_m * 2.0 and rotation_error_rad <= rot_tolerance_rad * 2.0:
        return q
    return None


TWO_PI = 2.0 * np.pi


def shortest_angular_distance(a, b):
    return (b - a + np.pi) % TWO_PI - np.pi


def wrap_to_prev(prev, angles):
    wrapped = np.asarray(angles, dtype=float).copy()
    return np.asarray(prev, dtype=float) + shortest_angular_distance(prev, wrapped)


def find_closest_solution(solutions, current_joint_angles):
    if solutions is None or solutions.size == 0:
        return None
    if solutions.ndim == 1:
        return solutions
    continuous_solutions = np.array([wrap_to_prev(current_joint_angles, sol) for sol in solutions])
    distances = np.linalg.norm(continuous_solutions - current_joint_angles, axis=1)
    return continuous_solutions[int(np.argmin(distances))]
