"""Validation helpers for operator review decision projections."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import OperatorReviewDecisionError


def validate_operator_review_decision_projection(projection: Mapping[str, Any]) -> None:
    summary = projection.get("summary", {})
    if len(projection.get("decisionItems", [])) != 46:
        raise OperatorReviewDecisionError("DECISION_ITEM_COUNT_INVALID", "expected 46 decision items")
    if len(projection.get("decisionGroups", [])) != 8:
        raise OperatorReviewDecisionError("DECISION_GROUP_COUNT_INVALID", "expected 8 decision groups")
    if len(projection.get("decisionQueues", [])) != 8:
        raise OperatorReviewDecisionError("DECISION_QUEUE_COUNT_INVALID", "expected 8 decision queues")
    if summary.get("blockingDecisionCount") != 45 or summary.get("nonBlockingDecisionCount") != 1:
        raise OperatorReviewDecisionError("BLOCKING_DECISION_COUNTS_INVALID", "expected 45 blocking and 1 non-blocking")
    for key in ("decisionWriteCount", "approvalWriteCount", "canonicalWriteCount", "databaseWriteCount"):
        if summary.get(key) != 0:
            raise OperatorReviewDecisionError("FORBIDDEN_WRITE_COUNT", f"{key} must be zero")
    for key in ("apiEnabled", "frontendEnabled", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "containsCustomerAssetIdentifiers"):
        if summary.get(key) is not False:
            raise OperatorReviewDecisionError("FORBIDDEN_RUNTIME_CAPABILITY", f"{key} must be false")
    for item in projection.get("decisionItems", []):
        if item.get("decisionState") in {"APPROVED", "REJECTED"}:
            raise OperatorReviewDecisionError("DECISION_ALREADY_APPLIED", "projection must not approve or reject decisions")


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
        raise OperatorReviewDecisionError("BOUNDARY_VIOLATION", ", ".join(found))
