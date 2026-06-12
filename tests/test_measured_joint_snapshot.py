import pytest

from gradient_os.arm_controller import actuator_runtime, utils


@pytest.fixture(autouse=True)
def restore_measured_snapshot():
    original_current = list(utils.current_logical_joint_angles_rad)
    original_measured = list(utils.latest_measured_joint_angles_rad)
    original_mono = utils.latest_measured_joint_angles_monotonic
    original_wall = utils.latest_measured_joint_angles_wall_time
    original_source = utils.latest_measured_joint_angles_source
    yield
    utils.current_logical_joint_angles_rad = original_current
    utils.latest_measured_joint_angles_rad = original_measured
    utils.latest_measured_joint_angles_monotonic = original_mono
    utils.latest_measured_joint_angles_wall_time = original_wall
    utils.latest_measured_joint_angles_source = original_source


class _Backend:
    num_joints = 2
    is_initialized = True

    def __init__(self):
        self.commanded = None

    def set_joint_positions(self, positions, speed, acceleration):
        self.commanded = (list(positions), speed, acceleration)

    def get_joint_positions(self, verbose=False):
        return [0.3, 0.4]


def test_measured_joint_snapshot_round_trips_with_age_and_source():
    utils.update_latest_measured_joint_angles([0.1, 0.2], source="test_read")

    snapshot = utils.get_latest_measured_joint_snapshot()

    assert snapshot["valid"] is True
    assert snapshot["joints"] == [0.1, 0.2]
    assert snapshot["source"] == "test_read"
    assert snapshot["updated_at"] is not None
    assert snapshot["age_s"] >= 0.0


def test_actuator_writes_do_not_update_measured_joint_snapshot(monkeypatch):
    backend = _Backend()
    monkeypatch.setattr(actuator_runtime, "get_initialized_backend", lambda operation=None: backend)

    utils.update_latest_measured_joint_angles([0.1, 0.2], source="initial_read")
    assert actuator_runtime.set_joint_positions([1.0, 2.0], speed=100, acceleration=0)

    after_write = utils.get_latest_measured_joint_snapshot()
    assert after_write["joints"] == [0.1, 0.2]
    assert after_write["source"] == "initial_read"
    assert utils.current_logical_joint_angles_rad == [1.0, 2.0]

    measured = actuator_runtime.get_joint_positions(verbose=False)

    after_read = utils.get_latest_measured_joint_snapshot()
    assert measured == [0.3, 0.4]
    assert after_read["joints"] == [0.3, 0.4]
    assert after_read["source"] == "actuator_runtime.get_joint_positions"
