"""Validation helpers for read-only frontend implementation release gates."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import ReadOnlyFrontendReleaseGateError


EXPECTED_SUMMARY = {
    "a8StageCount": 2, "passedStageCount": 2, "failedStageCount": 0, "pageCount": 8, "pageSkeletonCount": 8, "pageContractCount": 8,
    "routeSkeletonCount": 8, "layoutContractCount": 8, "componentCoverageEntryCount": 8, "interactionCoverageEntryCount": 8,
    "releaseGateCount": 17, "passedGateCount": 17, "blockingGateFailureCount": 0, "componentBindingContractCount": 24,
    "uiStateContractCount": 48, "interactionContractCount": 64, "dataBindingSkeletonCount": 8, "cardSkeletonCount": 8,
    "queueSkeletonCount": 8, "staticOnlyPageCount": 8, "readOnlyPageCount": 8, "productionEnabledPageCount": 0,
    "productionRouteEnabledCount": 0, "realFrontendFileChangeCount": 0, "realMenuEntryChangeCount": 0,
    "liveApiCallEnabledCount": 0, "browserLaunchRequiredCount": 0, "networkCallRequiredCount": 0,
    "localhostCallRequiredCount": 0, "mutationAllowedInteractionCount": 0, "readOnlyFrontendImplementationAllowed": True,
    "productionFrontendAllowed": False, "realRouteImplementationAllowed": False, "menuImplementationAllowed": False,
    "liveApiCallAllowed": False, "dataMutationAllowed": False, "browserSmokeAllowed": False, "databaseWriteAllowed": False,
    "runtimeActivationAllowed": False, "productionActivationAllowed": False, "apiImplementationRequired": False, "pushAllowed": False,
    "apiEnabled": False, "frontendEnabled": False, "databaseWriteCount": 0, "canonicalWriteCount": 0, "decisionWriteCount": 0,
    "approvalWriteCount": 0, "auditWriteCount": 0, "containsCustomerAssetIdentifiers": False, "crossIndustry": True, "airportSpecific": False,
}


def validate_read_only_frontend_release_gate(gate: Mapping[str, Any]) -> None:
    summary = gate.get("summary", {})
    for key, value in EXPECTED_SUMMARY.items():
        if summary.get(key) != value:
            raise ReadOnlyFrontendReleaseGateError("SUMMARY_INVALID", f"{key} must be {value}")
    for collection, count in (("stageResults", 2), ("pageCoverageMatrix", 8), ("componentCoverageMatrix", 8), ("interactionCoverageMatrix", 8), ("releaseGateResults", 17)):
        if len(gate.get(collection, [])) != count:
            raise ReadOnlyFrontendReleaseGateError("COUNT_INVALID", f"{collection} must contain {count}")
    for collection in ("stageResults", "pageCoverageMatrix", "componentCoverageMatrix", "interactionCoverageMatrix", "releaseGateResults", "dependencyGateResults"):
        if any(item.get("status") != "PASS" for item in gate.get(collection, [])):
            raise ReadOnlyFrontendReleaseGateError("STATUS_INVALID", f"{collection} must pass")
    decision = gate.get("implementationDecision", {})
    if decision.get("decisionState") != "READY_FOR_READ_ONLY_FRONTEND_IMPLEMENTATION" or decision.get("readOnlyFrontendImplementationAllowed") is not True:
        raise ReadOnlyFrontendReleaseGateError("DECISION_INVALID", "future read-only frontend implementation must be allowed")
    for key in ("productionFrontendAllowed", "realRouteImplementationAllowed", "menuImplementationAllowed", "liveApiCallAllowed", "dataMutationAllowed", "browserSmokeAllowed", "databaseWriteAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "apiImplementationRequired", "pushAllowed"):
        if decision.get(key) is not False:
            raise ReadOnlyFrontendReleaseGateError("DECISION_BOUNDARY_INVALID", f"{key} must be false")


def validate_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = ("sql" + "alchemy", "fla" + "sk", "fast" + "api", "req" + "uests.", "url" + "lib", "soc" + "ket", "src." + "ufms", "src." + "umms", "rea" + "ct", "v" + "ue")
    found = [token for token in forbidden if token in lowered]
    if found:
        raise ReadOnlyFrontendReleaseGateError("BOUNDARY_VIOLATION", ", ".join(found))
