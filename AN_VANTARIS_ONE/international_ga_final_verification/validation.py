"""Validation helpers for International GA final local verification."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import InternationalGaFinalVerificationError

EXPECTED_SUMMARY = {
    "localVerificationEntryCount": 18, "requiredVerificationCount": 18, "passedVerificationCount": 18,
    "commitChainEntryCount": 12, "activeArtifactSnapshotCount": 10, "presentActiveArtifactCount": 10,
    "verificationGateCount": 15, "passedVerificationGateCount": 15, "blockingGateFailureCount": 0,
    "handoffNotesFrozen": True, "releasePackageReady": True, "releaseGatePassed": True, "validationMatrixReady": True,
    "stakeholderHandoffReady": True, "engineeringHandoffReady": True, "internationalGaReleaseCandidateReady": True,
    "localVerificationPassed": True, "readyForStakeholderHandoff": True, "tagPlanDefined": True, "pushPlanDefined": True,
    "tagAllowedNow": False, "pushAllowedNow": False, "requiresExplicitUserApprovalForTag": True,
    "requiresExplicitUserApprovalForPush": True, "databaseWriteAllowed": False, "runtimeActivationAllowed": False,
    "productionActivationAllowed": False, "apiProductionAllowed": False, "frontendProductionAllowed": False,
    "approvalExecutionAllowed": False, "pushAllowed": False, "tagAllowed": False, "containsCustomerAssetIdentifiers": False,
    "crossIndustry": True, "airportSpecific": False,
}


def validate_international_ga_final_local_verification(verification: Mapping[str, Any]) -> None:
    summary = verification.get("summary", {})
    for key, value in EXPECTED_SUMMARY.items():
        if summary.get(key) != value:
            raise InternationalGaFinalVerificationError("SUMMARY_INVALID", f"{key} must be {value}")
    checks = (("localVerificationMatrix", 18), ("commitChainSummary", 12), ("activeArtifactSnapshot", 10), ("verificationGates", 15))
    for collection, count in checks:
        if len(verification.get(collection, [])) != count:
            raise InternationalGaFinalVerificationError("COUNT_INVALID", f"{collection} must contain {count}")
    if any(item.get("status") != "PASS" for item in verification.get("verificationGates", [])):
        raise InternationalGaFinalVerificationError("GATE_INVALID", "all verification gates must pass")
    if verification.get("optionalTagPlan", {}).get("tagAllowedNow") is not False or verification.get("optionalPushPlan", {}).get("pushAllowedNow") is not False:
        raise InternationalGaFinalVerificationError("RELEASE_PLAN_INVALID", "tag and push must be plan-only")
    boundary = verification.get("finalBoundaryStatement", {})
    for key in ("databaseWriteAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "apiProductionAllowed", "frontendProductionAllowed", "approvalExecutionAllowed", "pushAllowed", "tagAllowed", "customerIdentifierLeakageAllowed"):
        if boundary.get(key) is not False:
            raise InternationalGaFinalVerificationError("BOUNDARY_INVALID", f"{key} must be false")


def validate_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = ("sql" + "alchemy", "fla" + "sk", "fast" + "api", "req" + "uests.", "url" + "lib", "soc" + "ket", "src." + "ufms", "src." + "umms", "rea" + "ct", "v" + "ue")
    found = [token for token in forbidden if token in lowered]
    if found:
        raise InternationalGaFinalVerificationError("BOUNDARY_VIOLATION", ", ".join(found))
