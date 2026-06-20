"""Deterministic builders for International GA release candidate packages."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def _digest_item(item: dict[str, Any]) -> dict[str, Any]:
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_stage_inventory_entry(*, stage_id: str, stage_name: str, stage_status: str, active_pass_marker: str, active_artifact_path: str, commit_reference: str) -> dict[str, Any]:
    return _digest_item({"stageId": stage_id, "stageName": stage_name, "stageStatus": stage_status, "activePassMarker": active_pass_marker, "activeArtifactPath": active_artifact_path, "commitReference": commit_reference})


def build_artifact_inventory_entry(*, artifact_key: str, artifact_type: str, artifact_path: str, source_stage: str, required: bool, present: bool, active: bool, legacy_compatibility: bool) -> dict[str, Any]:
    return _digest_item({"artifactId": sha256_digest({"artifactKey": artifact_key, "artifactPath": artifact_path}), "artifactKey": artifact_key, "artifactType": artifact_type, "artifactPath": artifact_path, "sourceStage": source_stage, "required": bool(required), "present": bool(present), "active": bool(active), "legacyCompatibility": bool(legacy_compatibility)})


def build_validator_matrix_entry(*, validator_name: str, command: str, source_stage: str, expected_pass_marker: str, required_for_ga: bool, status: str) -> dict[str, Any]:
    return _digest_item({"validatorId": sha256_digest({"validatorName": validator_name}), "validatorName": validator_name, "command": command, "sourceStage": source_stage, "expectedPassMarker": expected_pass_marker, "requiredForGa": bool(required_for_ga), "status": status})


def build_unit_test_matrix_entry(*, test_path: str, source_stage: str, expected_scope: str, required_for_ga: bool, status: str) -> dict[str, Any]:
    return _digest_item({"testMatrixId": sha256_digest({"testPath": test_path}), "testPath": test_path, "sourceStage": source_stage, "expectedScope": expected_scope, "requiredForGa": bool(required_for_ga), "status": status})


def build_boundary_statement(*, statement_id: str, runtime_activation_allowed: bool, production_activation_allowed: bool, database_write_allowed: bool, api_production_allowed: bool, frontend_production_allowed: bool, approval_execution_allowed: bool, push_allowed: bool, tag_allowed: bool, customer_identifier_leakage_allowed: bool) -> dict[str, Any]:
    return _digest_item({"statementId": statement_id, "runtimeActivationAllowed": bool(runtime_activation_allowed), "productionActivationAllowed": bool(production_activation_allowed), "databaseWriteAllowed": bool(database_write_allowed), "apiProductionAllowed": bool(api_production_allowed), "frontendProductionAllowed": bool(frontend_production_allowed), "approvalExecutionAllowed": bool(approval_execution_allowed), "pushAllowed": bool(push_allowed), "tagAllowed": bool(tag_allowed), "customerIdentifierLeakageAllowed": bool(customer_identifier_leakage_allowed)})


def build_release_notes(*, release_candidate_name: str, release_candidate_type: str, release_summary: str, known_warnings: Sequence[str], compatibility_notes: Sequence[str], next_phase_recommendations: Sequence[str]) -> dict[str, Any]:
    return _digest_item({"releaseNotesId": sha256_digest({"releaseCandidateName": release_candidate_name}), "releaseCandidateName": release_candidate_name, "releaseCandidateType": release_candidate_type, "releaseSummary": release_summary, "knownWarnings": list(known_warnings), "compatibilityNotes": list(compatibility_notes), "nextPhaseRecommendations": list(next_phase_recommendations)})


def build_handoff_inventory_entry(*, handoff_type: str, title: str, source_artifact_path: str, target_future_phase: str, ready_for_handoff: bool, implementation_allowed_now: bool) -> dict[str, Any]:
    return _digest_item({"handoffId": sha256_digest({"handoffType": handoff_type}), "handoffType": handoff_type, "title": title, "sourceArtifactPath": source_artifact_path, "targetFuturePhase": target_future_phase, "readyForHandoff": bool(ready_for_handoff), "implementationAllowedNow": bool(implementation_allowed_now)})


def build_packaging_gate(*, gate_id: str, gate_name: str, status: str, severity: str, blocking: bool, reason_codes: Sequence[str]) -> dict[str, Any]:
    return _digest_item({"gateId": gate_id, "gateName": gate_name, "status": status, "severity": severity, "blocking": bool(blocking), "reasonCodes": sorted(str(code) for code in reason_codes)})


def build_release_decision(*, decision_state: str, international_ga_package_allowed: bool, international_ga_readiness_allowed: bool, release_candidate_allowed: bool, push_allowed: bool, tag_allowed: bool, production_activation_allowed: bool, runtime_activation_allowed: bool, database_write_allowed: bool, api_production_allowed: bool, frontend_production_allowed: bool, approval_execution_allowed: bool, decision_reason: str) -> dict[str, Any]:
    return _digest_item({"decisionState": decision_state, "internationalGaPackageAllowed": bool(international_ga_package_allowed), "internationalGaReadinessAllowed": bool(international_ga_readiness_allowed), "releaseCandidateAllowed": bool(release_candidate_allowed), "pushAllowed": bool(push_allowed), "tagAllowed": bool(tag_allowed), "productionActivationAllowed": bool(production_activation_allowed), "runtimeActivationAllowed": bool(runtime_activation_allowed), "databaseWriteAllowed": bool(database_write_allowed), "apiProductionAllowed": bool(api_production_allowed), "frontendProductionAllowed": bool(frontend_production_allowed), "approvalExecutionAllowed": bool(approval_execution_allowed), "decisionReason": decision_reason})


def build_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    return _digest_item({"artifactType": artifact_type, "path": path, "digest": digest})


def build_international_ga_release_candidate_package(*, package_id: str, authority: str, profile_id: str, package_version: str, implementation_status: str, readiness_outcome: str, summary: Mapping[str, Any], stage_inventory: Sequence[Mapping[str, Any]], artifact_inventory: Sequence[Mapping[str, Any]], validator_matrix: Sequence[Mapping[str, Any]], unit_test_matrix: Sequence[Mapping[str, Any]], boundary_statement: Mapping[str, Any], release_notes: Mapping[str, Any], handoff_inventory: Sequence[Mapping[str, Any]], packaging_gates: Sequence[Mapping[str, Any]], release_decision: Mapping[str, Any], source_artifact_references: Sequence[Mapping[str, Any]], generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP") -> dict[str, Any]:
    package = {"packageId": package_id, "contractVersion": CONTRACT_VERSION, "authority": authority, "profileId": profile_id, "packageVersion": package_version, "implementationStatus": implementation_status, "readinessOutcome": readiness_outcome, "summary": dict(summary), "stageInventory": list(stage_inventory), "artifactInventory": list(artifact_inventory), "validatorMatrix": list(validator_matrix), "unitTestMatrix": list(unit_test_matrix), "boundaryStatement": dict(boundary_statement), "releaseNotes": dict(release_notes), "handoffInventory": list(handoff_inventory), "packagingGates": list(packaging_gates), "releaseDecision": dict(release_decision), "sourceArtifactReferences": list(source_artifact_references), "generatedAtPolicy": generated_at_policy}
    package["deterministicDigest"] = sha256_digest({k: v for k, v in package.items() if k != "deterministicDigest"})
    return package
