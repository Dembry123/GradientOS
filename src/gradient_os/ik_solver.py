"""Thin solver facade for GradientOS kinematics.

Concrete implementations live in ``gradient_os.ik_backends``. This module keeps
the legacy public functions used by the controller and planners.
"""

from __future__ import annotations

import csv
import datetime
import os
from pathlib import Path

import numpy as np

from .arm_controller import utils
from .ik_backends import (
    BackendUnavailable,
    END_EFFECTOR_OFFSET,
    build_backend,
    canonical_backend_name,
    find_closest_solution,
    shortest_angular_distance,
    urdf_fk_matrix,
    wrap_to_prev,
)


_BACKEND_NAME = canonical_backend_name(os.getenv("MINI_ARM_SOLVER", "ikfast"))
_BACKEND = build_backend(_BACKEND_NAME)
_BACKEND_NAME = _BACKEND.name

NUM_JOINTS = _BACKEND.num_joints

# Legacy private names used by older local scripts.
_urdf_fk_matrix = urdf_fk_matrix
_find_closest_solution = find_closest_solution
_shortest_angular_distance = shortest_angular_distance
_wrap_to_prev = wrap_to_prev


def solve_ik(*, target_position, target_orientation_matrix=None, initial_joint_angles=None):
    """Return joint angles for a public tool-frame target pose, or ``None``."""
    return _BACKEND.solve_pose(
        target_position,
        target_orientation_matrix=target_orientation_matrix,
        seed=initial_joint_angles,
    )


def solve_pose(*, target_position, target_orientation_matrix=None, seed=None):
    """Backend-neutral pose IK API used by newer control paths."""
    return solve_ik(
        target_position=target_position,
        target_orientation_matrix=target_orientation_matrix,
        initial_joint_angles=seed,
    )


def solve_differential_result(
    *,
    target_position=None,
    target_orientation_matrix=None,
    twist=None,
    current_q=None,
    dt=0.04,
):
    """Return explicit ``q_next``, ``dq``, and ``qdot`` for one differential step."""
    return _BACKEND.solve_differential(
        target_position=target_position,
        target_orientation_matrix=target_orientation_matrix,
        twist=twist,
        current_q=current_q,
        dt=dt,
    )


def solve_differential(
    *,
    target_position=None,
    target_orientation_matrix=None,
    twist=None,
    current_q=None,
    dt=0.04,
):
    """Compatibility wrapper: return only ``q_next`` from one differential IK step."""
    return solve_differential_result(
        target_position=target_position,
        target_orientation_matrix=target_orientation_matrix,
        twist=twist,
        current_q=current_q,
        dt=dt,
    ).q_next


def get_backend_name() -> str:
    return _BACKEND_NAME


def get_fk_matrix(active_joint_angles):
    """Return a 4x4 public tool-tip pose matrix for ``active_joint_angles``."""
    return _BACKEND.fk_matrix(active_joint_angles)


def get_fk(active_joint_angles):
    """Return just XYZ position from ``get_fk_matrix``."""
    fk_matrix = get_fk_matrix(active_joint_angles)
    if fk_matrix is not None:
        return fk_matrix[:3, 3]
    return None


def solve_ik_path_sequential(path_points, initial_joint_angles=None, target_orientations=None, *, verbose=True):
    """Solve IK point-by-point, seeding each point from the previous solution."""
    if target_orientations and len(target_orientations) != len(path_points):
        raise ValueError("The number of target orientations must match the number of path points.")

    current_joint_angles = np.array(
        initial_joint_angles if initial_joint_angles is not None else [0.0] * NUM_JOINTS,
        dtype=np.float64,
    )
    all_solutions = []
    for i, position in enumerate(path_points):
        if verbose:
            print(f"\n--- Path Point {i + 1}/{len(path_points)} ---")
        orientation = np.array(target_orientations[i]).flatten() if target_orientations else None
        solution = solve_ik(
            target_position=position,
            target_orientation_matrix=orientation,
            initial_joint_angles=current_joint_angles,
        )
        if solution is None:
            if verbose:
                print(f"IK solution not found for point {i} at position {position}. Aborting path calculation.")
            return None
        all_solutions.append(solution)
        current_joint_angles[:] = solution
    return all_solutions


def _write_ik_plan_diagnostics(path_points, joint_solutions) -> None:
    if joint_solutions is None or os.environ.get("MINI_ARM_IK_LOG", "0") != "1":
        return
    try:
        session_id = utils.trajectory_state.get("diagnostics_session_id")
        folder_type = utils.trajectory_state.get("diagnostics_folder_type", "ik_plans")
        if session_id:
            out_dir = Path(f"diagnostics/{folder_type}/{session_id}")
            csv_file = out_dir / "ik_plan.csv"
        else:
            session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            out_dir = Path(f"diagnostics/{folder_type}")
            csv_file = out_dir / f"ik_plan_{session_id}.csv"

        out_dir.mkdir(parents=True, exist_ok=True)
        with open(csv_file, "w", newline="") as fp:
            writer = csv.writer(fp)
            header = ["idx", "target_x", "target_y", "target_z", *[f"J{i + 1}_rad" for i in range(len(joint_solutions[0]))]]
            writer.writerow(header)
            for idx, (pt, q) in enumerate(zip(path_points, joint_solutions)):
                writer.writerow([idx, *pt, *q])
        print(f"[IK Solver] Diagnostics CSV saved -> {csv_file}")
    except Exception as e:
        print(f"[IK Solver] WARNING: Failed to write diagnostics CSV: {e}")


def solve_ik_path_batch(path_points, initial_joint_angles=None, target_orientations=None):
    """Solve a Cartesian path using backend batch support when available."""
    num_poses = len(path_points)
    if target_orientations and len(target_orientations) != num_poses:
        raise ValueError("The number of target orientations must match the number of path points.")

    joint_solutions = _BACKEND.solve_path_batch(
        path_points,
        initial_joint_angles=initial_joint_angles,
        target_orientations=target_orientations,
    )
    if joint_solutions is None:
        joint_solutions = solve_ik_path_sequential(
            path_points,
            initial_joint_angles=initial_joint_angles,
            target_orientations=target_orientations,
            verbose=False,
        )

    _write_ik_plan_diagnostics(path_points, joint_solutions)
    return joint_solutions


__all__ = [
    "BackendUnavailable",
    "END_EFFECTOR_OFFSET",
    "NUM_JOINTS",
    "get_backend_name",
    "get_fk",
    "get_fk_matrix",
    "solve_differential",
    "solve_differential_result",
    "solve_ik",
    "solve_ik_path_batch",
    "solve_ik_path_sequential",
    "solve_pose",
]
