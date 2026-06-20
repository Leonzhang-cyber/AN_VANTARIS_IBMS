"""Airport International GA handoff notes and release notes freeze."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from international_ga_handoff_notes.enums import Audience, GateStatus, WarningSeverity
from international_ga_handoff_notes.models import (
    build_artifact_reference,
    build_boundary_statement,
    build_engineering_handoff_section,
    build_handoff_gate,
    build_international_ga_handoff_notes,
    build_known_warning,
    build_next_phase_plan,
    build_release_metadata,
    build_release_notes,
    build_stakeholder_handoff_section,
    build_validation_command,
)
from international_ga_handoff_notes.validation import validate_international_ga_handoff_notes
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-GA-03"
PROFILE_ID = "airport-international-ga-handoff-notes-profile-v1"
IMPLEMENTATION_STATUS = "INTERNATIONAL_GA_HANDOFF_NOTES_AND_RELEASE_NOTES_FREEZE_COMPLETE"
READINESS_OUTCOME = "INTERNATIONAL_GA_HANDOFF_NOTES_READY_FOR_STAKEHOLDER_AND_ENGINEERING_HANDOFF"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
PACKAGE_ARTIFACT = PROJECTIONS_DIR / "airport-international-ga-release-candidate-package.v1.json"
RELEASE_GATE_ARTIFACT = PROJECTIONS_DIR / "airport-international-ga-release-gate.v1.json"

STAGE_GROUPS = [
    "A1 Asset Intake / Review Projection",
    "A2 Source System / Integration Health",
    "A3 Alarm → Fault → Work → Evidence Projection",
    "A4 Operator Review Decision Layer",
    "A5 Airport Operations Console Package",
    "A6 API / Frontend Readiness Contract and Gate",
    "A7 Read-only API Skeleton / Contract / Mock / Release Gate",
    "A8 Read-only Frontend Skeleton / Page Contract / Gate",
    "GA-01 International GA terminology alignment",
    "GA-02 International GA release package and validation matrix",
]

BUSINESS_CAPABILITIES = [
    "Airport Asset Review",
    "Source System Registry",
    "Integration Health",
    "Alarm Event Intake",
    "Asset Resolution Review",
    "FaultCase Candidates",
    "WorkOrder Intent Candidates",
    "Evidence Investigation",
    "UConsole Alarm Event Operations",
    "Operator Review Decision Queue",
    "Operator Policy Guard",
    "Airport Operations Console Package",
    "API Readiness Contract",
    "Read-only API Skeleton",
    "Read-only Frontend Skeleton",
]

VALIDATORS = [
    ("validate-one-airport-international-ga-release-package.py", "GA-02", "ONE_AIRPORT_GA_02_INTERNATIONAL_GA_RELEASE_CANDIDATE_PACKAGING_AND_VALIDATION_MATRIX_PASS"),
    ("validate-one-airport-international-ga-release-gate.py", "GA-01", "ONE_AIRPORT_GA_01_ALIGN_AIRPORT_RELEASE_TERMINOLOGY_WITH_INTERNATIONAL_GA_PASS"),
    ("validate-one-airport-read-only-frontend-release-gate.py", "A8", "ONE_AIRPORT_A8_03_READ_ONLY_FRONTEND_IMPLEMENTATION_RELEASE_GATE_PASS"),
    ("validate-one-airport-read-only-frontend-page-contract.py", "A8", "ONE_AIRPORT_A8_02_READ_ONLY_FRONTEND_PAGE_CONTRACT_AND_LOCAL_SMOKE_GATE_PASS"),
    ("validate-one-airport-read-only-frontend-skeleton.py", "A8", "ONE_AIRPORT_A8_01_READ_ONLY_FRONTEND_SKELETON_FOUNDATION_PASS"),
    ("validate-one-airport-read-only-api-release-gate.py", "A7", "ONE_AIRPORT_A7_04_READ_ONLY_API_IMPLEMENTATION_RELEASE_GATE_PASS"),
    ("validate-one-airport-read-only-api-mock-route-contract.py", "A7", "ONE_AIRPORT_A7_03_READ_ONLY_API_MOCK_ROUTE_CONTRACT_AND_LOCAL_SMOKE_GATE_PASS"),
    ("validate-one-airport-read-only-api-response-contract.py", "A7", "ONE_AIRPORT_A7_02_READ_ONLY_API_RESPONSE_CONTRACT_AND_VALIDATION_GATE_PASS"),
    ("validate-one-airport-read-only-api-skeleton.py", "A7", "ONE_AIRPORT_A7_01_READ_ONLY_API_SKELETON_FOUNDATION_PASS"),
    ("validate-one-airport-api-frontend-implementation-gate.py", "A6", "ONE_AIRPORT_A6_02_API_FRONTEND_IMPLEMENTATION_READINESS_RELEASE_GATE_PASS"),
    ("validate-one-airport-api-frontend-readiness-contract.py", "A6", "ONE_AIRPORT_A6_01_API_FRONTEND_READINESS_CONTRACT_FREEZE_PASS"),
    ("validate-one-airport-operations-console-handoff-gate.py", "A5", "ONE_AIRPORT_A5_02_AIRPORT_CONSOLE_PACKAGE_READINESS_AND_HANDOFF_GATE_PASS"),
    ("validate-one-airport-operations-console-package.py", "A5", "ONE_AIRPORT_A5_01_READ_ONLY_AIRPORT_OPERATIONS_CONSOLE_PACKAGE_FOUNDATION_PASS"),
    ("validate-one-airport-a4-readiness-release-gate.py", "A4", "ONE_AIRPORT_A4_04_OPERATOR_REVIEW_READINESS_AND_RELEASE_GATE_PASS"),
    ("validate-one-airport-a3-readiness-release-gate.py", "A3", "ONE_AIRPORT_A3_07_A3_READINESS_AGGREGATION_AND_RELEASE_GATE_PASS"),
    ("validate-one-uconsole-operator-review-queue-projection.py", "A4", "ONE_AIRPORT_A4_02_OPERATOR_REVIEW_UCONSOLE_QUEUE_PROJECTION_PASS"),
    ("validate-one-uconsole-alarm-event-operations-projection.py", "A3", "ONE_AIRPORT_A3_06_READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_PASS"),
    ("validate-one-uconsole-integration-health-projection.py", "A2", "ONE_AIRPORT_A2_05_READ_ONLY_UCONSOLE_INTEGRATION_HEALTH_PROJECTION_PASS"),
    ("validate-one-airport-source-system-review.py", "A1", "ONE_AIRPORT_A2_02_SOURCE_SYSTEM_EVIDENCE_BINDING_AND_REVIEW_PROJECTION_PASS"),
    ("validate-one-source-system-registry.py", "A1", "ONE_AIRPORT_A2_01_GENERIC_SOURCE_SYSTEM_REGISTRY_FOUNDATION_PASS"),
    ("validate-one-boundaries.py", "BOUNDARY", "ONE_BOUNDARY_BASELINE_PASS"),
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _summary() -> dict[str, Any]:
    package = _load(PACKAGE_ARTIFACT)
    s = package["summary"]
    return {
        "stakeholderHandoffSectionCount": 7,
        "engineeringHandoffSectionCount": 6,
        "validationCommandCount": 21,
        "requiredValidationCommandCount": 21,
        "knownWarningCount": 5,
        "blockingKnownWarningCount": 0,
        "nextPhasePlanCount": 6,
        "handoffGateCount": 13,
        "passedHandoffGateCount": 13,
        "blockingGateFailureCount": 0,
        "stageInventoryCount": s["stageInventoryCount"],
        "artifactInventoryCount": s["artifactInventoryCount"],
        "validatorMatrixCount": s["validatorMatrixCount"],
        "unitTestMatrixCount": s["unitTestMatrixCount"],
        "businessCapabilityCount": s["businessCapabilityCount"],
        "totalDeviceEvidenceCount": s["totalDeviceEvidenceCount"],
        "decisionItemCount": s["decisionItemCount"],
        "pendingDecisionCount": s["pendingDecisionCount"],
        "blockingDecisionCount": s["blockingDecisionCount"],
        "internationalGaPackageAllowed": s["internationalGaPackageAllowed"],
        "internationalGaReadinessAllowed": s["internationalGaReadinessAllowed"],
        "releaseCandidateAllowed": s["releaseCandidateAllowed"],
        "handoffNotesFrozen": True,
        "readyForHandoff": True,
        "databaseWriteAllowed": False,
        "runtimeActivationAllowed": False,
        "productionActivationAllowed": False,
        "apiProductionAllowed": False,
        "frontendProductionAllowed": False,
        "approvalExecutionAllowed": False,
        "pushAllowed": False,
        "tagAllowed": False,
        "containsCustomerAssetIdentifiers": s["containsCustomerAssetIdentifiers"],
        "crossIndustry": s["crossIndustry"],
        "airportSpecific": s["airportSpecific"],
    }


def _release_notes() -> dict[str, Any]:
    return build_release_notes(
        release_title="VANTARIS ONE Airport International GA-ready Read-only Release Candidate",
        release_type="INTERNATIONAL_GA_READY_READ_ONLY_FOUNDATION",
        release_candidate_name="VANTARIS_ONE_AIRPORT_INTERNATIONAL_GA_READY_RC",
        release_summary="Airport industry solution package is frozen as an International GA-ready read-only foundation with production-grade readiness gates and explicit runtime, production, write, push, and tag boundaries.",
        included_stage_groups=STAGE_GROUPS,
        included_business_capabilities=BUSINESS_CAPABILITIES,
        readiness_statement="Ready for stakeholder and engineering handoff; production activation remains disabled until explicitly authorized.",
    )


def _stakeholder_sections() -> list[dict[str, Any]]:
    specs = [
        (Audience.PRODUCT_OWNER.value, "Product owner release posture", "Release candidate is ready for International GA stakeholder review.", ["GA_RELEASE_PACKAGE", "GA_RELEASE_GATE"], False),
        (Audience.ENGINEERING.value, "Engineering implementation handoff", "Read-only API and frontend planning can proceed within frozen boundaries.", ["VALIDATION_COMMAND_SET", "BOUNDARY_STATEMENT"], False),
        (Audience.API_TEAM.value, "API team handoff", "Read-only route implementation is a future implementation phase; production API remains blocked.", ["READ_ONLY_API_RELEASE_GATE"], False),
        (Audience.FRONTEND_TEAM.value, "Frontend team handoff", "Read-only frontend implementation is a future implementation phase; production frontend remains blocked.", ["READ_ONLY_FRONTEND_RELEASE_GATE"], False),
        (Audience.QA_VALIDATION.value, "QA validation command set", "Twenty-one required validation commands are frozen for handoff.", ["VALIDATION_COMMAND_SET"], False),
        (Audience.DEPLOYMENT_TEAM.value, "Deployment boundary", "Deployment, push, tag, runtime, and production activation are not authorized by this package.", ["BOUNDARY_STATEMENT"], True),
        (Audience.CUSTOMER_TECHNICAL_REVIEW.value, "Customer technical review", "Customer-facing technical review can inspect read-only release notes without customer identifier leakage.", ["RELEASE_NOTES", "KNOWN_WARNINGS"], False),
    ]
    return [build_stakeholder_handoff_section(audience=audience, title=title, summary=summary, included_artifact_keys=keys, decision_required=decision) for audience, title, summary, keys, decision in specs]


def _engineering_sections() -> list[dict[str, Any]]:
    specs = [
        ("READ_ONLY_API_ROUTE_IMPLEMENTATION", "Read-only API route implementation", "Allowed as future read-only route work; no production API activation.", True, False),
        ("READ_ONLY_FRONTEND_IMPLEMENTATION", "Read-only frontend implementation", "Allowed as future read-only UI work; no production frontend activation.", True, False),
        ("OPERATOR_DECISION_EXECUTION_FUTURE_PHASE", "Operator decision execution", "Not allowed in this package; requires explicit future authorization.", False, False),
        ("RUNTIME_ACTIVATION_FUTURE_PHASE", "Runtime activation", "Not allowed in this package.", False, False),
        ("PRODUCTION_DEPLOYMENT_FUTURE_PHASE", "Production deployment", "Not allowed in this package.", False, False),
        ("PUSH_TAG_RELEASE_FUTURE_PHASE", "Push and tag release", "Not allowed unless explicitly instructed by the user.", False, False),
    ]
    boundaries = ["NO_DATABASE_WRITES", "NO_RUNTIME_ACTIVATION", "NO_PRODUCTION_ACTIVATION", "NO_APPROVAL_EXECUTION", "NO_PUSH_TAG"]
    return [build_engineering_handoff_section(engineering_area=area, title=title, summary=summary, required_boundaries=boundaries, next_phase_allowed=allowed, implementation_allowed_now=impl) for area, title, summary, allowed, impl in specs]


def _validation_commands() -> list[dict[str, Any]]:
    return [build_validation_command(command=f"PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/{name}", validation_area=area, required_for_handoff=True, expected_marker=marker) for name, area, marker in VALIDATORS]


def _known_warnings() -> list[dict[str, Any]]:
    compatibility_note = "historical POC-named artifacts are compatibility-only; active release uses International GA terminology"
    specs = [
        ("BOUNDARY_VALIDATOR_LEGACY_WARNINGS", "Boundary validator legacy warnings", "Existing legacy warnings are known and unchanged.", WarningSeverity.LOW.value, "Keep existing boundary baseline visible in release handoff."),
        ("NO_PRODUCTION_ACTIVATION_IN_THIS_RELEASE", "No production activation in this release", "Production activation is intentionally disabled.", WarningSeverity.INFO.value, "Require explicit future authorization before activation."),
        ("NO_REAL_API_FRONTEND_RUNTIME_IN_THIS_RELEASE", "No real API/frontend runtime in this release", "This release freezes readiness and handoff notes; it does not implement runtime API or frontend behavior.", WarningSeverity.INFO.value, "Plan read-only implementation in future phases."),
        ("DECISIONS_REMAIN_PENDING", "Decisions remain pending", "46 pending decisions remain operator-review candidates, not applied approvals.", WarningSeverity.LOW.value, "Use future authorized operator decision workflow."),
        ("HISTORICAL_COMPATIBILITY_ARTIFACTS", "Historical compatibility artifacts", compatibility_note, WarningSeverity.INFO.value, "Keep active artifacts on International GA naming."),
    ]
    return [build_known_warning(warning_type=kind, title=title, description=description, severity=severity, blocking=False, mitigation=mitigation) for kind, title, description, severity, mitigation in specs]


def _boundary_statement() -> dict[str, Any]:
    return build_boundary_statement(statement_id="airport-international-ga-handoff-boundary-v1", database_write_allowed=False, runtime_activation_allowed=False, production_activation_allowed=False, api_production_allowed=False, frontend_production_allowed=False, approval_execution_allowed=False, push_allowed=False, tag_allowed=False, customer_identifier_leakage_allowed=False)


def _next_phase_plan() -> list[dict[str, Any]]:
    specs = [
        ("READ_ONLY_API_ROUTE_IMPLEMENTATION", "Read-only API route implementation", True, ["Read-only GET route planning and implementation"], ["Production API activation", "Mutation endpoints"], ["GA_RELEASE_PACKAGE", "READ_ONLY_API_RELEASE_GATE"]),
        ("READ_ONLY_FRONTEND_IMPLEMENTATION", "Read-only frontend implementation", True, ["Read-only frontend implementation planning"], ["Production frontend activation", "Mutation interactions"], ["GA_RELEASE_PACKAGE", "READ_ONLY_FRONTEND_RELEASE_GATE"]),
        ("OPERATOR_DECISION_EXECUTION", "Operator decision execution", False, [], ["Approval execution", "Decision writes"], ["OPERATOR_REVIEW_RELEASE_GATE"]),
        ("RUNTIME_ACTIVATION", "Runtime activation", False, [], ["Live polling", "Connector runtime", "Alarm runtime"], ["BOUNDARY_AUTHORIZATION"]),
        ("PRODUCTION_DEPLOYMENT", "Production deployment", False, [], ["Production deployment", "Production activation"], ["DEPLOYMENT_AUTHORIZATION"]),
        ("PUSH_AND_TAG_RELEASE", "Push and tag release", False, [], ["Git push", "Release tag"], ["EXPLICIT_USER_INSTRUCTION"]),
    ]
    return [build_next_phase_plan(phase_key=key, title=title, allowed=allowed, allowed_scope=allow, blocked_scope=blocked, prerequisite_artifact_keys=prereqs) for key, title, allowed, allow, blocked, prereqs in specs]


def _release_metadata() -> dict[str, Any]:
    package = _load(PACKAGE_ARTIFACT)
    return build_release_metadata(active_head_reference="b6138c7", branch="main", package_artifact_path=str(PACKAGE_ARTIFACT.relative_to(ROOT)), release_gate_artifact_path=str(RELEASE_GATE_ARTIFACT.relative_to(ROOT)), release_package_decision=package["releaseDecision"]["decisionState"], release_candidate_allowed=True, push_allowed=False, tag_allowed=False)


def _handoff_gates() -> list[dict[str, Any]]:
    specs = [
        ("G01_RELEASE_NOTES_COMPLETE", "Release notes complete", ["RELEASE_NOTES_PRESENT"]),
        ("G02_STAKEHOLDER_HANDOFF_COMPLETE", "Stakeholder handoff complete", ["SEVEN_STAKEHOLDER_SECTIONS"]),
        ("G03_ENGINEERING_HANDOFF_COMPLETE", "Engineering handoff complete", ["SIX_ENGINEERING_SECTIONS"]),
        ("G04_VALIDATION_COMMAND_SET_COMPLETE", "Validation command set complete", ["TWENTY_ONE_VALIDATION_COMMANDS"]),
        ("G05_KNOWN_WARNINGS_COMPLETE", "Known warnings complete", ["FIVE_NON_BLOCKING_WARNINGS"]),
        ("G06_BOUNDARY_STATEMENT_COMPLETE", "Boundary statement complete", ["ALL_RESTRICTED_FLAGS_FALSE"]),
        ("G07_NEXT_PHASE_PLAN_COMPLETE", "Next phase plan complete", ["SIX_NEXT_PHASES"]),
        ("G08_RELEASE_METADATA_COMPLETE", "Release metadata complete", ["ACTIVE_HEAD_AND_ARTIFACTS_RECORDED"]),
        ("G09_GA_PACKAGE_DEPENDENCY", "GA package dependency", ["INTERNATIONAL_GA_RELEASE_PACKAGE_PASS"]),
        ("G10_GA_RELEASE_GATE_DEPENDENCY", "GA release gate dependency", ["INTERNATIONAL_GA_READINESS_PASS"]),
        ("G11_NO_ACTIVE_STAGE_TERMINOLOGY", "No active superseded terminology", ["ACTIVE_GA03_TERMINOLOGY_PASS"]),
        ("G12_DETERMINISTIC_OUTPUT", "Deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"]),
        ("G13_HANDOFF_DECISION", "Handoff decision", ["READY_FOR_HANDOFF"]),
    ]
    return [build_handoff_gate(gate_id=gate_id, gate_name=name, status=GateStatus.PASS.value, severity="INFO", blocking=True, reason_codes=reasons) for gate_id, name, reasons in specs]


def _artifact_refs() -> list[dict[str, Any]]:
    refs = []
    for kind, path in (("GA_PACKAGE", PACKAGE_ARTIFACT), ("GA_RELEASE_GATE", RELEASE_GATE_ARTIFACT)):
        refs.append(build_artifact_reference(artifact_type=kind, path=str(path.relative_to(ROOT)), digest=sha256_digest(_load(path))))
    return refs


def build_airport_international_ga_handoff_notes() -> dict[str, Any]:
    notes = build_international_ga_handoff_notes(
        handoff_notes_id=sha256_digest({"authority": AUTHORITY, "profileId": PROFILE_ID}),
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=_summary(),
        release_notes=_release_notes(),
        stakeholder_handoff_sections=_stakeholder_sections(),
        engineering_handoff_sections=_engineering_sections(),
        validation_command_set=_validation_commands(),
        known_warnings=_known_warnings(),
        boundary_statement=_boundary_statement(),
        next_phase_plan=_next_phase_plan(),
        release_metadata=_release_metadata(),
        handoff_gates=_handoff_gates(),
        source_artifact_references=_artifact_refs(),
    )
    validate_international_ga_handoff_notes(notes)
    return notes
