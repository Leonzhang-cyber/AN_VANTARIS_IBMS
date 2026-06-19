"""Ephemeral in-memory Asset Graph read model."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional

from ..compatibility.models import ProjectionContext
from ..models import AssetRelationship, Device, Point, Tag
from ..reconciliation.models import ReconciliationInput, ReconciliationRun
from .builder import (
    build_indexes_from_materialized_run,
    build_read_model_summary,
)
from .errors import ReadModelDiscardedError, ReadModelError
from .indexes import ReadModelIndexes
from .pagination import PageResult, paginate, query_binding, validate_limit
from .projections import safe_device, safe_point, safe_relationship, safe_tag, tag_key
from .queries import DeviceListQuery, PointListQuery, RelationshipListQuery, TagListQuery
from .scope import ReadScope

LIFECYCLE_CREATED = "CREATED"
LIFECYCLE_ACTIVE = "ACTIVE"
LIFECYCLE_DISCARDED = "DISCARDED"


def _source_system_for_object(item: Device | Point | Tag | AssetRelationship) -> str | None:
    identities = getattr(item, "source_identities", None)
    if identities:
        return str(identities[0].source_system_id)
    source_system_id = getattr(item, "source_system_id", None)
    return str(source_system_id) if source_system_id else None


def _source_namespace_for_object(item: Device | Point | Tag | AssetRelationship) -> str | None:
    identities = getattr(item, "source_identities", None)
    if identities:
        return str(identities[0].source_namespace)
    source_namespace = getattr(item, "source_namespace", None)
    return str(source_namespace) if source_namespace else None


class EphemeralAssetGraphReadModel:
    def __init__(
        self,
        *,
        lifecycle_state: str,
        indexes: Optional[ReadModelIndexes],
        summary: Mapping[str, Any],
        discard_evidence: Mapping[str, Any],
    ) -> None:
        self.lifecycle_state = lifecycle_state
        self.indexes = indexes
        self.summary = summary
        self.discard_evidence = discard_evidence

    @classmethod
    def from_execution_artifacts(
        cls,
        *,
        execution_result: Mapping[str, Any],
        artifact_manifest: Mapping[str, Any],
        output_dir: Path,
        root: Path,
    ) -> "EphemeralAssetGraphReadModel":
        from .builder import build_ephemeral_read_model_from_execution

        indexes, summary, _, _, _ = build_ephemeral_read_model_from_execution(
            execution_result=execution_result,
            artifact_manifest=artifact_manifest,
            output_dir=output_dir,
            root=root,
        )
        return cls(lifecycle_state=LIFECYCLE_ACTIVE, indexes=indexes, summary=summary, discard_evidence={})

    @classmethod
    def from_materialized_run(
        cls,
        *,
        execution_result: Mapping[str, Any],
        run: ReconciliationRun,
        reconciliation_input: ReconciliationInput,
        context: ProjectionContext,
        scope_policy: ReadScope,
    ) -> "EphemeralAssetGraphReadModel":
        indexes, stats = build_indexes_from_materialized_run(run, reconciliation_input, context)
        summary = build_read_model_summary(
            execution_result=execution_result,
            indexes=indexes,
            stats=stats,
            scope_policy=scope_policy.serialize(),
        )
        return cls(lifecycle_state=LIFECYCLE_ACTIVE, indexes=indexes, summary=summary, discard_evidence={})

    def _require_active(self) -> ReadModelIndexes:
        if self.lifecycle_state == LIFECYCLE_DISCARDED:
            raise ReadModelDiscardedError("read model has been discarded")
        if self.indexes is None:
            raise ReadModelError("read model indexes are unavailable")
        return self.indexes

    def _object_scope_fields(self, item: Device | Point | Tag | AssetRelationship) -> tuple[str, str | None, str | None]:
        tenant_id = str(item.tenant_id)
        site_id = str(item.site_id) if getattr(item, "site_id", None) else None
        source_system = _source_system_for_object(item)
        return tenant_id, site_id, source_system

    def _matches_common_filters(
        self,
        item: Device | Point | Tag | AssetRelationship,
        *,
        tenant_id: str | None,
        site_id: str | None,
        source_system_id: str | None,
        source_namespace: str | None,
    ) -> bool:
        if tenant_id is not None and str(item.tenant_id) != tenant_id:
            return False
        if site_id is not None and str(getattr(item, "site_id", "")) != site_id:
            return False
        item_source_system = _source_system_for_object(item)
        if source_system_id is not None and item_source_system != source_system_id:
            return False
        item_source_namespace = _source_namespace_for_object(item)
        if source_namespace is not None and item_source_namespace != source_namespace:
            return False
        return True

    def _in_scope(self, item: Device | Point | Tag | AssetRelationship, scope: ReadScope) -> bool:
        tenant_id, site_id, source_system = self._object_scope_fields(item)
        return scope.allows(tenant_id=tenant_id, site_id=site_id, source_system_id=source_system)

    def discard(self, *, reason: str = "READ_MODEL_DISCARDED") -> Mapping[str, Any]:
        self.lifecycle_state = LIFECYCLE_DISCARDED
        self.indexes = None
        self.discard_evidence = {
            "reason": reason,
            "modelDigest": self.summary.get("modelDigest"),
            "executionResultDigest": self.summary.get("executionResultDigest"),
        }
        return dict(self.discard_evidence)

    def get_device(self, global_id: str, scope: ReadScope) -> Optional[dict[str, Any]]:
        indexes = self._require_active()
        device = indexes.devices_by_global_id.get(global_id)
        if device is None or not self._in_scope(device, scope):
            return None
        return safe_device(device)

    def get_point(self, global_id: str, scope: ReadScope) -> Optional[dict[str, Any]]:
        indexes = self._require_active()
        point = indexes.points_by_global_id.get(global_id)
        if point is None or not self._in_scope(point, scope):
            return None
        return safe_point(point)

    def get_tag(self, tag_key_value: str, scope: ReadScope) -> Optional[dict[str, Any]]:
        indexes = self._require_active()
        tag = indexes.tags_by_key.get(tag_key_value)
        if tag is None or not self._in_scope(tag, scope):
            return None
        return safe_tag(tag)

    def get_relationship(self, global_id: str, scope: ReadScope) -> Optional[dict[str, Any]]:
        indexes = self._require_active()
        relationship = indexes.relationships_by_global_id.get(global_id)
        if relationship is None or not self._in_scope(relationship, scope):
            return None
        return safe_relationship(relationship)

    def list_devices(self, query: DeviceListQuery) -> PageResult:
        indexes = self._require_active()
        rows = [
            device
            for device in indexes.devices_by_global_id.values()
            if self._in_scope(device, query.scope)
            and self._matches_common_filters(
                device,
                tenant_id=query.tenant_id,
                site_id=query.site_id,
                source_system_id=query.source_system_id,
                source_namespace=query.source_namespace,
            )
            and (query.device_type is None or device.device_type == query.device_type)
            and (query.lifecycle_status is None or device.lifecycle_status == query.lifecycle_status)
            and (query.operational_status is None or device.operational_status == query.operational_status)
        ]
        binding = query_binding(
            {
                "type": "devices",
                "scope": query.scope.serialize(),
                "tenantId": query.tenant_id,
                "siteId": query.site_id,
                "sourceSystemId": query.source_system_id,
                "sourceNamespace": query.source_namespace,
                "deviceType": query.device_type,
                "lifecycleStatus": query.lifecycle_status,
                "operationalStatus": query.operational_status,
            }
        )
        page = paginate(
            rows,
            limit=validate_limit(query.limit),
            cursor=query.cursor,
            query_binding_value=binding,
            sort_key=lambda item: str(item.global_id),
        )
        return PageResult(
            items=tuple(safe_device(item) for item in page.items),
            next_cursor=page.next_cursor,
            limit=page.limit,
            query_binding=page.query_binding,
        )

    def list_points(self, query: PointListQuery) -> PageResult:
        indexes = self._require_active()
        rows = [
            point
            for point in indexes.points_by_global_id.values()
            if self._in_scope(point, query.scope)
            and self._matches_common_filters(
                point,
                tenant_id=query.tenant_id,
                site_id=query.site_id,
                source_system_id=query.source_system_id,
                source_namespace=query.source_namespace,
            )
            and (query.lifecycle_status is None or point.lifecycle_status == query.lifecycle_status)
        ]
        binding = query_binding(
            {
                "type": "points",
                "scope": query.scope.serialize(),
                "tenantId": query.tenant_id,
                "siteId": query.site_id,
                "sourceSystemId": query.source_system_id,
                "sourceNamespace": query.source_namespace,
                "lifecycleStatus": query.lifecycle_status,
            }
        )
        page = paginate(
            rows,
            limit=validate_limit(query.limit),
            cursor=query.cursor,
            query_binding_value=binding,
            sort_key=lambda item: str(item.global_id),
        )
        return PageResult(
            items=tuple(safe_point(item) for item in page.items),
            next_cursor=page.next_cursor,
            limit=page.limit,
            query_binding=page.query_binding,
        )

    def list_tags(self, query: TagListQuery) -> PageResult:
        indexes = self._require_active()
        rows = [
            tag
            for tag in indexes.tags_by_key.values()
            if self._in_scope(tag, query.scope)
            and self._matches_common_filters(
                tag,
                tenant_id=query.tenant_id,
                site_id=query.site_id,
                source_system_id=query.source_system_id,
                source_namespace=query.source_namespace,
            )
            and (query.tag_namespace is None or tag.source_namespace == query.tag_namespace)
        ]
        binding = query_binding(
            {
                "type": "tags",
                "scope": query.scope.serialize(),
                "tenantId": query.tenant_id,
                "siteId": query.site_id,
                "sourceSystemId": query.source_system_id,
                "sourceNamespace": query.source_namespace,
                "tagNamespace": query.tag_namespace,
            }
        )
        page = paginate(
            rows,
            limit=validate_limit(query.limit),
            cursor=query.cursor,
            query_binding_value=binding,
            sort_key=tag_key,
        )
        return PageResult(
            items=tuple(safe_tag(item) for item in page.items),
            next_cursor=page.next_cursor,
            limit=page.limit,
            query_binding=page.query_binding,
        )

    def list_relationships(self, query: RelationshipListQuery) -> PageResult:
        indexes = self._require_active()
        rows = [
            relationship
            for relationship in indexes.relationships_by_global_id.values()
            if self._in_scope(relationship, query.scope)
            and self._matches_common_filters(
                relationship,
                tenant_id=query.tenant_id,
                site_id=query.site_id,
                source_system_id=query.source_system_id,
                source_namespace=None,
            )
            and (query.relationship_type is None or relationship.relationship_type == query.relationship_type)
        ]
        binding = query_binding(
            {
                "type": "relationships",
                "scope": query.scope.serialize(),
                "tenantId": query.tenant_id,
                "siteId": query.site_id,
                "sourceSystemId": query.source_system_id,
                "relationshipType": query.relationship_type,
            }
        )
        page = paginate(
            rows,
            limit=validate_limit(query.limit),
            cursor=query.cursor,
            query_binding_value=binding,
            sort_key=lambda item: str(item.relationship_id),
        )
        return PageResult(
            items=tuple(safe_relationship(item) for item in page.items),
            next_cursor=page.next_cursor,
            limit=page.limit,
            query_binding=page.query_binding,
        )

    def list_points_for_device(self, device_global_id: str, scope: ReadScope) -> tuple[dict[str, Any], ...]:
        indexes = self._require_active()
        device = indexes.devices_by_global_id.get(device_global_id)
        if device is None or not self._in_scope(device, scope):
            return ()
        return tuple(
            safe_point(indexes.points_by_global_id[point_id])
            for point_id in indexes.points_by_device_global_id.get(device_global_id, ())
            if point_id in indexes.points_by_global_id
        )

    def list_relationships_for_source(self, source_global_id: str, scope: ReadScope) -> tuple[dict[str, Any], ...]:
        indexes = self._require_active()
        return tuple(
            safe_relationship(indexes.relationships_by_global_id[rel_id])
            for rel_id in indexes.relationships_by_source_global_id.get(source_global_id, ())
            if rel_id in indexes.relationships_by_global_id
            and self._in_scope(indexes.relationships_by_global_id[rel_id], scope)
        )

    def list_relationships_for_target(self, target_global_id: str, scope: ReadScope) -> tuple[dict[str, Any], ...]:
        indexes = self._require_active()
        return tuple(
            safe_relationship(indexes.relationships_by_global_id[rel_id])
            for rel_id in indexes.relationships_by_target_global_id.get(target_global_id, ())
            if rel_id in indexes.relationships_by_global_id
            and self._in_scope(indexes.relationships_by_global_id[rel_id], scope)
        )
