"""Validation helpers for alarm/event resolution review projections."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import AlarmEventResolutionError

FORBIDDEN_SUMMARY_COUNTS = (
    "ufmsFaultCaseCreatedCount",
    "workOrderIntentCreatedCount",
    "workOrderCreatedCount",
    "canonicalWriteCount",
    "databaseWriteCount",
    "runtimeAlarmObservedCount",
)


def validate_resolution_projection(projection: Mapping[str, Any]) -> None:
    summary = projection.get("summary", {})
    rows = projection.get("resolutionRows", [])
    cards = projection.get("reviewCards", [])
    if len(rows) != 5:
        raise AlarmEventResolutionError("RESOLUTION_ROW_COUNT_INVALID", "expected exactly five resolution rows")
    if len(cards) != 7:
        raise AlarmEventResolutionError("REVIEW_CARD_COUNT_INVALID", "expected exactly seven review cards")
    for key in FORBIDDEN_SUMMARY_COUNTS:
        if summary.get(key) != 0:
            raise AlarmEventResolutionError("FORBIDDEN_WRITE_OR_RUNTIME_COUNT", f"{key} must be zero")
    if summary.get("containsCustomerAssetIdentifiers") is not False:
        raise AlarmEventResolutionError("CUSTOMER_IDENTIFIER_LEAKAGE", "projection must not expose customer identifiers")


def validate_projection_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = (
        "sql" + "alchemy",
        "fla" + "sk",
        "req" + "uests.",
        "url" + "lib",
        "soc" + "ket",
        "blue" + "print",
        "rea" + "ct",
        "src." + "ufms",
        "src." + "umms",
    )
    found = [token for token in forbidden if token in lowered]
    if found:
        raise AlarmEventResolutionError("BOUNDARY_VIOLATION", ", ".join(found))
