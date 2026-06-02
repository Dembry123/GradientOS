import unittest
import sys
import os

from gradient_os.arm_controller import servo_protocol
from gradient_os.arm_controller import utils
from gradient_os.arm_controller.backends.feetech import config as feetech_config
from gradient_os.arm_controller.backends.feetech import protocol as feetech_protocol


class FakeSerial:
    def __init__(self, response: bytes):
        self.response = response
        self.timeout = 0.1
        self.is_open = True
        self.writes: list[bytes] = []

    def reset_input_buffer(self) -> None:
        pass

    def write(self, packet: bytes) -> None:
        self.writes.append(bytes(packet))

    def read(self, size: int) -> bytes:
        return self.response[:size]


def _status_packet(servo_id: int, status: int, data: bytes) -> bytes:
    body = bytes([servo_id, len(data) + 2, status]) + data
    return b"\xff\xff" + body + bytes([feetech_protocol.calculate_checksum(body)])

class TestServoProtocol(unittest.TestCase):
    """
    Unit tests for the low-level servo protocol functions.
    These tests do not require a hardware connection.
    """

    def test_calculate_checksum(self) -> None:
        """
        Tests the checksum calculation against a known correct value.
        The example is taken from the Feetech servo documentation for writing
        the value 0x1A to register 0x04 on servo 0x01.
        """
        packet_data = bytearray([0x01, 0x04, 0x03, 0x04, 0x1A])
        # Expected checksum from documentation is 0xD9
        expected_checksum = 0xD9
        calculated_checksum = servo_protocol.calculate_checksum(packet_data)
        self.assertEqual(calculated_checksum, expected_checksum)

    def test_sync_write_packet_structure(self) -> None:
        """
        Tests that the sync_write_goal_pos_speed_accel function generates a
        packet with the correct structure and checksum for a two-servo command.
        """
        # Command servo 10 to pos 1000 and servo 20 to pos 2000
        servo_data = [
            (10, 1000, 100, 1), # (id, pos, speed, accel)
            (20, 2000, 200, 2),
        ]
        if utils.SERVO_INSTRUCTION_SYNC_WRITE is None:
            utils.SERVO_HEADER = feetech_config.SERVO_HEADER
            utils.SERVO_BROADCAST_ID = feetech_config.SERVO_BROADCAST_ID
            utils.SERVO_INSTRUCTION_SYNC_WRITE = feetech_config.SERVO_INSTRUCTION_SYNC_WRITE
            utils.SYNC_WRITE_START_ADDRESS = feetech_config.SYNC_WRITE_START_ADDRESS
            utils.SYNC_WRITE_DATA_LEN_PER_SERVO = feetech_config.SYNC_WRITE_DATA_LEN_PER_SERVO
        
        # Manually construct the expected packet
        # pos 1000 = 0x03E8 -> [0xE8, 0x03]
        # pos 2000 = 0x07D0 -> [0xD0, 0x07]
        # speed 100 = 0x0064 -> [0x64, 0x00]
        # speed 200 = 0x00C8 -> [0xC8, 0x00]
        
        # Expected data block for servo 10:
        # ID(1) + Accel(1) + Pos(2) + Time(2) + Speed(2) = 8 bytes
        # 10, 1, 0xE8, 0x03, 0x00, 0x00, 0x64, 0x00
        
        # Expected data block for servo 20:
        # 20, 2, 0xD0, 0x07, 0x00, 0x00, 0xC8, 0x00

        # L = (Num Servos * (Len Per Servo + 1)) + 4 = (2 * (7+1)) + 4 = 20 = 0x14
        
        # Construct the part of the packet that gets checksummed
        checksum_data = bytearray([
            0xFE, # Broadcast ID
            20,   # Packet Length (L)
            utils.SERVO_INSTRUCTION_SYNC_WRITE, # Instruction
            utils.SYNC_WRITE_START_ADDRESS,     # Start Address
            utils.SYNC_WRITE_DATA_LEN_PER_SERVO, # Len per servo
            10, 1, 0xE8, 0x03, 0x00, 0x00, 0x64, 0x00, # Servo 10 data
            20, 2, 0xD0, 0x07, 0x00, 0x00, 0xC8, 0x00, # Servo 20 data
        ])
        
        expected_checksum = servo_protocol.calculate_checksum(checksum_data)
        
        expected_packet = bytearray([0xFF, 0xFF]) + checksum_data + bytearray([expected_checksum])

        # To test, we need to mock the ser.write call
        with unittest.mock.patch('gradient_os.arm_controller.utils.ser') as mock_serial:
            servo_protocol.sync_write_goal_pos_speed_accel(servo_data)
            # Check that write was called
            mock_serial.write.assert_called_once()
            # Get the actual packet that was written
            actual_packet = mock_serial.write.call_args[0][0]
            self.assertEqual(actual_packet, expected_packet)

    def test_feetech_sync_read_keeps_position_with_status_error(self) -> None:
        """
        Servo status bits such as overload should raise an alert but should not
        cause valid position bytes to be discarded.
        """
        packet = _status_packet(20, 0x20, bytes([0x5C, 0x06]))
        alerts_seen: list[tuple[int, int, list[str]]] = []

        positions = feetech_protocol.sync_read_positions(
            FakeSerial(packet),
            [20],
            alert_callback=lambda sid, code, names: alerts_seen.append((sid, code, names)),
        )

        self.assertEqual(positions, {20: 1628})
        self.assertEqual(alerts_seen, [(20, 0x20, ["Overload"])])

    def test_feetech_sync_read_block_keeps_data_with_status_error(self) -> None:
        packet = _status_packet(20, 0x20, bytes([0x5C, 0x06]))

        block = feetech_protocol.sync_read_block(
            FakeSerial(packet),
            [20],
            start_address=0x38,
            data_len=2,
        )

        self.assertEqual(block, {20: bytes([0x5C, 0x06])})

    def test_feetech_status_telemetry_uses_status_bit_names(self) -> None:
        data = bytes([0x20, 0x00, 0x00, 0x00, 0x00])

        parsed = feetech_config.parse_telemetry_block2(data)

        self.assertEqual(parsed["status_names"], ["Overload"])


if __name__ == '__main__':
    unittest.main()
