"""QuIK/PyQuIK backend adapter."""

from __future__ import annotations

import importlib
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
    find_closest_solution,
    urdf_fk_matrix,
)


def _load_pyquik():
    try:
        return importlib.import_module("pyquik")
    except ImportError:
        return importlib.import_module("numeric_solver.pyquik.pyquik")


class QuikBackend(IKBackend):
    name = "quik"

    def __init__(self) -> None:
        dh_path = os.getenv("MINI_ARM_DH_CSV", "mini-6dof-arm/dh_params.csv")
        try:
            self._pyquik = _load_pyquik()
            self._robot, self._solver = self._init_quik_solver(dh_path)
            self.num_joints = int(getattr(self._robot, "num_joints", getattr(self._robot, "dof", 6)))
            print(f"[IK Solver] QuIK/PyQuIK back-end initialised for {self.num_joints} joints.")
        except Exception as e:
            raise BackendUnavailable(f"Failed to load QuIK/PyQuIK backend: {e}") from e

        try:
            raw_zero = np.asarray(self._quik_fk(np.zeros(self.num_joints)), dtype=float).reshape(4, 4)
            public_zero = urdf_fk_matrix(np.zeros(self.num_joints))
            self._internal_to_public = np.linalg.inv(raw_zero) @ public_zero
            self._public_to_internal = np.linalg.inv(self._internal_to_public)
        except Exception as e:
            raise BackendUnavailable(f"Failed to establish QuIK tool-frame transform: {e}") from e

    def _init_quik_solver(self, dh_csv_path: str):
        dh_path = Path(dh_csv_path)
        if not dh_path.is_file():
            dh_path = Path(__file__).resolve().parents[3] / dh_csv_path
        if not dh_path.is_file():
            raise FileNotFoundError(f"DH CSV not found at {dh_csv_path} or {dh_path}")

        dh_params = np.genfromtxt(str(dh_path), delimiter=",", skip_header=1, usecols=(1, 2, 3, 4), dtype=float)
        link_types = [0] * dh_params.shape[0]
        q_sign = np.ones(dh_params.shape[0])
        robot = self._pyquik.Robot(dh_params, link_types, q_sign, np.identity(4), np.identity(4))
        try:
            solver = self._pyquik.IKSolver(robot)
        except Exception as e:
            raise RuntimeError(f"Failed to create pyquik.IKSolver: {e}") from e
        return robot, solver

    def _quik_fk(self, joint_angles):
        q = np.asarray(joint_angles, dtype=float)
        if hasattr(self._robot, "fk"):
            return self._robot.fk(q)
        return self._robot.FK(q)

    def _quik_ik(self, quat, pos, seed=None):
        q_seed = np.zeros(self.num_joints, dtype=float) if seed is None else np.asarray(seed, dtype=float)
        if hasattr(self._solver, "ik"):
            return self._solver.ik(quat, pos, q_seed)
        q_vec, e_vec, iters, reason = self._solver.solve(quat, pos, q_seed)
        return (
            np.asarray(q_vec, dtype=float),
            np.asarray(e_vec, dtype=float),
            iters,
            reason,
        )

    def solve_pose(self, target_position, target_orientation_matrix=None, seed=None):
        target_rotation = as_rotation_matrix(target_orientation_matrix)
        public_target = np.eye(4)
        public_target[:3, :3] = target_rotation
        public_target[:3, 3] = np.asarray(target_position, dtype=float)
        internal_target = public_target @ self._public_to_internal

        quat = R.from_matrix(internal_target[:3, :3]).as_quat()
        sol, _, _, _ = self._quik_ik(quat, internal_target[:3, 3], seed)
        if sol is None:
            return None
        if seed is not None:
            try:
                return find_closest_solution(np.asarray(sol), np.asarray(seed, dtype=float))
            except Exception:
                return sol
        return sol

    def fk_matrix(self, joint_angles):
        return self._quik_fk(joint_angles) @ self._internal_to_public

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
