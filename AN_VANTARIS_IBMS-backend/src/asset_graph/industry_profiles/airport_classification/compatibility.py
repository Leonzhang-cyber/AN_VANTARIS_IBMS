"""System-device compatibility checks for airport classification."""
from __future__ import annotations

from .constants import SYSTEM_DEVICE_COMPATIBILITY


def evaluate_compatibility(
    *,
    generic_system_category: str,
    device_type_code: str,
    system_mapping_status: str,
    device_type_mapping_status: str,
) -> tuple[str, list[str]]:
    code = str(device_type_code or "").strip().upper()
    category = str(generic_system_category or "").strip()
    reasons: list[str] = []

    if device_type_mapping_status in {"UNKNOWN_DEVICE_TYPE_CODE", "TYPE_REVIEW_REQUIRED"}:
        return "COMPATIBILITY_REVIEW_REQUIRED", ["UNKNOWN_DEVICE_TYPE"]

    if system_mapping_status in {"UNMAPPED_SOURCE_CODE", "UNSUPPORTED_SYSTEM", "REVIEW_REQUIRED", "AMBIGUOUS_SOURCE_CODE"}:
        return "COMPATIBILITY_REVIEW_REQUIRED", ["SYSTEM_MAPPING_UNRESOLVED"]

    if not category or not code:
        return "COMPATIBILITY_REVIEW_REQUIRED", ["MISSING_CATEGORY_OR_TYPE"]

    expected = SYSTEM_DEVICE_COMPATIBILITY.get(category)
    if expected is None:
        return "COMPATIBILITY_REVIEW_REQUIRED", ["UNCATALOGUED_SYSTEM_CATEGORY"]

    if code in expected:
        return "SYSTEM_DEVICE_COMPATIBLE", reasons

    if device_type_mapping_status == "DEVICE_TYPE_COLUMN_CONFLICT":
        return "SYSTEM_DEVICE_CONFLICT", ["DEVICE_TYPE_COLUMN_CONFLICT"]

    return "SYSTEM_DEVICE_UNEXPECTED", ["UNEXPECTED_DEVICE_TYPE_FOR_SYSTEM"]
