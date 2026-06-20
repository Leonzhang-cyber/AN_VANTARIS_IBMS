"""Validation helpers for Operations Console Handoff Gates."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import OperationsConsoleHandoffGateError


def validate_operations_console_handoff_gate(gate: Mapping[str, Any]) -> None:
    summary = gate.get("summary", {})
    if len(gate.get("pageHandoffMatrix", [])) != 8 or summary.get("pageHandoffCount") != 8:
        raise OperationsConsoleHandoffGateError("PAGE_HANDOFF_COUNT_INVALID", "expected eight page handoff entries")
    if len(gate.get("dataSourceHandoffMatrix", [])) != 15 or summary.get("dataSourceHandoffCount") != 15:
        raise OperationsConsoleHandoffGateError("DATASOURCE_HANDOFF_COUNT_INVALID", "expected fifteen datasource handoff entries")
    if len(gate.get("cardHandoffMatrix", [])) != 8 or summary.get("cardHandoffCount") != 8:
        raise OperationsConsoleHandoffGateError("CARD_HANDOFF_COUNT_INVALID", "expected eight card handoff entries")
    if len(gate.get("releaseGateResults", [])) != 15 or summary.get("releaseGateCount") != 15 or summary.get("passedGateCount") != 15:
        raise OperationsConsoleHandoffGateError("RELEASE_GATE_COUNT_INVALID", "expected fifteen passing release gates")
    for data_source in gate.get("dataSourceHandoffMatrix", []):
        for key, expected in (("readOnly", True), ("apiEnabled", False), ("frontendEnabled", False), ("databaseAccessEnabled", False)):
            if data_source.get(key) is not expected:
                raise OperationsConsoleHandoffGateError("DATASOURCE_BOUNDARY_INVALID", f"{data_source.get('dataSourceKey')} {key} invalid")
    for key in (
        "runtimeObservedCount",
        "runtimeAlarmObservedCount",
        "ufmsFaultCaseCreatedCount",
        "workOrderIntentCreatedCount",
        "workOrderCreatedCount",
        "evidenceCenterWriteCount",
        "ummsWriteCount",
        "oneWorkManagementWriteCount",
        "decisionWriteCount",
        "approvalWriteCount",
        "auditWriteCount",
        "canonicalWriteCount",
        "databaseWriteCount",
    ):
        if summary.get(key) != 0:
            raise OperationsConsoleHandoffGateError("FORBIDDEN_WRITE_OR_RUNTIME_COUNT", f"{key} must be zero")
    for key in ("apiEnabled", "frontendEnabled", "endpointImplementationAllowed", "frontendImplementationAllowed", "routeImplementationAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "containsCustomerAssetIdentifiers", "airportSpecific"):
        if summary.get(key) is not False:
            raise OperationsConsoleHandoffGateError("FORBIDDEN_CAPABILITY_ENABLED", f"{key} must be false")
    if summary.get("handoffAllowed") is not True or gate.get("handoffDecision", {}).get("handoffAllowed") is not True:
        raise OperationsConsoleHandoffGateError("HANDOFF_NOT_ALLOWED", "handoff must be allowed for future planning")
    if summary.get("crossIndustry") is not True:
        raise OperationsConsoleHandoffGateError("CROSS_INDUSTRY_INVALID", "VANTARIS ONE gate model must remain cross-industry")
    if any(item.get("blocking") and item.get("status") != "PASS" for item in gate.get("releaseGateResults", [])):
        raise OperationsConsoleHandoffGateError("BLOCKING_GATE_FAILED", "all blocking gates must pass")


def validate_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = ("sql" + "alchemy", "fla" + "sk", "req" + "uests.", "url" + "lib", "soc" + "ket", "blue" + "print", "rea" + "ct", "src." + "ufms", "src." + "umms")
    found = [token for token in forbidden if token in lowered]
    if found:
        raise OperationsConsoleHandoffGateError("BOUNDARY_VIOLATION", ", ".join(found))
