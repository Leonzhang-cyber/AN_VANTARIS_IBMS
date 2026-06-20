"""Deterministic model builders for A4 readiness release gates."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def build_stage_result(*, stage_id: str, stage_name: str, pass_marker: str, commit_reference: str, artifact_path: str, validator_name: str, status: str, summary: Mapping[str, Any]) -> dict[str, Any]:
    stage = {
        "stageId": stage_id,
        "stageName": stage_name,
        "passMarker": pass_marker,
        "commitReference": commit_reference,
        "artifactPath": artifact_path,
        "validatorName": validator_name,
        "status": status,
        "summary": dict(summary),
    }
    stage["deterministicDigest"] = sha256_digest(stage)
    return stage


def build_gate_result(*, gate_id: str, gate_name: str, status: str, severity: str, reason_codes: Sequence[str], blocking: bool, evidence_references: Sequence[str]) -> dict[str, Any]:
    gate = {
        "gateId": gate_id,
        "gateName": gate_name,
        "status": status,
        "severity": severity,
        "reasonCodes": sorted(str(reason) for reason in reason_codes),
        "blocking": bool(blocking),
        "evidenceReferences": sorted(str(ref) for ref in evidence_references),
    }
    gate["deterministicDigest"] = sha256_digest(gate)
    return gate


def build_regression_matrix_entry(*, validator_name: str, command: str, expected_marker: str, status: str, required_for_release: bool) -> dict[str, Any]:
    entry = {
        "validatorName": validator_name,
        "command": command,
        "expectedMarker": expected_marker,
        "status": status,
        "requiredForRelease": bool(required_for_release),
    }
    entry["deterministicDigest"] = sha256_digest(entry)
    return entry


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


def build_release_decision(
    *,
    decision_state: str,
    decision_reason: str,
    release_allowed: bool,
    push_allowed: bool,
    production_activation_allowed: bool,
    runtime_activation_allowed: bool,
    database_write_allowed: bool,
    api_enabled: bool,
    frontend_enabled: bool,
    decision_write_allowed: bool,
    approval_write_allowed: bool,
    audit_write_allowed: bool,
) -> dict[str, Any]:
    decision = {
        "decisionState": decision_state,
        "decisionReason": decision_reason,
        "releaseAllowed": bool(release_allowed),
        "pushAllowed": bool(push_allowed),
        "productionActivationAllowed": bool(production_activation_allowed),
        "runtimeActivationAllowed": bool(runtime_activation_allowed),
        "databaseWriteAllowed": bool(database_write_allowed),
        "apiEnabled": bool(api_enabled),
        "frontendEnabled": bool(frontend_enabled),
        "decisionWriteAllowed": bool(decision_write_allowed),
        "approvalWriteAllowed": bool(approval_write_allowed),
        "auditWriteAllowed": bool(audit_write_allowed),
    }
    decision["deterministicDigest"] = sha256_digest(decision)
    return decision


def build_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    ref = {"artifactType": artifact_type, "path": path, "digest": digest}
    ref["deterministicDigest"] = sha256_digest(ref)
    return ref


def build_a4_readiness_release_gate(
    *,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    stage_results: Sequence[Mapping[str, Any]],
    gate_results: Sequence[Mapping[str, Any]],
    regression_matrix: Sequence[Mapping[str, Any]],
    boundary_matrix: Sequence[Mapping[str, Any]],
    artifact_references: Sequence[Mapping[str, Any]],
    release_decision: Mapping[str, Any],
    release_notes: Sequence[str],
    generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
) -> dict[str, Any]:
    release_gate = {
        "releaseGateId": sha256_digest(
            {
                "contractVersion": CONTRACT_VERSION,
                "authority": authority,
                "profileId": profile_id,
                "stageDigests": [stage.get("deterministicDigest") for stage in stage_results],
                "gateDigests": [gate.get("deterministicDigest") for gate in gate_results],
            }
        ),
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "stageResults": list(stage_results),
        "gateResults": list(gate_results),
        "regressionMatrix": list(regression_matrix),
        "boundaryMatrix": list(boundary_matrix),
        "artifactReferences": list(artifact_references),
        "releaseDecision": dict(release_decision),
        "releaseNotes": sorted(str(note) for note in release_notes),
        "generatedAtPolicy": generated_at_policy,
    }
    release_gate["deterministicDigest"] = sha256_digest({k: v for k, v in release_gate.items() if k != "deterministicDigest"})
    return release_gate
