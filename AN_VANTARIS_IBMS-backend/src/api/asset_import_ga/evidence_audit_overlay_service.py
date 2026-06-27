"""Read-only evidence and audit closure projections for airport HMI maps."""

from __future__ import annotations

from typing import Any

from src.api.asset_import_ga.asset_import_service import readonly_flags
from src.api.asset_import_ga.fault_work_order_overlay_service import (
    BLOCKED_STATUS,
    SOURCE_MODE,
    FaultWorkOrderOverlayService,
    _split_required_items,
)


OVERLAY_MODE = "readonly_projection"
CLOSURE_STATUS = "not_ready_due_to_asset_quality_blockers"
PENDING_EVIDENCE = "pending_closure_evidence"


def _evidence_type(label: str) -> str:
    lowered = label.lower()
    if "photo" in lowered:
        return "photo"
    if "screenshot" in lowered:
        return "screenshot"
    if "log" in lowered:
        return "action_log"
    return "status_report"


class EvidenceAuditOverlayService:
    def __init__(self, fault_work_order_service: FaultWorkOrderOverlayService | None = None) -> None:
        self.source = fault_work_order_service or FaultWorkOrderOverlayService()

    def _base(self, map_id: str) -> dict[str, Any]:
        quality = self.source._asset_quality()
        return {
            **readonly_flags(),
            "map_id": map_id,
            "overlay_mode": OVERLAY_MODE,
            "source_mode": SOURCE_MODE,
            "asset_import_readiness": quality["asset_import_readiness"],
            "asset_overlay_status": quality["asset_overlay_status"],
            "closure_status": CLOSURE_STATUS,
            "formal_evidence_write": False,
            "formal_work_order_closure": False,
            "formal_asset_registry_write": False,
            "formal_event_registry_write": False,
            "formal_work_order_write": False,
            "confirm_enabled": quality["confirm_enabled"],
        }

    def _evidence_rows(self) -> list[dict[str, Any]]:
        rows = []
        for work_order in self.source.work_orders:
            work_context = self.source._work_order_context(work_order)
            items = _split_required_items(work_context.get("evidence_required", ""))
            for index, item in enumerate(items, start=1):
                rows.append(
                    {
                        "evidence_id": f"EVID-{work_context['work_order_id']}-{index:02d}",
                        "source_type": "work_order",
                        "source_id": work_context.get("work_order_id", ""),
                        "event_id": work_context.get("event_id", ""),
                        "work_order_id": work_context.get("work_order_id", ""),
                        "asset_id": work_context.get("asset_id", ""),
                        "space_id": work_context.get("space_id", ""),
                        "zone": work_context.get("zone", ""),
                        "location": work_context.get("location", ""),
                        "evidence_type": _evidence_type(item),
                        "evidence_label": item,
                        "required_for_closure": True,
                        "status": PENDING_EVIDENCE,
                        "audit_ready": False,
                        "blocked_reason": "Asset import quality blockers must be resolved before formal closure evidence can be committed.",
                    }
                )
        return rows

    def evidence_overlay(self, map_id: str) -> dict[str, Any]:
        rows = self._evidence_rows()
        work_order_ids = {row["work_order_id"] for row in rows if row.get("work_order_id")}
        return {
            **self._base(map_id),
            "summary": {
                "evidence_items_required": len(rows),
                "work_orders_with_evidence": len(work_order_ids),
                "audit_ready_items": 0,
                "closure_ready": False,
                "blocked_by_asset_quality": True,
            },
            "data": rows,
        }

    def work_order_evidence(self, map_id: str) -> dict[str, Any]:
        rows = []
        for work_order in self.source.work_orders:
            context = self.source._work_order_context(work_order)
            items = _split_required_items(context.get("evidence_required", ""))
            rows.append(
                {
                    "work_order_id": context.get("work_order_id", ""),
                    "event_id": context.get("event_id", ""),
                    "priority": context.get("priority", ""),
                    "assigned_team": context.get("assigned_team", ""),
                    "work_title": context.get("work_title", ""),
                    "location": context.get("location", ""),
                    "route_hint": context.get("route_hint", ""),
                    "evidence_required_raw": context.get("evidence_required", ""),
                    "evidence_items": [
                        {"evidence_type": _evidence_type(item), "label": item, "required": True, "status": "pending"}
                        for item in items
                    ],
                    "closure_readiness": "blocked_by_asset_quality",
                    "confirm_close_enabled": False,
                }
            )
        return {
            **self._base(map_id),
            "summary": {
                "work_order_count": len(rows),
                "evidence_required_count": sum(len(row["evidence_items"]) for row in rows),
                "closure_ready_count": 0,
                "blocked_count": len(rows),
            },
            "data": rows,
        }

    def closure_readiness(self, map_id: str) -> dict[str, Any]:
        work_order_count = len(self.source.work_orders)
        evidence_count = len(self._evidence_rows())
        return {
            **self._base(map_id),
            "summary": {
                "total_work_orders": work_order_count,
                "ready_to_close": 0,
                "blocked_by_asset_quality": work_order_count,
                "pending_evidence": evidence_count,
            },
            "gates": [
                {
                    "gate": "Asset Import Quality",
                    "status": "blocked",
                    "reason": "Asset import readiness is HOLD_BLOCKED",
                },
                {
                    "gate": "Evidence Required",
                    "status": "pending",
                    "reason": "Closure evidence is not formally uploaded",
                },
                {
                    "gate": "Audit Trail",
                    "status": OVERLAY_MODE,
                    "reason": "Audit payload is available but not committed to formal registry",
                },
            ],
        }

    def import_audit_summary(self, map_id: str) -> dict[str, Any]:
        report_summary = self.source.quality_report.get("summary", {})
        alert = self.source.quality_report.get("alert", {})
        return {
            **self._base(map_id),
            "source": "asset_import_quality_report",
            "summary": {
                "total_records": int(report_summary.get("total_records", 0)),
                "blocker_count": int(report_summary.get("blocker_count", 0)),
                "major_count": int(report_summary.get("major_count", 0)),
                "warning_count": int(report_summary.get("warning_count", 0)),
                "info_count": int(report_summary.get("info_count", 0)),
                "readiness": report_summary.get("readiness", "UNKNOWN"),
            },
            "audit": {
                "formal_import_committed": False,
                "formal_asset_registry_write": False,
                "rollback_reference": "not_available_before_formal_import",
                "quality_report_available": bool(self.source.quality_report),
                "confirm_enabled": bool(alert.get("confirm_enabled", False)),
            },
        }

    def export_evidence_center(self, map_id: str) -> dict[str, Any]:
        return {
            **self._base(map_id),
            "export_ready": False,
            "export_status": "blocked_by_asset_quality",
            "available_packages": [
                {
                    "package_id": "airport-t3-gf-data-quality-report",
                    "label": "Airport T3 Ground Floor Asset Data Quality Report",
                    "status": "available_readonly",
                    "source": "airport_asset_import_quality_report",
                },
                {
                    "package_id": "airport-t3-gf-work-order-evidence",
                    "label": "Airport T3 Ground Floor Work Order Evidence Requirements",
                    "status": OVERLAY_MODE,
                },
            ],
            "blocked_reason": "Formal export package requires asset import clearance and evidence commitment.",
        }
