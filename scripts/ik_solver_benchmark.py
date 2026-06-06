#!/usr/bin/env python3
"""Benchmark available GradientOS IK solver backends on shared URDF targets."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from statistics import mean

import numpy as np
from scipy.spatial.transform import Rotation as R


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
DEFAULT_SOLVERS = ("ikfast", "quik", "trac", "dls", "qp")
TARGET_POSES = (
    ((0.489006, 0.0, 0.3701), (0.0, 0.0, 0.0)),
    ((0.469006, 0.0, 0.3901), (0.0, 0.0, 0.0)),
    ((0.449006, 0.0, 0.3901), (0.0, 0.0, 0.0)),
    ((0.489006, 0.0, 0.3701), (5.0, 0.0, 0.0)),
)


def _child_main(solver: str) -> int:
    os.environ["MINI_ARM_SOLVER"] = solver
    sys.path.insert(0, str(SRC_DIR))
    try:
        from gradient_os import ik_solver
    except Exception as exc:
        print(
            json.dumps(
                {
                    "solver": solver,
                    "available": False,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
        )
        return 0

    rows: list[dict[str, object]] = []
    seed = np.zeros(6, dtype=float)
    for index, (target_position, target_euler_deg) in enumerate(TARGET_POSES):
        target_pose = np.eye(4)
        target_pose[:3, 3] = np.asarray(target_position, dtype=float)
        target_pose[:3, :3] = R.from_euler("xyz", target_euler_deg, degrees=True).as_matrix()
        started = time.perf_counter()
        try:
            solution = ik_solver.solve_ik(
                target_position=target_pose[:3, 3],
                target_orientation_matrix=target_pose[:3, :3],
                initial_joint_angles=seed,
            )
            error = None
        except Exception as exc:
            solution = None
            error = f"{type(exc).__name__}: {exc}"
        elapsed_ms = (time.perf_counter() - started) * 1000.0

        if solution is None:
            rows.append(
                {
                    "target": index,
                    "success": False,
                    "solve_time_ms": elapsed_ms,
                    "error": error or "no solution",
                }
            )
            continue

        solution = np.asarray(solution, dtype=float).reshape(6)
        solved_pose = ik_solver.get_fk_matrix(solution)
        pos_error_m = float(np.linalg.norm(solved_pose[:3, 3] - target_pose[:3, 3]))
        rot_error_deg = float(
            np.rad2deg(
                np.linalg.norm(
                    R.from_matrix(target_pose[:3, :3] @ solved_pose[:3, :3].T).as_rotvec()
                )
            )
        )
        joint_delta_rad = float(np.linalg.norm(solution - seed))
        success = pos_error_m <= 0.01 and rot_error_deg <= 5.0
        rows.append(
            {
                "target": index,
                "success": success,
                "solve_time_ms": elapsed_ms,
                "pos_error_m": pos_error_m,
                "rot_error_deg": rot_error_deg,
                "joint_delta_rad": joint_delta_rad,
            }
        )
        seed = solution

    print(
        json.dumps(
            {
                "solver": ik_solver.get_backend_name(),
                "available": True,
                "rows": rows,
            }
        )
    )
    return 0


def _run_solver(solver: str) -> dict[str, object]:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{SRC_DIR}{os.pathsep}{env.get('PYTHONPATH', '')}"
    cmd = [sys.executable, str(Path(__file__).resolve()), "--child", solver]
    completed = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    for line in reversed(completed.stdout.splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                result = json.loads(line)
                if completed.stderr.strip():
                    result["stderr"] = completed.stderr.strip()
                return result
            except json.JSONDecodeError:
                pass
    return {
        "solver": solver,
        "available": False,
        "error": completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}",
    }


def _format_report(results: list[dict[str, object]]) -> str:
    lines = [
        "Solver   Avail  Success  Mean ms  Max pos mm  Max rot deg  Notes",
        "-------  -----  -------  -------  ----------  -----------  -----",
    ]
    for result in results:
        solver = str(result.get("solver", "unknown"))
        if not result.get("available"):
            note = str(result.get("error", "unavailable")).splitlines()[-1]
            lines.append(f"{solver:<7}  no     0/0      -        -           -            {note}")
            continue
        rows = result.get("rows", [])
        assert isinstance(rows, list)
        successes = [row for row in rows if isinstance(row, dict) and row.get("success")]
        times = [float(row.get("solve_time_ms", 0.0)) for row in rows if isinstance(row, dict)]
        pos_errors = [
            float(row.get("pos_error_m", 0.0)) * 1000.0
            for row in rows
            if isinstance(row, dict) and row.get("pos_error_m") is not None
        ]
        rot_errors = [
            float(row.get("rot_error_deg", 0.0))
            for row in rows
            if isinstance(row, dict) and row.get("rot_error_deg") is not None
        ]
        failed = len(rows) - len(successes)
        note = "" if failed == 0 else f"{failed} failed target(s)"
        lines.append(
            f"{solver:<7}  yes    {len(successes)}/{len(rows):<3}    "
            f"{mean(times) if times else 0.0:7.2f}  "
            f"{max(pos_errors) if pos_errors else 0.0:10.2f}  "
            f"{max(rot_errors) if rot_errors else 0.0:11.2f}  {note}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark GradientOS IK solvers.")
    parser.add_argument("--solvers", default=",".join(DEFAULT_SOLVERS))
    parser.add_argument("--json", action="store_true", help="Emit raw JSON results.")
    parser.add_argument("--child", choices=DEFAULT_SOLVERS, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.child:
        return _child_main(args.child)

    solvers = [item.strip() for item in args.solvers.split(",") if item.strip()]
    results = [_run_solver(solver) for solver in solvers]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(_format_report(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
