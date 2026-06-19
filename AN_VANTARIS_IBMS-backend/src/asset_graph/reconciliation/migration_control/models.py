"""Immutable migration control contract objects."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Tuple

from ..models import sha256_digest


@dataclass(frozen=True)
class ApprovalRecord:
    approval_id: str
    approval_type: str
    approved_by_role: str
    scope_digest: str
    evidence_digest: str
    readiness_result_digest: str
    issued_at_policy: str
    expires_at: str
    status: str
    constraints: Tuple[str, ...]
    revocation_reason: str = ""

    def serialize(self) -> dict[str, Any]:
        return {
            "approvalId": self.approval_id,
            "approvalType": self.approval_type,
            "approvedByRole": self.approved_by_role,
            "scopeDigest": self.scope_digest,
            "evidenceDigest": self.evidence_digest,
            "readinessResultDigest": self.readiness_result_digest,
            "issuedAtPolicy": self.issued_at_policy,
            "expiresAt": self.expires_at,
            "status": self.status,
            "constraints": list(self.constraints),
            "revocationReason": self.revocation_reason,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ApprovalRecord":
        return cls(
            approval_id=str(value["approvalId"]),
            approval_type=str(value["approvalType"]),
            approved_by_role=str(value["approvedByRole"]),
            scope_digest=str(value["scopeDigest"]),
            evidence_digest=str(value["evidenceDigest"]),
            readiness_result_digest=str(value["readinessResultDigest"]),
            issued_at_policy=str(value["issuedAtPolicy"]),
            expires_at=str(value["expiresAt"]),
            status=str(value["status"]),
            constraints=tuple(str(item) for item in value.get("constraints", ())),
            revocation_reason=str(value.get("revocationReason", "")),
        )


@dataclass(frozen=True)
class ExecutionScope:
    tenant_scope: str
    site_scope: str
    source_system_scope: str
    mapping_version: str
    maximum_device_count: int
    maximum_point_count: int
    allowed_operations: Tuple[str, ...]
    forbidden_operations: Tuple[str, ...]
    output_location_policy: str
    retention_policy: str
    rollback_policy: str
    approval_expiry: str

    def digest_material(self) -> dict[str, Any]:
        return {
            "tenantScope": self.tenant_scope,
            "siteScope": self.site_scope,
            "sourceSystemScope": self.source_system_scope,
            "mappingVersion": self.mapping_version,
            "maximumDeviceCount": self.maximum_device_count,
            "maximumPointCount": self.maximum_point_count,
            "allowedOperations": list(self.allowed_operations),
            "forbiddenOperations": list(self.forbidden_operations),
            "outputLocationPolicy": self.output_location_policy,
            "retentionPolicy": self.retention_policy,
            "rollbackPolicy": self.rollback_policy,
            "approvalExpiry": self.approval_expiry,
        }

    def scope_digest(self) -> str:
        return sha256_digest(self.digest_material())

    def serialize(self) -> dict[str, Any]:
        payload = self.digest_material()
        payload["scopeDigest"] = self.scope_digest()
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ExecutionScope":
        return cls(
            tenant_scope=str(value["tenantScope"]),
            site_scope=str(value["siteScope"]),
            source_system_scope=str(value["sourceSystemScope"]),
            mapping_version=str(value["mappingVersion"]),
            maximum_device_count=int(value["maximumDeviceCount"]),
            maximum_point_count=int(value["maximumPointCount"]),
            allowed_operations=tuple(str(item) for item in value.get("allowedOperations", ())),
            forbidden_operations=tuple(str(item) for item in value.get("forbiddenOperations", ())),
            output_location_policy=str(value["outputLocationPolicy"]),
            retention_policy=str(value["retentionPolicy"]),
            rollback_policy=str(value["rollbackPolicy"]),
            approval_expiry=str(value["approvalExpiry"]),
        )


@dataclass(frozen=True)
class ControlInput:
    readiness_result_digest: str
    readiness_policy_version: str
    readiness_decision: str
    evidence_classification: str
    evidence_digest: str
    mapping_version: str
    source_count_summary: Mapping[str, Any]
    projected_count_summary: Mapping[str, Any]
    blocker_count: int
    review_count: int
    warning_count: int
    hard_blocker_count: int
    relationship_invariant_summary: Mapping[str, Any]
    deterministic_verification_confirmed: bool
    write_cutover_status: str
    requested_operations: Tuple[str, ...]
    migration_intent: str
    execution_scope: ExecutionScope
    approvals: Tuple[ApprovalRecord, ...]
    evaluation_instant: str

    def serialize(self) -> dict[str, Any]:
        return {
            "readinessResultDigest": self.readiness_result_digest,
            "readinessPolicyVersion": self.readiness_policy_version,
            "readinessDecision": self.readiness_decision,
            "evidenceClassification": self.evidence_classification,
            "evidenceDigest": self.evidence_digest,
            "mappingVersion": self.mapping_version,
            "sourceCountSummary": dict(self.source_count_summary),
            "projectedCountSummary": dict(self.projected_count_summary),
            "blockerCount": self.blocker_count,
            "reviewCount": self.review_count,
            "warningCount": self.warning_count,
            "hardBlockerCount": self.hard_blocker_count,
            "relationshipInvariantSummary": dict(self.relationship_invariant_summary),
            "deterministicVerificationConfirmed": self.deterministic_verification_confirmed,
            "writeCutoverStatus": self.write_cutover_status,
            "requestedOperations": list(self.requested_operations),
            "migrationIntent": self.migration_intent,
            "executionScope": self.execution_scope.serialize(),
            "approvals": [item.serialize() for item in self.approvals],
            "evaluationInstant": self.evaluation_instant,
        }


@dataclass(frozen=True)
class PreconditionResult:
    gate_code: str
    status: str
    blocking: bool
    observed_value: str
    required_value: str
    remediation_category: str

    def serialize(self) -> dict[str, Any]:
        return {
            "gateCode": self.gate_code,
            "status": self.status,
            "blocking": self.blocking,
            "observedValue": self.observed_value,
            "requiredValue": self.required_value,
            "remediationCategory": self.remediation_category,
        }


@dataclass(frozen=True)
class ExecutionPlanResult:
    plan_name: str
    plan_version: str
    authority: str
    contract_version: str
    readiness_decision: str
    evidence_classification: str
    execution_state: str
    approval_status: str
    scope_summary: Mapping[str, Any]
    allowed_operations: Tuple[str, ...]
    forbidden_operations: Tuple[str, ...]
    preconditions: Tuple[PreconditionResult, ...]
    failed_preconditions: Tuple[str, ...]
    rollback_requirements: Tuple[str, ...]
    retention_requirements: Tuple[str, ...]
    write_cutover_status: str
    result_digest: str = ""

    def serialize(self) -> dict[str, Any]:
        payload = {
            "planName": self.plan_name,
            "planVersion": self.plan_version,
            "authority": self.authority,
            "contractVersion": self.contract_version,
            "readinessDecision": self.readiness_decision,
            "evidenceClassification": self.evidence_classification,
            "executionState": self.execution_state,
            "approvalStatus": self.approval_status,
            "scopeSummary": dict(self.scope_summary),
            "allowedOperations": list(self.allowed_operations),
            "forbiddenOperations": list(self.forbidden_operations),
            "preconditions": [item.serialize() for item in self.preconditions],
            "failedPreconditions": list(self.failed_preconditions),
            "rollbackRequirements": list(self.rollback_requirements),
            "retentionRequirements": list(self.retention_requirements),
            "writeCutoverStatus": self.write_cutover_status,
        }
        payload["resultDigest"] = self.result_digest or sha256_digest(payload)
        return payload
