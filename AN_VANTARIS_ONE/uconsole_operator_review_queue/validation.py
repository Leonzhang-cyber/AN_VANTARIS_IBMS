"""Validation helpers for UConsole Operator Review Queue projections."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import UConsoleOperatorReviewQueueError


def validate_uconsole_operator_review_queue_projection(projection: Mapping[str, Any]) -> None:
    summary = projection.get("summary", {})
    if len(projection.get("queueRows", [])) != 46:
        raise UConsoleOperatorReviewQueueError("QUEUE_ROW_COUNT_INVALID", "expected 46 queue rows")
    if len(projection.get("queueGroups", [])) != 8:
        raise UConsoleOperatorReviewQueueError("QUEUE_GROUP_COUNT_INVALID", "expected 8 queue groups")
    if len(projection.get("queueCards", [])) != 8:
        raise UConsoleOperatorReviewQueueError("QUEUE_CARD_COUNT_INVALID", "expected 8 queue cards")
    if summary.get("blockingDecisionCount") != 45 or summary.get("nonBlockingDecisionCount") != 1:
        raise UConsoleOperatorReviewQueueError("BLOCKING_COUNTS_INVALID", "expected 45 blocking and 1 non-blocking")
    for key in ("decisionWriteCount", "approvalWriteCount", "canonicalWriteCount", "databaseWriteCount"):
        if summary.get(key) != 0:
            raise UConsoleOperatorReviewQueueError("FORBIDDEN_WRITE_COUNT", f"{key} must be zero")
    for key in ("apiEnabled", "frontendEnabled", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "containsCustomerAssetIdentifiers"):
        if summary.get(key) is not False:
            raise UConsoleOperatorReviewQueueError("FORBIDDEN_RUNTIME_CAPABILITY", f"{key} must be false")
    if any(row.get("decisionState") == "APPROVED" for row in projection.get("queueRows", [])):
        raise UConsoleOperatorReviewQueueError("APPROVED_ROW_FORBIDDEN", "rows must not be approved")


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
        raise UConsoleOperatorReviewQueueError("BOUNDARY_VIOLATION", ", ".join(found))
