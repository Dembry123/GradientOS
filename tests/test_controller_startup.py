from gradient_os.arm_controller import utils
from gradient_os.run_controller import (
    _configure_startup_diagnostics,
    _validate_real_servo_startup,
)


class _Robot:
    actuator_ids = [10, 20, 21]


class _Backend:
    def __init__(self, present_ids):
        self._present_ids = set(present_ids)

    def get_present_actuator_ids(self):
        return set(self._present_ids)


def test_real_servo_startup_validation_requires_all_configured_actuators():
    assert not _validate_real_servo_startup(_Robot(), _Backend([10, 20]))


def test_real_servo_startup_validation_passes_when_all_configured_actuators_present():
    assert _validate_real_servo_startup(_Robot(), _Backend([10, 20, 21]))


def test_startup_diagnostics_env_toggles_controller_state(monkeypatch):
    original_state = utils.trajectory_state.copy()
    try:
        utils.trajectory_state["diagnostics_enabled"] = False
        utils.trajectory_state["jog_debug"] = False
        monkeypatch.setenv("MINI_ARM_IK_LOG", "1")
        monkeypatch.setenv("GRADIENT_JOG_DEBUG_LOG", "true")

        _configure_startup_diagnostics()

        assert utils.trajectory_state["diagnostics_enabled"] is True
        assert utils.trajectory_state["jog_debug"] is True
    finally:
        utils.trajectory_state.clear()
        utils.trajectory_state.update(original_state)
