import json

import numpy as np
import pytest

from gradient_os.arm_controller import command_api


@pytest.fixture(autouse=True)
def restore_jog_state():
    original_state = command_api.utils.trajectory_state.copy()
    yield
    command_api.utils.trajectory_state.clear()
    command_api.utils.trajectory_state.update(original_state)


def test_jog_joint_target_uses_nearest_limited_wraparound_angle(monkeypatch):
    monkeypatch.setattr(
        command_api.utils,
        "LOGICAL_JOINT_LIMITS_RAD",
        [(-np.pi, np.pi)] * 6,
    )
    q_current = np.zeros(6)
    q_target = np.zeros(6)
    q_current[5] = np.deg2rad(179.0)
    q_target[5] = np.deg2rad(-179.0)

    q_limited, wrapped, limited = command_api._nearest_limited_joint_target(
        q_current,
        q_target,
    )

    assert wrapped[5]
    assert limited[5]
    assert q_limited[5] == pytest.approx(np.pi)
    assert abs(q_limited[5] - q_current[5]) < np.deg2rad(2.0)


def test_deadman_release_zeroes_velocity_without_stopping_jog(monkeypatch):
    command_api.utils.trajectory_state["is_jogging"] = True
    command_api.utils.trajectory_state["jog_deadman"] = True
    command_api.utils.trajectory_state["jog_velocities"] = np.ones(6, dtype=float)
    command_api.utils.trajectory_state["jog_gripper_velocity_deg_s"] = 12.0

    brake_calls = []
    monkeypatch.setattr(
        command_api,
        "_brake_to_current_position",
        lambda reason: brake_calls.append(reason) or True,
    )

    command_api.handle_set_jog_deadman(False)

    assert command_api.utils.trajectory_state["is_jogging"] is True
    assert command_api.utils.trajectory_state["jog_deadman"] is False
    np.testing.assert_allclose(command_api.utils.trajectory_state["jog_velocities"], np.zeros(6))
    assert command_api.utils.trajectory_state["jog_gripper_velocity_deg_s"] == 0.0
    assert brake_calls == ["deadman released"]


def test_jog_thread_rechecks_stop_before_servo_command(monkeypatch):
    command_api.utils.trajectory_state["is_jogging"] = True
    command_api.utils.trajectory_state["is_running"] = False
    command_api.utils.trajectory_state["jog_deadman"] = True
    command_api.utils.trajectory_state["jog_velocities"] = np.array([0.01, 0.0, 0.0, 0.0, 0.0, 0.0])
    command_api.utils.trajectory_state["jog_gripper_velocity_deg_s"] = 0.0
    command_api.utils.trajectory_state["last_jog_command_time"] = command_api.time.monotonic()
    command_api.utils.trajectory_state["jog_thread"] = None
    monkeypatch.setattr(
        command_api.utils,
        "LOGICAL_JOINT_LIMITS_RAD",
        [(-np.pi, np.pi)] * 6,
    )

    monkeypatch.setattr(
        command_api.actuators,
        "get_joint_positions",
        lambda verbose=False: np.zeros(6),
    )

    fk_matrix = np.eye(4)
    monkeypatch.setattr(command_api.ik_solver, "get_fk_matrix", lambda q: fk_matrix)

    def solve_ik(*, target_position, target_orientation_matrix, initial_joint_angles):
        command_api.utils.trajectory_state["jog_deadman"] = False
        command_api.utils.trajectory_state["is_jogging"] = False
        return np.full(6, 0.01)

    monkeypatch.setattr(command_api.ik_solver, "solve_ik", solve_ik)

    servo_commands = []
    monkeypatch.setattr(
        command_api.actuators,
        "set_joint_positions",
        lambda positions, speed, accel: servo_commands.append((positions, speed, accel)),
    )
    monkeypatch.setattr(command_api.time, "sleep", lambda seconds: None)

    command_api._jog_controller_thread()

    assert servo_commands == []
    assert command_api.utils.trajectory_state["is_jogging"] is False


def test_jog_debug_writes_diagnostic_record_for_ik_failure(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    command_api.utils.trajectory_state["is_jogging"] = True
    command_api.utils.trajectory_state["is_running"] = False
    command_api.utils.trajectory_state["jog_deadman"] = True
    command_api.utils.trajectory_state["jog_debug"] = True
    command_api.utils.trajectory_state["jog_mode"] = "absolute_pose"
    command_api.utils.trajectory_state["jog_target_position_m"] = np.array([0.1, 0.0, 0.0])
    command_api.utils.trajectory_state["jog_target_orientation_matrix"] = np.eye(3)
    command_api.utils.trajectory_state["last_jog_target_time"] = command_api.time.monotonic()
    command_api.utils.trajectory_state["last_jog_command_time"] = command_api.time.monotonic()
    command_api.utils.trajectory_state["jog_gripper_velocity_deg_s"] = 0.0
    command_api.utils.trajectory_state["jog_thread"] = None

    measured_q = np.zeros(6)
    monkeypatch.setattr(
        command_api.actuators,
        "get_joint_positions",
        lambda verbose=False: measured_q,
    )

    fk_matrix = np.eye(4)
    monkeypatch.setattr(command_api.ik_solver, "get_fk_matrix", lambda q: fk_matrix)

    def solve_ik(*, target_position, target_orientation_matrix, initial_joint_angles):
        command_api.utils.trajectory_state["is_jogging"] = False
        return None

    monkeypatch.setattr(command_api.ik_solver, "solve_ik", solve_ik)
    monkeypatch.setattr(command_api.time, "sleep", lambda seconds: None)

    command_api._jog_controller_thread()
    command_api._close_jog_diag_log()

    diag_files = list((tmp_path / "diagnostics" / "jog_motion").glob("jog_motion_*.jsonl"))
    assert len(diag_files) == 1
    records = [json.loads(line) for line in diag_files[0].read_text().splitlines()]

    assert records
    failure = records[-1]
    assert failure["event"] == "ik_failed"
    assert failure["target_position_m"] == pytest.approx([0.1, 0.0, 0.0])
    assert failure["current_position_m"] == pytest.approx([0.0, 0.0, 0.0])
    assert failure["q_current_rad"] == pytest.approx([0.0] * 6)
    assert failure["actual_joint_angles_rad"] == pytest.approx([0.0] * 6)
    assert failure["teleop_mode"] == "absolute_pose"
