"""Immutable sanitized legacy snapshots and projection result models."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional, Tuple

from ..models import (
    AssetRelationship, Device, GlobalId, Point, SiteId, SourceIdentity, Tag,
    TenantId,
)
from .constants import MAPPING_VERSION, ProjectionCategory

_PROHIBITED_KEY = re.compile(
    r"(password|private.?key|secret|credential|token|api.?key|authorization|"
    r"connect.?config|connection.?string|certificate|session.?state|runtime.?state|"
    r"current.?value|live.?value|telemetry|command.?payload|raw.?config|vc.?json|public.?key)",
    re.IGNORECASE,
)
_PROHIBITED_VALUE = re.compile(
    r"(bearer\s+|-----BEGIN .*PRIVATE KEY-----|password\s*[=:]|token\s*[=:]|"
    r"api[_-]?key\s*[=:]|://[^/\s:]+:[^@\s]+@)",
    re.IGNORECASE,
)


class ProhibitedSourceField(ValueError):
    pass


def sanitized_mapping(value: Mapping[str, Any], allowed: set[str]) -> dict[str, Any]:
    result = {}
    for key, item in value.items():
        if _PROHIBITED_KEY.search(str(key)):
            raise ProhibitedSourceField(f"prohibited source field: {key}")
        if key not in allowed:
            continue
        if isinstance(item, str) and _PROHIBITED_VALUE.search(item):
            raise ProhibitedSourceField(f"prohibited source value in: {key}")
        result[key] = item
    return result


def safe_label(value: Optional[str]) -> bool:
    return value is None or not _PROHIBITED_VALUE.search(value)


def aware(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class LegacyDeviceSnapshot:
    source_id: str
    device_name: str
    device_code: Optional[str] = None
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    device_type: Optional[str] = None
    status: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    source_version: Optional[str] = None
    parent_reference: Optional[str] = None
    source_tenant_id: Optional[str] = None
    source_site_id: Optional[str] = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "LegacyDeviceSnapshot":
        aliases = dict(value)
        if "id" in aliases and "source_id" not in aliases:
            aliases["source_id"] = aliases.pop("id")
        allowed = set(cls.__dataclass_fields__)
        return cls(**sanitized_mapping(aliases, allowed))


@dataclass(frozen=True)
class LegacyFieldSnapshot:
    source_id: str
    field_code: str
    field_name: str
    field_type: str
    unit: Optional[str] = None
    description: Optional[str] = None
    access_mode: Optional[str] = None
    is_configuration: bool = False
    source_version: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "LegacyFieldSnapshot":
        aliases = dict(value)
        if "id" in aliases and "source_id" not in aliases:
            aliases["source_id"] = aliases.pop("id")
        allowed = set(cls.__dataclass_fields__)
        return cls(**sanitized_mapping(aliases, allowed))


@dataclass(frozen=True)
class ProjectionContext:
    tenant_id: str
    source_system_id: str
    source_namespace: str
    site_id: Optional[str] = None
    parent_asset_id: Optional[str] = None
    metadata_classification: str = "INTERNAL"
    default_device_type: Optional[str] = None
    site_scope_mode: str = "SINGLE_SITE_STRICT"
    primary_site_id: Optional[str] = None
    allowed_site_ids: Tuple[str, ...] = ()

    def allows_record_site(self, record_site_id: Optional[str]) -> bool:
        if record_site_id is None or not str(record_site_id).strip():
            return True
        record_site = str(record_site_id).strip()
        if self.site_scope_mode == "MULTI_SITE_DECLARED":
            return record_site in self.allowed_site_ids
        declared_site = self.site_id or self.primary_site_id
        if declared_site:
            return record_site == declared_site
        return True


@dataclass(frozen=True)
class MappingDecision:
    source_field: str
    canonical_field: str
    disposition: str
    note: str


@dataclass(frozen=True)
class UnresolvedRelationship:
    relationship_type: str
    source_reference: str
    target_reference: str
    reason: str


@dataclass(frozen=True)
class ProjectionAuditMetadata:
    source_model: str
    projection_action: str
    tenant_id: Optional[str]
    site_id: Optional[str]
    mapping_version: str
    result_category: str


@dataclass(frozen=True)
class ProjectionResult:
    accepted: bool
    category: str
    canonical_device: Optional[Device] = None
    canonical_points: Tuple[Point, ...] = ()
    canonical_tags: Tuple[Tag, ...] = ()
    relationships: Tuple[AssetRelationship, ...] = ()
    unresolved_relationships: Tuple[UnresolvedRelationship, ...] = ()
    warnings: Tuple[str, ...] = ()
    reviews: Tuple[str, ...] = ()
    omitted_fields: Tuple[str, ...] = ()
    source_identity: Optional[SourceIdentity] = None
    mapping_version: str = MAPPING_VERSION
    error_code: Optional[str] = None

    def serialize(self) -> str:
        def convert(item):
            if hasattr(item, "serialize"):
                return json.loads(item.serialize())
            if isinstance(item, datetime):
                return item.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            return item

        data = asdict(self)
        for key in ("canonical_device",):
            if getattr(self, key) is not None:
                data[key] = convert(getattr(self, key))
        for key in ("canonical_points", "canonical_tags", "relationships"):
            data[key] = [convert(item) for item in getattr(self, key)]
        return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)

    @property
    def audit_metadata(self) -> ProjectionAuditMetadata:
        return ProjectionAuditMetadata(
            source_model="IMSDevice",
            projection_action="LEGACY_DEVICE_READ_PROJECTION",
            tenant_id=str(self.canonical_device.tenant_id) if self.canonical_device else None,
            site_id=str(self.canonical_device.site_id) if self.canonical_device and self.canonical_device.site_id else None,
            mapping_version=self.mapping_version,
            result_category=self.category,
        )


@dataclass(frozen=True)
class BatchProjectionResult:
    results: Tuple[ProjectionResult, ...]
    mapping_version: str = MAPPING_VERSION

    @property
    def accepted_count(self) -> int:
        return sum(1 for item in self.results if item.accepted)
