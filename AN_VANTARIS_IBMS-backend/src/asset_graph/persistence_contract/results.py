"""Immutable persistence result models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Tuple

from ..reconciliation.models import sha256_digest
from .constants import CONTRACT_AUTHORITY, RESULT_NAME, RESULT_VERSION, WRITE_CUTOVER_STATUS


def _result_digest(payload: Mapping[str, Any]) -> str:
    material = {key: value for key, value in payload.items() if key != "resultDigest"}
    return sha256_digest(material)


@dataclass(frozen=True)
class PersistenceAuthorizationResult:
    decision: str
    blocking: bool
    conflict_code: Optional[str]
    safe_message: str
    write_cutover_status: str = WRITE_CUTOVER_STATUS

    def serialize(self) -> dict[str, Any]:
        payload = {
            "resultName": RESULT_NAME,
            "resultVersion": RESULT_VERSION,
            "authority": CONTRACT_AUTHORITY,
            "decision": self.decision,
            "blocking": self.blocking,
            "conflictCode": self.conflict_code,
            "safeMessage": self.safe_message,
            "writeCutoverStatus": self.write_cutover_status,
        }
        payload["resultDigest"] = _result_digest(payload)
        return payload


@dataclass(frozen=True)
class PersistenceCommandResult:
    command_id: str
    idempotency_key_digest: str
    object_type: str
    canonical_global_id_digest: str
    status: str
    conflict_code: Optional[str]
    previous_version: Optional[int]
    new_version: Optional[int]
    transaction_id: str
    audit_record_id: Optional[str]
    rollback_required: bool
    retryable: bool
    write_cutover_status: str = WRITE_CUTOVER_STATUS

    def serialize(self) -> dict[str, Any]:
        payload = {
            "resultName": RESULT_NAME,
            "resultVersion": RESULT_VERSION,
            "authority": CONTRACT_AUTHORITY,
            "commandId": self.command_id,
            "idempotencyKeyDigest": self.idempotency_key_digest,
            "objectType": self.object_type,
            "canonicalGlobalIdDigest": self.canonical_global_id_digest,
            "status": self.status,
            "conflictCode": self.conflict_code,
            "previousVersion": self.previous_version,
            "newVersion": self.new_version,
            "transactionId": self.transaction_id,
            "auditRecordId": self.audit_record_id,
            "rollbackRequired": self.rollback_required,
            "retryable": self.retryable,
            "writeCutoverStatus": self.write_cutover_status,
        }
        payload["resultDigest"] = _result_digest(payload)
        return payload


@dataclass(frozen=True)
class PersistenceBatchResult:
    transaction_id: str
    command_results: Tuple[PersistenceCommandResult, ...]
    status: str
    rollback_required: bool
    write_cutover_status: str = WRITE_CUTOVER_STATUS

    def serialize(self) -> dict[str, Any]:
        payload = {
            "resultName": RESULT_NAME,
            "resultVersion": RESULT_VERSION,
            "authority": CONTRACT_AUTHORITY,
            "transactionId": self.transaction_id,
            "status": self.status,
            "rollbackRequired": self.rollback_required,
            "writeCutoverStatus": self.write_cutover_status,
            "commandResults": [item.serialize() for item in self.command_results],
        }
        payload["resultDigest"] = _result_digest(payload)
        return payload


@dataclass(frozen=True)
class PersistenceTransactionResult:
    transaction_id: str
    status: str
    command_results: Tuple[PersistenceCommandResult, ...]
    rollback_reason: Optional[str]
    audit_record_ids: Tuple[str, ...]
    rollback_required: bool
    write_cutover_status: str = WRITE_CUTOVER_STATUS

    def serialize(self) -> dict[str, Any]:
        payload = {
            "resultName": RESULT_NAME,
            "resultVersion": RESULT_VERSION,
            "authority": CONTRACT_AUTHORITY,
            "transactionId": self.transaction_id,
            "status": self.status,
            "rollbackReason": self.rollback_reason,
            "auditRecordIds": list(self.audit_record_ids),
            "rollbackRequired": self.rollback_required,
            "writeCutoverStatus": self.write_cutover_status,
            "commandResults": [item.serialize() for item in self.command_results],
        }
        payload["resultDigest"] = _result_digest(payload)
        return payload
