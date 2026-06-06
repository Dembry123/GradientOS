## IK Solver And Teleop Modes

`src/gradient_os/ik_solver.py` is now a thin facade used by the controller. Existing callers still use `solve_ik(...)`, `get_fk_matrix(...)`, and `solve_ik_path_batch(...)`, but concrete solver code lives under `src/gradient_os/ik_backends/`. The backend is selected with `MINI_ARM_SOLVER` or the `./start --solver=...` flag.

The backend package is organized as:

```text
gradient_os.ik_solver
  -> gradient_os.ik_backends.base.IKBackend
  -> gradient_os.ik_backends.ikfast_backend.IKFastBackend
  -> gradient_os.ik_backends.quik_backend.QuikBackend
  -> gradient_os.ik_backends.trac_backend.TracBackend
  -> gradient_os.ik_backends.dls_backend.DlsBackend
  -> gradient_os.ik_backends.qp_backend.QpBackend
```

All public solver calls use the same public tool frame: the pose is the robot `tool_link`, not an internal wrist center. IKFast still subtracts `END_EFFECTOR_OFFSET` internally because its generated solver targets the wrist. QuIK has its own raw end-effector convention, so the wrapper establishes a fixed transform between raw QuIK zero FK and the URDF/public zero tool pose. DLS and QP use the URDF tool frame directly. TRAC-IK targets `base` to `tool_link` from `mini-6dof-arm/mini-6dof-arm.urdf`.

### Solver Backends

`ikfast` is the existing generated analytic solver. It is very fast and remains the default. It can return multiple branches; the wrapper chooses the solution nearest the seed/current joint vector. In the current local benchmark it still shows branch/target acceptance limits, so failed targets are reported rather than hidden.

`quik` uses the repo’s PyQuIK C++ binding under `src/numeric_solver/pyquik`. It requires the `src/numeric_solver/quik` submodule, Eigen, pybind11, and a built `pyquik` extension. On macOS, build it with:

```bash
scripts/build_pyquik.sh
```

`trac` uses the optional `trac_ik_python` package through `src/numeric_solver/trac_ik_interface.py`. This backend is wired in, but it intentionally fails at startup if `trac_ik_python` is not installed. It does not fall back to IKFast.

`dls` is a Python damped-least-squares differential IK backend. It uses finite-difference FK/Jacobian, joint limits, bounded per-iteration joint steps, and iterative convergence on full pose error.

`qp` is a Python bounded least-squares/QP differential IK backend using SciPy `lsq_linear`. It includes joint step bounds and joint position bounds in each differential solve.

For DLS and QP, `solve_pose(...)` iterates internal differential steps until it can return a full `q_target` to legacy callers. The explicit one-step API is `solve_differential_result(...)`, which returns `q_next`, `dq`, and `qdot`. The older `solve_differential(...)` compatibility wrapper returns only `q_next`.

### Teleop Modes

`velocity_jog` is the original mode. The phone bridge computes Cartesian pose error, multiplies by gains to produce Cartesian velocity, and the controller integrates that velocity every jog tick before solving IK. This preserves the existing rate-limited feel and works with the existing web jog controls.

`absolute_pose` is the new direct target mode. The phone bridge still does B1/deadman latching, phone-frame calibration, target pose generation, stale feedback release, and gripper velocity. Instead of sending Cartesian velocity, it sends the calibrated robot-space target pose to `/control/jog/target-pose`. The controller solves IK directly for that target every tick, seeds from measured joint feedback when available, commands the resulting joint target with the configured raw servo speed register, and does not assume `q_current == q_goal` after sending.

Use the stack launcher:

```bash
./start --sim=true --solver=ikfast --teleop-mode=velocity_jog --joint-speed-limit=800 --jog-frequency=25
./start --sim=true --solver=quik --teleop-mode=absolute_pose --joint-speed-limit=300 --jog-frequency=30
./start --real --solver=dls --teleop-mode=absolute_pose --joint-speed-limit=200 --jog-frequency=25
```

The launcher starts controller, API, and web UI without vision. It exports `MINI_ARM_SOLVER`, `GRADIENT_TELEOP_MODE`, `GRADIENT_JOG_FREQUENCY_HZ`, and `GRADIENT_JOG_SERVO_SPEED_REGISTER`.

### API Commands

The HTTP API exposes the new path:

```bash
curl -X POST http://127.0.0.1:4000/control/jog/start \
  -H 'content-type: application/json' \
  -d '{"mode":"absolute_pose"}'

curl -X POST http://127.0.0.1:4000/control/jog/target-pose \
  -H 'content-type: application/json' \
  -d '{"position_m":{"x":0.489,"y":0,"z":0.3701},"orientation_quat_xyzw":{"x":0,"y":0,"z":0,"w":1}}'
```

The controller UDP equivalents are `JOG_START,absolute_pose`, `SET_JOG_MODE,absolute_pose`, and `SET_JOG_TARGET_POSE,x,y,z,qx,qy,qz,qw`.

### Diagnostics

Realtime jog telemetry now includes the solver name, teleop mode, solve time, target pose, current pose, pose error, `q_goal`, `q_commanded`, measured joints when available, `q_delta`, and rejection/failure reason. Large joint jumps still trip the jog jump guard before servo commands are sent.

Run the solver comparison:

```bash
./.venv/bin/python scripts/ik_solver_benchmark.py
./.venv/bin/python scripts/ik_solver_benchmark.py --solvers=ikfast,quik,dls,qp --json
```

The benchmark runs each solver in a separate process because backend selection happens at import time. It reports unavailable optional backends explicitly, including TRAC-IK when `trac_ik_python` is missing.
