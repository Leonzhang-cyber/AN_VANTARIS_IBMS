"""Pre-execution verification for limited read validation."""
from __future__ import annotations

from typing import Any, Mapping

from .models import (
    ACCEPTED_PLAN_STATE,
    PreExecutionGateResult,
    WRITE_CUTOVER_STATUS,
)

FORBIDDEN_OPERATIONS = frozenset({
    "WRITE_LEGACY",
    "WRITE_CANONICAL",
    "CREATE_DATABASE_SCHEMA",
    "ALTER_DATABASE_SCHEMA",
    "RUN_MIGRATION",
    "ENABLE_DUAL_WRITE",
    "MODIFY_SOURCE_DATA",
    "PUBLISH_PUBLIC_API",
    "APPROVE_WRITE_CUTOVER",
})

SYNTHETIC_APPROVAL_TYPES = frozenset({"SYNTHETIC_LIMITED_READ_VALIDATION"})
REAL_APPROVAL_TYPES = frozenset({"REAL_READ_MIGRATION_CANDIDATE_REVIEW", "REAL_LIMITED_READ_VALIDATION"})


def _gate(
    gate_code: str,
    *,
    status: str,
    observed: str,
    required: str,
    blocking: bool = True,
) -> PreExecutionGateResult:
    return PreExecutionGateResult(
        gate_code=gate_code,
        status=status,
        blocking=blocking,
        observed_value=observed,
        required_value=required,
    )


def verify_pre_execution(
    plan: Mapping[str, Any],
    readiness: Mapping[str, Any],
    *,
    evidence_digest: str,
    readiness_result_digest: str,
    scope_digest: str,
    mapping_version: str,
    evaluation_instant: str,
) -> tuple[PreExecutionGateResult, ...]:
    scope = plan.get("scopeSummary", {})
    allowed_ops = set(plan.get("allowedOperations", ()))
    classification = str(plan.get("evidenceClassification", readiness.get("evidenceClassification", "")))

    gates = [
        _gate(
            "PLAN_FORMAT_GATE",
            status="PASS" if plan.get("planName") and plan.get("planVersion") == "1.0.0" else "FAIL",
            observed=f"name={bool(plan.get('planName'))};version={plan.get('planVersion')}",
            required="planName present;planVersion=1.0.0",
        ),
        _gate(
            "EXECUTION_STATE_GATE",
            status="PASS" if plan.get("executionState") == ACCEPTED_PLAN_STATE else "FAIL",
            observed=str(plan.get("executionState", "")),
            required=ACCEPTED_PLAN_STATE,
        ),
        _gate(
            "APPROVAL_STATUS_GATE",
            status="PASS" if plan.get("approvalStatus") == "APPROVED" else "FAIL",
            observed=str(plan.get("approvalStatus", "")),
            required="APPROVED",
        ),
        _gate(
            "APPROVAL_TYPE_GATE",
            status="PASS" if _approval_type_compatible(classification) else "FAIL",
            observed=classification,
            required="classification compatible with limited read validation approval path",
        ),
        _gate(
            "APPROVAL_EXPIRY_GATE",
            status="PASS" if str(scope.get("approvalExpiry", "")) > evaluation_instant else "FAIL",
            observed=f"{scope.get('approvalExpiry')};now={evaluation_instant}",
            required=f"approvalExpiry>{evaluation_instant}",
        ),
        _gate(
            "SCOPE_DIGEST_GATE",
            status="PASS" if scope.get("scopeDigest") == scope_digest else "FAIL",
            observed=str(scope_digest),
            required=str(scope.get("scopeDigest", "")),
        ),
        _gate(
            "EVIDENCE_DIGEST_GATE",
            status="PASS"
            if evidence_digest and evidence_digest == readiness.get("evidenceDigest")
            else "FAIL",
            observed=str(evidence_digest or "missing"),
            required=str(readiness.get("evidenceDigest", "")),
        ),
        _gate(
            "READINESS_DIGEST_GATE",
            status="PASS"
            if readiness_result_digest and readiness_result_digest == readiness.get("resultDigest")
            else "FAIL",
            observed=str(readiness_result_digest or "missing"),
            required=str(readiness.get("resultDigest", "")),
        ),
        _gate(
            "MAPPING_VERSION_GATE",
            status="PASS"
            if mapping_version and mapping_version == scope.get("mappingVersion")
            else "FAIL",
            observed=f"request={mapping_version};scope={scope.get('mappingVersion')}",
            required=str(scope.get("mappingVersion", "")),
        ),
        _gate(
            "TENANT_SCOPE_GATE",
            status="PASS" if scope.get("tenantScope") else "FAIL",
            observed=str(scope.get("tenantScope", "")),
            required="non-empty tenantScope",
        ),
        _gate(
            "SITE_SCOPE_GATE",
            status="PASS" if scope.get("siteScope") else "FAIL",
            observed=str(scope.get("siteScope", "")),
            required="non-empty siteScope",
        ),
        _gate(
            "SOURCE_SYSTEM_SCOPE_GATE",
            status="PASS" if scope.get("sourceSystemScope") else "FAIL",
            observed=str(scope.get("sourceSystemScope", "")),
            required="non-empty sourceSystemScope",
        ),
        _gate(
            "ROLLBACK_POLICY_GATE",
            status="PASS" if len(str(scope.get("rollbackPolicy", "")).strip()) >= 8 else "FAIL",
            observed=str(len(str(scope.get("rollbackPolicy", "")).strip())),
            required=">=8",
        ),
        _gate(
            "RETENTION_POLICY_GATE",
            status="PASS" if len(str(scope.get("retentionPolicy", "")).strip()) >= 8 else "FAIL",
            observed=str(len(str(scope.get("retentionPolicy", "")).strip())),
            required=">=8",
        ),
        _gate(
            "OUTPUT_LOCATION_POLICY_GATE",
            status="PASS" if scope.get("outputLocationPolicy") == "OFFLINE_AGGREGATE_EXPORT_ONLY" else "FAIL",
            observed=str(scope.get("outputLocationPolicy", "")),
            required="OFFLINE_AGGREGATE_EXPORT_ONLY",
        ),
        _gate(
            "FORBIDDEN_OPERATION_GATE",
            status="PASS" if not FORBIDDEN_OPERATIONS.intersection(allowed_ops) else "FAIL",
            observed=",".join(sorted(FORBIDDEN_OPERATIONS.intersection(allowed_ops))) or "none",
            required="no forbidden operations in plan allowedOperations",
        ),
        _gate(
            "WRITE_CUTOVER_PROHIBITION_GATE",
            status="PASS"
            if plan.get("writeCutoverStatus") == WRITE_CUTOVER_STATUS
            and "APPROVE_WRITE_CUTOVER" not in allowed_ops
            else "FAIL",
            observed=f"status={plan.get('writeCutoverStatus')};allowed={','.join(sorted(allowed_ops)) or 'none'}",
            required=f"status={WRITE_CUTOVER_STATUS};no APPROVE_WRITE_CUTOVER",
        ),
    ]
    return tuple(gates)


def _approval_type_compatible(classification: str) -> bool:
    if classification == "SYNTHETIC_REPRESENTATIVE_ONLY":
        return True
    if classification == "REAL_SANITIZED_EVIDENCE":
        return True
    return False


def package_boundary_gates(
    package: Mapping[str, Any],
    scope: Mapping[str, Any],
) -> tuple[PreExecutionGateResult, ...]:
    source_summary = package.get("sourceSummary", {})
    tenant = package.get("tenantContext", {})
    site = package.get("siteContext", {})
    source_system = package.get("sourceSystemContext", {})
    device_count = int(source_summary.get("deviceCount", len(package.get("devices", ()))))
    point_count = len(package.get("standardFields", ()))
    return (
        _gate(
            "TENANT_SCOPE_MATCH_GATE",
            status="PASS" if tenant.get("tenantId") == scope.get("tenantScope") else "FAIL",
            observed=str(tenant.get("tenantId", "")),
            required=str(scope.get("tenantScope", "")),
        ),
        _gate(
            "SITE_SCOPE_MATCH_GATE",
            status="PASS" if site.get("siteId") == scope.get("siteScope") else "FAIL",
            observed=str(site.get("siteId", "")),
            required=str(scope.get("siteScope", "")),
        ),
        _gate(
            "SOURCE_SYSTEM_SCOPE_MATCH_GATE",
            status="PASS"
            if source_system.get("sourceSystemId") == scope.get("sourceSystemScope")
            else "FAIL",
            observed=str(source_system.get("sourceSystemId", "")),
            required=str(scope.get("sourceSystemScope", "")),
        ),
        _gate(
            "COUNT_BOUNDARY_GATE",
            status="PASS"
            if device_count <= int(scope.get("maximumDeviceCount", 0))
            and point_count <= int(scope.get("maximumPointCount", 0))
            else "FAIL",
            observed=f"devices={device_count}/{scope.get('maximumDeviceCount')};points={point_count}/{scope.get('maximumPointCount')}",
            required="counts within scope ceilings",
        ),
        _gate(
            "MAPPING_VERSION_PACKAGE_GATE",
            status="PASS" if package.get("mappingVersion") == scope.get("mappingVersion") else "FAIL",
            observed=str(package.get("mappingVersion", "")),
            required=str(scope.get("mappingVersion", "")),
        ),
    )
