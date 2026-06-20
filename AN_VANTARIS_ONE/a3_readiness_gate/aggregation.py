"""Aggregation helpers for A3 readiness release gates."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .enums import GateStatus
from .models import build_boundary_matrix_entry, build_regression_matrix_entry


def build_regression_matrix(specs: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        build_regression_matrix_entry(
            validator_name=str(spec["validatorName"]),
            command=str(spec["command"]),
            expected_marker=str(spec["expectedMarker"]),
            status=str(spec.get("status", GateStatus.PASS.value)),
            required_for_release=bool(spec.get("requiredForRelease", True)),
        )
        for spec in specs
    ]


def build_boundary_matrix(boundaries: Mapping[str, tuple[Any, Any, bool]]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for key in sorted(boundaries):
        expected, actual, blocking = boundaries[key]
        entries.append(
            build_boundary_matrix_entry(
                boundary_key=key,
                expected_value=expected,
                actual_value=actual,
                status=GateStatus.PASS.value if expected == actual else GateStatus.FAIL.value,
                blocking=blocking,
            )
        )
    return entries
