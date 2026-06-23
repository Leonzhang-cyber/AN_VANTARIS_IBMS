"""Unified Asset Context read-only provider.

This module builds a local projection across asset, maintenance, event,
evidence, report, delivery, and diagnostics sources. It is intentionally
read-only and does not call runtime, command, persistence, or control paths.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional


SCOPE = "ASSET_CONTEXT_GA_R1"
VISUAL_STYLE = "VANTARIS_LIGHT_OPERATIONS_CONSOLE"
GRAPH_MODE = "local-readonly-asset-context-projection"
PASS_MARKER = "ONE_ASSET_CONTEXT_GA_R1_UNIFIED_LINKAGE_PASS"

READ_ONLY_FLAGS: Dict[str, Any] = {
    "readOnly": True,
    "runtimeEnabled": False,
    "dbWriteEnabled": False,
    "assetGraphWriteEnabled": False,
    "edgeCommandExecution": False,
    "linkCommandExecution": False,
    "deviceControlEnabled": False,
    "productionActivation": False,
    "visualStyle": VISUAL_STYLE,
    "scope": SCOPE,
}

GUARDRAILS = [
    "Read-only aggregation only",
    "No DB write",
    "No Asset Graph canonical write",
    "No DB migration",
    "No auth/login/JWT/RBAC mutation",
    "No runtime activation",
    "No device control",
    "No EDGE command execution",
    "No LINK command execution",
    "No SSH, deployment, or install action",
    "No ONE Adapter introduction",
    "No PDF/Excel/ZIP/report artifact generation",
]

LINKED_OBJECT_TYPES = [
    "asset",
    "system",
    "device",
    "event",
    "workOrder",
    "maintenanceTask",
    "uhmiPanel",
    "ucdeEvidence",
    "report",
    "customerDelivery",
    "foundationDiagnostics",
]


def common() -> Dict[str, Any]:
    return {
        **READ_ONLY_FLAGS,
        "moduleId": "asset-context",
        "moduleName": "Asset Context",
        "provider": "local-readonly-asset-context-provider",
        "linkageMode": GRAPH_MODE,
        "passMarker": PASS_MARKER,
    }


def _safe_call(name: str, fn: Callable[[], Any], limitations: List[str], statuses: Dict[str, Any]) -> Any:
    try:
        value = fn()
        statuses[name] = {"integrationStatus": "available", "readOnly": True}
        return value
    except Exception as exc:  # pragma: no cover - defensive integration guard
        message = f"{name} unavailable: {exc.__class__.__name__}"
        statuses[name] = {"integrationStatus": "unavailable", "readOnly": True, "reason": message}
        limitations.append(message)
        return None


def _items(payload: Any, *keys: str) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if not isinstance(payload, dict):
        return []
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    return []


def _contains(row: Dict[str, Any], asset_id: str, *keys: str) -> bool:
    for key in keys:
        value = row.get(key)
        if str(value) == asset_id:
            return True
        if isinstance(value, list) and asset_id in {str(item) for item in value}:
            return True
    return False


def _text_match(row: Dict[str, Any], *needles: str) -> bool:
    haystack = " ".join(str(value) for value in row.values()).lower()
    return any(needle and needle.lower() in haystack for needle in needles)


def _collect_sources() -> Dict[str, Any]:
    limitations: List[str] = []
    statuses: Dict[str, Any] = {}

    def assets() -> Dict[str, Any]:
        from src.assets.assets_service import AssetsTopologyService

        service = AssetsTopologyService()
        return {
            "health": service.get_assets_health(),
            "summary": service.get_assets_summary(),
            "assets": service.list_assets({}),
            "topology": service.get_topology(),
        }

    def umms() -> Dict[str, Any]:
        from src.umms.umms_service import UmmsMaintenanceService

        service = UmmsMaintenanceService()
        return {
            "health": service.get_umms_health(),
            "workOrders": service.list_work_orders({}),
            "summary": service.get_maintenance_summary(),
            "workspace": service.get_ga_r2_workspace(),
        }

    def ucde() -> Dict[str, Any]:
        from src.ucde.evidence_service import UcdeEvidenceService

        service = UcdeEvidenceService()
        return {
            "health": service.get_ucde_health(),
            "evidence": service.list_evidence({}),
            "summary": service.get_evidence_summary(),
        }

    def uhmi() -> Dict[str, Any]:
        from src.uhmi.uhmi_provider import get_devices, get_events, get_evidence, get_panels, get_systems

        return {
            "systems": get_systems(),
            "devices": get_devices(),
            "events": get_events(),
            "evidence": get_evidence(),
            "panels": get_panels(),
        }

    def reports() -> Dict[str, Any]:
        from src.reports.reports_service import ReportsService

        service = ReportsService()
        return service.get_ga_r13_workspace()

    def delivery() -> Dict[str, Any]:
        from src.customer_delivery.readonly_preview_provider import customer_delivery_preview

        return customer_delivery_preview()

    def foundation() -> Dict[str, Any]:
        from src.foundation_diagnostics.service import FoundationDiagnosticsService

        return FoundationDiagnosticsService().workspace()

    return {
        "limitations": limitations,
        "providerStatuses": statuses,
        "assets": _safe_call("assets", assets, limitations, statuses) or {},
        "umms": _safe_call("umms", umms, limitations, statuses) or {},
        "ucde": _safe_call("ucde", ucde, limitations, statuses) or {},
        "uhmi": _safe_call("uhmi", uhmi, limitations, statuses) or {},
        "reports": _safe_call("reports", reports, limitations, statuses) or {},
        "customerDelivery": _safe_call("customerDelivery", delivery, limitations, statuses) or {},
        "foundationDiagnostics": _safe_call("foundationDiagnostics", foundation, limitations, statuses) or {},
    }


def _source_rows(sources: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    assets_payload = sources.get("assets", {})
    umms_payload = sources.get("umms", {})
    ucde_payload = sources.get("ucde", {})
    uhmi_payload = sources.get("uhmi", {})
    reports_payload = sources.get("reports", {})
    delivery_payload = sources.get("customerDelivery", {})
    foundation_payload = sources.get("foundationDiagnostics", {})
    return {
        "assets": _items(assets_payload.get("assets"), "items"),
        "workOrders": _items(umms_payload.get("workOrders"), "workOrders", "items"),
        "maintenanceTasks": _items(umms_payload.get("workspace"), "maintenanceTasks", "tasks"),
        "events": _items(uhmi_payload.get("events"), "events", "items"),
        "evidence": _items(ucde_payload.get("evidence"), "items") + _items(uhmi_payload.get("evidence"), "evidence", "items"),
        "panels": _items(uhmi_payload.get("panels"), "panels", "mimicPanels", "items"),
        "reports": _items(reports_payload, "reportLibrary", "reports"),
        "delivery": _items(delivery_payload, "handoffItems", "readinessMatrix", "customerHandoffChecklist"),
        "diagnostics": _items(foundation_payload, "packageReadiness", "healthcheckPreview", "diagnostics"),
        "systems": _items(uhmi_payload.get("systems"), "systems", "items"),
        "devices": _items(uhmi_payload.get("devices"), "devices", "items"),
    }


def _linked_rows(asset: Dict[str, Any], rows: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    asset_id = str(asset.get("assetId", ""))
    system_id = str(asset.get("systemId", ""))
    system_name = str(asset.get("systemName", ""))
    asset_name = str(asset.get("assetName", ""))
    asset_type = str(asset.get("assetType", ""))
    return {
        "linkedWorkOrders": [
            row for row in rows["workOrders"] if _contains(row, asset_id, "assetId", "linkedAssetId", "targetAssetId") or _text_match(row, asset_name, system_id, system_name)
        ][:4],
        "linkedEvents": [
            row for row in rows["events"] if _contains(row, asset_id, "assetId", "linkedAssetId") or _text_match(row, asset_name, system_name)
        ][:4],
        "linkedEvidence": [
            row for row in rows["evidence"] if _contains(row, asset_id, "assetId", "linkedAssetId", "sourceRecordId") or _text_match(row, asset_id, asset_name, system_name)
        ][:4],
        "linkedUhmiPanels": [
            row for row in rows["panels"] if _text_match(row, asset_name, system_name, asset_type)
        ][:4],
        "linkedReports": [
            row for row in rows["reports"] if _text_match(row, asset_name, system_name, asset_type, "Asset", "Maintenance", "Evidence")
        ][:5],
        "linkedDeliveryItems": [
            row for row in rows["delivery"] if _text_match(row, asset_name, system_name, "asset", "handoff", "readiness")
        ][:4],
        "linkedDiagnostics": [
            row for row in rows["diagnostics"] if _text_match(row, asset_name, system_name, "asset", "foundation", "diagnostic")
        ][:4],
    }


def _context_asset(asset: Dict[str, Any], rows: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    links = _linked_rows(asset, rows)
    summary = {
        "workOrderCount": len(links["linkedWorkOrders"]),
        "eventCount": len(links["linkedEvents"]),
        "evidenceCount": len(links["linkedEvidence"]),
        "uhmiPanelCount": len(links["linkedUhmiPanels"]),
        "reportCount": len(links["linkedReports"]),
        "deliveryItemCount": len(links["linkedDeliveryItems"]),
        "diagnosticCount": len(links["linkedDiagnostics"]),
    }
    return {
        "assetId": str(asset.get("assetId", "")),
        "assetName": str(asset.get("assetName", "")),
        "assetType": str(asset.get("assetType", "")),
        "systemId": str(asset.get("systemId", "")),
        "systemName": str(asset.get("systemName", "")),
        "siteId": str(asset.get("siteId", "")),
        "zoneId": str(asset.get("zoneId", "")),
        "operationalStatus": str(asset.get("operationalStatus", "")),
        **links,
        "relationshipSummary": summary,
        **READ_ONLY_FLAGS,
    }


def list_asset_contexts() -> Dict[str, Any]:
    sources = _collect_sources()
    rows = _source_rows(sources)
    items = [_context_asset(asset, rows) for asset in rows["assets"]]
    return {
        **common(),
        "items": items,
        "total": len(items),
        "limitations": sources["limitations"],
        "providerStatuses": sources["providerStatuses"],
    }


def get_asset_context(asset_id: str) -> Optional[Dict[str, Any]]:
    sources = _collect_sources()
    rows = _source_rows(sources)
    asset = next((row for row in rows["assets"] if str(row.get("assetId")) == asset_id), None)
    if not asset:
        return None
    context = _context_asset(asset, rows)
    relationships = {
        "asset": context,
        "systems": [row for row in rows["systems"] if _text_match(row, context["systemName"], context["systemId"])],
        "devices": [row for row in rows["devices"] if _text_match(row, context["assetName"], context["systemName"])],
    }
    return {
        **common(),
        "asset": context,
        "assetRelationships": relationships,
        "workOrders": context["linkedWorkOrders"],
        "maintenanceTasks": [
            row for row in rows["maintenanceTasks"] if _contains(row, asset_id, "assetId", "linkedAssetId") or _text_match(row, context["assetName"], context["systemName"])
        ],
        "events": context["linkedEvents"],
        "evidence": context["linkedEvidence"],
        "uhmiPanels": context["linkedUhmiPanels"],
        "reports": context["linkedReports"],
        "customerDelivery": context["linkedDeliveryItems"],
        "foundationDiagnostics": context["linkedDiagnostics"],
        "traceabilityPath": [
            "Asset",
            "System",
            "Device",
            "Event",
            "Work Order",
            "UCDE Evidence",
            "Reports",
            "Customer Delivery",
            "Foundation Diagnostics",
        ],
        "limitations": sources["limitations"],
        "providerStatuses": sources["providerStatuses"],
        "guardrails": GUARDRAILS,
    }


def get_asset_links(asset_id: str) -> Optional[Dict[str, Any]]:
    detail = get_asset_context(asset_id)
    if not detail:
        return None
    return {
        **common(),
        "assetId": asset_id,
        "assetRelationships": detail["assetRelationships"],
        "workOrders": detail["workOrders"],
        "events": detail["events"],
        "evidence": detail["evidence"],
        "reports": detail["reports"],
        "uhmiPanels": detail["uhmiPanels"],
        "customerDelivery": detail["customerDelivery"],
        "foundationDiagnostics": detail["foundationDiagnostics"],
        "guardrails": GUARDRAILS,
    }


def get_summary() -> Dict[str, Any]:
    sources = _collect_sources()
    rows = _source_rows(sources)
    return {
        **common(),
        "totalAssets": len(rows["assets"]),
        "totalSystems": len(rows["systems"]) or len({str(row.get("systemId", "")) for row in rows["assets"] if row.get("systemId")}),
        "totalDevices": len(rows["devices"]),
        "totalEvents": len(rows["events"]),
        "totalWorkOrders": len(rows["workOrders"]),
        "totalEvidence": len(rows["evidence"]),
        "totalReports": len(rows["reports"]),
        "totalPanels": len(rows["panels"]),
        "linkedObjectTypes": LINKED_OBJECT_TYPES,
        "guardrails": GUARDRAILS,
        "limitations": sources["limitations"],
        "providerStatuses": sources["providerStatuses"],
    }


def get_health() -> Dict[str, Any]:
    summary = get_summary()
    unavailable = [name for name, status in summary["providerStatuses"].items() if status.get("integrationStatus") == "unavailable"]
    return {
        **common(),
        "status": "degraded" if unavailable else "ok",
        "providerStatuses": summary["providerStatuses"],
        "limitations": summary["limitations"],
        "unavailableProviders": unavailable,
    }


def _node(node_id: str, label: str, node_type: str, source: str) -> Dict[str, Any]:
    return {"id": node_id, "label": label, "type": node_type, "source": source, **READ_ONLY_FLAGS}


def _edge(source: str, target: str, relationship: str) -> Dict[str, Any]:
    return {"id": f"{relationship}-{source}-{target}", "source": source, "target": target, "relationship": relationship, **READ_ONLY_FLAGS}


def get_graph() -> Dict[str, Any]:
    asset_payload = list_asset_contexts()
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    seen = set()

    def add_node(node: Dict[str, Any]) -> None:
        if node["id"] not in seen:
            seen.add(node["id"])
            nodes.append(node)

    for asset in asset_payload["items"]:
        asset_id = asset["assetId"]
        system_id = asset.get("systemId") or f"system-{asset.get('systemName')}"
        add_node(_node(asset_id, asset["assetName"], "asset", "Assets & Topology"))
        add_node(_node(system_id, asset.get("systemName") or "System", "system", "UHMI / Assets"))
        edges.append(_edge(asset_id, system_id, "belongs-to"))
        if asset.get("zoneId"):
            zone_id = str(asset["zoneId"])
            add_node(_node(zone_id, zone_id, "device", "Assets & Topology"))
            edges.append(_edge(asset_id, zone_id, "located-in"))
        for collection, node_type, relationship, label_key, source in (
            ("linkedWorkOrders", "workOrder", "has-work-order", "workOrderName", "UMMS"),
            ("linkedEvents", "event", "has-event", "title", "UHMI"),
            ("linkedEvidence", "evidence", "has-evidence", "evidenceName", "UCDE"),
            ("linkedUhmiPanels", "panel", "shown-in-panel", "panelName", "UHMI"),
            ("linkedReports", "report", "included-in-report", "reportName", "Reports & Analytics"),
            ("linkedDeliveryItems", "delivery", "referenced-by-delivery", "itemName", "Customer Delivery"),
            ("linkedDiagnostics", "diagnostics", "checked-by-diagnostics", "packageName", "Foundation Diagnostics"),
        ):
            for row in asset.get(collection, []):
                node_id = str(row.get(f"{node_type}Id") or row.get("reportId") or row.get("checkId") or row.get("packageId") or row.get("id") or f"{node_type}-{len(nodes)}")
                add_node(_node(node_id, str(row.get(label_key) or row.get("name") or node_id), node_type, source))
                edges.append(_edge(asset_id, node_id, relationship))
    return {
        **common(),
        "graphMode": GRAPH_MODE,
        "nodes": nodes,
        "edges": edges,
        "summary": {"nodeCount": len(nodes), "edgeCount": len(edges)},
        "guardrails": GUARDRAILS,
        "limitations": asset_payload["limitations"],
    }


def get_guardrails() -> Dict[str, Any]:
    return {**common(), "guardrails": GUARDRAILS}

