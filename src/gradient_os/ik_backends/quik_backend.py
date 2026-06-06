"""QuIK/PyQuIK backend adapter."""

from __future__ import annotations

import os

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
    find_closest_solution,
    urdf_fk_matrix,
)


class QuikBackend(IKBackend):
    name = "quik"

    def __init__(self) -> None:
        from numeric_solver.numeric_wrapper import numeric_fk, numeric_ik, init_numeric_solver

        self._numeric_fk = numeric_fk
        self._numeric_ik = numeric_ik
        dh_path = os.getenv("MINI_ARM_DH_CSV", "mini-6dof-arm/dh_params.csv")
        try:
            kin, solver = init_numeric_solver(dh_path)
            self.num_joints = kin.num_joints if hasattr(kin, "num_joints") else 6
            self.legacy_solver = solver
            print(f"[IK Solver] QuIK/PyQuIK back-end initialised for {self.num_joints} joints.")
        except Exception as e:
            raise BackendUnavailable(f"Failed to load QuIK/PyQuIK backend: {e}") from e

        try:
            raw_zero = np.asarray(self._numeric_fk(np.zeros(self.num_joints)), dtype=float).reshape(4, 4)
            public_zero = urdf_fk_matrix(np.zeros(self.num_joints))
            self._internal_to_public = np.linalg.inv(raw_zero) @ public_zero
            self._public_to_internal = np.linalg.inv(self._internal_to_public)
        except Exception as e:
            raise BackendUnavailable(f"Failed to establish QuIK tool-frame transform: {e}") from e

    def solve_pose(self, target_position, target_orientation_matrix=None, seed=None):
        target_rotation = as_rotation_matrix(target_orientation_matrix)
        public_target = np.eye(4)
        public_target[:3, :3] = target_rotation
        public_target[:3, 3] = np.asarray(target_position, dtype=float)
        internal_target = public_target @ self._public_to_internal

        quat = R.from_matrix(internal_target[:3, :3]).as_quat()
        sol, _, _, _ = self._numeric_ik(quat, internal_target[:3, 3], seed)
        if sol is None:
            return None
        if seed is not None:
            try:
                return find_closest_solution(np.asarray(sol), np.asarray(seed, dtype=float))
            except Exception:
                return sol
        return sol

    def fk_matrix(self, joint_angles):
        return self._numeric_fk(joint_angles) @ self._internal_to_public

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
