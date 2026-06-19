"""Contract-only Unit of Work boundary."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence, Tuple

from ..reconciliation.models import sha256_digest
from .commands import (
    CreateCanonicalDevice,
    CreateCanonicalPoint,
    CreateCanonicalRelationship,
    CreateCanonicalTag,
    PersistenceCommand,
    UpdateCanonicalDevice,
    UpdateCanonicalPoint,
)
from .errors import PersistenceUnitOfWorkError
from .identity import CanonicalVersionMetadata, evaluate_update_version
from .providers import AssetGraphUnitOfWork, StagedWriteResult


@dataclass
class ContractUnitOfWork(AssetGraphUnitOfWork):
    """In-memory contract evaluator; does not persist canonical data."""

    transaction_id: str
    tenant_id: str
    site_id: str
    simulate_point_failure: bool = False
    _staged: list[PersistenceCommand] = field(default_factory=list)
    _device_staged: bool = False
    _versions: dict[str, CanonicalVersionMetadata] = field(default_factory=dict)
    _committed: bool = False
    _rolled_back: bool = False

    def stage(self, command: PersistenceCommand) -> StagedWriteResult:
        if self._committed or self._rolled_back:
            raise PersistenceUnitOfWorkError("unit of work is closed")
        if command.tenant_id != self.tenant_id or command.site_id != self.site_id:
            raise PersistenceUnitOfWorkError("command scope mismatch")
        self._validate_order(command)
        self._staged.append(command)
        if isinstance(command, (CreateCanonicalDevice, UpdateCanonicalDevice)):
            self._device_staged = True
        return StagedWriteResult(
            status="STAGED",
            object_type=command.object_type(),
            canonical_global_id_digest=command.canonical_global_id_digest(),
            previous_version=self._versions.get(command.canonical_global_id_digest(), CanonicalVersionMetadata(0, "", "")).version
            if command.canonical_global_id_digest() in self._versions
            else None,
            new_version=None,
        )

    def validate_staged(self) -> Tuple[str, ...]:
        errors: list[str] = []
        if any(isinstance(command, (CreateCanonicalPoint, CreateCanonicalRelationship)) for command in self._staged):
            if not self._device_staged:
                errors.append("device must be staged before dependent point or relationship commands")
        for command in self._staged:
            if isinstance(command, (UpdateCanonicalDevice, UpdateCanonicalPoint)):
                current = self._versions.get(command.canonical_global_id_digest())
                outcome = evaluate_update_version(
                    current=current,
                    expected_version=command.expected_version,
                )
                if outcome == "VERSION_CONFLICT":
                    errors.append(f"version conflict for command {command.command_id}")
                if outcome == "NOT_FOUND":
                    errors.append(f"not found for command {command.command_id}")
        return tuple(errors)

    def commit(self) -> Mapping[str, Any]:
        if self._committed or self._rolled_back:
            raise PersistenceUnitOfWorkError("unit of work is closed")
        errors = self.validate_staged()
        if errors:
            raise PersistenceUnitOfWorkError("; ".join(errors))
        if self.simulate_point_failure and any(isinstance(command, CreateCanonicalPoint) for command in self._staged):
            raise PersistenceUnitOfWorkError("dependent point write failure")
        results: list[dict[str, Any]] = []
        for command in self._staged:
            key = command.canonical_global_id_digest()
            current = self._versions.get(key)
            previous_version = current.version if current else 0
            new_version = previous_version + 1 if isinstance(command, (UpdateCanonicalDevice, UpdateCanonicalPoint)) else 1
            revision = sha256_digest({"transactionId": self.transaction_id, "commandId": command.command_id})
            self._versions[key] = CanonicalVersionMetadata(
                version=new_version,
                created_revision=current.created_revision if current else revision,
                updated_revision=revision,
            )
            results.append(
                {
                    "commandId": command.command_id,
                    "objectType": command.object_type(),
                    "status": "ACCEPTED",
                    "previousVersion": previous_version if previous_version else None,
                    "newVersion": new_version,
                }
            )
        self._committed = True
        return {
            "transactionId": self.transaction_id,
            "status": "COMMITTED",
            "commandResults": results,
        }

    def rollback(self, *, reason: str) -> Mapping[str, Any]:
        self._staged.clear()
        self._device_staged = False
        self._rolled_back = True
        return {
            "transactionId": self.transaction_id,
            "status": "ROLLED_BACK",
            "reason": reason,
        }

    def _validate_order(self, command: PersistenceCommand) -> None:
        if isinstance(command, (CreateCanonicalPoint, CreateCanonicalRelationship)) and not self._device_staged:
            device_create_pending = any(isinstance(item, CreateCanonicalDevice) for item in self._staged)
            if not device_create_pending:
                raise PersistenceUnitOfWorkError("device creation must precede dependent writes")


def build_transaction_id(material: Mapping[str, Any]) -> str:
    return sha256_digest(material)[:32]
