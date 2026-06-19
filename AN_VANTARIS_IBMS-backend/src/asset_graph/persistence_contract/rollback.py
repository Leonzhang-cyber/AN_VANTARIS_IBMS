"""Rollback contract semantics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Tuple

from ..reconciliation.models import sha256_digest
from .constants import CONTRACT_AUTHORITY, WRITE_CUTOVER_STATUS


ROLLBACK_TRIGGERS = frozenset(
    {
        "validationFailure",
        "authorizationFailure",
        "providerFailure",
        "auditFailure",
        "dependencyFailure",
        "versionConflict",
        "partialStagingFailure",
    }
)


@dataclass(frozen=True)
class RollbackResult:
    transaction_id: str
    trigger: str
    status: str
    idempotency_reservations_released: int
    audit_required: bool
    guarantees: Tuple[str, ...]

    def serialize(self) -> Mapping[str, Any]:
        payload = {
            "authority": CONTRACT_AUTHORITY,
            "transactionId": self.transaction_id,
            "trigger": self.trigger,
            "status": self.status,
            "idempotencyReservationsReleased": self.idempotency_reservations_released,
            "auditRequired": self.audit_required,
            "guarantees": list(self.guarantees),
            "writeCutoverStatus": WRITE_CUTOVER_STATUS,
        }
        payload["resultDigest"] = sha256_digest(payload)
        return payload


ROLLBACK_GUARANTEES = (
    "noPartialCanonicalGraph",
    "sourceDataUnchanged",
    "legacyDataUnchanged",
    "failedCommandsNotMarkedSuccessful",
    "rollbackAuditRequired",
    "idempotencyReservationReleasedOrFailedDeterministically",
)


def build_rollback_result(
    *,
    transaction_id: str,
    trigger: str,
    idempotency_reservations_released: int,
) -> RollbackResult:
    if trigger not in ROLLBACK_TRIGGERS:
        raise ValueError(f"unknown rollback trigger: {trigger}")
    return RollbackResult(
        transaction_id=transaction_id,
        trigger=trigger,
        status="ROLLED_BACK",
        idempotency_reservations_released=idempotency_reservations_released,
        audit_required=True,
        guarantees=ROLLBACK_GUARANTEES,
    )
