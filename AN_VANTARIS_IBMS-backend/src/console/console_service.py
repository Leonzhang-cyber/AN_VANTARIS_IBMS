"""UConsole read-only platform operations service."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.console.module_readiness_registry import (
    calculate_registry_summary,
    get_module_readiness,
    get_registry_health_details,
    list_module_readiness,
)
from src.console.platform_readiness_score import calculate_platform_readiness_score


class ConsoleService:
    MODULE_ID = "uconsole"
    MODULE_NAME = "UConsole / Platform Operations Dashboard"
    RUNTIME_MODE = "skeleton"
    PROVIDER = "local-platform-summary"
    SOURCE_SEMANTICS = "ibms-neutral"

    def get_console_health(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "moduleId": self.MODULE_ID,
            "moduleName": self.MODULE_NAME,
            "runtimeMode": self.RUNTIME_MODE,
            "provider": self.PROVIDER,
            "sourceSemantics": self.SOURCE_SEMANTICS,
            "readOnly": True,
            "controlActionsEnabled": False,
            "certified": False,
            "iec62443Certified": False,
        }

    def get_platform_modules_summary(self) -> List[Dict[str, Any]]:
        modules = list_module_readiness()
        items: List[Dict[str, Any]] = []
        for module in modules:
            audit_mode = str(module.get("auditReadiness", "planned"))
            items.append(
                {
                    "moduleId": module.get("moduleId", ""),
                    "moduleName": module.get("moduleName", ""),
                    "moduleType": module.get("moduleType", "platform-module"),
                    "domain": module.get("domain", "platform-operations"),
                    "route": module.get("route", ""),
                    "runtimeStatus": module.get("runtimeStatus", "planned"),
                    "readinessLevel": module.get("readinessLevel", "not-integrated"),
                    "lifecycleStage": module.get("lifecycleStage", "planned"),
                    "frontendReady": bool(module.get("frontendReady", False)),
                    "backendReady": bool(module.get("backendReady", False)),
                    "apiReady": bool(module.get("apiReady", False)),
                    "auditReadiness": audit_mode in {"ready", "foundation", "limited"},
                    "permissionMode": module.get("permissionMode", "not-integrated"),
                    "dataPersistenceMode": module.get("dataPersistenceMode", "not-integrated"),
                    "integrationMode": module.get("integrationMode", "not-integrated"),
                    "healthStatus": module.get("healthStatus", "planned"),
                    "healthScore": module.get("healthScore", 0),
                    "securityNotes": "; ".join(module.get("limitations", [])[:2]),
                    "certified": False,
                    "iec62443Certified": False,
                }
            )
        return items

    def get_operations_dashboard_summary(self) -> Dict[str, Any]:
        modules = list_module_readiness()
        totals = calculate_registry_summary(modules)
        readiness_score = calculate_platform_readiness_score(modules)
        return {
            "totals": totals,
            "readinessScore": readiness_score,
            "highlights": [
                "Reports readiness candidate",
                "UConsole r2 foundation",
            ],
            "warnings": [
                "Permission mode placeholder",
                "No IEC62443 certification claim",
                "No production RBAC integration",
                "Legacy docs may contain cross-system references but runtime is clean.",
            ],
            "securityPosture": {
                "auditReadinessFoundation": True,
                "realRbacIntegrated": False,
                "dbAuditIntegrated": False,
                "siemIntegrated": False,
                "ucdeRuntimeIntegrated": False,
                "edgeRuntimeIntegrated": False,
                "linkRuntimeIntegrated": False,
                "certified": False,
                "iec62443Certified": False,
            },
        }

    def get_reports_readiness_snapshot(self) -> Dict[str, Any]:
        reports = get_module_readiness("reports") or {}
        details = reports.get("healthDetails", {}) if isinstance(reports, dict) else {}

        def _is_ready(key: str) -> bool:
            part = details.get(key, {})
            status = str(part.get("status", "")).strip().lower()
            return status in {"ready", "foundation", "limited"}

        return {
            "routeReady": bool(reports.get("route")),
            "menuReady": bool(reports.get("route")),
            "queryReady": _is_ready("api"),
            "exportReady": _is_ready("api"),
            "manifestReady": _is_ready("api"),
            "auditStoreReady": _is_ready("audit"),
            "auditVerifyReady": _is_ready("audit"),
            "permissionPlaceholderReady": _is_ready("permission"),
            "auditExportReady": _is_ready("audit"),
            "certified": False,
            "iec62443Certified": False,
            "limitations": reports.get("limitations", []),
        }

    def get_module_health_detail(self, module_id: str) -> Optional[Dict[str, Any]]:
        return get_module_readiness(module_id)

    def get_all_module_health_details(self) -> List[Dict[str, Any]]:
        return get_registry_health_details()

    def get_readiness_registry(self) -> List[Dict[str, Any]]:
        return list_module_readiness()

    def get_readiness_summary(self) -> Dict[str, Any]:
        return calculate_registry_summary(list_module_readiness())

    def get_platform_readiness_score(self) -> Dict[str, Any]:
        return calculate_platform_readiness_score(list_module_readiness())

    def get_platform_navigation_model(self) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = []
        for module in list_module_readiness():
            module_id = str(module.get("moduleId", ""))
            module_name = str(module.get("moduleName", ""))
            status = str(module.get("runtimeStatus", "planned"))
            route = str(module.get("route", "")) or None

            launch_enabled = bool(route) and status in {"ready", "foundation"}
            launch_label = "Open Module"
            disabled_reason: Optional[str] = None
            boundary_note: Optional[str] = None

            if module_id == "reports":
                launch_label = "Open Reports"
            elif module_id == "uconsole":
                launch_label = "Current Dashboard"
            elif status == "planned":
                launch_label = "Planned"
                disabled_reason = "Module route is not available in current stage."
                boundary_note = "No runtime integration is performed from UConsole."
            elif status == "not-integrated":
                launch_label = "Not Integrated"
                disabled_reason = f"{module_name} runtime is not integrated in VANTARIS ONE at this stage."
                if module_id == "edge-fleet":
                    boundary_note = "AN_VANTARIS_EDGE remains a separate shared foundation boundary."
                elif module_id == "link-gateway":
                    boundary_note = "AN_VANTARIS_LINK remains a separate shared foundation boundary."
                else:
                    boundary_note = "This module remains a separate shared foundation boundary."
            else:
                launch_label = "Open Module" if launch_enabled else "Unavailable"
                if not launch_enabled:
                    disabled_reason = "Module route is not available in current stage."
                    boundary_note = "No runtime integration is performed from UConsole."

            items.append(
                {
                    "moduleId": module_id,
                    "moduleName": module_name,
                    "route": route,
                    "launchEnabled": launch_enabled,
                    "launchLabel": launch_label,
                    "status": status,
                    "disabledReason": disabled_reason,
                    "boundaryNote": boundary_note,
                    "readOnly": True,
                    "controlActionsEnabled": False,
                    "certified": False,
                    "iec62443Certified": False,
                }
            )
        return {
            "navigationMode": "read-only-module-launch",
            "controlActionsEnabled": False,
            "items": items,
        }

