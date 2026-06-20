"""Validation helpers for read-only API implementation release gates."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import ReadOnlyApiReleaseGateError


EXPECTED_SUMMARY = {
    "a7StageCount": 3,
    "passedStageCount": 3,
    "failedStageCount": 0,
    "endpointCount": 8,
    "endpointSkeletonCount": 8,
    "endpointResponseContractCount": 8,
    "paginationContractCount": 8,
    "filterContractCount": 8,
    "facetContractCount": 8,
    "errorContractCount": 8,
    "authPolicyContractCount": 8,
    "mockRouteContractCount": 8,
    "localSmokeCaseCount": 8,
    "coverageEntryCount": 8,
    "mockRouteCoverageEntryCount": 8,
    "releaseGateCount": 19,
    "passedGateCount": 19,
    "blockingGateFailureCount": 0,
    "getEndpointCount": 8,
    "readOnlyEndpointCount": 8,
    "readOnlyRouteCount": 8,
    "authRequiredCount": 8,
    "rolePolicyRequiredCount": 8,
    "networkCallRequiredCount": 0,
    "localhostCallRequiredCount": 0,
    "backendRouteImplementationCount": 0,
    "productionEnabledEndpointCount": 0,
    "databaseAccessEnabledEndpointCount": 0,
    "writeOperationEnabledEndpointCount": 0,
    "runtimeActivationEnabledEndpointCount": 0,
    "readOnlyApiRouteImplementationAllowed": True,
    "productionApiAllowed": False,
    "backendRouteImplementationAllowed": False,
    "databaseAccessAllowed": False,
    "writeOperationAllowed": False,
    "runtimeActivationAllowed": False,
    "productionActivationAllowed": False,
    "frontendImplementationAllowed": False,
    "pushAllowed": False,
    "apiEnabled": False,
    "frontendEnabled": False,
    "databaseWriteCount": 0,
    "canonicalWriteCount": 0,
    "decisionWriteCount": 0,
    "approvalWriteCount": 0,
    "auditWriteCount": 0,
    "containsCustomerAssetIdentifiers": False,
    "crossIndustry": True,
    "airportSpecific": False,
}


def validate_read_only_api_release_gate(gate: Mapping[str, Any]) -> None:
    summary = gate.get("summary", {})
    for key, value in EXPECTED_SUMMARY.items():
        if summary.get(key) != value:
            raise ReadOnlyApiReleaseGateError("SUMMARY_INVALID", f"{key} must be {value}")
    if len(gate.get("stageResults", [])) != 3:
        raise ReadOnlyApiReleaseGateError("STAGE_COUNT_INVALID", "exactly 3 A7 stages are required")
    if any(stage.get("status") != "PASS" for stage in gate.get("stageResults", [])):
        raise ReadOnlyApiReleaseGateError("STAGE_STATUS_INVALID", "all A7 stages must pass")
    if len(gate.get("apiContractCoverageMatrix", [])) != 8:
        raise ReadOnlyApiReleaseGateError("COVERAGE_COUNT_INVALID", "exactly 8 endpoint coverage entries are required")
    if len(gate.get("mockRouteCoverageMatrix", [])) != 8:
        raise ReadOnlyApiReleaseGateError("MOCK_COVERAGE_COUNT_INVALID", "exactly 8 mock route coverage entries are required")
    if any(item.get("status") != "PASS" for item in gate.get("apiContractCoverageMatrix", [])):
        raise ReadOnlyApiReleaseGateError("COVERAGE_STATUS_INVALID", "all endpoint coverage entries must pass")
    if any(item.get("status") != "PASS" for item in gate.get("mockRouteCoverageMatrix", [])):
        raise ReadOnlyApiReleaseGateError("MOCK_COVERAGE_STATUS_INVALID", "all mock route coverage entries must pass")
    if len(gate.get("releaseGateResults", [])) != 19:
        raise ReadOnlyApiReleaseGateError("RELEASE_GATE_COUNT_INVALID", "exactly 19 release gates are required")
    if any(item.get("status") != "PASS" for item in gate.get("releaseGateResults", [])):
        raise ReadOnlyApiReleaseGateError("RELEASE_GATE_STATUS_INVALID", "all release gates must pass")
    decision = gate.get("implementationDecision", {})
    if decision.get("decisionState") != "READY_FOR_READ_ONLY_ROUTE_IMPLEMENTATION":
        raise ReadOnlyApiReleaseGateError("DECISION_STATE_INVALID", "future read-only route implementation must be allowed")
    if decision.get("readOnlyApiRouteImplementationAllowed") is not True:
        raise ReadOnlyApiReleaseGateError("DECISION_FLAG_INVALID", "read-only route implementation flag must be true")
    for key in ("productionApiAllowed", "backendRouteImplementationAllowed", "databaseAccessAllowed", "writeOperationAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "frontendImplementationAllowed", "pushAllowed"):
        if decision.get(key) is not False:
            raise ReadOnlyApiReleaseGateError("BOUNDARY_DECISION_INVALID", f"{key} must remain false")


def validate_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = (
        "sql" + "alchemy",
        "fla" + "sk",
        "fast" + "api",
        "req" + "uests.",
        "url" + "lib",
        "soc" + "ket",
        "src." + "ufms",
        "src." + "umms",
    )
    found = [token for token in forbidden if token in lowered]
    if found:
        raise ReadOnlyApiReleaseGateError("BOUNDARY_VIOLATION", ", ".join(found))
