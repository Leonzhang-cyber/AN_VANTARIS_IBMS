"""Validation helpers for API / Frontend implementation readiness gates."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import ApiFrontendImplementationGateError


def validate_api_frontend_implementation_readiness_gate(gate: Mapping[str, Any]) -> None:
    summary = gate.get("summary", {})
    expected = {
        "apiEndpointCandidateCount": 8,
        "readOnlyEndpointCandidateCount": 8,
        "frontendPageCandidateCount": 8,
        "frontendRouteCandidateCount": 8,
        "dataBindingContractCount": 15,
        "cardBindingContractCount": 8,
        "queueBindingContractCount": 8,
        "authPolicyRequiredCount": 8,
        "contractReadinessGateCount": 15,
        "contractPassedGateCount": 15,
        "implementationReleaseGateCount": 16,
        "implementationPassedGateCount": 16,
        "blockingGateFailureCount": 0,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise ApiFrontendImplementationGateError("SUMMARY_COUNT_INVALID", f"{key} must be {value}")
    for key in ("a5HandoffAllowed", "a4ReleaseAllowed", "a3ReleaseAllowed", "apiSkeletonPhaseAllowed", "frontendSkeletonPhaseAllowed", "crossIndustry"):
        if summary.get(key) is not True:
            raise ApiFrontendImplementationGateError("REQUIRED_TRUE_FLAG_INVALID", f"{key} must be true")
    for key in ("productionApiAllowed", "productionFrontendAllowed", "databaseWriteAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "apiEnabled", "frontendEnabled", "containsCustomerAssetIdentifiers", "airportSpecific"):
        if summary.get(key) is not False:
            raise ApiFrontendImplementationGateError("REQUIRED_FALSE_FLAG_INVALID", f"{key} must be false")
    for key in ("databaseWriteCount", "canonicalWriteCount", "decisionWriteCount", "approvalWriteCount", "auditWriteCount"):
        if summary.get(key) != 0:
            raise ApiFrontendImplementationGateError("WRITE_COUNT_INVALID", f"{key} must be zero")
    if len(gate.get("releaseGateResults", [])) != 16 or any(item.get("status") != "PASS" for item in gate.get("releaseGateResults", [])):
        raise ApiFrontendImplementationGateError("RELEASE_GATES_INVALID", "all sixteen release gates must pass")
    decision = gate.get("implementationDecision", {})
    if decision.get("apiSkeletonPhaseAllowed") is not True or decision.get("frontendSkeletonPhaseAllowed") is not True:
        raise ApiFrontendImplementationGateError("SKELETON_PLANNING_NOT_ALLOWED", "future skeleton planning must be allowed")
    for key in ("productionApiAllowed", "productionFrontendAllowed", "databaseWriteAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed"):
        if decision.get(key) is not False:
            raise ApiFrontendImplementationGateError("IMPLEMENTATION_DECISION_BOUNDARY_INVALID", f"{key} must be false")


def validate_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = ("sql" + "alchemy", "fla" + "sk", "req" + "uests.", "url" + "lib", "soc" + "ket", "blue" + "print", "api." + "route", "src." + "ufms", "src." + "umms")
    found = [token for token in forbidden if token in lowered]
    if found:
        raise ApiFrontendImplementationGateError("BOUNDARY_VIOLATION", ", ".join(found))
