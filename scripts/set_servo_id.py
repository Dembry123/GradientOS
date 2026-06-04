"""Rename a single Feetech servo's hardware ID.

Writes a new ID to the Feetech ID EEPROM register. The new ID persists across
power cycles.

SAFETY: This protocol cannot prove how many physical servos share the same
source ID. To rename a factory-fresh servo (ID 1), physically disconnect all
other ID-1 servos from the daisy chain before running. This tool verifies that
the source ID responds stably and the target ID is not already occupied.

Usage:
    python scripts/set_servo_id.py --from 1 --to 31
    python scripts/set_servo_id.py --from 1 --to 100 [--port /dev/tty.usbserial-110]
"""
import argparse
import sys
import time

import serial

from gradient_os.arm_controller.backends.feetech import config, protocol

VALID_TARGETS = {10, 20, 21, 30, 31, 40, 50, 60, 100}
OP_GAP_S = 0.01
EEPROM_COMMIT_S = 0.15


def write_register(ser: serial.Serial, sid: int, addr: int, value: int) -> bool:
    ok = protocol.write_register_byte(ser, sid, addr, value)
    time.sleep(OP_GAP_S)
    return ok


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="src", type=int, required=True, help="Current ID")
    p.add_argument("--to", dest="dst", type=int, required=True, help="Target ID")
    p.add_argument("--port", default="/dev/tty.usbserial-110")
    p.add_argument("--baud", type=int, default=1_000_000)
    p.add_argument("--force", action="store_true",
                   help="Allow target IDs outside the canonical Gradient0 set.")
    args = p.parse_args()

    if not (0 < args.src < 254) or not (0 < args.dst < 254):
        print("FAIL: IDs must be in 1..253", file=sys.stderr)
        return 2
    if args.src == args.dst:
        print("FAIL: --from and --to are equal", file=sys.stderr)
        return 2
    if args.dst not in VALID_TARGETS and not args.force:
        print(f"FAIL: target ID {args.dst} is not in the Gradient0 canonical set "
              f"{sorted(VALID_TARGETS)}. Use --force to override.", file=sys.stderr)
        return 2

    try:
        ser = serial.Serial(args.port, args.baud, timeout=0.1)
    except serial.SerialException as e:
        print(f"FAIL: could not open {args.port}: {e}", file=sys.stderr)
        return 2

    time.sleep(0.1)  # CH340 settle
    ser.reset_input_buffer()

    print(f"Renaming servo {args.src} -> {args.dst} on {args.port}\n")

    print(f"  [check] does ID {args.src} respond?", end=" ", flush=True)
    if not protocol.ping(ser, args.src):
        print("NO")
        print(f"FAIL: no device at ID {args.src}. Nothing to rename.", file=sys.stderr)
        return 1
    print("yes")

    print(f"  [check] is target ID {args.dst} already taken?", end=" ", flush=True)
    if protocol.ping(ser, args.dst):
        print("YES")
        print(f"FAIL: ID {args.dst} already in use. Refusing to write to avoid a collision.",
              file=sys.stderr)
        return 1
    print("no")

    print(f"  [check] confirm stable communication with ID {args.src} (re-ping x5)...", end=" ", flush=True)
    hits = sum(1 for _ in range(5) if protocol.ping(ser, args.src))
    print(f"{hits}/5 responses")
    if hits < 5:
        print("WARN: not all probes succeeded. This may indicate an ID collision, "
              "bus echo/noise, or a flaky cable. Proceeding anyway is risky; "
              "physically disconnect all but one ID-1 servo and rerun.", file=sys.stderr)
        return 1

    print(f"\n  [write] unlock EEPROM on ID {args.src}")
    if not write_register(ser, args.src, config.SERVO_ADDR_WRITE_LOCK, 0):
        print("FAIL", file=sys.stderr)
        return 1

    print(f"  [write] register 0x{config.SERVO_ADDR_ID:02X} on ID {args.src} <- {args.dst}")
    if not write_register(ser, args.src, config.SERVO_ADDR_ID, args.dst):
        print("FAIL", file=sys.stderr)
        return 1
    time.sleep(EEPROM_COMMIT_S)  # let EEPROM commit

    print(f"  [verify] ping new ID {args.dst}...", end=" ", flush=True)
    new_ok = protocol.ping(ser, args.dst)
    print("ok" if new_ok else "FAIL")

    print(f"  [verify] confirm old ID {args.src} is gone...", end=" ", flush=True)
    old_gone = not protocol.ping(ser, args.src)
    print("ok" if old_gone else "STILL RESPONDS")

    if new_ok:
        print(f"  [write] relock EEPROM on ID {args.dst}")
        relock_write_ok = write_register(ser, args.dst, config.SERVO_ADDR_WRITE_LOCK, 1)
        print(f"  [verify] ping relocked ID {args.dst}...", end=" ", flush=True)
        relock_ok = relock_write_ok and protocol.ping(ser, args.dst)
        print("ok" if relock_ok else "FAIL")
        new_ok = new_ok and relock_ok
    elif protocol.ping(ser, args.src):
        print(f"  [write] relock EEPROM on original ID {args.src}")
        write_register(ser, args.src, config.SERVO_ADDR_WRITE_LOCK, 1)

    ser.close()

    if new_ok and old_gone:
        print(f"\nSUCCESS: servo is now at ID {args.dst}.")
        return 0
    print("\nFAIL: rename did not complete cleanly. Inspect physically and rerun scan.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
