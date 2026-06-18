"""UConsole module package center service (read-only local skeleton)."""

from __future__ import annotations

from typing import Any, Dict, Optional

from src.console.module_package_registry import (
    get_admin_package_entries,
    get_customer_applications,
    get_engineer_workspace_entries,
    get_locked_packages,
    get_module_package,
    get_package_summary,
    get_patch_readiness,
    list_module_packages,
)
from src.console.module_role_visibility import (
    get_role_entry_view,
    get_role_menu_preview,
    get_role_visibility_policy,
    get_supported_roles,
)


class ModulePackageService:
    MODULE_ID = "uconsole-package-center"
    MODULE_NAME = "UConsole Module Package Center"

    def get_package_center_health(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "moduleId": self.MODULE_ID,
            "moduleName": self.MODULE_NAME,
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
        }

    def list_packages(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        values = filters or {}
        active_filters = {
            "moduleId": values.get("moduleId", ""),
            "packageCategory": values.get("packageCategory", ""),
            "installed": values.get("installed"),
            "entitled": values.get("entitled"),
            "enabled": values.get("enabled"),
            "visible": values.get("visible"),
            "patchStatus": values.get("patchStatus", ""),
            "role": values.get("role", ""),
        }
        return {
            "items": list_module_packages(active_filters),
            "summary": get_package_summary(),
            "filters": active_filters,
            "runtimeMode": "local-skeleton",
            "provider": "local-package-registry",
            "readOnly": True,
            "controlActionsEnabled": False,
            "patchActionsEnabled": False,
            "certified": False,
            "iec62443Certified": False,
        }

    def get_package_detail(self, package_id_or_module_id: str) -> Optional[Dict[str, Any]]:
        return get_module_package(package_id_or_module_id)

    def get_package_summary(self) -> Dict[str, Any]:
        return get_package_summary()

    def get_entry_center(self) -> Dict[str, Any]:
        return {
            "customerApplications": get_customer_applications(),
            "engineerWorkspace": get_engineer_workspace_entries(),
            "adminPackageCenter": get_admin_package_entries(),
            "lockedPackages": get_locked_packages(),
            "entryMode": "local-skeleton-entry-center",
            "roleAware": True,
            "runtimeLinked": False,
            "certified": False,
            "iec62443Certified": False,
        }

    def get_locked_packages(self) -> Dict[str, Any]:
        return {
            "items": get_locked_packages(),
            "count": len(get_locked_packages()),
            "runtimeMode": "local-skeleton",
            "readOnly": True,
            "certified": False,
            "iec62443Certified": False,
        }

    def get_patch_readiness(self) -> Dict[str, Any]:
        return get_patch_readiness()

    def get_supported_roles(self) -> Dict[str, Any]:
        return {
            "items": get_supported_roles(),
            "roleVisibilityMode": "local-skeleton-role-visibility",
            "readOnly": True,
            "realRbacIntegrated": False,
            "authIntegrated": False,
            "routeGuardIntegrated": False,
            "certified": False,
            "iec62443Certified": False,
        }

    def get_role_visibility(self, role: str) -> Optional[Dict[str, Any]]:
        packages = list_module_packages({})
        return get_role_visibility_policy(role, packages)

    def get_role_entries(self, role: str) -> Optional[Dict[str, Any]]:
        packages = list_module_packages({})
        return get_role_entry_view(role, packages)

    def get_role_menu_preview(self, role: str) -> Optional[Dict[str, Any]]:
        packages = list_module_packages({})
        return get_role_menu_preview(role, packages)

    def get_role_visibility_summary(self) -> Dict[str, Any]:
        packages = list_module_packages({})
        customer_view = get_role_entry_view("customer", packages) or {}
        engineer_view = get_role_entry_view("engineer", packages) or {}
        admin_view = get_role_entry_view("admin", packages) or {}

        return {
            "supportedRoles": get_supported_roles(),
            "roleVisibilityMode": "local-skeleton-role-visibility",
            "realRbacIntegrated": False,
            "authIntegrated": False,
            "routeGuardIntegrated": False,
            "customerVisibleCount": len(customer_view.get("visiblePackages", [])),
            "engineerVisibleCount": len(engineer_view.get("visiblePackages", [])),
            "adminVisibleCount": len(admin_view.get("visiblePackages", [])),
            "lockedPackageCount": len(admin_view.get("lockedPackages", [])),
            "hiddenPackageCount": len(admin_view.get("hiddenPackages", [])),
            "readOnly": True,
            "controlActionsEnabled": False,
            "certified": False,
            "iec62443Certified": False,
        }

