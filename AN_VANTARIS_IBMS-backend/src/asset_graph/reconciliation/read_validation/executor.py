"""Offline limited read validation executor."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from ..models import sha256_digest
from ..readiness import assess_readiness, load_readiness_policy
from ..evidence.runner import EvidencePackageError, run_device_reconciliation_evidence
from .artifacts import write_output_artifacts
from .models import (
    AUTHORITY,
    EXECUTION_NAME,
    EXECUTION_VERSION,
    ExecutionRequest,
    ExecutionResult,
    PreExecutionGateResult,
    RollbackEvidence,
    WRITE_CUTOVER_STATUS,
)
from .policies import OutputPolicyError, validate_output_directory
from .pre_execution import package_boundary_gates, verify_pre_execution


def _blocked_result(
    request: ExecutionRequest,
    plan: Mapping[str, Any],
    gates: tuple[PreExecutionGateResult, ...],
    *,
    reason: str,
) -> ExecutionResult:
    scope = plan.get("scopeSummary", {})
    rollback = RollbackEvidence(
        rollback_required=False,
        rollback_reason=reason,
        in_memory_state_discarded=True,
        source_data_unchanged=True,
        canonical_data_unchanged=True,
        artifacts_retained_or_removed="NONE_GENERATED",
    )
    return ExecutionResult(
        execution_name=EXECUTION_NAME,
        execution_version=EXECUTION_VERSION,
        authority=AUTHORITY,
        contract_version=str(plan.get("contractVersion", "")),
        plan_digest=str(plan.get("resultDigest", "")),
        scope_digest=request.scope_digest,
        evidence_digest=request.evidence_digest,
        readiness_result_digest=request.readiness_result_digest,
        mapping_version=request.mapping_version,
        run_id=request.run_id,
        execution_state="EXECUTION_BLOCKED",
        pre_execution_gate_results=gates,
        source_counts={},
        projection_counts={},
        relationship_metrics={},
        readiness_decision=str(plan.get("readinessDecision", "")),
        validation_outcome="EXECUTION_BLOCKED",
        output_artifacts=(),
        retention_disposition=str(scope.get("retentionPolicy", "")),
        rollback_disposition=rollback.serialize(),
        write_cutover_status=WRITE_CUTOVER_STATUS,
        result_digest="",
    )


def _validation_outcome(
    reconciliation_report: Mapping[str, Any],
    readiness_assessment: Mapping[str, Any],
) -> str:
    if readiness_assessment.get("decision") in {"NOT_READY", "INPUT_REJECTED"}:
        return "VALIDATION_FAILED"
    if reconciliation_report.get("blockers"):
        return "VALIDATION_FAILED"
    review_count = int(readiness_assessment.get("reviewCount", 0))
    if review_count > 0 or reconciliation_report.get("reviews"):
        return "VALIDATION_COMPLETE_WITH_REVIEWS"
    return "VALIDATION_COMPLETE"


def execute_limited_read_validation(request: ExecutionRequest) -> ExecutionResult:
    root = Path(request.root).resolve()
    plan = json.loads(Path(request.plan_path).read_text(encoding="utf-8"))
    readiness = json.loads(Path(request.readiness_path).read_text(encoding="utf-8"))
    output_dir = Path(request.output_dir).resolve()
    scope = plan.get("scopeSummary", {})

    pre_gates = verify_pre_execution(
        plan,
        readiness,
        evidence_digest=request.evidence_digest,
        readiness_result_digest=request.readiness_result_digest,
        scope_digest=request.scope_digest,
        mapping_version=request.mapping_version,
        evaluation_instant=request.evaluation_instant,
    )
    if any(gate.status != "PASS" for gate in pre_gates):
        return _blocked_result(
            request,
            plan,
            pre_gates,
            reason="pre-execution verification failed",
        )

    try:
        validate_output_directory(output_dir, output_location_policy=str(scope.get("outputLocationPolicy", "")))
    except OutputPolicyError as exc:
        failed = pre_gates + (
            PreExecutionGateResult(
                gate_code="OUTPUT_LOCATION_POLICY_GATE",
                status="FAIL",
                blocking=True,
                observed_value=str(output_dir),
                required_value=str(exc),
            ),
        )
        return _blocked_result(request, plan, failed, reason=str(exc))

    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = Path(request.evidence_path).resolve()
    package = json.loads(evidence_path.read_text(encoding="utf-8"))
    boundary_gates = package_boundary_gates(package, scope)
    all_pre_gates = pre_gates + boundary_gates
    if any(gate.status != "PASS" for gate in boundary_gates):
        return _blocked_result(
            request,
            plan,
            all_pre_gates,
            reason="package boundary verification failed",
        )

    reconciliation_path = output_dir / "reconciliation-report.json"
    try:
        reconciliation_report = run_device_reconciliation_evidence(
            root=root,
            input_path=evidence_path,
            output_path=reconciliation_path,
            run_id=request.run_id,
        )
    except EvidencePackageError as exc:
        failed = all_pre_gates + (
            PreExecutionGateResult(
                gate_code="SOURCE_PACKAGE_VALIDATION_GATE",
                status="FAIL",
                blocking=True,
                observed_value=exc.code,
                required_value="valid sanitized source package",
            ),
        )
        return _blocked_result(request, plan, failed, reason=str(exc))

    if reconciliation_report.get("resultDigest") != request.evidence_digest:
        failed = all_pre_gates + (
            PreExecutionGateResult(
                gate_code="EVIDENCE_DIGEST_MATCH_GATE",
                status="FAIL",
                blocking=True,
                observed_value=str(reconciliation_report.get("resultDigest", "")),
                required_value=request.evidence_digest,
            ),
        )
        return _blocked_result(request, plan, failed, reason="generated evidence digest mismatch")

    policy = load_readiness_policy(root=root)
    readiness_assessment = assess_readiness(
        reconciliation_report,
        policy,
        determinism_confirmed=True,
    ).serialize()

    validation_outcome = _validation_outcome(reconciliation_report, readiness_assessment)
    final_state = validation_outcome if validation_outcome != "EXECUTION_BLOCKED" else "VALIDATION_FAILED"

    rollback = RollbackEvidence(
        rollback_required=True,
        rollback_reason=str(scope.get("rollbackPolicy", "DISCARD_IN_MEMORY_PROJECTION_NO_PERSISTENCE")),
        in_memory_state_discarded=True,
        source_data_unchanged=True,
        canonical_data_unchanged=True,
        artifacts_retained_or_removed=str(scope.get("retentionPolicy", "")),
    )

    execution_payload = {
        "executionName": EXECUTION_NAME,
        "executionVersion": EXECUTION_VERSION,
        "authority": AUTHORITY,
        "contractVersion": str(plan.get("contractVersion", "")),
        "planDigest": str(plan.get("resultDigest", "")),
        "scopeDigest": request.scope_digest,
        "evidenceDigest": request.evidence_digest,
        "readinessResultDigest": request.readiness_result_digest,
        "mappingVersion": request.mapping_version,
        "runId": request.run_id,
        "executionState": final_state,
        "preExecutionGateResults": [item.serialize() for item in all_pre_gates],
        "sourceCounts": {
            "deviceCount": package.get("sourceSummary", {}).get("deviceCount", 0),
            "recordCount": package.get("sourceSummary", {}).get("recordCount", 0),
        },
        "projectionCounts": reconciliation_report.get("projectionSummary", {}),
        "relationshipMetrics": reconciliation_report.get("relationshipMetrics", {}),
        "readinessDecision": readiness_assessment.get("decision"),
        "validationOutcome": validation_outcome,
        "retentionDisposition": str(scope.get("retentionPolicy", "")),
        "rollbackDisposition": rollback.serialize(),
        "writeCutoverStatus": WRITE_CUTOVER_STATUS,
    }

    result = ExecutionResult(
        execution_name=EXECUTION_NAME,
        execution_version=EXECUTION_VERSION,
        authority=AUTHORITY,
        contract_version=str(plan.get("contractVersion", "")),
        plan_digest=str(plan.get("resultDigest", "")),
        scope_digest=request.scope_digest,
        evidence_digest=request.evidence_digest,
        readiness_result_digest=request.readiness_result_digest,
        mapping_version=request.mapping_version,
        run_id=request.run_id,
        execution_state=final_state,
        pre_execution_gate_results=all_pre_gates,
        source_counts=execution_payload["sourceCounts"],
        projection_counts=dict(execution_payload["projectionCounts"]),
        relationship_metrics=dict(execution_payload["relationshipMetrics"]),
        readiness_decision=str(readiness_assessment.get("decision", "")),
        validation_outcome=validation_outcome,
        output_artifacts=(),
        retention_disposition=str(scope.get("retentionPolicy", "")),
        rollback_disposition=rollback.serialize(),
        write_cutover_status=WRITE_CUTOVER_STATUS,
        result_digest="",
    )
    serialized = result.serialize()
    artifacts = write_output_artifacts(
        output_dir,
        execution_result=serialized,
        reconciliation_report=reconciliation_report,
        readiness_assessment=readiness_assessment,
        retention_class=str(scope.get("retentionPolicy", "")),
    )
    final_payload = result.serialize()
    final_payload["outputArtifacts"] = [item.serialize() for item in artifacts]
    final_payload["resultDigest"] = sha256_digest(
        {key: value for key, value in final_payload.items() if key != "resultDigest"}
    )
    from .artifacts import write_json

    write_json(output_dir / "execution-result.json", final_payload)
    return ExecutionResult(
        execution_name=result.execution_name,
        execution_version=result.execution_version,
        authority=result.authority,
        contract_version=result.contract_version,
        plan_digest=result.plan_digest,
        scope_digest=result.scope_digest,
        evidence_digest=result.evidence_digest,
        readiness_result_digest=result.readiness_result_digest,
        mapping_version=result.mapping_version,
        run_id=result.run_id,
        execution_state=result.execution_state,
        pre_execution_gate_results=result.pre_execution_gate_results,
        source_counts=result.source_counts,
        projection_counts=result.projection_counts,
        relationship_metrics=result.relationship_metrics,
        readiness_decision=result.readiness_decision,
        validation_outcome=result.validation_outcome,
        output_artifacts=artifacts,
        retention_disposition=result.retention_disposition,
        rollback_disposition=result.rollback_disposition,
        write_cutover_status=result.write_cutover_status,
        result_digest=final_payload["resultDigest"],
    )
