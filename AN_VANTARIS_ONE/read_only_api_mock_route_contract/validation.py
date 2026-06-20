"""Validation helpers for read-only API mock route contracts."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import ReadOnlyApiMockRouteContractError


EXPECTED_SUMMARY = {
    "mockRouteContractCount": 8,
    "localSmokeCaseCount": 8,
    "smokeGateCount": 15,
    "passedSmokeGateCount": 15,
    "blockingGateFailureCount": 0,
    "getRouteCount": 8,
    "readOnlyRouteCount": 8,
    "productionRouteEnabledCount": 0,
    "databaseAccessEnabledRouteCount": 0,
    "writeOperationEnabledRouteCount": 0,
    "runtimeActivationEnabledRouteCount": 0,
    "responseContractLinkedCount": 8,
    "authPolicyLinkedCount": 8,
    "expectedStatus200Count": 8,
    "expectedEnvelopeRequiredCount": 8,
    "expectedAuthRequiredCount": 8,
    "expectedPaginationSupportedCount": 8,
    "expectedFiltersSupportedCount": 8,
    "expectedFacetsSupportedCount": 8,
    "expectedNoWriteCount": 8,
    "networkCallRequiredCount": 0,
    "localhostCallRequiredCount": 0,
    "backendRouteImplementationCount": 0,
    "apiEnabled": False,
    "productionApiAllowed": False,
    "databaseWriteCount": 0,
    "canonicalWriteCount": 0,
    "decisionWriteCount": 0,
    "approvalWriteCount": 0,
    "auditWriteCount": 0,
    "frontendEnabled": False,
    "runtimeActivationAllowed": False,
    "productionActivationAllowed": False,
    "pushAllowed": False,
    "containsCustomerAssetIdentifiers": False,
    "crossIndustry": True,
    "airportSpecific": False,
}


def validate_read_only_api_mock_route_contract(contract: Mapping[str, Any]) -> None:
    summary = contract.get("summary", {})
    for key, value in EXPECTED_SUMMARY.items():
        if summary.get(key) != value:
            raise ReadOnlyApiMockRouteContractError("SUMMARY_INVALID", f"{key} must be {value}")
    if len(contract.get("mockRouteContracts", [])) != 8:
        raise ReadOnlyApiMockRouteContractError("MOCK_ROUTE_COUNT_INVALID", "exactly 8 mock route contracts are required")
    if len(contract.get("localSmokeCases", [])) != 8:
        raise ReadOnlyApiMockRouteContractError("SMOKE_CASE_COUNT_INVALID", "exactly 8 local smoke cases are required")
    if len(contract.get("smokeGateResults", [])) != 15:
        raise ReadOnlyApiMockRouteContractError("GATE_COUNT_INVALID", "exactly 15 smoke gates are required")
    if any(gate.get("status") != "PASS" for gate in contract.get("smokeGateResults", [])):
        raise ReadOnlyApiMockRouteContractError("GATE_INVALID", "all smoke gates must pass")
    for route in contract.get("mockRouteContracts", []):
        if route.get("method") != "GET" or route.get("readOnly") is not True:
            raise ReadOnlyApiMockRouteContractError("ROUTE_BOUNDARY_INVALID", "all mock routes must be GET read-only routes")
        for key in ("productionRouteEnabled", "databaseAccessEnabled", "writeOperationEnabled", "runtimeActivationEnabled"):
            if route.get(key) is not False:
                raise ReadOnlyApiMockRouteContractError("ROUTE_ACTIVATION_INVALID", f"{key} must be false")
    for case in contract.get("localSmokeCases", []):
        if case.get("networkCallRequired") is not False or case.get("localhostCallRequired") is not False:
            raise ReadOnlyApiMockRouteContractError("SMOKE_BOUNDARY_INVALID", "local smoke cases must not require network or localhost calls")


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
        raise ReadOnlyApiMockRouteContractError("BOUNDARY_VIOLATION", ", ".join(found))
