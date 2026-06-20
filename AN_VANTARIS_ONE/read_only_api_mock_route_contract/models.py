"""Deterministic model builders for read-only API mock route contracts."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def build_mock_route_contract(
    *,
    endpoint_key: str,
    method: str,
    path: str,
    route_mode: str,
    source_projection_type: str,
    source_artifact_path: str,
    response_contract_id: str,
    auth_policy_contract_id: str,
    mock_response_shape: str,
    expected_status_codes: Sequence[int],
) -> dict[str, Any]:
    item = {
        "mockRouteContractId": sha256_digest({"endpointKey": endpoint_key, "path": path, "contract": "MOCK_ROUTE"}),
        "endpointKey": endpoint_key,
        "method": method,
        "path": path,
        "routeMode": route_mode,
        "sourceProjectionType": source_projection_type,
        "sourceArtifactPath": source_artifact_path,
        "responseContractId": response_contract_id,
        "authPolicyContractId": auth_policy_contract_id,
        "mockResponseShape": mock_response_shape,
        "expectedStatusCodes": list(expected_status_codes),
        "readOnly": True,
        "productionRouteEnabled": False,
        "databaseAccessEnabled": False,
        "writeOperationEnabled": False,
        "runtimeActivationEnabled": False,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_local_smoke_case(*, endpoint_key: str, method: str, path: str) -> dict[str, Any]:
    item = {
        "smokeCaseId": sha256_digest({"endpointKey": endpoint_key, "path": path, "contract": "LOCAL_SMOKE"}),
        "endpointKey": endpoint_key,
        "method": method,
        "path": path,
        "expectedStatusCode": 200,
        "expectedEnvelopeRequired": True,
        "expectedPaginationSupported": True,
        "expectedFiltersSupported": True,
        "expectedFacetsSupported": True,
        "expectedAuthRequired": True,
        "expectedReadOnly": True,
        "expectedNoWrite": True,
        "networkCallRequired": False,
        "localhostCallRequired": False,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_smoke_gate_result(*, gate_id: str, gate_name: str, status: str, severity: str, blocking: bool, reason_codes: Sequence[str]) -> dict[str, Any]:
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


def build_boundary_entry(*, boundary_key: str, expected_value: Any, actual_value: Any, blocking: bool) -> dict[str, Any]:
    item = {
        "boundaryKey": boundary_key,
        "expectedValue": expected_value,
        "actualValue": actual_value,
        "status": "PASS" if expected_value == actual_value else "FAIL",
        "blocking": bool(blocking),
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    item = {"artifactType": artifact_type, "path": path, "digest": digest}
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_read_only_api_mock_route_contract(
    *,
    mock_route_contract_id: str,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    mock_route_contracts: Sequence[Mapping[str, Any]],
    local_smoke_cases: Sequence[Mapping[str, Any]],
    smoke_gate_results: Sequence[Mapping[str, Any]],
    boundary_matrix: Sequence[Mapping[str, Any]],
    source_artifact_references: Sequence[Mapping[str, Any]],
    generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
) -> dict[str, Any]:
    contract = {
        "mockRouteContractId": mock_route_contract_id,
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "mockRouteContracts": list(mock_route_contracts),
        "localSmokeCases": list(local_smoke_cases),
        "smokeGateResults": list(smoke_gate_results),
        "boundaryMatrix": list(boundary_matrix),
        "sourceArtifactReferences": list(source_artifact_references),
        "generatedAtPolicy": generated_at_policy,
    }
    contract["deterministicDigest"] = sha256_digest({k: v for k, v in contract.items() if k != "deterministicDigest"})
    return contract
