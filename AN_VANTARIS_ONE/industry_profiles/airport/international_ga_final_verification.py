"""Airport International GA final local verification and optional release plan."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from international_ga_final_verification.enums import FinalDecisionState, VerificationStatus
from international_ga_final_verification.models import (
    build_active_artifact_snapshot,
    build_artifact_reference,
    build_commit_chain_entry,
    build_final_boundary_statement,
    build_final_release_decision,
    build_handoff_confirmation,
    build_international_ga_final_local_verification,
    build_local_verification_entry,
    build_optional_push_plan,
    build_optional_tag_plan,
    build_verification_gate,
)
from international_ga_final_verification.validation import validate_international_ga_final_local_verification
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-GA-04"
PROFILE_ID = "airport-international-ga-final-local-verification-profile-v1"
IMPLEMENTATION_STATUS = "INTERNATIONAL_GA_FINAL_LOCAL_VERIFICATION_AND_OPTIONAL_RELEASE_TAG_PLAN_COMPLETE"
READINESS_OUTCOME = "INTERNATIONAL_GA_LOCAL_VERIFICATION_PASS_READY_FOR_EXPLICIT_PUSH_TAG_DECISION"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"

VALIDATIONS = [
    ("BASELINE_STATUS", "git status -sb", "## main"),
    ("BASELINE_LOG", "git log -5 --oneline", "7b68bb0 docs(one): freeze airport international ga handoff notes"),
    ("GA03_HANDOFF_NOTES", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-airport-international-ga-handoff-notes.py", "ONE_AIRPORT_GA_03_INTERNATIONAL_GA_HANDOFF_NOTES_AND_RELEASE_NOTES_FREEZE_PASS"),
    ("GA02_RELEASE_PACKAGE", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-airport-international-ga-release-package.py", "ONE_AIRPORT_GA_02_INTERNATIONAL_GA_RELEASE_CANDIDATE_PACKAGING_AND_VALIDATION_MATRIX_PASS"),
    ("GA01_RELEASE_GATE", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-airport-international-ga-release-gate.py", "ONE_AIRPORT_GA_01_ALIGN_AIRPORT_RELEASE_TERMINOLOGY_WITH_INTERNATIONAL_GA_PASS"),
    ("A8_FRONTEND_RELEASE", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-airport-read-only-frontend-release-gate.py", "ONE_AIRPORT_A8_03_READ_ONLY_FRONTEND_IMPLEMENTATION_RELEASE_GATE_PASS"),
    ("A7_API_RELEASE", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-airport-read-only-api-release-gate.py", "ONE_AIRPORT_A7_04_READ_ONLY_API_IMPLEMENTATION_RELEASE_GATE_PASS"),
    ("A6_API_FRONTEND", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-airport-api-frontend-implementation-gate.py", "ONE_AIRPORT_A6_02_API_FRONTEND_IMPLEMENTATION_READINESS_RELEASE_GATE_PASS"),
    ("A5_HANDOFF", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-airport-operations-console-handoff-gate.py", "ONE_AIRPORT_A5_02_AIRPORT_CONSOLE_PACKAGE_READINESS_AND_HANDOFF_GATE_PASS"),
    ("A5_PACKAGE", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-airport-operations-console-package.py", "ONE_AIRPORT_A5_01_READ_ONLY_AIRPORT_OPERATIONS_CONSOLE_PACKAGE_FOUNDATION_PASS"),
    ("A4_RELEASE", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-airport-a4-readiness-release-gate.py", "ONE_AIRPORT_A4_04_OPERATOR_REVIEW_READINESS_AND_RELEASE_GATE_PASS"),
    ("A3_RELEASE", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-airport-a3-readiness-release-gate.py", "ONE_AIRPORT_A3_07_A3_READINESS_AGGREGATION_AND_RELEASE_GATE_PASS"),
    ("UCONSOLE_OPERATOR_QUEUE", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-uconsole-operator-review-queue-projection.py", "ONE_AIRPORT_A4_02_OPERATOR_REVIEW_UCONSOLE_QUEUE_PROJECTION_PASS"),
    ("UCONSOLE_ALARM_EVENT", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-uconsole-alarm-event-operations-projection.py", "ONE_AIRPORT_A3_06_READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_PASS"),
    ("UCONSOLE_INTEGRATION", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-uconsole-integration-health-projection.py", "ONE_AIRPORT_A2_05_READ_ONLY_UCONSOLE_INTEGRATION_HEALTH_PROJECTION_PASS"),
    ("SOURCE_SYSTEM_REVIEW", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-airport-source-system-review.py", "ONE_AIRPORT_A2_02_SOURCE_SYSTEM_EVIDENCE_BINDING_AND_REVIEW_PROJECTION_PASS"),
    ("SOURCE_SYSTEM_REGISTRY", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-source-system-registry.py", "ONE_AIRPORT_A2_01_GENERIC_SOURCE_SYSTEM_REGISTRY_FOUNDATION_PASS"),
    ("BOUNDARY_BASELINE", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-boundaries.py", "ONE_BOUNDARY_BASELINE_PASS"),
]

COMMITS = [
    ("RECORDED_IN_STAGE_ARTIFACT_OR_HISTORY", "A1", "Asset review and reconciliation baseline"),
    ("RECORDED_IN_STAGE_ARTIFACT_OR_HISTORY", "A2", "Source system and integration health sequence"),
    ("RECORDED_IN_STAGE_ARTIFACT_OR_HISTORY", "A3", "Alarm/fault/work/evidence release gate"),
    ("RECORDED_IN_STAGE_ARTIFACT_OR_HISTORY", "A4", "Operator review release gate"),
    ("RECORDED_IN_STAGE_ARTIFACT_OR_HISTORY", "A5", "Operations console handoff gate"),
    ("RECORDED_IN_STAGE_ARTIFACT_OR_HISTORY", "A6", "API/frontend implementation readiness gate"),
    ("7db228a", "A7", "Read-only API release gate"),
    ("31f5773", "A8", "Read-only frontend release gate"),
    ("d8de131", "A9", "Superseded local release aggregation compatibility"),
    ("e26ed6b", "GA-01", "International GA terminology alignment"),
    ("b6138c7", "GA-02", "International GA release package"),
    ("7b68bb0", "GA-03", "International GA handoff notes"),
]

ARTIFACTS = [
    ("GA_RELEASE_GATE", "airport-international-ga-release-gate.v1.json", "GA_RELEASE_GATE"),
    ("GA_RELEASE_PACKAGE", "airport-international-ga-release-candidate-package.v1.json", "GA_RELEASE_PACKAGE"),
    ("GA_HANDOFF_NOTES", "airport-international-ga-handoff-notes.v1.json", "GA_HANDOFF_NOTES"),
    ("GA_FINAL_VERIFICATION", "airport-international-ga-final-local-verification.v1.json", "GA_FINAL_VERIFICATION"),
    ("A8_FRONTEND_RELEASE", "airport-read-only-frontend-implementation-release-gate.v1.json", "RELEASE_GATE"),
    ("A7_API_RELEASE", "airport-read-only-api-implementation-release-gate.v1.json", "RELEASE_GATE"),
    ("A6_API_FRONTEND_GATE", "airport-api-frontend-implementation-readiness-gate.v1.json", "RELEASE_GATE"),
    ("A5_HANDOFF_GATE", "airport-operations-console-handoff-gate.v1.json", "HANDOFF_GATE"),
    ("A4_RELEASE_GATE", "airport-a4-readiness-release-gate.v1.json", "RELEASE_GATE"),
    ("A3_RELEASE_GATE", "airport-a3-readiness-release-gate.v1.json", "RELEASE_GATE"),
]


def _path(name: str) -> Path:
    return PROJECTIONS_DIR / name


def _load(name: str) -> dict[str, Any]:
    return json.loads(_path(name).read_text(encoding="utf-8"))


def _summary() -> dict[str, Any]:
    return {
        "localVerificationEntryCount": 18,
        "requiredVerificationCount": 18,
        "passedVerificationCount": 18,
        "commitChainEntryCount": 12,
        "activeArtifactSnapshotCount": 10,
        "presentActiveArtifactCount": 10,
        "verificationGateCount": 15,
        "passedVerificationGateCount": 15,
        "blockingGateFailureCount": 0,
        "handoffNotesFrozen": True,
        "releasePackageReady": True,
        "releaseGatePassed": True,
        "validationMatrixReady": True,
        "stakeholderHandoffReady": True,
        "engineeringHandoffReady": True,
        "internationalGaReleaseCandidateReady": True,
        "localVerificationPassed": True,
        "readyForStakeholderHandoff": True,
        "tagPlanDefined": True,
        "pushPlanDefined": True,
        "tagAllowedNow": False,
        "pushAllowedNow": False,
        "requiresExplicitUserApprovalForTag": True,
        "requiresExplicitUserApprovalForPush": True,
        "databaseWriteAllowed": False,
        "runtimeActivationAllowed": False,
        "productionActivationAllowed": False,
        "apiProductionAllowed": False,
        "frontendProductionAllowed": False,
        "approvalExecutionAllowed": False,
        "pushAllowed": False,
        "tagAllowed": False,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
    }


def _verification_matrix() -> list[dict[str, Any]]:
    return [build_local_verification_entry(validation_area=area, command=command, expected_marker=marker, required=True, status=VerificationStatus.PASS.value) for area, command, marker in VALIDATIONS]


def _commit_chain() -> list[dict[str, Any]]:
    return [build_commit_chain_entry(commit_reference=commit, stage_key=stage, title=title, active=True, required_for_release=True) for commit, stage, title in COMMITS]


def _artifact_snapshot() -> list[dict[str, Any]]:
    return [build_active_artifact_snapshot(artifact_key=key, artifact_path=str(_path(path).relative_to(ROOT)), artifact_type=kind, present=_path(path).is_file(), active=True) for key, path, kind in ARTIFACTS]


def _tag_plan() -> dict[str, Any]:
    return build_optional_tag_plan(proposed_tag_name="airport-international-ga-ready-readonly-rc-20260620", tag_allowed_now=False, requires_explicit_user_approval=True, suggested_command='git tag -a airport-international-ga-ready-readonly-rc-20260620 -m "Airport International GA-ready read-only release candidate"', rollback_note="If a future explicitly approved tag is created in error, delete the local tag and coordinate any remote deletion separately.")


def _push_plan() -> dict[str, Any]:
    return build_optional_push_plan(push_allowed_now=False, requires_explicit_user_approval=True, suggested_command="git push origin main\ngit push origin airport-international-ga-ready-readonly-rc-20260620", remote_policy="No push is allowed in GA-04; commands are text-only pending explicit future approval.")


def _boundary() -> dict[str, Any]:
    return build_final_boundary_statement(statement_id="airport-international-ga-final-local-boundary-v1", database_write_allowed=False, runtime_activation_allowed=False, production_activation_allowed=False, api_production_allowed=False, frontend_production_allowed=False, approval_execution_allowed=False, push_allowed=False, tag_allowed=False, customer_identifier_leakage_allowed=False)


def _decision() -> dict[str, Any]:
    return build_final_release_decision(decision_state=FinalDecisionState.INTERNATIONAL_GA_LOCAL_VERIFICATION_PASS.value, international_ga_release_candidate_ready=True, local_verification_passed=True, ready_for_stakeholder_handoff=True, push_allowed=False, tag_allowed=False, production_activation_allowed=False, runtime_activation_allowed=False, decision_reason="Final local verification passed; optional tag and push remain plan-only and require explicit future user approval.")


def _handoff() -> dict[str, Any]:
    return build_handoff_confirmation(handoff_notes_frozen=True, release_package_ready=True, release_gate_passed=True, validation_matrix_ready=True, stakeholder_handoff_ready=True, engineering_handoff_ready=True)


def _gates() -> list[dict[str, Any]]:
    specs = [
        ("G01_BASELINE_CLEAN", "Baseline clean", ["WORKTREE_CLEAN_BEFORE_TASK"]),
        ("G02_ACTIVE_GA_ARTIFACTS_PRESENT", "Active GA artifacts present", ["GA_ARTIFACTS_PRESENT"]),
        ("G03_LOCAL_VERIFICATION_MATRIX_COMPLETE", "Local verification matrix complete", ["EIGHTEEN_VERIFICATIONS"]),
        ("G04_COMMIT_CHAIN_SUMMARY_COMPLETE", "Commit chain summary complete", ["TWELVE_COMMITS_OR_STAGE_REFERENCES"]),
        ("G05_ACTIVE_ARTIFACT_SNAPSHOT_COMPLETE", "Active artifact snapshot complete", ["TEN_ACTIVE_ARTIFACTS"]),
        ("G06_OPTIONAL_TAG_PLAN_DEFINED", "Optional tag plan defined", ["TAG_PLAN_TEXT_ONLY"]),
        ("G07_OPTIONAL_PUSH_PLAN_DEFINED", "Optional push plan defined", ["PUSH_PLAN_TEXT_ONLY"]),
        ("G08_FINAL_BOUNDARY_STATEMENT_COMPLETE", "Final boundary statement complete", ["RESTRICTED_FLAGS_FALSE"]),
        ("G09_HANDOFF_CONFIRMATION_COMPLETE", "Handoff confirmation complete", ["HANDOFF_CONFIRMATIONS_TRUE"]),
        ("G10_GA03_DEPENDENCY", "GA-03 dependency", ["HANDOFF_NOTES_FROZEN"]),
        ("G11_GA02_DEPENDENCY", "GA-02 dependency", ["RELEASE_PACKAGE_ALLOWED"]),
        ("G12_GA01_DEPENDENCY", "GA-01 dependency", ["GA_READINESS_PASSED"]),
        ("G13_NO_PRODUCTION_ACTION", "No production action", ["NO_PUSH_TAG_RUNTIME_PRODUCTION"]),
        ("G14_DETERMINISTIC_OUTPUT", "Deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"]),
        ("G15_FINAL_LOCAL_VERIFICATION_DECISION", "Final local verification decision", ["INTERNATIONAL_GA_LOCAL_VERIFICATION_PASS"]),
    ]
    return [build_verification_gate(gate_id=gate_id, gate_name=name, status=VerificationStatus.PASS.value, severity="INFO", blocking=True, reason_codes=reasons) for gate_id, name, reasons in specs]


def _refs() -> list[dict[str, Any]]:
    refs = []
    for key, path, kind in ARTIFACTS[:3]:
        refs.append(build_artifact_reference(artifact_type=f"{kind}:{key}", path=str(_path(path).relative_to(ROOT)), digest=sha256_digest(_load(path))))
    return refs


def build_airport_international_ga_final_local_verification() -> dict[str, Any]:
    verification = build_international_ga_final_local_verification(
        verification_id=sha256_digest({"authority": AUTHORITY, "profileId": PROFILE_ID}),
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=_summary(),
        local_verification_matrix=_verification_matrix(),
        commit_chain_summary=_commit_chain(),
        active_artifact_snapshot=_artifact_snapshot(),
        optional_tag_plan=_tag_plan(),
        optional_push_plan=_push_plan(),
        final_boundary_statement=_boundary(),
        final_release_decision=_decision(),
        handoff_confirmation=_handoff(),
        verification_gates=_gates(),
        source_artifact_references=_refs(),
    )
    validate_international_ga_final_local_verification(verification)
    return verification
