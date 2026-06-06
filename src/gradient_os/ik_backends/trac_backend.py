"""TRAC-IK backend adapter."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation as R

from .base import IKBackend
from .common import (
    BackendUnavailable,
    as_joint_vector,
    as_rotation_matrix,
    differential_result_from_dq,
    dls_joint_step,
    error_from_target_or_twist,
    urdf_fk_matrix,
    wrap_to_prev,
)


class TracBackend(IKBackend):
    name = "trac"

    def __init__(self) -> None:
        try:
            from numeric_solver.trac_ik_interface import TracIKInterface
        except Exception as e:
            raise BackendUnavailable(f"Failed to import TRAC-IK wrapper: {e}") from e

        urdf_path = Path(__file__).resolve().parents[3] / "mini-6dof-arm" / "mini-6dof-arm.urdf"
        try:
            urdf_string = urdf_path.read_text(encoding="utf-8")
            self.solver = TracIKInterface(
                "base",
                "tool_link",
                urdf_string=urdf_string,
                timeout=float(os.getenv("MINI_ARM_TRAC_TIMEOUT_S", "0.008")),
                epsilon=float(os.getenv("MINI_ARM_TRAC_EPSILON", "1e-5")),
            )
            self.num_joints = self.solver.number_of_joints
            self.legacy_solver = self.solver
            print(f"[IK Solver] TRAC-IK back-end initialised for {self.num_joints} joints.")
        except Exception as e:
            raise BackendUnavailable(f"Failed to load TRAC-IK backend: {e}") from e

    def solve_pose(self, target_position, target_orientation_matrix=None, seed=None):
        target_rotation = as_rotation_matrix(target_orientation_matrix)
        quat = R.from_matrix(target_rotation).as_quat()
        seed_q = as_joint_vector(seed)
        sol = self.solver.solve(np.asarray(target_position, dtype=float), quat, seed=seed_q)
        if sol is None:
            return None
        return wrap_to_prev(seed_q, np.asarray(sol, dtype=float))

    def fk_matrix(self, joint_angles):
        return urdf_fk_matrix(joint_angles)

    def solve_differential(
        self,
        *,
        target_position=None,
        target_orientation_matrix=None,
        twist=None,
        current_q=None,
        dt=0.04,
    ):
        q = as_joint_vector(current_q)
        error = error_from_target_or_twist(
            fk_func=self.fk_matrix,
            current_q=q,
            target_position=target_position,
            target_orientation_matrix=target_orientation_matrix,
            twist=twist,
            dt=dt,
        )
        dq = dls_joint_step(fk_func=self.fk_matrix, current_q=q, pose_error=error)
        return differential_result_from_dq(q, dq, dt)
