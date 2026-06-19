"""Validation helpers for bounded Asset Graph operations."""
from __future__ import annotations

from .constants import MAX_QUERY_LIMIT
from .errors import AssetGraphValidationError
from .models import AssetRelationship, Device, Point, Tag


def validate_query_scope(query) -> None:
    if not query.platform_query and not str(query.tenant_id or "").strip():
        raise AssetGraphValidationError("tenant_id is required")
    if query.limit < 1 or query.limit > MAX_QUERY_LIMIT:
        raise AssetGraphValidationError(f"limit must be between 1 and {MAX_QUERY_LIMIT}")


def validate_point_device(point: Point, device: Device) -> None:
    if point.device_id != device.global_id:
        raise AssetGraphValidationError("Point must belong to the referenced Device")
    if point.tenant_id != device.tenant_id:
        raise AssetGraphValidationError("Point and Device tenant scope must match")
    if point.site_id != device.site_id:
        raise AssetGraphValidationError("Point and Device site scope must match")


def validate_tag_scope(tag: Tag, tenant_id, site_id) -> None:
    if tag.tenant_id != tenant_id:
        raise AssetGraphValidationError("Tag tenant scope must match canonical object")
    if tag.site_id != site_id:
        raise AssetGraphValidationError("Tag site scope must match canonical object")


def validate_relationship_scope(
    relationship: AssetRelationship,
    source_tenant, source_site, target_tenant, target_site,
) -> None:
    if relationship.tenant_id != source_tenant or relationship.tenant_id != target_tenant:
        raise AssetGraphValidationError("relationship tenant scope mismatch")
    cross_site_allowed = relationship.relationship_type in {"CONNECTED_TO", "SERVES"}
    if not cross_site_allowed and source_site != target_site:
        raise AssetGraphValidationError("relationship site scope mismatch")
    if relationship.site_id is not None and relationship.site_id not in {source_site, target_site}:
        raise AssetGraphValidationError("relationship site_id does not match endpoints")
