"""Deterministic model builders for read-only API skeletons."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def build_endpoint_skeleton(*, endpoint_key: str, path: str, page_key: str, source_data_source_key: str, source_projection_type: str, response_contract_id: str, auth_policy: str, implementation_state: str) -> dict[str, Any]:
    item = {
        "endpointSkeletonId": sha256_digest({"endpointKey": endpoint_key, "path": path}),
        "endpointKey": endpoint_key,
        "method": "GET",
        "path": path,
        "pageKey": page_key,
        "sourceDataSourceKey": source_data_source_key,
        "sourceProjectionType": source_projection_type,
        "responseContractId": response_contract_id,
        "authPolicy": auth_policy,
        "readOnly": True,
        "implementationState": implementation_state,
        "productionEnabled": False,
        "databaseAccessEnabled": False,
        "writeOperationEnabled": False,
        "runtimeActivationEnabled": False,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_response_contract(*, endpoint_key: str, response_shape: Mapping[str, Any], source_artifact_path: str, projection_root_key: str, pagination_supported: bool, filters_supported: bool, facets_supported: bool) -> dict[str, Any]:
    item = {
        "responseContractId": sha256_digest({"endpointKey": endpoint_key, "sourceArtifactPath": source_artifact_path}),
        "endpointKey": endpoint_key,
        "responseShape": dict(response_shape),
        "sourceArtifactPath": source_artifact_path,
        "projectionRootKey": projection_root_key,
        "paginationSupported": bool(pagination_supported),
        "filtersSupported": bool(filters_supported),
        "facetsSupported": bool(facets_supported),
        "containsCustomerAssetIdentifiers": False,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_route_group(*, group_key: str, title: str, endpoint_skeleton_ids: Sequence[str]) -> dict[str, Any]:
    item = {
        "routeGroupId": sha256_digest({"groupKey": group_key}),
        "groupKey": group_key,
        "title": title,
        "endpointSkeletonIds": list(endpoint_skeleton_ids),
        "readOnly": True,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_api_readiness_gate(*, gate_id: str, gate_name: str, status: str, severity: str, blocking: bool, reason_codes: Sequence[str]) -> dict[str, Any]:
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


def build_read_only_api_skeleton(
    *,
    api_skeleton_id: str,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    endpoint_skeletons: Sequence[Mapping[str, Any]],
    response_contracts: Sequence[Mapping[str, Any]],
    route_groups: Sequence[Mapping[str, Any]],
    api_readiness_gates: Sequence[Mapping[str, Any]],
    boundary_matrix: Sequence[Mapping[str, Any]],
    source_artifact_references: Sequence[Mapping[str, Any]],
    generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
) -> dict[str, Any]:
    skeleton = {
        "apiSkeletonId": api_skeleton_id,
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "endpointSkeletons": list(endpoint_skeletons),
        "responseContracts": list(response_contracts),
        "routeGroups": list(route_groups),
        "apiReadinessGates": list(api_readiness_gates),
        "boundaryMatrix": list(boundary_matrix),
        "sourceArtifactReferences": list(source_artifact_references),
        "generatedAtPolicy": generated_at_policy,
    }
    skeleton["deterministicDigest"] = sha256_digest({k: v for k, v in skeleton.items() if k != "deterministicDigest"})
    return skeleton
