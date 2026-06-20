"""Validation helpers for International GA handoff notes."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import InternationalGaHandoffNotesError

EXPECTED_SUMMARY = {
    "stakeholderHandoffSectionCount": 7, "engineeringHandoffSectionCount": 6, "validationCommandCount": 21,
    "requiredValidationCommandCount": 21, "knownWarningCount": 5, "blockingKnownWarningCount": 0, "nextPhasePlanCount": 6,
    "handoffGateCount": 13, "passedHandoffGateCount": 13, "blockingGateFailureCount": 0, "stageInventoryCount": 9,
    "artifactInventoryCount": 30, "validatorMatrixCount": 20, "unitTestMatrixCount": 9, "businessCapabilityCount": 15,
    "totalDeviceEvidenceCount": 470, "decisionItemCount": 46, "pendingDecisionCount": 46, "blockingDecisionCount": 45,
    "internationalGaPackageAllowed": True, "internationalGaReadinessAllowed": True, "releaseCandidateAllowed": True,
    "handoffNotesFrozen": True, "readyForHandoff": True, "databaseWriteAllowed": False, "runtimeActivationAllowed": False,
    "productionActivationAllowed": False, "apiProductionAllowed": False, "frontendProductionAllowed": False,
    "approvalExecutionAllowed": False, "pushAllowed": False, "tagAllowed": False, "containsCustomerAssetIdentifiers": False,
    "crossIndustry": True, "airportSpecific": False,
}


def validate_international_ga_handoff_notes(notes: Mapping[str, Any]) -> None:
    summary = notes.get("summary", {})
    for key, value in EXPECTED_SUMMARY.items():
        if summary.get(key) != value:
            raise InternationalGaHandoffNotesError("SUMMARY_INVALID", f"{key} must be {value}")
    checks = (("stakeholderHandoffSections", 7), ("engineeringHandoffSections", 6), ("validationCommandSet", 21), ("knownWarnings", 5), ("nextPhasePlan", 6), ("handoffGates", 13))
    for collection, count in checks:
        if len(notes.get(collection, [])) != count:
            raise InternationalGaHandoffNotesError("COUNT_INVALID", f"{collection} must contain {count}")
    if any(item.get("blocking") for item in notes.get("knownWarnings", [])):
        raise InternationalGaHandoffNotesError("WARNING_INVALID", "known warnings must be non-blocking")
    if any(item.get("status") != "PASS" for item in notes.get("handoffGates", [])):
        raise InternationalGaHandoffNotesError("GATE_INVALID", "all handoff gates must pass")
    boundary = notes.get("boundaryStatement", {})
    for key in ("databaseWriteAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "apiProductionAllowed", "frontendProductionAllowed", "approvalExecutionAllowed", "pushAllowed", "tagAllowed", "customerIdentifierLeakageAllowed"):
        if boundary.get(key) is not False:
            raise InternationalGaHandoffNotesError("BOUNDARY_INVALID", f"{key} must be false")


def validate_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = ("sql" + "alchemy", "fla" + "sk", "fast" + "api", "req" + "uests.", "url" + "lib", "soc" + "ket", "src." + "ufms", "src." + "umms", "rea" + "ct", "v" + "ue")
    found = [token for token in forbidden if token in lowered]
    if found:
        raise InternationalGaHandoffNotesError("BOUNDARY_VIOLATION", ", ".join(found))
