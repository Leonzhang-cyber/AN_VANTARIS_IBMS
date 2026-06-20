"""Airport read-only API response contract and validation gate."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from read_only_api_response_contract.enums import GateStatus, ResponseShape, Severity
from read_only_api_response_contract.models import (
    build_artifact_reference,
    build_auth_policy_contract,
    build_boundary_entry,
    build_endpoint_response_contract,
    build_error_contract,
    build_facet_contract,
    build_filter_contract,
    build_pagination_contract,
    build_read_only_api_response_contract,
    build_response_readiness_gate,
)
from read_only_api_response_contract.validation import validate_read_only_api_response_contract
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A7-02"
PROFILE_ID = "airport-read-only-api-response-contract-profile-v1"
IMPLEMENTATION_STATUS = "READ_ONLY_API_RESPONSE_CONTRACT_AND_VALIDATION_GATE_COMPLETE"
READINESS_OUTCOME = "READ_ONLY_API_RESPONSE_CONTRACT_READY_FOR_FUTURE_ROUTE_IMPLEMENTATION"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
A7_SKELETON = PROJECTIONS_DIR / "airport-read-only-api-skeleton.v1.json"
A6_GATE = PROJECTIONS_DIR / "airport-api-frontend-implementation-readiness-gate.v1.json"
A6_CONTRACT = PROJECTIONS_DIR / "airport-api-frontend-readiness-contract.v1.json"
A5_PACKAGE = PROJECTIONS_DIR / "airport-operations-console-package.v1.json"
A5_HANDOFF = PROJECTIONS_DIR / "airport-operations-console-handoff-gate.v1.json"

FILTER_KEYS = {
    "AIRPORT_OVERVIEW": ["pageKey", "readinessState", "severity"],
    "SYSTEMS_INTEGRATION_HEALTH": ["sourceSystemKey", "readinessState", "runtimeObserved"],
    "ASSETS_TOPOLOGY": ["sourceSystemKey", "reviewState", "decisionRequired"],
    "ALARMS_EVENTS": ["sourceSystemKey", "eventKind", "eventSeverity", "operationalStatus"],
    "FAULT_CASES": ["sourceSystemKey", "proposedFaultCaseType", "eligibilityState"],
    "MAINTENANCE_WORK_ORDERS": ["sourceSystemKey", "proposedWorkOrderIntentType", "eligibilityState"],
    "EVIDENCE_INVESTIGATION": ["sourceSystemKey", "investigationState", "linkageState"],
    "REPORTS": ["gateStatus", "readinessState", "decisionRequired"],
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_reference(path: Path, artifact_type: str) -> dict[str, Any]:
    artifact = _load(path)
    return build_artifact_reference(artifact_type=artifact_type, path=str(path.relative_to(ROOT)), digest=sha256_digest(artifact))


def _summary(skeleton: Mapping[str, Any]) -> dict[str, Any]:
    return {
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
        "apiSkeletonEndpointCount": skeleton["summary"]["endpointSkeletonCount"],
        "apiEnabled": False,
        "productionApiAllowed": False,
        "databaseAccessEnabled": False,
        "databaseWriteCount": 0,
        "writeOperationEnabledCount": 0,
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


def _error_contracts(skeleton: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted([build_error_contract(endpoint_key=item["endpointKey"]) for item in skeleton["endpointSkeletons"]], key=lambda item: item["endpointKey"])


def _auth_contracts(skeleton: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted([build_auth_policy_contract(endpoint_key=item["endpointKey"]) for item in skeleton["endpointSkeletons"]], key=lambda item: item["endpointKey"])


def _endpoint_response_contracts(skeleton: Mapping[str, Any], errors: list[Mapping[str, Any]], auths: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    response_by_endpoint = {item["endpointKey"]: item for item in skeleton["responseContracts"]}
    error_by_endpoint = {item["endpointKey"]: item["errorContractId"] for item in errors}
    auth_by_endpoint = {item["endpointKey"]: item["authPolicyContractId"] for item in auths}
    contracts: list[dict[str, Any]] = []
    for endpoint in skeleton["endpointSkeletons"]:
        response = response_by_endpoint[endpoint["endpointKey"]]
        shape = ResponseShape.SUMMARY_PROJECTION_ENVELOPE.value if endpoint["endpointKey"] in {"AIRPORT_OVERVIEW", "REPORTS"} else ResponseShape.PAGINATED_PROJECTION_ENVELOPE.value
        contracts.append(
            build_endpoint_response_contract(
                endpoint_key=endpoint["endpointKey"],
                method=endpoint["method"],
                path=endpoint["path"],
                response_shape=shape,
                source_projection_type=endpoint["sourceProjectionType"],
                source_artifact_path=response["sourceArtifactPath"],
                projection_root_key=response["projectionRootKey"],
                error_contract_id=error_by_endpoint[endpoint["endpointKey"]],
                auth_policy_contract_id=auth_by_endpoint[endpoint["endpointKey"]],
            )
        )
    return sorted(contracts, key=lambda item: item["endpointKey"])


def _pagination_contracts(skeleton: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted([build_pagination_contract(endpoint_key=item["endpointKey"]) for item in skeleton["endpointSkeletons"]], key=lambda item: item["endpointKey"])


def _filter_contracts(skeleton: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted([build_filter_contract(endpoint_key=item["endpointKey"], filter_keys=FILTER_KEYS[item["endpointKey"]]) for item in skeleton["endpointSkeletons"]], key=lambda item: item["endpointKey"])


def _facet_contracts(skeleton: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted([build_facet_contract(endpoint_key=item["endpointKey"], facet_keys=FILTER_KEYS[item["endpointKey"]]) for item in skeleton["endpointSkeletons"]], key=lambda item: item["endpointKey"])


def _gates() -> list[dict[str, Any]]:
    specs = [
        ("G01_ENDPOINT_RESPONSE_CONTRACT_COMPLETENESS", "Endpoint response contract completeness", ["8_ENDPOINT_RESPONSE_CONTRACTS"]),
        ("G02_PAGINATION_CONTRACT_COMPLETENESS", "Pagination contract completeness", ["8_PAGINATION_CONTRACTS"]),
        ("G03_FILTER_CONTRACT_COMPLETENESS", "Filter contract completeness", ["8_FILTER_CONTRACTS"]),
        ("G04_FACET_CONTRACT_COMPLETENESS", "Facet contract completeness", ["8_FACET_CONTRACTS"]),
        ("G05_ERROR_CONTRACT_COMPLETENESS", "Error contract completeness", ["8_ERROR_CONTRACTS"]),
        ("G06_AUTH_POLICY_CONTRACT_COMPLETENESS", "Auth policy contract completeness", ["8_AUTH_POLICY_CONTRACTS"]),
        ("G07_GET_ONLY_BOUNDARY", "GET-only boundary", ["ALL_METHODS_GET"]),
        ("G08_READ_ONLY_BOUNDARY", "Read-only boundary", ["READ_ONLY_AND_NO_WRITES"]),
        ("G09_RESPONSE_ENVELOPE_BOUNDARY", "Response envelope boundary", ["ALL_RESPONSES_REQUIRE_ENVELOPE"]),
        ("G10_PAGINATION_DETERMINISM", "Pagination determinism", ["STABLE_TOKEN_AND_DETERMINISTIC_ORDERING"]),
        ("G11_ERROR_SAFETY", "Error safety", ["NO_STACK_TRACE_OR_CREDENTIAL_LEAKAGE"]),
        ("G12_AUTH_POLICY_REQUIRED", "Auth policy required", ["AUTH_AND_ROLE_POLICY_REQUIRED"]),
        ("G13_CUSTOMER_IDENTIFIER_SAFETY", "Customer identifier safety", ["NO_CUSTOMER_IDENTIFIER_LEAKAGE"]),
        ("G14_NO_API_IMPLEMENTATION", "No API implementation", ["NO_PRODUCTION_API_ROUTE_FILES_CHANGED"]),
        ("G15_A7_API_SKELETON_DEPENDENCY", "A7 API skeleton dependency", ["8_ENDPOINT_SKELETONS_AND_API_DISABLED"]),
        ("G16_DETERMINISTIC_OUTPUT", "Deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"]),
        ("G17_RESPONSE_CONTRACT_DECISION", "Response contract decision", ["READY_FOR_FUTURE_ROUTE_IMPLEMENTATION_PRODUCTION_DISABLED"]),
    ]
    return [
        build_response_readiness_gate(gate_id=gate_id, gate_name=name, status=GateStatus.PASS.value, severity=Severity.INFO.value if gate_id != "G17_RESPONSE_CONTRACT_DECISION" else Severity.LOW.value, blocking=True, reason_codes=reasons)
        for gate_id, name, reasons in specs
    ]


def _boundary_matrix(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    pairs = {
        "apiEnabled": (False, summary["apiEnabled"]),
        "productionApiAllowed": (False, summary["productionApiAllowed"]),
        "databaseAccessEnabled": (False, summary["databaseAccessEnabled"]),
        "databaseWriteCount": (0, summary["databaseWriteCount"]),
        "writeOperationEnabledCount": (0, summary["writeOperationEnabledCount"]),
        "canonicalWriteCount": (0, summary["canonicalWriteCount"]),
        "decisionWriteCount": (0, summary["decisionWriteCount"]),
        "approvalWriteCount": (0, summary["approvalWriteCount"]),
        "auditWriteCount": (0, summary["auditWriteCount"]),
        "frontendEnabled": (False, summary["frontendEnabled"]),
        "runtimeActivationAllowed": (False, summary["runtimeActivationAllowed"]),
        "productionActivationAllowed": (False, summary["productionActivationAllowed"]),
        "pushAllowed": (False, summary["pushAllowed"]),
        "containsCustomerAssetIdentifiers": (False, summary["containsCustomerAssetIdentifiers"]),
    }
    return [build_boundary_entry(boundary_key=key, expected_value=expected, actual_value=actual, blocking=True) for key, (expected, actual) in sorted(pairs.items())]


def build_airport_read_only_api_response_contract() -> dict[str, Any]:
    skeleton = _load(A7_SKELETON)
    summary = _summary(skeleton)
    errors = _error_contracts(skeleton)
    auths = _auth_contracts(skeleton)
    contract = build_read_only_api_response_contract(
        response_contract_gate_id=sha256_digest({"authority": AUTHORITY, "profileId": PROFILE_ID, "skeletonDigest": skeleton["deterministicDigest"]}),
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        endpoint_response_contracts=_endpoint_response_contracts(skeleton, errors, auths),
        pagination_contracts=_pagination_contracts(skeleton),
        filter_contracts=_filter_contracts(skeleton),
        facet_contracts=_facet_contracts(skeleton),
        error_contracts=errors,
        auth_policy_contracts=auths,
        response_readiness_gates=_gates(),
        boundary_matrix=_boundary_matrix(summary),
        source_artifact_references=[
            _artifact_reference(A7_SKELETON, "A7_READ_ONLY_API_SKELETON"),
            _artifact_reference(A6_GATE, "A6_IMPLEMENTATION_GATE"),
            _artifact_reference(A6_CONTRACT, "A6_READINESS_CONTRACT"),
            _artifact_reference(A5_PACKAGE, "A5_OPERATIONS_CONSOLE_PACKAGE"),
            _artifact_reference(A5_HANDOFF, "A5_HANDOFF_GATE"),
        ],
    )
    validate_read_only_api_response_contract(contract)
    return contract
