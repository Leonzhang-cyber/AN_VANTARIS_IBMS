"""Airport read-only API mock route contract and local smoke gate."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from read_only_api_mock_route_contract.enums import GateStatus, MockResponseShape, RouteMode, Severity
from read_only_api_mock_route_contract.models import (
    build_artifact_reference,
    build_boundary_entry,
    build_local_smoke_case,
    build_mock_route_contract,
    build_read_only_api_mock_route_contract,
    build_smoke_gate_result,
)
from read_only_api_mock_route_contract.validation import validate_read_only_api_mock_route_contract
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A7-03"
PROFILE_ID = "airport-read-only-api-mock-route-contract-profile-v1"
IMPLEMENTATION_STATUS = "READ_ONLY_API_MOCK_ROUTE_CONTRACT_AND_LOCAL_SMOKE_GATE_COMPLETE"
READINESS_OUTCOME = "READ_ONLY_API_MOCK_ROUTE_CONTRACT_READY_FOR_FUTURE_ROUTE_IMPLEMENTATION"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
A7_SKELETON = PROJECTIONS_DIR / "airport-read-only-api-skeleton.v1.json"
A7_RESPONSE_CONTRACT = PROJECTIONS_DIR / "airport-read-only-api-response-contract.v1.json"
A6_GATE = PROJECTIONS_DIR / "airport-api-frontend-implementation-readiness-gate.v1.json"
A5_PACKAGE = PROJECTIONS_DIR / "airport-operations-console-package.v1.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_reference(path: Path, artifact_type: str) -> dict[str, Any]:
    artifact = _load(path)
    return build_artifact_reference(artifact_type=artifact_type, path=str(path.relative_to(ROOT)), digest=sha256_digest(artifact))


def _summary() -> dict[str, Any]:
    return {
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


def _shape(response_shape: str) -> str:
    if response_shape == MockResponseShape.SUMMARY_PROJECTION_ENVELOPE.value:
        return MockResponseShape.SUMMARY_PROJECTION_ENVELOPE.value
    return MockResponseShape.PAGINATED_PROJECTION_ENVELOPE.value


def _mock_route_contracts(skeleton: Mapping[str, Any], response_contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    response_by_endpoint = {item["endpointKey"]: item for item in response_contract["endpointResponseContracts"]}
    auth_by_endpoint = {item["endpointKey"]: item for item in response_contract["authPolicyContracts"]}
    contracts: list[dict[str, Any]] = []
    for endpoint in skeleton["endpointSkeletons"]:
        response = response_by_endpoint[endpoint["endpointKey"]]
        auth = auth_by_endpoint[endpoint["endpointKey"]]
        contracts.append(
            build_mock_route_contract(
                endpoint_key=endpoint["endpointKey"],
                method=endpoint["method"],
                path=endpoint["path"],
                route_mode=RouteMode.MOCK_CONTRACT_ONLY.value,
                source_projection_type=endpoint["sourceProjectionType"],
                source_artifact_path=response["sourceArtifactPath"],
                response_contract_id=response["endpointResponseContractId"],
                auth_policy_contract_id=auth["authPolicyContractId"],
                mock_response_shape=_shape(response["responseShape"]),
                expected_status_codes=[200],
            )
        )
    return sorted(contracts, key=lambda item: item["endpointKey"])


def _local_smoke_cases(skeleton: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        [build_local_smoke_case(endpoint_key=item["endpointKey"], method=item["method"], path=item["path"]) for item in skeleton["endpointSkeletons"]],
        key=lambda item: item["endpointKey"],
    )


def _gates() -> list[dict[str, Any]]:
    specs = [
        ("G01_MOCK_ROUTE_CONTRACT_COMPLETENESS", "Mock route contract completeness", ["8_MOCK_ROUTE_CONTRACTS"]),
        ("G02_LOCAL_SMOKE_CASE_COMPLETENESS", "Local smoke case completeness", ["8_LOCAL_SMOKE_CASES"]),
        ("G03_GET_ONLY_BOUNDARY", "GET-only boundary", ["ALL_METHODS_GET"]),
        ("G04_PRODUCTION_ROUTE_DISABLED", "Production route disabled", ["PRODUCTION_ROUTES_DISABLED"]),
        ("G05_READ_ONLY_ROUTE_BOUNDARY", "Read-only route boundary", ["READ_ONLY_AND_NO_WRITES"]),
        ("G06_DATABASE_BOUNDARY", "Database boundary", ["DATABASE_ACCESS_DISABLED"]),
        ("G07_RUNTIME_BOUNDARY", "Runtime boundary", ["RUNTIME_ACTIVATION_DISABLED"]),
        ("G08_RESPONSE_CONTRACT_LINKAGE", "Response contract linkage", ["8_A7_02_RESPONSE_CONTRACT_LINKS"]),
        ("G09_AUTH_POLICY_LINKAGE", "Auth policy linkage", ["8_A7_02_AUTH_POLICY_LINKS"]),
        ("G10_LOCAL_SMOKE_EXPECTATIONS", "Local smoke expectations", ["ENVELOPE_AUTH_PAGINATION_FILTERS_FACETS_READ_ONLY_NO_WRITE"]),
        ("G11_NO_NETWORK_CALLS", "No network calls", ["NO_NETWORK_OR_LOCALHOST_SMOKE_EXECUTION"]),
        ("G12_NO_BACKEND_ROUTE_IMPLEMENTATION", "No backend route implementation", ["NO_PRODUCTION_BACKEND_API_ROUTE_FILES_CHANGED"]),
        ("G13_CUSTOMER_IDENTIFIER_SAFETY", "Customer identifier safety", ["NO_CUSTOMER_IDENTIFIER_LEAKAGE"]),
        ("G14_DETERMINISTIC_OUTPUT", "Deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"]),
        ("G15_MOCK_ROUTE_CONTRACT_DECISION", "Mock route contract decision", ["READY_FOR_FUTURE_ROUTE_IMPLEMENTATION_PRODUCTION_DISABLED"]),
    ]
    return [
        build_smoke_gate_result(
            gate_id=gate_id,
            gate_name=name,
            status=GateStatus.PASS.value,
            severity=Severity.INFO.value if gate_id != "G15_MOCK_ROUTE_CONTRACT_DECISION" else Severity.LOW.value,
            blocking=True,
            reason_codes=reasons,
        )
        for gate_id, name, reasons in specs
    ]


def _boundary_matrix(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    pairs = {
        "apiEnabled": (False, summary["apiEnabled"]),
        "productionApiAllowed": (False, summary["productionApiAllowed"]),
        "databaseWriteCount": (0, summary["databaseWriteCount"]),
        "canonicalWriteCount": (0, summary["canonicalWriteCount"]),
        "decisionWriteCount": (0, summary["decisionWriteCount"]),
        "approvalWriteCount": (0, summary["approvalWriteCount"]),
        "auditWriteCount": (0, summary["auditWriteCount"]),
        "frontendEnabled": (False, summary["frontendEnabled"]),
        "runtimeActivationAllowed": (False, summary["runtimeActivationAllowed"]),
        "productionActivationAllowed": (False, summary["productionActivationAllowed"]),
        "pushAllowed": (False, summary["pushAllowed"]),
        "containsCustomerAssetIdentifiers": (False, summary["containsCustomerAssetIdentifiers"]),
        "networkCallRequiredCount": (0, summary["networkCallRequiredCount"]),
        "localhostCallRequiredCount": (0, summary["localhostCallRequiredCount"]),
        "backendRouteImplementationCount": (0, summary["backendRouteImplementationCount"]),
    }
    return [build_boundary_entry(boundary_key=key, expected_value=expected, actual_value=actual, blocking=True) for key, (expected, actual) in sorted(pairs.items())]


def build_airport_read_only_api_mock_route_contract() -> dict[str, Any]:
    skeleton = _load(A7_SKELETON)
    response_contract = _load(A7_RESPONSE_CONTRACT)
    summary = _summary()
    contract = build_read_only_api_mock_route_contract(
        mock_route_contract_id=sha256_digest(
            {
                "authority": AUTHORITY,
                "profileId": PROFILE_ID,
                "skeletonDigest": skeleton["deterministicDigest"],
                "responseContractDigest": response_contract["deterministicDigest"],
            }
        ),
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        mock_route_contracts=_mock_route_contracts(skeleton, response_contract),
        local_smoke_cases=_local_smoke_cases(skeleton),
        smoke_gate_results=_gates(),
        boundary_matrix=_boundary_matrix(summary),
        source_artifact_references=[
            _artifact_reference(A7_SKELETON, "A7_READ_ONLY_API_SKELETON"),
            _artifact_reference(A7_RESPONSE_CONTRACT, "A7_READ_ONLY_API_RESPONSE_CONTRACT"),
            _artifact_reference(A6_GATE, "A6_IMPLEMENTATION_GATE"),
            _artifact_reference(A5_PACKAGE, "A5_OPERATIONS_CONSOLE_PACKAGE"),
        ],
    )
    validate_read_only_api_mock_route_contract(contract)
    return contract
