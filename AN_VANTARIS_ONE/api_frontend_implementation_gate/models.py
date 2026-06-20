"""Deterministic model builders for API / Frontend implementation readiness gates."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def build_api_implementation_readiness(*, candidate_endpoint_count: int, read_only_endpoint_candidate_count: int, endpoint_contract_coverage_count: int, auth_policy_required_count: int, skeleton_phase_allowed: bool, required_future_phase: str) -> dict[str, Any]:
    item = {
        "readinessId": sha256_digest({"readiness": "API", "candidateEndpointCount": candidate_endpoint_count}),
        "candidateEndpointCount": int(candidate_endpoint_count),
        "readOnlyEndpointCandidateCount": int(read_only_endpoint_candidate_count),
        "endpointContractCoverageCount": int(endpoint_contract_coverage_count),
        "authPolicyRequiredCount": int(auth_policy_required_count),
        "implementationAllowed": False,
        "publicApiEnabled": False,
        "databaseAccessAllowed": False,
        "writeOperationAllowed": False,
        "skeletonPhaseAllowed": bool(skeleton_phase_allowed),
        "requiredFuturePhase": required_future_phase,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_frontend_implementation_readiness(*, page_candidate_count: int, route_candidate_count: int, card_candidate_count: int, data_binding_contract_count: int, route_contract_coverage_count: int, skeleton_phase_allowed: bool, required_future_phase: str) -> dict[str, Any]:
    item = {
        "readinessId": sha256_digest({"readiness": "FRONTEND", "pageCandidateCount": page_candidate_count}),
        "pageCandidateCount": int(page_candidate_count),
        "routeCandidateCount": int(route_candidate_count),
        "cardCandidateCount": int(card_candidate_count),
        "dataBindingContractCount": int(data_binding_contract_count),
        "routeContractCoverageCount": int(route_contract_coverage_count),
        "implementationAllowed": False,
        "routeImplementationAllowed": False,
        "runtimeDataMutationAllowed": False,
        "skeletonPhaseAllowed": bool(skeleton_phase_allowed),
        "requiredFuturePhase": required_future_phase,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_contract_coverage_entry(*, coverage_type: str, source_key: str, expected_count: int, actual_count: int, blocking: bool) -> dict[str, Any]:
    item = {
        "coverageId": sha256_digest({"coverageType": coverage_type, "sourceKey": source_key}),
        "coverageType": coverage_type,
        "sourceKey": source_key,
        "expectedCount": int(expected_count),
        "actualCount": int(actual_count),
        "status": "PASS" if int(expected_count) == int(actual_count) else "FAIL",
        "blocking": bool(blocking),
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


def build_gate_result(*, gate_id: str, gate_name: str, status: str, severity: str, blocking: bool, reason_codes: Sequence[str]) -> dict[str, Any]:
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


def build_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    item = {"artifactType": artifact_type, "path": path, "digest": digest}
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_implementation_decision(*, decision_state: str, api_skeleton_phase_allowed: bool, frontend_skeleton_phase_allowed: bool, production_api_allowed: bool, production_frontend_allowed: bool, database_write_allowed: bool, runtime_activation_allowed: bool, production_activation_allowed: bool, push_allowed: bool, decision_reason: str) -> dict[str, Any]:
    item = {
        "decisionState": decision_state,
        "apiSkeletonPhaseAllowed": bool(api_skeleton_phase_allowed),
        "frontendSkeletonPhaseAllowed": bool(frontend_skeleton_phase_allowed),
        "productionApiAllowed": bool(production_api_allowed),
        "productionFrontendAllowed": bool(production_frontend_allowed),
        "databaseWriteAllowed": bool(database_write_allowed),
        "runtimeActivationAllowed": bool(runtime_activation_allowed),
        "productionActivationAllowed": bool(production_activation_allowed),
        "pushAllowed": bool(push_allowed),
        "decisionReason": decision_reason,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_api_frontend_implementation_readiness_gate(
    *,
    release_gate_id: str,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    api_implementation_readiness: Mapping[str, Any],
    frontend_implementation_readiness: Mapping[str, Any],
    contract_coverage_matrix: Sequence[Mapping[str, Any]],
    implementation_boundary_matrix: Sequence[Mapping[str, Any]],
    dependency_gate_results: Sequence[Mapping[str, Any]],
    release_gate_results: Sequence[Mapping[str, Any]],
    artifact_references: Sequence[Mapping[str, Any]],
    implementation_decision: Mapping[str, Any],
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
        "apiImplementationReadiness": dict(api_implementation_readiness),
        "frontendImplementationReadiness": dict(frontend_implementation_readiness),
        "contractCoverageMatrix": list(contract_coverage_matrix),
        "implementationBoundaryMatrix": list(implementation_boundary_matrix),
        "dependencyGateResults": list(dependency_gate_results),
        "releaseGateResults": list(release_gate_results),
        "artifactReferences": list(artifact_references),
        "implementationDecision": dict(implementation_decision),
        "generatedAtPolicy": generated_at_policy,
    }
    gate["deterministicDigest"] = sha256_digest({k: v for k, v in gate.items() if k != "deterministicDigest"})
    return gate
