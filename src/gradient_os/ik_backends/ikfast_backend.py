"""IKFast backend adapter."""

from __future__ import annotations

import numpy as np

from .base import IKBackend
from .common import (
    BackendUnavailable,
    END_EFFECTOR_OFFSET,
    as_joint_vector,
    as_rotation_matrix,
    differential_result_from_dq,
    dls_joint_step,
    error_from_target_or_twist,
    find_closest_solution,
)


class IKFastBackend(IKBackend):
    name = "ikfast"

    def __init__(self) -> None:
        from ikfast_solver.ikfast_wrapper import IKFastSolver

        try:
            self.solver = IKFastSolver()
        except (RuntimeError, OSError) as e:
            raise BackendUnavailable(f"Failed to load IKFast backend: {e}") from e
        self.num_joints = self.solver.num_joints
        self.legacy_solver = self.solver
        print(f"[IK Solver] IKFast back-end initialised for {self.num_joints} joints.")

    def solve_pose(self, target_position, target_orientation_matrix=None, seed=None):
        target_rotation = as_rotation_matrix(target_orientation_matrix)
        wrist_position = np.asarray(target_position, dtype=float) - target_rotation.dot(END_EFFECTOR_OFFSET)
        sol = self.solver.solve_ik(wrist_position, target_rotation.flatten(), seed)
        if sol is None:
            return None
        if seed is not None:
            try:
                return find_closest_solution(np.asarray(sol), np.asarray(seed, dtype=float))
            except Exception:
                return sol
        return sol

    def fk_matrix(self, joint_angles):
        wrist_t, wrist_r = self.solver.compute_fk(joint_angles)
        wrist_matrix = np.eye(4)
        wrist_matrix[:3, :3] = wrist_r.reshape(3, 3)
        wrist_matrix[:3, 3] = wrist_t

        offset_matrix = np.eye(4)
        offset_matrix[:3, 3] = END_EFFECTOR_OFFSET
        return wrist_matrix.dot(offset_matrix)

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

    def solve_path_batch(self, path_points, initial_joint_angles=None, target_orientations=None):
        num_poses = len(path_points)
        start_angles_np = np.array(
            initial_joint_angles if initial_joint_angles is not None else [0.0] * self.num_joints,
            dtype=np.float64,
        )
        poses_batch = np.zeros((num_poses, 12), dtype=np.float64)
        default_rotation = np.identity(3)
        for i in range(num_poses):
            target_rotation = (
                np.array(target_orientations[i]).reshape(3, 3)
                if target_orientations
                else default_rotation
            )
            wrist_position = np.array(path_points[i], dtype=float) - target_rotation.dot(END_EFFECTOR_OFFSET)
            poses_batch[i, :3] = wrist_position
            poses_batch[i, 3:] = target_rotation.flatten()
        return self.solver.solve_ik_path(poses_batch, start_angles_np)
