"""Storage-neutral Asset Graph provider interface and bounded specifications."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Optional, Tuple, TypeVar

from .constants import DEFAULT_QUERY_LIMIT
from .models import AssetRelationship, Device, GlobalId, Point, SourceIdentity, Tag

T = TypeVar("T")


@dataclass(frozen=True)
class OperationResult:
    status: str
    object_id: str
    accepted: bool
    duplicate: bool = False
    error_code: Optional[str] = None
    provider_status: str = ""


@dataclass(frozen=True)
class QueryResult(Generic[T]):
    items: Tuple[T, ...]
    next_cursor: Optional[str]
    provider_status: str


@dataclass(frozen=True)
class DeviceQuery:
    tenant_id: Optional[str] = None
    site_id: Optional[str] = None
    parent_asset_id: Optional[str] = None
    lifecycle_status: Optional[str] = None
    operational_status: Optional[str] = None
    device_type: Optional[str] = None
    manufacturer: Optional[str] = None
    source_identity: Optional[SourceIdentity] = None
    limit: int = DEFAULT_QUERY_LIMIT
    cursor: Optional[str] = None
    platform_query: bool = False


@dataclass(frozen=True)
class PointQuery:
    tenant_id: Optional[str] = None
    site_id: Optional[str] = None
    device_id: Optional[str] = None
    point_type: Optional[str] = None
    unit: Optional[str] = None
    data_type: Optional[str] = None
    access_mode: Optional[str] = None
    lifecycle_status: Optional[str] = None
    source_identity: Optional[SourceIdentity] = None
    limit: int = DEFAULT_QUERY_LIMIT
    cursor: Optional[str] = None
    platform_query: bool = False


@dataclass(frozen=True)
class RelationshipQuery:
    tenant_id: Optional[str] = None
    site_id: Optional[str] = None
    source_global_id: Optional[str] = None
    target_global_id: Optional[str] = None
    relationship_type: Optional[str] = None
    active_only: bool = True
    limit: int = DEFAULT_QUERY_LIMIT
    cursor: Optional[str] = None
    platform_query: bool = False


@dataclass(frozen=True)
class TagQuery:
    tenant_id: Optional[str] = None
    site_id: Optional[str] = None
    canonical_object_id: Optional[str] = None
    tag_type: Optional[str] = None
    source_system_id: Optional[str] = None
    source_namespace: Optional[str] = None
    limit: int = DEFAULT_QUERY_LIMIT
    cursor: Optional[str] = None
    platform_query: bool = False


class AssetGraphProvider(ABC):
    @abstractmethod
    def add_device(self, device: Device) -> OperationResult: ...
    @abstractmethod
    def get_device(self, global_id: GlobalId) -> Optional[Device]: ...
    @abstractmethod
    def find_device_by_source_identity(self, source_identity: SourceIdentity) -> Optional[Device]: ...
    @abstractmethod
    def query_devices(self, query: DeviceQuery) -> QueryResult[Device]: ...
    @abstractmethod
    def add_point(self, point: Point) -> OperationResult: ...
    @abstractmethod
    def get_point(self, global_id: GlobalId) -> Optional[Point]: ...
    @abstractmethod
    def find_point_by_source_identity(self, source_identity: SourceIdentity) -> Optional[Point]: ...
    @abstractmethod
    def query_points(self, query: PointQuery) -> QueryResult[Point]: ...
    @abstractmethod
    def add_tag(self, tag: Tag) -> OperationResult: ...
    @abstractmethod
    def query_tags(self, query: TagQuery) -> QueryResult[Tag]: ...
    @abstractmethod
    def add_relationship(self, relationship: AssetRelationship) -> OperationResult: ...
    @abstractmethod
    def query_relationships(self, query: RelationshipQuery) -> QueryResult[AssetRelationship]: ...
