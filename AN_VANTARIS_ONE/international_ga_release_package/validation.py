"""Validation helpers for International GA release candidate packages."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import InternationalGaReleasePackageError

EXPECTED_SUMMARY = {
    "stageInventoryCount": 9, "activeStageCount": 9, "failedStageCount": 0, "artifactInventoryCount": 30,
    "requiredArtifactCount": 30, "presentRequiredArtifactCount": 30, "validatorMatrixCount": 20, "requiredValidatorCount": 20,
    "passedValidatorCount": 20, "unitTestMatrixCount": 9, "handoffInventoryCount": 6, "packagingGateCount": 18,
    "passedPackagingGateCount": 18, "blockingGateFailureCount": 0, "businessCapabilityCount": 15, "releaseGateCount": 20,
    "passedGateCount": 20, "sourceSystemCandidateCount": 5, "alarmEventCandidateCount": 5, "faultCaseCandidateCount": 5,
    "workOrderIntentCandidateCount": 5, "investigationCaseCount": 5, "operationsRowCount": 5, "decisionItemCount": 46,
    "queueRowCount": 46, "policyGuardResultCount": 46, "auditPreviewCount": 46, "pageDefinitionCount": 8,
    "apiEndpointCandidateCount": 8, "readOnlyEndpointCount": 8, "frontendPageCandidateCount": 8, "frontendRouteCandidateCount": 8,
    "pageSkeletonCount": 8, "pageContractCount": 8, "totalDeviceEvidenceCount": 470, "pendingDecisionCount": 46,
    "blockingDecisionCount": 45, "runtimeObservedCount": 0, "runtimeAlarmObservedCount": 0, "ufmsFaultCaseCreatedCount": 0,
    "workOrderIntentCreatedCount": 0, "workOrderCreatedCount": 0, "evidenceCenterWriteCount": 0, "ummsWriteCount": 0,
    "oneWorkManagementWriteCount": 0, "decisionWriteCount": 0, "approvalWriteCount": 0, "auditWriteCount": 0,
    "canonicalWriteCount": 0, "databaseWriteCount": 0, "apiEnabled": False, "frontendEnabled": False,
    "productionApiAllowed": False, "productionFrontendAllowed": False, "runtimeActivationAllowed": False,
    "productionActivationAllowed": False, "internationalGaReadinessAllowed": True, "internationalGaPackageAllowed": True,
    "releaseCandidateAllowed": True, "pushAllowed": False, "tagAllowed": False, "containsCustomerAssetIdentifiers": False,
    "crossIndustry": True, "airportSpecific": False,
}


def validate_international_ga_release_candidate_package(package: Mapping[str, Any]) -> None:
    summary = package.get("summary", {})
    for key, value in EXPECTED_SUMMARY.items():
        if summary.get(key) != value:
            raise InternationalGaReleasePackageError("SUMMARY_INVALID", f"{key} must be {value}")
    checks = (("stageInventory", 9), ("artifactInventory", 30), ("validatorMatrix", 20), ("unitTestMatrix", 9), ("handoffInventory", 6), ("packagingGates", 18))
    for collection, count in checks:
        if len(package.get(collection, [])) != count:
            raise InternationalGaReleasePackageError("COUNT_INVALID", f"{collection} must contain {count}")
    artifacts = package.get("artifactInventory", [])
    if any(item.get("required") and (not item.get("present") or not item.get("active") or item.get("legacyCompatibility")) for item in artifacts):
        raise InternationalGaReleasePackageError("ARTIFACT_INVALID", "required artifacts must be present, active, and non-legacy")
    if any("poc" in item.get("artifactPath", "").lower() and item.get("required") for item in artifacts):
        raise InternationalGaReleasePackageError("TERMINOLOGY_INVALID", "required active artifacts must not use misleading product-stage wording")
    if any(item.get("status") != "PASS" for item in package.get("packagingGates", [])):
        raise InternationalGaReleasePackageError("GATE_INVALID", "all packaging gates must pass")
    decision = package.get("releaseDecision", {})
    if decision.get("decisionState") != "INTERNATIONAL_GA_RELEASE_PACKAGE_PASS" or decision.get("internationalGaPackageAllowed") is not True:
        raise InternationalGaReleasePackageError("DECISION_INVALID", "International GA package decision must pass")
    for key in ("pushAllowed", "tagAllowed", "productionActivationAllowed", "runtimeActivationAllowed", "databaseWriteAllowed", "apiProductionAllowed", "frontendProductionAllowed", "approvalExecutionAllowed"):
        if decision.get(key) is not False:
            raise InternationalGaReleasePackageError("DECISION_BOUNDARY_INVALID", f"{key} must be false")


def validate_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = ("sql" + "alchemy", "fla" + "sk", "fast" + "api", "req" + "uests.", "url" + "lib", "soc" + "ket", "src." + "ufms", "src." + "umms", "rea" + "ct", "v" + "ue")
    found = [token for token in forbidden if token in lowered]
    if found:
        raise InternationalGaReleasePackageError("BOUNDARY_VIOLATION", ", ".join(found))
