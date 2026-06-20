"""Validation helpers for A4 readiness release gates."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import A4ReadinessGateError


def validate_a4_readiness_release_gate(release_gate: Mapping[str, Any]) -> None:
    summary = release_gate.get("summary", {})
    if len(release_gate.get("stageResults", [])) != 3:
        raise A4ReadinessGateError("A4_STAGE_COUNT_INVALID", "expected three A4 stage results")
    if len(release_gate.get("gateResults", [])) != 15:
        raise A4ReadinessGateError("A4_GATE_COUNT_INVALID", "expected fifteen A4 gate results")
    if summary.get("a4StageCount") != 3 or summary.get("passedStageCount") != 3:
        raise A4ReadinessGateError("A4_STAGE_SUMMARY_INVALID", "all three A4 stages must pass")
    if summary.get("gateCount") != 15 or summary.get("passedGateCount") != 15:
        raise A4ReadinessGateError("A4_GATE_SUMMARY_INVALID", "all fifteen A4 gates must pass")
    for key in ("decisionWriteCount", "approvalWriteCount", "auditWriteCount", "canonicalWriteCount", "databaseWriteCount"):
        if summary.get(key) != 0:
            raise A4ReadinessGateError("A4_FORBIDDEN_WRITE_COUNT", f"{key} must be zero")
    decision = release_gate.get("releaseDecision", {})
    if decision.get("releaseAllowed") is not True:
        raise A4ReadinessGateError("A4_RELEASE_NOT_ALLOWED", "read-only local release gate must pass")
    for key in ("pushAllowed", "productionActivationAllowed", "runtimeActivationAllowed", "databaseWriteAllowed", "decisionWriteAllowed", "approvalWriteAllowed", "auditWriteAllowed", "apiEnabled", "frontendEnabled"):
        if decision.get(key) is not False:
            raise A4ReadinessGateError("A4_FORBIDDEN_RELEASE_CAPABILITY", f"{key} must remain false")


def validate_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = ("sql" + "alchemy", "fla" + "sk", "req" + "uests.", "url" + "lib", "soc" + "ket", "blue" + "print", "rea" + "ct", "src." + "ufms", "src." + "umms")
    found = [token for token in forbidden if token in lowered]
    if found:
        raise A4ReadinessGateError("A4_BOUNDARY_VIOLATION", ", ".join(found))
