"""Write authorization gate for canonical persistence."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

from .conflicts import CONFLICT_MESSAGES, conflict_result
from .constants import (
    AUTHORIZATION_APPROVED_VALIDATION,
    AUTHORIZATION_DENIED,
    AUTHORIZATION_WAITING_PERSISTENCE_APPROVAL,
    AUTHORIZATION_WAITING_READINESS,
    AUTHORIZATION_WAITING_REAL_EVIDENCE,
    REAL_EVIDENCE_CLASSIFICATION,
    READY_FOR_READ_MIGRATION,
    WRITE_CUTOVER_STATUS,
)
from .providers import ProviderCapabilityDeclaration
from .results import PersistenceAuthorizationResult


@dataclass(frozen=True)
class PersistenceAuthorizationInput:
    evidence_classification: str
    readiness_decision: str
    hard_blocker_count: int
    evidence_digest: str
    readiness_result_digest: str
    execution_result_digest: str
    tenant_scope: str
    site_scope: str
    source_system_scope: str
    mapping_version: str
    requested_evidence_digest: str
    requested_readiness_result_digest: str
    requested_execution_result_digest: str
    requested_tenant_id: str
    requested_site_id: str
    requested_source_system_id: str
    requested_mapping_version: str
    persistence_approval_granted: bool
    approved_execution_contract_present: bool
    provider_capabilities: ProviderCapabilityDeclaration

    @classmethod
    def from_mapping(cls, value: Mapping[str, object], *, provider_capabilities: ProviderCapabilityDeclaration) -> "PersistenceAuthorizationInput":
        return cls(
            evidence_classification=str(value["evidenceClassification"]),
            readiness_decision=str(value["readinessDecision"]),
            hard_blocker_count=int(value.get("hardBlockerCount", 0)),
            evidence_digest=str(value["evidenceDigest"]),
            readiness_result_digest=str(value["readinessResultDigest"]),
            execution_result_digest=str(value["executionResultDigest"]),
            tenant_scope=str(value["tenantScope"]),
            site_scope=str(value["siteScope"]),
            source_system_scope=str(value["sourceSystemScope"]),
            mapping_version=str(value["mappingVersion"]),
            requested_evidence_digest=str(value["requestedEvidenceDigest"]),
            requested_readiness_result_digest=str(value["requestedReadinessResultDigest"]),
            requested_execution_result_digest=str(value["requestedExecutionResultDigest"]),
            requested_tenant_id=str(value["requestedTenantId"]),
            requested_site_id=str(value["requestedSiteId"]),
            requested_source_system_id=str(value["requestedSourceSystemId"]),
            requested_mapping_version=str(value["requestedMappingVersion"]),
            persistence_approval_granted=bool(value.get("persistenceApprovalGranted", False)),
            approved_execution_contract_present=bool(value.get("approvedExecutionContractPresent", False)),
            provider_capabilities=provider_capabilities,
        )


def evaluate_persistence_authorization(
    authorization_input: PersistenceAuthorizationInput,
) -> PersistenceAuthorizationResult:
    if authorization_input.evidence_classification != REAL_EVIDENCE_CLASSIFICATION:
        if authorization_input.evidence_classification == "SYNTHETIC_REPRESENTATIVE_ONLY":
            return _auth(
                AUTHORIZATION_DENIED,
                blocking=True,
                conflict_code=None,
                safe_message="Synthetic evidence cannot authorize canonical persistence.",
            )
        return _auth(
            AUTHORIZATION_WAITING_REAL_EVIDENCE,
            blocking=True,
            conflict_code=None,
            safe_message="Real sanitized evidence is required before canonical persistence.",
        )

    if authorization_input.readiness_decision != READY_FOR_READ_MIGRATION:
        return _auth(
            AUTHORIZATION_WAITING_READINESS,
            blocking=True,
            conflict_code=None,
            safe_message="Readiness decision must be READY_FOR_READ_MIGRATION_CANDIDATE.",
        )

    if authorization_input.hard_blocker_count > 0:
        return _auth(
            AUTHORIZATION_DENIED,
            blocking=True,
            conflict_code="VALIDATION_FAILED",
            safe_message="Hard blockers prevent canonical persistence.",
        )

    if not authorization_input.approved_execution_contract_present:
        return _auth(
            AUTHORIZATION_DENIED,
            blocking=True,
            conflict_code=None,
            safe_message="Approved read migration execution contract is required.",
        )

    if not authorization_input.persistence_approval_granted:
        return _auth(
            AUTHORIZATION_WAITING_PERSISTENCE_APPROVAL,
            blocking=True,
            conflict_code=None,
            safe_message="Explicit persistence authorization is required.",
        )

    if not authorization_input.provider_capabilities.enabled_for_canonical_writes:
        return _auth(
            AUTHORIZATION_DENIED,
            blocking=True,
            conflict_code="PROVIDER_UNAVAILABLE",
            safe_message="Canonical write provider is not enabled.",
        )

    digest_conflict = _digest_scope_conflict(authorization_input)
    if digest_conflict is not None:
        return digest_conflict

    return _auth(
        AUTHORIZATION_APPROVED_VALIDATION,
        blocking=False,
        conflict_code=None,
        safe_message="Persistence authorization approved for canonical write validation.",
    )


def _digest_scope_conflict(authorization_input: PersistenceAuthorizationInput) -> Optional[PersistenceAuthorizationResult]:
    if authorization_input.requested_evidence_digest != authorization_input.evidence_digest:
        return _auth(
            AUTHORIZATION_DENIED,
            blocking=True,
            conflict_code="EVIDENCE_DIGEST_CONFLICT",
            safe_message=CONFLICT_MESSAGES["EVIDENCE_DIGEST_CONFLICT"],
        )
    if authorization_input.requested_readiness_result_digest != authorization_input.readiness_result_digest:
        return _auth(
            AUTHORIZATION_DENIED,
            blocking=True,
            conflict_code="READINESS_DIGEST_CONFLICT",
            safe_message=CONFLICT_MESSAGES["READINESS_DIGEST_CONFLICT"],
        )
    if authorization_input.requested_execution_result_digest != authorization_input.execution_result_digest:
        return _auth(
            AUTHORIZATION_DENIED,
            blocking=True,
            conflict_code="EXECUTION_DIGEST_CONFLICT",
            safe_message=CONFLICT_MESSAGES["EXECUTION_DIGEST_CONFLICT"],
        )
    if authorization_input.requested_mapping_version != authorization_input.mapping_version:
        return _auth(
            AUTHORIZATION_DENIED,
            blocking=True,
            conflict_code="MAPPING_VERSION_CONFLICT",
            safe_message=CONFLICT_MESSAGES["MAPPING_VERSION_CONFLICT"],
        )
    if authorization_input.requested_tenant_id != authorization_input.tenant_scope:
        return _auth(
            AUTHORIZATION_DENIED,
            blocking=True,
            conflict_code="TENANT_SCOPE_CONFLICT",
            safe_message=CONFLICT_MESSAGES["TENANT_SCOPE_CONFLICT"],
        )
    if authorization_input.requested_site_id != authorization_input.site_scope:
        return _auth(
            AUTHORIZATION_DENIED,
            blocking=True,
            conflict_code="SITE_SCOPE_CONFLICT",
            safe_message=CONFLICT_MESSAGES["SITE_SCOPE_CONFLICT"],
        )
    if authorization_input.requested_source_system_id != authorization_input.source_system_scope:
        return _auth(
            AUTHORIZATION_DENIED,
            blocking=True,
            conflict_code="TENANT_SCOPE_CONFLICT",
            safe_message=CONFLICT_MESSAGES["TENANT_SCOPE_CONFLICT"],
        )
    return None


def _auth(
    decision: str,
    *,
    blocking: bool,
    conflict_code: Optional[str],
    safe_message: str,
) -> PersistenceAuthorizationResult:
    return PersistenceAuthorizationResult(
        decision=decision,
        blocking=blocking,
        conflict_code=conflict_code,
        safe_message=safe_message,
        write_cutover_status=WRITE_CUTOVER_STATUS,
    )
