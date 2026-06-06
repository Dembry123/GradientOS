import math

from gradient_os.arm_controller.backends.feetech import protocol
from gradient_os.arm_controller.backends.feetech import config
from gradient_os.arm_controller.backends.feetech.driver import FeetechBackend


def _backend() -> FeetechBackend:
    backend = FeetechBackend(
        {
            "servo_ids": [10, 20, 21],
            "logical_to_physical_map": {0: [0], 1: [1, 2]},
            "inverted_servo_ids": {21},
            "joint_limits_rad": [[-math.pi, math.pi], [-math.pi, math.pi]],
            "master_offsets_rad": [0.0, 0.0],
        }
    )
    backend._initialized = True
    backend._present_servo_ids = {10, 20, 21}
    backend._ser = object()
    return backend


def test_raw_to_joint_positions_handles_direct_and_inverted_actuators() -> None:
    backend = _backend()

    positions = backend.raw_to_joint_positions({
        10: 2047,
        20: 3071,
        21: 1023,
    })

    assert math.isclose(positions[0], 0.0, abs_tol=0.01)
    assert math.isclose(positions[1], math.pi / 2, abs_tol=0.01)


def test_prepare_sync_write_commands_maps_logical_joints_to_physical_actuators() -> None:
    backend = _backend()

    commands = backend.prepare_sync_write_commands([math.pi / 2, 0.0], speed=100, accel=0)

    by_id = {servo_id: raw for servo_id, raw, _speed, _accel in commands}
    assert set(by_id) == {10, 20, 21}
    assert by_id[10] == 3071
    assert by_id[20] == 2048
    assert by_id[21] == 2048


def test_set_joint_positions_uses_feetech_protocol(monkeypatch) -> None:
    backend = _backend()
    writes = []
    monkeypatch.setattr(protocol, "sync_write_goal_pos_speed_accel", lambda _ser, commands: writes.append(commands))

    backend.set_joint_positions([math.pi / 2, 0.0], speed=100, acceleration=0)

    assert writes
    commanded_ids = {cmd[0] for cmd in writes[0]}
    assert commanded_ids == {10, 20, 21}


def test_clear_hardware_zero_offsets_writes_position_correction(monkeypatch) -> None:
    backend = _backend()
    calls = []

    def write_byte(_ser, servo_id, register_address, value):
        calls.append(("byte", servo_id, register_address, value))
        return True

    def write_word(_ser, servo_id, register_address, value):
        calls.append(("word", servo_id, register_address, value))
        return True

    def read_word(_ser, servo_id, register_address):
        calls.append(("read_word", servo_id, register_address, None))
        return 0

    monkeypatch.setattr(protocol, "write_register_byte", write_byte)
    monkeypatch.setattr(protocol, "write_register_word", write_word)
    monkeypatch.setattr(protocol, "read_register_word", read_word)

    result = backend.clear_hardware_zero_offsets([10, 99])

    assert result == {10: True, 99: False}
    assert calls == [
        ("byte", 10, config.SERVO_ADDR_WRITE_LOCK, 0),
        ("word", 10, config.SERVO_ADDR_POSITION_CORRECTION, 0),
        ("byte", 10, config.SERVO_ADDR_WRITE_LOCK, 1),
        ("read_word", 10, config.SERVO_ADDR_POSITION_CORRECTION, None),
    ]
