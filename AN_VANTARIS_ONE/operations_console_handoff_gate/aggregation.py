"""Aggregation helpers for Operations Console Handoff Gates."""
from __future__ import annotations

from typing import Any, Mapping

from .models import build_boundary_matrix_entry


def build_boundary_matrix(boundaries: Mapping[str, tuple[Any, Any, bool]]) -> list[dict[str, Any]]:
    return [
        build_boundary_matrix_entry(
            boundary_key=key,
            expected_value=expected,
            actual_value=actual,
            status="PASS" if actual == expected else "FAIL",
            blocking=blocking,
        )
        for key, (expected, actual, blocking) in sorted(boundaries.items())
    ]
