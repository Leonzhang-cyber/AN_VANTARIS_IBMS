"""Deterministic idempotency semantics for persistence commands."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional, Tuple

from ..reconciliation.models import sha256_digest
from .commands import PersistenceCommand
from .conflicts import CONFLICT_MESSAGES
from .results import PersistenceCommandResult


@dataclass(frozen=True)
class IdempotencyEvaluation:
    status: str
    conflict_code: Optional[str]
    previous_result_digest: Optional[str]


@dataclass
class IdempotencyLedger:
    """In-memory contract ledger; not a persistence store."""

    _entries: dict[str, tuple[str, str]]

    def __init__(self) -> None:
        self._entries = {}

    def evaluate(self, command: PersistenceCommand, *, canonical_content_digest: Optional[str] = None) -> IdempotencyEvaluation:
        key_digest = command.idempotency_key_digest()
        command_digest = command.command_digest()
        existing = self._entries.get(key_digest)
        if existing is None:
            return IdempotencyEvaluation(status="NEW", conflict_code=None, previous_result_digest=None)
        previous_command_digest, previous_result_digest = existing
        if previous_command_digest != command_digest:
            return IdempotencyEvaluation(
                status="IDEMPOTENCY_CONFLICT",
                conflict_code="IDEMPOTENCY_CONFLICT",
                previous_result_digest=previous_result_digest,
            )
        return IdempotencyEvaluation(
            status="IDEMPOTENT_REPLAY",
            conflict_code=None,
            previous_result_digest=previous_result_digest,
        )

    def record(self, command: PersistenceCommand, result: PersistenceCommandResult) -> None:
        self._entries[command.idempotency_key_digest()] = (
            command.command_digest(),
            result.serialize()["resultDigest"],
        )

    def release(self, command: PersistenceCommand) -> None:
        self._entries.pop(command.idempotency_key_digest(), None)

    def mark_failed(self, command: PersistenceCommand) -> None:
        key_digest = command.idempotency_key_digest()
        if key_digest in self._entries:
            command_digest, _ = self._entries[key_digest]
            self._entries[key_digest] = (command_digest, sha256_digest({"status": "FAILED"}))


def evaluate_canonical_identity(
    *,
    canonical_global_id_digest: str,
    existing_content_digest: Optional[str],
    incoming_content_digest: str,
) -> IdempotencyEvaluation:
    if existing_content_digest is None:
        return IdempotencyEvaluation(status="NEW", conflict_code=None, previous_result_digest=None)
    if existing_content_digest == incoming_content_digest:
        return IdempotencyEvaluation(status="ALREADY_APPLIED", conflict_code=None, previous_result_digest=None)
    return IdempotencyEvaluation(
        status="CANONICAL_IDENTITY_CONFLICT",
        conflict_code="CANONICAL_IDENTITY_CONFLICT",
        previous_result_digest=None,
    )


def evaluate_relationship_pair(
    *,
    pair_digest: str,
    existing_pair_digest: Optional[str],
    incoming_pair_digest: str,
) -> IdempotencyEvaluation:
    if existing_pair_digest is None:
        return IdempotencyEvaluation(status="NEW", conflict_code=None, previous_result_digest=None)
    if existing_pair_digest == incoming_pair_digest:
        return IdempotencyEvaluation(status="ALREADY_APPLIED", conflict_code=None, previous_result_digest=None)
    return IdempotencyEvaluation(
        status="RELATIONSHIP_DUPLICATE_CONFLICT",
        conflict_code="RELATIONSHIP_DUPLICATE_CONFLICT",
        previous_result_digest=None,
    )


def safe_idempotency_message(status: str) -> str:
    if status == "IDEMPOTENCY_CONFLICT":
        return CONFLICT_MESSAGES["IDEMPOTENCY_CONFLICT"]
    if status == "CANONICAL_IDENTITY_CONFLICT":
        return CONFLICT_MESSAGES["CANONICAL_IDENTITY_CONFLICT"]
    if status == "RELATIONSHIP_DUPLICATE_CONFLICT":
        return CONFLICT_MESSAGES["RELATIONSHIP_DUPLICATE_CONFLICT"]
    return status
