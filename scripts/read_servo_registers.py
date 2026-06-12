"""Read the documented STS3215 control-table registers from Gradient0 servos.

This tool is read-only. It opens the Feetech serial bus directly and does not
initialize the GradientOS backend, because backend initialization writes PID
defaults to the servos.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import glob
import os
import platform
import sys
import time
from typing import Callable

import serial


DEFAULT_SERVO_IDS = (10, 20, 21, 30, 31, 40, 50, 60, 100)
FACTORY_DEFAULT_SERVO_IDS = (1, 2, 3)
DEFAULT_BAUD_RATE = 1_000_000
DEFAULT_TIMEOUT_S = 0.1
CURRENT_SCALE_FACTOR = 0.0065

SERVO_HEADER = 0xFF
SERVO_INSTRUCTION_PING = 0x01
SERVO_INSTRUCTION_READ = 0x02

STATUS_BIT_NAMES = {
    0x01: "Input Voltage",
    0x02: "Angle Limit",
    0x04: "Overheating",
    0x08: "Range",
    0x10: "Checksum",
    0x20: "Overload",
    0x40: "Instruction",
}
ALARM_BIT_NAMES = {
    0: "Overload",
    1: "Overheat",
    2: "Overvoltage",
    3: "Undervoltage",
    4: "Stall",
    5: "Position Fault",
    6: "Comm/Error",
    7: "Unknown",
}
MACOS_USB_SERIAL_PATTERNS = (
    "/dev/cu.usbserial*",
    "/dev/cu.usbmodem*",
    "/dev/cu.SLAB_USBtoUART*",
    "/dev/cu.wchusbserial*",
    "/dev/cu.CH34*",
)
LINUX_USB_SERIAL_PATTERNS = (
    "/dev/serial/by-id/usb-*",
    "/dev/ttyUSB*",
    "/dev/ttyACM*",
)
SERVO_LABELS = {
    10: "J1 base",
    20: "J2 shoulder primary",
    21: "J2 shoulder secondary",
    30: "J3 elbow primary",
    31: "J3 elbow secondary",
    40: "J4 wrist roll",
    50: "J5 wrist pitch",
    60: "J6 wrist yaw",
    100: "gripper",
}

BAUD_RATE_BY_REGISTER = {
    0: 9_600,
    1: 19_200,
    2: 38_400,
    3: 57_600,
    4: 115_200,
    5: 250_000,
    6: 500_000,
    7: 1_000_000,
}


@dataclass(frozen=True)
class Register:
    addr: int
    size: int
    access: str
    name: str
    meaning: str
    decoder: Callable[[int], str] | None = None


def _u16_to_i16(value: int) -> int:
    return value - 0x10000 if value & 0x8000 else value


def _decode_baud(value: int) -> str:
    baud = BAUD_RATE_BY_REGISTER.get(value)
    return f"{value} ({baud} bps)" if baud else f"{value} (unknown baud index)"


def _decode_delay(value: int) -> str:
    return f"{value} ({value * 2} us)"


def _decode_voltage(value: int) -> str:
    return f"{value} ({value / 10.0:.1f} V)"


def _decode_temperature(value: int) -> str:
    return f"{value} ({value} deg C)"


def _decode_current(value: int) -> str:
    signed = _u16_to_i16(value)
    return f"{value} ({signed}; {signed * CURRENT_SCALE_FACTOR:.3f} A)"


def _decode_signed_word(value: int) -> str:
    return f"{value} ({_u16_to_i16(value)} signed)"


def _decode_alarm_bits(value: int) -> str:
    names = [ALARM_BIT_NAMES.get(i, f"b{i}") for i in range(8) if ((value >> i) & 1) == 1]
    suffix = ", ".join(names) if names else "none"
    return f"{value} ({suffix})"


def _decode_status_bits(value: int) -> str:
    names = [name for bit, name in STATUS_BIT_NAMES.items() if value & bit]
    suffix = ", ".join(names) if names else "none"
    return f"{value} ({suffix})"


def _decode_enabled(value: int) -> str:
    if value == 0:
        return "0 (off)"
    if value == 1:
        return "1 (on)"
    return str(value)


REGISTERS: tuple[Register, ...] = (
    Register(0x00, 1, "R", "Firmware Version Low", "Firmware version low byte"),
    Register(0x01, 1, "R", "Firmware Version High", "Firmware version high byte"),
    Register(0x03, 1, "R", "Servo Model Low", "Servo model low byte"),
    Register(0x04, 1, "R", "Servo Model High", "Servo model high byte"),
    Register(0x05, 1, "R/W", "ID", "Servo ID; 0xFE is broadcast"),
    Register(0x06, 1, "R/W", "Baud Rate", "Serial baud-rate index", _decode_baud),
    Register(0x07, 1, "R/W", "Response Delay Time", "Reply delay in 2 us units", _decode_delay),
    Register(0x08, 1, "R/W", "Response Status Level", "0 ping only, 1 read only, 2 all writes/read"),
    Register(0x09, 2, "R/W", "Minimum Angle Limit", "Minimum position-mode angle limit in raw steps"),
    Register(0x0B, 2, "R/W", "Maximum Angle Limit", "Maximum position-mode angle limit in raw steps"),
    Register(0x0D, 1, "R/W", "Max Temperature Limit", "Shutdown/alarm temperature limit in deg C", _decode_temperature),
    Register(0x0E, 1, "R/W", "Max Input Voltage", "Maximum input voltage limit in 0.1 V units", _decode_voltage),
    Register(0x0F, 1, "R/W", "Min Input Voltage", "Minimum input voltage limit in 0.1 V units", _decode_voltage),
    Register(0x10, 2, "R/W", "Max Torque", "EEPROM maximum torque, 0-1000 = 0-100%"),
    Register(0x13, 1, "R/W", "Unloading Condition", "Alarm conditions that can unload/disable torque", _decode_alarm_bits),
    Register(0x14, 1, "R/W", "LED Alarm Condition", "Alarm conditions that light the servo LED", _decode_alarm_bits),
    Register(0x15, 1, "R/W", "Position Kp Gain", "Position controller proportional gain"),
    Register(0x16, 1, "R/W", "Position Kd Gain", "Position controller derivative gain"),
    Register(0x17, 1, "R/W", "Position Ki Gain", "Position controller integral gain"),
    Register(0x18, 2, "R/W", "Min Startup Force", "Minimum startup force or punch"),
    Register(0x1A, 1, "R/W", "CW Insensitive Area", "Clockwise deadband in steps"),
    Register(0x1B, 1, "R/W", "CCW Insensitive Area", "Counter-clockwise deadband in steps"),
    Register(0x1C, 2, "R/W", "Current Protection Threshold", "Overcurrent threshold in 6.5 mA units", _decode_current),
    Register(0x1E, 1, "R/W", "Angular Resolution", "Angle resolution multiplier"),
    Register(0x1F, 2, "R/W", "Position Correction", "Persistent hardware zero offset in steps", _decode_signed_word),
    Register(0x20, 1, "R/W", "LED Control", "Servo LED control", _decode_enabled),
    Register(0x21, 1, "R/W", "Operation Mode", "0 position, 1 velocity closed-loop, 2 velocity open-loop, 3 step"),
    Register(0x22, 1, "R/W", "Torque Protection Threshold", "Overload torque threshold percentage"),
    Register(0x23, 1, "R/W", "Torque Protection Time", "Overload protection time in 10 ms units"),
    Register(0x24, 1, "R/W", "Overload Torque", "Overload torque percentage of max torque"),
    Register(0x25, 1, "R/W", "Speed Kp Gain", "Velocity controller proportional gain"),
    Register(0x26, 1, "R/W", "Overcurrent Time", "Overcurrent protection time in 10 ms units"),
    Register(0x27, 1, "R/W", "Speed Ki Gain", "Velocity controller integral gain"),
    Register(0x28, 1, "R/W", "Torque Switch", "Torque enable flag", _decode_enabled),
    Register(0x29, 1, "R/W", "Target Acceleration", "Target acceleration register; 0 disables accel control"),
    Register(0x2A, 2, "R/W", "Target Position", "Commanded target position in raw steps"),
    Register(0x2C, 2, "R/W", "Running Time", "Commanded time to target in ms; 0 uses speed control"),
    Register(0x2E, 2, "R/W", "Running Speed", "Commanded speed register"),
    Register(0x30, 2, "R/W", "Torque Limit", "RAM torque limit, 0-1000 = 0-100%"),
    Register(0x37, 1, "R/W", "Write Lock", "0 EEPROM writable, 1 EEPROM locked"),
    Register(0x38, 2, "R", "Current Position", "Measured present position in raw steps", _decode_signed_word),
    Register(0x3A, 2, "R", "Current Speed", "Measured present speed", _decode_signed_word),
    Register(0x3C, 2, "R", "Current Drive Voltage", "Measured load or drive duty register"),
    Register(0x3E, 1, "R", "Current Voltage", "Measured input voltage in 0.1 V units", _decode_voltage),
    Register(0x3F, 1, "R", "Current Temperature", "Measured internal temperature in deg C", _decode_temperature),
    Register(0x40, 1, "R", "Asynchronous Write Flag", "0 no RegWrite pending, 1 RegWrite pending"),
    Register(0x41, 1, "R", "Status", "Hardware error status bits", _decode_status_bits),
    Register(0x42, 1, "R", "Moving Status", "0 stopped/in position, 1 moving"),
    Register(0x45, 2, "R", "Current Current", "Measured current in 6.5 mA units", _decode_current),
)


def parse_ids(raw: str) -> list[int]:
    ids: list[int] = []
    for token in raw.replace(",", " ").split():
        servo_id = int(token, 0)
        if not 0 < servo_id < 254:
            raise argparse.ArgumentTypeError(f"servo ID {servo_id} is outside 1..253")
        if servo_id not in ids:
            ids.append(servo_id)
    if not ids:
        raise argparse.ArgumentTypeError("expected at least one servo ID")
    return ids


def resolve_port(explicit_port: str | None) -> str:
    if explicit_port:
        return explicit_port
    env_port = os.environ.get("SERIAL_PORT")
    if env_port:
        return env_port
    discovered = discover_default_serial_port()
    if discovered:
        return discovered
    raise RuntimeError("No serial port found. Pass --port /dev/...")


def discover_default_serial_port() -> str | None:
    patterns = MACOS_USB_SERIAL_PATTERNS if platform.system() == "Darwin" else LINUX_USB_SERIAL_PATTERNS
    candidates: list[str] = []
    seen_realpaths: set[str] = set()
    for pattern in patterns:
        for path in sorted(glob.glob(pattern)):
            realpath = os.path.realpath(path)
            if realpath in seen_realpaths or not os.path.exists(realpath):
                continue
            seen_realpaths.add(realpath)
            candidates.append(path)

    try:
        from serial.tools import list_ports

        for port in list_ports.comports():
            device = getattr(port, "device", None)
            if not device:
                continue
            lower = device.lower()
            if platform.system() == "Darwin":
                is_candidate = device.startswith("/dev/cu.") and (
                    getattr(port, "vid", None) is not None
                    or any(token in lower for token in ("usb", "serial", "slab", "wch", "ch34", "modem"))
                )
            else:
                is_candidate = (
                    getattr(port, "vid", None) is not None
                    or device.startswith("/dev/ttyUSB")
                    or device.startswith("/dev/ttyACM")
                    or device.startswith("/dev/serial/by-id/usb-")
                )
            if not is_candidate:
                continue
            realpath = os.path.realpath(device)
            if realpath in seen_realpaths or not os.path.exists(realpath):
                continue
            seen_realpaths.add(realpath)
            candidates.append(device)
    except Exception:
        pass

    return candidates[0] if candidates else None


def calculate_checksum(packet_data: bytes | bytearray) -> int:
    return (~sum(packet_data)) & 0xFF


def build_instruction_packet(servo_id: int, instruction: int, params: bytes = b"") -> bytearray:
    packet = bytearray([SERVO_HEADER, SERVO_HEADER, servo_id, len(params) + 2, instruction])
    packet.extend(params)
    packet.append(calculate_checksum(packet[2:]))
    return packet


def find_status_packet(
    response: bytes,
    servo_id: int,
    expected_data_len: int,
    command: bytes | None = None,
) -> bytes | None:
    expected_length = expected_data_len + 2
    frame_len = expected_length + 4
    if len(response) < frame_len:
        return None

    for idx in range(len(response) - frame_len + 1):
        frame = bytes(response[idx : idx + frame_len])
        if command is not None and frame == command:
            continue
        if frame[0] != SERVO_HEADER or frame[1] != SERVO_HEADER:
            continue
        if frame[2] != servo_id or frame[3] != expected_length:
            continue
        if calculate_checksum(frame[2:-1]) != frame[-1]:
            continue
        return frame
    return None


def send_instruction_and_read_status(
    ser: serial.Serial,
    packet: bytes,
    servo_id: int,
    expected_data_len: int,
    read_size: int = 24,
) -> bytes | None:
    expected_frame_len = expected_data_len + 6
    ser.reset_input_buffer()
    ser.write(packet)
    time.sleep(0.005)
    response = ser.read(max(read_size, len(packet) + expected_frame_len))
    return find_status_packet(response, servo_id, expected_data_len, command=bytes(packet))


def ping(ser: serial.Serial, servo_id: int) -> bool:
    packet = build_instruction_packet(servo_id, SERVO_INSTRUCTION_PING)
    status = send_instruction_and_read_status(ser, packet, servo_id, expected_data_len=0)
    return status is not None and status[4] == 0


def read_register_byte(ser: serial.Serial, servo_id: int, register_address: int) -> int | None:
    packet = build_instruction_packet(servo_id, SERVO_INSTRUCTION_READ, bytes([register_address, 1]))
    status = send_instruction_and_read_status(ser, packet, servo_id, expected_data_len=1)
    if status is None or status[4] != 0:
        return None
    return status[5]


def read_register_word(ser: serial.Serial, servo_id: int, register_address: int) -> int | None:
    packet = build_instruction_packet(servo_id, SERVO_INSTRUCTION_READ, bytes([register_address, 2]))
    status = send_instruction_and_read_status(ser, packet, servo_id, expected_data_len=2)
    if status is None or status[4] != 0:
        return None
    return status[5] | (status[6] << 8)


def read_register(ser: serial.Serial, servo_id: int, register: Register) -> int | None:
    if register.size == 1:
        return read_register_byte(ser, servo_id, register.addr)
    if register.size == 2:
        return read_register_word(ser, servo_id, register.addr)
    raise ValueError(f"Unsupported register size {register.size} at 0x{register.addr:02X}")


def format_value(register: Register, value: int | None) -> str:
    if value is None:
        return "READ_FAILED"
    if register.decoder is None:
        return str(value)
    return register.decoder(value)


def print_table(rows: list[tuple[str, str, str, str, str, str]]) -> None:
    widths = [len(header) for header in ("Addr", "Size", "Access", "Name", "What It Means", "value")]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))

    fmt = "  ".join(f"{{:<{width}}}" for width in widths)
    print(fmt.format("Addr", "Size", "Access", "Name", "What It Means", "value"))
    print(fmt.format(*(("-" * width) for width in widths)))
    for row in rows:
        print(fmt.format(*row))


def read_servo(ser: serial.Serial, servo_id: int, delay_s: float) -> list[tuple[str, str, str, str, str, str]]:
    rows: list[tuple[str, str, str, str, str, str]] = []
    for register in REGISTERS:
        value = read_register(ser, servo_id, register)
        rows.append(
            (
                f"0x{register.addr:02X}",
                str(register.size),
                register.access,
                register.name,
                register.meaning,
                format_value(register, value),
            )
        )
        if delay_s > 0:
            time.sleep(delay_s)
    return rows


def selected_servo_ids(args: argparse.Namespace) -> list[int]:
    ids = list(args.ids) if args.ids else list(DEFAULT_SERVO_IDS)
    if args.include_factory:
        ids.extend(sid for sid in FACTORY_DEFAULT_SERVO_IDS if sid not in ids)
    if args.full_sweep:
        ids = list(range(1, 254))
    return ids


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read documented STS3215 control-table registers from every selected servo."
    )
    parser.add_argument("--port", default=None, help="Serial port. Defaults to SERIAL_PORT or auto-discovery.")
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD_RATE, help="Serial baud rate.")
    parser.add_argument(
        "--ids",
        type=parse_ids,
        default=None,
        help="Servo IDs to read, comma or space separated. Default: Gradient0 IDs.",
    )
    parser.add_argument(
        "--include-factory",
        action="store_true",
        help="Also probe factory-default IDs 1, 2, and 3.",
    )
    parser.add_argument(
        "--full-sweep",
        action="store_true",
        help="Probe IDs 1..253 and read registers from every responding servo.",
    )
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_S, help="Serial read timeout in seconds.")
    parser.add_argument("--delay", type=float, default=0.005, help="Delay between register reads in seconds.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        port = resolve_port(args.port)
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    try:
        ser = serial.Serial(port, args.baud, timeout=max(0.0, args.timeout))
    except serial.SerialException as exc:
        print(f"FAIL: could not open {port}: {exc}", file=sys.stderr)
        return 2

    try:
        time.sleep(0.1)
        ser.reset_input_buffer()
        ids = selected_servo_ids(args)
        print(f"Reading registers on {port} @ {args.baud} baud")
        print(f"Selected IDs: {', '.join(str(sid) for sid in ids)}")

        found = 0
        for servo_id in ids:
            label = SERVO_LABELS.get(servo_id)
            title = f"Servo ID {servo_id}" + (f" ({label})" if label else "")
            print(f"\n{title}")
            print("=" * len(title))

            if not ping(ser, servo_id):
                print("ABSENT")
                continue

            found += 1
            rows = read_servo(ser, servo_id, max(0.0, args.delay))
            print_table(rows)

        if found == 0:
            print("\nNo selected servos responded.", file=sys.stderr)
            return 1
        return 0
    finally:
        ser.close()


if __name__ == "__main__":
    raise SystemExit(main())
