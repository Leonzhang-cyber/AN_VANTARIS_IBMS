"""Validation helpers for read-only API skeletons."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import ReadOnlyApiSkeletonError


def validate_read_only_api_skeleton(skeleton: Mapping[str, Any]) -> None:
    summary = skeleton.get("summary", {})
    expected = {
        "endpointSkeletonCount": 8,
        "getEndpointCount": 8,
        "readOnlyEndpointCount": 8,
        "responseContractCount": 8,
        "routeGroupCount": 3,
        "readinessGateCount": 14,
        "passedGateCount": 14,
        "blockingGateFailureCount": 0,
        "authPolicyRequiredCount": 8,
        "productionEnabledEndpointCount": 0,
        "databaseAccessEnabledEndpointCount": 0,
        "writeOperationEnabledEndpointCount": 0,
        "runtimeActivationEnabledEndpointCount": 0,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise ReadOnlyApiSkeletonError("SUMMARY_INVALID", f"{key} must be {value}")
    for endpoint in skeleton.get("endpointSkeletons", []):
        for key, expected_value in (("method", "GET"), ("readOnly", True), ("productionEnabled", False), ("databaseAccessEnabled", False), ("writeOperationEnabled", False), ("runtimeActivationEnabled", False)):
            if endpoint.get(key) != expected_value:
                raise ReadOnlyApiSkeletonError("ENDPOINT_BOUNDARY_INVALID", f"{endpoint.get('endpointKey')} {key} invalid")
        if endpoint.get("authPolicy") not in {"AUTH_REQUIRED", "ROLE_POLICY_REQUIRED"}:
            raise ReadOnlyApiSkeletonError("AUTH_POLICY_INVALID", f"{endpoint.get('endpointKey')} auth policy invalid")
    for key in ("apiSkeletonPhaseAllowed", "crossIndustry"):
        if summary.get(key) is not True:
            raise ReadOnlyApiSkeletonError("REQUIRED_TRUE_INVALID", f"{key} must be true")
    for key in ("productionApiAllowed", "apiEnabled", "frontendEnabled", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "containsCustomerAssetIdentifiers", "airportSpecific"):
        if summary.get(key) is not False:
            raise ReadOnlyApiSkeletonError("REQUIRED_FALSE_INVALID", f"{key} must be false")
    for key in ("databaseWriteCount", "canonicalWriteCount", "decisionWriteCount", "approvalWriteCount", "auditWriteCount"):
        if summary.get(key) != 0:
            raise ReadOnlyApiSkeletonError("WRITE_COUNT_INVALID", f"{key} must be zero")
    if len(skeleton.get("apiReadinessGates", [])) != 14 or any(gate.get("status") != "PASS" for gate in skeleton.get("apiReadinessGates", [])):
        raise ReadOnlyApiSkeletonError("GATES_INVALID", "all fourteen readiness gates must pass")


def validate_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = ("sql" + "alchemy", "fla" + "sk", "fast" + "api", "req" + "uests.", "url" + "lib", "soc" + "ket", "src." + "ufms", "src." + "umms")
    found = [token for token in forbidden if token in lowered]
    if found:
        raise ReadOnlyApiSkeletonError("BOUNDARY_VIOLATION", ", ".join(found))
