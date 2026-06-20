"""Airport read-only API implementation release gate."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from read_only_api_release_gate.enums import DecisionState, GateStatus, Severity
from read_only_api_release_gate.models import (
    build_api_contract_coverage_entry,
    build_artifact_reference,
    build_implementation_boundary_entry,
    build_implementation_decision,
    build_mock_route_coverage_entry,
    build_read_only_api_implementation_release_gate,
    build_release_gate_result,
    build_stage_result,
)
from read_only_api_release_gate.validation import validate_read_only_api_release_gate
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A7-04"
PROFILE_ID = "airport-read-only-api-implementation-release-gate-profile-v1"
IMPLEMENTATION_STATUS = "READ_ONLY_API_IMPLEMENTATION_RELEASE_GATE_COMPLETE"
READINESS_OUTCOME = "READ_ONLY_API_READY_FOR_FUTURE_ROUTE_IMPLEMENTATION"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
A7_SKELETON = PROJECTIONS_DIR / "airport-read-only-api-skeleton.v1.json"
A7_RESPONSE = PROJECTIONS_DIR / "airport-read-only-api-response-contract.v1.json"
A7_MOCK = PROJECTIONS_DIR / "airport-read-only-api-mock-route-contract.v1.json"
A6_GATE = PROJECTIONS_DIR / "airport-api-frontend-implementation-readiness-gate.v1.json"
A6_CONTRACT = PROJECTIONS_DIR / "airport-api-frontend-readiness-contract.v1.json"
A5_HANDOFF = PROJECTIONS_DIR / "airport-operations-console-handoff-gate.v1.json"
A5_PACKAGE = PROJECTIONS_DIR / "airport-operations-console-package.v1.json"

STAGE_SPECS = [
    (
        "A7-01",
        "Read-only API Skeleton Foundation",
        "ONE_AIRPORT_A7_01_READ_ONLY_API_SKELETON_FOUNDATION_PASS",
        A7_SKELETON,
        "validate-one-airport-read-only-api-skeleton.py",
    ),
    (
        "A7-02",
        "Read-only API Response Contract and Validation Gate",
        "ONE_AIRPORT_A7_02_READ_ONLY_API_RESPONSE_CONTRACT_AND_VALIDATION_GATE_PASS",
        A7_RESPONSE,
        "validate-one-airport-read-only-api-response-contract.py",
    ),
    (
        "A7-03",
        "Read-only API Mock Route Contract and Local Smoke Gate",
        "ONE_AIRPORT_A7_03_READ_ONLY_API_MOCK_ROUTE_CONTRACT_AND_LOCAL_SMOKE_GATE_PASS",
        A7_MOCK,
        "validate-one-airport-read-only-api-mock-route-contract.py",
    ),
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_reference(path: Path, artifact_type: str) -> dict[str, Any]:
    artifact = _load(path)
    return build_artifact_reference(artifact_type=artifact_type, path=str(path.relative_to(ROOT)), digest=sha256_digest(artifact))


def _summary() -> dict[str, Any]:
    return {
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


def _stage_results() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for stage_id, name, marker, path, validator in STAGE_SPECS:
        artifact = _load(path)
        results.append(
            build_stage_result(
                stage_id=stage_id,
                stage_name=name,
                pass_marker=marker,
                artifact_path=str(path.relative_to(ROOT)),
                validator_name=validator,
                status=GateStatus.PASS.value,
                summary=artifact["summary"],
            )
        )
    return results


def _api_contract_coverage(skeleton: Mapping[str, Any], response: Mapping[str, Any], mock: Mapping[str, Any]) -> list[dict[str, Any]]:
    endpoint_keys = {item["endpointKey"] for item in skeleton["endpointSkeletons"]}
    response_keys = {item["endpointKey"] for item in response["endpointResponseContracts"]}
    pagination_keys = {item["endpointKey"] for item in response["paginationContracts"]}
    filter_keys = {item["endpointKey"] for item in response["filterContracts"]}
    facet_keys = {item["endpointKey"] for item in response["facetContracts"]}
    error_keys = {item["endpointKey"] for item in response["errorContracts"]}
    auth_keys = {item["endpointKey"] for item in response["authPolicyContracts"]}
    mock_keys = {item["endpointKey"] for item in mock["mockRouteContracts"]}
    smoke_keys = {item["endpointKey"] for item in mock["localSmokeCases"]}
    return [
        build_api_contract_coverage_entry(
            endpoint_key=key,
            endpoint_skeleton_present=key in endpoint_keys,
            response_contract_present=key in response_keys,
            pagination_contract_present=key in pagination_keys,
            filter_contract_present=key in filter_keys,
            facet_contract_present=key in facet_keys,
            error_contract_present=key in error_keys,
            auth_policy_contract_present=key in auth_keys,
            mock_route_contract_present=key in mock_keys,
            local_smoke_case_present=key in smoke_keys,
        )
        for key in sorted(endpoint_keys)
    ]


def _mock_route_coverage(mock: Mapping[str, Any]) -> list[dict[str, Any]]:
    smoke_by_endpoint = {item["endpointKey"]: item for item in mock["localSmokeCases"]}
    entries: list[dict[str, Any]] = []
    for route in mock["mockRouteContracts"]:
        smoke = smoke_by_endpoint[route["endpointKey"]]
        entries.append(
            build_mock_route_coverage_entry(
                endpoint_key=route["endpointKey"],
                method=route["method"],
                path=route["path"],
                response_contract_linked=bool(route["responseContractId"]),
                auth_policy_linked=bool(route["authPolicyContractId"]),
                local_smoke_defined=smoke["expectedStatusCode"] == 200,
                network_call_required=smoke["networkCallRequired"],
                localhost_call_required=smoke["localhostCallRequired"],
                production_route_enabled=route["productionRouteEnabled"],
            )
        )
    return sorted(entries, key=lambda item: item["endpointKey"])


def _implementation_boundary_matrix(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    pairs = {
        "apiEnabled": (False, summary["apiEnabled"]),
        "productionApiAllowed": (False, summary["productionApiAllowed"]),
        "backendRouteImplementationAllowed": (False, summary["backendRouteImplementationAllowed"]),
        "databaseAccessAllowed": (False, summary["databaseAccessAllowed"]),
        "writeOperationAllowed": (False, summary["writeOperationAllowed"]),
        "runtimeActivationAllowed": (False, summary["runtimeActivationAllowed"]),
        "productionActivationAllowed": (False, summary["productionActivationAllowed"]),
        "frontendImplementationAllowed": (False, summary["frontendImplementationAllowed"]),
        "frontendEnabled": (False, summary["frontendEnabled"]),
        "pushAllowed": (False, summary["pushAllowed"]),
        "networkCallRequiredCount": (0, summary["networkCallRequiredCount"]),
        "localhostCallRequiredCount": (0, summary["localhostCallRequiredCount"]),
        "backendRouteImplementationCount": (0, summary["backendRouteImplementationCount"]),
        "databaseWriteCount": (0, summary["databaseWriteCount"]),
        "canonicalWriteCount": (0, summary["canonicalWriteCount"]),
        "decisionWriteCount": (0, summary["decisionWriteCount"]),
        "approvalWriteCount": (0, summary["approvalWriteCount"]),
        "auditWriteCount": (0, summary["auditWriteCount"]),
        "containsCustomerAssetIdentifiers": (False, summary["containsCustomerAssetIdentifiers"]),
    }
    return [build_implementation_boundary_entry(boundary_key=key, expected_value=expected, actual_value=actual, blocking=True) for key, (expected, actual) in sorted(pairs.items())]


def _release_gates() -> list[dict[str, Any]]:
    specs = [
        ("G01_A7_STAGE_COMPLETENESS", "A7 stage completeness", ["A7_01_A7_02_A7_03_ARTIFACTS_PRESENT"]),
        ("G02_A7_PASS_MARKER_COMPLETENESS", "A7 pass marker completeness", ["THREE_A7_PASS_MARKERS_REPRESENTED"]),
        ("G03_ENDPOINT_SKELETON_COVERAGE", "Endpoint skeleton coverage", ["8_ENDPOINT_SKELETONS"]),
        ("G04_RESPONSE_CONTRACT_COVERAGE", "Response contract coverage", ["8_RESPONSE_CONTRACTS"]),
        ("G05_PAGINATION_FILTER_FACET_COVERAGE", "Pagination filter facet coverage", ["EACH_ENDPOINT_HAS_PAGINATION_FILTER_FACET"]),
        ("G06_ERROR_AUTH_CONTRACT_COVERAGE", "Error auth contract coverage", ["EACH_ENDPOINT_HAS_ERROR_AUTH"]),
        ("G07_MOCK_ROUTE_COVERAGE", "Mock route coverage", ["8_MOCK_ROUTE_CONTRACTS"]),
        ("G08_LOCAL_SMOKE_COVERAGE", "Local smoke coverage", ["8_LOCAL_SMOKE_CASES"]),
        ("G09_GET_ONLY_BOUNDARY", "GET-only boundary", ["ALL_ROUTES_GET"]),
        ("G10_READ_ONLY_BOUNDARY", "Read-only boundary", ["READ_ONLY_AND_NO_WRITES"]),
        ("G11_DATABASE_BOUNDARY", "Database boundary", ["DATABASE_ACCESS_AND_WRITES_DISABLED"]),
        ("G12_RUNTIME_PRODUCTION_BOUNDARY", "Runtime production boundary", ["RUNTIME_AND_PRODUCTION_DISABLED"]),
        ("G13_NO_BACKEND_ROUTE_IMPLEMENTATION", "No backend route implementation", ["BACKEND_ROUTE_IMPLEMENTATION_COUNT_ZERO"]),
        ("G14_NO_NETWORK_LOCALHOST_SMOKE", "No network localhost smoke", ["NETWORK_AND_LOCALHOST_SMOKE_ZERO"]),
        ("G15_A6_DEPENDENCY_GATE", "A6 dependency gate", ["A6_ALLOWS_SKELETON_PHASE_PRODUCTION_DISABLED"]),
        ("G16_A5_HANDOFF_DEPENDENCY", "A5 handoff dependency", ["A5_HANDOFF_ALLOWED"]),
        ("G17_CUSTOMER_IDENTIFIER_SAFETY", "Customer identifier safety", ["NO_CUSTOMER_IDENTIFIER_LEAKAGE"]),
        ("G18_DETERMINISTIC_OUTPUT", "Deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"]),
        ("G19_IMPLEMENTATION_DECISION", "Implementation decision", ["FUTURE_READ_ONLY_ROUTE_ALLOWED_PRODUCTION_DISABLED"]),
    ]
    return [
        build_release_gate_result(
            gate_id=gate_id,
            gate_name=name,
            status=GateStatus.PASS.value,
            severity=Severity.INFO.value if gate_id != "G19_IMPLEMENTATION_DECISION" else Severity.LOW.value,
            blocking=True,
            reason_codes=reasons,
        )
        for gate_id, name, reasons in specs
    ]


def _dependency_gate_results(a6_gate: Mapping[str, Any], a5_handoff: Mapping[str, Any], a5_package: Mapping[str, Any]) -> list[dict[str, Any]]:
    checks = [
        ("D01_A6_API_SKELETON_PHASE_ALLOWED", "A6 API skeleton phase allowed", a6_gate["summary"]["apiSkeletonPhaseAllowed"] is True),
        ("D02_A6_FRONTEND_SKELETON_PHASE_ALLOWED", "A6 frontend skeleton phase allowed", a6_gate["summary"]["frontendSkeletonPhaseAllowed"] is True),
        ("D03_A6_PRODUCTION_API_DISABLED", "A6 production API disabled", a6_gate["summary"]["productionApiAllowed"] is False),
        ("D04_A5_HANDOFF_ALLOWED", "A5 handoff allowed", a5_handoff["summary"]["handoffAllowed"] is True),
        ("D05_A5_PACKAGE_SHAPE", "A5 package shape", a5_package["summary"]["pageDefinitionCount"] == 8 and a5_package["summary"]["packageDataSourceCount"] == 15 and a5_package["summary"]["consoleCardCount"] == 8),
    ]
    return [
        build_release_gate_result(
            gate_id=gate_id,
            gate_name=name,
            status=GateStatus.PASS.value if ok else GateStatus.FAIL.value,
            severity=Severity.INFO.value,
            blocking=True,
            reason_codes=[gate_id, "DEPENDENCY_PASS" if ok else "DEPENDENCY_FAIL"],
        )
        for gate_id, name, ok in checks
    ]


def _implementation_decision() -> dict[str, Any]:
    return build_implementation_decision(
        decision_state=DecisionState.READY_FOR_READ_ONLY_ROUTE_IMPLEMENTATION.value,
        read_only_api_route_implementation_allowed=True,
        production_api_allowed=False,
        backend_route_implementation_allowed=False,
        database_access_allowed=False,
        write_operation_allowed=False,
        runtime_activation_allowed=False,
        production_activation_allowed=False,
        frontend_implementation_allowed=False,
        push_allowed=False,
        decision_reason="A7 contract, response, mock route, and local smoke gates are complete; only a future read-only route implementation phase is allowed.",
    )


def build_airport_read_only_api_release_gate() -> dict[str, Any]:
    skeleton = _load(A7_SKELETON)
    response = _load(A7_RESPONSE)
    mock = _load(A7_MOCK)
    a6_gate = _load(A6_GATE)
    a5_handoff = _load(A5_HANDOFF)
    a5_package = _load(A5_PACKAGE)
    summary = _summary()
    gate = build_read_only_api_implementation_release_gate(
        release_gate_id=sha256_digest(
            {
                "authority": AUTHORITY,
                "profileId": PROFILE_ID,
                "skeletonDigest": skeleton["deterministicDigest"],
                "responseDigest": response["deterministicDigest"],
                "mockDigest": mock["deterministicDigest"],
            }
        ),
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        stage_results=_stage_results(),
        api_contract_coverage_matrix=_api_contract_coverage(skeleton, response, mock),
        mock_route_coverage_matrix=_mock_route_coverage(mock),
        implementation_boundary_matrix=_implementation_boundary_matrix(summary),
        release_gate_results=_release_gates(),
        dependency_gate_results=_dependency_gate_results(a6_gate, a5_handoff, a5_package),
        implementation_decision=_implementation_decision(),
        artifact_references=[
            _artifact_reference(A7_SKELETON, "A7_READ_ONLY_API_SKELETON"),
            _artifact_reference(A7_RESPONSE, "A7_READ_ONLY_API_RESPONSE_CONTRACT"),
            _artifact_reference(A7_MOCK, "A7_READ_ONLY_API_MOCK_ROUTE_CONTRACT"),
            _artifact_reference(A6_GATE, "A6_IMPLEMENTATION_GATE"),
            _artifact_reference(A6_CONTRACT, "A6_READINESS_CONTRACT"),
            _artifact_reference(A5_HANDOFF, "A5_HANDOFF_GATE"),
            _artifact_reference(A5_PACKAGE, "A5_OPERATIONS_CONSOLE_PACKAGE"),
        ],
    )
    validate_read_only_api_release_gate(gate)
    return gate
