"""Hierarchy validation for airport spatial profile."""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping


def validate_device_spatial_fields(device: Mapping[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    row = int(device.get("sourceRowNumber", 0))
    worksheet = str(device.get("sourceWorksheet", ""))
    checks = (
        ("buildingCode", "MISSING_BUILDING"),
        ("levelCode", "MISSING_LEVEL"),
        ("zoneCode", "MISSING_ZONE"),
        ("distributionAreaCode", "MISSING_DISTRIBUTION_AREA"),
    )
    for field, classification in checks:
        if not str(device.get(field, "")).strip():
            findings.append(
                {
                    "classification": classification,
                    "worksheet": worksheet,
                    "rowNumber": str(row),
                    "field": field,
                }
            )
    location = str(device.get("normalizedLocation", "")).strip()
    if not location:
        findings.append(
            {
                "classification": "LOCATION_MISSING",
                "worksheet": worksheet,
                "rowNumber": str(row),
                "field": "normalizedLocation",
            }
        )
    return findings


def detect_hierarchy_cycles(parent_map: dict[str, str]) -> list[str]:
    cycles: list[str] = []
    for start in parent_map:
        seen: set[str] = set()
        current = start
        while current and current in parent_map:
            if current in seen:
                cycles.append(start)
                break
            seen.add(current)
            current = parent_map[current]
    return cycles


def detect_multiple_parent_conflicts(child_parents: dict[str, set[str]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for child, parents in child_parents.items():
        if len(parents) > 1:
            findings.append(
                {
                    "classification": "MULTIPLE_PARENT_CONFLICT",
                    "candidateKey": child,
                    "parentCount": len(parents),
                }
            )
    return findings


def build_parent_map(candidates: list[Mapping[str, Any]]) -> dict[str, str]:
    parent_map: dict[str, str] = {}
    for candidate in candidates:
        key = str(candidate.get("candidateKey", ""))
        parent = str(candidate.get("parentCandidateKey", ""))
        if key and parent:
            parent_map[key] = parent
    return parent_map


def index_location_collisions(devices: list[Mapping[str, Any]]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for device in devices:
        key = str(device.get("normalizedLocation", "")).strip().upper()
        if key:
            groups[key].append(str(device.get("sourceId", "")))
    return groups
