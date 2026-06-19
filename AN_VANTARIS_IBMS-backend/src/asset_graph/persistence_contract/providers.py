"""Storage-neutral canonical persistence provider ports."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Mapping, Optional, Tuple, TypeVar

from ..models import AssetRelationship, Device, GlobalId, Point, SourceIdentity, Tag
from .commands import PersistenceCommand

T = TypeVar("T")


@dataclass(frozen=True)
class BoundedListQuery:
    tenant_id: str
    site_id: str
    source_system_id: str
    limit: int
    cursor: Optional[str] = None


@dataclass(frozen=True)
class BoundedListResult(Generic[T]):
    items: Tuple[T, ...]
    next_cursor: Optional[str]


@dataclass(frozen=True)
class StagedWriteResult:
    status: str
    object_type: str
    canonical_global_id_digest: str
    previous_version: Optional[int]
    new_version: Optional[int]
    conflict_code: Optional[str] = None


class CanonicalDeviceProvider(ABC):
    @abstractmethod
    def get_by_global_id(self, global_id: GlobalId) -> Optional[Device]: ...

    @abstractmethod
    def get_by_source_identity(self, source_identity: SourceIdentity) -> Optional[Device]: ...

    @abstractmethod
    def list_bounded(self, query: BoundedListQuery) -> BoundedListResult[Device]: ...

    @abstractmethod
    def stage_create(self, command: PersistenceCommand) -> StagedWriteResult: ...

    @abstractmethod
    def stage_update(self, command: PersistenceCommand) -> StagedWriteResult: ...


class CanonicalPointProvider(ABC):
    @abstractmethod
    def get_by_global_id(self, global_id: GlobalId) -> Optional[Point]: ...

    @abstractmethod
    def get_by_source_identity(self, source_identity: SourceIdentity) -> Optional[Point]: ...

    @abstractmethod
    def list_bounded(self, query: BoundedListQuery) -> BoundedListResult[Point]: ...

    @abstractmethod
    def stage_create(self, command: PersistenceCommand) -> StagedWriteResult: ...

    @abstractmethod
    def stage_update(self, command: PersistenceCommand) -> StagedWriteResult: ...


class CanonicalTagProvider(ABC):
    @abstractmethod
    def get_by_global_id(self, global_id: GlobalId) -> Optional[Tag]: ...

    @abstractmethod
    def get_by_source_identity(self, source_identity: SourceIdentity) -> Optional[Tag]: ...

    @abstractmethod
    def list_bounded(self, query: BoundedListQuery) -> BoundedListResult[Tag]: ...

    @abstractmethod
    def stage_create(self, command: PersistenceCommand) -> StagedWriteResult: ...


class CanonicalRelationshipProvider(ABC):
    @abstractmethod
    def get_by_global_id(self, global_id: GlobalId) -> Optional[AssetRelationship]: ...

    @abstractmethod
    def list_bounded(self, query: BoundedListQuery) -> BoundedListResult[AssetRelationship]: ...

    @abstractmethod
    def stage_relationship_create(self, command: PersistenceCommand) -> StagedWriteResult: ...


class AssetGraphUnitOfWork(ABC):
    @abstractmethod
    def stage(self, command: PersistenceCommand) -> StagedWriteResult: ...

    @abstractmethod
    def validate_staged(self) -> Tuple[str, ...]: ...

    @abstractmethod
    def commit(self) -> Mapping[str, Any]: ...

    @abstractmethod
    def rollback(self, *, reason: str) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class ProviderCapabilityDeclaration:
    provider_name: str
    provider_version: str
    storage_type: str
    supports_transactions: bool
    supports_optimistic_concurrency: bool
    supports_idempotency: bool
    supports_tenant_isolation: bool
    supports_site_isolation: bool
    supports_relationship_integrity: bool
    supports_audit_binding: bool
    maximum_batch_size: int
    health_status: str
    enabled_for_canonical_writes: bool

    def serialize(self) -> dict[str, Any]:
        return {
            "providerName": self.provider_name,
            "providerVersion": self.provider_version,
            "storageType": self.storage_type,
            "supportsTransactions": self.supports_transactions,
            "supportsOptimisticConcurrency": self.supports_optimistic_concurrency,
            "supportsIdempotency": self.supports_idempotency,
            "supportsTenantIsolation": self.supports_tenant_isolation,
            "supportsSiteIsolation": self.supports_site_isolation,
            "supportsRelationshipIntegrity": self.supports_relationship_integrity,
            "supportsAuditBinding": self.supports_audit_binding,
            "maximumBatchSize": self.maximum_batch_size,
            "healthStatus": self.health_status,
            "enabledForCanonicalWrites": self.enabled_for_canonical_writes,
        }


def default_provider_capabilities() -> ProviderCapabilityDeclaration:
    return ProviderCapabilityDeclaration(
        provider_name="UNCONFIGURED_CANONICAL_PROVIDER",
        provider_version="0.0.0",
        storage_type="NONE",
        supports_transactions=False,
        supports_optimistic_concurrency=False,
        supports_idempotency=False,
        supports_tenant_isolation=False,
        supports_site_isolation=False,
        supports_relationship_integrity=False,
        supports_audit_binding=False,
        maximum_batch_size=0,
        health_status="UNAVAILABLE",
        enabled_for_canonical_writes=False,
    )
