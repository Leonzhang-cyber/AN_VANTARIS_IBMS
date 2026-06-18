"""UConsole read-only platform operations service."""

from __future__ import annotations

from typing import Any, Dict, List


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
        return [
            {
                "moduleId": "reports",
                "moduleName": "Reports",
                "moduleType": "platform-module",
                "runtimeStatus": "ready",
                "readinessLevel": "readiness-candidate",
                "route": "/reports",
                "frontendReady": True,
                "backendReady": True,
                "auditReadiness": True,
                "permissionMode": "placeholder-allow",
                "dataPersistenceMode": "local-jsonl-audit",
                "securityNotes": "Audit readiness foundation with placeholder permission mode.",
                "certified": False,
                "iec62443Certified": False,
            },
            {
                "moduleId": "uconsole",
                "moduleName": "UConsole / Platform Operations Dashboard",
                "moduleType": "platform-module",
                "runtimeStatus": "foundation",
                "readinessLevel": "r1-foundation",
                "route": "/console/operations",
                "frontendReady": True,
                "backendReady": True,
                "auditReadiness": False,
                "permissionMode": "placeholder-allow",
                "dataPersistenceMode": "none",
                "securityNotes": "Read-only dashboard foundation; no control actions enabled.",
                "certified": False,
                "iec62443Certified": False,
            },
            {
                "moduleId": "ucde",
                "moduleName": "UCDE Evidence Center",
                "moduleType": "business-module",
                "runtimeStatus": "planned",
                "readinessLevel": "not-integrated",
                "route": "",
                "frontendReady": False,
                "backendReady": False,
                "auditReadiness": False,
                "permissionMode": "not-integrated",
                "dataPersistenceMode": "not-integrated",
                "securityNotes": "Runtime integration not included in this stage.",
                "certified": False,
                "iec62443Certified": False,
            },
            {
                "moduleId": "uesg",
                "moduleName": "UESG Sustainability",
                "moduleType": "business-module",
                "runtimeStatus": "planned",
                "readinessLevel": "not-integrated",
                "route": "",
                "frontendReady": False,
                "backendReady": False,
                "auditReadiness": False,
                "permissionMode": "not-integrated",
                "dataPersistenceMode": "not-integrated",
                "securityNotes": "Runtime integration not included in this stage.",
                "certified": False,
                "iec62443Certified": False,
            },
            {
                "moduleId": "umms",
                "moduleName": "UMMS Maintenance",
                "moduleType": "business-module",
                "runtimeStatus": "planned",
                "readinessLevel": "not-integrated",
                "route": "",
                "frontendReady": False,
                "backendReady": False,
                "auditReadiness": False,
                "permissionMode": "not-integrated",
                "dataPersistenceMode": "not-integrated",
                "securityNotes": "Runtime integration not included in this stage.",
                "certified": False,
                "iec62443Certified": False,
            },
            {
                "moduleId": "assets-topology",
                "moduleName": "Assets & Topology",
                "moduleType": "platform-module",
                "runtimeStatus": "planned",
                "readinessLevel": "not-integrated",
                "route": "",
                "frontendReady": False,
                "backendReady": False,
                "auditReadiness": False,
                "permissionMode": "not-integrated",
                "dataPersistenceMode": "not-integrated",
                "securityNotes": "Foundation planning only.",
                "certified": False,
                "iec62443Certified": False,
            },
            {
                "moduleId": "edge-fleet",
                "moduleName": "EDGE Fleet",
                "moduleType": "foundation-module",
                "runtimeStatus": "not-integrated",
                "readinessLevel": "external-foundation-reference",
                "route": "",
                "frontendReady": False,
                "backendReady": False,
                "auditReadiness": False,
                "permissionMode": "not-integrated",
                "dataPersistenceMode": "not-integrated",
                "securityNotes": "No direct runtime integration in IBMS scope.",
                "certified": False,
                "iec62443Certified": False,
            },
            {
                "moduleId": "link-gateway",
                "moduleName": "LINK Gateway",
                "moduleType": "foundation-module",
                "runtimeStatus": "not-integrated",
                "readinessLevel": "external-foundation-reference",
                "route": "",
                "frontendReady": False,
                "backendReady": False,
                "auditReadiness": False,
                "permissionMode": "not-integrated",
                "dataPersistenceMode": "not-integrated",
                "securityNotes": "No direct runtime integration in IBMS scope.",
                "certified": False,
                "iec62443Certified": False,
            },
            {
                "moduleId": "nexus-ai",
                "moduleName": "NEXUS-AI",
                "moduleType": "platform-module",
                "runtimeStatus": "planned",
                "readinessLevel": "not-integrated",
                "route": "",
                "frontendReady": False,
                "backendReady": False,
                "auditReadiness": False,
                "permissionMode": "not-integrated",
                "dataPersistenceMode": "not-integrated",
                "securityNotes": "Planned capability; no runtime integration yet.",
                "certified": False,
                "iec62443Certified": False,
            },
        ]

    def get_operations_dashboard_summary(self) -> Dict[str, Any]:
        modules = self.get_platform_modules_summary()
        ready_modules = [item for item in modules if item.get("runtimeStatus") == "ready"]
        foundation_modules = [item for item in modules if item.get("runtimeStatus") == "foundation"]
        planned_modules = [item for item in modules if item.get("runtimeStatus") == "planned"]
        audit_ready_modules = [item for item in modules if bool(item.get("auditReadiness"))]
        return {
            "totals": {
                "totalModules": len(modules),
                "readyModules": len(ready_modules),
                "foundationModules": len(foundation_modules),
                "plannedModules": len(planned_modules),
                "auditReadyModules": len(audit_ready_modules),
                "certifiedModules": 0,
                "iec62443CertifiedModules": 0,
            },
            "highlights": [
                "Reports readiness candidate",
                "UConsole foundation",
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
                "certified": False,
                "iec62443Certified": False,
            },
        }

    def get_reports_readiness_snapshot(self) -> Dict[str, Any]:
        return {
            "routeReady": True,
            "menuReady": True,
            "queryReady": True,
            "exportReady": True,
            "manifestReady": True,
            "auditStoreReady": True,
            "auditVerifyReady": True,
            "permissionPlaceholderReady": True,
            "auditExportReady": True,
            "certified": False,
            "iec62443Certified": False,
            "limitations": [
                "No real auth/RBAC integration.",
                "No DB audit table migration.",
                "No formal immutable evidence chain.",
                "No UCDE runtime integration.",
                "No IEC62443 certification claim.",
            ],
        }

