"""Read-only servo bus scanner.

Pings each expected Gradient0 servo ID plus a few likely factory-default IDs
and prints which respond. Does not write any registers.

Usage: python scripts/scan_servo_bus.py [--port /dev/tty.usbserial-110] [--baud 1000000]
"""
import argparse
import sys
import time

import serial

from gradient_os.arm_controller.backends.feetech import config, protocol

EXPECTED = [10, 20, 21, 30, 31, 40, 50, 60, 100]
FACTORY_DEFAULTS = [1, 2, 3]
JOINT_LABEL = {
    10: "J1 base",
    20: "J2 shoulder (primary)",
    21: "J2 shoulder (secondary)",
    30: "J3 elbow (primary)",
    31: "J3 elbow (secondary)",
    40: "J4 wrist roll",
    50: "J5 wrist pitch",
    60: "J6 wrist yaw",
    100: "gripper",
}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--port", default="/dev/tty.usbserial-110")
    p.add_argument("--baud", type=int, default=config.DEFAULT_BAUD_RATE)
    p.add_argument("--full-sweep", action="store_true",
                   help="Also sweep IDs 1..253 (slow, ~25s).")
    args = p.parse_args()

    try:
        ser = serial.Serial(args.port, args.baud, timeout=0.1)
    except serial.SerialException as e:
        print(f"FAIL: could not open {args.port}: {e}", file=sys.stderr)
        return 2

    time.sleep(0.1)  # CH340 needs time to settle after open or first frames are dropped
    ser.reset_input_buffer()
    print(f"Scanning on {args.port} @ {args.baud} baud\n")

    print("Expected Gradient0 servos:")
    present_expected: list[int] = []
    for sid in EXPECTED:
        ok = protocol.ping(ser, sid)
        tag = "PRESENT" if ok else "ABSENT "
        print(f"  [{tag}] ID {sid:>3}  ({JOINT_LABEL[sid]})")
        if ok:
            present_expected.append(sid)
        time.sleep(0.005)

    print("\nFactory-default IDs (any response here = unconfigured servo on bus):")
    factory_hits: list[int] = []
    for sid in FACTORY_DEFAULTS:
        ok = protocol.ping(ser, sid)
        tag = "RESPONDED" if ok else "silent   "
        print(f"  [{tag}] ID {sid}")
        if ok:
            factory_hits.append(sid)
        time.sleep(0.005)

    if args.full_sweep:
        print("\nFull sweep 4..253 (excluding already-tested IDs):")
        already = set(EXPECTED) | set(FACTORY_DEFAULTS)
        extra_hits: list[int] = []
        for sid in range(4, 254):
            if sid in already:
                continue
            if protocol.ping(ser, sid):
                print(f"  [HIT] ID {sid}")
                extra_hits.append(sid)
            time.sleep(0.003)
        if not extra_hits:
            print("  (nothing else on the bus)")

    print("\n--- Summary ---")
    print(f"Expected found:  {len(present_expected)} / {len(EXPECTED)}  -> {present_expected}")
    missing = [sid for sid in EXPECTED if sid not in present_expected]
    if missing:
        print(f"Missing:         {missing}")
        for sid in missing:
            print(f"                 - ID {sid} ({JOINT_LABEL[sid]})")
    else:
        print("Missing:         (none)")
    print(f"Factory-default: {factory_hits if factory_hits else '(none)'}")

    ser.close()
    return 0 if not missing and not factory_hits else 1


if __name__ == "__main__":
    sys.exit(main())
