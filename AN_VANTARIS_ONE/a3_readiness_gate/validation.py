"""Validation helpers for A3 readiness release gates."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import A3ReadinessGateError


def validate_a3_readiness_release_gate(release_gate: Mapping[str, Any]) -> None:
    summary = release_gate.get("summary", {})
    if len(release_gate.get("stageResults", [])) != 6:
        raise A3ReadinessGateError("A3_STAGE_COUNT_INVALID", "expected six A3 stage results")
    if len(release_gate.get("gateResults", [])) != 12:
        raise A3ReadinessGateError("A3_GATE_COUNT_INVALID", "expected twelve gate results")
    if summary.get("a3StageCount") != 6 or summary.get("passedStageCount") != 6:
        raise A3ReadinessGateError("A3_STAGE_SUMMARY_INVALID", "all six A3 stages must pass")
    if summary.get("gateCount") != 12 or summary.get("passedGateCount") != 12:
        raise A3ReadinessGateError("A3_GATE_SUMMARY_INVALID", "all twelve A3 gates must pass")
    if summary.get("blockingGateFailureCount") != 0:
        raise A3ReadinessGateError("A3_BLOCKING_GATE_FAILURE", "blocking gate failures must be zero")
    for key in (
        "runtimeObservedCount",
        "runtimeAlarmObservedCount",
        "ufmsFaultCaseCreatedCount",
        "workOrderIntentCreatedCount",
        "workOrderCreatedCount",
        "evidenceCenterWriteCount",
        "ummsWriteCount",
        "oneWorkManagementWriteCount",
        "canonicalWriteCount",
        "databaseWriteCount",
    ):
        if summary.get(key) != 0:
            raise A3ReadinessGateError("A3_FORBIDDEN_RUNTIME_OR_WRITE_COUNT", f"{key} must be zero")
    decision = release_gate.get("releaseDecision", {})
    if decision.get("releaseAllowed") is not True:
        raise A3ReadinessGateError("A3_RELEASE_NOT_ALLOWED", "read-only local release gate must pass")
    for key in ("pushAllowed", "productionActivationAllowed", "runtimeActivationAllowed", "databaseWriteAllowed", "apiEnabled", "frontendEnabled"):
        if decision.get(key) is not False:
            raise A3ReadinessGateError("A3_FORBIDDEN_RELEASE_CAPABILITY", f"{key} must remain false")


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
        raise A3ReadinessGateError("A3_BOUNDARY_VIOLATION", ", ".join(found))
