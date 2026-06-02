"""Rename a single Feetech servo's hardware ID.

Writes a new ID to register 0x05 (EEPROM). The new ID persists across power cycles.

SAFETY: This tool refuses to run if (a) more than one device responds at the
source ID, or (b) any device already responds at the target ID. To rename a
factory-fresh servo (ID 1), physically disconnect all other ID-1 servos from
the daisy chain before running.

Usage:
    python scripts/set_servo_id.py --from 1 --to 31
    python scripts/set_servo_id.py --from 1 --to 100 [--port /dev/tty.usbserial-110]
"""
import argparse
import sys
import time

import serial

HEADER = 0xFF
INSTR_PING = 0x01
INSTR_WRITE = 0x03
REG_ID = 0x05
REG_WRITE_LOCK = 0x37

VALID_TARGETS = {10, 20, 21, 30, 31, 40, 50, 60, 100}
OP_GAP_S = 0.01
EEPROM_COMMIT_S = 0.15


def _checksum(packet_after_headers: bytes) -> int:
    return (~sum(packet_after_headers)) & 0xFF


def ping(ser: serial.Serial, sid: int) -> bool:
    pkt = bytearray([HEADER, HEADER, sid, 2, INSTR_PING])
    pkt.append(_checksum(pkt[2:5]))
    ser.reset_input_buffer()
    ser.write(pkt)
    resp = ser.read(6)
    return (
        len(resp) == 6
        and resp[0] == HEADER
        and resp[1] == HEADER
        and resp[2] == sid
    )


def write_register(ser: serial.Serial, sid: int, addr: int, value: int) -> None:
    """Single-byte register write. No response is awaited beyond input drain."""
    pkt = bytearray([HEADER, HEADER, sid, 4, INSTR_WRITE, addr, value])
    pkt.append(_checksum(pkt[2:7]))
    ser.reset_input_buffer()
    ser.write(pkt)
    ser.read(6)  # status packet (or whatever the bus echoes); discard
    time.sleep(OP_GAP_S)


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
    if not ping(ser, args.src):
        print("NO")
        print(f"FAIL: no device at ID {args.src}. Nothing to rename.", file=sys.stderr)
        return 1
    print("yes")

    print(f"  [check] is target ID {args.dst} already taken?", end=" ", flush=True)
    if ping(ser, args.dst):
        print("YES")
        print(f"FAIL: ID {args.dst} already in use. Refusing to write to avoid a collision.",
              file=sys.stderr)
        return 1
    print("no")

    print(f"  [check] confirm exactly one device at ID {args.src} (re-ping x5)...", end=" ", flush=True)
    hits = sum(1 for _ in range(5) if ping(ser, args.src))
    print(f"{hits}/5 responses")
    if hits < 5:
        print("WARN: not all probes succeeded. This may indicate a collision (multiple "
              "servos at the source ID) or a flaky cable. Proceeding anyway is risky — "
              "physically disconnect all but one ID-1 servo and rerun.", file=sys.stderr)
        return 1

    print(f"\n  [write] unlock EEPROM on ID {args.src}")
    write_register(ser, args.src, REG_WRITE_LOCK, 0)

    print(f"  [write] register 0x05 on ID {args.src} <- {args.dst}")
    write_register(ser, args.src, REG_ID, args.dst)
    time.sleep(EEPROM_COMMIT_S)  # let EEPROM commit

    print(f"  [verify] ping new ID {args.dst}...", end=" ", flush=True)
    new_ok = ping(ser, args.dst)
    print("ok" if new_ok else "FAIL")

    print(f"  [verify] confirm old ID {args.src} is gone...", end=" ", flush=True)
    old_gone = not ping(ser, args.src)
    print("ok" if old_gone else "STILL RESPONDS")

    if new_ok:
        print(f"  [write] relock EEPROM on ID {args.dst}")
        write_register(ser, args.dst, REG_WRITE_LOCK, 1)
        print(f"  [verify] ping relocked ID {args.dst}...", end=" ", flush=True)
        relock_ok = ping(ser, args.dst)
        print("ok" if relock_ok else "FAIL")
        new_ok = new_ok and relock_ok
    elif ping(ser, args.src):
        print(f"  [write] relock EEPROM on original ID {args.src}")
        write_register(ser, args.src, REG_WRITE_LOCK, 1)

    ser.close()

    if new_ok and old_gone:
        print(f"\nSUCCESS: servo is now at ID {args.dst}.")
        return 0
    print("\nFAIL: rename did not complete cleanly. Inspect physically and rerun scan.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
