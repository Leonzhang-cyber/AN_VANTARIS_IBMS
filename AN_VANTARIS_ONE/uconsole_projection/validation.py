"""Fail-closed validation for read-only UConsole projections."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .enums import GENERATED_AT_POLICY
from .errors import UConsoleProjectionError


def validate_projection(projection: Mapping[str, Any]) -> None:
    required = (
        "projectionId",
        "projectionType",
        "authority",
        "profileId",
        "projectionVersion",
        "implementationStatus",
        "readinessOutcome",
        "summary",
        "dashboardCards",
        "healthSummaryCards",
        "reviewQueueCards",
        "evidenceContractCards",
        "sourceSystemRows",
        "filters",
        "facets",
        "defaultPage",
        "sourceArtifactReferences",
        "generatedAtPolicy",
        "deterministicDigest",
    )
    for key in required:
        if key not in projection:
            raise UConsoleProjectionError("MISSING_REQUIRED_FIELD", f"missing required field: {key}")

    if projection.get("generatedAtPolicy") != GENERATED_AT_POLICY:
        raise UConsoleProjectionError("INVALID_GENERATED_AT_POLICY", "volatile timestamp policy is forbidden")

    if "generatedAt" in projection or "observedAt" in projection:
        raise UConsoleProjectionError("VOLATILE_TIMESTAMP", "volatile timestamps are forbidden")

    summary = projection.get("summary", {})
    for flag in ("frontendEnabled", "apiEnabled", "databaseAccessEnabled", "productionActivationEnabled"):
        if summary.get(flag) is True:
            raise UConsoleProjectionError("FORBIDDEN_CAPABILITY", f"{flag} must remain false")

    if summary.get("runtimeConnectorExecutionEnabled") is True:
        raise UConsoleProjectionError("FORBIDDEN_CAPABILITY", "runtimeConnectorExecutionEnabled must remain false")

    rows = projection.get("sourceSystemRows", [])
    if not isinstance(rows, Sequence) or not rows:
        raise UConsoleProjectionError("EMPTY_SOURCE_SYSTEM_ROWS", "sourceSystemRows must not be empty")

    for row in rows:
        _validate_row(row)

    for section in ("dashboardCards", "healthSummaryCards", "reviewQueueCards", "evidenceContractCards"):
        cards = projection.get(section, [])
        if not isinstance(cards, Sequence):
            raise UConsoleProjectionError("INVALID_CARD_SECTION", f"{section} must be a sequence")
        for card in cards:
            _validate_card(card)


def _validate_row(row: Mapping[str, Any]) -> None:
    required = (
        "rowId",
        "sourceSystemKey",
        "registryEntryId",
        "lifecycleState",
        "approvalState",
        "readinessState",
        "integrationHealthState",
        "reviewState",
        "evidenceContractState",
        "runtimeObserved",
        "runtimeVerified",
        "deviceEvidenceCount",
        "pendingDecisionCount",
        "findingCount",
        "deterministicDigest",
    )
    for key in required:
        if key not in row:
            raise UConsoleProjectionError("MISSING_ROW_FIELD", f"missing row field: {key}")


def _validate_card(card: Mapping[str, Any]) -> None:
    required = (
        "cardId",
        "cardType",
        "title",
        "severity",
        "status",
        "value",
        "unit",
        "affectedSourceSystemKeys",
        "decisionRequired",
        "evidenceReferences",
        "deterministicDigest",
    )
    for key in required:
        if key not in card:
            raise UConsoleProjectionError("MISSING_CARD_FIELD", f"missing card field: {key}")
