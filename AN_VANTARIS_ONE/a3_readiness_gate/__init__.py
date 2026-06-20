"""A3 readiness aggregation and release gate foundation."""
from .aggregation import build_boundary_matrix, build_regression_matrix
from .enums import GateStatus, ReleaseDecisionState, Severity
from .models import (
    CONTRACT_VERSION,
    build_a3_readiness_release_gate,
    build_artifact_reference,
    build_boundary_matrix_entry,
    build_gate_result,
    build_regression_matrix_entry,
    build_release_decision,
    build_stage_result,
)
from .validation import validate_a3_readiness_release_gate, validate_boundary

__all__ = [
    "CONTRACT_VERSION",
    "GateStatus",
    "ReleaseDecisionState",
    "Severity",
    "build_a3_readiness_release_gate",
    "build_artifact_reference",
    "build_boundary_matrix",
    "build_boundary_matrix_entry",
    "build_gate_result",
    "build_regression_matrix",
    "build_regression_matrix_entry",
    "build_release_decision",
    "build_stage_result",
    "validate_a3_readiness_release_gate",
    "validate_boundary",
]
