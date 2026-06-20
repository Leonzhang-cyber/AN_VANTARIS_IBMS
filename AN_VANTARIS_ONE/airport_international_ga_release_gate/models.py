"""Deterministic builders for the Airport International GA release gate."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def _digest_item(item: dict[str, Any]) -> dict[str, Any]:
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_stage_result(*, stage_id: str, stage_name: str, pass_marker: str, artifact_path: str, validator_name: str, status: str, summary: Mapping[str, Any]) -> dict[str, Any]:
    return _digest_item({"stageId": stage_id, "stageName": stage_name, "passMarker": pass_marker, "artifactPath": artifact_path, "validatorName": validator_name, "status": status, "summary": dict(summary)})


def build_artifact_coverage_entry(*, stage_id: str, artifact_key: str, artifact_path: str, present: bool, required: bool) -> dict[str, Any]:
    return _digest_item({"coverageId": sha256_digest({"stageId": stage_id, "artifactKey": artifact_key}), "stageId": stage_id, "artifactKey": artifact_key, "artifactPath": artifact_path, "present": bool(present), "required": bool(required), "status": "PASS" if present or not required else "FAIL"})


def build_business_capability_entry(*, capability_key: str, title: str, source_stage: str, readiness_state: str) -> dict[str, Any]:
    return _digest_item({"capabilityId": sha256_digest({"capabilityKey": capability_key}), "capabilityKey": capability_key, "title": title, "sourceStage": source_stage, "readinessState": readiness_state, "readOnly": True, "productionEnabled": False})


def build_technical_boundary_entry(*, boundary_key: str, expected_value: Any, actual_value: Any, blocking: bool) -> dict[str, Any]:
    return _digest_item({"boundaryId": sha256_digest({"boundaryKey": boundary_key}), "boundaryKey": boundary_key, "expectedValue": expected_value, "actualValue": actual_value, "status": "PASS" if expected_value == actual_value else "FAIL", "blocking": bool(blocking)})


def build_release_gate_result(*, gate_id: str, gate_name: str, status: str, severity: str, blocking: bool, reason_codes: Sequence[str]) -> dict[str, Any]:
    return _digest_item({"gateId": gate_id, "gateName": gate_name, "status": status, "severity": severity, "blocking": bool(blocking), "reasonCodes": sorted(str(code) for code in reason_codes)})


def build_release_decision(*, decision_state: str, international_ga_readiness_allowed: bool, release_candidate_allowed: bool, push_allowed: bool, tag_allowed: bool, production_activation_allowed: bool, runtime_activation_allowed: bool, database_write_allowed: bool, api_production_allowed: bool, frontend_production_allowed: bool, approval_execution_allowed: bool, decision_reason: str) -> dict[str, Any]:
    return _digest_item({
        "decisionState": decision_state,
        "internationalGaReadinessAllowed": bool(international_ga_readiness_allowed),
        "releaseCandidateAllowed": bool(release_candidate_allowed),
        "pushAllowed": bool(push_allowed),
        "tagAllowed": bool(tag_allowed),
        "productionActivationAllowed": bool(production_activation_allowed),
        "runtimeActivationAllowed": bool(runtime_activation_allowed),
        "databaseWriteAllowed": bool(database_write_allowed),
        "apiProductionAllowed": bool(api_production_allowed),
        "frontendProductionAllowed": bool(frontend_production_allowed),
        "approvalExecutionAllowed": bool(approval_execution_allowed),
        "decisionReason": decision_reason,
    })


def build_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    return _digest_item({"artifactType": artifact_type, "path": path, "digest": digest})


def build_airport_international_ga_release_gate(*, release_gate_id: str, authority: str, profile_id: str, implementation_status: str, readiness_outcome: str, summary: Mapping[str, Any], stage_results: Sequence[Mapping[str, Any]], release_gate_results: Sequence[Mapping[str, Any]], artifact_coverage_matrix: Sequence[Mapping[str, Any]], business_capability_matrix: Sequence[Mapping[str, Any]], technical_boundary_matrix: Sequence[Mapping[str, Any]], regression_matrix: Sequence[Mapping[str, Any]], release_decision: Mapping[str, Any], source_artifact_references: Sequence[Mapping[str, Any]], generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP") -> dict[str, Any]:
    gate = {
        "releaseGateId": release_gate_id,
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "stageResults": list(stage_results),
        "releaseGateResults": list(release_gate_results),
        "artifactCoverageMatrix": list(artifact_coverage_matrix),
        "businessCapabilityMatrix": list(business_capability_matrix),
        "technicalBoundaryMatrix": list(technical_boundary_matrix),
        "regressionMatrix": list(regression_matrix),
        "releaseDecision": dict(release_decision),
        "sourceArtifactReferences": list(source_artifact_references),
        "generatedAtPolicy": generated_at_policy,
    }
    gate["deterministicDigest"] = sha256_digest({k: v for k, v in gate.items() if k != "deterministicDigest"})
    return gate
