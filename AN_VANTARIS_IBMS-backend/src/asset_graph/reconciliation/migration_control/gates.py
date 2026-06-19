"""Read migration execution precondition gate evaluation."""
from __future__ import annotations

from typing import Any, Mapping

from .models import ApprovalRecord, ControlInput, ExecutionScope, PreconditionResult


def _result(
    gate_code: str,
    *,
    status: str,
    observed: str,
    required: str,
    blocking: bool,
    remediation: str = "MIGRATION_CONTROL",
) -> PreconditionResult:
    return PreconditionResult(
        gate_code=gate_code,
        status=status,
        blocking=blocking,
        observed_value=observed,
        required_value=required,
        remediation_category=remediation,
    )


def _active_approvals(approvals: tuple[ApprovalRecord, ...]) -> tuple[ApprovalRecord, ...]:
    return tuple(item for item in approvals if item.status == "ACTIVE")


def _requirements_for_input(control_input: ControlInput, contract: Mapping[str, Any]) -> Mapping[str, Any]:
    if control_input.evidence_classification == "REAL_SANITIZED_EVIDENCE":
        return contract["realReadMigrationCandidateRequirements"]
    return contract["syntheticLimitedReadValidationRequirements"]


def evaluate_precondition_gates(
    control_input: ControlInput,
    contract: Mapping[str, Any],
) -> tuple[PreconditionResult, ...]:
    requirements = _requirements_for_input(control_input, contract)
    scope = control_input.execution_scope
    scope_digest = scope.scope_digest()
    active = _active_approvals(control_input.approvals)
    rel = control_input.relationship_invariant_summary
    rel_req = contract.get("relationshipInvariantRequirements", {})
    forbidden_ops = set(contract.get("forbiddenOperations", ()))
    allowed_ops = set(contract.get("allowedOperations", ()))
    forbidden_intents = set(contract.get("forbiddenMigrationIntents", ()))

    readiness_ok = control_input.readiness_decision == requirements["readinessDecision"]
    classification_ok = control_input.evidence_classification == requirements["evidenceClassification"]
    synthetic_production_blocked = (
        control_input.evidence_classification == "SYNTHETIC_REPRESENTATIVE_ONLY"
        and control_input.migration_intent in forbidden_intents
    )
    classification_gate_ok = classification_ok and not synthetic_production_blocked

    gates = [
        _result(
            "READINESS_RESULT_GATE",
            status="PASS" if readiness_ok else "FAIL",
            observed=control_input.readiness_decision,
            required=requirements["readinessDecision"],
            blocking=True,
        ),
        _result(
            "EVIDENCE_CLASSIFICATION_GATE",
            status="PASS" if classification_gate_ok else "FAIL",
            observed=f"classification={control_input.evidence_classification};intent={control_input.migration_intent}",
            required=f"classification={requirements['evidenceClassification']};syntheticProductionProhibited=true",
            blocking=True,
        ),
        _result(
            "EVIDENCE_DIGEST_GATE",
            status="PASS" if control_input.evidence_digest else "FAIL",
            observed=control_input.evidence_digest or "missing",
            required="non-empty evidence digest",
            blocking=True,
        ),
        _result(
            "POLICY_VERSION_GATE",
            status="PASS"
            if control_input.readiness_policy_version in contract.get("supportedReadinessPolicyVersions", ())
            else "FAIL",
            observed=control_input.readiness_policy_version,
            required=",".join(contract.get("supportedReadinessPolicyVersions", ())),
            blocking=True,
        ),
        _result(
            "MAPPING_VERSION_GATE",
            status="PASS"
            if control_input.mapping_version in contract.get("supportedMappingVersions", ())
            and control_input.mapping_version == scope.mapping_version
            else "FAIL",
            observed=f"input={control_input.mapping_version};scope={scope.mapping_version}",
            required=",".join(contract.get("supportedMappingVersions", ())),
            blocking=True,
        ),
        _result(
            "DETERMINISM_GATE",
            status="PASS" if control_input.deterministic_verification_confirmed else "FAIL",
            observed=f"confirmed={control_input.deterministic_verification_confirmed}",
            required="confirmed=true",
            blocking=True,
        ),
        _result(
            "HARD_BLOCKER_GATE",
            status="PASS"
            if control_input.hard_blocker_count <= int(requirements["hardBlockerMaximum"])
            else "FAIL",
            observed=str(control_input.hard_blocker_count),
            required=f"<={requirements['hardBlockerMaximum']}",
            blocking=True,
        ),
        _result(
            "RELATIONSHIP_INVARIANT_GATE",
            status="PASS"
            if rel.get("duplicateCanonicalRelationshipCount", 0)
            <= int(rel_req.get("duplicateCanonicalRelationshipMaximum", 0))
            and (
                rel.get("hasPointParityValid", False)
                if rel_req.get("hasPointParityRequired")
                else True
            )
            and (
                rel.get("unresolvedRelationshipCount", 0)
                <= int(rel_req.get("unresolvedRelationshipMaximumForSynthetic", 0))
                if control_input.evidence_classification != "REAL_SANITIZED_EVIDENCE"
                else rel.get("unresolvedRelationshipCount", 0) == 0
            )
            else "FAIL",
            observed=(
                f"parity={rel.get('hasPointParityValid')};"
                f"unresolved={rel.get('unresolvedRelationshipCount')};"
                f"duplicate={rel.get('duplicateCanonicalRelationshipCount')}"
            ),
            required="relationship invariants satisfied for classification",
            blocking=True,
        ),
        _result(
            "SCOPE_DECLARATION_GATE",
            status="PASS"
            if scope.tenant_scope and scope.site_scope and scope.source_system_scope and scope.approval_expiry
            else "FAIL",
            observed=f"tenant={bool(scope.tenant_scope)};site={bool(scope.site_scope)};expiry={bool(scope.approval_expiry)}",
            required="explicit tenant, site, source-system, and approval expiry",
            blocking=True,
        ),
        _result(
            "COUNT_BOUNDARY_GATE",
            status="PASS"
            if control_input.source_count_summary.get("deviceCount", 0) <= scope.maximum_device_count
            and control_input.projected_count_summary.get("projectedPointCount", 0) <= scope.maximum_point_count
            else "FAIL",
            observed=(
                f"devices={control_input.source_count_summary.get('deviceCount')}/"
                f"{scope.maximum_device_count};points="
                f"{control_input.projected_count_summary.get('projectedPointCount')}/"
                f"{scope.maximum_point_count}"
            ),
            required="counts within declared scope boundaries",
            blocking=True,
        ),
        _result(
            "APPROVAL_PRESENT_GATE",
            status="PASS" if _approval_roles_present(active, requirements) else "FAIL",
            observed=_approval_roles_observed(active),
            required=",".join(requirements.get("requiredApprovalRoles", ())),
            blocking=False,
        ),
        _result(
            "APPROVAL_SCOPE_MATCH_GATE",
            status="PASS" if _approval_scope_matches(active, scope_digest, control_input) else "FAIL",
            observed=_approval_scope_observed(active, scope_digest),
            required=f"scopeDigest={scope_digest}",
            blocking=False,
        ),
        _result(
            "APPROVAL_EXPIRY_GATE",
            status="PASS" if _approval_not_expired(active, control_input.evaluation_instant) else "FAIL",
            observed=_approval_expiry_observed(active, control_input.evaluation_instant),
            required=f"expiresAt>{control_input.evaluation_instant}",
            blocking=False,
        ),
        _result(
            "ROLLBACK_PLAN_GATE",
            status="PASS"
            if len(scope.rollback_policy.strip())
            >= int(contract.get("rollbackPolicyMinimumLength", 8))
            else "FAIL",
            observed=str(len(scope.rollback_policy.strip())),
            required=f">={contract.get('rollbackPolicyMinimumLength', 8)}",
            blocking=True,
        ),
        _result(
            "RETENTION_POLICY_GATE",
            status="PASS"
            if len(scope.retention_policy.strip())
            >= int(contract.get("retentionPolicyMinimumLength", 8))
            else "FAIL",
            observed=str(len(scope.retention_policy.strip())),
            required=f">={contract.get('retentionPolicyMinimumLength', 8)}",
            blocking=True,
        ),
        _result(
            "FORBIDDEN_OPERATION_GATE",
            status="PASS"
            if not forbidden_ops.intersection(control_input.requested_operations)
            and not forbidden_ops.intersection(scope.allowed_operations)
            and not set(scope.allowed_operations) - allowed_ops
            else "FAIL",
            observed=",".join(
                sorted(
                    forbidden_ops.intersection(control_input.requested_operations)
                    | forbidden_ops.intersection(scope.allowed_operations)
                    | (set(scope.allowed_operations) - allowed_ops)
                )
            )
            or "none",
            required="no forbidden operations requested",
            blocking=True,
        ),
        _result(
            "WRITE_CUTOVER_PROHIBITION_GATE",
            status="PASS"
            if control_input.write_cutover_status == requirements["writeCutoverStatus"]
            and "APPROVE_WRITE_CUTOVER" not in control_input.requested_operations
            and control_input.migration_intent not in forbidden_intents
            else "FAIL",
            observed=(
                f"status={control_input.write_cutover_status};"
                f"intent={control_input.migration_intent};"
                f"requested={','.join(control_input.requested_operations) or 'none'}"
            ),
            required=f"status={requirements['writeCutoverStatus']};no write-cutover intent or operation",
            blocking=True,
        ),
    ]

    return tuple(gates)


def _approval_roles_present(active: tuple[ApprovalRecord, ...], requirements: Mapping[str, Any]) -> bool:
    required_roles = set(requirements.get("requiredApprovalRoles", ()))
    required_types = set(requirements.get("requiredApprovalTypes", ()))
    present_roles = {item.approved_by_role for item in active if item.approval_type in required_types}
    return required_roles.issubset(present_roles)


def _approval_roles_observed(active: tuple[ApprovalRecord, ...]) -> str:
    if not active:
        return "none"
    return ",".join(f"{item.approved_by_role}:{item.approval_type}" for item in active)


def _approval_scope_matches(
    active: tuple[ApprovalRecord, ...],
    scope_digest: str,
    control_input: ControlInput,
) -> bool:
    if not active:
        return False
    for item in active:
        if item.scope_digest != scope_digest:
            return False
        if item.evidence_digest != control_input.evidence_digest:
            return False
        if item.readiness_result_digest != control_input.readiness_result_digest:
            return False
    return True


def _approval_scope_observed(active: tuple[ApprovalRecord, ...], scope_digest: str) -> str:
    if not active:
        return "none"
    return ",".join(item.scope_digest for item in active) + f";expected={scope_digest}"


def _approval_not_expired(active: tuple[ApprovalRecord, ...], evaluation_instant: str) -> bool:
    if not active:
        return False
    return all(item.expires_at > evaluation_instant for item in active)


def _approval_expiry_observed(active: tuple[ApprovalRecord, ...], evaluation_instant: str) -> str:
    if not active:
        return "none"
    return ",".join(f"{item.approval_id}:{item.expires_at}" for item in active) + f";now={evaluation_instant}"
