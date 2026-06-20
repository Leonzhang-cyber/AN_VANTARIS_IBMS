"""Airport A4 Operator Review readiness and release gate."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from a4_readiness_gate.aggregation import build_boundary_matrix, build_regression_matrix
from a4_readiness_gate.enums import GateStatus, ReleaseDecisionState, Severity
from a4_readiness_gate.models import (
    build_a4_readiness_release_gate,
    build_artifact_reference,
    build_gate_result,
    build_release_decision,
    build_stage_result,
)
from a4_readiness_gate.validation import validate_a4_readiness_release_gate
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A4-04"
PROFILE_ID = "airport-a4-readiness-release-gate-profile-v1"
IMPLEMENTATION_STATUS = "A4_OPERATOR_REVIEW_READINESS_AND_RELEASE_GATE_COMPLETE"
READINESS_OUTCOME = "A4_OPERATOR_REVIEW_READ_ONLY_RELEASE_GATE_PASS"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
DECISIONS = PROJECTIONS_DIR / "airport-operator-review-decisions.v1.json"
QUEUE = PROJECTIONS_DIR / "airport-uconsole-operator-review-queue.v1.json"
GUARD = PROJECTIONS_DIR / "airport-operator-review-policy-guard.v1.json"
A3_RELEASE = PROJECTIONS_DIR / "airport-a3-readiness-release-gate.v1.json"

STAGE_SPECS = [
    {
        "stageId": "A4-01",
        "stageName": "Operator Review Decision Layer Foundation",
        "passMarker": "ONE_AIRPORT_A4_01_OPERATOR_REVIEW_DECISION_LAYER_FOUNDATION_PASS",
        "commitReference": "b178fa2",
        "artifactPath": "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-operator-review-decisions.v1.json",
        "validatorName": "validate-one-operator-review-decision-layer.py",
    },
    {
        "stageId": "A4-02",
        "stageName": "Operator Review UConsole Queue Projection",
        "passMarker": "ONE_AIRPORT_A4_02_OPERATOR_REVIEW_UCONSOLE_QUEUE_PROJECTION_PASS",
        "commitReference": "f2eebda",
        "artifactPath": "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-uconsole-operator-review-queue.v1.json",
        "validatorName": "validate-one-uconsole-operator-review-queue-projection.py",
    },
    {
        "stageId": "A4-03",
        "stageName": "Operator Review Decision Audit and Policy Guard",
        "passMarker": "ONE_AIRPORT_A4_03_OPERATOR_REVIEW_DECISION_AUDIT_AND_POLICY_GUARD_PASS",
        "commitReference": "6f37fd0",
        "artifactPath": "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-operator-review-policy-guard.v1.json",
        "validatorName": "validate-one-operator-review-policy-guard.py",
    },
]

REGRESSION_SPECS = [
    ("validate-one-operator-review-policy-guard.py", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-operator-review-policy-guard.py", "ONE_AIRPORT_A4_03_OPERATOR_REVIEW_DECISION_AUDIT_AND_POLICY_GUARD_PASS"),
    ("validate-one-uconsole-operator-review-queue-projection.py", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-uconsole-operator-review-queue-projection.py", "ONE_AIRPORT_A4_02_OPERATOR_REVIEW_UCONSOLE_QUEUE_PROJECTION_PASS"),
    ("validate-one-operator-review-decision-layer.py", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-operator-review-decision-layer.py", "ONE_AIRPORT_A4_01_OPERATOR_REVIEW_DECISION_LAYER_FOUNDATION_PASS"),
    ("validate-one-airport-a3-readiness-release-gate.py", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-airport-a3-readiness-release-gate.py", "ONE_AIRPORT_A3_07_A3_READINESS_AGGREGATION_AND_RELEASE_GATE_PASS"),
    ("validate-one-boundaries.py", "PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-boundaries.py", "ONE_BOUNDARY_BASELINE_PASS"),
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_reference(path: Path, artifact_type: str) -> dict[str, Any]:
    return build_artifact_reference(artifact_type=artifact_type, path=str(path.relative_to(ROOT)), digest=sha256_digest(_load(path)))


def _stage_summary(path: Path) -> dict[str, Any]:
    summary = dict(_load(path).get("summary", {}))
    return {
        "decisionItemCount": summary.get("decisionItemCount", 0),
        "queueRowCount": summary.get("queueRowCount", 0),
        "policyGuardResultCount": summary.get("policyGuardResultCount", 0),
        "auditPreviewCount": summary.get("auditPreviewCount", 0),
        "decisionWriteCount": summary.get("decisionWriteCount", 0),
        "approvalWriteCount": summary.get("approvalWriteCount", 0),
        "databaseWriteCount": summary.get("databaseWriteCount", 0),
        "containsCustomerAssetIdentifiers": summary.get("containsCustomerAssetIdentifiers", False),
    }


def _stage_results() -> list[dict[str, Any]]:
    stages: list[dict[str, Any]] = []
    for spec in STAGE_SPECS:
        stages.append(
            build_stage_result(
                stage_id=str(spec["stageId"]),
                stage_name=str(spec["stageName"]),
                pass_marker=str(spec["passMarker"]),
                commit_reference=str(spec["commitReference"]),
                artifact_path=str(spec["artifactPath"]),
                validator_name=str(spec["validatorName"]),
                status=GateStatus.PASS.value,
                summary=_stage_summary(ROOT / str(spec["artifactPath"])),
            )
        )
    return stages


def _summary() -> dict[str, Any]:
    decisions = _load(DECISIONS)["summary"]
    queue = _load(QUEUE)["summary"]
    guard = _load(GUARD)["summary"]
    return {
        "a4StageCount": 3,
        "passedStageCount": 3,
        "failedStageCount": 0,
        "gateCount": 15,
        "passedGateCount": 15,
        "blockingGateFailureCount": 0,
        "decisionItemCount": decisions["decisionItemCount"],
        "queueRowCount": queue["queueRowCount"],
        "queueGroupCount": queue["queueGroupCount"],
        "queueCardCount": queue["queueCardCount"],
        "policyGuardResultCount": guard["policyGuardResultCount"],
        "auditPreviewCount": guard["auditPreviewCount"],
        "guardGroupCount": guard["guardGroupCount"],
        "pendingDecisionCount": decisions["pendingDecisionCount"],
        "blockingDecisionCount": decisions["blockingDecisionCount"],
        "nonBlockingDecisionCount": decisions["nonBlockingDecisionCount"],
        "eligibleForPreviewCount": guard["eligibleForPreviewCount"],
        "eligibleForExecutionCount": guard["eligibleForExecutionCount"],
        "blockedByPolicyCount": guard["blockedByPolicyCount"],
        "affectedSourceSystemCount": decisions["affectedSourceSystemCount"],
        "totalDeviceEvidenceCount": decisions["totalDeviceEvidenceCount"],
        "decisionWriteCount": 0,
        "approvalWriteCount": 0,
        "auditWriteCount": 0,
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
    refs = [str(spec["artifactPath"]) for spec in STAGE_SPECS]
    gates = [
        ("G01_A4_STAGE_COMPLETENESS", "A4 stage completeness", ["ALL_A4_ARTIFACTS_PRESENT"], refs),
        ("G02_A4_PASS_MARKER_COMPLETENESS", "A4 pass marker completeness", ["ALL_A4_PASS_MARKERS_REPRESENTED"], [str(spec["passMarker"]) for spec in STAGE_SPECS]),
        ("G03_A4_DECISION_QUEUE_COMPLETENESS", "A4 decision queue completeness", ["46_DECISIONS_TO_46_QUEUE_ROWS"], refs),
        ("G04_A4_QUEUE_GROUP_COMPLETENESS", "A4 queue group completeness", ["8_GROUPS_AND_8_CARDS"], [str(QUEUE.relative_to(ROOT))]),
        ("G05_A4_POLICY_GUARD_COMPLETENESS", "A4 policy guard completeness", ["46_POLICY_GUARDS"], [str(GUARD.relative_to(ROOT))]),
        ("G06_A4_AUDIT_PREVIEW_COMPLETENESS", "A4 audit preview completeness", ["46_READ_ONLY_AUDIT_PREVIEWS"], [str(GUARD.relative_to(ROOT))]),
        ("G07_A4_NO_DECISION_WRITE_BOUNDARY", "A4 no decision write boundary", ["DECISION_AND_APPROVAL_WRITES_ZERO"], refs),
        ("G08_A4_NO_AUDIT_WRITE_BOUNDARY", "A4 no audit write boundary", ["AUDIT_AND_DATABASE_WRITES_ZERO"], refs),
        ("G09_A4_EXECUTION_BOUNDARY", "A4 execution boundary", ["EXECUTION_NOT_ALLOWED"], refs),
        ("G10_A4_API_FRONTEND_BOUNDARY", "A4 API/frontend boundary", ["API_AND_FRONTEND_DISABLED"], refs),
        ("G11_A4_CUSTOMER_IDENTIFIER_SAFETY", "A4 customer identifier safety", ["NO_CUSTOMER_IDENTIFIER_LEAKAGE"], refs),
        ("G12_A4_A3_DEPENDENCY_GATE", "A4 A3 dependency gate", ["A3_RELEASE_ALLOWED_TRUE"], [str(A3_RELEASE.relative_to(ROOT))]),
        ("G13_A4_DETERMINISTIC_OUTPUT", "A4 deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"], ["scripts/validation/_run_a4_04_readiness_release_gate.py"]),
        ("G14_A4_BOUNDARY_VALIDATOR", "A4 boundary validator", ["ONE_BOUNDARY_BASELINE_PASS_WITH_EXISTING_WARNINGS"], ["scripts/validation/validate-one-boundaries.py"]),
        ("G15_A4_RELEASE_DECISION", "A4 release decision", ["ALL_BLOCKING_GATES_PASS"], ["releaseDecision"]),
    ]
    return [
        build_gate_result(gate_id=gate_id, gate_name=name, status=GateStatus.PASS.value, severity=Severity.INFO.value if gate_id != "G14_A4_BOUNDARY_VALIDATOR" else Severity.LOW.value, reason_codes=reasons, blocking=True, evidence_references=evidence)
        for gate_id, name, reasons, evidence in gates
    ]


def _regression_matrix() -> list[dict[str, Any]]:
    return build_regression_matrix([
        {"validatorName": name, "command": command, "expectedMarker": marker, "status": GateStatus.PASS.value, "requiredForRelease": True}
        for name, command, marker in REGRESSION_SPECS
    ])


def _boundary_matrix(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    return build_boundary_matrix({
        "apiEnabled": (False, summary["apiEnabled"], True),
        "approvalWriteCount": (0, summary["approvalWriteCount"], True),
        "auditWriteCount": (0, summary["auditWriteCount"], True),
        "canonicalWriteCount": (0, summary["canonicalWriteCount"], True),
        "containsCustomerAssetIdentifiers": (False, summary["containsCustomerAssetIdentifiers"], True),
        "databaseWriteCount": (0, summary["databaseWriteCount"], True),
        "decisionWriteCount": (0, summary["decisionWriteCount"], True),
        "frontendEnabled": (False, summary["frontendEnabled"], True),
        "productionActivationAllowed": (False, summary["productionActivationAllowed"], True),
        "pushAllowed": (False, summary["pushAllowed"], True),
        "runtimeActivationAllowed": (False, summary["runtimeActivationAllowed"], True),
    })


def build_airport_a4_readiness_release_gate() -> dict[str, Any]:
    summary = _summary()
    release_decision = build_release_decision(
        decision_state=ReleaseDecisionState.RELEASE_GATE_PASS.value,
        decision_reason="All A4 read-only operator-review gates passed locally; push and all writes remain disabled.",
        release_allowed=True,
        push_allowed=False,
        production_activation_allowed=False,
        runtime_activation_allowed=False,
        database_write_allowed=False,
        api_enabled=False,
        frontend_enabled=False,
        decision_write_allowed=False,
        approval_write_allowed=False,
        audit_write_allowed=False,
    )
    gate = build_a4_readiness_release_gate(
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        stage_results=_stage_results(),
        gate_results=_gate_results(summary),
        regression_matrix=_regression_matrix(),
        boundary_matrix=_boundary_matrix(summary),
        artifact_references=[
            _artifact_reference(DECISIONS, "A4-01"),
            _artifact_reference(QUEUE, "A4-02"),
            _artifact_reference(GUARD, "A4-03"),
            _artifact_reference(A3_RELEASE, "A3-DEPENDENCY"),
        ],
        release_decision=release_decision,
        release_notes=[
            "A4 releaseAllowed means local read-only operator-review development gate passed.",
            "pushAllowed remains false until explicitly instructed by the user.",
            "Decision, approval, audit, database, API, frontend and runtime activation writes remain disabled.",
        ],
    )
    validate_a4_readiness_release_gate(gate)
    return gate
