"""Read-only fault and work-order overlay projections for airport HMI maps."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.api.asset_import_ga.asset_import_service import readonly_flags
from src.api.asset_import_ga.asset_import_store import repo_root


EVENT_SAMPLE_PATH = "AN_VANTARIS_ONE/poc-data/airport-t3-ground-floor/event_alarm_sample.csv"
WORK_ORDER_SAMPLE_PATH = "AN_VANTARIS_ONE/poc-data/airport-t3-ground-floor/work_order_sample.csv"
HMI_PAYLOAD_PATH = "AN_VANTARIS_ONE/poc-data/airport-t3-ground-floor/l3_data_asset_map_demo_payload.json"
QUALITY_REPORT_PATH = "AN_VANTARIS_ONE/reports/asset-import-ga/airport_asset_import_quality_report.json"
OVERLAY_MODE = "readonly_projection"
SOURCE_MODE = "controlled_sample_projection"
BLOCKED_STATUS = "blocked_by_data_quality"
PENDING_CLEARANCE = "pending_asset_import_clearance"


def _read_csv(relative_path: str) -> list[dict[str, str]]:
    path = repo_root() / relative_path
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _read_json(relative_path: str) -> dict[str, Any]:
    path = repo_root() / relative_path
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _split_required_items(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def _route_parts(route_hint: str) -> tuple[str, str]:
    parts = [part.strip() for part in route_hint.split("->", 1)]
    if len(parts) == 2:
        return parts[0], parts[1]
    return "Map Context", route_hint.strip() or "Pending destination"


class FaultWorkOrderOverlayService:
    def __init__(self) -> None:
        self.events = _read_csv(EVENT_SAMPLE_PATH)
        self.work_orders = _read_csv(WORK_ORDER_SAMPLE_PATH)
        self.hmi_payload = _read_json(HMI_PAYLOAD_PATH)
        self.quality_report = _read_json(QUALITY_REPORT_PATH)

    def _asset_quality(self) -> dict[str, Any]:
        summary = self.quality_report.get("summary", {})
        readiness = str(summary.get("readiness", "UNKNOWN"))
        return {
            "asset_import_readiness": readiness,
            "asset_overlay_status": BLOCKED_STATUS if readiness == "HOLD_BLOCKED" else "pending_review",
            "confirm_enabled": bool(self.quality_report.get("alert", {}).get("confirm_enabled", readiness != "HOLD_BLOCKED")),
            "blocked_by_asset_quality": readiness == "HOLD_BLOCKED",
        }

    def _base(self, map_id: str) -> dict[str, Any]:
        quality = self._asset_quality()
        return {
            **readonly_flags(),
            "map_id": map_id,
            "overlay_mode": OVERLAY_MODE,
            "source_mode": SOURCE_MODE,
            "asset_import_readiness": quality["asset_import_readiness"],
            "asset_overlay_status": quality["asset_overlay_status"],
            "formal_event_registry_write": False,
            "formal_work_order_write": False,
            "formal_asset_registry_write": False,
            "confirm_enabled": quality["confirm_enabled"],
        }

    def _space_by_id(self) -> dict[str, dict[str, Any]]:
        spaces = self.hmi_payload.get("critical_space_map", [])
        if not isinstance(spaces, list):
            return {}
        return {str(row.get("space_id", "")): row for row in spaces if isinstance(row, dict)}

    def _work_orders_by_event(self) -> dict[str, list[dict[str, str]]]:
        grouped: dict[str, list[dict[str, str]]] = {}
        for work_order in self.work_orders:
            grouped.setdefault(work_order.get("event_id", ""), []).append(work_order)
        return grouped

    def _event_context(self, event: dict[str, str]) -> dict[str, Any]:
        spaces = self._space_by_id()
        space = spaces.get(event.get("space_id", ""), {})
        return {
            "event_id": event.get("event_id", ""),
            "severity": event.get("severity", ""),
            "status": event.get("status", ""),
            "asset_id": event.get("asset_id", ""),
            "device_id": event.get("tag_id", ""),
            "system": space.get("system_domain", ""),
            "device_type": event.get("event_title", ""),
            "zone": event.get("zone_id", ""),
            "location": space.get("space_name", event.get("space_id", "")),
            "space_id": event.get("space_id", ""),
            "event_title": event.get("event_title", ""),
            "operational_impact": event.get("operational_impact", ""),
            "recommended_action": event.get("recommended_action", ""),
        }

    def _work_order_context(self, work_order: dict[str, str]) -> dict[str, Any]:
        event = next((row for row in self.events if row.get("event_id") == work_order.get("event_id")), {})
        event_context = self._event_context(event) if event else {}
        return {
            "work_order_id": work_order.get("work_order_id", ""),
            "event_id": work_order.get("event_id", ""),
            "priority": work_order.get("priority", ""),
            "status": work_order.get("status", ""),
            "assigned_team": work_order.get("assigned_team", ""),
            "asset_id": work_order.get("asset_id", ""),
            "device_id": event_context.get("device_id", ""),
            "zone": event_context.get("zone", ""),
            "location": event_context.get("location", work_order.get("space_id", "")),
            "space_id": work_order.get("space_id", ""),
            "work_title": work_order.get("work_title", ""),
            "route_hint": work_order.get("route_hint", ""),
            "evidence_required": work_order.get("evidence_required", ""),
        }

    def fault_overlay(self, map_id: str) -> dict[str, Any]:
        work_orders_by_event = self._work_orders_by_event()
        rows = []
        for event in self.events:
            row = {
                **self._event_context(event),
                "marker_type": "fault_marker",
                "data_quality_status": PENDING_CLEARANCE,
                "click_action": "open_decision_lens",
                "linked_work_orders": [wo.get("work_order_id", "") for wo in work_orders_by_event.get(event.get("event_id", ""), [])],
            }
            rows.append(row)

        severity_counts = {severity: sum(1 for event in self.events if event.get("severity") == severity) for severity in {"critical", "high"}}
        return {
            **self._base(map_id),
            "summary": {
                "fault_count": len(rows),
                "critical_faults": severity_counts.get("critical", 0),
                "high_faults": severity_counts.get("high", 0),
                "linked_work_orders": sum(len(value) for value in work_orders_by_event.values()),
                "blocked_by_asset_quality": self._asset_quality()["blocked_by_asset_quality"],
            },
            "data": rows,
        }

    def work_order_overlay(self, map_id: str) -> dict[str, Any]:
        rows = [
            {
                **self._work_order_context(work_order),
                "marker_type": "work_order_route",
                "route_status": "route_hint_only",
                "click_action": "review_work_order_context",
            }
            for work_order in self.work_orders
        ]
        return {
            **self._base(map_id),
            "summary": {
                "work_order_count": len(rows),
                "p1_count": sum(1 for row in rows if row.get("priority") == "P1"),
                "p2_count": sum(1 for row in rows if row.get("priority") == "P2"),
                "assigned_count": sum(1 for row in rows if row.get("status") == "assigned"),
                "blocked_by_asset_quality": self._asset_quality()["blocked_by_asset_quality"],
            },
            "data": rows,
        }

    def technician_navigation(self, map_id: str) -> dict[str, Any]:
        routes = []
        for work_order in self.work_orders:
            context = self._work_order_context(work_order)
            start, destination = _route_parts(context.get("route_hint", ""))
            routes.append(
                {
                    "route_id": f"ROUTE-{context['work_order_id']}",
                    "assigned_team": context.get("assigned_team", ""),
                    "priority": context.get("priority", ""),
                    "start_context": start,
                    "destination": destination,
                    "zone": context.get("zone", ""),
                    "location": context.get("location", ""),
                    "asset_context": context.get("asset_id", ""),
                    "route_hint": context.get("route_hint", ""),
                    "evidence_required": context.get("evidence_required", ""),
                    "navigation_status": "route_hint_only",
                    "blocked_reason": "Precise CAD coordinate binding pending asset import clearance",
                }
            )
        return {
            **self._base(map_id),
            "summary": {
                "route_count": len(routes),
                "teams": sorted({route["assigned_team"] for route in routes if route["assigned_team"]}),
                "critical_routes": sum(1 for route in routes if route.get("priority") == "P1"),
            },
            "data": routes,
        }

    def decision_lens(self, map_id: str, *, event_id: str = "", work_order_id: str = "") -> dict[str, Any]:
        work_order = next((row for row in self.work_orders if row.get("work_order_id") == work_order_id), {})
        event = next((row for row in self.events if row.get("event_id") == event_id), {})
        if work_order and not event:
            event = next((row for row in self.events if row.get("event_id") == work_order.get("event_id")), {})
        if event and not work_order:
            work_order = next((row for row in self.work_orders if row.get("event_id") == event.get("event_id")), {})

        fault = self._event_context(event) if event else {}
        work_context = self._work_order_context(work_order) if work_order else {}
        context_type = "work_order" if work_order_id and work_context else "fault" if event_id and fault else "map"
        space = self._space_by_id().get(fault.get("space_id") or work_context.get("space_id", ""), {})
        evidence_items = _split_required_items(work_context.get("evidence_required", ""))
        return {
            **self._base(map_id),
            "decision_lens_id": f"DL-{work_context.get('work_order_id') or fault.get('event_id') or map_id}",
            "context_type": context_type,
            "data_quality_warning": "Asset import readiness is HOLD_BLOCKED; overlay is controlled sample projection only.",
            "fault": fault,
            "work_order": work_context,
            "asset_context": {
                "asset_id": work_context.get("asset_id") or fault.get("asset_id", ""),
                "device_id": fault.get("device_id", ""),
                "formal_asset_registry_write": False,
                "asset_binding_status": PENDING_CLEARANCE,
            },
            "space_context": {
                "space_id": space.get("space_id", fault.get("space_id") or work_context.get("space_id", "")),
                "space_name": space.get("space_name", fault.get("location") or work_context.get("location", "")),
                "zone": space.get("zone", fault.get("zone") or work_context.get("zone", "")),
                "criticality": space.get("criticality", ""),
            },
            "operational_context": {
                "impact": fault.get("operational_impact", ""),
                "recommended_action": fault.get("recommended_action", ""),
                "related_system": fault.get("system", ""),
                "related_location": fault.get("location") or work_context.get("location", ""),
            },
            "evidence_context": {
                "required": bool(evidence_items),
                "required_items": evidence_items,
                "status": "pending_closure_evidence",
            },
        }
