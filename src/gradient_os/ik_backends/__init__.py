"""IK backend factory."""

from __future__ import annotations

from .base import IKBackend
from .common import (
    BackendUnavailable,
    DifferentialResult,
    END_EFFECTOR_OFFSET,
    canonical_backend_name,
    find_closest_solution,
    shortest_angular_distance,
    urdf_fk_matrix,
    wrap_to_prev,
)


def build_backend(name: str | None) -> IKBackend:
    backend_name = canonical_backend_name(name)
    if backend_name == "ikfast":
        from .ikfast_backend import IKFastBackend

        return IKFastBackend()
    if backend_name == "quik":
        from .quik_backend import QuikBackend

        return QuikBackend()
    if backend_name == "trac":
        from .trac_backend import TracBackend

        return TracBackend()
    if backend_name == "dls":
        from .dls_backend import DlsBackend

        return DlsBackend()
    if backend_name == "qp":
        from .qp_backend import QpBackend

        return QpBackend()
    raise ValueError(f"Unknown MINI_ARM_SOLVER backend '{backend_name}'")


__all__ = [
    "BackendUnavailable",
    "DifferentialResult",
    "END_EFFECTOR_OFFSET",
    "IKBackend",
    "build_backend",
    "canonical_backend_name",
    "find_closest_solution",
    "shortest_angular_distance",
    "urdf_fk_matrix",
    "wrap_to_prev",
]
