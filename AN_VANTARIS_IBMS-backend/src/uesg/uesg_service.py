"""UESG sustainability service (read-only runtime skeleton)."""

from __future__ import annotations

from typing import Any, Dict, Optional

from src.uesg.uesg_provider import (
    get_associations,
    get_metric,
    get_metrics_breakdown,
    get_metrics_summary,
    get_uesg_health,
    list_metrics,
)


class UesgSustainabilityService:
    MODULE_ID = "uesg"
    MODULE_NAME = "UESG Sustainability"
    PROVIDER = "local-uesg-provider"
    RUNTIME_MODE = "skeleton"
    SOURCE_SEMANTICS = "ibms-neutral"

    def get_uesg_health(self) -> Dict[str, Any]:
        health = get_uesg_health()
        health["moduleId"] = self.MODULE_ID
        health["moduleName"] = self.MODULE_NAME
        return health

    def list_metrics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        active_filters = {
            "metricCategory": str((filters or {}).get("metricCategory", "")).strip(),
            "metricScope": str((filters or {}).get("metricScope", "")).strip(),
            "metricPeriod": str((filters or {}).get("metricPeriod", "")).strip(),
            "siteId": str((filters or {}).get("siteId", "")).strip(),
            "systemId": str((filters or {}).get("systemId", "")).strip(),
            "dataQuality": str((filters or {}).get("dataQuality", "")).strip(),
        }
        items = list_metrics(active_filters)
        return {
            "items": items,
            "total": len(items),
            "filters": active_filters,
            "summary": self.get_metrics_summary(),
            "provider": self.PROVIDER,
            "runtimeMode": self.RUNTIME_MODE,
            "sourceSemantics": self.SOURCE_SEMANTICS,
            "mockData": True,
            "readOnly": True,
            "certified": False,
            "iec62443Certified": False,
            "greenMarkCertified": False,
            "griCertified": False,
            "isoCertified": False,
        }

    def get_metrics_summary(self) -> Dict[str, Any]:
        summary = get_metrics_summary()
        summary["limitations"] = summary.get("limitations", []) + [
            "UESG R1 uses local skeleton ESG metrics.",
            "Meter integration, carbon factor database, EDGE/LINK integration and certification reporting are not integrated.",
        ]
        return summary

    def get_metrics_breakdown(self) -> Dict[str, Any]:
        return get_metrics_breakdown()

    def get_associations(self) -> Dict[str, Any]:
        return get_associations()

    def get_metric_detail(self, metric_id: str) -> Optional[Dict[str, Any]]:
        return get_metric(metric_id)

