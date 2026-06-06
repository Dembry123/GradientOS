#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON_BIN="${PYTHON_BIN:-${PWD}/.venv/bin/python}"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "[pyquik] ERROR: Python not found at ${PYTHON_BIN}" >&2
  echo "[pyquik] Set PYTHON_BIN or create the repo .venv first." >&2
  exit 1
fi

git submodule update --init --recursive src/numeric_solver/quik

if ! "${PYTHON_BIN}" -m pybind11 --cmakedir >/dev/null 2>&1; then
  "${PYTHON_BIN}" -m pip install pybind11==2.13.6 pybind11-global==2.13.6
fi

if ! command -v brew >/dev/null 2>&1; then
  echo "[pyquik] ERROR: Homebrew is required on macOS to install/find Eigen." >&2
  exit 1
fi

if ! brew list --versions eigen >/dev/null 2>&1; then
  brew install eigen
fi

PYBIND11_DIR="$("${PYTHON_BIN}" -m pybind11 --cmakedir)"
EIGEN_PREFIX="$(brew --prefix eigen)"

cmake -S src/numeric_solver/pyquik -B build/pyquik \
  -DPython_EXECUTABLE="${PYTHON_BIN}" \
  -Dpybind11_DIR="${PYBIND11_DIR}" \
  -DEigen3_DIR="${EIGEN_PREFIX}/share/eigen3/cmake"
cmake --build build/pyquik -j

echo "[pyquik] Built src/numeric_solver/pyquik/pyquik*.so"
