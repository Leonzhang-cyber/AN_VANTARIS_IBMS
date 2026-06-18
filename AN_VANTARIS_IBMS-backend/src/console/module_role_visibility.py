"""UConsole role visibility policy skeleton (read-only local preview)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple


SUPPORTED_ROLES: Tuple[str, ...] = ("customer", "engineer", "admin")


def _normalize_role(role: str) -> str:
    return str(role or "").strip().lower()


def _role_label(role: str) -> str:
    if role == "customer":
        return "Customer User"
    if role == "engineer":
        return "Engineer User"
    return "Admin User"


def _role_modes(role: str) -> Tuple[List[str], List[str]]:
    if role == "customer":
        return (["customer-application"], ["engineer-diagnostics", "admin-package-center"])
    if role == "engineer":
        return (["engineer-diagnostics", "customer-application"], ["admin-package-center"])
    return (["customer-application", "engineer-diagnostics", "admin-package-center"], [])


def _entry_item(
    *,
    role: str,
    package: Dict[str, Any],
    entry: Dict[str, Any],
    entry_mode: str,
    context_only: bool = False,
) -> Dict[str, Any]:
    entitled = bool(package.get("entitled"))
    installed = bool(package.get("installed"))
    package_enabled = bool(package.get("enabled"))
    package_visible = bool(package.get("visible"))
    entry_enabled = bool(entry.get("enabled"))
    entry_visible = bool(entry.get("visible"))
    locked_reason = entry.get("lockedReason") or package.get("lockedReason")

    if context_only:
        effective_visible = entry_visible
        effective_enabled = False
    else:
        effective_visible = entry_visible and package_visible
        effective_enabled = entry_enabled and package_enabled

    state = "visible"
    if locked_reason or not entitled or not installed:
        state = "locked"
    elif not effective_visible:
        state = "hidden"
    elif not effective_enabled:
        state = "disabled"

    if state in {"hidden", "disabled"} and not locked_reason:
        if not entitled:
            locked_reason = "Package not entitled"
        elif not installed:
            locked_reason = "Package not installed"
        elif not effective_visible:
            locked_reason = "Hidden by role visibility policy"
        elif not effective_enabled:
            locked_reason = "Entry disabled in local skeleton state"

    return {
        "role": role,
        "packageId": package.get("packageId"),
        "packageCode": package.get("packageCode"),
        "packageName": package.get("packageName"),
        "moduleId": package.get("moduleId"),
        "moduleName": package.get("moduleName"),
        "entryMode": entry_mode,
        "label": entry.get("label", ""),
        "route": entry.get("route", ""),
        "visible": bool(effective_visible),
        "enabled": bool(effective_enabled),
        "entitled": entitled,
        "installed": installed,
        "contextOnly": bool(context_only),
        "lockedReason": locked_reason,
        "state": state,
        "readOnly": True,
        "controlActionsEnabled": False,
        "realRbacIntegrated": False,
        "authIntegrated": False,
        "routeGuardIntegrated": False,
        "certified": False,
        "iec62443Certified": False,
    }


def _role_entries(role: str, packages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for package in packages:
        customer_entry = deepcopy(package.get("customerEntry", {}))
        engineer_entry = deepcopy(package.get("engineerEntry", {}))
        admin_entry = deepcopy(package.get("adminEntry", {}))

        if role == "customer":
            rows.append(
                _entry_item(
                    role=role,
                    package=package,
                    entry=customer_entry,
                    entry_mode="customer-application",
                )
            )
            continue

        if role == "engineer":
            rows.append(
                _entry_item(
                    role=role,
                    package=package,
                    entry=engineer_entry,
                    entry_mode="engineer-diagnostics",
                )
            )
            # Engineer can see customer application state as context preview.
            rows.append(
                _entry_item(
                    role=role,
                    package=package,
                    entry=customer_entry,
                    entry_mode="customer-application",
                    context_only=True,
                )
            )
            continue

        # admin
        rows.append(
            _entry_item(
                role=role,
                package=package,
                entry=customer_entry,
                entry_mode="customer-application",
            )
        )
        rows.append(
            _entry_item(
                role=role,
                package=package,
                entry=engineer_entry,
                entry_mode="engineer-diagnostics",
            )
        )
        rows.append(
            _entry_item(
                role=role,
                package=package,
                entry=admin_entry,
                entry_mode="admin-package-center",
            )
        )
    return rows


def get_supported_roles() -> List[str]:
    return list(SUPPORTED_ROLES)


def get_role_entry_view(role: str, packages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    role_key = _normalize_role(role)
    if role_key not in SUPPORTED_ROLES:
        return None

    entries = _role_entries(role_key, packages or [])
    visible = [item for item in entries if str(item.get("state")) == "visible"]
    locked = [item for item in entries if str(item.get("state")) == "locked"]
    hidden = [item for item in entries if str(item.get("state")) in {"hidden", "disabled"}]

    return {
        "role": role_key,
        "roleLabel": _role_label(role_key),
        "entryMode": "local-skeleton-role-entry-view",
        "visiblePackages": visible,
        "lockedPackages": locked,
        "hiddenPackages": hidden,
        "readOnly": True,
        "controlActionsEnabled": False,
        "realRbacIntegrated": False,
        "authIntegrated": False,
        "routeGuardIntegrated": False,
        "certified": False,
        "iec62443Certified": False,
    }


def get_role_menu_preview(role: str, packages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    role_key = _normalize_role(role)
    if role_key not in SUPPORTED_ROLES:
        return None

    rows = _role_entries(role_key, packages or [])
    return {
        "role": role_key,
        "roleLabel": _role_label(role_key),
        "menuPreviewMode": "local-skeleton-role-menu-preview",
        "items": rows,
        "readOnly": True,
        "realRbacIntegrated": False,
        "authIntegrated": False,
        "routeGuardIntegrated": False,
        "certified": False,
        "iec62443Certified": False,
    }


def get_hidden_or_locked_reasons(role: str, packages: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
    role_key = _normalize_role(role)
    if role_key not in SUPPORTED_ROLES:
        return None

    rows = _role_entries(role_key, packages or [])
    reasons: List[Dict[str, Any]] = []
    for row in rows:
        state = str(row.get("state", ""))
        if state not in {"locked", "hidden", "disabled"}:
            continue
        reasons.append(
            {
                "role": role_key,
                "packageCode": row.get("packageCode"),
                "moduleName": row.get("moduleName"),
                "entryMode": row.get("entryMode"),
                "reason": row.get("lockedReason") or "Hidden by role visibility policy",
                "state": state,
                "certified": False,
                "iec62443Certified": False,
            }
        )
    return reasons


def get_role_visibility_policy(role: str, packages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    role_key = _normalize_role(role)
    if role_key not in SUPPORTED_ROLES:
        return None

    allowed_modes, hidden_modes = _role_modes(role_key)
    entry_view = get_role_entry_view(role_key, packages or []) or {}
    menu_preview = get_role_menu_preview(role_key, packages or []) or {}
    reasons = get_hidden_or_locked_reasons(role_key, packages or []) or []

    return {
        "role": role_key,
        "roleLabel": _role_label(role_key),
        "visibilityMode": "local-skeleton-role-visibility",
        "realRbacIntegrated": False,
        "authIntegrated": False,
        "routeGuardIntegrated": False,
        "readOnly": True,
        "allowedEntryModes": allowed_modes,
        "hiddenEntryModes": hidden_modes,
        "visiblePackages": entry_view.get("visiblePackages", []),
        "lockedPackages": entry_view.get("lockedPackages", []),
        "hiddenPackages": entry_view.get("hiddenPackages", []),
        "menuPreview": menu_preview.get("items", []),
        "hiddenOrLockedReasons": reasons,
        "limitations": [
            "Local role visibility preview only.",
            "Real RBAC/auth integration is not enabled.",
            "Route guard enforcement is not enabled.",
        ],
        "certified": False,
        "iec62443Certified": False,
    }

