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

EXPECTED = [10, 20, 21, 30, 31, 40, 50, 60, 100]
HEADER = 0xFF
INSTR_WRITE = 0x03
INSTR_READ = 0x02
REG_TARGET_POSITION = 0x2A
REG_TORQUE_SWITCH = 0x28
REG_CURRENT_POSITION = 0x38


def _checksum(buf: bytes) -> int:
    return (~sum(buf)) & 0xFF


_OP_GAP_S = 0.003  # let the half-duplex bus settle between consecutive transactions


def read_word(ser: serial.Serial, sid: int, addr: int, retries: int = 5) -> int | None:
    """Half-duplex-safe register read.

    The CH340 adapter echoes our 8-byte TX onto the same RX line that the servo
    then replies on. So the byte stream is up to 16 bytes per request:
    [echo(8)] then [response(8)]. We read up to 24 bytes and scan for the
    response packet, distinguishing it from the echo by inspecting offset +4
    (which is INSTR_READ in an echo, error-flag in a response).
    """
    pkt = bytearray([HEADER, HEADER, sid, 4, INSTR_READ, addr, 2])
    pkt.append(_checksum(pkt[2:7]))
    for _ in range(retries):
        ser.reset_input_buffer()
        ser.write(pkt)
        # Wait long enough for echo + servo response delay (~500us default) +
        # response transmission. 5ms is generous at 1Mbps.
        time.sleep(0.005)
        resp = ser.read(24)
        time.sleep(_OP_GAP_S)
        # Scan the buffer for a valid response packet from this servo.
        for i in range(len(resp) - 7):
            if resp[i] != HEADER or resp[i + 1] != HEADER or resp[i + 2] != sid:
                continue
            if resp[i + 4] == INSTR_READ:
                # Echo of our own request — skip past it.
                continue
            return resp[i + 5] | (resp[i + 6] << 8)
    return None


def write_byte(ser: serial.Serial, sid: int, addr: int, value: int) -> None:
    pkt = bytearray([HEADER, HEADER, sid, 4, INSTR_WRITE, addr, value & 0xFF])
    pkt.append(_checksum(pkt[2:7]))
    ser.reset_input_buffer()
    ser.write(pkt)
    ser.read(6)
    time.sleep(_OP_GAP_S)


def write_word(ser: serial.Serial, sid: int, addr: int, value: int) -> None:
    lo = value & 0xFF
    hi = (value >> 8) & 0xFF
    pkt = bytearray([HEADER, HEADER, sid, 5, INSTR_WRITE, addr, lo, hi])
    pkt.append(_checksum(pkt[2:8]))
    ser.reset_input_buffer()
    ser.write(pkt)
    ser.read(6)
    time.sleep(_OP_GAP_S)


def engage_torque_hold(ser: serial.Serial, sid: int) -> bool:
    """Read current position, set it as target, then enable torque. Returns True on success."""
    pos = read_word(ser, sid, REG_CURRENT_POSITION)
    if pos is None:
        return False
    write_word(ser, sid, REG_TARGET_POSITION, pos)
    write_byte(ser, sid, REG_TORQUE_SWITCH, 1)
    return True


def disable_torque(ser: serial.Serial, sid: int) -> None:
    write_byte(ser, sid, REG_TORQUE_SWITCH, 0)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["on", "off"])
    p.add_argument("--port", default="/dev/tty.usbserial-110")
    p.add_argument("--baud", type=int, default=1_000_000)
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
            disable_torque(ser, sid)
            print(f"  servo {sid}: torque OFF")
        time.sleep(0.01)

    ser.close()
    if failures:
        print(f"\nWARNING: torque engage failed on {failures}. Re-run, or these servos won't hold.")
        return 1
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
