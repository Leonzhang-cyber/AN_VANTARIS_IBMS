"""Validation helpers for the final Airport International GA release gate."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import AirportInternationalGaReleaseGateError

EXPECTED_SUMMARY = {
    "stageGroupCount": 8, "passedStageGroupCount": 8, "failedStageGroupCount": 0, "businessCapabilityCount": 15,
    "releaseGateCount": 20, "passedGateCount": 20, "blockingGateFailureCount": 0, "sourceSystemCandidateCount": 5,
    "alarmEventCandidateCount": 5, "faultCaseCandidateCount": 5, "workOrderIntentCandidateCount": 5,
    "investigationCaseCount": 5, "operationsRowCount": 5, "decisionItemCount": 46, "queueRowCount": 46,
    "policyGuardResultCount": 46, "auditPreviewCount": 46, "pageDefinitionCount": 8, "apiEndpointCandidateCount": 8,
    "readOnlyEndpointCount": 8, "frontendPageCandidateCount": 8, "frontendRouteCandidateCount": 8, "pageSkeletonCount": 8,
    "pageContractCount": 8, "totalDeviceEvidenceCount": 470, "pendingDecisionCount": 46, "blockingDecisionCount": 45,
    "runtimeObservedCount": 0, "runtimeAlarmObservedCount": 0, "ufmsFaultCaseCreatedCount": 0, "workOrderIntentCreatedCount": 0,
    "workOrderCreatedCount": 0, "evidenceCenterWriteCount": 0, "ummsWriteCount": 0, "oneWorkManagementWriteCount": 0,
    "decisionWriteCount": 0, "approvalWriteCount": 0, "auditWriteCount": 0, "canonicalWriteCount": 0, "databaseWriteCount": 0,
    "apiEnabled": False, "frontendEnabled": False, "productionApiAllowed": False, "productionFrontendAllowed": False,
    "runtimeActivationAllowed": False, "productionActivationAllowed": False, "internationalGaReadinessAllowed": True, "releaseCandidateAllowed": True,
    "pushAllowed": False, "tagAllowed": False, "containsCustomerAssetIdentifiers": False, "crossIndustry": True, "airportSpecific": False,
}


def validate_airport_international_ga_release_gate(gate: Mapping[str, Any]) -> None:
    summary = gate.get("summary", {})
    for key, value in EXPECTED_SUMMARY.items():
        if summary.get(key) != value:
            raise AirportInternationalGaReleaseGateError("SUMMARY_INVALID", f"{key} must be {value}")
    checks = (("stageResults", 8), ("businessCapabilityMatrix", 15), ("releaseGateResults", 20))
    for collection, count in checks:
        if len(gate.get(collection, [])) != count:
            raise AirportInternationalGaReleaseGateError("COUNT_INVALID", f"{collection} must contain {count}")
    if any(item.get("status") not in {"PASS", "PASS_WITH_WARNINGS"} for item in gate.get("releaseGateResults", [])):
        raise AirportInternationalGaReleaseGateError("GATE_STATUS_INVALID", "all release gates must pass")
    if any(item.get("readOnly") is not True or item.get("productionEnabled") is not False for item in gate.get("businessCapabilityMatrix", [])):
        raise AirportInternationalGaReleaseGateError("CAPABILITY_BOUNDARY_INVALID", "capabilities must be read-only and non-production")
    decision = gate.get("releaseDecision", {})
    if decision.get("decisionState") != "INTERNATIONAL_GA_READINESS_PASS" or decision.get("internationalGaReadinessAllowed") is not True or decision.get("releaseCandidateAllowed") is not True:
        raise AirportInternationalGaReleaseGateError("DECISION_INVALID", "International GA readiness candidate must pass locally")
    for key in ("pushAllowed", "tagAllowed", "productionActivationAllowed", "runtimeActivationAllowed", "databaseWriteAllowed", "apiProductionAllowed", "frontendProductionAllowed", "approvalExecutionAllowed"):
        if decision.get(key) is not False:
            raise AirportInternationalGaReleaseGateError("DECISION_BOUNDARY_INVALID", f"{key} must be false")


def validate_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = ("sql" + "alchemy", "fla" + "sk", "fast" + "api", "req" + "uests.", "url" + "lib", "soc" + "ket", "src." + "ufms", "src." + "umms", "rea" + "ct", "v" + "ue")
    found = [token for token in forbidden if token in lowered]
    if found:
        raise AirportInternationalGaReleaseGateError("BOUNDARY_VIOLATION", ", ".join(found))
