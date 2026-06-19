"""UConsole module content dashboard service (read-only local skeleton)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.console.console_service import ConsoleService
from src.console.module_package_registry import get_engineer_workspace_entries, list_module_packages
from src.console.module_package_service import ModulePackageService
from src.console.module_role_visibility import get_role_entry_view


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_role(role: str) -> str:
    role_key = str(role or "admin").strip().lower()
    if role_key in {"customer", "engineer", "admin"}:
        return role_key
    return "admin"


def _entry_for_role(package: Dict[str, Any], role: str) -> Dict[str, Any]:
    if role == "customer":
        return dict(package.get("customerEntry", {}))
    if role == "engineer":
        return dict(package.get("engineerEntry", {}))
    return dict(package.get("adminEntry", {}))


def _base_card(
    *,
    package: Dict[str, Any],
    role: str,
    module_id: str,
    module_name: str,
    package_code: str,
    status: str,
    summary: Dict[str, Any],
    highlights: List[str],
    risks: List[str],
    limitations: List[str],
    fallback_used: bool,
) -> Dict[str, Any]:
    entry = _entry_for_role(package, role)
    role_visibility = dict(package.get("roleVisibility", {}))
    route = str(entry.get("route", "") or "")
    if not route and role == "admin":
        route = str(package.get("customerEntry", {}).get("route", "") or "")
    return {
        "moduleId": module_id,
        "moduleName": module_name,
        "packageCode": package_code,
        "contentMode": "local-skeleton-summary",
        "runtimeLinked": False,
        "visible": bool(package.get("visible", False)) and bool(entry.get("visible", False)),
        "enabled": bool(package.get("enabled", False)) and bool(entry.get("enabled", False)),
        "entitled": bool(package.get("entitled", False)),
        "route": route,
        "status": status,
        "summary": summary,
        "highlights": highlights,
        "risks": risks,
        "limitations": limitations,
        "lastUpdated": _now_iso(),
        "fallbackUsed": bool(fallback_used),
        "lockedReason": entry.get("lockedReason") or package.get("lockedReason"),
        "entryMode": str(entry.get("entryMode", "")),
        "roleVisibility": role_visibility,
        "packageState": {
            "installed": bool(package.get("installed", False)),
            "entitled": bool(package.get("entitled", False)),
            "enabled": bool(package.get("enabled", False)),
            "visible": bool(package.get("visible", False)),
            "patchStatus": str(package.get("patchStatus", "")),
            "upgradeRequired": bool(package.get("upgradeRequired", False)),
            "lockedReason": package.get("lockedReason"),
        },
        "readOnly": True,
        "controlActionsEnabled": False,
        "realRbacIntegrated": False,
        "routeGuardIntegrated": False,
        "certified": False,
        "iec62443Certified": False,
    }


class ModuleContentDashboardService:
    """Aggregates read-only module content summaries for UConsole."""

    def __init__(self) -> None:
        self._package_service = ModulePackageService()
        self._console_service = ConsoleService()

    def _packages_by_module(self) -> Dict[str, Dict[str, Any]]:
        rows = list_module_packages({})
        return {str(item.get("moduleId", "")): item for item in rows}

    def _reports_card(self, package: Dict[str, Any], role: str) -> Dict[str, Any]:
        fallback_used = False
        try:
            readiness = self._console_service.get_reports_readiness_snapshot()
            summary = {
                "readinessStatus": "readiness-candidate",
                "auditReady": bool(readiness.get("auditStoreReady")) and bool(readiness.get("auditVerifyReady")),
                "exportReady": bool(readiness.get("exportReady")),
                "permissionMode": "placeholder-allow" if bool(readiness.get("permissionPlaceholderReady")) else "not-integrated",
                "route": "/reports",
            }
            highlights = [
                "Reports readiness candidate summary is available.",
                "Audit foundation and export flow are in local skeleton mode.",
            ]
            risks = [
                "Permission mode remains placeholder-only.",
                "No certified evidence protocol is integrated.",
            ]
            limitations = list(readiness.get("limitations", []))
        except Exception:
            fallback_used = True
            summary = {
                "readinessStatus": "foundation",
                "auditReady": False,
                "exportReady": False,
                "permissionMode": "not-integrated",
                "route": "/reports",
            }
            highlights = ["Reports content summary fallback is active."]
            risks = ["Reports readiness source is unavailable; fallback data is shown."]
            limitations = ["Reports summary fallback only; no cross-module runtime dependency is required."]
        return _base_card(
            package=package,
            role=role,
            module_id="reports",
            module_name="Reports",
            package_code="PKG-REPORTS",
            status="foundation",
            summary=summary,
            highlights=highlights,
            risks=risks,
            limitations=limitations,
            fallback_used=fallback_used,
        )

    def _ucde_card(self, package: Dict[str, Any], role: str) -> Dict[str, Any]:
        fallback_used = False
        try:
            from src.ucde.evidence_service import UcdeEvidenceService

            summary_data = UcdeEvidenceService().get_evidence_summary()
            summary = {
                "totalEvidence": int(summary_data.get("totalEvidence", 0)),
                "readinessEvidence": int(summary_data.get("readinessEvidence", 0)),
                "auditEvidence": int(summary_data.get("auditEvidence", 0)),
                "traceabilityPathCount": int(summary_data.get("traceabilityPathCount", 0)),
                "relationshipGraphReady": bool(summary_data.get("relationshipGraphReady", False)),
                "runtimeLinkedReferences": 0,
            }
            highlights = [
                "Evidence and traceability summary is available in local skeleton mode.",
                "Relationship graph readiness is exposed as read-only metadata.",
            ]
            risks = [
                "No runtime evidence chain validation is integrated.",
            ]
            limitations = list(summary_data.get("limitations", []))
        except Exception:
            fallback_used = True
            summary = {
                "totalEvidence": 0,
                "readinessEvidence": 0,
                "auditEvidence": 0,
                "traceabilityPathCount": 0,
                "relationshipGraphReady": False,
                "runtimeLinkedReferences": 0,
            }
            highlights = ["UCDE content summary fallback is active."]
            risks = ["UCDE summary source is unavailable; fallback data is shown."]
            limitations = ["UCDE summary fallback only; runtime calls are not required in this stage."]
        return _base_card(
            package=package,
            role=role,
            module_id="ucde",
            module_name="UCDE Evidence Center",
            package_code="PKG-UCDE",
            status="foundation",
            summary=summary,
            highlights=highlights,
            risks=risks,
            limitations=limitations,
            fallback_used=fallback_used,
        )

    def _assets_card(self, package: Dict[str, Any], role: str) -> Dict[str, Any]:
        fallback_used = False
        try:
            from src.assets.assets_service import AssetsTopologyService

            summary_data = AssetsTopologyService().get_assets_summary()
            summary = {
                "totalAssets": int(summary_data.get("totalAssets", 0)),
                "systemCount": int(summary_data.get("systemCount", 0)),
                "equipmentCount": int(summary_data.get("equipmentCount", 0)),
                "pointCount": int(summary_data.get("pointCount", 0)),
                "totalRelationships": int(summary_data.get("totalRelationships", 0)),
                "topologyValidated": bool(summary_data.get("topologyValidated", False)),
                "runtimeLinkedAssets": 0,
            }
            highlights = [
                "Assets hierarchy and relationship totals are available.",
                "Topology summary remains read-only and local skeleton.",
            ]
            risks = ["Runtime discovery and telemetry linking are not integrated."]
            limitations = list(summary_data.get("limitations", []))
        except Exception:
            fallback_used = True
            summary = {
                "totalAssets": 0,
                "systemCount": 0,
                "equipmentCount": 0,
                "pointCount": 0,
                "totalRelationships": 0,
                "topologyValidated": False,
                "runtimeLinkedAssets": 0,
            }
            highlights = ["Assets content summary fallback is active."]
            risks = ["Assets summary source is unavailable; fallback data is shown."]
            limitations = ["Assets summary fallback only; runtime calls are not required in this stage."]
        return _base_card(
            package=package,
            role=role,
            module_id="assets-topology",
            module_name="Assets & Topology",
            package_code="PKG-ASSETS",
            status="foundation",
            summary=summary,
            highlights=highlights,
            risks=risks,
            limitations=limitations,
            fallback_used=fallback_used,
        )

    def _uesg_card(self, package: Dict[str, Any], role: str) -> Dict[str, Any]:
        fallback_used = False
        try:
            from src.uesg.uesg_service import UesgSustainabilityService

            summary_data = UesgSustainabilityService().get_metrics_summary()
            summary = {
                "totalMetrics": int(summary_data.get("totalMetrics", 0)),
                "energyMetricCount": int(summary_data.get("energyMetrics", 0)),
                "carbonMetricCount": int(summary_data.get("carbonMetrics", 0)),
                "waterMetricCount": int(summary_data.get("waterMetrics", 0)),
                "categoryDetailReady": bool(summary_data.get("categoryDetailReady", False)),
                "dataQualityReady": bool(summary_data.get("dataQualityReady", False)),
                "meterLinkedMetrics": 0,
                "reportReadyMetrics": 0,
            }
            highlights = [
                "ESG metric categories and quality readiness are visible.",
                "Category and calculation readiness are presented as local summaries.",
            ]
            risks = ["No meter integration or certified reporting integration."]
            limitations = list(summary_data.get("limitations", []))
        except Exception:
            fallback_used = True
            summary = {
                "totalMetrics": 0,
                "energyMetricCount": 0,
                "carbonMetricCount": 0,
                "waterMetricCount": 0,
                "categoryDetailReady": False,
                "dataQualityReady": False,
                "meterLinkedMetrics": 0,
                "reportReadyMetrics": 0,
            }
            highlights = ["UESG content summary fallback is active."]
            risks = ["UESG summary source is unavailable; fallback data is shown."]
            limitations = ["UESG summary fallback only; runtime calls are not required in this stage."]
        return _base_card(
            package=package,
            role=role,
            module_id="uesg",
            module_name="UESG Sustainability",
            package_code="PKG-UESG",
            status="foundation",
            summary=summary,
            highlights=highlights,
            risks=risks,
            limitations=limitations,
            fallback_used=fallback_used,
        )

    def _umms_card(self, package: Dict[str, Any], role: str) -> Dict[str, Any]:
        fallback_used = False
        try:
            from src.umms.umms_service import UmmsMaintenanceService

            summary_data = UmmsMaintenanceService().get_maintenance_summary()
            summary = {
                "totalWorkOrders": int(summary_data.get("totalWorkOrders", 0)),
                "preventiveCount": int(summary_data.get("preventiveCount", 0)),
                "correctiveCount": int(summary_data.get("correctiveCount", 0)),
                "openCount": int(summary_data.get("openCount", 0)),
                "plannedCount": int(summary_data.get("plannedCount", 0)),
                "highPriorityCount": int(summary_data.get("highPriorityCount", 0)),
                "dispatchedWorkOrders": 0,
            }
            highlights = [
                "Maintenance work order summary is available.",
                "Preventive/corrective and priority distribution is shown as skeleton data.",
            ]
            risks = ["Dispatch, mobile and notification integrations are not enabled."]
            limitations = list(summary_data.get("limitations", []))
        except Exception:
            fallback_used = True
            summary = {
                "totalWorkOrders": 0,
                "preventiveCount": 0,
                "correctiveCount": 0,
                "openCount": 0,
                "plannedCount": 0,
                "highPriorityCount": 0,
                "dispatchedWorkOrders": 0,
            }
            highlights = ["UMMS content summary fallback is active."]
            risks = ["UMMS summary source is unavailable; fallback data is shown."]
            limitations = ["UMMS summary fallback only; runtime calls are not required in this stage."]
        return _base_card(
            package=package,
            role=role,
            module_id="umms",
            module_name="UMMS Maintenance",
            package_code="PKG-UMMS",
            status="foundation",
            summary=summary,
            highlights=highlights,
            risks=risks,
            limitations=limitations,
            fallback_used=fallback_used,
        )

    def _package_role_summary_card(self, role: str) -> Dict[str, Any]:
        package_summary = self._package_service.get_package_summary()
        role_summary = self._package_service.get_role_visibility_summary()
        package = self._packages_by_module().get("uconsole", {})
        summary = {
            "totalPackages": int(package_summary.get("totalPackages", 0)),
            "visiblePackages": int(package_summary.get("visiblePackages", 0)),
            "lockedPackages": int(package_summary.get("lockedPackages", 0)),
            "customerVisibleCount": int(role_summary.get("customerVisibleCount", 0)),
            "engineerVisibleCount": int(role_summary.get("engineerVisibleCount", 0)),
            "adminVisibleCount": int(role_summary.get("adminVisibleCount", 0)),
            "patchReadyPackages": int(package_summary.get("patchReadyPackages", 0)),
            "upgradeRequiredPackages": int(package_summary.get("upgradeRequiredPackages", 0)),
        }
        return _base_card(
            package=package
            if package
            else {
                "installed": True,
                "entitled": True,
                "enabled": True,
                "visible": True,
                "patchStatus": "up-to-date",
                "upgradeRequired": False,
                "customerEntry": {"route": "/console/operations", "entryMode": "customer-application", "visible": True, "enabled": True},
                "engineerEntry": {"route": "/console/operations", "entryMode": "engineer-diagnostics", "visible": True, "enabled": False},
                "adminEntry": {"route": "/console/operations", "entryMode": "admin-package-center", "visible": True, "enabled": True},
                "roleVisibility": {"customer": True, "engineer": True, "admin": True},
            },
            role=role,
            module_id="package-role-summary",
            module_name="Package / Role Summary",
            package_code="PKG-UCONSOLE-SUMMARY",
            status="foundation",
            summary=summary,
            highlights=["Package and role visibility totals are synchronized with local registry."],
            risks=["Role visibility remains preview-only and read-only."],
            limitations=[
                "No real RBAC/auth integration.",
                "No route guard enforcement.",
                "No runtime package control actions.",
            ],
            fallback_used=False,
        )

    def _locked_future_card(self, role: str) -> Dict[str, Any]:
        rows = list_module_packages({})
        locked = {str(item.get("moduleId", "")): bool(item.get("entryStatus") == "locked") for item in rows}
        package = self._packages_by_module().get("nexus-ai", {})
        summary = {
            "ufmsLocked": bool(locked.get("ufms", False)),
            "uedgeLocked": bool(locked.get("uedge", False)),
            "linkLocked": bool(locked.get("link-gateway", False)),
            "nexusAiLocked": bool(locked.get("nexus-ai", False)),
        }
        return _base_card(
            package=package
            if package
            else {
                "installed": False,
                "entitled": False,
                "enabled": False,
                "visible": False,
                "patchStatus": "not-installed",
                "upgradeRequired": False,
                "lockedReason": "Package not installed",
                "customerEntry": {"route": "", "entryMode": "customer-application", "visible": False, "enabled": False},
                "engineerEntry": {"route": "", "entryMode": "engineer-diagnostics", "visible": False, "enabled": False},
                "adminEntry": {"route": "/console/operations", "entryMode": "admin-package-center", "visible": True, "enabled": True},
                "roleVisibility": {"customer": False, "engineer": False, "admin": True},
            },
            role=role,
            module_id="locked-future-modules",
            module_name="Locked / Future Content Preview",
            package_code="PKG-LOCKED-PREVIEW",
            status="locked",
            summary=summary,
            highlights=["Locked/future modules are preview-only and cannot be launched."],
            risks=["No entitlement runtime and no install workflow are integrated."],
            limitations=[
                "UFMS/UEDGE/LINK/NEXUS-AI remain locked placeholders.",
                "No runtime calls are performed for locked packages.",
            ],
            fallback_used=False,
        )

    def _engineer_context_card(self) -> Dict[str, Any]:
        placeholders = [
            row
            for row in get_engineer_workspace_entries()
            if str(row.get("moduleId", "")) in {"uedge", "link-gateway", "connector-debug", "mapping-review"}
        ]
        return {
            "moduleId": "engineer-content-context",
            "moduleName": "Engineer Content Context",
            "packageCode": "PKG-ENGINEER-CONTEXT",
            "contentMode": "local-skeleton-summary",
            "runtimeLinked": False,
            "visible": True,
            "enabled": False,
            "entitled": False,
            "route": "/console/operations",
            "status": "foundation",
            "summary": {
                "workspacePlaceholders": len(placeholders),
                "uedgeDiagnosticsPlaceholder": True,
                "linkDiagnosticsPlaceholder": True,
                "connectorDebugPlaceholder": True,
                "mappingReviewPlaceholder": True,
            },
            "highlights": ["Engineer workspace placeholders are visible as context-only entries."],
            "risks": ["No EDGE/LINK diagnostics integration is connected in this stage."],
            "limitations": [
                "Engineer context uses package registry placeholders only.",
                "No runtime diagnostics calls are performed.",
            ],
            "lastUpdated": _now_iso(),
            "fallbackUsed": False,
            "lockedReason": "Package not installed",
            "entryMode": "engineer-diagnostics",
            "roleVisibility": {"customer": False, "engineer": True, "admin": True},
            "packageState": {
                "installed": False,
                "entitled": False,
                "enabled": False,
                "visible": True,
                "patchStatus": "not-installed",
                "upgradeRequired": False,
                "lockedReason": "Package not installed",
            },
            "readOnly": True,
            "controlActionsEnabled": False,
            "realRbacIntegrated": False,
            "routeGuardIntegrated": False,
            "certified": False,
            "iec62443Certified": False,
        }

    def _core_cards(self, role: str) -> List[Dict[str, Any]]:
        packages = self._packages_by_module()
        cards: List[Dict[str, Any]] = []
        reports_pkg = packages.get("reports")
        ucde_pkg = packages.get("ucde")
        assets_pkg = packages.get("assets-topology")
        uesg_pkg = packages.get("uesg")
        umms_pkg = packages.get("umms")
        if reports_pkg:
            cards.append(self._reports_card(reports_pkg, role))
        if ucde_pkg:
            cards.append(self._ucde_card(ucde_pkg, role))
        if assets_pkg:
            cards.append(self._assets_card(assets_pkg, role))
        if uesg_pkg:
            cards.append(self._uesg_card(uesg_pkg, role))
        if umms_pkg:
            cards.append(self._umms_card(umms_pkg, role))
        cards.append(self._package_role_summary_card(role))
        cards.append(self._locked_future_card(role))
        if role in {"engineer", "admin"}:
            cards.append(self._engineer_context_card())
        return cards

    def _filter_cards_by_role(self, cards: List[Dict[str, Any]], role: str) -> List[Dict[str, Any]]:
        role_key = _normalize_role(role)
        if role_key == "admin":
            return cards

        packages = list_module_packages({})
        role_entries = get_role_entry_view(role_key, packages) or {}
        visible_ids = {str(row.get("moduleId", "")) for row in role_entries.get("visiblePackages", [])}
        locked_ids = {str(row.get("moduleId", "")) for row in role_entries.get("lockedPackages", [])}

        filtered: List[Dict[str, Any]] = []
        for card in cards:
            module_id = str(card.get("moduleId", ""))
            if module_id in {"package-role-summary", "locked-future-modules"}:
                filtered.append(card)
                continue
            if role_key == "engineer" and module_id == "engineer-content-context":
                filtered.append(card)
                continue
            if module_id in visible_ids:
                filtered.append(card)
                continue
            if role_key == "customer" and module_id in locked_ids:
                # customer keeps locked cards only as preview and without launch
                row = dict(card)
                row["visible"] = False
                row["enabled"] = False
                row["route"] = ""
                filtered.append(row)
        return filtered

    def get_module_content_cards(self, role: str = "admin") -> Dict[str, Any]:
        role_key = _normalize_role(role)
        cards = self._filter_cards_by_role(self._core_cards(role_key), role_key)
        return {
            "role": role_key,
            "items": cards,
            "contentMode": "local-skeleton-content-dashboard",
            "runtimeLinked": False,
            "readOnly": True,
            "controlActionsEnabled": False,
            "realRbacIntegrated": False,
            "routeGuardIntegrated": False,
            "certified": False,
            "iec62443Certified": False,
        }

    def get_module_content_summary(self, role: str = "admin") -> Dict[str, Any]:
        role_key = _normalize_role(role)
        cards = self._filter_cards_by_role(self._core_cards(role_key), role_key)
        return {
            "role": role_key,
            "totalContentCards": len(cards),
            "visibleContentCards": len([row for row in cards if bool(row.get("visible"))]),
            "fallbackCards": len([row for row in cards if bool(row.get("fallbackUsed"))]),
            "lockedPreviewCards": len([row for row in cards if bool(row.get("lockedReason")) or str(row.get("status")) == "locked"]),
            "readOnly": True,
            "runtimeLinked": False,
            "realRbacIntegrated": False,
            "routeGuardIntegrated": False,
            "certified": False,
            "iec62443Certified": False,
        }

    def get_module_content_detail(self, module_id: str, role: str = "admin") -> Optional[Dict[str, Any]]:
        role_key = _normalize_role(role)
        target = str(module_id or "").strip().lower()
        if not target:
            return None
        cards = self._filter_cards_by_role(self._core_cards(role_key), role_key)
        for card in cards:
            if str(card.get("moduleId", "")).lower() == target:
                return {
                    "role": role_key,
                    "item": card,
                    "readOnly": True,
                    "runtimeLinked": False,
                    "realRbacIntegrated": False,
                    "routeGuardIntegrated": False,
                    "certified": False,
                    "iec62443Certified": False,
                }
        return None

    def get_module_content_dashboard(self, role: str = "admin") -> Dict[str, Any]:
        role_key = _normalize_role(role)
        cards_data = self.get_module_content_cards(role_key)
        summary = self.get_module_content_summary(role_key)
        return {
            "role": role_key,
            "summary": summary,
            "cards": cards_data.get("items", []),
            "contentMode": "local-skeleton-content-dashboard",
            "runtimeLinked": False,
            "readOnly": True,
            "controlActionsEnabled": False,
            "realRbacIntegrated": False,
            "routeGuardIntegrated": False,
            "limitations": [
                "Module Content Dashboard uses read-only local skeleton summaries.",
                "Cross-module aggregation, EDGE/LINK diagnostics and UFMS integration are not connected.",
            ],
            "certified": False,
            "iec62443Certified": False,
        }
