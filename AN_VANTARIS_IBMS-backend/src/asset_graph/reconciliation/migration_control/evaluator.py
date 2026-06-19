"""Evaluate controlled read migration execution plans."""
from __future__ import annotations

from typing import Any, Mapping

from ..models import sha256_digest
from .gates import evaluate_precondition_gates
from .models import ControlInput, ExecutionPlanResult, PreconditionResult

PLAN_NAME = "VANTARIS ONE Asset Graph Controlled Read Migration Execution Plan"
PLAN_VERSION = "1.0.0"
AUTHORITY = "ONE-A5-P1-16L"


def _failed_preconditions(gates: tuple[PreconditionResult, ...]) -> tuple[str, ...]:
    return tuple(gate.gate_code for gate in gates if gate.status != "PASS")


def _approval_status(gates: tuple[PreconditionResult, ...]) -> str:
    approval_gates = {
        "APPROVAL_PRESENT_GATE",
        "APPROVAL_SCOPE_MATCH_GATE",
        "APPROVAL_EXPIRY_GATE",
    }
    approval_results = [gate for gate in gates if gate.gate_code in approval_gates]
    if not approval_results:
        return "NOT_REQUIRED"
    if all(gate.status == "PASS" for gate in approval_results):
        return "APPROVED"
    if any(gate.gate_code == "APPROVAL_PRESENT_GATE" and gate.status == "FAIL" for gate in approval_results):
        return "MISSING"
    return "INVALID"


def _determine_execution_state(
    control_input: ControlInput,
    contract: Mapping[str, Any],
    gates: tuple[PreconditionResult, ...],
) -> str:
    failed = _failed_preconditions(gates)
    blocking_failures = tuple(
        gate.gate_code for gate in gates if gate.status != "PASS" and gate.blocking
    )
    approval_status = _approval_status(gates)

    if not control_input.evidence_digest or not control_input.readiness_result_digest:
        return "WAITING_FOR_EVIDENCE"
    if control_input.readiness_decision in {"NOT_READY", "INPUT_REJECTED", "UNKNOWN"}:
        return "EXECUTION_BLOCKED"
    if control_input.readiness_decision not in {
        "READY_FOR_LIMITED_READ_VALIDATION",
        "READY_FOR_READ_MIGRATION_CANDIDATE",
        "READY_WITH_REMEDIATION",
    }:
        return "WAITING_FOR_READINESS"
    if blocking_failures:
        return "EXECUTION_BLOCKED"
    if approval_status == "MISSING":
        return "WAITING_FOR_APPROVAL"
    if approval_status == "INVALID":
        return "EXECUTION_BLOCKED"
    if failed:
        return "EXECUTION_BLOCKED"

    requirements = (
        contract["realReadMigrationCandidateRequirements"]
        if control_input.evidence_classification == "REAL_SANITIZED_EVIDENCE"
        else contract["syntheticLimitedReadValidationRequirements"]
    )
    return str(requirements["approvedExecutionState"])


def evaluate_execution_plan(
    control_input: ControlInput,
    contract: Mapping[str, Any],
) -> ExecutionPlanResult:
    gates = evaluate_precondition_gates(control_input, contract)
    failed = _failed_preconditions(gates)
    execution_state = _determine_execution_state(control_input, contract, gates)
    if execution_state in contract.get("forbiddenExecutionStates", ()):
        execution_state = "EXECUTION_BLOCKED"
    scope = control_input.execution_scope
    payload = {
        "planName": PLAN_NAME,
        "planVersion": PLAN_VERSION,
        "authority": AUTHORITY,
        "contractVersion": str(contract.get("contractVersion", "")),
        "readinessDecision": control_input.readiness_decision,
        "evidenceClassification": control_input.evidence_classification,
        "executionState": execution_state,
        "approvalStatus": _approval_status(gates),
        "scopeSummary": scope.serialize(),
        "allowedOperations": list(scope.allowed_operations),
        "forbiddenOperations": list(scope.forbidden_operations or contract.get("forbiddenOperations", ())),
        "preconditions": [item.serialize() for item in gates],
        "failedPreconditions": list(failed),
        "rollbackRequirements": [scope.rollback_policy],
        "retentionRequirements": [scope.retention_policy],
        "writeCutoverStatus": str(contract.get("writeCutoverStatus", "NOT_READY_FOR_WRITE_CUTOVER")),
    }
    return ExecutionPlanResult(
        plan_name=PLAN_NAME,
        plan_version=PLAN_VERSION,
        authority=AUTHORITY,
        contract_version=str(contract.get("contractVersion", "")),
        readiness_decision=control_input.readiness_decision,
        evidence_classification=control_input.evidence_classification,
        execution_state=execution_state,
        approval_status=_approval_status(gates),
        scope_summary=scope.serialize(),
        allowed_operations=scope.allowed_operations,
        forbidden_operations=tuple(scope.forbidden_operations or contract.get("forbiddenOperations", ())),
        preconditions=gates,
        failed_preconditions=failed,
        rollback_requirements=(scope.rollback_policy,),
        retention_requirements=(scope.retention_policy,),
        write_cutover_status=str(contract.get("writeCutoverStatus", "NOT_READY_FOR_WRITE_CUTOVER")),
        result_digest=sha256_digest(payload),
    )
