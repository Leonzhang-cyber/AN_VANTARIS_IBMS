"""Read-only HMI asset overlay projection service.

R2C intentionally projects quality-gated import report data only. It does not
read or write the formal Asset Registry and does not activate runtime overlays.
"""

from __future__ import annotations

from collections import Counter
import json
import re
from pathlib import Path
from typing import Any

from src.api.asset_import_ga.asset_import_service import readonly_flags
from src.api.asset_import_ga.asset_import_store import AssetImportRuntimeStore, repo_root


STATIC_REPORT_PATH = "AN_VANTARIS_ONE/reports/asset-import-ga/airport_asset_import_quality_report.json"
OVERLAY_MODE = "readonly_projection"
GROUPED_OVERLAY_MODE = "zone_location_grouped"
BLOCKED_STATUS = "blocked_by_data_quality"
UNAVAILABLE_STATUS = "unavailable"
PENDING_REVIEW = "pending_review"


def _safe_pairs(value: Any) -> list[tuple[str, int]]:
    pairs = []
    if isinstance(value, list):
        for row in value:
            if isinstance(row, (list, tuple)) and len(row) >= 2:
                pairs.append((str(row[0]), int(row[1] or 0)))
    return pairs


def _slug(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "-", value.upper()).strip("-")
    return text or "UNKNOWN"


def _top_dict(pairs: list[tuple[str, int]], limit: int = 10) -> dict[str, int]:
    return {name or "UNKNOWN": count for name, count in pairs[:limit]}


class AssetOverlayService:
    def __init__(self, store: AssetImportRuntimeStore | None = None) -> None:
        self.store = store or AssetImportRuntimeStore()

    def _load_report(self) -> tuple[dict[str, Any] | None, str]:
        batches = self.store.list_batches()
        for row in batches:
            batch = self.store.get_batch(str(row.get("import_batch_id", "")))
            if batch and isinstance(batch.get("quality_report"), dict):
                return batch["quality_report"], "runtime_batch_report"

        static_path = repo_root() / STATIC_REPORT_PATH
        if static_path.is_file():
            return json.loads(static_path.read_text(encoding="utf-8")), "fallback_static_report"
        return None, "fallback_static_report_missing"

    def _base(self, map_id: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
        report, source_status = self._load_report()
        if not report:
            return (
                {
                    **readonly_flags(),
                    "map_id": map_id,
                    "overlay_mode": OVERLAY_MODE,
                    "data_source_status": source_status,
                    "asset_import_readiness": "UNKNOWN",
                    "asset_overlay_status": UNAVAILABLE_STATUS,
                    "formal_asset_registry_write": False,
                    "confirm_enabled": False,
                },
                None,
            )

        summary = report.get("summary", {})
        readiness = str(summary.get("readiness", "UNKNOWN"))
        confirm_enabled = bool(summary.get("confirm_enabled", readiness != "HOLD_BLOCKED"))
        overlay_status = BLOCKED_STATUS if readiness == "HOLD_BLOCKED" else "pending_review"
        return (
            {
                **readonly_flags(),
                "map_id": map_id,
                "overlay_mode": OVERLAY_MODE,
                "data_source_status": source_status,
                "asset_import_readiness": readiness,
                "asset_overlay_status": overlay_status,
                "formal_asset_registry_write": False,
                "confirm_enabled": confirm_enabled,
                "source_file_name": report.get("source_file_name", summary.get("source_file_name", "")),
            },
            report,
        )

    def zone_summary(self, map_id: str) -> dict[str, Any]:
        base, report = self._base(map_id)
        if not report:
            return {**base, "summary": {}, "data": []}
        summary = report.get("summary", {})
        zone_pairs = _safe_pairs(report.get("zone_summary", []))
        system_pairs = _safe_pairs(report.get("system_summary", []))
        blocked_records = int(summary.get("blocker_count", 0))
        return {
            **base,
            "summary": {
                "zone_count": len(zone_pairs),
                "asset_records_seen": int(summary.get("total_records", 0)),
                "formal_assets_imported": 0,
                "blocked_records": blocked_records,
                "unmapped_locations": int(summary.get("unmatched_location_count", summary.get("location_count", 0))),
            },
            "data": [
                {
                    "zone": zone or "UNKNOWN",
                    "level": "MIXED",
                    "asset_record_count": count,
                    "system_summary": _top_dict(system_pairs, 7),
                    "device_type_summary": _top_dict(_safe_pairs(report.get("device_type_summary", [])), 8),
                    "data_quality_status": PENDING_REVIEW,
                }
                for zone, count in zone_pairs
            ],
        }

    def location_summary(self, map_id: str) -> dict[str, Any]:
        base, report = self._base(map_id)
        if not report:
            return {**base, "summary": {}, "data": []}
        summary = report.get("summary", {})
        location_pairs = _safe_pairs(report.get("location_summary", []))
        system_names = [name for name, _ in _safe_pairs(report.get("system_summary", [])) if name]
        top_device_types = [name for name, _ in _safe_pairs(report.get("device_type_summary", []))[:10] if name]
        return {
            **base,
            "summary": {
                "location_count": len(location_pairs),
                "asset_records_seen": int(summary.get("total_records", 0)),
                "formal_assets_imported": 0,
                "pending_review_locations": len(location_pairs),
            },
            "data": [
                {
                    "location": location or "UNKNOWN",
                    "zone": "PENDING_REVIEW",
                    "level": "PENDING_REVIEW",
                    "asset_record_count": count,
                    "systems": system_names[:7],
                    "top_device_types": top_device_types,
                    "data_quality_status": PENDING_REVIEW,
                    "map_binding_status": GROUPED_OVERLAY_MODE,
                }
                for location, count in location_pairs[:250]
            ],
        }

    def asset_overlay(self, map_id: str) -> dict[str, Any]:
        base, report = self._base(map_id)
        if not report:
            return {**base, "overlay_mode": GROUPED_OVERLAY_MODE, "summary": {}, "data": []}
        summary = report.get("summary", {})
        location_pairs = _safe_pairs(report.get("location_summary", []))
        system_pairs = _safe_pairs(report.get("system_summary", []))
        device_pairs = _safe_pairs(report.get("device_type_summary", []))
        markers = [
            {
                "marker_id": f"{_slug(map_id)}-{_slug(location)}",
                "level": "PENDING_REVIEW",
                "zone": "PENDING_REVIEW",
                "location": location or "UNKNOWN",
                "marker_type": "location_cluster",
                "asset_record_count": count,
                "system_summary": _top_dict(system_pairs, 7),
                "device_type_summary": _top_dict(device_pairs, 8),
                "data_quality_status": PENDING_REVIEW,
                "click_action": "review_location_assets",
            }
            for location, count in location_pairs[:250]
        ]
        return {
            **base,
            "overlay_mode": GROUPED_OVERLAY_MODE,
            "summary": {
                "records_seen": int(summary.get("total_records", 0)),
                "overlay_markers": len(markers),
                "blocked_by_quality": base["asset_overlay_status"] == BLOCKED_STATUS,
                "confirm_enabled": base["confirm_enabled"],
                "formal_asset_registry_write": False,
            },
            "data": markers,
        }

    def system_overlay(self, map_id: str) -> dict[str, Any]:
        base, report = self._base(map_id)
        if not report:
            return {**base, "summary": {}, "data": []}
        system_pairs = _safe_pairs(report.get("system_summary", []))
        level_counter = Counter(dict(_safe_pairs(report.get("level_summary", []))))
        zone_counter = Counter(dict(_safe_pairs(report.get("zone_summary", []))))
        location_pairs = _safe_pairs(report.get("location_summary", []))
        device_pairs = _safe_pairs(report.get("device_type_summary", []))
        return {
            **base,
            "summary": {
                "system_count": len(system_pairs),
                "asset_records_seen": int(report.get("summary", {}).get("total_records", 0)),
                "formal_assets_imported": 0,
            },
            "data": [
                {
                    "system": system or "UNKNOWN",
                    "asset_record_count": count,
                    "levels": dict(level_counter),
                    "zones": dict(zone_counter),
                    "top_locations": [{"location": name or "UNKNOWN", "count": value} for name, value in location_pairs[:10]],
                    "top_device_types": [{"device_type": name or "UNKNOWN", "count": value} for name, value in device_pairs[:10]],
                    "data_quality_status": PENDING_REVIEW,
                }
                for system, count in system_pairs
            ],
        }
