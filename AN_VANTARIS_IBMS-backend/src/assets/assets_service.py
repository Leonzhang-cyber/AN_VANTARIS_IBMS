"""Assets & Topology service (read-only runtime skeleton)."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from src.assets.assets_provider import (
    get_asset,
    get_asset_health,
    get_assets_summary,
    get_topology_relationships,
    list_assets,
)


class AssetsTopologyService:
    MODULE_ID = "assets-topology"
    MODULE_NAME = "Assets & Topology"
    RUNTIME_MODE = "skeleton"
    PROVIDER = "local-assets-provider"
    SOURCE_SEMANTICS = "ibms-neutral"

    def get_assets_health(self) -> Dict[str, Any]:
        provider_health = get_asset_health()
        return {
            "status": "ok",
            "moduleId": self.MODULE_ID,
            "moduleName": self.MODULE_NAME,
            "runtimeMode": self.RUNTIME_MODE,
            "provider": self.PROVIDER,
            "sourceSemantics": self.SOURCE_SEMANTICS,
            "readOnly": True,
            "controlActionsEnabled": False,
            "discoveryEnabled": False,
            "edgeRuntimeIntegrated": False,
            "linkRuntimeIntegrated": False,
            "dbPersistenceIntegrated": False,
            "totalAssets": provider_health.get("totalAssets", 0),
            "runtimeLinkedAssets": provider_health.get("runtimeLinkedAssets", 0),
            "certified": False,
            "iec62443Certified": False,
        }

    def list_assets(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        active_filters = {
            "assetType": str((filters or {}).get("assetType", "")).strip(),
            "assetCategory": str((filters or {}).get("assetCategory", "")).strip(),
            "lifecycleStatus": str((filters or {}).get("lifecycleStatus", "")).strip(),
            "operationalStatus": str((filters or {}).get("operationalStatus", "")).strip(),
            "siteId": str((filters or {}).get("siteId", "")).strip(),
            "systemId": str((filters or {}).get("systemId", "")).strip(),
        }
        items = list_assets(active_filters)
        return {
            "items": items,
            "total": len(items),
            "filters": active_filters,
            "summary": self.get_assets_summary(),
            "provider": self.PROVIDER,
            "runtimeMode": self.RUNTIME_MODE,
            "sourceSemantics": self.SOURCE_SEMANTICS,
            "mockData": True,
            "readOnly": True,
            "discoveryEnabled": False,
            "certified": False,
            "iec62443Certified": False,
        }

    def get_asset_detail(self, asset_id: str) -> Optional[Dict[str, Any]]:
        return get_asset(asset_id)

    def get_assets_summary(self) -> Dict[str, Any]:
        summary = get_assets_summary()
        summary["limitations"] = summary.get("limitations", []) + [
            "Assets R1 uses local skeleton topology.",
            "Runtime discovery, EDGE/LINK integration and DB persistence are not integrated.",
        ]
        return summary

    def get_topology(self) -> Dict[str, Any]:
        topology = get_topology_relationships()
        topology["summary"] = {
            "nodeCount": len(topology.get("nodes", [])),
            "edgeCount": len(topology.get("edges", [])),
            "runtimeLinked": False,
        }
        return topology

    def get_asset_relationships(
        self, asset_id: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[int, str]]]:
        asset = get_asset(asset_id)
        if not asset:
            return None, (404, "assetId not found")

        all_assets = list_assets()
        parent_id = str(asset.get("parentAssetId", "")).strip()
        parent = get_asset(parent_id) if parent_id else None
        children = [item for item in all_assets if str(item.get("parentAssetId", "")) == asset["assetId"]]
        related_ids = [str(item) for item in asset.get("relatedAssetIds", []) if str(item).strip()]
        related = [item for item in all_assets if str(item.get("assetId", "")) in related_ids]

        edges = []
        if parent:
            edges.append(
                {
                    "edgeId": f"edge-parent-{parent['assetId']}-{asset['assetId']}",
                    "from": parent["assetId"],
                    "to": asset["assetId"],
                    "relationship": "contains",
                    "runtimeLinked": False,
                }
            )
        edges.extend(
            [
                {
                    "edgeId": f"edge-child-{asset['assetId']}-{child['assetId']}",
                    "from": asset["assetId"],
                    "to": child["assetId"],
                    "relationship": "contains",
                    "runtimeLinked": False,
                }
                for child in children
            ]
        )
        edges.extend(
            [
                {
                    "edgeId": f"edge-related-{asset['assetId']}-{item['assetId']}",
                    "from": asset["assetId"],
                    "to": item["assetId"],
                    "relationship": "related-to",
                    "runtimeLinked": False,
                }
                for item in related
            ]
        )

        return {
            "assetId": asset["assetId"],
            "relationshipMode": "local-skeleton-relationships",
            "parent": parent,
            "children": children,
            "related": related,
            "edges": edges,
            "runtimeLinked": False,
            "certified": False,
            "iec62443Certified": False,
        }, None

