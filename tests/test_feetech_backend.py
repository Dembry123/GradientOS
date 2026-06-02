import pytest

from gradient_os.arm_controller.backends.feetech import protocol
from gradient_os.arm_controller.backends.feetech.driver import FeetechBackend


def _backend() -> FeetechBackend:
    return FeetechBackend(
        {
            "servo_ids": [10, 20],
            "logical_to_physical_map": {0: [0], 1: [1]},
            "inverted_servo_ids": set(),
            "joint_limits_rad": [[-3.14, 3.14], [-3.14, 3.14]],
        }
    )


def test_raw_to_joint_positions_preserves_missing_joint_feedback():
    backend = _backend()
    backend._current_positions_rad = [1.25, -0.75]

    positions = backend.raw_to_joint_positions({10: 2047})

    assert positions[0] == pytest.approx(-0.000767, abs=1e-6)
    assert positions[1] == -0.75


def test_get_joint_positions_keeps_last_known_on_empty_syncread(monkeypatch):
    backend = _backend()
    backend._initialized = True
    backend._ser = object()
    backend._present_servo_ids = {10, 20}
    backend._current_positions_rad = [1.25, -0.75]
    backend._has_valid_position_read = True

    monkeypatch.setattr(protocol, "sync_read_positions", lambda *args, **kwargs: {})

    assert backend.get_joint_positions() == [1.25, -0.75]
