import pytest

from gradient_os import run_controller


@pytest.fixture(autouse=True)
def restore_trajectory_state():
    original_state = run_controller.utils.trajectory_state.copy()
    yield
    run_controller.utils.trajectory_state.clear()
    run_controller.utils.trajectory_state.update(original_state)


def test_controller_active_commanding_state_tracks_motion_sources():
    run_controller.utils.trajectory_state["is_running"] = False
    run_controller.utils.trajectory_state["is_jogging"] = False
    run_controller.utils.trajectory_state["weld_active"] = False

    assert run_controller._controller_is_actively_commanding() is False

    run_controller.utils.trajectory_state["is_jogging"] = True
    assert run_controller._controller_is_actively_commanding() is True

    run_controller.utils.trajectory_state["is_jogging"] = False
    run_controller.utils.trajectory_state["is_running"] = True
    assert run_controller._controller_is_actively_commanding() is True

    run_controller.utils.trajectory_state["is_running"] = False
    run_controller.utils.trajectory_state["weld_active"] = True
    assert run_controller._controller_is_actively_commanding() is True
