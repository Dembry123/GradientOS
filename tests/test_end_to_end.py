import unittest
import sys
import os
import socket
import threading
import errno
import time

from unittest.mock import MagicMock, patch

from gradient_os.run_controller import main as run_controller_main
from gradient_os.arm_controller import utils
from gradient_os.arm_controller.backends.simulation.backend import SimulationBackend

class TestEndToEnd(unittest.TestCase):
    """
    End-to-end tests for the controller, from UDP command to serial output.
    This test mocks the serial port to run without hardware.
    """

    def setUp(self) -> None:
        """Set up for each test."""
        # Reset the trajectory state before each test
        utils.trajectory_state = {
            "is_running": False,
            "should_stop": False,
            "thread": None
        }

    @patch('gradient_os.ik_solver.solve_ik_path_batch')
    def test_move_line_command_to_serial_output(self,
                                                mock_solve_ik: MagicMock) -> None:
        """
        Tests the full pipeline from a MOVE_LINE UDP command to backend motion output.
        """
        # 1. Configure Mocks
        # Mock the IK solver to return a simple, predictable path
        mock_solve_ik.return_value = [
            [0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
            [0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
        ]

        # 2. Start the controller main loop in a background thread
        sync_write_calls = []
        original_sync_write = SimulationBackend.sync_write

        def recording_sync_write(backend_self, commands):
            sync_write_calls.append(commands)
            return original_sync_write(backend_self, commands)

        sync_write_patcher = patch.object(SimulationBackend, "sync_write", recording_sync_write)
        sync_write_patcher.start()
        self.addCleanup(sync_write_patcher.stop)

        with patch.object(sys, "argv", ["gradient-controller", "--sim"]):
            controller_thread = threading.Thread(target=run_controller_main, daemon=True)
            controller_thread.start()
            time.sleep(1.5) # Give the server time to start

        # 3. Send a MOVE_LINE command via UDP
        target_ip = utils.PI_IP
        if target_ip == "0.0.0.0":
            target_ip = "127.0.0.1"
        command = "MOVE_LINE,0.1,0.2,0.3,0.1,0.05"
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(1.0)
            sock.sendto(b"GET_STATUS", (target_ip, utils.UDP_PORT))
            try:
                _resp, _ = sock.recvfrom(1024)
            except socket.timeout:
                self.fail("Controller did not respond to GET_STATUS")
            try:
                sock.sendto(command.encode('utf-8'), (target_ip, utils.UDP_PORT))
            except OSError as exc:
                # Some hosts (e.g., macOS) cannot route to 0.0.0.0; fall back to loopback.
                if getattr(exc, "errno", None) in {errno.EHOSTUNREACH, errno.EADDRNOTAVAIL, errno.ENETUNREACH}:
                    target_ip = "127.0.0.1"
                    sock.sendto(command.encode('utf-8'), (target_ip, utils.UDP_PORT))
                else:
                    raise
            for _ in range(10):
                if sync_write_calls:
                    break
                time.sleep(0.2)

        # 4. Assert that the controller attempted backend sync writes with actuator commands
        self.assertTrue(sync_write_calls, "Controller never issued a backend sync write.")
        sent_commands = sync_write_calls[0]

        commanded_ids = {cmd[0] for cmd in sent_commands}
        expected_ids = set(utils.SERVO_IDS[:-1])  # Gripper may not be commanded in every move
        expected_sim_indices = set(range(utils.NUM_LOGICAL_JOINTS))
        self.assertTrue(
            expected_ids.issubset(commanded_ids) or expected_sim_indices.issubset(commanded_ids),
            "Missing arm actuator commands in backend sync write.",
        )

        # 6. Stop the controller
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto("STOP".encode('utf-8'), (target_ip, utils.UDP_PORT))
        
        # Give the thread time to shut down
        time.sleep(0.2)
        # Explicitly wait for the trajectory thread to finish
        if utils.trajectory_state["thread"] is not None:
             utils.trajectory_state["thread"].join(timeout=1)

        # Since controller_thread is a daemon, it will exit automatically.


if __name__ == '__main__':
    unittest.main() 
