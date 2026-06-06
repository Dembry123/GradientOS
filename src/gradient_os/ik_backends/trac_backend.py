"""TRAC-IK backend adapter."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Sequence

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
            from trac_ik_python.trac_ik import IK  # type: ignore
        except Exception as e:
            raise BackendUnavailable(f"Failed to import trac_ik_python: {e}") from e

        urdf_path = Path(__file__).resolve().parents[3] / "mini-6dof-arm" / "mini-6dof-arm.urdf"
        try:
            urdf_string = urdf_path.read_text(encoding="utf-8")
            self._ik = IK(
                "base",
                "tool_link",
                urdf_string=urdf_string,
                timeout=float(os.getenv("MINI_ARM_TRAC_TIMEOUT_S", "0.008")),
                epsilon=float(os.getenv("MINI_ARM_TRAC_EPSILON", "1e-5")),
            )
            self.joint_names = tuple(self._ik.joint_names)
            self.link_names = tuple(self._ik.link_names)
            self.num_joints = int(self._ik.number_of_joints)
            print(f"[IK Solver] TRAC-IK back-end initialised for {self.num_joints} joints.")
        except Exception as e:
            raise BackendUnavailable(f"Failed to load TRAC-IK backend: {e}") from e

    def _get_joint_limits(self) -> tuple[np.ndarray, np.ndarray]:
        lower, upper = self._ik.get_joint_limits()
        return np.asarray(lower, dtype=float), np.asarray(upper, dtype=float)

    def set_joint_limits(self, lower: Sequence[float], upper: Sequence[float]) -> None:
        self._ik.set_joint_limits(lower, upper)

    def _solve_trac(
        self,
        position: np.ndarray,
        orientation: np.ndarray,
        *,
        seed: Optional[np.ndarray] = None,
        pos_bounds: Optional[np.ndarray] = None,
        rot_bounds: Optional[np.ndarray] = None,
    ) -> np.ndarray | None:
        position = np.asarray(position, dtype=float)
        orientation = np.asarray(orientation, dtype=float)
        if position.shape != (3,):
            raise ValueError("`position` must be shape (3,)")
        if orientation.shape != (4,):
            raise ValueError("`orientation` must be shape (4,)")

        if seed is None:
            lower, upper = self._get_joint_limits()
            seed_arr = (lower + upper) / 2.0
        else:
            seed_arr = np.asarray(seed, dtype=float)
            if seed_arr.shape != (self.num_joints,):
                raise ValueError(f"`seed` must be shape ({self.num_joints},) but is {seed_arr.shape}")

        result = self._ik.get_ik(
            seed_arr.tolist(),
            *position.tolist(),
            *orientation.tolist(),
            *(pos_bounds.tolist() if pos_bounds is not None else []),
            *(rot_bounds.tolist() if rot_bounds is not None else []),
        )
        if result is None:
            return None
        return np.asarray(result, dtype=float)

    def solve_pose(self, target_position, target_orientation_matrix=None, seed=None):
        target_rotation = as_rotation_matrix(target_orientation_matrix)
        quat = R.from_matrix(target_rotation).as_quat()
        seed_q = as_joint_vector(seed)
        sol = self._solve_trac(np.asarray(target_position, dtype=float), quat, seed=seed_q)
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
