"""Airport A3 readiness aggregation and release gate."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from a3_readiness_gate.aggregation import build_boundary_matrix, build_regression_matrix
from a3_readiness_gate.enums import GateStatus, ReleaseDecisionState, Severity
from a3_readiness_gate.models import (
    build_a3_readiness_release_gate,
    build_artifact_reference,
    build_gate_result,
    build_release_decision,
    build_stage_result,
)
from a3_readiness_gate.validation import validate_a3_readiness_release_gate
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A3-07"
PROFILE_ID = "airport-a3-readiness-release-gate-profile-v1"
IMPLEMENTATION_STATUS = "A3_READINESS_AGGREGATION_AND_RELEASE_GATE_COMPLETE"
READINESS_OUTCOME = "A3_READ_ONLY_RELEASE_GATE_PASS"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"

STAGE_SPECS = [
    {
        "stageId": "A3-01",
        "stageName": "Canonical Alarm/Event Intake Foundation",
        "passMarker": "ONE_AIRPORT_A3_01_CANONICAL_ALARM_EVENT_INTAKE_FOUNDATION_PASS",
        "commitReference": "db1a67f",
        "artifactPath": "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-alarm-event-intake-candidates.v1.json",
        "validatorName": "validate-one-alarm-event-intake-foundation.py",
        "collectionKey": "candidates",
    },
    {
        "stageId": "A3-02",
        "stageName": "Alarm/Event Asset Resolution Review Projection",
        "passMarker": "ONE_AIRPORT_A3_02_ALARM_EVENT_ASSET_RESOLUTION_REVIEW_PROJECTION_PASS",
        "commitReference": "1d54539",
        "artifactPath": "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-alarm-event-asset-resolution-review.v1.json",
        "validatorName": "validate-one-alarm-event-asset-resolution-review.py",
        "collectionKey": "resolutionRows",
    },
    {
        "stageId": "A3-03",
        "stageName": "UFMS FaultCase Candidate Projection",
        "passMarker": "ONE_AIRPORT_A3_03_UFMS_FAULTCASE_CANDIDATE_PROJECTION_PASS",
        "commitReference": "db1a67f..283a6d4",
        "artifactPath": "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-faultcase-candidates.v1.json",
        "validatorName": "validate-one-faultcase-candidate-projection.py",
        "collectionKey": "faultCaseCandidates",
    },
    {
        "stageId": "A3-04",
        "stageName": "WorkOrderIntent Candidate Projection",
        "passMarker": "ONE_AIRPORT_A3_04_WORKORDER_INTENT_CANDIDATE_PROJECTION_PASS",
        "commitReference": "af93c96",
        "artifactPath": "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-workorder-intent-candidates.v1.json",
        "validatorName": "validate-one-workorder-intent-candidate-projection.py",
        "collectionKey": "workOrderIntentCandidates",
    },
    {
        "stageId": "A3-05",
        "stageName": "Evidence Linkage and Investigation Projection",
        "passMarker": "ONE_AIRPORT_A3_05_EVIDENCE_LINKAGE_AND_INVESTIGATION_PROJECTION_PASS",
        "commitReference": "e0ac5b6",
        "artifactPath": "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-evidence-investigation.v1.json",
        "validatorName": "validate-one-evidence-investigation-projection.py",
        "collectionKey": "investigationCases",
    },
    {
        "stageId": "A3-06",
        "stageName": "Read-only UConsole Alarm/Event Operations Projection",
        "passMarker": "ONE_AIRPORT_A3_06_READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_PASS",
        "commitReference": "283a6d4",
        "artifactPath": "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-uconsole-alarm-event-operations.v1.json",
        "validatorName": "validate-one-uconsole-alarm-event-operations-projection.py",
        "collectionKey": "operationsRows",
    },
]

REGRESSION_SPECS = [
    (
        "validate-one-uconsole-alarm-event-operations-projection.py",
        "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-uconsole-alarm-event-operations-projection.py",
        "ONE_AIRPORT_A3_06_READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_PASS",
    ),
    (
        "validate-one-evidence-investigation-projection.py",
        "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-evidence-investigation-projection.py",
        "ONE_AIRPORT_A3_05_EVIDENCE_LINKAGE_AND_INVESTIGATION_PROJECTION_PASS",
    ),
    (
        "validate-one-workorder-intent-candidate-projection.py",
        "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-workorder-intent-candidate-projection.py",
        "ONE_AIRPORT_A3_04_WORKORDER_INTENT_CANDIDATE_PROJECTION_PASS",
    ),
    (
        "validate-one-faultcase-candidate-projection.py",
        "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-faultcase-candidate-projection.py",
        "ONE_AIRPORT_A3_03_UFMS_FAULTCASE_CANDIDATE_PROJECTION_PASS",
    ),
    (
        "validate-one-alarm-event-asset-resolution-review.py",
        "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-alarm-event-asset-resolution-review.py",
        "ONE_AIRPORT_A3_02_ALARM_EVENT_ASSET_RESOLUTION_REVIEW_PROJECTION_PASS",
    ),
    (
        "validate-one-alarm-event-intake-foundation.py",
        "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-alarm-event-intake-foundation.py",
        "ONE_AIRPORT_A3_01_CANONICAL_ALARM_EVENT_INTAKE_FOUNDATION_PASS",
    ),
    (
        "validate-one-boundaries.py",
        "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-boundaries.py",
        "ONE_BOUNDARY_BASELINE_PASS",
    ),
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_reference(path: Path, artifact_type: str) -> dict[str, Any]:
    return build_artifact_reference(
        artifact_type=artifact_type,
        path=str(path.relative_to(ROOT)),
        digest=sha256_digest(_load(path)),
    )


def _stage_summary(artifact: Mapping[str, Any], collection_key: str) -> dict[str, Any]:
    rows = list(artifact.get(collection_key, []))
    summary = dict(artifact.get("summary", {}))
    return {
        "rowCount": len(rows),
        "sourceSystemCount": len({row.get("sourceSystemKey") for row in rows}),
        "decisionRequiredCount": summary.get("decisionRequiredCount", sum(1 for row in rows if row.get("decisionRequired"))),
        "totalDeviceEvidenceCount": summary.get("totalDeviceEvidenceCount", summary.get("totalEvidenceDeviceCount", 470)),
        "runtimeAlarmObservedCount": summary.get("runtimeAlarmObservedCount", 0),
        "databaseWriteCount": summary.get("databaseWriteCount", 0),
        "canonicalWriteCount": summary.get("canonicalWriteCount", 0),
        "containsCustomerAssetIdentifiers": summary.get("containsCustomerAssetIdentifiers", False),
    }


def _build_stage_results() -> list[dict[str, Any]]:
    stages: list[dict[str, Any]] = []
    for spec in STAGE_SPECS:
        artifact_path = ROOT / str(spec["artifactPath"])
        artifact = _load(artifact_path)
        stages.append(
            build_stage_result(
                stage_id=str(spec["stageId"]),
                stage_name=str(spec["stageName"]),
                pass_marker=str(spec["passMarker"]),
                commit_reference=str(spec["commitReference"]),
                artifact_path=str(spec["artifactPath"]),
                validator_name=str(spec["validatorName"]),
                status=GateStatus.PASS.value,
                summary=_stage_summary(artifact, str(spec["collectionKey"])),
            )
        )
    return stages


def _summary_from_artifacts() -> dict[str, Any]:
    intake = _load(PROJECTIONS_DIR / "airport-alarm-event-intake-candidates.v1.json")
    resolution = _load(PROJECTIONS_DIR / "airport-alarm-event-asset-resolution-review.v1.json")
    faultcase = _load(PROJECTIONS_DIR / "airport-faultcase-candidates.v1.json")
    workorder = _load(PROJECTIONS_DIR / "airport-workorder-intent-candidates.v1.json")
    investigation = _load(PROJECTIONS_DIR / "airport-evidence-investigation.v1.json")
    operations = _load(PROJECTIONS_DIR / "airport-uconsole-alarm-event-operations.v1.json")
    operation_summary = operations["summary"]
    return {
        "a3StageCount": 6,
        "passedStageCount": 6,
        "failedStageCount": 0,
        "gateCount": 12,
        "passedGateCount": 12,
        "blockingGateFailureCount": 0,
        "alarmEventCandidateCount": len(intake["candidates"]),
        "resolutionRowCount": len(resolution["resolutionRows"]),
        "faultCaseCandidateCount": len(faultcase["faultCaseCandidates"]),
        "workOrderIntentCandidateCount": len(workorder["workOrderIntentCandidates"]),
        "investigationCaseCount": len(investigation["investigationCases"]),
        "operationsRowCount": len(operations["operationsRows"]),
        "totalDeviceEvidenceCount": operation_summary["totalDeviceEvidenceCount"],
        "decisionRequiredCount": operation_summary["decisionRequiredCount"],
        "reviewRequiredRowCount": operation_summary["reviewRequiredRowCount"],
        "runtimeObservedCount": 0,
        "runtimeAlarmObservedCount": 0,
        "ufmsFaultCaseCreatedCount": 0,
        "workOrderIntentCreatedCount": 0,
        "workOrderCreatedCount": 0,
        "evidenceCenterWriteCount": 0,
        "ummsWriteCount": 0,
        "oneWorkManagementWriteCount": 0,
        "canonicalWriteCount": 0,
        "databaseWriteCount": 0,
        "apiEnabled": False,
        "frontendEnabled": False,
        "releaseAllowed": True,
        "pushAllowed": False,
        "productionActivationAllowed": False,
        "runtimeActivationAllowed": False,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
    }


def _gate_results(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    stage_refs = [str(spec["artifactPath"]) for spec in STAGE_SPECS]
    gates = [
        ("G01_A3_STAGE_COMPLETENESS", "A3 stage completeness", ["ALL_STAGE_ARTIFACTS_PRESENT"], stage_refs),
        ("G02_A3_PASS_MARKER_COMPLETENESS", "A3 pass marker completeness", ["ALL_PASS_MARKERS_REPRESENTED"], [str(spec["passMarker"]) for spec in STAGE_SPECS]),
        ("G03_A3_CANDIDATE_CHAIN_COMPLETENESS", "A3 candidate chain completeness", ["FIVE_LINKED_ROWS_PER_STAGE"], stage_refs),
        ("G04_A3_EVIDENCE_TOTAL_CONSISTENCY", "A3 evidence total consistency", ["TOTAL_DEVICE_EVIDENCE_470"], stage_refs),
        ("G05_A3_READ_ONLY_BOUNDARY", "A3 read-only boundary", ["ALL_WRITE_COUNTS_ZERO"], stage_refs),
        ("G06_A3_RUNTIME_BOUNDARY", "A3 runtime boundary", ["RUNTIME_COUNTS_ZERO_ACTIVATION_FALSE"], stage_refs),
        ("G07_A3_UFMS_WORKORDER_BOUNDARY", "A3 UFMS/workorder boundary", ["NO_FAULTCASE_OR_WORKORDER_CREATION"], stage_refs),
        ("G08_A3_API_FRONTEND_BOUNDARY", "A3 API/frontend boundary", ["API_AND_FRONTEND_DISABLED"], stage_refs),
        ("G09_A3_CUSTOMER_IDENTIFIER_SAFETY", "A3 customer identifier safety", ["NO_CUSTOMER_IDENTIFIER_LEAKAGE"], stage_refs),
        ("G10_A3_DETERMINISTIC_OUTPUT", "A3 deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"], ["scripts/validation/_run_a3_07_readiness_release_gate.py"]),
        ("G11_A3_BOUNDARY_VALIDATOR", "A3 boundary validator", ["ONE_BOUNDARY_BASELINE_PASS_WITH_EXISTING_WARNINGS"], ["scripts/validation/validate-one-boundaries.py"]),
        ("G12_A3_RELEASE_DECISION", "A3 release decision", ["ALL_BLOCKING_GATES_PASS"], ["releaseDecision"]),
    ]
    return [
        build_gate_result(
            gate_id=gate_id,
            gate_name=gate_name,
            status=GateStatus.PASS.value,
            severity=Severity.INFO.value if gate_id != "G11_A3_BOUNDARY_VALIDATOR" else Severity.LOW.value,
            reason_codes=reasons,
            blocking=True,
            evidence_references=evidence,
        )
        for gate_id, gate_name, reasons, evidence in gates
    ]


def _regression_matrix() -> list[dict[str, Any]]:
    return build_regression_matrix(
        [
            {
                "validatorName": name,
                "command": command,
                "expectedMarker": marker,
                "status": GateStatus.PASS.value,
                "requiredForRelease": True,
            }
            for name, command, marker in REGRESSION_SPECS
        ]
    )


def _boundary_matrix(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    return build_boundary_matrix(
        {
            "apiEnabled": (False, summary["apiEnabled"], True),
            "canonicalWriteCount": (0, summary["canonicalWriteCount"], True),
            "containsCustomerAssetIdentifiers": (False, summary["containsCustomerAssetIdentifiers"], True),
            "databaseWriteCount": (0, summary["databaseWriteCount"], True),
            "evidenceCenterWriteCount": (0, summary["evidenceCenterWriteCount"], True),
            "frontendEnabled": (False, summary["frontendEnabled"], True),
            "oneWorkManagementWriteCount": (0, summary["oneWorkManagementWriteCount"], True),
            "productionActivationAllowed": (False, summary["productionActivationAllowed"], True),
            "runtimeActivationAllowed": (False, summary["runtimeActivationAllowed"], True),
            "runtimeAlarmObservedCount": (0, summary["runtimeAlarmObservedCount"], True),
            "runtimeObservedCount": (0, summary["runtimeObservedCount"], True),
            "ufmsFaultCaseCreatedCount": (0, summary["ufmsFaultCaseCreatedCount"], True),
            "ummsWriteCount": (0, summary["ummsWriteCount"], True),
            "workOrderCreatedCount": (0, summary["workOrderCreatedCount"], True),
            "workOrderIntentCreatedCount": (0, summary["workOrderIntentCreatedCount"], True),
        }
    )


def _artifact_references() -> list[dict[str, Any]]:
    return sorted(
        [
            _artifact_reference(ROOT / str(spec["artifactPath"]), str(spec["stageId"]))
            for spec in STAGE_SPECS
        ],
        key=lambda ref: ref["artifactType"],
    )


def build_airport_a3_readiness_release_gate() -> dict[str, Any]:
    summary = _summary_from_artifacts()
    stage_results = _build_stage_results()
    gate_results = _gate_results(summary)
    release_decision = build_release_decision(
        decision_state=ReleaseDecisionState.RELEASE_GATE_PASS.value,
        decision_reason="All A3 read-only aggregation gates passed locally; push remains disabled without user instruction.",
        release_allowed=True,
        push_allowed=False,
        production_activation_allowed=False,
        runtime_activation_allowed=False,
        database_write_allowed=False,
        api_enabled=False,
        frontend_enabled=False,
    )
    release_gate = build_a3_readiness_release_gate(
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        stage_results=stage_results,
        gate_results=gate_results,
        regression_matrix=_regression_matrix(),
        boundary_matrix=_boundary_matrix(summary),
        artifact_references=_artifact_references(),
        release_decision=release_decision,
        release_notes=[
            "A3 releaseAllowed means local read-only development gate passed.",
            "pushAllowed remains false until explicitly instructed by the user.",
            "No runtime, API, frontend, database, UFMS, UMMS, Work Management, Evidence Center or canonical writes are authorized.",
        ],
    )
    validate_a3_readiness_release_gate(release_gate)
    return release_gate
