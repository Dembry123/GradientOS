"""Backend interface for GradientOS inverse kinematics."""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from .common import DifferentialResult


class IKBackend(ABC):
    name: str
    num_joints: int = 6

    @abstractmethod
    def fk_matrix(self, joint_angles) -> np.ndarray | None:
        """Return public tool-frame FK as a 4x4 matrix."""

    @abstractmethod
    def solve_pose(self, target_position, target_orientation_matrix=None, seed=None) -> np.ndarray | None:
        """Return a full joint target for a public tool-frame target pose."""

    def solve_differential(
        self,
        *,
        target_position=None,
        target_orientation_matrix=None,
        twist=None,
        current_q=None,
        dt=0.04,
    ) -> DifferentialResult:
        raise NotImplementedError(f"Backend '{self.name}' does not expose differential IK.")

    def solve_path_batch(self, path_points, initial_joint_angles=None, target_orientations=None):
        return None
