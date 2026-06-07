# Arm Controller Architecture

This document describes the abstraction architecture for multi-robot and multi-servo compatibility in GradientOS.

## Overview

The arm controller is designed to support:
- **Multiple robots** (e.g., `gradient0`, `gradient0_5`, future designs)
- **Multiple servo backends** (e.g., Feetech STS3215, Dynamixel, simulation)

This is achieved through two parallel abstraction layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           run_controller.py                                 │
│                                                                             │
│   1. Selects ROBOT config    (--robot gradient0)                            │
│   2. Selects SERVO backend   (--servo-backend feetech)                      │
│   3. Initializes both before any servo operations                           │
└─────────────────────────────────────────────────────────────────────────────┘
                    │                              │
                    ▼                              ▼
┌───────────────────────────────────┐  ┌───────────────────────────────────┐
│         ROBOT CONFIGURATION       │  │         SERVO BACKEND             │
│                                   │  │                                   │
│  "What robot am I controlling?"   │  │  "How do I talk to the servos?"   │
│                                   │  │                                   │
│  • Number of joints (6 DOF)       │  │  • Protocol (packet structure)    │
│  • Servo IDs (10,20,21,30,...)    │  │  • Checksum algorithm             │
│  • Joint limits (radians)         │  │  • Register addresses             │
│  • Twin motor mappings            │  │  • Encoder resolution (4095)      │
│  • Inverted servos                │  │  • Baud rate (1000000)            │
│  • Master calibration offsets     │  │  • PID defaults                   │
│  • Default servo backend          │  │  • Telemetry parsing              │
└───────────────────────────────────┘  └───────────────────────────────────┘
         │                                        │
         ▼                                        ▼
┌───────────────────────────────────┐  ┌───────────────────────────────────┐
│        robots/base.py             │  │     backends/base.py              │
│        RobotConfig (ABC)          │  │     ActuatorBackend (ABC)         │
└───────────────────────────────────┘  └───────────────────────────────────┘
         │                                        │
         ▼                                        ▼
┌───────────────────────────────────┐  ┌───────────────────────────────────┐
│  robots/gradient0/config.py       │  │  backends/feetech/backend.py      │
│  Gradient0Config(RobotConfig)     │  │  FeetechBackend(ActuatorBackend)  │
│                                   │  │                                   │
│  • 6 DOF + gripper                │  │  • Feetech STS protocol           │
│  • Servo IDs: 10,20,21,30,31...   │  │  • 0xFF 0xFF header               │
│  • Uses Feetech servos (default)  │  │  • Registers: 0x2A, 0x38, etc.    │
└───────────────────────────────────┘  └───────────────────────────────────┘
         │                                        │
         ▼                                        ▼
┌───────────────────────────────────┐  ┌───────────────────────────────────┐
│  robots/gradient0_5/config.py     │  │  backends/dynamixel/backend.py    │
│  Gradient05Config(RobotConfig)    │  │  DynamixelBackend(ActuatorBackend)│
│                                   │  │                                   │
│  • Different joint config         │  │  • Dynamixel Protocol 2.0         │
│  • Different servo IDs            │  │  • Different registers            │
│  • May use Dynamixel servos       │  │  • Different packet structure     │
└───────────────────────────────────┘  └───────────────────────────────────┘
```

## Initialization Flow

```python
# In run_controller.py main():

# 1. Parse command-line arguments
#    --robot gradient0
#    --servo-backend feetech (or uses robot's default)

# 2. Load robot configuration
selected_robot = get_robot_config("gradient0")
robot_config.set_active_robot(selected_robot)

# 3. Determine servo backend (CLI override or robot's default)
servo_backend = args.servo_backend or selected_robot.default_servo_backend

# 4. Configure servo backend (MUST happen before any servo operations)
backend_registry.set_active_backend(servo_backend)

# 5. Populate module-level constants from the active configuration
utils._populate_servo_constants()

# 6. Create, initialize, and register the backend instance
backend = backend_registry.create_backend(servo_backend, selected_robot.get_config_dict())
backend_registry.set_active_backend_instance(backend)
backend.initialize()

# 7. Runtime code uses actuator_runtime or the active backend directly
```

## File Structure

```
arm_controller/
├── ARCHITECTURE.md              # This file
│
├── robots/                      # ROBOT CONFIGURATIONS
│   ├── __init__.py              # Registry: get_robot_config(), list_available_robots()
│   ├── base.py                  # RobotConfig ABC
│   └── gradient0/
│       ├── __init__.py
│       └── config.py            # Gradient0Config implementation
│
├── backends/                    # SERVO BACKENDS
│   ├── __init__.py              # Registers available backends
│   ├── registry.py              # Active backend management
│   ├── feetech/
│   │   ├── __init__.py
│   │   ├── config.py            # Constants (registers, defaults, telemetry parsing)
│   │   ├── protocol.py          # Low-level packet functions (INTERNAL)
│   │   └── driver.py            # FeetechBackend(ActuatorBackend)
│   └── simulation/
│       └── backend.py           # SimulationBackend (in-memory, no hardware)
│
├── actuator_interface.py        # ActuatorBackend ABC + SimulationBackend
│
├── actuator_runtime.py          # App-facing active-backend helpers + state sync
│
├── robot_config.py              # LEGACY: Module-level constants
│                                # Now populated dynamically by set_active_robot()
│
├── utils.py                     # Shared utilities and runtime state
│                                # Constants populated by _populate_servo_constants()
│
├── trajectory_execution.py      # Trajectory planning and execution
├── command_handlers.py               # UDP command handlers
└── pid_tuner.py                 # PID tuning utilities
```

## ActuatorBackend Interface

The complete interface that all servo backends must implement:

```python
class ActuatorBackend(ABC):
    """Abstract interface for servo/actuator communication."""
    
    # --- Properties ---
    @property
    @abstractmethod
    def encoder_resolution(self) -> int:
        """Max encoder value (e.g., 4095 for 12-bit)."""
        pass
    
    @property
    @abstractmethod
    def encoder_center(self) -> int:
        """Center encoder value (e.g., 2048)."""
        pass
    
    # --- Connection ---
    @abstractmethod
    def connect(self, port: str, baud_rate: int) -> bool:
        """Open serial connection."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close serial connection."""
        pass
    
    # --- Discovery ---
    @abstractmethod
    def ping(self, actuator_id: int) -> bool:
        """Check if actuator is present."""
        pass
    
    @abstractmethod
    def scan(self, id_range: range) -> list[int]:
        """Scan for present actuators."""
        pass
    
    # --- Position Control ---
    @abstractmethod
    def sync_write_positions(self, commands: list[tuple[int, int, int, int]]) -> None:
        """Write positions to multiple actuators.
        Each tuple: (actuator_id, position, speed, acceleration)
        """
        pass
    
    @abstractmethod
    def sync_read_positions(self, actuator_ids: list[int]) -> dict[int, int]:
        """Read positions from multiple actuators."""
        pass
    
    # --- Configuration ---
    @abstractmethod
    def set_pid_gains(self, actuator_id: int, kp: int, ki: int, kd: int) -> bool:
        """Set PID gains for an actuator."""
        pass
    
    @abstractmethod
    def set_angle_limits(self, actuator_id: int, min_raw: int, max_raw: int) -> bool:
        """Set angle limits for an actuator."""
        pass
    
    # --- Calibration ---
    @abstractmethod
    def calibrate_middle_position(self, actuator_id: int) -> bool:
        """Set current position as center (zero)."""
        pass
    
    @abstractmethod
    def factory_reset(self, actuator_id: int) -> bool:
        """Reset actuator to factory defaults."""
        pass
    
    # --- Telemetry ---
    @abstractmethod
    def read_telemetry(self, actuator_ids: list[int]) -> dict[int, dict]:
        """Read telemetry (voltage, temp, current, status) from actuators."""
        pass
```

## RobotConfig Interface

The complete interface that all robot configurations must implement:

```python
class RobotConfig(ABC):
    """Abstract interface for robot-specific configuration."""
    
    # --- Identity ---
    @property
    @abstractmethod
    def name(self) -> str: ...
    
    @property
    @abstractmethod
    def version(self) -> str: ...
    
    # --- Kinematics ---
    @property
    @abstractmethod
    def num_logical_joints(self) -> int:
        """Number of logical joints (e.g., 6 for 6-DOF arm)."""
        pass
    
    @property
    @abstractmethod
    def num_physical_actuators(self) -> int:
        """Number of physical actuators (may differ due to twin motors)."""
        pass
    
    # --- Actuator Mapping ---
    @property
    @abstractmethod
    def actuator_ids(self) -> list[int]:
        """List of physical actuator IDs."""
        pass
    
    @property
    @abstractmethod
    def logical_to_physical_map(self) -> list[list[int]]:
        """Maps logical joint index to list of physical actuator indices."""
        pass
    
    @property
    @abstractmethod
    def twin_motor_actuator_ids(self) -> dict[int, int]:
        """Maps logical joint index to secondary motor ID (for twin-motor joints)."""
        pass
    
    @property
    @abstractmethod
    def logical_joint_to_actuator_ids(self) -> dict[int, list[int]]:
        """Maps 1-based logical joint number to physical actuator IDs."""
        pass
    
    # --- Limits ---
    @property
    @abstractmethod
    def logical_joint_limits_rad(self) -> list[tuple[float, float]]:
        """Min/max angles for each logical joint in radians."""
        pass
    
    @property
    @abstractmethod
    def actuator_limits_rad(self) -> list[tuple[float, float]]:
        """Min/max angles for each physical actuator in radians."""
        pass
    
    # --- Servo Backend ---
    @property
    @abstractmethod
    def default_servo_backend(self) -> str:
        """Default servo backend for this robot (e.g., "feetech")."""
        pass
    
    @property
    @abstractmethod
    def actuator_pid_gains(self) -> dict[int, tuple[int, int, int]]:
        """Per-actuator PID gains {actuator_id: (kp, ki, kd)}."""
        pass
```

## Migration Path

### Current State
- Feetech packet code lives in `backends/feetech/protocol.py`.
- Feetech serial runtime behavior lives in `backends/feetech/driver.py`.
- Higher-level production modules use `actuator_runtime` / the active backend.
- The package-level servo runtime shims have been removed. Scripts that need packet-level Feetech operations should import `backends/feetech/protocol.py`; application code should use `actuator_runtime` or the active backend.

### Target State
1. Move `servo_protocol.py` content to `backends/feetech/protocol.py` ✅
2. Implement `FeetechBackend(ActuatorBackend)` in `backends/feetech/driver.py` ✅
3. Remove the package-level servo compatibility shims after production and scripts migrate ✅
4. Update higher-level modules to use backend directly ✅

### Backward Compatibility
- Existing imports from `robot_config` continue to work
- No breaking changes to external interfaces (UDP commands, etc.)

## Adding a New Robot

1. Create `robots/my_robot/config.py`:
   ```python
   from ..base import RobotConfig
   
   class MyRobotConfig(RobotConfig):
       @property
       def name(self) -> str:
           return "My Robot"
       
       @property
       def default_servo_backend(self) -> str:
           return "dynamixel"  # This robot uses Dynamixel servos
       
       # ... implement all abstract properties
   ```

2. Register in `robots/__init__.py`:
   ```python
   from .my_robot.config import MyRobotConfig
   register_robot("my_robot", MyRobotConfig)
   ```

3. Use: `python -m gradient_os.run_controller --robot my_robot`

## Adding a New Servo Backend

1. Create `backends/dynamixel/`:
   ```
   backends/dynamixel/
   ├── __init__.py
   ├── config.py      # Protocol constants, register addresses
   ├── protocol.py    # Low-level packet functions
   └── backend.py     # DynamixelBackend(ActuatorBackend)
   ```

2. Implement `DynamixelBackend(ActuatorBackend)` with all required methods

3. Register in `backends/__init__.py`:
   ```python
   from .dynamixel import DynamixelBackend
   registry.register_backend("dynamixel", "...dynamixel.config")
   ```

4. Use: `python -m gradient_os.run_controller --robot gradient0 --servo-backend dynamixel`

## Design Principles

1. **No hardcoded values in high-level code**: All robot/servo-specific values come from configs
2. **Fail loudly**: If config is not set, raise clear errors (no silent fallbacks)
3. **Configuration at startup**: Robot and backend are set once in `run_controller.py`
4. **Single source of truth**: Each value defined in exactly one place
5. **Backward compatibility**: Existing imports continue to work during migration

---

## Detailed Migration TODO

### Current State Assessment

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `actuator_runtime.py` | small | ✅ ACTIVE | App-facing helper layer over active `ActuatorBackend`; synchronizes `utils` state |
| `trajectory_execution.py` | 1092 | ✅ MIGRATED | Uses `actuator_runtime` / active backend for sync read/write paths |
| `command_handlers.py` | 1579 | ✅ MIGRATED | Uses `actuator_runtime` for motion, gripper, jog, and readback paths |
| `run_controller.py` | 929 | ✅ MIGRATED | Creates/initializes backend and uses it directly; no serial fallback through old modules |
| `backends/feetech/protocol.py` | 727 | ✅ NEW | Clean Feetech protocol implementation |
| `backends/feetech/driver.py` | 835 | ✅ ACTIVE | FeetechBackend class used by runtime Feetech path |
| `backends/registry.py` | 183 | ✅ ACTIVE | Config and backend instance registry |
| `actuator_interface.py` | 617 | ✅ ACTIVE | Backend interface used by Feetech, simulation, and EtherCAT RTCore |
| `robot_config.py` | 251 | ✅ DONE | Dynamic loading via set_active_robot() |
| `utils.py` | 305 | ✅ DONE | Constants from registry via `_populate_servo_constants()` and `_populate_robot_constants()` |
| `robots/base.py` | 589 | ✅ DONE | RobotConfig ABC complete |
| `robots/gradient0/config.py` | 403 | ✅ DONE | Gradient0Config complete |

### Phase 1: Backend Instance Management ✅ COMPLETE

**Goal**: Registry manages backend INSTANCES (not just configs)

- [x] **1.1** Update `backends/registry.py`:
  - Add `_active_backend_instance: Optional[ActuatorBackend] = None`
  - Add `create_backend(name, robot_config) -> ActuatorBackend`
  - Add `get_active_backend() -> ActuatorBackend`
  - Add `set_active_backend_instance(backend: ActuatorBackend)`

- [x] **1.2** Update `backends/__init__.py`:
  - Register backend CLASSES (not just config paths)
  - `BACKEND_CLASSES = {"feetech": FeetechBackend, "simulation": SimulationBackend}`

- [x] **1.3** Update `run_controller.py` initialization:
  ```python
  # After robot config is set:
  backend = backend_registry.create_backend(
      servo_backend, 
      selected_robot.get_config_dict()
  )
  backend.initialize()
  backend_registry.set_active_backend_instance(backend)
  ```

### Phase 2: High-Level Module Migration

**Goal**: Modules use backend instance instead of `servo_protocol` directly

#### 2.1 servo_driver.py (Priority: HIGH) ✅ COMPLETE

- [x] **2.1.1** Add backend accessor at top:
  ```python
  def _get_backend():
      from .backends import registry
      return registry.get_active_backend()
  ```

- [x] **2.1.2** Migrate `initialize_servos()`:
  - Compatibility wrapper delegates to the active backend.

- [x] **2.1.3** Migrate `set_servo_positions()`:
  - Compatibility wrapper delegates to `actuator_runtime.set_joint_positions()`.

- [x] **2.1.4** Migrate `get_current_arm_state_rad()`:
  - Compatibility wrapper delegates to `actuator_runtime.get_joint_positions()`.

- [x] **2.1.5** Migrate calibration functions:
  - `set_current_position_as_hardware_zero()` → `backend.set_current_position_as_zero()`
  - `set_servo_pid_gains()` → `backend.set_pid_gains()`
  - `set_servo_angle_limits_from_urdf()` → `backend.apply_joint_limits()`

- [x] **2.1.6** Keep angle conversion helpers (robot-config dependent):
  - `angle_to_raw()`, `raw_to_angle_rad()` - these use robot config mapping
  - Also added `_build_logical_to_servo_id_map()` helper

#### 2.2 trajectory_execution.py (Priority: HIGH) ✅ COMPLETE

- [x] **2.2.1** Add backend accessor functions:
  - `_get_backend()`, `_use_backend()`
  - `_build_primary_feedback_ids()` - dynamically builds primary IDs from robot config
  - `_build_logical_to_physical_index_map()` - replaces hardcoded joint-to-servo mapping
  - `_get_twin_motor_pairs()` - gets twin motor pairs from robot config

- [x] **2.2.2** Migrate open-loop executor:
  - `sync_write_goal_pos_speed_accel()` now uses backend if available

- [x] **2.2.3** Migrate closed-loop execution:
  - `sync_read_positions()` now uses backend if available
  - `sync_write_goal_pos_speed_accel()` now uses backend if available

- [x] **2.2.4** Remove hardcoded twin motor logic:
  - Replaced hardcoded `20, 21, 30, 31` with dynamic `_get_twin_motor_pairs()`

- [x] **2.2.5** Remove hardcoded primary ID mapping:
  - Replaced `{0: 10, 1: 20, 2: 30, ...}` with `_build_primary_feedback_ids()`

- [x] **2.2.6** Update sync_profiles for diagnostics:
  - Uses `backend.get_sync_profiles()` if available

#### 2.3 command_handlers.py (Priority: MEDIUM) ✅ COMPLETE

- [x] **2.3.1** Audit all `servo_protocol` and `servo_driver` calls
- [x] **2.3.2** Remove production direct `servo_protocol` and `servo_driver` usage; runtime calls go through `actuator_runtime` / active backend
- [x] **2.3.3** Remove deprecated package-level servo shims after call sites migrated
- [x] **2.3.4** Gripper writes use backend single-actuator APIs via `actuator_runtime`
- [x] **2.3.5** Fixed `SimulationBackend` to properly handle servo ID to joint index mapping
- [x] **2.3.6** Renamed utils functions for clarity:
  - `_populate_backend_constants()` → `_populate_servo_constants()`
  - `_reinitialize_state()` → `_populate_robot_constants()`

#### 2.4 run_controller.py (Priority: MEDIUM) ✅ COMPLETE

- [x] **2.4.1** Gripper initialization now uses backend gripper APIs through `actuator_runtime`
- [x] **2.4.2** Telemetry loop updated to use backend if available:
  - Uses `backend.present_servo_ids` for servo list
  - Uses `backend.sync_read_block()` for telemetry data
  - Skips backend-specific block telemetry when the active backend does not support it
- [x] **2.4.3** Calibration mode now uses backend single-actuator reads
- [x] **2.4.4** FACTORY_RESET uses `backend.factory_reset_actuator()` and `backend.restart_actuator()`
- [x] **2.4.5** GET_ALL_POSITIONS uses `backend.sync_read_positions()`
- [x] **2.4.6** Removed production fallback through `servo_protocol`

### Phase 3: Remove Old Modules ✅ COMPLETE

- [x] **3.1** Moved packet construction/parsing to `backends/feetech/protocol.py`
- [x] **3.2** Migrated production runtime calls to `actuator_runtime` / active backend APIs
- [x] **3.3** Removed package-level servo driver/protocol shims
- [x] **3.4** Removed the old monkey-patch simulator entrypoint; use `backends/simulation/backend.py`

### Phase 4: Clean Up ✅ COMPLETE

- [x] **4.1** Created `backends/simulation/` with proper structure:
  - `backends/simulation/__init__.py` - exports SimulationBackend
  - `backends/simulation/backend.py` - full SimulationBackend implementation

- [x] **4.2** Cleaned up `actuator_interface.py`:
  - Moved `SimulationBackend` to `backends/simulation/backend.py`
  - `actuator_interface.py` now only contains `ActuatorBackend` ABC
  - Re-exports `SimulationBackend` for backward compatibility

- [x] **4.3** Updated `backends/__init__.py`:
  - Imports `SimulationBackend` from new location
  - All backends now follow consistent structure

**Backward compatibility maintained:**
- `from actuator_interface import SimulationBackend` still works
- `from backends import SimulationBackend` still works
- New preferred: `from backends.simulation import SimulationBackend`

### Phase 5: Testing & Validation

- [ ] **5.1** Test with real hardware:
  - Verify `gradient0` robot works with new backend system
  - Verify all motion commands work
  - Verify calibration works

- [ ] **5.2** Test simulation mode:
  - Verify `--sim` flag works
  - Verify telemetry in simulation

- [ ] **5.3** Test error cases:
  - Missing servos
  - Communication errors
  - Invalid robot/backend combinations

---

## Function Migration Reference

### servo_protocol.py → FeetechBackend

| Old Function | New Method | Notes |
|--------------|------------|-------|
| `ping(servo_id)` | `backend.ping_actuator(servo_id)` | |
| `send_servo_command()` | `backend.set_single_actuator_position()` | |
| `sync_write_goal_pos_speed_accel()` | `backend.sync_write()` | Pre-compute with `prepare_sync_write_commands()` |
| `sync_read_positions()` | `backend.sync_read_positions()` | |
| `read_servo_position()` | `backend.read_single_actuator_position()` | |
| `read_servo_register_word()` | (internal to backend) | Not exposed in interface |
| `write_servo_register_word()` | (internal to backend) | Not exposed in interface |
| `calibrate_servo_middle_position()` | `backend.set_current_position_as_zero()` | |
| `factory_reset_servo()` | `backend.factory_reset_actuator()` | |
| `restart_servo()` | `backend.restart_actuator()` | |
| `write_servo_angle_limits()` | `backend.apply_joint_limits()` | Works on all servos |
| `set_servo_acceleration()` | (included in position commands) | |
| `get_present_servo_ids()` | `backend.get_present_actuator_ids()` | |

### servo_driver.py → FeetechBackend

| Old Function | New Method | Notes |
|--------------|------------|-------|
| `initialize_servos()` | `backend.initialize()` | |
| `set_servo_positions()` | `backend.set_joint_positions()` | |
| `get_current_arm_state_rad()` | `backend.get_joint_positions()` | |
| `set_single_servo_position_rads()` | `backend.set_single_actuator_position()` | |
| `set_servo_pid_gains()` | `backend.set_pid_gains()` | |
| `set_servo_angle_limits_from_urdf()` | `backend.apply_joint_limits()` | |
| `set_current_position_as_hardware_zero()` | `backend.set_current_position_as_zero()` | |
| `reinitialize_servo()` | (custom sequence) | Factory reset + init |
| `logical_q_to_syncwrite_tuple()` | `backend.prepare_sync_write_commands()` | |
| `angle_to_raw()` | (internal to backend) | |
| `raw_to_angle_rad()` | (used by `raw_to_joint_positions()`) | |

---

## Cleanup Status

The package-level servo runtime shims and the archived monolithic controller have been removed. Backend-native maintenance scripts should live under `scripts/`; the old bulk zero-offset reset helper is now represented by `scripts/reset_servo_zero_offsets.py`.
