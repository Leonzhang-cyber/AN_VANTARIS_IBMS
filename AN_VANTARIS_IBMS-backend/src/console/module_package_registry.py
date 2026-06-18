"""UConsole module package registry (read-only local skeleton)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional


def _entry(
    *,
    enabled: bool,
    visible: bool,
    route: str,
    label: str,
    entry_mode: str,
    locked_reason: Optional[str],
) -> Dict[str, Any]:
    return {
        "enabled": bool(enabled),
        "visible": bool(visible),
        "route": route,
        "label": label,
        "entryMode": entry_mode,
        "lockedReason": locked_reason,
    }


def _role_visibility(customer: bool, engineer: bool, admin: bool) -> Dict[str, bool]:
    return {"customer": bool(customer), "engineer": bool(engineer), "admin": bool(admin)}


def _package_record(
    *,
    package_id: str,
    package_code: str,
    package_name: str,
    module_id: str,
    module_name: str,
    module_type: str,
    package_category: str,
    installed: bool,
    entitled: bool,
    enabled: bool,
    visible: bool,
    installed_version: str,
    available_version: str,
    patch_status: str,
    patch_mode: str,
    upgrade_required: bool,
    activation_mode: str,
    locked_reason: Optional[str],
    customer_entry: Dict[str, Any],
    engineer_entry: Dict[str, Any],
    admin_entry: Dict[str, Any],
    role_visibility: Dict[str, bool],
    entry_status: str,
    limitations: List[str],
    next_actions: List[str],
) -> Dict[str, Any]:
    return {
        "packageId": package_id,
        "packageCode": package_code,
        "packageName": package_name,
        "moduleId": module_id,
        "moduleName": module_name,
        "moduleType": module_type,
        "packageCategory": package_category,
        "installed": bool(installed),
        "entitled": bool(entitled),
        "enabled": bool(enabled),
        "visible": bool(visible),
        "installedVersion": installed_version,
        "availableVersion": available_version,
        "patchStatus": patch_status,
        "patchMode": patch_mode,
        "upgradeRequired": bool(upgrade_required),
        "activationMode": activation_mode,
        "lockedReason": locked_reason,
        "customerEntry": customer_entry,
        "engineerEntry": engineer_entry,
        "adminEntry": admin_entry,
        "roleVisibility": role_visibility,
        "entryStatus": entry_status,
        "runtimeMode": "local-skeleton",
        "provider": "local-package-registry",
        "readOnly": True,
        "controlActionsEnabled": False,
        "patchActionsEnabled": False,
        "licenseServerIntegrated": False,
        "entitlementRuntimeIntegrated": False,
        "hotPlugArchitectureReady": True,
        "roleEntryModelReady": True,
        "certified": False,
        "iec62443Certified": False,
        "limitations": limitations,
        "nextActions": next_actions,
    }


def _base_packages() -> List[Dict[str, Any]]:
    admin_entry = _entry(
        enabled=True,
        visible=True,
        route="/console/operations",
        label="Package Management",
        entry_mode="admin-package-center",
        locked_reason=None,
    )

    def _locked_entry(route: str, label: str, mode: str, reason: str) -> Dict[str, Any]:
        return _entry(enabled=False, visible=False, route=route, label=label, entry_mode=mode, locked_reason=reason)

    return [
        _package_record(
            package_id="PKG-REPORTS",
            package_code="PKG-REPORTS",
            package_name="Reports Package",
            module_id="reports",
            module_name="Reports",
            module_type="platform-module",
            package_category="operations",
            installed=True,
            entitled=True,
            enabled=True,
            visible=True,
            installed_version="1.0.0",
            available_version="1.0.0",
            patch_status="up-to-date",
            patch_mode="local-skeleton-patch",
            upgrade_required=False,
            activation_mode="entitlement-gated",
            locked_reason=None,
            customer_entry=_entry(
                enabled=True,
                visible=True,
                route="/reports",
                label="Reports",
                entry_mode="customer-application",
                locked_reason=None,
            ),
            engineer_entry=_entry(
                enabled=False,
                visible=False,
                route="",
                label="Reports Diagnostics",
                entry_mode="engineer-diagnostics",
                locked_reason="Engineer workspace not installed",
            ),
            admin_entry=deepcopy(admin_entry),
            role_visibility=_role_visibility(True, False, True),
            entry_status="active",
            limitations=["No runtime enable/disable action.", "No real patch installer.", "No license server integration."],
            next_actions=["Keep package state in local skeleton until entitlement runtime is approved."],
        ),
        _package_record(
            package_id="PKG-UCDE",
            package_code="PKG-UCDE",
            package_name="UCDE Package",
            module_id="ucde",
            module_name="UCDE Evidence Center",
            module_type="business-module",
            package_category="compliance",
            installed=True,
            entitled=True,
            enabled=True,
            visible=True,
            installed_version="1.0.0",
            available_version="1.0.0",
            patch_status="up-to-date",
            patch_mode="local-skeleton-patch",
            upgrade_required=False,
            activation_mode="entitlement-gated",
            locked_reason=None,
            customer_entry=_entry(
                enabled=True,
                visible=True,
                route="/ucde/evidence",
                label="UCDE Evidence Center",
                entry_mode="customer-application",
                locked_reason=None,
            ),
            engineer_entry=_entry(
                enabled=False,
                visible=False,
                route="",
                label="UCDE Diagnostics",
                entry_mode="engineer-diagnostics",
                locked_reason="Engineer workspace not installed",
            ),
            admin_entry=deepcopy(admin_entry),
            role_visibility=_role_visibility(True, False, True),
            entry_status="active",
            limitations=["No runtime enable/disable action.", "No real patch installer.", "No license server integration."],
            next_actions=["Add package entitlement validation after runtime gate approval."],
        ),
        _package_record(
            package_id="PKG-ASSETS",
            package_code="PKG-ASSETS",
            package_name="Assets Package",
            module_id="assets-topology",
            module_name="Assets & Topology",
            module_type="platform-module",
            package_category="operations",
            installed=True,
            entitled=True,
            enabled=True,
            visible=True,
            installed_version="1.0.0",
            available_version="1.0.0",
            patch_status="up-to-date",
            patch_mode="local-skeleton-patch",
            upgrade_required=False,
            activation_mode="entitlement-gated",
            locked_reason=None,
            customer_entry=_entry(
                enabled=True,
                visible=True,
                route="/assets/topology",
                label="Assets & Topology",
                entry_mode="customer-application",
                locked_reason=None,
            ),
            engineer_entry=_entry(
                enabled=False,
                visible=False,
                route="",
                label="Assets Diagnostics",
                entry_mode="engineer-diagnostics",
                locked_reason="Engineer workspace not installed",
            ),
            admin_entry=deepcopy(admin_entry),
            role_visibility=_role_visibility(True, False, True),
            entry_status="active",
            limitations=["No runtime enable/disable action.", "No real patch installer.", "No license server integration."],
            next_actions=["Add package activation workflow after governance gate approval."],
        ),
        _package_record(
            package_id="PKG-UESG",
            package_code="PKG-UESG",
            package_name="UESG Package",
            module_id="uesg",
            module_name="UESG Sustainability",
            module_type="business-module",
            package_category="sustainability",
            installed=True,
            entitled=True,
            enabled=True,
            visible=True,
            installed_version="1.0.0",
            available_version="1.1.0",
            patch_status="upgrade-available",
            patch_mode="local-skeleton-patch",
            upgrade_required=True,
            activation_mode="entitlement-gated",
            locked_reason=None,
            customer_entry=_entry(
                enabled=True,
                visible=True,
                route="/uesg/sustainability",
                label="UESG Sustainability",
                entry_mode="customer-application",
                locked_reason=None,
            ),
            engineer_entry=_entry(
                enabled=False,
                visible=False,
                route="",
                label="UESG Diagnostics",
                entry_mode="engineer-diagnostics",
                locked_reason="Engineer workspace not installed",
            ),
            admin_entry=deepcopy(admin_entry),
            role_visibility=_role_visibility(True, False, True),
            entry_status="active",
            limitations=["No runtime enable/disable action.", "No real patch installer.", "No license server integration."],
            next_actions=["Review upgrade workflow after patch governance gate approval."],
        ),
        _package_record(
            package_id="PKG-UMMS",
            package_code="PKG-UMMS",
            package_name="UMMS Package",
            module_id="umms",
            module_name="UMMS Maintenance",
            module_type="business-module",
            package_category="maintenance",
            installed=True,
            entitled=True,
            enabled=True,
            visible=True,
            installed_version="1.0.0",
            available_version="1.0.0",
            patch_status="up-to-date",
            patch_mode="local-skeleton-patch",
            upgrade_required=False,
            activation_mode="entitlement-gated",
            locked_reason=None,
            customer_entry=_entry(
                enabled=True,
                visible=True,
                route="/umms/maintenance",
                label="UMMS Maintenance",
                entry_mode="customer-application",
                locked_reason=None,
            ),
            engineer_entry=_entry(
                enabled=False,
                visible=False,
                route="",
                label="UMMS Diagnostics",
                entry_mode="engineer-diagnostics",
                locked_reason="Engineer workspace not installed",
            ),
            admin_entry=deepcopy(admin_entry),
            role_visibility=_role_visibility(True, False, True),
            entry_status="active",
            limitations=["No runtime enable/disable action.", "No real patch installer.", "No license server integration."],
            next_actions=["Add maintenance package entitlement checks in future runtime gate."],
        ),
        _package_record(
            package_id="PKG-UFMS",
            package_code="PKG-UFMS",
            package_name="UFMS Package Placeholder",
            module_id="ufms",
            module_name="UFMS Fault Management",
            module_type="business-module",
            package_category="placeholder",
            installed=False,
            entitled=False,
            enabled=False,
            visible=False,
            installed_version="",
            available_version="1.0.0",
            patch_status="locked",
            patch_mode="local-skeleton-patch",
            upgrade_required=False,
            activation_mode="entitlement-gated",
            locked_reason="Package not entitled",
            customer_entry=_locked_entry(
                route="/ufms/fault-management",
                label="UFMS Fault Management",
                mode="customer-application",
                reason="Package not entitled",
            ),
            engineer_entry=_locked_entry(
                route="/ufms/diagnostics",
                label="UFMS Diagnostics",
                mode="engineer-diagnostics",
                reason="Package not entitled",
            ),
            admin_entry=deepcopy(admin_entry),
            role_visibility=_role_visibility(False, False, True),
            entry_status="locked",
            limitations=["UFMS package is placeholder-only in this stage.", "UFMS integration is not connected in this stage."],
            next_actions=["Keep UFMS as locked placeholder until entitlement policy is approved."],
        ),
        _package_record(
            package_id="PKG-UEDGE",
            package_code="PKG-UEDGE",
            package_name="UEDGE Package Placeholder",
            module_id="uedge",
            module_name="UEDGE Setup",
            module_type="foundation-module",
            package_category="placeholder",
            installed=False,
            entitled=False,
            enabled=False,
            visible=False,
            installed_version="",
            available_version="1.0.0",
            patch_status="not-installed",
            patch_mode="local-skeleton-patch",
            upgrade_required=False,
            activation_mode="installation-gated",
            locked_reason="Package not installed",
            customer_entry=_locked_entry(
                route="/uedge/setup",
                label="UEDGE Setup",
                mode="customer-application",
                reason="Package not installed",
            ),
            engineer_entry=_entry(
                enabled=False,
                visible=True,
                route="/uedge/diagnostics",
                label="UEDGE Diagnostics",
                entry_mode="engineer-diagnostics",
                locked_reason="Package not installed",
            ),
            admin_entry=deepcopy(admin_entry),
            role_visibility=_role_visibility(False, True, True),
            entry_status="locked",
            limitations=["UEDGE package is placeholder-only in this stage.", "No EDGE runtime integration."],
            next_actions=["Keep UEDGE diagnostics as placeholder until installation gate is approved."],
        ),
        _package_record(
            package_id="PKG-LINK",
            package_code="PKG-LINK",
            package_name="LINK Gateway Package Placeholder",
            module_id="link-gateway",
            module_name="LINK Gateway",
            module_type="foundation-module",
            package_category="placeholder",
            installed=False,
            entitled=False,
            enabled=False,
            visible=False,
            installed_version="",
            available_version="1.0.0",
            patch_status="not-installed",
            patch_mode="local-skeleton-patch",
            upgrade_required=False,
            activation_mode="installation-gated",
            locked_reason="Package not installed",
            customer_entry=_locked_entry(
                route="",
                label="LINK Gateway",
                mode="customer-application",
                reason="Package not installed",
            ),
            engineer_entry=_entry(
                enabled=False,
                visible=True,
                route="/link/diagnostics",
                label="LINK Diagnostics",
                entry_mode="engineer-diagnostics",
                locked_reason="Package not installed",
            ),
            admin_entry=deepcopy(admin_entry),
            role_visibility=_role_visibility(False, True, True),
            entry_status="locked",
            limitations=["LINK package is placeholder-only in this stage.", "No LINK runtime integration."],
            next_actions=["Keep LINK diagnostics as placeholder until installation gate is approved."],
        ),
        _package_record(
            package_id="PKG-NEXUS-AI",
            package_code="PKG-NEXUS-AI",
            package_name="NEXUS-AI Package Placeholder",
            module_id="nexus-ai",
            module_name="NEXUS-AI",
            module_type="platform-module",
            package_category="future",
            installed=False,
            entitled=False,
            enabled=False,
            visible=False,
            installed_version="",
            available_version="1.0.0",
            patch_status="not-installed",
            patch_mode="local-skeleton-patch",
            upgrade_required=False,
            activation_mode="installation-gated",
            locked_reason="Package not installed",
            customer_entry=_locked_entry(
                route="/nexus-ai/workspace",
                label="NEXUS-AI Workspace",
                mode="customer-application",
                reason="Package not installed",
            ),
            engineer_entry=_locked_entry(
                route="/nexus-ai/debug",
                label="NEXUS-AI Debug",
                mode="engineer-diagnostics",
                reason="Package not installed",
            ),
            admin_entry=deepcopy(admin_entry),
            role_visibility=_role_visibility(False, False, True),
            entry_status="locked",
            limitations=["NEXUS-AI package is placeholder-only in this stage."],
            next_actions=["Keep NEXUS-AI as locked placeholder until future roadmap gate."],
        ),
    ]


def _normalized_packages() -> List[Dict[str, Any]]:
    return [deepcopy(item) for item in _base_packages()]


def _parse_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def list_module_packages(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    values = filters or {}
    module_id = str(values.get("moduleId", "")).strip()
    package_category = str(values.get("packageCategory", "")).strip()
    patch_status = str(values.get("patchStatus", "")).strip()
    role = str(values.get("role", "")).strip().lower()
    installed = _parse_bool(values.get("installed"))
    entitled = _parse_bool(values.get("entitled"))
    enabled = _parse_bool(values.get("enabled"))
    visible = _parse_bool(values.get("visible"))

    def _match(item: Dict[str, Any]) -> bool:
        if module_id and str(item.get("moduleId", "")) != module_id:
            return False
        if package_category and str(item.get("packageCategory", "")) != package_category:
            return False
        if patch_status and str(item.get("patchStatus", "")) != patch_status:
            return False
        if installed is not None and bool(item.get("installed")) != installed:
            return False
        if entitled is not None and bool(item.get("entitled")) != entitled:
            return False
        if enabled is not None and bool(item.get("enabled")) != enabled:
            return False
        if visible is not None and bool(item.get("visible")) != visible:
            return False
        if role in {"customer", "engineer", "admin"} and not bool(item.get("roleVisibility", {}).get(role)):
            return False
        return True

    return [item for item in _normalized_packages() if _match(item)]


def get_module_package(package_id_or_module_id: str) -> Optional[Dict[str, Any]]:
    target = str(package_id_or_module_id or "").strip().lower()
    if not target:
        return None
    for item in _normalized_packages():
        if str(item.get("packageId", "")).lower() == target:
            return item
        if str(item.get("moduleId", "")).lower() == target:
            return item
    return None


def get_package_summary() -> Dict[str, Any]:
    rows = _normalized_packages()
    return {
        "totalPackages": len(rows),
        "installedPackages": len([item for item in rows if bool(item.get("installed"))]),
        "entitledPackages": len([item for item in rows if bool(item.get("entitled"))]),
        "enabledPackages": len([item for item in rows if bool(item.get("enabled"))]),
        "visiblePackages": len([item for item in rows if bool(item.get("visible"))]),
        "lockedPackages": len([item for item in rows if str(item.get("entryStatus", "")) == "locked"]),
        "customerEntryCount": len(
            [
                item
                for item in rows
                if bool(item.get("customerEntry", {}).get("visible")) and bool(item.get("customerEntry", {}).get("enabled"))
            ]
        ),
        "engineerEntryCount": len(
            [item for item in rows if bool(item.get("engineerEntry", {}).get("visible"))]
        ),
        "adminEntryCount": len(
            [item for item in rows if bool(item.get("adminEntry", {}).get("visible"))]
        ),
        "patchReadyPackages": len([item for item in rows if str(item.get("patchStatus", "")) in {"up-to-date", "upgrade-available"}]),
        "upgradeRequiredPackages": len([item for item in rows if bool(item.get("upgradeRequired"))]),
        "licenseServerIntegrated": False,
        "patchActionsEnabled": False,
        "controlActionsEnabled": False,
        "roleEntryModelReady": True,
        "hotPlugArchitectureReady": True,
        "limitations": [
            "No real patch installer.",
            "No license server integration.",
            "No runtime enable/disable action.",
        ],
        "certified": False,
        "iec62443Certified": False,
    }


def get_customer_applications() -> List[Dict[str, Any]]:
    rows = _normalized_packages()
    return [
        {
            "packageId": item.get("packageId"),
            "moduleId": item.get("moduleId"),
            "moduleName": item.get("moduleName"),
            "entry": deepcopy(item.get("customerEntry", {})),
            "entitled": bool(item.get("entitled")),
            "enabled": bool(item.get("enabled")),
            "visible": bool(item.get("visible")),
            "lockedReason": item.get("lockedReason"),
            "certified": False,
            "iec62443Certified": False,
        }
        for item in rows
    ]


def get_engineer_workspace_entries() -> List[Dict[str, Any]]:
    rows = _normalized_packages()
    entries = [
        {
            "packageId": item.get("packageId"),
            "moduleId": item.get("moduleId"),
            "moduleName": item.get("moduleName"),
            "entry": deepcopy(item.get("engineerEntry", {})),
            "certified": False,
            "iec62443Certified": False,
        }
        for item in rows
        if bool(item.get("roleVisibility", {}).get("engineer")) or bool(item.get("engineerEntry", {}).get("visible"))
    ]
    entries.extend(
        [
            {
                "packageId": "PKG-CONNECTOR-DEBUG",
                "moduleId": "connector-debug",
                "moduleName": "Connector Debug Placeholder",
                "entry": _entry(
                    enabled=False,
                    visible=True,
                    route="/console/operations",
                    label="Connector Debug",
                    entry_mode="engineer-diagnostics",
                    locked_reason="Package not installed",
                ),
                "certified": False,
                "iec62443Certified": False,
            },
            {
                "packageId": "PKG-MAPPING-REVIEW",
                "moduleId": "mapping-review",
                "moduleName": "Mapping Review Placeholder",
                "entry": _entry(
                    enabled=False,
                    visible=True,
                    route="/console/operations",
                    label="Mapping Review",
                    entry_mode="engineer-diagnostics",
                    locked_reason="Package not installed",
                ),
                "certified": False,
                "iec62443Certified": False,
            },
        ]
    )
    return entries


def get_admin_package_entries() -> List[Dict[str, Any]]:
    rows = _normalized_packages()
    return [
        {
            "packageId": item.get("packageId"),
            "moduleId": item.get("moduleId"),
            "moduleName": item.get("moduleName"),
            "entry": deepcopy(item.get("adminEntry", {})),
            "entitled": bool(item.get("entitled")),
            "enabled": bool(item.get("enabled")),
            "visible": bool(item.get("visible")),
            "patchStatus": item.get("patchStatus"),
            "upgradeRequired": bool(item.get("upgradeRequired")),
            "certified": False,
            "iec62443Certified": False,
        }
        for item in rows
    ]


def get_locked_packages() -> List[Dict[str, Any]]:
    rows = _normalized_packages()
    return [item for item in rows if str(item.get("entryStatus", "")) == "locked"]


def get_patch_readiness() -> Dict[str, Any]:
    rows = _normalized_packages()
    return {
        "patchMode": "local-skeleton-patch-readiness",
        "patchActionsEnabled": False,
        "packages": [
            {
                "packageId": item.get("packageId"),
                "packageCode": item.get("packageCode"),
                "patchStatus": item.get("patchStatus"),
                "upgradeRequired": bool(item.get("upgradeRequired")),
                "installedVersion": item.get("installedVersion"),
                "availableVersion": item.get("availableVersion"),
            }
            for item in rows
        ],
        "upgradeRequiredPackages": [item.get("packageId") for item in rows if bool(item.get("upgradeRequired"))],
        "patchReadyPackages": [
            item.get("packageId") for item in rows if str(item.get("patchStatus", "")) in {"up-to-date", "upgrade-available"}
        ],
        "licenseServerIntegrated": False,
        "limitations": [
            "No real patch installer.",
            "No license server integration.",
            "No runtime enable/disable action.",
        ],
        "certified": False,
        "iec62443Certified": False,
    }

