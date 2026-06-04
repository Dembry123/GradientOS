"""Enable or disable torque on Gradient0 servos.

When torque is OFF the servos free-spin: you can manually pose the arm.
When torque is ON they hold whatever position they're currently at.

REQUIRES the main controller to be stopped first (it owns the serial port):
    pkill -f gradient_os.run_controller

Usage:
    python scripts/torque.py off    # disable, then you can move arm by hand
    python scripts/torque.py on     # re-enable, servos hold current pose
    python scripts/torque.py off --ids 40,50  # disable only J4/J5 wrist servos

SAFETY: physically support the arm before running `off` — without torque the
joints will sag under gravity and the arm can drop hard.
"""
import argparse
import sys
import time

import serial

from gradient_os.arm_controller.backends.feetech import config, protocol

EXPECTED = [10, 20, 21, 30, 31, 40, 50, 60, 100]


_OP_GAP_S = 0.003  # let the half-duplex bus settle between consecutive transactions


def _op_gap() -> None:
    time.sleep(_OP_GAP_S)


def engage_torque_hold(ser: serial.Serial, sid: int) -> bool:
    """Read current position, set it as target, then enable torque. Returns True on success."""
    pos = protocol.read_register_word(ser, sid, config.SERVO_ADDR_PRESENT_POSITION)
    if pos is None:
        return False
    _op_gap()
    if not protocol.write_register_word(ser, sid, config.SERVO_ADDR_TARGET_POSITION, pos):
        return False
    _op_gap()
    return protocol.write_register_byte(ser, sid, config.SERVO_ADDR_TORQUE_SWITCH, 1)


def disable_torque(ser: serial.Serial, sid: int) -> bool:
    ok = protocol.write_register_byte(ser, sid, config.SERVO_ADDR_TORQUE_SWITCH, 0)
    _op_gap()
    return ok


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["on", "off"])
    p.add_argument("--port", default="/dev/tty.usbserial-110")
    p.add_argument("--baud", type=int, default=config.DEFAULT_BAUD_RATE)
    p.add_argument(
        "--ids",
        default=",".join(str(sid) for sid in EXPECTED),
        help="Comma-separated servo IDs to affect. Defaults to every configured servo.",
    )
    args = p.parse_args()

    try:
        target_ids = [int(part.strip()) for part in args.ids.split(",") if part.strip()]
    except ValueError:
        print(f"FAIL: invalid --ids value {args.ids!r}", file=sys.stderr)
        return 2

    unknown_ids = [sid for sid in target_ids if sid not in EXPECTED]
    if unknown_ids:
        print(f"FAIL: unknown servo IDs {unknown_ids}; expected subset of {EXPECTED}", file=sys.stderr)
        return 2

    if not target_ids:
        print("FAIL: no servo IDs requested", file=sys.stderr)
        return 2

    enable = args.mode == "on"
    try:
        ser = serial.Serial(args.port, args.baud, timeout=0.1)
    except serial.SerialException as e:
        print(f"FAIL: could not open {args.port}: {e}", file=sys.stderr)
        print("If the controller is running, stop it first: "
              "pkill -f gradient_os.run_controller", file=sys.stderr)
        return 2

    time.sleep(0.1)
    ser.reset_input_buffer()

    label = "ENABLING" if enable else "DISABLING"
    print(f"{label} torque on {len(target_ids)} servos: {target_ids}")
    if not enable:
        print("WARNING: arm will go limp. Support it physically before continuing.")
        print("(Press Ctrl+C in the next 3 seconds to abort.)")
        try:
            time.sleep(3)
        except KeyboardInterrupt:
            print("aborted")
            return 1

    failures: list[int] = []
    for sid in target_ids:
        if enable:
            ok = engage_torque_hold(ser, sid)
            if ok:
                print(f"  servo {sid}: torque ON (target locked to current position)")
            else:
                print(f"  servo {sid}: FAILED to read position; torque not engaged")
                failures.append(sid)
        else:
            if disable_torque(ser, sid):
                print(f"  servo {sid}: torque OFF")
            else:
                print(f"  servo {sid}: FAILED to disable torque")
                failures.append(sid)
        time.sleep(0.01)

    ser.close()
    if failures:
        print(f"\nWARNING: torque engage failed on {failures}. Re-run, or these servos won't hold.")
        return 1
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
