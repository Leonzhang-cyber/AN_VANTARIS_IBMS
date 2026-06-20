"""Aggregation helpers for API / Frontend implementation readiness gates."""
from __future__ import annotations

from typing import Any, Mapping

from .models import build_contract_coverage_entry, build_implementation_boundary_entry


def build_contract_coverage_matrix(items: Mapping[str, tuple[str, int, int, bool]]) -> list[dict[str, Any]]:
    return [
        build_contract_coverage_entry(coverage_type=coverage_type, source_key=source_key, expected_count=expected, actual_count=actual, blocking=blocking)
        for source_key, (coverage_type, expected, actual, blocking) in sorted(items.items())
    ]


def build_implementation_boundary_matrix(items: Mapping[str, tuple[Any, Any, bool]]) -> list[dict[str, Any]]:
    return [
        build_implementation_boundary_entry(boundary_key=key, expected_value=expected, actual_value=actual, blocking=blocking)
        for key, (expected, actual, blocking) in sorted(items.items())
    ]
