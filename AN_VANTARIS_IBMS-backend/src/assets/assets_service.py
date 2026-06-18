"""Assets & Topology service (read-only runtime skeleton)."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from src.assets.assets_provider import (
    get_asset,
    get_asset_health,
    get_asset_impact_skeleton,
    get_asset_topology_lineage,
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
            "Assets R2 uses local skeleton topology relationship details.",
            "Topology relationships are local skeleton references. Runtime discovery, telemetry correlation and EDGE/LINK integration are not integrated.",
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
        by_id = {str(item.get("assetId", "")): item for item in all_assets}
        children_map: Dict[str, list] = {}
        for row in all_assets:
            parent = str(row.get("parentAssetId", "")).strip()
            if parent:
                children_map.setdefault(parent, []).append(row)

        parent_id = str(asset.get("parentAssetId", "")).strip()
        parent = by_id.get(parent_id) if parent_id else None
        children = list(children_map.get(asset["assetId"], []))
        related_ids = [str(item) for item in asset.get("relatedAssetIds", []) if str(item).strip()]
        related = [by_id[item_id] for item_id in related_ids if item_id in by_id]

        upstream = []
        current_parent_id = parent_id
        visited = set()
        while current_parent_id and current_parent_id not in visited:
            visited.add(current_parent_id)
            parent_row = by_id.get(current_parent_id)
            if not parent_row:
                break
            upstream.append(parent_row)
            current_parent_id = str(parent_row.get("parentAssetId", "")).strip()

        queue = list(children)
        downstream = []
        downstream_seen = set()
        while queue:
            current = queue.pop(0)
            current_id = str(current.get("assetId", ""))
            if current_id in downstream_seen:
                continue
            downstream_seen.add(current_id)
            downstream.append(current)
            queue.extend(children_map.get(current_id, []))

        points = [row for row in downstream if str(row.get("assetType", "")) == "point"]
        equipment = [row for row in downstream if str(row.get("assetType", "")) == "equipment"]
        systems = [row for row in downstream if str(row.get("assetType", "")) == "system"]

        hierarchy_path = asset.get("hierarchyPath", {})
        root_to_asset = hierarchy_path.get("levels", []) if isinstance(hierarchy_path, dict) else []
        root_asset_id = str(root_to_asset[0].get("assetId", "")) if root_to_asset else ""

        def _asset_to_leaf_paths(start_id: str) -> list:
            paths = []

            def _walk(current_id: str, acc: list, walk_seen: set) -> None:
                if current_id in walk_seen:
                    return
                walk_seen.add(current_id)
                current_node = by_id.get(current_id)
                if not current_node:
                    return
                next_acc = acc + [
                    {
                        "assetId": current_node.get("assetId", ""),
                        "assetName": current_node.get("assetName", ""),
                        "assetType": current_node.get("assetType", ""),
                    }
                ]
                current_children = children_map.get(current_id, [])
                if not current_children:
                    paths.append(next_acc)
                    return
                for child in current_children:
                    _walk(str(child.get("assetId", "")), next_acc, set(walk_seen))

            _walk(start_id, [], set())
            return paths

        asset_to_leaves = _asset_to_leaf_paths(asset["assetId"])
        relationship_complete = bool(hierarchy_path.get("complete", True)) if isinstance(hierarchy_path, dict) else False

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

        edges.extend(
            [
                {
                    "edgeId": f"edge-upstream-{row['assetId']}-{asset['assetId']}",
                    "from": row["assetId"],
                    "to": asset["assetId"],
                    "relationship": "belongs-to",
                    "runtimeLinked": False,
                }
                for row in upstream
            ]
        )
        edges.extend(
            [
                {
                    "edgeId": f"edge-downstream-{asset['assetId']}-{row['assetId']}",
                    "from": asset["assetId"],
                    "to": row["assetId"],
                    "relationship": "contains",
                    "runtimeLinked": False,
                }
                for row in downstream
            ]
        )

        return {
            "assetId": asset["assetId"],
            "relationshipMode": "local-skeleton-relationships",
            "parent": parent,
            "children": children,
            "related": related,
            "relationshipSummary": {
                "parentCount": 1 if parent else 0,
                "childCount": len(children),
                "relatedCount": len(related),
                "upstreamCount": len(upstream),
                "downstreamCount": len(downstream),
                "pointCount": len(points),
                "equipmentCount": len(equipment),
                "systemCount": len(systems),
                "runtimeLinkedRelationships": 0,
            },
            "relationshipGroups": {
                "parent": [parent] if parent else [],
                "children": children,
                "related": related,
                "upstream": upstream,
                "downstream": downstream,
                "points": points,
                "equipment": equipment,
                "systems": systems,
            },
            "relationshipPath": {
                "pathMode": "local-skeleton-relationship-path",
                "assetId": asset["assetId"],
                "rootAssetId": root_asset_id,
                "rootToAsset": root_to_asset,
                "assetToLeaves": asset_to_leaves,
                "complete": relationship_complete,
                "runtimeLinked": False,
            },
            "edges": edges,
            "runtimeLinked": False,
            "certified": False,
            "iec62443Certified": False,
        }, None

    def get_asset_topology_lineage(
        self, asset_id: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[int, str]]]:
        lineage = get_asset_topology_lineage(asset_id)
        if not lineage:
            return None, (404, "assetId not found")
        return lineage, None

    def get_asset_impact(
        self, asset_id: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[int, str]]]:
        impact = get_asset_impact_skeleton(asset_id)
        if not impact:
            return None, (404, "assetId not found")
        return impact, None

