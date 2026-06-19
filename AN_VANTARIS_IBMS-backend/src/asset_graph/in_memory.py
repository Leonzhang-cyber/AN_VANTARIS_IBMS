"""NON_PRODUCTION_IN_MEMORY_PROVIDER for Asset Graph contract validation."""
from __future__ import annotations

import base64
from threading import RLock
from typing import Dict, Iterable, Optional

from .constants import IN_MEMORY_STATUS, LifecycleStatus, OperationStatus, RelationshipType, TagType
from .errors import AssetGraphValidationError
from .models import AssetRelationship, Device, GlobalId, Point, SourceIdentity, Tag
from .provider import (
    AssetGraphProvider, DeviceQuery, OperationResult, PointQuery, QueryResult,
    RelationshipQuery, TagQuery,
)
from .validation import (
    validate_point_device, validate_query_scope, validate_relationship_scope,
    validate_tag_scope,
)


class InMemoryAssetGraphProvider(AssetGraphProvider):
    """NON_PRODUCTION_IN_MEMORY_PROVIDER; no filesystem, ORM, or runtime access."""

    PROVIDER_STATUS = IN_MEMORY_STATUS

    def __init__(self) -> None:
        self._devices: Dict[str, Device] = {}
        self._points: Dict[str, Point] = {}
        self._tags: Dict[str, Tag] = {}
        self._relationships: Dict[str, AssetRelationship] = {}
        self._device_sources: Dict[tuple, str] = {}
        self._point_sources: Dict[tuple, str] = {}
        self._source_tags: Dict[tuple, str] = {}
        self._lock = RLock()

    def _result(self, status, object_id, accepted, duplicate=False, error=None):
        return OperationResult(status, object_id, accepted, duplicate, error, self.PROVIDER_STATUS)

    @staticmethod
    def _cursor(value: str) -> str:
        return base64.urlsafe_b64encode(value.encode()).decode().rstrip("=")

    @staticmethod
    def _decode(value: str) -> str:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)).decode()

    def _page(self, items: Iterable, limit: int, cursor: Optional[str], key):
        rows = sorted(items, key=key)
        if cursor:
            after = self._decode(cursor)
            rows = [row for row in rows if key(row) > after]
        page = rows[:limit]
        next_cursor = self._cursor(key(page[-1])) if len(rows) > limit and page else None
        return tuple(page), next_cursor

    def _source_conflict(self, identities, index, global_id) -> bool:
        return any(index.get(item.uniqueness_key) not in {None, global_id} for item in identities)

    def add_device(self, device: Device) -> OperationResult:
        gid = str(device.global_id)
        with self._lock:
            existing = self._devices.get(gid)
            if existing is not None:
                return self._result(
                    OperationStatus.DUPLICATE_IDENTICAL.value if existing == device else OperationStatus.CONFLICT.value,
                    gid, existing == device, existing == device,
                    None if existing == device else "GLOBAL_ID_CONFLICT",
                )
            if self._source_conflict(device.source_identities, self._device_sources, gid):
                return self._result(OperationStatus.CONFLICT.value, gid, False, error="SOURCE_IDENTITY_CONFLICT")
            self._devices[gid] = device
            for identity in device.source_identities:
                self._device_sources[identity.uniqueness_key] = gid
        return self._result(OperationStatus.ACCEPTED.value, gid, True)

    def get_device(self, global_id: GlobalId) -> Optional[Device]:
        with self._lock: return self._devices.get(str(global_id))

    def find_device_by_source_identity(self, source_identity: SourceIdentity) -> Optional[Device]:
        with self._lock:
            gid = self._device_sources.get(source_identity.uniqueness_key)
            return self._devices.get(gid) if gid else None

    def query_devices(self, query: DeviceQuery) -> QueryResult[Device]:
        validate_query_scope(query)
        with self._lock: rows = list(self._devices.values())
        filters = (
            ("site_id", query.site_id), ("asset_id", query.parent_asset_id),
            ("lifecycle_status", query.lifecycle_status), ("operational_status", query.operational_status),
            ("device_type", query.device_type), ("manufacturer", query.manufacturer),
        )
        if not query.platform_query:
            rows = [row for row in rows if str(row.tenant_id) == query.tenant_id]
        for field, expected in filters:
            if expected is not None:
                rows = [row for row in rows if str(getattr(row, field) or "") == expected]
        if query.source_identity:
            rows = [row for row in rows if query.source_identity in row.source_identities]
        page, cursor = self._page(rows, query.limit, query.cursor, lambda row: str(row.global_id))
        return QueryResult(page, cursor, self.PROVIDER_STATUS)

    def add_point(self, point: Point) -> OperationResult:
        gid = str(point.global_id)
        with self._lock:
            device = self._devices.get(str(point.device_id))
            if device is None:
                return self._result(OperationStatus.NOT_FOUND.value, gid, False, error="DEVICE_NOT_FOUND")
            try:
                validate_point_device(point, device)
            except AssetGraphValidationError:
                return self._result(OperationStatus.VALIDATION_FAILED.value, gid, False, error="DEVICE_SCOPE_MISMATCH")
            existing = self._points.get(gid)
            if existing is not None:
                return self._result(
                    OperationStatus.DUPLICATE_IDENTICAL.value if existing == point else OperationStatus.CONFLICT.value,
                    gid, existing == point, existing == point,
                    None if existing == point else "GLOBAL_ID_OR_DEVICE_CONFLICT",
                )
            if self._source_conflict(point.source_identities, self._point_sources, gid):
                return self._result(OperationStatus.CONFLICT.value, gid, False, error="SOURCE_IDENTITY_CONFLICT")
            self._points[gid] = point
            for identity in point.source_identities:
                self._point_sources[identity.uniqueness_key] = gid
        return self._result(OperationStatus.ACCEPTED.value, gid, True)

    def get_point(self, global_id: GlobalId) -> Optional[Point]:
        with self._lock: return self._points.get(str(global_id))

    def find_point_by_source_identity(self, source_identity: SourceIdentity) -> Optional[Point]:
        with self._lock:
            gid = self._point_sources.get(source_identity.uniqueness_key)
            return self._points.get(gid) if gid else None

    def query_points(self, query: PointQuery) -> QueryResult[Point]:
        validate_query_scope(query)
        with self._lock: rows = list(self._points.values())
        if not query.platform_query:
            rows = [row for row in rows if str(row.tenant_id) == query.tenant_id]
        filters = (
            ("site_id", query.site_id), ("device_id", query.device_id),
            ("point_type", query.point_type), ("unit", query.unit),
            ("data_type", query.data_type), ("access_mode", query.access_mode),
            ("lifecycle_status", query.lifecycle_status),
        )
        for field, expected in filters:
            if expected is not None:
                rows = [row for row in rows if str(getattr(row, field) or "") == expected]
        if query.source_identity:
            rows = [row for row in rows if query.source_identity in row.source_identities]
        page, cursor = self._page(rows, query.limit, query.cursor, lambda row: str(row.global_id))
        return QueryResult(page, cursor, self.PROVIDER_STATUS)

    def add_tag(self, tag: Tag) -> OperationResult:
        gid = str(tag.tag_id); object_id = str(tag.canonical_object_id)
        with self._lock:
            canonical = self._devices.get(object_id) or self._points.get(object_id)
            if canonical is None:
                return self._result(OperationStatus.NOT_FOUND.value, gid, False, error="CANONICAL_OBJECT_NOT_FOUND")
            try:
                validate_tag_scope(tag, canonical.tenant_id, canonical.site_id)
            except AssetGraphValidationError:
                return self._result(OperationStatus.VALIDATION_FAILED.value, gid, False, error="TAG_SCOPE_MISMATCH")
            existing = self._tags.get(gid)
            if existing is not None:
                return self._result(
                    OperationStatus.DUPLICATE_IDENTICAL.value if existing == tag else OperationStatus.CONFLICT.value,
                    gid, existing == tag, existing == tag, None if existing == tag else "TAG_ID_CONFLICT",
                )
            if tag.tag_type == TagType.SOURCE_TAG_NAME.value:
                key = (str(tag.tenant_id), str(tag.source_system_id), tag.source_namespace, tag.value)
                mapped = self._source_tags.get(key)
                if mapped is not None:
                    return self._result(OperationStatus.CONFLICT.value, gid, False, error="SOURCE_TAG_CONFLICT")
                self._source_tags[key] = object_id
            self._tags[gid] = tag
        return self._result(OperationStatus.ACCEPTED.value, gid, True)

    def query_tags(self, query: TagQuery) -> QueryResult[Tag]:
        validate_query_scope(query)
        with self._lock: rows = list(self._tags.values())
        if not query.platform_query:
            rows = [row for row in rows if str(row.tenant_id) == query.tenant_id]
        filters = (
            ("site_id", query.site_id), ("canonical_object_id", query.canonical_object_id),
            ("tag_type", query.tag_type), ("source_system_id", query.source_system_id),
            ("source_namespace", query.source_namespace),
        )
        for field, expected in filters:
            if expected is not None:
                rows = [row for row in rows if str(getattr(row, field) or "") == expected]
        page, cursor = self._page(rows, query.limit, query.cursor, lambda row: str(row.tag_id))
        return QueryResult(page, cursor, self.PROVIDER_STATUS)

    def _object_scope(self, gid: str):
        item = self._devices.get(gid) or self._points.get(gid)
        return (item.tenant_id, item.site_id, type(item).__name__) if item else None

    def add_relationship(self, relationship: AssetRelationship) -> OperationResult:
        rid = str(relationship.relationship_id)
        with self._lock:
            source = self._object_scope(str(relationship.source_global_id))
            target = self._object_scope(str(relationship.target_global_id))
            if not source or not target:
                return self._result(OperationStatus.NOT_FOUND.value, rid, False, error="RELATIONSHIP_ENDPOINT_NOT_FOUND")
            if relationship.relationship_type == RelationshipType.HAS_POINT.value:
                if source[2] != "Device" or target[2] != "Point":
                    return self._result(OperationStatus.VALIDATION_FAILED.value, rid, False, error="HAS_POINT_TYPE_MISMATCH")
                point = self._points[str(relationship.target_global_id)]
                if point.device_id != relationship.source_global_id:
                    return self._result(OperationStatus.CONFLICT.value, rid, False, error="POINT_DEVICE_CONFLICT")
            try:
                validate_relationship_scope(relationship, source[0], source[1], target[0], target[1])
            except AssetGraphValidationError:
                return self._result(OperationStatus.VALIDATION_FAILED.value, rid, False, error="RELATIONSHIP_SCOPE_MISMATCH")
            existing = self._relationships.get(rid)
            if existing is not None:
                return self._result(
                    OperationStatus.DUPLICATE_IDENTICAL.value if existing == relationship else OperationStatus.CONFLICT.value,
                    rid, existing == relationship, existing == relationship,
                    None if existing == relationship else "RELATIONSHIP_ID_CONFLICT",
                )
            active_key = (
                str(relationship.source_global_id), str(relationship.target_global_id),
                relationship.relationship_type,
            )
            for item in self._relationships.values():
                if item.lifecycle_status == LifecycleStatus.ACTIVE.value and (
                    str(item.source_global_id), str(item.target_global_id), item.relationship_type
                ) == active_key:
                    return self._result(OperationStatus.CONFLICT.value, rid, False, error="ACTIVE_RELATIONSHIP_CONFLICT")
            self._relationships[rid] = relationship
        return self._result(OperationStatus.ACCEPTED.value, rid, True)

    def query_relationships(self, query: RelationshipQuery) -> QueryResult[AssetRelationship]:
        validate_query_scope(query)
        with self._lock: rows = list(self._relationships.values())
        if not query.platform_query:
            rows = [row for row in rows if str(row.tenant_id) == query.tenant_id]
        filters = (
            ("site_id", query.site_id), ("source_global_id", query.source_global_id),
            ("target_global_id", query.target_global_id), ("relationship_type", query.relationship_type),
        )
        for field, expected in filters:
            if expected is not None:
                rows = [row for row in rows if str(getattr(row, field) or "") == expected]
        if query.active_only:
            rows = [row for row in rows if row.lifecycle_status == LifecycleStatus.ACTIVE.value]
        page, cursor = self._page(rows, query.limit, query.cursor, lambda row: str(row.relationship_id))
        return QueryResult(page, cursor, self.PROVIDER_STATUS)

    def clear_for_test(self) -> None:
        with self._lock:
            self._devices.clear(); self._points.clear(); self._tags.clear()
            self._relationships.clear(); self._device_sources.clear()
            self._point_sources.clear(); self._source_tags.clear()
