"""Validation helpers for API / Frontend readiness contracts."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import ApiFrontendReadinessContractError


def validate_api_frontend_readiness_contract(contract: Mapping[str, Any]) -> None:
    summary = contract.get("summary", {})
    expected_counts = {
        "apiEndpointCandidates": ("apiEndpointCandidateCount", 8),
        "frontendPageCandidates": ("frontendPageCandidateCount", 8),
        "frontendRouteCandidates": ("frontendRouteCandidateCount", 8),
        "dataBindingContracts": ("dataBindingContractCount", 15),
        "cardBindingContracts": ("cardBindingContractCount", 8),
        "queueBindingContracts": ("queueBindingContractCount", 8),
        "readinessGates": ("readinessGateCount", 15),
    }
    for collection, (summary_key, expected) in expected_counts.items():
        if len(contract.get(collection, [])) != expected or summary.get(summary_key) != expected:
            raise ApiFrontendReadinessContractError("COUNT_INVALID", f"{summary_key} must be {expected}")
    if summary.get("passedGateCount") != 15 or summary.get("blockingGateFailureCount") != 0:
        raise ApiFrontendReadinessContractError("GATE_SUMMARY_INVALID", "all readiness gates must pass")
    for endpoint in contract.get("apiEndpointCandidates", []):
        for key, expected in (("readOnly", True), ("implementationAllowed", False), ("publicApiEnabled", False), ("databaseAccessAllowed", False), ("writeOperationAllowed", False), ("authPolicyRequired", True)):
            if endpoint.get(key) is not expected:
                raise ApiFrontendReadinessContractError("ENDPOINT_BOUNDARY_INVALID", f"{endpoint.get('endpointKey')} {key} invalid")
    for page in contract.get("frontendPageCandidates", []):
        for key in ("implementationAllowed", "routeImplementationAllowed", "runtimeDataMutationAllowed"):
            if page.get(key) is not False:
                raise ApiFrontendReadinessContractError("PAGE_BOUNDARY_INVALID", f"{page.get('pageKey')} {key} invalid")
    for route in contract.get("frontendRouteCandidates", []):
        for key in ("implementationAllowed", "runtimeDataMutationAllowed"):
            if route.get(key) is not False:
                raise ApiFrontendReadinessContractError("ROUTE_BOUNDARY_INVALID", f"{route.get('routeKey')} {key} invalid")
    for key in ("databaseWriteCount", "canonicalWriteCount", "decisionWriteCount", "approvalWriteCount", "auditWriteCount"):
        if summary.get(key) != 0:
            raise ApiFrontendReadinessContractError("WRITE_COUNT_INVALID", f"{key} must be zero")
    for key in ("apiEnabled", "frontendEnabled", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "containsCustomerAssetIdentifiers", "airportSpecific"):
        if summary.get(key) is not False:
            raise ApiFrontendReadinessContractError("BOUNDARY_FLAG_INVALID", f"{key} must be false")
    if summary.get("crossIndustry") is not True:
        raise ApiFrontendReadinessContractError("CROSS_INDUSTRY_INVALID", "contract must remain cross-industry")


def validate_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = ("sql" + "alchemy", "fla" + "sk", "req" + "uests.", "url" + "lib", "soc" + "ket", "blue" + "print", "api." + "route", "src." + "ufms", "src." + "umms")
    found = [token for token in forbidden if token in lowered]
    if found:
        raise ApiFrontendReadinessContractError("BOUNDARY_VIOLATION", ", ".join(found))
