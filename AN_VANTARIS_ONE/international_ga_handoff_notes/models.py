"""Deterministic builders for International GA handoff notes."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def _digest_item(item: dict[str, Any]) -> dict[str, Any]:
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_release_notes(*, release_title: str, release_type: str, release_candidate_name: str, release_summary: str, included_stage_groups: Sequence[str], included_business_capabilities: Sequence[str], readiness_statement: str) -> dict[str, Any]:
    return _digest_item({"releaseNotesId": sha256_digest({"releaseTitle": release_title}), "releaseTitle": release_title, "releaseType": release_type, "releaseCandidateName": release_candidate_name, "releaseSummary": release_summary, "includedStageGroups": list(included_stage_groups), "includedBusinessCapabilities": list(included_business_capabilities), "readinessStatement": readiness_statement})


def build_stakeholder_handoff_section(*, audience: str, title: str, summary: str, included_artifact_keys: Sequence[str], decision_required: bool) -> dict[str, Any]:
    return _digest_item({"sectionId": sha256_digest({"audience": audience}), "audience": audience, "title": title, "summary": summary, "includedArtifactKeys": list(included_artifact_keys), "decisionRequired": bool(decision_required)})


def build_engineering_handoff_section(*, engineering_area: str, title: str, summary: str, required_boundaries: Sequence[str], next_phase_allowed: bool, implementation_allowed_now: bool) -> dict[str, Any]:
    return _digest_item({"sectionId": sha256_digest({"engineeringArea": engineering_area}), "engineeringArea": engineering_area, "title": title, "summary": summary, "requiredBoundaries": list(required_boundaries), "nextPhaseAllowed": bool(next_phase_allowed), "implementationAllowedNow": bool(implementation_allowed_now)})


def build_validation_command(*, command: str, validation_area: str, required_for_handoff: bool, expected_marker: str) -> dict[str, Any]:
    return _digest_item({"commandId": sha256_digest({"command": command}), "command": command, "validationArea": validation_area, "requiredForHandoff": bool(required_for_handoff), "expectedMarker": expected_marker})


def build_known_warning(*, warning_type: str, title: str, description: str, severity: str, blocking: bool, mitigation: str) -> dict[str, Any]:
    return _digest_item({"warningId": sha256_digest({"warningType": warning_type}), "warningType": warning_type, "title": title, "description": description, "severity": severity, "blocking": bool(blocking), "mitigation": mitigation})


def build_boundary_statement(*, statement_id: str, database_write_allowed: bool, runtime_activation_allowed: bool, production_activation_allowed: bool, api_production_allowed: bool, frontend_production_allowed: bool, approval_execution_allowed: bool, push_allowed: bool, tag_allowed: bool, customer_identifier_leakage_allowed: bool) -> dict[str, Any]:
    return _digest_item({"statementId": statement_id, "databaseWriteAllowed": bool(database_write_allowed), "runtimeActivationAllowed": bool(runtime_activation_allowed), "productionActivationAllowed": bool(production_activation_allowed), "apiProductionAllowed": bool(api_production_allowed), "frontendProductionAllowed": bool(frontend_production_allowed), "approvalExecutionAllowed": bool(approval_execution_allowed), "pushAllowed": bool(push_allowed), "tagAllowed": bool(tag_allowed), "customerIdentifierLeakageAllowed": bool(customer_identifier_leakage_allowed)})


def build_next_phase_plan(*, phase_key: str, title: str, allowed: bool, allowed_scope: Sequence[str], blocked_scope: Sequence[str], prerequisite_artifact_keys: Sequence[str]) -> dict[str, Any]:
    return _digest_item({"planId": sha256_digest({"phaseKey": phase_key}), "phaseKey": phase_key, "title": title, "allowed": bool(allowed), "allowedScope": list(allowed_scope), "blockedScope": list(blocked_scope), "prerequisiteArtifactKeys": list(prerequisite_artifact_keys)})


def build_release_metadata(*, active_head_reference: str, branch: str, package_artifact_path: str, release_gate_artifact_path: str, release_package_decision: str, release_candidate_allowed: bool, push_allowed: bool, tag_allowed: bool) -> dict[str, Any]:
    return _digest_item({"metadataId": sha256_digest({"activeHeadReference": active_head_reference, "packageArtifactPath": package_artifact_path}), "activeHeadReference": active_head_reference, "branch": branch, "packageArtifactPath": package_artifact_path, "releaseGateArtifactPath": release_gate_artifact_path, "releasePackageDecision": release_package_decision, "releaseCandidateAllowed": bool(release_candidate_allowed), "pushAllowed": bool(push_allowed), "tagAllowed": bool(tag_allowed)})


def build_handoff_gate(*, gate_id: str, gate_name: str, status: str, severity: str, blocking: bool, reason_codes: Sequence[str]) -> dict[str, Any]:
    return _digest_item({"gateId": gate_id, "gateName": gate_name, "status": status, "severity": severity, "blocking": bool(blocking), "reasonCodes": sorted(str(code) for code in reason_codes)})


def build_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    return _digest_item({"artifactType": artifact_type, "path": path, "digest": digest})


def build_international_ga_handoff_notes(*, handoff_notes_id: str, authority: str, profile_id: str, implementation_status: str, readiness_outcome: str, summary: Mapping[str, Any], release_notes: Mapping[str, Any], stakeholder_handoff_sections: Sequence[Mapping[str, Any]], engineering_handoff_sections: Sequence[Mapping[str, Any]], validation_command_set: Sequence[Mapping[str, Any]], known_warnings: Sequence[Mapping[str, Any]], boundary_statement: Mapping[str, Any], next_phase_plan: Sequence[Mapping[str, Any]], release_metadata: Mapping[str, Any], handoff_gates: Sequence[Mapping[str, Any]], source_artifact_references: Sequence[Mapping[str, Any]], generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP") -> dict[str, Any]:
    notes = {"handoffNotesId": handoff_notes_id, "contractVersion": CONTRACT_VERSION, "authority": authority, "profileId": profile_id, "implementationStatus": implementation_status, "readinessOutcome": readiness_outcome, "summary": dict(summary), "releaseNotes": dict(release_notes), "stakeholderHandoffSections": list(stakeholder_handoff_sections), "engineeringHandoffSections": list(engineering_handoff_sections), "validationCommandSet": list(validation_command_set), "knownWarnings": list(known_warnings), "boundaryStatement": dict(boundary_statement), "nextPhasePlan": list(next_phase_plan), "releaseMetadata": dict(release_metadata), "handoffGates": list(handoff_gates), "sourceArtifactReferences": list(source_artifact_references), "generatedAtPolicy": generated_at_policy}
    notes["deterministicDigest"] = sha256_digest({k: v for k, v in notes.items() if k != "deterministicDigest"})
    return notes
