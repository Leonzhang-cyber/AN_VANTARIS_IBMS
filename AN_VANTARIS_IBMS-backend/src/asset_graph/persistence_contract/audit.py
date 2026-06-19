"""Audit obligations for canonical persistence attempts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional, Protocol, Tuple

from src.governance.audit.models import AuditEmissionResult, AuditRecord

from ..reconciliation.models import sha256_digest
from .constants import AUDIT_OBLIGATIONS, CONTRACT_AUTHORITY
from .errors import PersistenceAuditError


def _audit_outcome(value: str) -> str:
    if value == "PASS":
        return "SUCCESS"
    if value == "DENY":
        return "DENIED"
    return "FAILURE"


FIXED_AUDIT_INSTANT = datetime(2026, 1, 1, tzinfo=timezone.utc)


class GovernanceAuditPort(Protocol):
    def emit(self, record: AuditRecord, failure_policy: str) -> AuditEmissionResult: ...


@dataclass(frozen=True)
class AuditObligationContext:
    obligation: str
    transaction_id: str
    command_id: Optional[str]
    tenant_id: Optional[str]
    site_id: Optional[str]
    outcome: str
    reason_code: Optional[str] = None

    def __post_init__(self) -> None:
        if self.obligation not in AUDIT_OBLIGATIONS:
            raise ValueError(f"unknown audit obligation: {self.obligation}")


AUDIT_ACTIONS = {
    "authorizationEvaluated": "ASSET_GRAPH_PERSISTENCE_AUTHZ_EVALUATED",
    "commandAccepted": "ASSET_GRAPH_PERSISTENCE_COMMAND_ACCEPTED",
    "commandRejected": "ASSET_GRAPH_PERSISTENCE_COMMAND_REJECTED",
    "transactionStarted": "ASSET_GRAPH_PERSISTENCE_TX_STARTED",
    "transactionCommitted": "ASSET_GRAPH_PERSISTENCE_TX_COMMITTED",
    "transactionRolledBack": "ASSET_GRAPH_PERSISTENCE_TX_ROLLED_BACK",
    "idempotentReplay": "ASSET_GRAPH_PERSISTENCE_IDEMPOTENT_REPLAY",
    "versionConflict": "ASSET_GRAPH_PERSISTENCE_VERSION_CONFLICT",
    "scopeConflict": "ASSET_GRAPH_PERSISTENCE_SCOPE_CONFLICT",
    "providerUnavailable": "ASSET_GRAPH_PERSISTENCE_PROVIDER_UNAVAILABLE",
}


def build_audit_record(context: AuditObligationContext) -> AuditRecord:
    audit_id = sha256_digest(
        {
            "authority": CONTRACT_AUTHORITY,
            "obligation": context.obligation,
            "transactionId": context.transaction_id,
            "commandId": context.command_id,
            "outcome": context.outcome,
        }
    )[:32]
    return AuditRecord(
        audit_id=audit_id,
        event_class="CONTROL_OPERATION",
        action=AUDIT_ACTIONS[context.obligation],
        occurred_at=FIXED_AUDIT_INSTANT,
        actor_type="SERVICE_IDENTITY",
        actor_id=None,
        service_identity_id=CONTRACT_AUTHORITY,
        tenant_id=context.tenant_id,
        site_id=context.site_id,
        subject_type="PERSISTENCE_TRANSACTION",
        subject_id=context.transaction_id,
        target_type="PERSISTENCE_COMMAND" if context.command_id else None,
        target_id=context.command_id,
        route_id=None,
        request_id=context.transaction_id,
        trace_id=context.transaction_id,
        correlation_id=context.transaction_id,
        permission="CANONICAL_PERSISTENCE_VALIDATION",
        package_id=None,
        outcome=_audit_outcome(context.outcome),
        denial_code=context.reason_code,
        reason_code=context.reason_code,
        previous_state_digest=None,
        resulting_state_digest=None,
        source_ip_class="INTERNAL",
        user_agent_class="SERVICE",
        contract_version="1.0.0",
        metadata_classification="INTERNAL",
        evidence_reference_ids=(),
    )


def fulfill_audit_obligations(
    *,
    audit_port: GovernanceAuditPort,
    obligations: Tuple[AuditObligationContext, ...],
    failure_policy: str = "FAIL_CLOSED",
) -> Tuple[str, ...]:
    record_ids: list[str] = []
    for context in obligations:
        record = build_audit_record(context)
        result = audit_port.emit(record, failure_policy)
        if not result.accepted:
            raise PersistenceAuditError(f"audit obligation failed: {context.obligation}")
        record_ids.append(record.audit_id)
    return tuple(record_ids)


def required_commit_obligations(
    *,
    transaction_id: str,
    tenant_id: str,
    site_id: str,
) -> Tuple[AuditObligationContext, ...]:
    return (
        AuditObligationContext(
            obligation="authorizationEvaluated",
            transaction_id=transaction_id,
            command_id=None,
            tenant_id=tenant_id,
            site_id=site_id,
            outcome="PASS",
        ),
        AuditObligationContext(
            obligation="transactionStarted",
            transaction_id=transaction_id,
            command_id=None,
            tenant_id=tenant_id,
            site_id=site_id,
            outcome="PASS",
        ),
        AuditObligationContext(
            obligation="transactionCommitted",
            transaction_id=transaction_id,
            command_id=None,
            tenant_id=tenant_id,
            site_id=site_id,
            outcome="PASS",
        ),
    )


def rollback_obligations(
    *,
    transaction_id: str,
    tenant_id: str,
    site_id: str,
    reason_code: str,
) -> Tuple[AuditObligationContext, ...]:
    return (
        AuditObligationContext(
            obligation="transactionRolledBack",
            transaction_id=transaction_id,
            command_id=None,
            tenant_id=tenant_id,
            site_id=site_id,
            outcome="FAIL",
            reason_code=reason_code,
        ),
    )
