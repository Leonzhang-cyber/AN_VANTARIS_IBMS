"""Deterministic model builders for read-only API implementation release gates."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def build_stage_result(*, stage_id: str, stage_name: str, pass_marker: str, artifact_path: str, validator_name: str, status: str, summary: Mapping[str, Any]) -> dict[str, Any]:
    item = {
        "stageId": stage_id,
        "stageName": stage_name,
        "passMarker": pass_marker,
        "artifactPath": artifact_path,
        "validatorName": validator_name,
        "status": status,
        "summary": dict(summary),
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_api_contract_coverage_entry(
    *,
    endpoint_key: str,
    endpoint_skeleton_present: bool,
    response_contract_present: bool,
    pagination_contract_present: bool,
    filter_contract_present: bool,
    facet_contract_present: bool,
    error_contract_present: bool,
    auth_policy_contract_present: bool,
    mock_route_contract_present: bool,
    local_smoke_case_present: bool,
) -> dict[str, Any]:
    status = "PASS" if all(
        [
            endpoint_skeleton_present,
            response_contract_present,
            pagination_contract_present,
            filter_contract_present,
            facet_contract_present,
            error_contract_present,
            auth_policy_contract_present,
            mock_route_contract_present,
            local_smoke_case_present,
        ]
    ) else "FAIL"
    item = {
        "coverageId": sha256_digest({"endpointKey": endpoint_key, "coverage": "API_CONTRACT"}),
        "endpointKey": endpoint_key,
        "endpointSkeletonPresent": bool(endpoint_skeleton_present),
        "responseContractPresent": bool(response_contract_present),
        "paginationContractPresent": bool(pagination_contract_present),
        "filterContractPresent": bool(filter_contract_present),
        "facetContractPresent": bool(facet_contract_present),
        "errorContractPresent": bool(error_contract_present),
        "authPolicyContractPresent": bool(auth_policy_contract_present),
        "mockRouteContractPresent": bool(mock_route_contract_present),
        "localSmokeCasePresent": bool(local_smoke_case_present),
        "status": status,
        "blocking": True,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_mock_route_coverage_entry(
    *,
    endpoint_key: str,
    method: str,
    path: str,
    response_contract_linked: bool,
    auth_policy_linked: bool,
    local_smoke_defined: bool,
    network_call_required: bool,
    localhost_call_required: bool,
    production_route_enabled: bool,
) -> dict[str, Any]:
    status = "PASS" if response_contract_linked and auth_policy_linked and local_smoke_defined and not network_call_required and not localhost_call_required and not production_route_enabled else "FAIL"
    item = {
        "coverageId": sha256_digest({"endpointKey": endpoint_key, "coverage": "MOCK_ROUTE"}),
        "endpointKey": endpoint_key,
        "method": method,
        "path": path,
        "responseContractLinked": bool(response_contract_linked),
        "authPolicyLinked": bool(auth_policy_linked),
        "localSmokeDefined": bool(local_smoke_defined),
        "networkCallRequired": bool(network_call_required),
        "localhostCallRequired": bool(localhost_call_required),
        "productionRouteEnabled": bool(production_route_enabled),
        "status": status,
        "blocking": True,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_implementation_boundary_entry(*, boundary_key: str, expected_value: Any, actual_value: Any, blocking: bool) -> dict[str, Any]:
    item = {
        "boundaryId": sha256_digest({"boundaryKey": boundary_key}),
        "boundaryKey": boundary_key,
        "expectedValue": expected_value,
        "actualValue": actual_value,
        "status": "PASS" if expected_value == actual_value else "FAIL",
        "blocking": bool(blocking),
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_release_gate_result(*, gate_id: str, gate_name: str, status: str, severity: str, blocking: bool, reason_codes: Sequence[str]) -> dict[str, Any]:
    item = {
        "gateId": gate_id,
        "gateName": gate_name,
        "status": status,
        "severity": severity,
        "blocking": bool(blocking),
        "reasonCodes": sorted(str(code) for code in reason_codes),
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_implementation_decision(
    *,
    decision_state: str,
    read_only_api_route_implementation_allowed: bool,
    production_api_allowed: bool,
    backend_route_implementation_allowed: bool,
    database_access_allowed: bool,
    write_operation_allowed: bool,
    runtime_activation_allowed: bool,
    production_activation_allowed: bool,
    frontend_implementation_allowed: bool,
    push_allowed: bool,
    decision_reason: str,
) -> dict[str, Any]:
    item = {
        "decisionState": decision_state,
        "readOnlyApiRouteImplementationAllowed": bool(read_only_api_route_implementation_allowed),
        "productionApiAllowed": bool(production_api_allowed),
        "backendRouteImplementationAllowed": bool(backend_route_implementation_allowed),
        "databaseAccessAllowed": bool(database_access_allowed),
        "writeOperationAllowed": bool(write_operation_allowed),
        "runtimeActivationAllowed": bool(runtime_activation_allowed),
        "productionActivationAllowed": bool(production_activation_allowed),
        "frontendImplementationAllowed": bool(frontend_implementation_allowed),
        "pushAllowed": bool(push_allowed),
        "decisionReason": decision_reason,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    item = {"artifactType": artifact_type, "path": path, "digest": digest}
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_read_only_api_implementation_release_gate(
    *,
    release_gate_id: str,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    stage_results: Sequence[Mapping[str, Any]],
    api_contract_coverage_matrix: Sequence[Mapping[str, Any]],
    mock_route_coverage_matrix: Sequence[Mapping[str, Any]],
    implementation_boundary_matrix: Sequence[Mapping[str, Any]],
    release_gate_results: Sequence[Mapping[str, Any]],
    dependency_gate_results: Sequence[Mapping[str, Any]],
    implementation_decision: Mapping[str, Any],
    artifact_references: Sequence[Mapping[str, Any]],
    generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
) -> dict[str, Any]:
    gate = {
        "releaseGateId": release_gate_id,
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "stageResults": list(stage_results),
        "apiContractCoverageMatrix": list(api_contract_coverage_matrix),
        "mockRouteCoverageMatrix": list(mock_route_coverage_matrix),
        "implementationBoundaryMatrix": list(implementation_boundary_matrix),
        "releaseGateResults": list(release_gate_results),
        "dependencyGateResults": list(dependency_gate_results),
        "implementationDecision": dict(implementation_decision),
        "artifactReferences": list(artifact_references),
        "generatedAtPolicy": generated_at_policy,
    }
    gate["deterministicDigest"] = sha256_digest({k: v for k, v in gate.items() if k != "deterministicDigest"})
    return gate
