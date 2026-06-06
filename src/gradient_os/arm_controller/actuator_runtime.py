"""Runtime helpers for the active actuator backend.

This module is the small app-facing layer for motion code that needs to update
GradientOS global state while using the active ActuatorBackend directly.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from . import utils
from .actuator_interface import ActuatorBackend
from .backends import registry as backend_registry


def get_backend() -> Optional[ActuatorBackend]:
    """Return the active backend instance, or None before controller startup."""
    try:
        return backend_registry.get_active_backend()
    except backend_registry.BackendInstanceNotSetError:
        return None


def get_initialized_backend(operation: str | None = None) -> Optional[ActuatorBackend]:
    backend = get_backend()
    if backend is None:
        if operation:
            print(f"[Actuators] Cannot {operation}: no active backend instance.")
        return None
    if not backend.is_initialized:
        if operation:
            print(f"[Actuators] Cannot {operation}: backend is not initialized.")
        return None
    return backend


def sync_global_state_from_backend(backend: Optional[ActuatorBackend] = None) -> None:
    """Mirror backend presence/gripper state into legacy global runtime caches."""
    active = backend if backend is not None else get_initialized_backend()
    if active is None:
        return

    present_ids = active.get_present_actuator_ids()
    gripper_id = active.gripper_actuator_id
    utils.gripper_present = bool(gripper_id is not None and gripper_id in present_ids)

    serial_port = getattr(active, "serial_port", None)
    if serial_port is not None:
        utils.ser = serial_port


def set_joint_positions(
    positions_rad: list[float],
    speed: float,
    acceleration: float,
) -> bool:
    backend = get_initialized_backend("set joint positions")
    if backend is None:
        return False

    positions = list(positions_rad)
    if len(positions) != backend.num_joints:
        print(f"[Actuators] Expected {backend.num_joints} joint positions, got {len(positions)}.")
        return False

    utils.current_logical_joint_angles_rad = positions
    backend.set_joint_positions(positions, speed=float(speed), acceleration=float(acceleration))
    return True


def get_joint_positions(verbose: bool = True) -> list[float]:
    backend = get_initialized_backend("read joint positions")
    if backend is None:
        return list(utils.current_logical_joint_angles_rad)

    positions = backend.get_joint_positions(verbose=verbose)
    utils.current_logical_joint_angles_rad = list(positions)

    if verbose:
        angles_deg = np.rad2deg(positions)
        print(f"[Actuators] Current logical angles (deg): {np.round(angles_deg, 2)}")

    return positions


def prepare_sync_write_commands(
    positions_rad: list[float],
    speed: int = 4095,
    accel: int = 0,
) -> list[tuple]:
    backend = get_initialized_backend("prepare sync-write commands")
    if backend is None:
        return []
    return backend.prepare_sync_write_commands(list(positions_rad), speed=int(speed), accel=int(accel))


def sync_write(commands: list[tuple]) -> bool:
    backend = get_initialized_backend("sync write")
    if backend is None:
        return False
    backend.sync_write(commands)
    return True


def sync_read_positions(
    actuator_ids: Optional[list[int]] = None,
    timeout_s: Optional[float] = None,
) -> dict[int, int]:
    backend = get_initialized_backend("sync read positions")
    if backend is None:
        return {}
    return backend.sync_read_positions(actuator_ids=actuator_ids, timeout_s=timeout_s)


def raw_to_joint_positions(raw_positions: dict[int, int]) -> list[float]:
    backend = get_initialized_backend("convert raw positions")
    if backend is None:
        return list(utils.current_logical_joint_angles_rad)
    positions = backend.raw_to_joint_positions(raw_positions)
    utils.current_logical_joint_angles_rad = list(positions)
    return positions


def set_single_actuator_position(
    actuator_id: int,
    position_rad: float,
    speed: int,
    accel: int,
) -> bool:
    backend = get_initialized_backend("set single actuator position")
    if backend is None:
        return False
    backend.set_single_actuator_position(
        int(actuator_id),
        float(position_rad),
        speed=int(speed),
        accel=int(accel),
    )
    return True


def read_single_actuator_position(actuator_id: int) -> Optional[int]:
    backend = get_initialized_backend("read single actuator position")
    if backend is None:
        return None
    return backend.read_single_actuator_position(int(actuator_id))


def set_current_position_as_zero(actuator_id: int) -> bool:
    backend = get_initialized_backend("set actuator zero")
    if backend is None:
        return False
    if actuator_id not in backend.get_present_actuator_ids():
        print(f"[Actuators] Cannot set zero for absent actuator {actuator_id}.")
        return False
    return bool(backend.set_current_position_as_zero(int(actuator_id)))


def set_pid_gains(actuator_id: int, kp: int, ki: int, kd: int) -> bool:
    backend = get_initialized_backend("set PID gains")
    if backend is None:
        return False
    return bool(backend.set_pid_gains(int(actuator_id), int(kp), int(ki), int(kd)))


def apply_joint_limits() -> bool:
    backend = get_initialized_backend("apply joint limits")
    if backend is None:
        return False
    return bool(backend.apply_joint_limits())


def get_gripper_position() -> Optional[float]:
    backend = get_initialized_backend("read gripper position")
    if backend is None or not backend.has_gripper:
        return None
    position = backend.get_gripper_position()
    if position is not None:
        utils.current_gripper_angle_rad = float(position)
    return position


def get_present_actuator_ids() -> set[int]:
    backend = get_initialized_backend()
    if backend is None:
        return set()
    return set(backend.get_present_actuator_ids())


def factory_reset_actuator(actuator_id: int) -> bool:
    backend = get_initialized_backend("factory reset actuator")
    if backend is None or not hasattr(backend, "factory_reset_actuator"):
        return False
    return bool(backend.factory_reset_actuator(int(actuator_id)))  # type: ignore[attr-defined]


def restart_actuator(actuator_id: int) -> bool:
    backend = get_initialized_backend("restart actuator")
    if backend is None or not hasattr(backend, "restart_actuator"):
        return False
    return bool(backend.restart_actuator(int(actuator_id)))  # type: ignore[attr-defined]


def sync_read_block(
    actuator_ids: list[int],
    start_address: int,
    data_len: int,
    timeout_s: Optional[float] = None,
    poll_delay_s: float = 0.0,
    diagnostics: bool = False,
) -> dict[int, bytes]:
    backend = get_initialized_backend("sync read telemetry block")
    if backend is None or not hasattr(backend, "sync_read_block"):
        return {}
    return backend.sync_read_block(  # type: ignore[attr-defined]
        list(actuator_ids),
        start_address=start_address,
        data_len=data_len,
        timeout_s=timeout_s,
        poll_delay_s=poll_delay_s,
        diagnostics=diagnostics,
    )


def get_sync_profiles() -> list[tuple[float, float, float]]:
    backend = get_initialized_backend()
    if backend is None or not hasattr(backend, "get_sync_profiles"):
        return []
    return backend.get_sync_profiles()  # type: ignore[attr-defined]


def read_hardware_zero_offsets(
    actuator_ids: Optional[list[int]] = None,
) -> dict[int, Optional[int]]:
    backend = get_initialized_backend()
    if backend is None or not hasattr(backend, "read_hardware_zero_offsets"):
        return {}
    return backend.read_hardware_zero_offsets(actuator_ids)  # type: ignore[attr-defined]


def clear_hardware_zero_offsets(
    actuator_ids: Optional[list[int]] = None,
) -> dict[int, bool]:
    backend = get_initialized_backend("clear hardware zero offsets")
    if backend is None or not hasattr(backend, "clear_hardware_zero_offsets"):
        return {}
    return backend.clear_hardware_zero_offsets(actuator_ids)  # type: ignore[attr-defined]
