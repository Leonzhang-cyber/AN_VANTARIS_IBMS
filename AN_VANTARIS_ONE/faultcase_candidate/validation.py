"""Validation helpers for UFMS FaultCase candidate projections."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import FaultCaseCandidateError

ZERO_SUMMARY_KEYS = (
    "ufmsFaultCaseCreatedCount",
    "workOrderIntentCreatedCount",
    "workOrderCreatedCount",
    "canonicalWriteCount",
    "databaseWriteCount",
    "runtimeAlarmObservedCount",
)


def validate_faultcase_projection(projection: Mapping[str, Any]) -> None:
    summary = projection.get("summary", {})
    candidates = projection.get("faultCaseCandidates", [])
    cards = projection.get("reviewCards", [])
    if len(candidates) != 5:
        raise FaultCaseCandidateError("FAULTCASE_CANDIDATE_COUNT_INVALID", "expected exactly five candidates")
    if len(cards) != 8:
        raise FaultCaseCandidateError("REVIEW_CARD_COUNT_INVALID", "expected exactly eight review cards")
    for key in ZERO_SUMMARY_KEYS:
        if summary.get(key) != 0:
            raise FaultCaseCandidateError("FORBIDDEN_WRITE_OR_RUNTIME_COUNT", f"{key} must be zero")
    if summary.get("containsCustomerAssetIdentifiers") is not False:
        raise FaultCaseCandidateError("CUSTOMER_IDENTIFIER_LEAKAGE", "projection must not expose customer identifiers")


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
        raise FaultCaseCandidateError("BOUNDARY_VIOLATION", ", ".join(found))
