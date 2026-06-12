# Diagnostics Guide

The controller includes a powerful set of diagnostic tools designed to help analyze and debug the performance of the IK solver and the trajectory executors. This is particularly useful for identifying and understanding behavior near joint singularities.

## 1. Live Diagnostic Logging

The primary way to capture performance data is through live logging. When enabled, every motion command that involves path planning (like `MOVE_LINE`, `MOVE_LINE_RELATIVE`, or `SET_ORIENTATION`) will automatically generate a detailed report.

### How to Enable

When using the full stack launcher, enable diagnostic logging with:

```bash
./start --diagnostic-logging
```

`./start --diagnostic`, `./start --diagnostics`, and `./start --diagnostic-log` are equivalent shortcuts.

That sets `MINI_ARM_IK_LOG=1` for the controller, enables realtime jog JSONL logging, passes `--diagnostic-log` to the HEBI Mobile I/O bridge when the bridge is started by `./start`, and creates per-stack-session telemetry diagnostics under `logs/stack/<session>/diagnostics/`.

The stack-session diagnostics include:

- `controller-telemetry.jsonl`: one record when the controller telemetry thread starts/stops and one `telemetry_tick` record per telemetry sample, including measured joints from the measured-state cache, measured snapshot age/source, `jog_ik`, payload byte size, and UDP send timing.
- `monitor-api.jsonl`: `/monitor` lifecycle and fanout records, including subscriptions, inbound controller UDP datagrams, queue drops, and SSE yield records with the joint payload summary sent toward the browser visualizer.

Realtime jog diagnostic files under `diagnostics/jog_motion/` include one row per jog loop while jog debug logging is enabled. Each row includes `dt_s`, `loop_body_ms`, `planned_sleep_ms`, position-read/write timing fields, IK `solve_time_ms` when an IK solve ran, and `serial_io_events` with per-operation Feetech lock-wait/write/read/parse timing for SyncRead, SyncWrite, and telemetry block reads that occurred during that loop.

If you are running the controller by itself, set the `MINI_ARM_IK_LOG` environment variable to `1` before starting the controller.

```bash
# From your shell in the project root
export MINI_ARM_IK_LOG=1
python -m gradient_os.run_controller
```

Now, any relevant move command you send to the running controller will create a new diagnostic session.

**Note:** When live diagnostics are active, the open-loop executor remains at the default **100 Hz**. Historical mentions of higher open-loop frequencies are deprecated.

### Output Folder Structure

Each diagnostic session creates a unique, timestamped folder to keep all related files together. The structure is:

```
diagnostics/
├── closed_loop/
│   └── 20231027_143000/  <-- Session ID
│       ├── ik_plan.csv
│       ├── timing.png
│       ├── error.png
│       └── sync.png
└── open_loop/
    └── 20231027_143115/  <-- Session ID
        ├── ik_plan.csv
        ├── timing.png
        └── error.png
```

### Generated Files

-   **`ik_plan.csv` (Most Important)**  
    This file contains the raw, unfiltered output from the batch IK solver. Each row contains the target Cartesian coordinate and the exact joint angles (in radians) the solver chose for that point. This is the key file for analyzing solver behavior, as you can plot the joint columns to visually identify large, sudden "flips" that indicate a singularity.

-   **`timing.png`**  
    This chart shows the performance of the executor thread, breaking down how long each part of the control loop took in milliseconds (e.g., reading feedback, writing commands). It's useful for spotting performance bottlenecks.

-   **`error.png`**  
    This chart displays the physical tracking error for each joint over the course of the move (commanded position vs. actual measured position). A spike in this chart almost always corresponds to a joint flip seen in the `ik_plan.csv`.

-   **`sync.png`** (Closed-loop only)  
    A more detailed breakdown of the timing for the `SyncRead` operation, which is often the main bottleneck in the closed-loop controller.

## 2. Standalone Path Analysis

For offline analysis or to test specific paths without running the full controller, you can use the `ik_path_diagnostics.py` script.

### How to Use

The script can generate its own straight-line path or load one from a JSON file.

**A. Generate a straight-line path:**

This command generates a 200-point path starting from the robot's current "home" position and moving 10cm straight down (`-0.1` in Z).

```bash
python3 diagnostics/ik_path_diagnostics.py --line 0 0 -0.1 200
```

**B. Load a path from a JSON file:**

The JSON file should contain a simple list of `[x, y, z]` coordinates.

```json
// my_test_path.json
[
  [0.4, 0.0, 0.3],
  [0.4, 0.05, 0.28],
  [0.4, 0.1, 0.26]
]
```

```bash
python3 diagnostics/ik_path_diagnostics.py --json my_test_path.json
```

### Output

The standalone script generates its output in the `diagnostics/ik_path/` directory. It produces a similar set of files (`ik_log_<timestamp>.csv`, `ik_angles_<timestamp>.png`, `ik_error_<timestamp>.png`) that allow you to analyze a specific path in isolation.
