"""UMMS maintenance service (read-only runtime skeleton)."""

from __future__ import annotations

from typing import Any, Dict, Optional

from src.umms.umms_provider import (
    get_maintenance_associations,
    get_maintenance_summary,
    get_umms_health,
    get_umms_ga_r2_section,
    get_umms_ga_r2_workspace,
    get_umms_customer_core_functions_projection,
    get_umms_package_entry_projection,
    get_umms_readiness_summary_projection,
    get_umms_safety_posture_projection,
    get_umms_stakeholder_review_projection,
    get_work_order,
    get_work_order_breakdown,
    list_work_orders,
)


class UmmsMaintenanceService:
    MODULE_ID = "umms"
    MODULE_NAME = "UMMS Maintenance"
    PROVIDER = "local-umms-provider"
    RUNTIME_MODE = "skeleton"
    SOURCE_SEMANTICS = "ibms-neutral"

    def get_umms_health(self) -> Dict[str, Any]:
        return get_umms_health()

    def list_work_orders(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        active_filters = {
            "workOrderType": str((filters or {}).get("workOrderType", "")).strip(),
            "workOrderCategory": str((filters or {}).get("workOrderCategory", "")).strip(),
            "workOrderStatus": str((filters or {}).get("workOrderStatus", "")).strip(),
            "priority": str((filters or {}).get("priority", "")).strip(),
            "siteId": str((filters or {}).get("siteId", "")).strip(),
            "systemId": str((filters or {}).get("systemId", "")).strip(),
            "assetId": str((filters or {}).get("assetId", "")).strip(),
        }
        rows = list_work_orders(active_filters)
        return {
            "workOrders": rows,
            "total": len(rows),
            "filters": active_filters,
            "summary": self.get_maintenance_summary(),
            "provider": self.PROVIDER,
            "runtimeMode": self.RUNTIME_MODE,
            "sourceSemantics": self.SOURCE_SEMANTICS,
            "mockData": True,
            "readOnly": True,
            "certified": False,
            "iec62443Certified": False,
        }

    def get_work_order_detail(self, work_order_id: str) -> Optional[Dict[str, Any]]:
        return get_work_order(work_order_id)

    def get_maintenance_summary(self) -> Dict[str, Any]:
        return get_maintenance_summary()

    def get_work_order_breakdown(self) -> Dict[str, Any]:
        return get_work_order_breakdown()

    def get_maintenance_associations(self) -> Dict[str, Any]:
        return get_maintenance_associations()

    def get_package_entry_projection(self) -> Dict[str, Any]:
        return get_umms_package_entry_projection()

    def get_stakeholder_review_projection(self) -> Dict[str, Any]:
        return get_umms_stakeholder_review_projection()

    def get_readiness_summary_projection(self) -> Dict[str, Any]:
        return get_umms_readiness_summary_projection()

    def get_customer_core_functions_projection(self) -> Dict[str, Any]:
        return get_umms_customer_core_functions_projection()

    def get_safety_posture_projection(self) -> Dict[str, Any]:
        return get_umms_safety_posture_projection()

    def get_ga_r2_workspace(self) -> Dict[str, Any]:
        return get_umms_ga_r2_workspace()

    def get_ga_r2_section(self, section: str) -> Dict[str, Any]:
        return get_umms_ga_r2_section(section)
