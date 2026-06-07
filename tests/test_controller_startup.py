from gradient_os.run_controller import _validate_real_servo_startup


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
