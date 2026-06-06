"""Damped least-squares differential IK backend."""

from __future__ import annotations

from .common import dls_joint_step
from .differential_base import DifferentialIKBackendBase


class DlsBackend(DifferentialIKBackendBase):
    name = "dls"

    def __init__(self) -> None:
        print(f"[IK Solver] DLS differential back-end initialised for {self.num_joints} joints.")

    def joint_step(self, current_q, pose_error):
        return dls_joint_step(fk_func=self.fk_matrix, current_q=current_q, pose_error=pose_error)
