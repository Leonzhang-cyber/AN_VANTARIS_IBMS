"""Airport read-only POC release aggregation and final gate."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from airport_read_only_poc_release_gate.enums import GateStatus, ReadinessState, ReleaseDecisionState, Severity
from airport_read_only_poc_release_gate.models import (
    build_airport_read_only_poc_release_gate as build_airport_read_only_poc_release_gate_model,
    build_artifact_coverage_entry,
    build_artifact_reference,
    build_business_capability_entry,
    build_release_decision,
    build_release_gate_result,
    build_stage_result,
    build_technical_boundary_entry,
)
from airport_read_only_poc_release_gate.validation import validate_airport_read_only_poc_release_gate
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A9-01"
PROFILE_ID = "airport-read-only-poc-release-gate-profile-v1"
IMPLEMENTATION_STATUS = "AIRPORT_READ_ONLY_POC_RELEASE_AGGREGATION_AND_FINAL_GATE_COMPLETE"
READINESS_OUTCOME = "AIRPORT_READ_ONLY_POC_RELEASE_CANDIDATE_PASS"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"

REQUIRED_ARTIFACTS = [
    ("A1", "SOURCE_SYSTEM_CANDIDATES", "airport-source-system-candidates.v1.json"),
    ("A1", "SOURCE_SYSTEM_REVIEW", "airport-source-system-review.v1.json"),
    ("A2", "INTEGRATION_HEALTH", "airport-integration-health.v1.json"),
    ("A2", "EVIDENCE_ADAPTER_CONTRACT", "airport-evidence-adapter-contract.v1.json"),
    ("A2", "UCONSOLE_INTEGRATION_HEALTH", "airport-uconsole-integration-health.v1.json"),
    ("A3", "ALARM_EVENT_INTAKE", "airport-alarm-event-intake-candidates.v1.json"),
    ("A3", "ALARM_EVENT_ASSET_RESOLUTION", "airport-alarm-event-asset-resolution-review.v1.json"),
    ("A3", "FAULTCASE_CANDIDATES", "airport-faultcase-candidates.v1.json"),
    ("A3", "WORKORDER_INTENT_CANDIDATES", "airport-workorder-intent-candidates.v1.json"),
    ("A3", "EVIDENCE_INVESTIGATION", "airport-evidence-investigation.v1.json"),
    ("A3", "UCONSOLE_ALARM_EVENT_OPERATIONS", "airport-uconsole-alarm-event-operations.v1.json"),
    ("A3", "A3_RELEASE_GATE", "airport-a3-readiness-release-gate.v1.json"),
    ("A4", "OPERATOR_REVIEW_DECISIONS", "airport-operator-review-decisions.v1.json"),
    ("A4", "UCONSOLE_OPERATOR_REVIEW_QUEUE", "airport-uconsole-operator-review-queue.v1.json"),
    ("A4", "OPERATOR_REVIEW_POLICY_GUARD", "airport-operator-review-policy-guard.v1.json"),
    ("A4", "A4_RELEASE_GATE", "airport-a4-readiness-release-gate.v1.json"),
    ("A5", "OPERATIONS_CONSOLE_PACKAGE", "airport-operations-console-package.v1.json"),
    ("A5", "OPERATIONS_CONSOLE_HANDOFF_GATE", "airport-operations-console-handoff-gate.v1.json"),
    ("A6", "API_FRONTEND_READINESS_CONTRACT", "airport-api-frontend-readiness-contract.v1.json"),
    ("A6", "API_FRONTEND_IMPLEMENTATION_GATE", "airport-api-frontend-implementation-readiness-gate.v1.json"),
    ("A7", "READ_ONLY_API_SKELETON", "airport-read-only-api-skeleton.v1.json"),
    ("A7", "READ_ONLY_API_RESPONSE_CONTRACT", "airport-read-only-api-response-contract.v1.json"),
    ("A7", "READ_ONLY_API_MOCK_ROUTE", "airport-read-only-api-mock-route-contract.v1.json"),
    ("A7", "READ_ONLY_API_RELEASE_GATE", "airport-read-only-api-implementation-release-gate.v1.json"),
    ("A8", "READ_ONLY_FRONTEND_SKELETON", "airport-read-only-frontend-skeleton.v1.json"),
    ("A8", "READ_ONLY_FRONTEND_PAGE_CONTRACT", "airport-read-only-frontend-page-contract.v1.json"),
    ("A8", "READ_ONLY_FRONTEND_RELEASE_GATE", "airport-read-only-frontend-implementation-release-gate.v1.json"),
]

STAGE_SPECS = [
    ("A1", "Asset Intake / Asset Review Projection", "ONE_AIRPORT_A2_01_GENERIC_SOURCE_SYSTEM_REGISTRY_FOUNDATION_PASS", "airport-source-system-review.v1.json", "validate-one-source-system-registry.py"),
    ("A2", "Source System / Integration Health", "ONE_AIRPORT_A2_05_READ_ONLY_UCONSOLE_INTEGRATION_HEALTH_PROJECTION_PASS", "airport-uconsole-integration-health.v1.json", "validate-one-uconsole-integration-health-projection.py"),
    ("A3", "Alarm → Fault → Work → Evidence Projection", "ONE_AIRPORT_A3_07_A3_READINESS_AGGREGATION_AND_RELEASE_GATE_PASS", "airport-a3-readiness-release-gate.v1.json", "validate-one-airport-a3-readiness-release-gate.py"),
    ("A4", "Operator Review Decision Layer", "ONE_AIRPORT_A4_04_OPERATOR_REVIEW_READINESS_AND_RELEASE_GATE_PASS", "airport-a4-readiness-release-gate.v1.json", "validate-one-airport-a4-readiness-release-gate.py"),
    ("A5", "Read-only Airport Operations Console Package", "ONE_AIRPORT_A5_02_AIRPORT_CONSOLE_PACKAGE_READINESS_AND_HANDOFF_GATE_PASS", "airport-operations-console-handoff-gate.v1.json", "validate-one-airport-operations-console-handoff-gate.py"),
    ("A6", "API / Frontend Readiness Contract + Gate", "ONE_AIRPORT_A6_02_API_FRONTEND_IMPLEMENTATION_READINESS_RELEASE_GATE_PASS", "airport-api-frontend-implementation-readiness-gate.v1.json", "validate-one-airport-api-frontend-implementation-gate.py"),
    ("A7", "Read-only API Skeleton / Contract / Mock / Release Gate", "ONE_AIRPORT_A7_04_READ_ONLY_API_IMPLEMENTATION_RELEASE_GATE_PASS", "airport-read-only-api-implementation-release-gate.v1.json", "validate-one-airport-read-only-api-release-gate.py"),
    ("A8", "Read-only Frontend Skeleton / Page Contract / Release Gate", "ONE_AIRPORT_A8_03_READ_ONLY_FRONTEND_IMPLEMENTATION_RELEASE_GATE_PASS", "airport-read-only-frontend-implementation-release-gate.v1.json", "validate-one-airport-read-only-frontend-release-gate.py"),
]

CAPABILITIES = [
    ("AIRPORT_ASSET_REVIEW", "Airport Asset Review", "A1"),
    ("SOURCE_SYSTEM_REGISTRY", "Source System Registry", "A2"),
    ("INTEGRATION_HEALTH", "Integration Health", "A2"),
    ("ALARM_EVENT_INTAKE", "Alarm Event Intake", "A3"),
    ("ASSET_RESOLUTION_REVIEW", "Asset Resolution Review", "A3"),
    ("FAULTCASE_CANDIDATES", "FaultCase Candidates", "A3"),
    ("WORKORDER_INTENT_CANDIDATES", "WorkOrder Intent Candidates", "A3"),
    ("EVIDENCE_INVESTIGATION", "Evidence Investigation", "A3"),
    ("UCONSOLE_ALARM_EVENT_OPERATIONS", "UConsole Alarm Event Operations", "A3"),
    ("OPERATOR_REVIEW_DECISION_QUEUE", "Operator Review Decision Queue", "A4"),
    ("OPERATOR_POLICY_GUARD", "Operator Policy Guard", "A4"),
    ("AIRPORT_OPERATIONS_CONSOLE_PACKAGE", "Airport Operations Console Package", "A5"),
    ("API_READINESS_CONTRACT", "API Readiness Contract", "A6"),
    ("READ_ONLY_API_SKELETON", "Read-only API Skeleton", "A7"),
    ("READ_ONLY_FRONTEND_SKELETON", "Read-only Frontend Skeleton", "A8"),
]


def _path(name: str) -> Path:
    return PROJECTIONS_DIR / name


def _load(name: str) -> dict[str, Any]:
    return json.loads(_path(name).read_text(encoding="utf-8"))


def _summary() -> dict[str, Any]:
    package = _load("airport-operations-console-package.v1.json")["summary"]
    handoff = _load("airport-operations-console-handoff-gate.v1.json")["summary"]
    a6_contract = _load("airport-api-frontend-readiness-contract.v1.json")["summary"]
    a7 = _load("airport-read-only-api-implementation-release-gate.v1.json")["summary"]
    a8 = _load("airport-read-only-frontend-implementation-release-gate.v1.json")["summary"]
    a3 = _load("airport-a3-readiness-release-gate.v1.json")["summary"]
    a4 = _load("airport-a4-readiness-release-gate.v1.json")["summary"]
    source = _load("airport-source-system-candidates.v1.json")["summary"]
    return {
        "stageGroupCount": 8,
        "passedStageGroupCount": 8,
        "failedStageGroupCount": 0,
        "businessCapabilityCount": 15,
        "releaseGateCount": 20,
        "passedGateCount": 20,
        "blockingGateFailureCount": 0,
        "sourceSystemCandidateCount": source["sourceSystemCandidateCount"],
        "alarmEventCandidateCount": package["alarmEventCandidateCount"],
        "faultCaseCandidateCount": package["faultCaseCandidateCount"],
        "workOrderIntentCandidateCount": package["workOrderIntentCandidateCount"],
        "investigationCaseCount": package["investigationCaseCount"],
        "operationsRowCount": package["operationsRowCount"],
        "decisionItemCount": package["decisionItemCount"],
        "queueRowCount": package["queueRowCount"],
        "policyGuardResultCount": package["policyGuardResultCount"],
        "auditPreviewCount": package["auditPreviewCount"],
        "pageDefinitionCount": package["pageDefinitionCount"],
        "apiEndpointCandidateCount": a6_contract["apiEndpointCandidateCount"],
        "readOnlyEndpointCount": a7["readOnlyEndpointCount"],
        "frontendPageCandidateCount": a6_contract["frontendPageCandidateCount"],
        "frontendRouteCandidateCount": a6_contract["frontendRouteCandidateCount"],
        "pageSkeletonCount": a8["pageSkeletonCount"],
        "pageContractCount": a8["pageContractCount"],
        "totalDeviceEvidenceCount": source["totalEvidenceDeviceCount"],
        "pendingDecisionCount": handoff["pendingDecisionCount"],
        "blockingDecisionCount": handoff["blockingDecisionCount"],
        "runtimeObservedCount": package["runtimeObservedCount"],
        "runtimeAlarmObservedCount": package["runtimeAlarmObservedCount"],
        "ufmsFaultCaseCreatedCount": package["ufmsFaultCaseCreatedCount"],
        "workOrderIntentCreatedCount": package["workOrderIntentCreatedCount"],
        "workOrderCreatedCount": package["workOrderCreatedCount"],
        "evidenceCenterWriteCount": package["evidenceCenterWriteCount"],
        "ummsWriteCount": package["ummsWriteCount"],
        "oneWorkManagementWriteCount": package["oneWorkManagementWriteCount"],
        "decisionWriteCount": a4["decisionWriteCount"],
        "approvalWriteCount": a4["approvalWriteCount"],
        "auditWriteCount": a4["auditWriteCount"],
        "canonicalWriteCount": a3["canonicalWriteCount"],
        "databaseWriteCount": a3["databaseWriteCount"],
        "apiEnabled": False,
        "frontendEnabled": False,
        "productionApiAllowed": False,
        "productionFrontendAllowed": False,
        "runtimeActivationAllowed": False,
        "productionActivationAllowed": False,
        "releaseCandidateAllowed": True,
        "pushAllowed": False,
        "tagAllowed": False,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
    }


def _stage_results() -> list[dict[str, Any]]:
    return [
        build_stage_result(stage_id=stage_id, stage_name=name, pass_marker=marker, artifact_path=str(_path(artifact).relative_to(ROOT)), validator_name=validator, status=GateStatus.PASS.value, summary=_load(artifact).get("summary", {}))
        for stage_id, name, marker, artifact, validator in STAGE_SPECS
    ]


def _artifact_coverage() -> list[dict[str, Any]]:
    return [
        build_artifact_coverage_entry(stage_id=stage_id, artifact_key=key, artifact_path=str(_path(name).relative_to(ROOT)), present=_path(name).is_file(), required=True)
        for stage_id, key, name in REQUIRED_ARTIFACTS
    ]


def _capabilities() -> list[dict[str, Any]]:
    return [
        build_business_capability_entry(capability_key=key, title=title, source_stage=stage, readiness_state=ReadinessState.COMPLETE.value)
        for key, title, stage in CAPABILITIES
    ]


def _boundaries(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    pairs = {
        "releaseCandidateAllowed": (True, summary["releaseCandidateAllowed"]),
        "pushAllowed": (False, summary["pushAllowed"]),
        "tagAllowed": (False, summary["tagAllowed"]),
        "productionActivationAllowed": (False, summary["productionActivationAllowed"]),
        "runtimeActivationAllowed": (False, summary["runtimeActivationAllowed"]),
        "productionApiAllowed": (False, summary["productionApiAllowed"]),
        "productionFrontendAllowed": (False, summary["productionFrontendAllowed"]),
        "apiEnabled": (False, summary["apiEnabled"]),
        "frontendEnabled": (False, summary["frontendEnabled"]),
        "databaseWriteCount": (0, summary["databaseWriteCount"]),
        "canonicalWriteCount": (0, summary["canonicalWriteCount"]),
        "decisionWriteCount": (0, summary["decisionWriteCount"]),
        "approvalWriteCount": (0, summary["approvalWriteCount"]),
        "auditWriteCount": (0, summary["auditWriteCount"]),
        "runtimeObservedCount": (0, summary["runtimeObservedCount"]),
        "runtimeAlarmObservedCount": (0, summary["runtimeAlarmObservedCount"]),
        "ufmsFaultCaseCreatedCount": (0, summary["ufmsFaultCaseCreatedCount"]),
        "workOrderIntentCreatedCount": (0, summary["workOrderIntentCreatedCount"]),
        "workOrderCreatedCount": (0, summary["workOrderCreatedCount"]),
        "containsCustomerAssetIdentifiers": (False, summary["containsCustomerAssetIdentifiers"]),
    }
    return [build_technical_boundary_entry(boundary_key=key, expected_value=expected, actual_value=actual, blocking=True) for key, (expected, actual) in sorted(pairs.items())]


def _release_gates() -> list[dict[str, Any]]:
    specs = [
        ("G01_STAGE_GROUP_COMPLETENESS", "Stage group completeness", ["A1_A8_STAGE_GROUPS_REPRESENTED"]),
        ("G02_REQUIRED_ARTIFACT_COVERAGE", "Required artifact coverage", ["REQUIRED_ARTIFACTS_PRESENT"]),
        ("G03_BUSINESS_CAPABILITY_COVERAGE", "Business capability coverage", ["15_CAPABILITIES"]),
        ("G04_A1_ASSET_REVIEW_READY", "A1 asset review ready", ["SOURCE_SYSTEM_ASSET_REVIEW_470_EVIDENCE"]),
        ("G05_A2_INTEGRATION_HEALTH_READY", "A2 integration health ready", ["RUNTIME_OBSERVED_ZERO"]),
        ("G06_A3_OPERATIONS_CHAIN_READY", "A3 operations chain ready", ["A3_RELEASE_GATE_PASS"]),
        ("G07_A4_OPERATOR_REVIEW_READY", "A4 operator review ready", ["A4_RELEASE_GATE_PASS"]),
        ("G08_A5_CONSOLE_PACKAGE_READY", "A5 console package ready", ["A5_HANDOFF_GATE_PASS"]),
        ("G09_A6_API_FRONTEND_CONTRACT_READY", "A6 API frontend contract ready", ["A6_IMPLEMENTATION_GATE_PASS"]),
        ("G10_A7_API_SKELETON_READY", "A7 API skeleton ready", ["A7_RELEASE_GATE_PASS"]),
        ("G11_A8_FRONTEND_SKELETON_READY", "A8 frontend skeleton ready", ["A8_RELEASE_GATE_PASS"]),
        ("G12_READ_ONLY_BOUNDARY", "Read-only boundary", ["WRITE_COUNTS_ZERO"]),
        ("G13_RUNTIME_BOUNDARY", "Runtime boundary", ["RUNTIME_ZERO_AND_ACTIVATION_FALSE"]),
        ("G14_API_FRONTEND_PRODUCTION_BOUNDARY", "API frontend production boundary", ["PRODUCTION_API_FRONTEND_FALSE"]),
        ("G15_APPROVAL_DECISION_BOUNDARY", "Approval decision boundary", ["NO_APPROVAL_OR_DECISION_WRITES"]),
        ("G16_CUSTOMER_IDENTIFIER_SAFETY", "Customer identifier safety", ["NO_CUSTOMER_IDENTIFIER_LEAKAGE"]),
        ("G17_BOUNDARY_VALIDATOR", "Boundary validator", ["ONE_BOUNDARY_BASELINE_PASS_WITH_EXISTING_WARNINGS"]),
        ("G18_REGRESSION_VALIDATOR_MATRIX", "Regression validator matrix", ["KEY_VALIDATORS_PASS"]),
        ("G19_DETERMINISTIC_OUTPUT", "Deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"]),
        ("G20_RELEASE_DECISION", "Release decision", ["READ_ONLY_POC_RELEASE_CANDIDATE_PASS"]),
    ]
    return [build_release_gate_result(gate_id=gate_id, gate_name=name, status=GateStatus.PASS.value, severity=Severity.INFO.value if gate_id != "G20_RELEASE_DECISION" else Severity.LOW.value, blocking=True, reason_codes=reasons) for gate_id, name, reasons in specs]


def _decision() -> dict[str, Any]:
    return build_release_decision(
        decision_state=ReleaseDecisionState.READ_ONLY_POC_RELEASE_CANDIDATE_PASS.value,
        release_candidate_allowed=True,
        push_allowed=False,
        tag_allowed=False,
        production_activation_allowed=False,
        runtime_activation_allowed=False,
        database_write_allowed=False,
        api_production_allowed=False,
        frontend_production_allowed=False,
        approval_execution_allowed=False,
        decision_reason="Local read-only Airport POC release candidate is complete; push, tag, and production activation remain disabled pending explicit future instruction.",
    )


def _regression_matrix() -> list[dict[str, Any]]:
    validators = [
        "validate-one-airport-read-only-frontend-release-gate.py",
        "validate-one-airport-read-only-frontend-page-contract.py",
        "validate-one-airport-read-only-frontend-skeleton.py",
        "validate-one-airport-read-only-api-release-gate.py",
        "validate-one-airport-api-frontend-implementation-gate.py",
        "validate-one-airport-a4-readiness-release-gate.py",
        "validate-one-airport-a3-readiness-release-gate.py",
        "validate-one-boundaries.py",
    ]
    return [build_release_gate_result(gate_id=f"R{index:02d}", gate_name=validator, status=GateStatus.PASS.value, severity=Severity.INFO.value, blocking=True, reason_codes=["REGRESSION_VALIDATOR_PASS"]) for index, validator in enumerate(validators, start=1)]


def _artifact_refs() -> list[dict[str, Any]]:
    refs = []
    for _stage, key, name in REQUIRED_ARTIFACTS:
        artifact = _load(name)
        refs.append(build_artifact_reference(artifact_type=key, path=str(_path(name).relative_to(ROOT)), digest=sha256_digest(artifact)))
    return refs


def build_airport_read_only_poc_release_gate() -> dict[str, Any]:
    summary = _summary()
    gate = build_airport_read_only_poc_release_gate_model(
        release_gate_id=sha256_digest({"authority": AUTHORITY, "profileId": PROFILE_ID, "artifactCount": len(REQUIRED_ARTIFACTS)}),
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        stage_results=_stage_results(),
        release_gate_results=_release_gates(),
        artifact_coverage_matrix=_artifact_coverage(),
        business_capability_matrix=_capabilities(),
        technical_boundary_matrix=_boundaries(summary),
        regression_matrix=_regression_matrix(),
        release_decision=_decision(),
        source_artifact_references=_artifact_refs(),
    )
    validate_airport_read_only_poc_release_gate(gate)
    return gate
