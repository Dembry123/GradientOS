# AGENT_SCRATCHPAD

Persistent execution memory for repo-local workflow and technical guardrails.

## File Policy

- `COMMITTED`: this file captures shared execution lessons for future agents.

## Session Entries

### 2026-06-04 16:56 CDT - IKFast generated solver internals

#### Trigger / Context

- User asked why the IKFast solver is called generated, whether it is just an imported open-source C++ file, and requested an explanation of the internal branching/decision-tree behavior.

#### Useful Mental Model

- `ikfast_solver.cpp` is both open-source-style IKFast code and robot-specific generated code:
  - boilerplate/API support comes from IKFast/OpenRAVE conventions.
  - robot geometry constants and algebraic solution branches are generated for this specific arm.
- `ComputeIk` enumerates analytic branches, validates each branch with thresholded equations (`evalcond`), and appends valid joint vectors.
- `ik_wrapper.cpp` is the repo-authored pybind wrapper that chooses the nearest candidate solution to the current joint seed and applies a max-step guard.

#### Guardrails For Next Session

- When explaining IKFast, distinguish:
  - IKFast generator/framework
  - generated robot-specific C++ solver
  - repo wrapper/selection logic
  - Python jog/trajectory caller
- Do not describe the generated branching as learned AI or generic numerical optimization; it is explicit trigonometric case enumeration with validity checks.

#### Follow-Ups / Risks

- `DEVLOG.md` and `AGENT_SCRATCHPAD.md` were absent in this checkout, so both were recreated minimally to satisfy AGENTS workflow requirements.
