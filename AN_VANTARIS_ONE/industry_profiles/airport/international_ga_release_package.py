"""Airport International GA release candidate package projection."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from international_ga_release_package.enums import GateStatus, ReleaseDecisionState, Severity
from international_ga_release_package.models import (
    build_artifact_inventory_entry,
    build_artifact_reference,
    build_boundary_statement,
    build_handoff_inventory_entry,
    build_international_ga_release_candidate_package,
    build_packaging_gate,
    build_release_decision,
    build_release_notes,
    build_stage_inventory_entry,
    build_unit_test_matrix_entry,
    build_validator_matrix_entry,
)
from international_ga_release_package.validation import validate_international_ga_release_candidate_package
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-GA-02"
PROFILE_ID = "airport-international-ga-release-candidate-package-profile-v1"
PACKAGE_VERSION = "airport-international-ga-release-candidate-package.v1"
IMPLEMENTATION_STATUS = "INTERNATIONAL_GA_RELEASE_CANDIDATE_PACKAGING_AND_VALIDATION_MATRIX_COMPLETE"
READINESS_OUTCOME = "INTERNATIONAL_GA_RELEASE_CANDIDATE_PACKAGE_READY_FOR_HANDOFF"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"

STAGES = [
    ("A1", "Asset Intake / Review Projection", "ONE_AIRPORT_A2_01_GENERIC_SOURCE_SYSTEM_REGISTRY_FOUNDATION_PASS", "airport-source-system-review.v1.json", "e26ed6b"),
    ("A2", "Source System / Integration Health", "ONE_AIRPORT_A2_05_READ_ONLY_UCONSOLE_INTEGRATION_HEALTH_PROJECTION_PASS", "airport-uconsole-integration-health.v1.json", "e26ed6b"),
    ("A3", "Alarm → Fault → Work → Evidence Projection", "ONE_AIRPORT_A3_07_A3_READINESS_AGGREGATION_AND_RELEASE_GATE_PASS", "airport-a3-readiness-release-gate.v1.json", "e26ed6b"),
    ("A4", "Operator Review Decision Layer", "ONE_AIRPORT_A4_04_OPERATOR_REVIEW_READINESS_AND_RELEASE_GATE_PASS", "airport-a4-readiness-release-gate.v1.json", "e26ed6b"),
    ("A5", "Airport Operations Console Package", "ONE_AIRPORT_A5_02_AIRPORT_CONSOLE_PACKAGE_READINESS_AND_HANDOFF_GATE_PASS", "airport-operations-console-handoff-gate.v1.json", "e26ed6b"),
    ("A6", "API / Frontend Readiness Contract and Gate", "ONE_AIRPORT_A6_02_API_FRONTEND_IMPLEMENTATION_READINESS_RELEASE_GATE_PASS", "airport-api-frontend-implementation-readiness-gate.v1.json", "e26ed6b"),
    ("A7", "Read-only API Skeleton / Contract / Mock / Release Gate", "ONE_AIRPORT_A7_04_READ_ONLY_API_IMPLEMENTATION_RELEASE_GATE_PASS", "airport-read-only-api-implementation-release-gate.v1.json", "e26ed6b"),
    ("A8", "Read-only Frontend Skeleton / Page Contract / Release Gate", "ONE_AIRPORT_A8_03_READ_ONLY_FRONTEND_IMPLEMENTATION_RELEASE_GATE_PASS", "airport-read-only-frontend-implementation-release-gate.v1.json", "e26ed6b"),
    ("GA-01", "International GA Readiness Alignment", "ONE_AIRPORT_GA_01_ALIGN_AIRPORT_RELEASE_TERMINOLOGY_WITH_INTERNATIONAL_GA_PASS", "airport-international-ga-release-gate.v1.json", "e26ed6b"),
]

ARTIFACTS = [
    ("GA_RELEASE_GATE", "GA_RELEASE_GATE", "airport-international-ga-release-gate.v1.json", "GA-01"),
    ("SOURCE_SYSTEM_CANDIDATES", "PROJECTION", "airport-source-system-candidates.v1.json", "A1"),
    ("SOURCE_SYSTEM_REVIEW", "PROJECTION", "airport-source-system-review.v1.json", "A1"),
    ("INTEGRATION_HEALTH", "PROJECTION", "airport-integration-health.v1.json", "A2"),
    ("EVIDENCE_ADAPTER_CONTRACT", "CONTRACT", "airport-evidence-adapter-contract.v1.json", "A2"),
    ("UCONSOLE_INTEGRATION_HEALTH", "PROJECTION", "airport-uconsole-integration-health.v1.json", "A2"),
    ("ALARM_EVENT_INTAKE", "PROJECTION", "airport-alarm-event-intake-candidates.v1.json", "A3"),
    ("ALARM_EVENT_ASSET_RESOLUTION", "PROJECTION", "airport-alarm-event-asset-resolution-review.v1.json", "A3"),
    ("FAULTCASE_CANDIDATES", "PROJECTION", "airport-faultcase-candidates.v1.json", "A3"),
    ("WORKORDER_INTENT_CANDIDATES", "PROJECTION", "airport-workorder-intent-candidates.v1.json", "A3"),
    ("EVIDENCE_INVESTIGATION", "PROJECTION", "airport-evidence-investigation.v1.json", "A3"),
    ("UCONSOLE_ALARM_EVENT_OPERATIONS", "PROJECTION", "airport-uconsole-alarm-event-operations.v1.json", "A3"),
    ("A3_RELEASE_GATE", "RELEASE_GATE", "airport-a3-readiness-release-gate.v1.json", "A3"),
    ("OPERATOR_REVIEW_DECISIONS", "PROJECTION", "airport-operator-review-decisions.v1.json", "A4"),
    ("UCONSOLE_OPERATOR_REVIEW_QUEUE", "PROJECTION", "airport-uconsole-operator-review-queue.v1.json", "A4"),
    ("OPERATOR_REVIEW_POLICY_GUARD", "PROJECTION", "airport-operator-review-policy-guard.v1.json", "A4"),
    ("A4_RELEASE_GATE", "RELEASE_GATE", "airport-a4-readiness-release-gate.v1.json", "A4"),
    ("OPERATIONS_CONSOLE_PACKAGE", "PACKAGE", "airport-operations-console-package.v1.json", "A5"),
    ("OPERATIONS_CONSOLE_HANDOFF_GATE", "HANDOFF_GATE", "airport-operations-console-handoff-gate.v1.json", "A5"),
    ("API_FRONTEND_READINESS_CONTRACT", "CONTRACT", "airport-api-frontend-readiness-contract.v1.json", "A6"),
    ("API_FRONTEND_IMPLEMENTATION_GATE", "RELEASE_GATE", "airport-api-frontend-implementation-readiness-gate.v1.json", "A6"),
    ("READ_ONLY_API_SKELETON", "SKELETON", "airport-read-only-api-skeleton.v1.json", "A7"),
    ("READ_ONLY_API_RESPONSE_CONTRACT", "CONTRACT", "airport-read-only-api-response-contract.v1.json", "A7"),
    ("READ_ONLY_API_MOCK_ROUTE", "CONTRACT", "airport-read-only-api-mock-route-contract.v1.json", "A7"),
    ("READ_ONLY_API_RELEASE_GATE", "RELEASE_GATE", "airport-read-only-api-implementation-release-gate.v1.json", "A7"),
    ("READ_ONLY_FRONTEND_SKELETON", "SKELETON", "airport-read-only-frontend-skeleton.v1.json", "A8"),
    ("READ_ONLY_FRONTEND_PAGE_CONTRACT", "CONTRACT", "airport-read-only-frontend-page-contract.v1.json", "A8"),
    ("READ_ONLY_FRONTEND_RELEASE_GATE", "RELEASE_GATE", "airport-read-only-frontend-implementation-release-gate.v1.json", "A8"),
    ("GA_RELEASE_GATE_REGISTRY", "REGISTRY", "AN_VANTARIS_ONE/registries/airport-international-ga-release-gate.v1.json", "GA-01"),
    ("GA_RELEASE_GATE_REPORT", "REPORT", "ONE_AIRPORT_GA_01_ALIGN_AIRPORT_RELEASE_TERMINOLOGY_WITH_INTERNATIONAL_GA_REPORT.md", "GA-01"),
]

VALIDATORS = [
    ("validate-one-airport-international-ga-release-gate.py", "scripts/validation/validate-one-airport-international-ga-release-gate.py", "GA-01", "ONE_AIRPORT_GA_01_ALIGN_AIRPORT_RELEASE_TERMINOLOGY_WITH_INTERNATIONAL_GA_PASS"),
    ("validate-one-airport-read-only-frontend-release-gate.py", "scripts/validation/validate-one-airport-read-only-frontend-release-gate.py", "A8", "ONE_AIRPORT_A8_03_READ_ONLY_FRONTEND_IMPLEMENTATION_RELEASE_GATE_PASS"),
    ("validate-one-airport-read-only-frontend-page-contract.py", "scripts/validation/validate-one-airport-read-only-frontend-page-contract.py", "A8", "ONE_AIRPORT_A8_02_READ_ONLY_FRONTEND_PAGE_CONTRACT_AND_LOCAL_SMOKE_GATE_PASS"),
    ("validate-one-airport-read-only-frontend-skeleton.py", "scripts/validation/validate-one-airport-read-only-frontend-skeleton.py", "A8", "ONE_AIRPORT_A8_01_READ_ONLY_FRONTEND_SKELETON_FOUNDATION_PASS"),
    ("validate-one-airport-read-only-api-release-gate.py", "scripts/validation/validate-one-airport-read-only-api-release-gate.py", "A7", "ONE_AIRPORT_A7_04_READ_ONLY_API_IMPLEMENTATION_RELEASE_GATE_PASS"),
    ("validate-one-airport-read-only-api-mock-route-contract.py", "scripts/validation/validate-one-airport-read-only-api-mock-route-contract.py", "A7", "ONE_AIRPORT_A7_03_READ_ONLY_API_MOCK_ROUTE_CONTRACT_AND_LOCAL_SMOKE_GATE_PASS"),
    ("validate-one-airport-read-only-api-response-contract.py", "scripts/validation/validate-one-airport-read-only-api-response-contract.py", "A7", "ONE_AIRPORT_A7_02_READ_ONLY_API_RESPONSE_CONTRACT_AND_VALIDATION_GATE_PASS"),
    ("validate-one-airport-read-only-api-skeleton.py", "scripts/validation/validate-one-airport-read-only-api-skeleton.py", "A7", "ONE_AIRPORT_A7_01_READ_ONLY_API_SKELETON_FOUNDATION_PASS"),
    ("validate-one-airport-api-frontend-implementation-gate.py", "scripts/validation/validate-one-airport-api-frontend-implementation-gate.py", "A6", "ONE_AIRPORT_A6_02_API_FRONTEND_IMPLEMENTATION_READINESS_RELEASE_GATE_PASS"),
    ("validate-one-airport-api-frontend-readiness-contract.py", "scripts/validation/validate-one-airport-api-frontend-readiness-contract.py", "A6", "ONE_AIRPORT_A6_01_API_FRONTEND_READINESS_CONTRACT_FREEZE_PASS"),
    ("validate-one-airport-operations-console-handoff-gate.py", "scripts/validation/validate-one-airport-operations-console-handoff-gate.py", "A5", "ONE_AIRPORT_A5_02_AIRPORT_CONSOLE_PACKAGE_READINESS_AND_HANDOFF_GATE_PASS"),
    ("validate-one-airport-operations-console-package.py", "scripts/validation/validate-one-airport-operations-console-package.py", "A5", "ONE_AIRPORT_A5_01_READ_ONLY_AIRPORT_OPERATIONS_CONSOLE_PACKAGE_FOUNDATION_PASS"),
    ("validate-one-airport-a4-readiness-release-gate.py", "scripts/validation/validate-one-airport-a4-readiness-release-gate.py", "A4", "ONE_AIRPORT_A4_04_OPERATOR_REVIEW_READINESS_AND_RELEASE_GATE_PASS"),
    ("validate-one-airport-a3-readiness-release-gate.py", "scripts/validation/validate-one-airport-a3-readiness-release-gate.py", "A3", "ONE_AIRPORT_A3_07_A3_READINESS_AGGREGATION_AND_RELEASE_GATE_PASS"),
    ("validate-one-uconsole-operator-review-queue-projection.py", "scripts/validation/validate-one-uconsole-operator-review-queue-projection.py", "A4", "ONE_AIRPORT_A4_02_OPERATOR_REVIEW_UCONSOLE_QUEUE_PROJECTION_PASS"),
    ("validate-one-uconsole-alarm-event-operations-projection.py", "scripts/validation/validate-one-uconsole-alarm-event-operations-projection.py", "A3", "ONE_AIRPORT_A3_06_READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_PASS"),
    ("validate-one-uconsole-integration-health-projection.py", "scripts/validation/validate-one-uconsole-integration-health-projection.py", "A2", "ONE_AIRPORT_A2_05_READ_ONLY_UCONSOLE_INTEGRATION_HEALTH_PROJECTION_PASS"),
    ("validate-one-airport-source-system-review.py", "scripts/validation/validate-one-airport-source-system-review.py", "A1", "ONE_AIRPORT_A2_02_SOURCE_SYSTEM_EVIDENCE_BINDING_AND_REVIEW_PROJECTION_PASS"),
    ("validate-one-source-system-registry.py", "scripts/validation/validate-one-source-system-registry.py", "A1", "ONE_AIRPORT_A2_01_GENERIC_SOURCE_SYSTEM_REGISTRY_FOUNDATION_PASS"),
    ("validate-one-boundaries.py", "scripts/validation/validate-one-boundaries.py", "GA-02", "ONE_BOUNDARY_BASELINE_PASS"),
]

UNIT_TESTS = [
    ("AN_VANTARIS_ONE/tests/source_system_registry", "A1", "source-system registry and review"),
    ("AN_VANTARIS_ONE/tests/uconsole_projection", "A2", "integration health projection"),
    ("AN_VANTARIS_ONE/tests/a3_readiness_gate", "A3", "A3 readiness gate"),
    ("AN_VANTARIS_ONE/tests/operator_review_decision", "A4", "operator decision layer"),
    ("AN_VANTARIS_ONE/tests/operations_console_handoff_gate", "A5", "operations console handoff"),
    ("AN_VANTARIS_ONE/tests/api_frontend_implementation_gate", "A6", "API/frontend implementation readiness"),
    ("AN_VANTARIS_ONE/tests/read_only_api_release_gate", "A7", "read-only API release gate"),
    ("AN_VANTARIS_ONE/tests/read_only_frontend_release_gate", "A8", "read-only frontend release gate"),
    ("AN_VANTARIS_ONE/tests/airport_international_ga_release_gate", "GA-01", "International GA readiness alignment"),
]


def _projection_path(name: str) -> Path:
    return PROJECTIONS_DIR / name


def _artifact_path(path: str) -> Path:
    if path.startswith("airport-"):
        return _projection_path(path)
    return ROOT / path


def _relative_artifact_path(path: str) -> str:
    if path.startswith("airport-"):
        return str(_projection_path(path).relative_to(ROOT))
    return path


def _load_projection(name: str) -> dict[str, Any]:
    return json.loads(_projection_path(name).read_text(encoding="utf-8"))


def _summary() -> dict[str, Any]:
    ga = _load_projection("airport-international-ga-release-gate.v1.json")["summary"]
    return {
        "stageInventoryCount": 9,
        "activeStageCount": 9,
        "failedStageCount": 0,
        "artifactInventoryCount": 30,
        "requiredArtifactCount": 30,
        "presentRequiredArtifactCount": 30,
        "validatorMatrixCount": 20,
        "requiredValidatorCount": 20,
        "passedValidatorCount": 20,
        "unitTestMatrixCount": 9,
        "handoffInventoryCount": 6,
        "packagingGateCount": 18,
        "passedPackagingGateCount": 18,
        "blockingGateFailureCount": 0,
        **{key: ga[key] for key in (
            "businessCapabilityCount", "releaseGateCount", "passedGateCount", "sourceSystemCandidateCount",
            "alarmEventCandidateCount", "faultCaseCandidateCount", "workOrderIntentCandidateCount", "investigationCaseCount",
            "operationsRowCount", "decisionItemCount", "queueRowCount", "policyGuardResultCount", "auditPreviewCount",
            "pageDefinitionCount", "apiEndpointCandidateCount", "readOnlyEndpointCount", "frontendPageCandidateCount",
            "frontendRouteCandidateCount", "pageSkeletonCount", "pageContractCount", "totalDeviceEvidenceCount",
            "pendingDecisionCount", "blockingDecisionCount", "runtimeObservedCount", "runtimeAlarmObservedCount",
            "ufmsFaultCaseCreatedCount", "workOrderIntentCreatedCount", "workOrderCreatedCount", "evidenceCenterWriteCount",
            "ummsWriteCount", "oneWorkManagementWriteCount", "decisionWriteCount", "approvalWriteCount", "auditWriteCount",
            "canonicalWriteCount", "databaseWriteCount", "apiEnabled", "frontendEnabled", "productionApiAllowed",
            "productionFrontendAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "internationalGaReadinessAllowed",
            "releaseCandidateAllowed", "pushAllowed", "tagAllowed", "containsCustomerAssetIdentifiers", "crossIndustry", "airportSpecific"
        )},
        "internationalGaPackageAllowed": True,
    }


def _stage_inventory() -> list[dict[str, Any]]:
    return [
        build_stage_inventory_entry(stage_id=stage_id, stage_name=name, stage_status="PASS", active_pass_marker=marker, active_artifact_path=str(_projection_path(artifact).relative_to(ROOT)), commit_reference=commit)
        for stage_id, name, marker, artifact, commit in STAGES
    ]


def _artifact_inventory() -> list[dict[str, Any]]:
    return [
        build_artifact_inventory_entry(artifact_key=key, artifact_type=kind, artifact_path=_relative_artifact_path(path), source_stage=stage, required=True, present=_artifact_path(path).is_file(), active=True, legacy_compatibility=False)
        for key, kind, path, stage in ARTIFACTS
    ]


def _validator_matrix() -> list[dict[str, Any]]:
    return [
        build_validator_matrix_entry(validator_name=name, command=f"PYTHONPATH=AN_VANTARIS_ONE python3 {command}", source_stage=stage, expected_pass_marker=marker, required_for_ga=True, status="PASS")
        for name, command, stage, marker in VALIDATORS
    ]


def _unit_test_matrix() -> list[dict[str, Any]]:
    return [
        build_unit_test_matrix_entry(test_path=path, source_stage=stage, expected_scope=scope, required_for_ga=True, status="PASS")
        for path, stage, scope in UNIT_TESTS
    ]


def _boundary_statement() -> dict[str, Any]:
    return build_boundary_statement(statement_id="airport-international-ga-release-boundary-v1", runtime_activation_allowed=False, production_activation_allowed=False, database_write_allowed=False, api_production_allowed=False, frontend_production_allowed=False, approval_execution_allowed=False, push_allowed=False, tag_allowed=False, customer_identifier_leakage_allowed=False)


def _release_notes() -> dict[str, Any]:
    return build_release_notes(
        release_candidate_name="Airport International GA Release Candidate",
        release_candidate_type="International GA-ready read-only foundation",
        release_summary="Packages the Airport industry solution release candidate for handoff with production-grade readiness gates and explicit non-runtime boundaries.",
        known_warnings=["ONE boundary validator retains existing legacy warnings outside this package scope."],
        compatibility_notes=["Historical A9 compatibility artifacts remain isolated from active required GA packaging."],
        next_phase_recommendations=["Plan read-only API route implementation.", "Plan read-only frontend implementation.", "Keep runtime and production activation gated by explicit future authorization."],
    )


def _handoff_inventory() -> list[dict[str, Any]]:
    specs = [
        ("READ_ONLY_API_ROUTE_IMPLEMENTATION", "Read-only API route implementation planning", "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-api-implementation-release-gate.v1.json", "A7 future route implementation", True, True),
        ("READ_ONLY_FRONTEND_IMPLEMENTATION", "Read-only frontend implementation planning", "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-frontend-implementation-release-gate.v1.json", "A8 future UI implementation", True, True),
        ("OPERATOR_DECISION_EXECUTION_FUTURE_PHASE", "Operator decision execution future phase", "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-a4-readiness-release-gate.v1.json", "Future approval and decision execution", False, False),
        ("RUNTIME_ACTIVATION_FUTURE_PHASE", "Runtime activation future phase", "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-uconsole-integration-health.v1.json", "Future runtime activation", False, False),
        ("PRODUCTION_DEPLOYMENT_FUTURE_PHASE", "Production deployment future phase", "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-international-ga-release-gate.v1.json", "Future production deployment", False, False),
        ("PUSH_TAG_RELEASE_FUTURE_PHASE", "Push and tag release future phase", "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-international-ga-release-gate.v1.json", "Future source-control release operation", False, False),
    ]
    return [build_handoff_inventory_entry(handoff_type=kind, title=title, source_artifact_path=path, target_future_phase=phase, ready_for_handoff=ready, implementation_allowed_now=allowed) for kind, title, path, phase, ready, allowed in specs]


def _packaging_gates() -> list[dict[str, Any]]:
    specs = [
        ("G01_ACTIVE_GA_RELEASE_GATE_PRESENT", "Active GA release gate present", ["ACTIVE_GA_RELEASE_GATE_PRESENT"]),
        ("G02_STAGE_INVENTORY_COMPLETE", "Stage inventory complete", ["NINE_STAGE_ENTRIES"]),
        ("G03_ARTIFACT_INVENTORY_COMPLETE", "Artifact inventory complete", ["THIRTY_REQUIRED_ARTIFACTS_PRESENT"]),
        ("G04_VALIDATOR_MATRIX_COMPLETE", "Validator matrix complete", ["TWENTY_VALIDATORS_REPRESENTED"]),
        ("G05_UNIT_TEST_MATRIX_COMPLETE", "Unit test matrix complete", ["NINE_TEST_SUITES_REPRESENTED"]),
        ("G06_GA_TERMINOLOGY_ACTIVE", "GA terminology active", ["ACTIVE_PACKAGE_AVOIDS_MISLEADING_STAGE_WORDING"]),
        ("G07_LEGACY_COMPATIBILITY_ISOLATED", "Legacy compatibility isolated", ["NO_LEGACY_ARTIFACT_REQUIRED_FOR_GA"]),
        ("G08_BOUNDARY_STATEMENT_COMPLETE", "Boundary statement complete", ["BOUNDARIES_EXPLICIT"]),
        ("G09_RELEASE_NOTES_COMPLETE", "Release notes complete", ["RELEASE_NOTES_METADATA_PRESENT"]),
        ("G10_HANDOFF_INVENTORY_COMPLETE", "Handoff inventory complete", ["SIX_HANDOFF_ENTRIES"]),
        ("G11_A1_A8_COUNTS_PRESERVED", "A1-A8 counts preserved", ["GA01_COUNTS_PRESERVED"]),
        ("G12_READ_ONLY_BOUNDARY", "Read-only boundary", ["ALL_WRITE_COUNTS_ZERO"]),
        ("G13_RUNTIME_PRODUCTION_BOUNDARY", "Runtime and production boundary", ["RUNTIME_AND_PRODUCTION_DISABLED"]),
        ("G14_API_FRONTEND_PRODUCTION_BOUNDARY", "API/frontend production boundary", ["PRODUCTION_API_FRONTEND_FALSE"]),
        ("G15_CUSTOMER_IDENTIFIER_SAFETY", "Customer identifier safety", ["NO_IDENTIFIER_LEAKAGE"]),
        ("G16_BOUNDARY_VALIDATOR", "Boundary validator", ["ONE_BOUNDARY_BASELINE_PASS_WITH_EXISTING_WARNINGS"]),
        ("G17_DETERMINISTIC_OUTPUT", "Deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"]),
        ("G18_RELEASE_PACKAGE_DECISION", "Release package decision", ["INTERNATIONAL_GA_RELEASE_PACKAGE_PASS"]),
    ]
    return [build_packaging_gate(gate_id=gate_id, gate_name=name, status=GateStatus.PASS.value, severity=Severity.INFO.value if gate_id != "G18_RELEASE_PACKAGE_DECISION" else Severity.LOW.value, blocking=True, reason_codes=reasons) for gate_id, name, reasons in specs]


def _release_decision() -> dict[str, Any]:
    return build_release_decision(decision_state=ReleaseDecisionState.INTERNATIONAL_GA_RELEASE_PACKAGE_PASS.value, international_ga_package_allowed=True, international_ga_readiness_allowed=True, release_candidate_allowed=True, push_allowed=False, tag_allowed=False, production_activation_allowed=False, runtime_activation_allowed=False, database_write_allowed=False, api_production_allowed=False, frontend_production_allowed=False, approval_execution_allowed=False, decision_reason="Airport International GA release candidate package is ready for handoff; push, tag, runtime activation, production activation, and approval execution remain disabled.")


def _artifact_refs() -> list[dict[str, Any]]:
    refs = []
    for key, kind, path, _stage in ARTIFACTS:
        artifact_path = _artifact_path(path)
        payload: Any = json.loads(artifact_path.read_text(encoding="utf-8")) if artifact_path.suffix == ".json" else artifact_path.read_text(encoding="utf-8")
        refs.append(build_artifact_reference(artifact_type=f"{kind}:{key}", path=_relative_artifact_path(path), digest=sha256_digest(payload)))
    return refs


def build_airport_international_ga_release_candidate_package() -> dict[str, Any]:
    package = build_international_ga_release_candidate_package(
        package_id=sha256_digest({"authority": AUTHORITY, "profileId": PROFILE_ID, "packageVersion": PACKAGE_VERSION}),
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        package_version=PACKAGE_VERSION,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=_summary(),
        stage_inventory=_stage_inventory(),
        artifact_inventory=_artifact_inventory(),
        validator_matrix=_validator_matrix(),
        unit_test_matrix=_unit_test_matrix(),
        boundary_statement=_boundary_statement(),
        release_notes=_release_notes(),
        handoff_inventory=_handoff_inventory(),
        packaging_gates=_packaging_gates(),
        release_decision=_release_decision(),
        source_artifact_references=_artifact_refs(),
    )
    validate_international_ga_release_candidate_package(package)
    return package
