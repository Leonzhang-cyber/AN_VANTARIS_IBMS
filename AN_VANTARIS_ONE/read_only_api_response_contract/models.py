"""Deterministic model builders for read-only API response contracts."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def build_endpoint_response_contract(*, endpoint_key: str, method: str, path: str, response_shape: str, source_projection_type: str, source_artifact_path: str, projection_root_key: str, error_contract_id: str, auth_policy_contract_id: str) -> dict[str, Any]:
    item = {
        "endpointResponseContractId": sha256_digest({"endpointKey": endpoint_key, "path": path}),
        "endpointKey": endpoint_key,
        "method": method,
        "path": path,
        "responseShape": response_shape,
        "sourceProjectionType": source_projection_type,
        "sourceArtifactPath": source_artifact_path,
        "projectionRootKey": projection_root_key,
        "readOnly": True,
        "envelopeRequired": True,
        "paginationSupported": True,
        "filtersSupported": True,
        "facetsSupported": True,
        "errorContractId": error_contract_id,
        "authPolicyContractId": auth_policy_contract_id,
        "containsCustomerAssetIdentifiers": False,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_pagination_contract(*, endpoint_key: str) -> dict[str, Any]:
    item = {
        "paginationContractId": sha256_digest({"endpointKey": endpoint_key, "contract": "PAGINATION"}),
        "endpointKey": endpoint_key,
        "supported": True,
        "defaultPageSize": 25,
        "maxPageSize": 100,
        "stableContinuationTokenRequired": True,
        "deterministicOrderingRequired": True,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_filter_contract(*, endpoint_key: str, filter_keys: Sequence[str]) -> dict[str, Any]:
    item = {
        "filterContractId": sha256_digest({"endpointKey": endpoint_key, "contract": "FILTER"}),
        "endpointKey": endpoint_key,
        "filterKeys": sorted(str(key) for key in filter_keys),
        "supported": True,
        "deterministic": True,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_facet_contract(*, endpoint_key: str, facet_keys: Sequence[str]) -> dict[str, Any]:
    item = {
        "facetContractId": sha256_digest({"endpointKey": endpoint_key, "contract": "FACET"}),
        "endpointKey": endpoint_key,
        "facetKeys": sorted(str(key) for key in facet_keys),
        "supported": True,
        "deterministic": True,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_error_contract(*, endpoint_key: str) -> dict[str, Any]:
    item = {
        "errorContractId": sha256_digest({"endpointKey": endpoint_key, "contract": "ERROR"}),
        "endpointKey": endpoint_key,
        "errorShape": "STANDARD_ERROR_ENVELOPE",
        "allowedStatusCodes": [400, 401, 403, 404, 500],
        "noStackTraceLeakage": True,
        "noCredentialLeakage": True,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_auth_policy_contract(*, endpoint_key: str, role_policy_required: bool = True) -> dict[str, Any]:
    item = {
        "authPolicyContractId": sha256_digest({"endpointKey": endpoint_key, "contract": "AUTH"}),
        "endpointKey": endpoint_key,
        "authRequired": True,
        "rolePolicyRequired": bool(role_policy_required),
        "allowedRoles": ["ADMIN", "ENGINEER", "OPERATOR"],
        "anonymousAccessAllowed": False,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_response_readiness_gate(*, gate_id: str, gate_name: str, status: str, severity: str, blocking: bool, reason_codes: Sequence[str]) -> dict[str, Any]:
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


def build_read_only_api_response_contract(
    *,
    response_contract_gate_id: str,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    endpoint_response_contracts: Sequence[Mapping[str, Any]],
    pagination_contracts: Sequence[Mapping[str, Any]],
    filter_contracts: Sequence[Mapping[str, Any]],
    facet_contracts: Sequence[Mapping[str, Any]],
    error_contracts: Sequence[Mapping[str, Any]],
    auth_policy_contracts: Sequence[Mapping[str, Any]],
    response_readiness_gates: Sequence[Mapping[str, Any]],
    boundary_matrix: Sequence[Mapping[str, Any]],
    source_artifact_references: Sequence[Mapping[str, Any]],
    generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
) -> dict[str, Any]:
    contract = {
        "responseContractGateId": response_contract_gate_id,
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "endpointResponseContracts": list(endpoint_response_contracts),
        "paginationContracts": list(pagination_contracts),
        "filterContracts": list(filter_contracts),
        "facetContracts": list(facet_contracts),
        "errorContracts": list(error_contracts),
        "authPolicyContracts": list(auth_policy_contracts),
        "responseReadinessGates": list(response_readiness_gates),
        "boundaryMatrix": list(boundary_matrix),
        "sourceArtifactReferences": list(source_artifact_references),
        "generatedAtPolicy": generated_at_policy,
    }
    contract["deterministicDigest"] = sha256_digest({k: v for k, v in contract.items() if k != "deterministicDigest"})
    return contract
