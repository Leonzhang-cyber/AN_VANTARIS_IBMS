"""Validation helpers for UConsole Alarm/Event Operations projections."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import UConsoleAlarmEventOperationsError

ZERO_SUMMARY_KEYS = (
    "runtimeAlarmObservedCount",
    "ufmsFaultCaseCreatedCount",
    "workOrderIntentCreatedCount",
    "workOrderCreatedCount",
    "evidenceCenterWriteCount",
    "ummsWriteCount",
    "oneWorkManagementWriteCount",
    "canonicalWriteCount",
    "databaseWriteCount",
)


def validate_operations_projection(projection: Mapping[str, Any]) -> None:
    summary = projection.get("summary", {})
    if len(projection.get("operationsRows", [])) != 5:
        raise UConsoleAlarmEventOperationsError("OPERATIONS_ROW_COUNT_INVALID", "expected five rows")
    if len(projection.get("operationsCards", [])) != 7:
        raise UConsoleAlarmEventOperationsError("OPERATIONS_CARD_COUNT_INVALID", "expected seven cards")
    for key in ZERO_SUMMARY_KEYS:
        if summary.get(key) != 0:
            raise UConsoleAlarmEventOperationsError("FORBIDDEN_WRITE_OR_RUNTIME_COUNT", f"{key} must be zero")
    if summary.get("apiEnabled") is not False or summary.get("frontendEnabled") is not False:
        raise UConsoleAlarmEventOperationsError("RUNTIME_SURFACE_ENABLED", "api/frontend must remain disabled")
    if summary.get("containsCustomerAssetIdentifiers") is not False:
        raise UConsoleAlarmEventOperationsError("CUSTOMER_IDENTIFIER_LEAKAGE", "projection must not expose identifiers")


def validate_boundary(source_text: str) -> None:
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
        raise UConsoleAlarmEventOperationsError("BOUNDARY_VIOLATION", ", ".join(found))
