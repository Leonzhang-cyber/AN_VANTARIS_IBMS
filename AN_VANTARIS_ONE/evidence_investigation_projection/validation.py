"""Validation helpers for Evidence Investigation projections."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import EvidenceInvestigationProjectionError

ZERO_SUMMARY_KEYS = (
    "evidenceCenterWriteCount",
    "ufmsFaultCaseCreatedCount",
    "workOrderIntentCreatedCount",
    "workOrderCreatedCount",
    "ummsWriteCount",
    "oneWorkManagementWriteCount",
    "canonicalWriteCount",
    "databaseWriteCount",
    "runtimeAlarmObservedCount",
)


def validate_evidence_investigation_projection(projection: Mapping[str, Any]) -> None:
    summary = projection.get("summary", {})
    if len(projection.get("investigationCases", [])) != 5:
        raise EvidenceInvestigationProjectionError("INVESTIGATION_CASE_COUNT_INVALID", "expected five cases")
    if len(projection.get("evidenceLinks", [])) < 20:
        raise EvidenceInvestigationProjectionError("EVIDENCE_LINK_COUNT_INVALID", "expected at least twenty links")
    if len(projection.get("investigationTimeline", [])) < 20:
        raise EvidenceInvestigationProjectionError("TIMELINE_COUNT_INVALID", "expected at least twenty timeline items")
    if len(projection.get("reviewCards", [])) != 9:
        raise EvidenceInvestigationProjectionError("REVIEW_CARD_COUNT_INVALID", "expected nine review cards")
    for key in ZERO_SUMMARY_KEYS:
        if summary.get(key) != 0:
            raise EvidenceInvestigationProjectionError("FORBIDDEN_WRITE_OR_RUNTIME_COUNT", f"{key} must be zero")
    if summary.get("containsCustomerAssetIdentifiers") is not False:
        raise EvidenceInvestigationProjectionError("CUSTOMER_IDENTIFIER_LEAKAGE", "projection must not expose identifiers")


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
        raise EvidenceInvestigationProjectionError("BOUNDARY_VIOLATION", ", ".join(found))
