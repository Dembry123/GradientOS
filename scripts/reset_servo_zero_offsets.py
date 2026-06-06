"""Reset Feetech hardware zero offsets through the active backend architecture.

This replaces the old archived ``reset_all_servo_offsets_to_zero`` helper. It
uses FeetechBackend instead of the removed servo_driver/servo_protocol shims.

Usage:
    python scripts/reset_servo_zero_offsets.py --read-only
    python scripts/reset_servo_zero_offsets.py --ids 10 20 21 --yes
"""

from __future__ import annotations

import argparse
import sys

from gradient_os.arm_controller import actuator_runtime as actuators
from gradient_os.arm_controller import robot_config, utils
from gradient_os.arm_controller.backends import registry as backend_registry
from gradient_os.arm_controller.robots import get_robot_config, list_available_robots


def _format_offsets(offsets: dict[int, int | None]) -> str:
    if not offsets:
        return "  (none)"
    return "\n".join(
        f"  ID {actuator_id:>3}: {offset if offset is not None else 'read failed'}"
        for actuator_id, offset in sorted(offsets.items())
    )


def _build_backend(args: argparse.Namespace):
    selected_robot = get_robot_config(args.robot)
    robot_config.set_active_robot(selected_robot)
    utils.SERIAL_PORT = args.serial_port or selected_robot.default_serial_port

    backend_registry.set_active_backend("feetech")
    utils._populate_servo_constants()

    backend = backend_registry.create_backend(
        backend_name="feetech",
        robot_config=selected_robot.get_config_dict(),
        serial_port=utils.SERIAL_PORT,
    )
    backend_registry.set_active_backend_instance(backend)

    if not backend.initialize():
        raise RuntimeError("Feetech backend initialization failed")

    actuators.sync_global_state_from_backend(backend)
    return backend


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read or clear Feetech hardware zero offset registers.",
    )
    parser.add_argument(
        "--robot",
        default="gradient0",
        choices=list_available_robots(),
        help="Robot configuration to use.",
    )
    parser.add_argument(
        "--serial-port",
        default=None,
        help="Override the robot's default Feetech serial port.",
    )
    parser.add_argument(
        "--ids",
        nargs="*",
        type=int,
        default=None,
        help="Actuator IDs to reset. Defaults to all detected Feetech actuators.",
    )
    parser.add_argument(
        "--read-only",
        action="store_true",
        help="Only print current hardware zero offsets.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the interactive destructive-operation confirmation.",
    )
    args = parser.parse_args()

    backend = None
    try:
        backend = _build_backend(args)
        target_ids = args.ids if args.ids else None

        before = actuators.read_hardware_zero_offsets(target_ids)
        print("Current hardware zero offsets:")
        print(_format_offsets(before))

        if args.read_only:
            return 0

        if not args.yes:
            print("\nThis writes 0 to the Feetech POSITION_CORRECTION EEPROM register.")
            confirmation = input("Type 'reset offsets' to continue: ").strip().lower()
            if confirmation != "reset offsets":
                print("Aborted.")
                return 2

        results = actuators.clear_hardware_zero_offsets(target_ids)
        print("\nClear results:")
        for actuator_id, ok in sorted(results.items()):
            print(f"  ID {actuator_id:>3}: {'ok' if ok else 'failed'}")

        after = actuators.read_hardware_zero_offsets(target_ids)
        print("\nHardware zero offsets after reset:")
        print(_format_offsets(after))

        return 0 if results and all(results.values()) else 1
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        if backend is not None:
            backend.shutdown()


if __name__ == "__main__":
    sys.exit(main())
