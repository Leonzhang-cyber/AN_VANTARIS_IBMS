"""Safe query projections for ephemeral read model results."""
from __future__ import annotations

from typing import Any, Mapping

from ..models import AssetRelationship, Device, Point, Tag


def safe_device(device: Device) -> dict[str, Any]:
    return {
        "globalId": str(device.global_id),
        "tenantId": str(device.tenant_id),
        "siteId": str(device.site_id) if device.site_id else None,
        "displayName": device.display_name,
        "deviceType": device.device_type,
        "lifecycleStatus": device.lifecycle_status,
        "operationalStatus": device.operational_status,
        "contractVersion": device.contract_version,
    }


def safe_point(point: Point) -> dict[str, Any]:
    return {
        "globalId": str(point.global_id),
        "tenantId": str(point.tenant_id),
        "siteId": str(point.site_id) if point.site_id else None,
        "deviceGlobalId": str(point.device_id),
        "displayName": point.display_name,
        "pointType": point.point_type,
        "unit": point.unit,
        "dataType": point.data_type,
        "accessMode": point.access_mode,
        "lifecycleStatus": point.lifecycle_status,
        "contractVersion": point.contract_version,
    }


def safe_tag(tag: Tag) -> dict[str, Any]:
    return {
        "tagKey": str(tag.tag_id),
        "tenantId": str(tag.tenant_id),
        "canonicalObjectId": str(tag.canonical_object_id),
        "tagType": tag.tag_type,
        "value": tag.value,
        "tagNamespace": tag.source_namespace,
        "contractVersion": tag.contract_version,
    }


def safe_relationship(relationship: AssetRelationship) -> dict[str, Any]:
    return {
        "globalId": str(relationship.relationship_id),
        "tenantId": str(relationship.tenant_id),
        "siteId": str(relationship.site_id) if relationship.site_id else None,
        "relationshipType": relationship.relationship_type,
        "sourceGlobalId": str(relationship.source_global_id),
        "targetGlobalId": str(relationship.target_global_id),
        "lifecycleStatus": relationship.lifecycle_status,
        "contractVersion": relationship.contract_version,
    }


def tag_key(tag: Tag) -> str:
    return str(tag.tag_id)
