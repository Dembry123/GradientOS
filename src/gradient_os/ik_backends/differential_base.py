"""Shared base class for differential IK backends."""

from __future__ import annotations

from .base import IKBackend
from .common import (
    as_joint_vector,
    differential_result_from_dq,
    error_from_target_or_twist,
    iterative_differential_ik,
    urdf_fk_matrix,
)


class DifferentialIKBackendBase(IKBackend):
    """Common pose/differential plumbing for DLS-style and QP-style solvers."""

    num_joints = 6
    legacy_solver = None

    def fk_matrix(self, joint_angles):
        return urdf_fk_matrix(joint_angles)

    def solve_pose(self, target_position, target_orientation_matrix=None, seed=None):
        return iterative_differential_ik(
            method=self.name,
            fk_func=self.fk_matrix,
            target_position=target_position,
            target_orientation_matrix=target_orientation_matrix,
            initial_joint_angles=seed,
        )

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
        dq = self.joint_step(q, error)
        return differential_result_from_dq(q, dq, dt)

    def joint_step(self, current_q, pose_error):
        raise NotImplementedError
