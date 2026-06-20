"""Deterministic model builders for Operations Console Handoff Gates."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def build_page_handoff_entry(
    *,
    page_key: str,
    page_title: str,
    page_type: str,
    readiness_state: str,
    source_projection_keys: Sequence[str],
    data_source_ids: Sequence[str],
    card_ids: Sequence[str],
    api_contract_candidate_state: str,
    frontend_contract_candidate_state: str,
    blocked: bool,
    decision_required: bool,
) -> dict[str, Any]:
    entry = {
        "pageHandoffId": sha256_digest({"pageKey": page_key, "handoffType": "PAGE"}),
        "pageKey": page_key,
        "pageTitle": page_title,
        "pageType": page_type,
        "readinessState": readiness_state,
        "sourceProjectionKeys": sorted(str(key) for key in source_projection_keys),
        "dataSourceIds": sorted(str(data_source_id) for data_source_id in data_source_ids),
        "cardIds": sorted(str(card_id) for card_id in card_ids),
        "apiContractCandidateState": api_contract_candidate_state,
        "frontendContractCandidateState": frontend_contract_candidate_state,
        "blocked": bool(blocked),
        "decisionRequired": bool(decision_required),
    }
    entry["deterministicDigest"] = sha256_digest(entry)
    return entry


def build_data_source_handoff_entry(
    *,
    data_source_key: str,
    source_artifact_path: str,
    source_projection_type: str,
    read_only: bool,
    api_enabled: bool,
    frontend_enabled: bool,
    database_access_enabled: bool,
    api_contract_candidate_state: str,
    frontend_contract_candidate_state: str,
) -> dict[str, Any]:
    entry = {
        "dataSourceHandoffId": sha256_digest({"dataSourceKey": data_source_key, "handoffType": "DATASOURCE"}),
        "dataSourceKey": data_source_key,
        "sourceArtifactPath": source_artifact_path,
        "sourceProjectionType": source_projection_type,
        "readOnly": bool(read_only),
        "apiEnabled": bool(api_enabled),
        "frontendEnabled": bool(frontend_enabled),
        "databaseAccessEnabled": bool(database_access_enabled),
        "apiContractCandidateState": api_contract_candidate_state,
        "frontendContractCandidateState": frontend_contract_candidate_state,
    }
    entry["deterministicDigest"] = sha256_digest(entry)
    return entry


def build_card_handoff_entry(
    *,
    card_type: str,
    title: str,
    page_key: str,
    source_data_source_keys: Sequence[str],
    readiness_state: str,
    api_contract_candidate_state: str,
    frontend_contract_candidate_state: str,
) -> dict[str, Any]:
    entry = {
        "cardHandoffId": sha256_digest({"pageKey": page_key, "title": title, "handoffType": "CARD"}),
        "cardType": card_type,
        "title": title,
        "pageKey": page_key,
        "sourceDataSourceKeys": sorted(str(key) for key in source_data_source_keys),
        "readinessState": readiness_state,
        "apiContractCandidateState": api_contract_candidate_state,
        "frontendContractCandidateState": frontend_contract_candidate_state,
    }
    entry["deterministicDigest"] = sha256_digest(entry)
    return entry


def build_api_readiness_contract(
    *,
    contract_state: str,
    endpoint_implementation_allowed: bool,
    public_api_enabled: bool,
    database_access_allowed: bool,
    write_operation_allowed: bool,
    candidate_endpoint_count: int,
    read_only_endpoint_candidate_count: int,
) -> dict[str, Any]:
    contract = {
        "contractId": sha256_digest({"contract": "API_READINESS", "candidateEndpointCount": candidate_endpoint_count}),
        "contractState": contract_state,
        "endpointImplementationAllowed": bool(endpoint_implementation_allowed),
        "publicApiEnabled": bool(public_api_enabled),
        "databaseAccessAllowed": bool(database_access_allowed),
        "writeOperationAllowed": bool(write_operation_allowed),
        "candidateEndpointCount": int(candidate_endpoint_count),
        "readOnlyEndpointCandidateCount": int(read_only_endpoint_candidate_count),
    }
    contract["deterministicDigest"] = sha256_digest(contract)
    return contract


def build_frontend_readiness_contract(
    *,
    contract_state: str,
    frontend_implementation_allowed: bool,
    route_implementation_allowed: bool,
    runtime_data_mutation_allowed: bool,
    page_candidate_count: int,
    card_candidate_count: int,
) -> dict[str, Any]:
    contract = {
        "contractId": sha256_digest({"contract": "FRONTEND_READINESS", "pageCandidateCount": page_candidate_count, "cardCandidateCount": card_candidate_count}),
        "contractState": contract_state,
        "frontendImplementationAllowed": bool(frontend_implementation_allowed),
        "routeImplementationAllowed": bool(route_implementation_allowed),
        "runtimeDataMutationAllowed": bool(runtime_data_mutation_allowed),
        "pageCandidateCount": int(page_candidate_count),
        "cardCandidateCount": int(card_candidate_count),
    }
    contract["deterministicDigest"] = sha256_digest(contract)
    return contract


def build_release_gate_result(*, gate_id: str, gate_name: str, status: str, severity: str, blocking: bool, reason_codes: Sequence[str], evidence_references: Sequence[str]) -> dict[str, Any]:
    result = {
        "gateId": gate_id,
        "gateName": gate_name,
        "status": status,
        "severity": severity,
        "blocking": bool(blocking),
        "reasonCodes": sorted(str(code) for code in reason_codes),
        "evidenceReferences": sorted(str(ref) for ref in evidence_references),
    }
    result["deterministicDigest"] = sha256_digest(result)
    return result


def build_boundary_matrix_entry(*, boundary_key: str, expected_value: Any, actual_value: Any, status: str, blocking: bool) -> dict[str, Any]:
    entry = {
        "boundaryKey": boundary_key,
        "expectedValue": expected_value,
        "actualValue": actual_value,
        "status": status,
        "blocking": bool(blocking),
    }
    entry["deterministicDigest"] = sha256_digest(entry)
    return entry


def build_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    ref = {"artifactType": artifact_type, "path": path, "digest": digest}
    ref["deterministicDigest"] = sha256_digest(ref)
    return ref


def build_handoff_decision(
    *,
    decision_state: str,
    handoff_allowed: bool,
    api_implementation_allowed: bool,
    frontend_implementation_allowed: bool,
    database_write_allowed: bool,
    runtime_activation_allowed: bool,
    production_activation_allowed: bool,
    push_allowed: bool,
    decision_reason: str,
) -> dict[str, Any]:
    decision = {
        "decisionState": decision_state,
        "handoffAllowed": bool(handoff_allowed),
        "apiImplementationAllowed": bool(api_implementation_allowed),
        "frontendImplementationAllowed": bool(frontend_implementation_allowed),
        "databaseWriteAllowed": bool(database_write_allowed),
        "runtimeActivationAllowed": bool(runtime_activation_allowed),
        "productionActivationAllowed": bool(production_activation_allowed),
        "pushAllowed": bool(push_allowed),
        "decisionReason": decision_reason,
    }
    decision["deterministicDigest"] = sha256_digest(decision)
    return decision


def build_operations_console_handoff_gate(
    *,
    handoff_gate_id: str,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    page_handoff_matrix: Sequence[Mapping[str, Any]],
    data_source_handoff_matrix: Sequence[Mapping[str, Any]],
    card_handoff_matrix: Sequence[Mapping[str, Any]],
    api_readiness_contract: Mapping[str, Any],
    frontend_readiness_contract: Mapping[str, Any],
    release_gate_results: Sequence[Mapping[str, Any]],
    boundary_matrix: Sequence[Mapping[str, Any]],
    artifact_references: Sequence[Mapping[str, Any]],
    handoff_decision: Mapping[str, Any],
    generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
) -> dict[str, Any]:
    gate = {
        "handoffGateId": handoff_gate_id,
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "pageHandoffMatrix": list(page_handoff_matrix),
        "dataSourceHandoffMatrix": list(data_source_handoff_matrix),
        "cardHandoffMatrix": list(card_handoff_matrix),
        "apiReadinessContract": dict(api_readiness_contract),
        "frontendReadinessContract": dict(frontend_readiness_contract),
        "releaseGateResults": list(release_gate_results),
        "boundaryMatrix": list(boundary_matrix),
        "artifactReferences": list(artifact_references),
        "handoffDecision": dict(handoff_decision),
        "generatedAtPolicy": generated_at_policy,
    }
    gate["deterministicDigest"] = sha256_digest({k: v for k, v in gate.items() if k != "deterministicDigest"})
    return gate
