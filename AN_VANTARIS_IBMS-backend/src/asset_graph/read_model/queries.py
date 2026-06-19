"""Bounded query objects for ephemeral read model access."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .scope import ReadScope


@dataclass(frozen=True)
class DeviceListQuery:
    scope: ReadScope
    tenant_id: Optional[str] = None
    site_id: Optional[str] = None
    source_system_id: Optional[str] = None
    source_namespace: Optional[str] = None
    device_type: Optional[str] = None
    lifecycle_status: Optional[str] = None
    operational_status: Optional[str] = None
    limit: Optional[int] = None
    cursor: Optional[str] = None


@dataclass(frozen=True)
class PointListQuery:
    scope: ReadScope
    tenant_id: Optional[str] = None
    site_id: Optional[str] = None
    source_system_id: Optional[str] = None
    source_namespace: Optional[str] = None
    device_type: Optional[str] = None
    lifecycle_status: Optional[str] = None
    operational_status: Optional[str] = None
    limit: Optional[int] = None
    cursor: Optional[str] = None


@dataclass(frozen=True)
class TagListQuery:
    scope: ReadScope
    tenant_id: Optional[str] = None
    site_id: Optional[str] = None
    source_system_id: Optional[str] = None
    source_namespace: Optional[str] = None
    tag_namespace: Optional[str] = None
    limit: Optional[int] = None
    cursor: Optional[str] = None


@dataclass(frozen=True)
class RelationshipListQuery:
    scope: ReadScope
    tenant_id: Optional[str] = None
    site_id: Optional[str] = None
    source_system_id: Optional[str] = None
    relationship_type: Optional[str] = None
    limit: Optional[int] = None
    cursor: Optional[str] = None
