"""Immutable canonical Device, Point, Tag and relationship models."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timezone
from typing import Any, Mapping, Optional, Tuple

from .constants import (
    LifecycleStatus, OperationalStatus, PointAccessMode, RelationshipType,
    TagType, MAX_IDENTIFIER_LENGTH,
)
from .errors import AssetGraphValidationError

SECRET_PATTERN = re.compile(
    r"(password|private[_-]?key|secret|credential|token|connect[_-]?config|"
    r"protocol[_-]?config|authorization|telemetry[_-]?(value|payload|history)|live[_-]?value)",
    re.IGNORECASE,
)


def _text(name: str, value: Any, required: bool = True) -> None:
    if value is None:
        if required:
            raise AssetGraphValidationError(f"{name} is required")
        return
    if not isinstance(value, str) or (required and not value.strip()):
        raise AssetGraphValidationError(f"{name} must be a non-empty string")
    if len(value) > MAX_IDENTIFIER_LENGTH:
        raise AssetGraphValidationError(f"{name} exceeds maximum length")
    if SECRET_PATTERN.search(value):
        raise AssetGraphValidationError(f"{name} contains prohibited secret-like content")


def _aware(name: str, value: datetime) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise AssetGraphValidationError(f"{name} must be timezone-aware")


def _serialize(value: Any) -> str:
    data = asdict(value)
    for key, item in tuple(data.items()):
        if isinstance(item, datetime):
            data[key] = item.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _mapping(cls, value: Mapping[str, Any]):
    allowed = {field.name for field in fields(cls)}
    for key in value:
        if SECRET_PATTERN.search(str(key)):
            raise AssetGraphValidationError(f"prohibited field: {key}")
        if key not in allowed:
            raise AssetGraphValidationError(f"unknown field: {key}")
    return cls(**value)


@dataclass(frozen=True, order=True)
class GlobalId:
    value: str

    def __post_init__(self): _text("global_id", self.value)
    def __str__(self): return self.value


@dataclass(frozen=True, order=True)
class TenantId:
    value: str

    def __post_init__(self): _text("tenant_id", self.value)
    def __str__(self): return self.value


@dataclass(frozen=True, order=True)
class SiteId:
    value: str

    def __post_init__(self): _text("site_id", self.value)
    def __str__(self): return self.value


@dataclass(frozen=True, order=True)
class SourceSystemId:
    value: str

    def __post_init__(self): _text("source_system_id", self.value)
    def __str__(self): return self.value


@dataclass(frozen=True, order=True)
class SourceObjectId:
    value: str

    def __post_init__(self): _text("source_object_id", self.value)
    def __str__(self): return self.value


@dataclass(frozen=True)
class CanonicalIdentity:
    global_id: GlobalId
    tenant_id: TenantId
    site_id: Optional[SiteId]
    canonical_object_type: str
    identity_version: str

    def __post_init__(self):
        _text("canonical_object_type", self.canonical_object_type)
        _text("identity_version", self.identity_version)
    def serialize(self): return _serialize(self)


@dataclass(frozen=True, order=True)
class SourceIdentity:
    source_system_id: SourceSystemId
    source_object_id: SourceObjectId
    source_object_type: str
    source_namespace: str
    external_tag_name: Optional[str] = None
    source_version: Optional[str] = None

    def __post_init__(self):
        _text("source_object_type", self.source_object_type)
        _text("source_namespace", self.source_namespace)
        _text("external_tag_name", self.external_tag_name, False)
        _text("source_version", self.source_version, False)

    @property
    def uniqueness_key(self) -> tuple[str, str, str, str]:
        return (
            str(self.source_system_id), self.source_namespace,
            self.source_object_type, str(self.source_object_id),
        )


@dataclass(frozen=True)
class Device:
    global_id: GlobalId
    tenant_id: TenantId
    site_id: Optional[SiteId]
    asset_id: Optional[GlobalId]
    display_name: str
    description: Optional[str]
    device_type: str
    manufacturer: Optional[str]
    model: Optional[str]
    serial_number: Optional[str]
    lifecycle_status: str
    operational_status: str
    classification_ids: Tuple[str, ...]
    source_identities: Tuple[SourceIdentity, ...]
    created_at: datetime
    updated_at: datetime
    contract_version: str
    metadata_classification: str

    def __post_init__(self):
        _text("display_name", self.display_name)
        _text("description", self.description, False)
        _text("device_type", self.device_type)
        for name in ("manufacturer", "model", "serial_number"):
            _text(name, getattr(self, name), False)
        if self.lifecycle_status not in {item.value for item in LifecycleStatus}:
            raise AssetGraphValidationError("invalid lifecycle_status")
        if self.operational_status not in {item.value for item in OperationalStatus}:
            raise AssetGraphValidationError("invalid operational_status")
        if len({item.uniqueness_key for item in self.source_identities}) != len(self.source_identities):
            raise AssetGraphValidationError("duplicate source identity")
        _aware("created_at", self.created_at); _aware("updated_at", self.updated_at)
        if self.updated_at < self.created_at:
            raise AssetGraphValidationError("updated_at must not precede created_at")
        _text("contract_version", self.contract_version); _text("metadata_classification", self.metadata_classification)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]): return _mapping(cls, value)
    def serialize(self): return _serialize(self)


@dataclass(frozen=True)
class Point:
    global_id: GlobalId
    tenant_id: TenantId
    site_id: Optional[SiteId]
    device_id: GlobalId
    display_name: str
    point_type: str
    unit: Optional[str]
    data_type: str
    access_mode: str
    lifecycle_status: str
    classification_ids: Tuple[str, ...]
    source_identities: Tuple[SourceIdentity, ...]
    created_at: datetime
    updated_at: datetime
    contract_version: str
    metadata_classification: str

    def __post_init__(self):
        _text("display_name", self.display_name); _text("point_type", self.point_type)
        _text("unit", self.unit, False); _text("data_type", self.data_type)
        if self.access_mode not in {item.value for item in PointAccessMode}:
            raise AssetGraphValidationError("invalid access_mode")
        if self.lifecycle_status not in {item.value for item in LifecycleStatus}:
            raise AssetGraphValidationError("invalid lifecycle_status")
        if len({item.uniqueness_key for item in self.source_identities}) != len(self.source_identities):
            raise AssetGraphValidationError("duplicate source identity")
        _aware("created_at", self.created_at); _aware("updated_at", self.updated_at)
        _text("contract_version", self.contract_version); _text("metadata_classification", self.metadata_classification)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]): return _mapping(cls, value)
    def serialize(self): return _serialize(self)


@dataclass(frozen=True)
class Tag:
    tag_id: GlobalId
    tenant_id: TenantId
    site_id: Optional[SiteId]
    canonical_object_id: GlobalId
    tag_type: str
    value: str
    source_system_id: Optional[SourceSystemId]
    source_namespace: Optional[str]
    contract_version: str

    def __post_init__(self):
        if self.tag_type not in {item.value for item in TagType}:
            raise AssetGraphValidationError("invalid tag_type")
        _text("tag value", self.value)
        _text("source_namespace", self.source_namespace, False)
        if self.tag_type == TagType.SOURCE_TAG_NAME.value and (not self.source_system_id or not self.source_namespace):
            raise AssetGraphValidationError("source tag requires source system and namespace")
        _text("contract_version", self.contract_version)

    def serialize(self): return _serialize(self)


@dataclass(frozen=True)
class AssetRelationship:
    relationship_id: GlobalId
    tenant_id: TenantId
    site_id: Optional[SiteId]
    relationship_type: str
    source_global_id: GlobalId
    target_global_id: GlobalId
    lifecycle_status: str
    valid_from: datetime
    valid_to: Optional[datetime]
    contract_version: str

    def __post_init__(self):
        if self.relationship_type not in {item.value for item in RelationshipType}:
            raise AssetGraphValidationError("invalid relationship_type")
        if self.source_global_id == self.target_global_id:
            raise AssetGraphValidationError("self relationship is not permitted")
        if self.lifecycle_status not in {item.value for item in LifecycleStatus}:
            raise AssetGraphValidationError("invalid lifecycle_status")
        _aware("valid_from", self.valid_from)
        if self.valid_to is not None:
            _aware("valid_to", self.valid_to)
            if self.valid_to < self.valid_from:
                raise AssetGraphValidationError("valid_to must not precede valid_from")
        _text("contract_version", self.contract_version)

    def serialize(self): return _serialize(self)


@dataclass(frozen=True)
class AuditEventDescription:
    """Future audit hook only; Asset Graph never owns AuditRecord persistence."""
    event_class: str
    action: str
    object_type: str
    global_id: GlobalId
    tenant_id: TenantId
    site_id: Optional[SiteId]
