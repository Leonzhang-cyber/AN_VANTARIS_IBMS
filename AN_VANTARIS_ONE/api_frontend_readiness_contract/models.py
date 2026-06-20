"""Deterministic model builders for API / Frontend readiness contracts."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def build_api_endpoint_candidate(*, endpoint_key: str, path_candidate: str, source_page_key: str, source_data_source_key: str, source_projection_type: str, response_contract_state: str) -> dict[str, Any]:
    item = {
        "endpointCandidateId": sha256_digest({"endpointKey": endpoint_key}),
        "endpointKey": endpoint_key,
        "method": "GET",
        "pathCandidate": path_candidate,
        "sourcePageKey": source_page_key,
        "sourceDataSourceKey": source_data_source_key,
        "sourceProjectionType": source_projection_type,
        "readOnly": True,
        "implementationAllowed": False,
        "publicApiEnabled": False,
        "databaseAccessAllowed": False,
        "writeOperationAllowed": False,
        "authPolicyRequired": True,
        "responseContractState": response_contract_state,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_frontend_page_candidate(*, page_key: str, title: str, page_type: str, route_candidate_key: str, source_data_source_keys: Sequence[str], card_candidate_ids: Sequence[str], readiness_state: str) -> dict[str, Any]:
    item = {
        "pageCandidateId": sha256_digest({"pageKey": page_key}),
        "pageKey": page_key,
        "title": title,
        "pageType": page_type,
        "routeCandidateKey": route_candidate_key,
        "sourceDataSourceKeys": sorted(str(key) for key in source_data_source_keys),
        "cardCandidateIds": sorted(str(card_id) for card_id in card_candidate_ids),
        "implementationAllowed": False,
        "routeImplementationAllowed": False,
        "runtimeDataMutationAllowed": False,
        "readinessState": readiness_state,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_frontend_route_candidate(*, route_key: str, path_candidate: str, page_key: str) -> dict[str, Any]:
    item = {
        "routeCandidateId": sha256_digest({"routeKey": route_key}),
        "routeKey": route_key,
        "pathCandidate": path_candidate,
        "pageKey": page_key,
        "implementationAllowed": False,
        "runtimeDataMutationAllowed": False,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_data_binding_contract(*, page_key: str, data_source_key: str, source_artifact_path: str, source_projection_type: str, api_endpoint_candidate_id: str, frontend_page_candidate_id: str) -> dict[str, Any]:
    item = {
        "dataBindingId": sha256_digest({"pageKey": page_key, "dataSourceKey": data_source_key}),
        "pageKey": page_key,
        "dataSourceKey": data_source_key,
        "sourceArtifactPath": source_artifact_path,
        "sourceProjectionType": source_projection_type,
        "readOnly": True,
        "apiEndpointCandidateId": api_endpoint_candidate_id,
        "frontendPageCandidateId": frontend_page_candidate_id,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_card_binding_contract(*, card_type: str, page_key: str, title: str, source_data_source_keys: Sequence[str]) -> dict[str, Any]:
    item = {
        "cardBindingId": sha256_digest({"pageKey": page_key, "title": title, "cardType": card_type}),
        "cardType": card_type,
        "pageKey": page_key,
        "title": title,
        "sourceDataSourceKeys": sorted(str(key) for key in source_data_source_keys),
        "readOnly": True,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_queue_binding_contract(*, queue_key: str, page_key: str, source_data_source_keys: Sequence[str], row_count: int) -> dict[str, Any]:
    item = {
        "queueBindingId": sha256_digest({"queueKey": queue_key, "pageKey": page_key}),
        "queueKey": queue_key,
        "pageKey": page_key,
        "sourceDataSourceKeys": sorted(str(key) for key in source_data_source_keys),
        "rowCount": int(row_count),
        "readOnly": True,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_readiness_gate(*, gate_id: str, gate_name: str, status: str, severity: str, blocking: bool, reason_codes: Sequence[str]) -> dict[str, Any]:
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


def build_boundary_matrix_entry(*, boundary_key: str, expected_value: Any, actual_value: Any, status: str, blocking: bool) -> dict[str, Any]:
    item = {
        "boundaryKey": boundary_key,
        "expectedValue": expected_value,
        "actualValue": actual_value,
        "status": status,
        "blocking": bool(blocking),
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    item = {"artifactType": artifact_type, "path": path, "digest": digest}
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_api_frontend_readiness_contract(
    *,
    contract_id: str,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    api_endpoint_candidates: Sequence[Mapping[str, Any]],
    frontend_page_candidates: Sequence[Mapping[str, Any]],
    frontend_route_candidates: Sequence[Mapping[str, Any]],
    data_binding_contracts: Sequence[Mapping[str, Any]],
    card_binding_contracts: Sequence[Mapping[str, Any]],
    queue_binding_contracts: Sequence[Mapping[str, Any]],
    readiness_gates: Sequence[Mapping[str, Any]],
    boundary_matrix: Sequence[Mapping[str, Any]],
    source_artifact_references: Sequence[Mapping[str, Any]],
    generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
) -> dict[str, Any]:
    contract = {
        "contractId": contract_id,
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "apiEndpointCandidates": list(api_endpoint_candidates),
        "frontendPageCandidates": list(frontend_page_candidates),
        "frontendRouteCandidates": list(frontend_route_candidates),
        "dataBindingContracts": list(data_binding_contracts),
        "cardBindingContracts": list(card_binding_contracts),
        "queueBindingContracts": list(queue_binding_contracts),
        "readinessGates": list(readiness_gates),
        "boundaryMatrix": list(boundary_matrix),
        "sourceArtifactReferences": list(source_artifact_references),
        "generatedAtPolicy": generated_at_policy,
    }
    contract["deterministicDigest"] = sha256_digest({k: v for k, v in contract.items() if k != "deterministicDigest"})
    return contract
