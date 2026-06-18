"""Assets local provider (read-only skeleton)."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _asset(
    *,
    asset_id: str,
    asset_code: str,
    asset_name: str,
    asset_type: str,
    asset_category: str,
    lifecycle_status: str,
    operational_status: str,
    site_id: str,
    site_name: str,
    building_id: str,
    building_name: str,
    floor_id: str,
    floor_name: str,
    zone_id: str,
    zone_name: str,
    system_id: str,
    system_name: str,
    parent_asset_id: str,
    children_asset_ids: List[str],
    related_asset_ids: List[str],
    source_record_id: str,
    tags: List[str],
    metadata: Dict[str, Any],
    limitations: List[str],
) -> Dict[str, Any]:
    now = _now_iso()
    return {
        "assetId": asset_id,
        "assetCode": asset_code,
        "assetName": asset_name,
        "assetType": asset_type,
        "assetCategory": asset_category,
        "lifecycleStatus": lifecycle_status,
        "operationalStatus": operational_status,
        "siteId": site_id,
        "siteName": site_name,
        "buildingId": building_id,
        "buildingName": building_name,
        "floorId": floor_id,
        "floorName": floor_name,
        "zoneId": zone_id,
        "zoneName": zone_name,
        "systemId": system_id,
        "systemName": system_name,
        "parentAssetId": parent_asset_id,
        "childrenAssetIds": children_asset_ids,
        "relatedAssetIds": related_asset_ids,
        "sourceSystem": "vantaris-one-platform",
        "sourceRecordId": source_record_id,
        "provider": "local-assets-provider",
        "runtimeMode": "skeleton",
        "sourceSemantics": "ibms-neutral",
        "mockData": True,
        "createdAt": now,
        "updatedAt": now,
        "tags": tags,
        "metadata": metadata,
        "limitations": limitations,
        "runtimeLinked": False,
        "certified": False,
        "iec62443Certified": False,
    }


def _base_assets() -> List[Dict[str, Any]]:
    base_limitations = [
        "No DB asset store.",
        "Runtime discovery is not integrated.",
        "EDGE/LINK integration is not integrated.",
    ]
    return [
        _asset(
            asset_id="site-main",
            asset_code="SITE-MAIN",
            asset_name="Main Site",
            asset_type="site",
            asset_category="location",
            lifecycle_status="active",
            operational_status="online",
            site_id="site-main",
            site_name="Main Site",
            building_id="",
            building_name="",
            floor_id="",
            floor_name="",
            zone_id="",
            zone_name="",
            system_id="",
            system_name="",
            parent_asset_id="",
            children_asset_ids=["building-main"],
            related_asset_ids=[],
            source_record_id="asset-site-main",
            tags=["site", "foundation"],
            metadata={"stage": "assets-r1", "scope": "ibms-neutral"},
            limitations=base_limitations,
        ),
        _asset(
            asset_id="building-main",
            asset_code="BLDG-MAIN",
            asset_name="Main Building",
            asset_type="building",
            asset_category="location",
            lifecycle_status="active",
            operational_status="online",
            site_id="site-main",
            site_name="Main Site",
            building_id="building-main",
            building_name="Main Building",
            floor_id="",
            floor_name="",
            zone_id="",
            zone_name="",
            system_id="",
            system_name="",
            parent_asset_id="site-main",
            children_asset_ids=["floor-l1"],
            related_asset_ids=[],
            source_record_id="asset-building-main",
            tags=["building", "foundation"],
            metadata={"stage": "assets-r1"},
            limitations=base_limitations,
        ),
        _asset(
            asset_id="floor-l1",
            asset_code="FLOOR-L1",
            asset_name="Level 1",
            asset_type="floor",
            asset_category="location",
            lifecycle_status="active",
            operational_status="online",
            site_id="site-main",
            site_name="Main Site",
            building_id="building-main",
            building_name="Main Building",
            floor_id="floor-l1",
            floor_name="Level 1",
            zone_id="",
            zone_name="",
            system_id="",
            system_name="",
            parent_asset_id="building-main",
            children_asset_ids=["zone-plant-room"],
            related_asset_ids=[],
            source_record_id="asset-floor-l1",
            tags=["floor", "foundation"],
            metadata={"stage": "assets-r1"},
            limitations=base_limitations,
        ),
        _asset(
            asset_id="zone-plant-room",
            asset_code="ZONE-PLANT",
            asset_name="Plant Room",
            asset_type="zone",
            asset_category="location",
            lifecycle_status="active",
            operational_status="online",
            site_id="site-main",
            site_name="Main Site",
            building_id="building-main",
            building_name="Main Building",
            floor_id="floor-l1",
            floor_name="Level 1",
            zone_id="zone-plant-room",
            zone_name="Plant Room",
            system_id="",
            system_name="",
            parent_asset_id="floor-l1",
            children_asset_ids=["system-mechanical", "system-electrical"],
            related_asset_ids=[],
            source_record_id="asset-zone-plant-room",
            tags=["zone", "foundation"],
            metadata={"stage": "assets-r1"},
            limitations=base_limitations,
        ),
        _asset(
            asset_id="system-mechanical",
            asset_code="SYS-MECH-01",
            asset_name="Mechanical System",
            asset_type="system",
            asset_category="mechanical",
            lifecycle_status="active",
            operational_status="online",
            site_id="site-main",
            site_name="Main Site",
            building_id="building-main",
            building_name="Main Building",
            floor_id="floor-l1",
            floor_name="Level 1",
            zone_id="zone-plant-room",
            zone_name="Plant Room",
            system_id="system-mechanical",
            system_name="Mechanical System",
            parent_asset_id="zone-plant-room",
            children_asset_ids=["device-chiller-01"],
            related_asset_ids=["system-electrical"],
            source_record_id="asset-system-mechanical",
            tags=["system", "mechanical"],
            metadata={"stage": "assets-r1"},
            limitations=base_limitations,
        ),
        _asset(
            asset_id="device-chiller-01",
            asset_code="DEV-CHILLER-01",
            asset_name="Chiller 01",
            asset_type="equipment",
            asset_category="hvac",
            lifecycle_status="active",
            operational_status="online",
            site_id="site-main",
            site_name="Main Site",
            building_id="building-main",
            building_name="Main Building",
            floor_id="floor-l1",
            floor_name="Level 1",
            zone_id="zone-plant-room",
            zone_name="Plant Room",
            system_id="system-mechanical",
            system_name="Mechanical System",
            parent_asset_id="system-mechanical",
            children_asset_ids=["point-chiller-status"],
            related_asset_ids=["device-panel-01"],
            source_record_id="asset-device-chiller-01",
            tags=["equipment", "hvac"],
            metadata={"stage": "assets-r1"},
            limitations=base_limitations,
        ),
        _asset(
            asset_id="point-chiller-status",
            asset_code="POINT-CHILLER-STATUS",
            asset_name="Chiller Running Status",
            asset_type="point",
            asset_category="telemetry-point",
            lifecycle_status="active",
            operational_status="online",
            site_id="site-main",
            site_name="Main Site",
            building_id="building-main",
            building_name="Main Building",
            floor_id="floor-l1",
            floor_name="Level 1",
            zone_id="zone-plant-room",
            zone_name="Plant Room",
            system_id="system-mechanical",
            system_name="Mechanical System",
            parent_asset_id="device-chiller-01",
            children_asset_ids=[],
            related_asset_ids=[],
            source_record_id="asset-point-chiller-status",
            tags=["point", "telemetry"],
            metadata={"stage": "assets-r1"},
            limitations=base_limitations,
        ),
        _asset(
            asset_id="system-electrical",
            asset_code="SYS-ELEC-01",
            asset_name="Electrical System",
            asset_type="system",
            asset_category="electrical",
            lifecycle_status="active",
            operational_status="online",
            site_id="site-main",
            site_name="Main Site",
            building_id="building-main",
            building_name="Main Building",
            floor_id="floor-l1",
            floor_name="Level 1",
            zone_id="zone-plant-room",
            zone_name="Plant Room",
            system_id="system-electrical",
            system_name="Electrical System",
            parent_asset_id="zone-plant-room",
            children_asset_ids=["device-panel-01"],
            related_asset_ids=["system-mechanical"],
            source_record_id="asset-system-electrical",
            tags=["system", "electrical"],
            metadata={"stage": "assets-r1"},
            limitations=base_limitations,
        ),
        _asset(
            asset_id="device-panel-01",
            asset_code="DEV-PANEL-01",
            asset_name="Panel 01",
            asset_type="equipment",
            asset_category="electrical-panel",
            lifecycle_status="active",
            operational_status="online",
            site_id="site-main",
            site_name="Main Site",
            building_id="building-main",
            building_name="Main Building",
            floor_id="floor-l1",
            floor_name="Level 1",
            zone_id="zone-plant-room",
            zone_name="Plant Room",
            system_id="system-electrical",
            system_name="Electrical System",
            parent_asset_id="system-electrical",
            children_asset_ids=[],
            related_asset_ids=["device-chiller-01"],
            source_record_id="asset-device-panel-01",
            tags=["equipment", "electrical"],
            metadata={"stage": "assets-r1"},
            limitations=base_limitations,
        ),
    ]


def _asset_type_count(items: List[Dict[str, Any]], asset_type: str) -> int:
    return len([item for item in items if str(item.get("assetType", "")) == asset_type])


def _normalized_assets() -> List[Dict[str, Any]]:
    return [deepcopy(row) for row in _base_assets()]


def list_assets(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    values = filters or {}
    asset_type = str(values.get("assetType", "")).strip()
    asset_category = str(values.get("assetCategory", "")).strip()
    lifecycle_status = str(values.get("lifecycleStatus", "")).strip()
    operational_status = str(values.get("operationalStatus", "")).strip()
    site_id = str(values.get("siteId", "")).strip()
    system_id = str(values.get("systemId", "")).strip()

    def _match(item: Dict[str, Any]) -> bool:
        if asset_type and str(item.get("assetType", "")) != asset_type:
            return False
        if asset_category and str(item.get("assetCategory", "")) != asset_category:
            return False
        if lifecycle_status and str(item.get("lifecycleStatus", "")) != lifecycle_status:
            return False
        if operational_status and str(item.get("operationalStatus", "")) != operational_status:
            return False
        if site_id and str(item.get("siteId", "")) != site_id:
            return False
        if system_id and str(item.get("systemId", "")) != system_id:
            return False
        return True

    return [item for item in _normalized_assets() if _match(item)]


def get_asset(asset_id: str) -> Optional[Dict[str, Any]]:
    target = str(asset_id or "").strip()
    if not target:
        return None
    for item in _normalized_assets():
        if str(item.get("assetId")) == target:
            return item
    return None


def get_assets_summary() -> Dict[str, Any]:
    items = _normalized_assets()
    asset_types = sorted({str(item.get("assetType", "")) for item in items if str(item.get("assetType", "")).strip()})
    asset_categories = sorted(
        {str(item.get("assetCategory", "")) for item in items if str(item.get("assetCategory", "")).strip()}
    )
    limitations = sorted(
        {
            text
            for item in items
            for text in item.get("limitations", [])
            if isinstance(text, str) and text.strip()
        }
    )
    active_assets = len([item for item in items if str(item.get("operationalStatus", "")) == "online"])
    mock_assets = len([item for item in items if bool(item.get("mockData"))])
    return {
        "totalAssets": len(items),
        "siteCount": _asset_type_count(items, "site"),
        "buildingCount": _asset_type_count(items, "building"),
        "floorCount": _asset_type_count(items, "floor"),
        "zoneCount": _asset_type_count(items, "zone"),
        "systemCount": _asset_type_count(items, "system"),
        "equipmentCount": _asset_type_count(items, "equipment"),
        "pointCount": _asset_type_count(items, "point"),
        "activeAssets": active_assets,
        "mockAssets": mock_assets,
        "runtimeLinkedAssets": 0,
        "certifiedAssets": 0,
        "iec62443CertifiedAssets": 0,
        "assetTypes": asset_types,
        "assetCategories": asset_categories,
        "limitations": limitations,
    }


def get_topology_relationships() -> Dict[str, Any]:
    items = _normalized_assets()
    nodes = [
        {
            "nodeId": f"node-{item['assetId']}",
            "assetId": item["assetId"],
            "label": item["assetName"],
            "nodeType": item["assetType"],
            "assetCategory": item["assetCategory"],
            "status": item["operationalStatus"],
            "runtimeLinked": False,
        }
        for item in items
    ]

    edges: List[Dict[str, Any]] = []
    edge_index = set()

    for item in items:
        parent_id = str(item.get("parentAssetId", "")).strip()
        if parent_id:
            edges.append(
                {
                    "edgeId": f"edge-{parent_id}-{item['assetId']}",
                    "from": f"node-{parent_id}",
                    "to": f"node-{item['assetId']}",
                    "relationship": "contains",
                    "runtimeLinked": False,
                }
            )

        for related_id in item.get("relatedAssetIds", []):
            pair = tuple(sorted([item["assetId"], related_id]))
            if pair in edge_index:
                continue
            edge_index.add(pair)
            edges.append(
                {
                    "edgeId": f"edge-related-{pair[0]}-{pair[1]}",
                    "from": f"node-{pair[0]}",
                    "to": f"node-{pair[1]}",
                    "relationship": "related-to",
                    "runtimeLinked": False,
                }
            )

    return {
        "topologyMode": "local-skeleton-topology",
        "nodes": nodes,
        "edges": edges,
        "runtimeLinked": False,
        "certified": False,
        "iec62443Certified": False,
        "notes": "Local skeleton topology; no runtime device discovery or EDGE/LINK integration.",
    }


def get_asset_health() -> Dict[str, Any]:
    summary = get_assets_summary()
    return {
        "status": "ok",
        "provider": "local-assets-provider",
        "runtimeMode": "skeleton",
        "sourceSemantics": "ibms-neutral",
        "totalAssets": summary["totalAssets"],
        "runtimeLinkedAssets": summary["runtimeLinkedAssets"],
        "certified": False,
        "iec62443Certified": False,
    }

