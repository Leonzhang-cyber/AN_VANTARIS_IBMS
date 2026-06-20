"""Validation helpers for WorkOrderIntent candidate projections."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import WorkOrderIntentCandidateError

ZERO_SUMMARY_KEYS = (
    "workOrderIntentCreatedCount",
    "workOrderCreatedCount",
    "ummsWriteCount",
    "oneWorkManagementWriteCount",
    "canonicalWriteCount",
    "databaseWriteCount",
    "runtimeAlarmObservedCount",
)


def validate_workorder_intent_projection(projection: Mapping[str, Any]) -> None:
    summary = projection.get("summary", {})
    candidates = projection.get("workOrderIntentCandidates", [])
    cards = projection.get("reviewCards", [])
    if len(candidates) != 5:
        raise WorkOrderIntentCandidateError("WORKORDER_INTENT_CANDIDATE_COUNT_INVALID", "expected five candidates")
    if len(cards) != 10:
        raise WorkOrderIntentCandidateError("REVIEW_CARD_COUNT_INVALID", "expected ten review cards")
    for key in ZERO_SUMMARY_KEYS:
        if summary.get(key) != 0:
            raise WorkOrderIntentCandidateError("FORBIDDEN_WRITE_OR_RUNTIME_COUNT", f"{key} must be zero")
    if summary.get("containsCustomerAssetIdentifiers") is not False:
        raise WorkOrderIntentCandidateError("CUSTOMER_IDENTIFIER_LEAKAGE", "projection must not expose identifiers")


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
        raise WorkOrderIntentCandidateError("BOUNDARY_VIOLATION", ", ".join(found))
