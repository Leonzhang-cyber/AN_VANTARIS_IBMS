"""Deterministic builders for International GA final local verification."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def _digest_item(item: dict[str, Any]) -> dict[str, Any]:
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_local_verification_entry(*, validation_area: str, command: str, expected_marker: str, required: bool, status: str) -> dict[str, Any]:
    return _digest_item({"verificationEntryId": sha256_digest({"command": command}), "validationArea": validation_area, "command": command, "expectedMarker": expected_marker, "required": bool(required), "status": status})


def build_commit_chain_entry(*, commit_reference: str, stage_key: str, title: str, active: bool, required_for_release: bool) -> dict[str, Any]:
    return _digest_item({"commitReference": commit_reference, "stageKey": stage_key, "title": title, "active": bool(active), "requiredForRelease": bool(required_for_release)})


def build_active_artifact_snapshot(*, artifact_key: str, artifact_path: str, artifact_type: str, present: bool, active: bool) -> dict[str, Any]:
    return _digest_item({"artifactSnapshotId": sha256_digest({"artifactKey": artifact_key, "artifactPath": artifact_path}), "artifactKey": artifact_key, "artifactPath": artifact_path, "artifactType": artifact_type, "present": bool(present), "active": bool(active)})


def build_optional_tag_plan(*, proposed_tag_name: str, tag_allowed_now: bool, requires_explicit_user_approval: bool, suggested_command: str, rollback_note: str) -> dict[str, Any]:
    return _digest_item({"tagPlanId": sha256_digest({"proposedTagName": proposed_tag_name}), "proposedTagName": proposed_tag_name, "tagAllowedNow": bool(tag_allowed_now), "requiresExplicitUserApproval": bool(requires_explicit_user_approval), "suggestedCommand": suggested_command, "rollbackNote": rollback_note})


def build_optional_push_plan(*, push_allowed_now: bool, requires_explicit_user_approval: bool, suggested_command: str, remote_policy: str) -> dict[str, Any]:
    return _digest_item({"pushPlanId": sha256_digest({"suggestedCommand": suggested_command}), "pushAllowedNow": bool(push_allowed_now), "requiresExplicitUserApproval": bool(requires_explicit_user_approval), "suggestedCommand": suggested_command, "remotePolicy": remote_policy})


def build_final_boundary_statement(*, statement_id: str, database_write_allowed: bool, runtime_activation_allowed: bool, production_activation_allowed: bool, api_production_allowed: bool, frontend_production_allowed: bool, approval_execution_allowed: bool, push_allowed: bool, tag_allowed: bool, customer_identifier_leakage_allowed: bool) -> dict[str, Any]:
    return _digest_item({"statementId": statement_id, "databaseWriteAllowed": bool(database_write_allowed), "runtimeActivationAllowed": bool(runtime_activation_allowed), "productionActivationAllowed": bool(production_activation_allowed), "apiProductionAllowed": bool(api_production_allowed), "frontendProductionAllowed": bool(frontend_production_allowed), "approvalExecutionAllowed": bool(approval_execution_allowed), "pushAllowed": bool(push_allowed), "tagAllowed": bool(tag_allowed), "customerIdentifierLeakageAllowed": bool(customer_identifier_leakage_allowed)})


def build_final_release_decision(*, decision_state: str, international_ga_release_candidate_ready: bool, local_verification_passed: bool, ready_for_stakeholder_handoff: bool, push_allowed: bool, tag_allowed: bool, production_activation_allowed: bool, runtime_activation_allowed: bool, decision_reason: str) -> dict[str, Any]:
    return _digest_item({"decisionId": sha256_digest({"decisionState": decision_state}), "decisionState": decision_state, "internationalGaReleaseCandidateReady": bool(international_ga_release_candidate_ready), "localVerificationPassed": bool(local_verification_passed), "readyForStakeholderHandoff": bool(ready_for_stakeholder_handoff), "pushAllowed": bool(push_allowed), "tagAllowed": bool(tag_allowed), "productionActivationAllowed": bool(production_activation_allowed), "runtimeActivationAllowed": bool(runtime_activation_allowed), "decisionReason": decision_reason})


def build_handoff_confirmation(*, handoff_notes_frozen: bool, release_package_ready: bool, release_gate_passed: bool, validation_matrix_ready: bool, stakeholder_handoff_ready: bool, engineering_handoff_ready: bool) -> dict[str, Any]:
    return _digest_item({"confirmationId": sha256_digest({"handoffNotesFrozen": handoff_notes_frozen, "releasePackageReady": release_package_ready}), "handoffNotesFrozen": bool(handoff_notes_frozen), "releasePackageReady": bool(release_package_ready), "releaseGatePassed": bool(release_gate_passed), "validationMatrixReady": bool(validation_matrix_ready), "stakeholderHandoffReady": bool(stakeholder_handoff_ready), "engineeringHandoffReady": bool(engineering_handoff_ready)})


def build_verification_gate(*, gate_id: str, gate_name: str, status: str, severity: str, blocking: bool, reason_codes: Sequence[str]) -> dict[str, Any]:
    return _digest_item({"gateId": gate_id, "gateName": gate_name, "status": status, "severity": severity, "blocking": bool(blocking), "reasonCodes": sorted(str(code) for code in reason_codes)})


def build_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    return _digest_item({"artifactType": artifact_type, "path": path, "digest": digest})


def build_international_ga_final_local_verification(*, verification_id: str, authority: str, profile_id: str, implementation_status: str, readiness_outcome: str, summary: Mapping[str, Any], local_verification_matrix: Sequence[Mapping[str, Any]], commit_chain_summary: Sequence[Mapping[str, Any]], active_artifact_snapshot: Sequence[Mapping[str, Any]], optional_tag_plan: Mapping[str, Any], optional_push_plan: Mapping[str, Any], final_boundary_statement: Mapping[str, Any], final_release_decision: Mapping[str, Any], handoff_confirmation: Mapping[str, Any], verification_gates: Sequence[Mapping[str, Any]], source_artifact_references: Sequence[Mapping[str, Any]], generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP") -> dict[str, Any]:
    verification = {"verificationId": verification_id, "contractVersion": CONTRACT_VERSION, "authority": authority, "profileId": profile_id, "implementationStatus": implementation_status, "readinessOutcome": readiness_outcome, "summary": dict(summary), "localVerificationMatrix": list(local_verification_matrix), "commitChainSummary": list(commit_chain_summary), "activeArtifactSnapshot": list(active_artifact_snapshot), "optionalTagPlan": dict(optional_tag_plan), "optionalPushPlan": dict(optional_push_plan), "finalBoundaryStatement": dict(final_boundary_statement), "finalReleaseDecision": dict(final_release_decision), "handoffConfirmation": dict(handoff_confirmation), "verificationGates": list(verification_gates), "sourceArtifactReferences": list(source_artifact_references), "generatedAtPolicy": generated_at_policy}
    verification["deterministicDigest"] = sha256_digest({k: v for k, v in verification.items() if k != "deterministicDigest"})
    return verification
