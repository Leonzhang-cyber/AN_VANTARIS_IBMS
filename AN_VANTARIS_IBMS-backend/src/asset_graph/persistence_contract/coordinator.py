"""Persistence coordinator contract evaluation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional, Sequence, Tuple

from src.governance.audit.models import AuditEmissionResult

from .audit import (
    AuditObligationContext,
    GovernanceAuditPort,
    fulfill_audit_obligations,
    required_commit_obligations,
    rollback_obligations,
)
from .authorization import PersistenceAuthorizationInput, evaluate_persistence_authorization
from .batch import validate_batch_limits
from .commands import (
    CreateCanonicalDevice,
    CreateCanonicalPoint,
    CreateCanonicalRelationship,
    CreateCanonicalTag,
    PersistenceCommand,
    UpdateCanonicalDevice,
    UpdateCanonicalPoint,
)
from .contract import batch_limits
from .errors import PersistenceAuditError, PersistenceUnitOfWorkError
from .idempotency import IdempotencyLedger
from .providers import ProviderCapabilityDeclaration, default_provider_capabilities
from .results import (
    PersistenceAuthorizationResult,
    PersistenceBatchResult,
    PersistenceCommandResult,
    PersistenceTransactionResult,
)
from .rollback import build_rollback_result
from .unit_of_work import ContractUnitOfWork, build_transaction_id


@dataclass(frozen=True)
class PersistenceCoordinatorInput:
    authorization: PersistenceAuthorizationInput
    commands: Tuple[PersistenceCommand, ...]
    contract: Mapping[str, object]
    simulate_point_failure: bool = False
    audit_should_fail: bool = False


class AssetGraphPersistenceCoordinator:
    """Coordinates authorization, batching, idempotency, UoW and audit obligations."""

    def __init__(
        self,
        *,
        audit_port: GovernanceAuditPort,
        idempotency_ledger: Optional[IdempotencyLedger] = None,
    ) -> None:
        self._audit_port = audit_port
        self._ledger = idempotency_ledger or IdempotencyLedger()

    @property
    def idempotency_ledger(self) -> IdempotencyLedger:
        return self._ledger

    def evaluate_authorization(
        self,
        authorization_input: PersistenceAuthorizationInput,
    ) -> PersistenceAuthorizationResult:
        return evaluate_persistence_authorization(authorization_input)

    def execute_batch(
        self,
        coordinator_input: PersistenceCoordinatorInput,
    ) -> PersistenceBatchResult | PersistenceTransactionResult:
        auth = evaluate_persistence_authorization(coordinator_input.authorization)
        transaction_id = build_transaction_id(
            {
                "commandIds": [command.command_id for command in coordinator_input.commands],
                "tenantId": coordinator_input.commands[0].tenant_id if coordinator_input.commands else "",
            }
        )
        if auth.blocking:
            self._emit_single_audit(
                obligation="commandRejected",
                transaction_id=transaction_id,
                tenant_id=coordinator_input.commands[0].tenant_id if coordinator_input.commands else None,
                site_id=coordinator_input.commands[0].site_id if coordinator_input.commands else None,
                outcome="DENY",
                reason_code=auth.decision,
            )
            return PersistenceBatchResult(
                transaction_id=transaction_id,
                command_results=(),
                status="REJECTED",
                rollback_required=False,
            )

        limits = batch_limits(coordinator_input.contract)
        validate_batch_limits(coordinator_input.commands, limits)

        replay_results: list[PersistenceCommandResult] = []
        staged_commands: list[PersistenceCommand] = []
        for command in coordinator_input.commands:
            idem = self._ledger.evaluate(command)
            if idem.status == "IDEMPOTENCY_CONFLICT":
                replay_results.append(
                    self._command_result(
                        command,
                        transaction_id=transaction_id,
                        status="REJECTED",
                        conflict_code="IDEMPOTENCY_CONFLICT",
                        rollback_required=False,
                    )
                )
                return PersistenceBatchResult(
                    transaction_id=transaction_id,
                    command_results=tuple(replay_results),
                    status="REJECTED",
                    rollback_required=False,
                )
            if idem.status == "IDEMPOTENT_REPLAY":
                replay_results.append(
                    self._command_result(
                        command,
                        transaction_id=transaction_id,
                        status="IDEMPOTENT_REPLAY",
                        conflict_code=None,
                        rollback_required=False,
                        audit_record_id=(idem.previous_result_digest or "")[:32] or None,
                    )
                )
                continue
            staged_commands.append(command)

        if not staged_commands:
            return PersistenceTransactionResult(
                transaction_id=transaction_id,
                status="COMMITTED",
                command_results=tuple(replay_results),
                rollback_reason=None,
                audit_record_ids=(),
                rollback_required=False,
            )

        uow = ContractUnitOfWork(
            transaction_id=transaction_id,
            tenant_id=staged_commands[0].tenant_id,
            site_id=staged_commands[0].site_id,
            simulate_point_failure=coordinator_input.simulate_point_failure,
        )
        try:
            for command in staged_commands:
                uow.stage(command)
            commit_payload = uow.commit()
        except PersistenceUnitOfWorkError:
            uow.rollback(reason="dependencyFailure")
            released = self._release_idempotency(staged_commands)
            build_rollback_result(
                transaction_id=transaction_id,
                trigger="dependencyFailure",
                idempotency_reservations_released=released,
            )
            if not coordinator_input.audit_should_fail:
                self._emit_rollback_audit(
                    transaction_id=transaction_id,
                    tenant_id=staged_commands[0].tenant_id,
                    site_id=staged_commands[0].site_id,
                    reason_code="dependencyFailure",
                )
            rolled_back = replay_results + [
                self._command_result(
                    command,
                    transaction_id=transaction_id,
                    status="ROLLED_BACK",
                    conflict_code="POINT_PARENT_CONFLICT" if coordinator_input.simulate_point_failure else None,
                    rollback_required=True,
                )
                for command in staged_commands
            ]
            return PersistenceTransactionResult(
                transaction_id=transaction_id,
                status="ROLLED_BACK",
                command_results=tuple(rolled_back),
                rollback_reason="dependencyFailure",
                audit_record_ids=(),
                rollback_required=True,
            )

        try:
            audit_ids = fulfill_audit_obligations(
                audit_port=self._audit_port if not coordinator_input.audit_should_fail else _FailingAuditPort(),
                obligations=required_commit_obligations(
                    transaction_id=transaction_id,
                    tenant_id=staged_commands[0].tenant_id,
                    site_id=staged_commands[0].site_id,
                ),
            )
        except PersistenceAuditError:
            uow.rollback(reason="auditFailure")
            released = self._release_idempotency(staged_commands)
            build_rollback_result(
                transaction_id=transaction_id,
                trigger="auditFailure",
                idempotency_reservations_released=released,
            )
            return PersistenceTransactionResult(
                transaction_id=transaction_id,
                status="FAILED",
                command_results=tuple(
                    replay_results
                    + [
                        self._command_result(
                            command,
                            transaction_id=transaction_id,
                            status="REJECTED",
                            conflict_code=None,
                            rollback_required=True,
                        )
                        for command in staged_commands
                    ]
                ),
                rollback_reason="auditFailure",
                audit_record_ids=(),
                rollback_required=True,
            )

        staged_results: list[PersistenceCommandResult] = []
        for index, command in enumerate(staged_commands):
            commit_row = commit_payload["commandResults"][index]
            result = self._command_result(
                command,
                transaction_id=transaction_id,
                status="ACCEPTED",
                conflict_code=None,
                rollback_required=False,
                audit_record_id=audit_ids[-1] if audit_ids else None,
                previous_version=commit_row["previousVersion"],
                new_version=commit_row["newVersion"],
            )
            self._ledger.record(command, result)
            staged_results.append(result)

        return PersistenceTransactionResult(
            transaction_id=transaction_id,
            status="COMMITTED",
            command_results=tuple(replay_results + staged_results),
            rollback_reason=None,
            audit_record_ids=audit_ids,
            rollback_required=False,
        )

    def _command_result(
        self,
        command: PersistenceCommand,
        *,
        transaction_id: str,
        status: str,
        conflict_code: Optional[str],
        rollback_required: bool,
        audit_record_id: Optional[str] = None,
        previous_version: Optional[int] = None,
        new_version: Optional[int] = None,
    ) -> PersistenceCommandResult:
        return PersistenceCommandResult(
            command_id=command.command_id,
            idempotency_key_digest=command.idempotency_key_digest(),
            object_type=command.object_type(),
            canonical_global_id_digest=command.canonical_global_id_digest(),
            status=status,
            conflict_code=conflict_code,
            previous_version=previous_version,
            new_version=new_version,
            transaction_id=transaction_id,
            audit_record_id=audit_record_id,
            rollback_required=rollback_required,
            retryable=conflict_code in {"VERSION_CONFLICT", "IDEMPOTENCY_CONFLICT"},
        )

    def _release_idempotency(self, commands: Sequence[PersistenceCommand]) -> int:
        released = 0
        for command in commands:
            if command.idempotency_key_digest() in self._ledger._entries:
                self._ledger.release(command)
                released += 1
        return released

    def _emit_single_audit(
        self,
        *,
        obligation: str,
        transaction_id: str,
        tenant_id: Optional[str],
        site_id: Optional[str],
        outcome: str,
        reason_code: Optional[str],
    ) -> None:
        fulfill_audit_obligations(
            audit_port=self._audit_port,
            obligations=(
                AuditObligationContext(
                    obligation=obligation,
                    transaction_id=transaction_id,
                    command_id=None,
                    tenant_id=tenant_id,
                    site_id=site_id,
                    outcome=outcome,
                    reason_code=reason_code,
                ),
            ),
        )

    def _emit_rollback_audit(
        self,
        *,
        transaction_id: str,
        tenant_id: str,
        site_id: str,
        reason_code: str,
    ) -> None:
        fulfill_audit_obligations(
            audit_port=self._audit_port,
            obligations=rollback_obligations(
                transaction_id=transaction_id,
                tenant_id=tenant_id,
                site_id=site_id,
                reason_code=reason_code,
            ),
        )


class _FailingAuditPort:
    def emit(self, record, failure_policy: str) -> AuditEmissionResult:
        return AuditEmissionResult(
            audit_id=record.audit_id,
            accepted=False,
            duplicate=False,
            provider_status="FAILED",
            failure_policy=failure_policy,
            error_code="AUDIT_UNAVAILABLE",
        )


def enabled_validation_provider_capabilities() -> ProviderCapabilityDeclaration:
    """Test-only capability profile for abstract canonical write validation approval."""
    base = default_provider_capabilities()
    return ProviderCapabilityDeclaration(
        provider_name="ABSTRACT_VALIDATION_PROVIDER",
        provider_version="0.0.0",
        storage_type="NONE",
        supports_transactions=True,
        supports_optimistic_concurrency=True,
        supports_idempotency=True,
        supports_tenant_isolation=True,
        supports_site_isolation=True,
        supports_relationship_integrity=True,
        supports_audit_binding=True,
        maximum_batch_size=20000,
        health_status="VALIDATION_ONLY",
        enabled_for_canonical_writes=True,
    )
