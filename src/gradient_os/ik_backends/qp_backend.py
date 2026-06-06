"""Bounded QP differential IK backend."""

from __future__ import annotations

from .common import BackendUnavailable, lsq_linear, qp_joint_step
from .differential_base import DifferentialIKBackendBase


class QpBackend(DifferentialIKBackendBase):
    name = "qp"

    def __init__(self) -> None:
        if lsq_linear is None:
            raise BackendUnavailable("SciPy lsq_linear is unavailable; cannot run qp IK backend.")
        print(f"[IK Solver] QP differential back-end initialised for {self.num_joints} joints.")

    def joint_step(self, current_q, pose_error):
        return qp_joint_step(fk_func=self.fk_matrix, current_q=current_q, pose_error=pose_error)
