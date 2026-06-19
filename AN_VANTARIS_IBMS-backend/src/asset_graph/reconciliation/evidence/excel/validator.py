"""Workbook validation for synthetic Excel evidence intake."""
from __future__ import annotations

import re
from collections import Counter
from typing import Any, Mapping, Sequence

from src.asset_graph.reconciliation.evidence.runner import PROHIBITED_KEY, PROHIBITED_VALUE

from .constants import (
    BUSINESS_SHEETS,
    DEFAULT_SITES,
    DEVICES_REQUIRED_COLUMNS,
    EXPECTED_PROFILE,
    REJECTED_CATEGORIES,
    REJECTED_SAMPLES_REQUIRED_COLUMNS,
    SCENARIO_CLASSES,
    STANDARD_FIELDS_REQUIRED_COLUMNS,
)
from .errors import ExcelIntakeError
from .workbook import ExcelWorkbook

_ACCEPTED_PRIVACY_KEY = re.compile(
    r"(password|secret|token|bearer|api[_-]?key|private[_-]?key|credential|telemetry|"
    r"current[_-]?value|connection[_-]?string|database[_-]?url)",
    re.IGNORECASE,
)


def validate_required_columns(headers: Sequence[str], required: Sequence[str], sheet: str) -> None:
    missing = [column for column in required if column not in headers]
    if missing:
        raise ExcelIntakeError("MISSING_COLUMNS", f"{sheet} missing columns: {', '.join(missing)}")


def validate_scenario_classes(rows: Sequence[Mapping[str, Any]], sheet: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for index, row in enumerate(rows, start=2):
        value = str(row.get("ScenarioClass", "")).strip().upper()
        if not value:
            raise ExcelIntakeError("MISSING_SCENARIO_CLASS", f"{sheet} row {index} missing ScenarioClass")
        if value not in SCENARIO_CLASSES:
            raise ExcelIntakeError("INVALID_SCENARIO_CLASS", f"{sheet} row {index} has invalid ScenarioClass")
        counts[value] += 1
    return counts


def _scan_accepted_privacy(rows: Sequence[Mapping[str, Any]], sheet: str) -> None:
    for index, row in enumerate(rows, start=2):
        for key, value in row.items():
            key_text = str(key)
            if key_text in {"ReviewNotes", "BlockerNotes", "Scenario", "ScenarioClass", "RowID"}:
                continue
            if _ACCEPTED_PRIVACY_KEY.search(key_text):
                raise ExcelIntakeError(
                    "PROHIBITED_FIELD_IN_ACCEPTED_SHEET",
                    f"{sheet} row {index} contains prohibited field name",
                )
            if isinstance(value, str) and PROHIBITED_VALUE.search(value):
                raise ExcelIntakeError(
                    "PROHIBITED_VALUE_IN_ACCEPTED_SHEET",
                    f"{sheet} row {index} contains prohibited value pattern",
                )
            if isinstance(value, str) and PROHIBITED_KEY.search(key_text) is None and PROHIBITED_VALUE.search(value):
                raise ExcelIntakeError(
                    "PROHIBITED_VALUE_IN_ACCEPTED_SHEET",
                    f"{sheet} row {index} contains prohibited value pattern",
                )


def validate_workbook_profile(
    device_rows: Sequence[Mapping[str, Any]],
    field_rows: Sequence[Mapping[str, Any]],
    rejected_rows: Sequence[Mapping[str, Any]],
    *,
    enforce_fixture_profile: bool = True,
) -> dict[str, Any]:
    device_count = len(device_rows)
    field_count = len(field_rows)
    if device_count < EXPECTED_PROFILE["device_rows_min"] or device_count > EXPECTED_PROFILE["device_rows_max"]:
        raise ExcelIntakeError("DEVICE_ROW_COUNT", "Devices row count is outside allowed bounds")
    if field_count < EXPECTED_PROFILE["field_rows_min"] or field_count > EXPECTED_PROFILE["field_rows_max"]:
        raise ExcelIntakeError("FIELD_ROW_COUNT", "StandardFields row count is outside allowed bounds")

    device_classes = validate_scenario_classes(device_rows, "Devices")
    field_classes = validate_scenario_classes(field_rows, "StandardFields")
    _scan_accepted_privacy(device_rows, "Devices")
    _scan_accepted_privacy(field_rows, "StandardFields")

    sites = sorted({
        str(row.get("SiteID", "")).strip()
        for row in list(device_rows) + list(field_rows)
        if str(row.get("SiteID", "")).strip() in DEFAULT_SITES
    })
    namespaces = sorted({
        str(row.get("SourceNamespace", "")).strip()
        for row in list(device_rows) + list(field_rows)
        if str(row.get("SourceNamespace", "")).strip()
    })
    if len(sites) != EXPECTED_PROFILE["sites"]:
        raise ExcelIntakeError("SITE_COUNT", f"expected {EXPECTED_PROFILE['sites']} sites, found {len(sites)}")
    if len(namespaces) < EXPECTED_PROFILE["namespaces_min"] or len(namespaces) > EXPECTED_PROFILE["namespaces_max"]:
        raise ExcelIntakeError("NAMESPACE_COUNT", "source namespace count is outside allowed bounds")

    for index, row in enumerate(rejected_rows, start=2):
        category = str(row.get("Category", "")).strip().upper()
        if category not in REJECTED_CATEGORIES:
            raise ExcelIntakeError("INVALID_REJECTED_CATEGORY", f"RejectedSamples row {index} has invalid category")

    profile = {
        "deviceRows": device_count,
        "standardFieldRows": field_count,
        "deviceScenarioDistribution": dict(device_classes),
        "fieldScenarioDistribution": dict(field_classes),
        "sites": sites,
        "sourceNamespaces": namespaces,
        "rejectedSampleCount": len(rejected_rows),
    }

    if enforce_fixture_profile:
        expected = EXPECTED_PROFILE
        if device_count != expected["device_rows"]:
            raise ExcelIntakeError("FIXTURE_DEVICE_COUNT", "workbook device count differs from approved synthetic fixture")
        if field_count != expected["standard_field_rows"]:
            raise ExcelIntakeError("FIXTURE_FIELD_COUNT", "workbook field count differs from approved synthetic fixture")
        if device_classes.get("CLEAN", 0) != expected["device_clean"]:
            raise ExcelIntakeError("FIXTURE_DEVICE_CLEAN", "device CLEAN distribution differs from approved fixture")
        if device_classes.get("REVIEW", 0) != expected["device_review"]:
            raise ExcelIntakeError("FIXTURE_DEVICE_REVIEW", "device REVIEW distribution differs from approved fixture")
        if device_classes.get("BLOCKER", 0) != expected["device_blocker"]:
            raise ExcelIntakeError("FIXTURE_DEVICE_BLOCKER", "device BLOCKER distribution differs from approved fixture")
        if field_classes.get("CLEAN", 0) != expected["field_clean"]:
            raise ExcelIntakeError("FIXTURE_FIELD_CLEAN", "field CLEAN distribution differs from approved fixture")
        if field_classes.get("REVIEW", 0) != expected["field_review"]:
            raise ExcelIntakeError("FIXTURE_FIELD_REVIEW", "field REVIEW distribution differs from approved fixture")
        if field_classes.get("BLOCKER", 0) != expected["field_blocker"]:
            raise ExcelIntakeError("FIXTURE_FIELD_BLOCKER", "field BLOCKER distribution differs from approved fixture")
        if len(rejected_rows) != expected["rejected_samples"]:
            raise ExcelIntakeError("FIXTURE_REJECTED_COUNT", "rejected sample count differs from approved fixture")

    return profile


def validate_workbook(book: ExcelWorkbook, *, enforce_fixture_profile: bool = True) -> dict[str, Any]:
    if book.has_hidden_binary_payload():
        raise ExcelIntakeError("HIDDEN_BINARY_PAYLOAD", "hidden binary payload is not accepted")
    device_rows = book.rows("Devices")
    field_rows = book.rows("StandardFields")
    rejected_rows = book.rows("RejectedSamples")
    if not device_rows:
        raise ExcelIntakeError("EMPTY_DEVICES", "Devices worksheet contains no data rows")
    if not field_rows:
        raise ExcelIntakeError("EMPTY_STANDARD_FIELDS", "StandardFields worksheet contains no data rows")
    validate_required_columns(tuple(device_rows[0]), DEVICES_REQUIRED_COLUMNS, "Devices")
    validate_required_columns(tuple(field_rows[0]), STANDARD_FIELDS_REQUIRED_COLUMNS, "StandardFields")
    if rejected_rows:
        validate_required_columns(tuple(rejected_rows[0]), REJECTED_SAMPLES_REQUIRED_COLUMNS, "RejectedSamples")
    return validate_workbook_profile(
        device_rows,
        field_rows,
        rejected_rows,
        enforce_fixture_profile=enforce_fixture_profile,
    )
