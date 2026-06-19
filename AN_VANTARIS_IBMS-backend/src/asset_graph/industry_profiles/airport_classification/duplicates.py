"""Duplicate device classification comparison."""
from __future__ import annotations

from typing import Any


def compare_duplicate_classifications(bindings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for binding in bindings:
        source_id = str(binding.get("sourceId", ""))
        if not source_id:
            continue
        grouped.setdefault(source_id, []).append(binding)

    findings: list[dict[str, Any]] = []
    for source_id, rows in sorted(grouped.items()):
        if len(rows) < 2:
            continue
        systems = {str(row.get("systemMappingStatus", "")) for row in rows}
        categories = {str(row.get("genericSystemCategory", "")) for row in rows}
        types = {str(row.get("deviceTypeMappingStatus", "")) for row in rows}
        classes = {str(row.get("genericDeviceClass", "")) for row in rows}
        compat = {str(row.get("compatibilityStatus", "")) for row in rows}

        if len(systems) == 1 and len(categories) == 1 and len(types) == 1 and len(classes) == 1 and len(compat) == 1:
            status = "DUPLICATE_CLASSIFICATION_AGREEMENT"
            reasons: list[str] = []
        elif systems != {next(iter(systems))} or categories != {next(iter(categories))}:
            status = "DUPLICATE_SYSTEM_CONFLICT"
            reasons = ["DUPLICATE_SYSTEM_MAPPING_DIVERGENCE"]
        elif types != {next(iter(types))} or classes != {next(iter(classes))}:
            status = "DUPLICATE_DEVICE_TYPE_CONFLICT"
            reasons = ["DUPLICATE_DEVICE_TYPE_DIVERGENCE"]
        else:
            status = "DUPLICATE_CLASSIFICATION_REVIEW_REQUIRED"
            reasons = ["DUPLICATE_CLASSIFICATION_PARTIAL_DIVERGENCE"]

        findings.append(
            {
                "classification": status,
                "occurrenceCount": len(rows),
                "sourceDeviceDigest": str(rows[0].get("deviceCandidateDigest", "")),
                "systemMappingStatuses": sorted(systems),
                "deviceTypeMappingStatuses": sorted(types),
                "compatibilityStatuses": sorted(compat),
                "reviewReasons": reasons,
            }
        )
    return findings
