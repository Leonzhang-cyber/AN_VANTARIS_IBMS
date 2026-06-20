"""Validation helpers for read-only API response contracts."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import ReadOnlyApiResponseContractError


def validate_read_only_api_response_contract(contract: Mapping[str, Any]) -> None:
    summary = contract.get("summary", {})
    expected = {
        "endpointResponseContractCount": 8,
        "paginationContractCount": 8,
        "filterContractCount": 8,
        "facetContractCount": 8,
        "errorContractCount": 8,
        "authPolicyContractCount": 8,
        "readinessGateCount": 17,
        "passedGateCount": 17,
        "blockingGateFailureCount": 0,
        "getEndpointCount": 8,
        "readOnlyEndpointCount": 8,
        "envelopeRequiredCount": 8,
        "paginationSupportedCount": 8,
        "filtersSupportedCount": 8,
        "facetsSupportedCount": 8,
        "stableContinuationTokenRequiredCount": 8,
        "deterministicOrderingRequiredCount": 8,
        "authRequiredCount": 8,
        "rolePolicyRequiredCount": 8,
        "anonymousAccessAllowedCount": 0,
        "noStackTraceLeakageCount": 8,
        "noCredentialLeakageCount": 8,
        "apiSkeletonEndpointCount": 8,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise ReadOnlyApiResponseContractError("SUMMARY_INVALID", f"{key} must be {value}")
    for key in ("apiEnabled", "productionApiAllowed", "databaseAccessEnabled", "frontendEnabled", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "containsCustomerAssetIdentifiers", "airportSpecific"):
        if summary.get(key) is not False:
            raise ReadOnlyApiResponseContractError("BOUNDARY_FLAG_INVALID", f"{key} must be false")
    for key in ("databaseWriteCount", "writeOperationEnabledCount", "canonicalWriteCount", "decisionWriteCount", "approvalWriteCount", "auditWriteCount"):
        if summary.get(key) != 0:
            raise ReadOnlyApiResponseContractError("WRITE_COUNT_INVALID", f"{key} must be zero")
    if summary.get("crossIndustry") is not True:
        raise ReadOnlyApiResponseContractError("CROSS_INDUSTRY_INVALID", "contract must remain cross-industry")
    if any(gate.get("status") != "PASS" for gate in contract.get("responseReadinessGates", [])):
        raise ReadOnlyApiResponseContractError("GATE_INVALID", "all response readiness gates must pass")


def validate_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = ("sql" + "alchemy", "fla" + "sk", "fast" + "api", "req" + "uests.", "url" + "lib", "soc" + "ket", "src." + "ufms", "src." + "umms")
    found = [token for token in forbidden if token in lowered]
    if found:
        raise ReadOnlyApiResponseContractError("BOUNDARY_VIOLATION", ", ".join(found))
