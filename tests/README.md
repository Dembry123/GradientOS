# Robotic Arm Controller Tests

This directory contains the unit, integration, and end-to-end tests for the `mini-arm` controller software.

## Running the Tests

To run the full test suite, you first need to install the required testing framework and mocks.

### 1. Install Dependencies

Navigate to the root directory of the project (`mini-arm`) and run the following command to install `pytest` and `pytest-mock`:

```bash
pip install pytest pytest-mock
```

### 2. Execute the Test Suite

Once the dependencies are installed, you can run all tests by executing the following command from the project's root directory:

```bash
python -m pytest tests/
```

Pytest will automatically discover and run all test files (files named `test_*.py` or `*_test.py`) within the `tests/` directory and its subdirectories.

## Test Descriptions

-   `test_protocol.py`: Contains low-level unit tests for `backends/feetech/protocol.py`. It verifies checksum calculation and Feetech packet structures.

-   `test_driver.py`: Includes unit tests for `FeetechBackend` logical-to-physical command mapping and backend write dispatch.

-   `test_planning.py`: Focuses on unit testing the core algorithms within `trajectory_execution.py`. It specifically tests the path unwrapping and smoothing logic to ensure that generated joint-space trajectories are continuous and do not contain unnecessary "wrap-around" jumps.

-   `test_solver.py`: An integration test for the IKFast backend. It performs sanity checks to ensure that Forward Kinematics (FK) and Inverse Kinematics (IK) are consistent and that the batch IK solver can process a sequence of poses correctly.

-   `test_end_to_end.py`: Provides high-level integration tests that simulate the full control loop, from receiving a UDP command to issuing backend actuator commands.
