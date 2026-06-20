#!/usr/bin/env python3
"""Build the static VANTARIS ONE frontend route and menu inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


ROUTE_SOURCE = Path("AN_VANTARIS_IBMS-frontend/src/router/routes.ts")
MENU_SOURCE = Path("AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts")


def stable_id(prefix: str, *parts: object) -> str:
    value = "|".join(str(part) for part in parts)
    return f"{prefix}-{hashlib.sha256(value.encode()).hexdigest()[:12].upper()}"


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def array_body(text: str, marker: str) -> tuple[str, int]:
    marker_pos = text.find(marker)
    if marker_pos < 0:
        raise ValueError(f"declaration not found: {marker}")
    assignment = text.find("=", marker_pos)
    start = text.find("[", assignment if assignment >= 0 else marker_pos)
    if start < 0:
        raise ValueError(f"array start not found: {marker}")
    depth = 0
    quote = ""
    escaped = False
    for pos in range(start, len(text)):
        char = text[pos]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            continue
        if char in {"'", '"', "`"}:
            quote = char
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return text[start + 1:pos], start + 1
    raise ValueError(f"unterminated array: {marker}")


def object_spans(text: str, base_offset: int = 0, top_level_only: bool = True) -> list[tuple[str, int, int]]:
    spans: list[tuple[str, int, int]] = []
    stack: list[int] = []
    bracket_depth = 0
    quote = ""
    escaped = False
    for pos, char in enumerate(text):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            continue
        if char in {"'", '"', "`"}:
            quote = char
        elif char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth -= 1
        elif char == "{":
            stack.append(pos)
        elif char == "}" and stack:
            start = stack.pop()
            if (not top_level_only) or (not stack and bracket_depth == 0):
                spans.append((text[start:pos + 1], base_offset + start, base_offset + pos + 1))
    return spans


def string_prop(block: str, key: str) -> str:
    match = re.search(rf"\b{re.escape(key)}\s*:\s*(['\"])(.*?)\1", block, re.DOTALL)
    return match.group(2) if match else ""


def symbol_prop(block: str, key: str) -> str:
    match = re.search(rf"\b{re.escape(key)}\s*:\s*([A-Za-z_$][\w$]*)", block)
    return match.group(1) if match else ""


def bool_prop(block: str, key: str) -> bool | None:
    match = re.search(rf"\b{re.escape(key)}\s*:\s*(true|false)", block)
    return match.group(1) == "true" if match else None


def string_array_prop(block: str, key: str) -> list[str]:
    match = re.search(rf"\b{re.escape(key)}\s*:\s*\[(.*?)\]", block, re.DOTALL)
    if not match:
        return []
    return re.findall(r"['\"]([^'\"]+)['\"]", match.group(1))


def package_for_route(path: str) -> tuple[str, str]:
    mappings = [
        ("/system/audit", "PKG-GOVERNANCE-SECURITY", "Governance & Security"),
        ("/system/permissions", "PKG-GOVERNANCE-SECURITY", "Governance & Security"),
        ("/system/integration", "PKG-UNIFIED-DATA-MODEL", "Integration Governance"),
        ("/system", "PKG-UCORE", "UCore"),
        ("/iot", "PKG-ASSET-GRAPH", "ONE Asset Graph"),
        ("/did", "PKG-GOVERNANCE-SECURITY", "Governance & Security"),
        ("/modeling", "PKG-NEXUS-AI", "Nexus AI"),
        ("/console", "PKG-UCONSOLE", "UConsole"),
        ("/assets", "PKG-ASSET-GRAPH", "ONE Asset Graph"),
        ("/ucde", "PKG-EVIDENCE-CENTER", "Evidence Center"),
        ("/uesg", "PKG-UESG", "UESG"),
        ("/umms", "PKG-UMMS", "UMMS"),
        ("/uedge", "PKG-EDGE", "AN_VANTARIS_EDGE"),
        ("/one/airport", "PKG-UCONSOLE", "UConsole"),
        ("/reports", "PKG-REPORTS", "Reports"),
        ("/dashboard", "PKG-UCONSOLE", "UConsole"),
    ]
    for prefix, package, owner in mappings:
        if path.startswith(prefix):
            return package, owner
    if path == "/login":
        return "PKG-GOVERNANCE-SECURITY", "Governance & Security"
    if path in {"/403", "/forbidden", "/:pathMatch(.*)*", "/"}:
        return "PKG-UCONSOLE", "UConsole"
    return "", "UNRESOLVED"


def target_permissions(path: str) -> list[str]:
    if path in {"/login", "/403", "/forbidden", "/:pathMatch(.*)*", "/"}:
        return []
    if path.startswith("/system/audit"):
        return ["audit:read"]
    if path.startswith("/system/permissions"):
        return ["security:admin"]
    if path.startswith("/system/integration"):
        return ["integration:configure"]
    if path.startswith("/system"):
        return ["context:read"]
    if path.startswith("/iot") or path.startswith("/assets"):
        return ["asset:read"]
    if path.startswith("/did"):
        return ["security:read"]
    if path.startswith("/modeling"):
        return ["ai:use"]
    if path.startswith("/console") or path.startswith("/dashboard"):
        return ["platform:read"]
    if path.startswith("/ucde"):
        return ["evidence:read"]
    if path.startswith("/uesg"):
        return ["esg:read"]
    if path.startswith("/umms"):
        return ["maintenance:read"]
    if path.startswith("/uedge/diagnostics"):
        return ["edge:diagnose"]
    if path.startswith("/uedge"):
        return ["edge:read"]
    if path.startswith("/one/airport"):
        return ["platform:read"]
    if path.startswith("/reports"):
        return ["report:read"]
    return []


def api_dependencies(path: str) -> list[str]:
    mappings = [
        ("/system/audit", ["/api/v1/audit"]),
        ("/system/permissions", ["/api/v1/security"]),
        ("/system/integration", ["/api/v1/integration"]),
        ("/system", ["/api/v1/context", "/api/v1/packages"]),
        ("/iot", ["/api/v1/assets", "/api/v1/integration"]),
        ("/did", ["/api/v1/security", "/api/v1/trust"]),
        ("/modeling", ["/api/v1/ai", "/api/v1/models"]),
        ("/console", ["/api/v1/console", "/api/v1/packages", "/api/v1/health"]),
        ("/assets", ["/api/v1/assets"]),
        ("/ucde", ["/api/v1/evidence"]),
        ("/uesg", ["/api/v1/esg"]),
        ("/umms", ["/api/v1/mms", "/api/v1/work"]),
        ("/uedge", ["/api/v1/edge", "/api/v1/health"]),
        ("/one/airport", []),
        ("/reports", ["/api/v1/reports"]),
        ("/dashboard", ["/api/v1/console"]),
    ]
    for prefix, values in mappings:
        if path.startswith(prefix):
            return values
    return []


def target_access(path: str, component: str, requires_auth: bool | None) -> str:
    if path == "/login":
        return "PUBLIC_ROUTE"
    if path in {"/403", "/forbidden", "/:pathMatch(.*)*"}:
        return "STATUS_ROUTE"
    if path == "/":
        return "STATUS_ROUTE"
    if "Diagnostics" in component:
        return "DIAGNOSTIC_ROUTE"
    if path.startswith("/system"):
        return "ADMIN_ROUTE"
    if requires_auth is False:
        return "PUBLIC_ROUTE"
    return "BUSINESS_ROUTE"


def parse_routes(root: Path) -> tuple[list[dict], list[dict]]:
    path = root / ROUTE_SOURCE
    text = path.read_text(encoding="utf-8")
    body, base = array_body(text, "export const routes")
    routes: list[dict] = []
    unresolved: list[dict] = []
    for block, start, _end in object_spans(body, base, top_level_only=True):
        route_path = string_prop(block, "path")
        if not route_path:
            unresolved.append({
                "declarationId": stable_id("UNRESOLVED-ROUTE", ROUTE_SOURCE, start),
                "sourcePath": ROUTE_SOURCE.as_posix(),
                "line": line_number(text, start),
                "declarationType": "ROUTE_OBJECT_WITHOUT_STATIC_PATH",
                "evidence": re.sub(r"\s+", " ", block)[:240],
                "requiredReview": "Resolve dynamic route path without executing frontend code.",
                "scannerConfidence": "MEDIUM",
            })
            continue
        name = string_prop(block, "name")
        component = symbol_prop(block, "component")
        redirect = string_prop(block, "redirect")
        requires_auth = bool_prop(block, "requiresAuth")
        current_permissions = string_array_prop(block, "permissions")
        package, owner = package_for_route(route_path)
        is_placeholder = bool(
            "Placeholder" in component or redirect or route_path in {"/", "/403", "/forbidden", "/:pathMatch(.*)*"}
        )
        runtime = "PLACEHOLDER" if is_placeholder else "PRODUCTION"
        if requires_auth is True and current_permissions:
            guard = "PERMISSION_AWARE"
        elif requires_auth is True:
            guard = "AUTHENTICATION_ONLY"
        elif requires_auth is False or redirect:
            guard = "NO_GUARD"
        else:
            guard = "INHERITED_UNKNOWN"
        target = target_access(route_path, component, requires_auth)
        routes.append({
            "frontendRouteId": stable_id("FROUTE", ROUTE_SOURCE, route_path, name, redirect),
            "sourcePath": ROUTE_SOURCE.as_posix(),
            "line": line_number(text, start),
            "symbol": name or redirect or "anonymous-route",
            "routePath": route_path,
            "routeName": name,
            "component": component or (f"REDIRECT:{redirect}" if redirect else ""),
            "parentRoute": "",
            "runtimeClass": runtime,
            "currentPackageId": "",
            "targetPackageId": package,
            "owningModule": owner,
            "currentPermissionMetadata": current_permissions,
            "targetPermissions": target_permissions(route_path),
            "currentEntitlementMetadata": "NOT_DECLARED",
            "currentPackageEnabledMetadata": "NOT_DECLARED",
            "currentHealthMetadata": "NOT_DECLARED",
            "directUrlCurrentlyAddressable": True,
            "currentGuardClass": guard,
            "currentMenuPresence": False,
            "targetMenuPresence": target not in {"PUBLIC_ROUTE", "STATUS_ROUTE", "LOCK_PAGE", "DENY"},
            "targetAccessClass": target,
            "backendApiDependencies": api_dependencies(route_path),
            "legacyStatus": "PLACEHOLDER" if is_placeholder else "CURRENT_TARGET",
            "compatibilityRequirement": "PRESERVE_ROUTE_UNTIL_TARGET_POLICY_RUNTIME_IS_VALIDATED",
            "remediationWorkstream": "WS-P0-PACKAGE-ENFORCEMENT",
            "proposedTaskId": "ONE-A5-P0-07",
            "scannerConfidence": "HIGH",
            "notes": [
                "Static route declaration extracted without importing or executing Vue code.",
                "Current package, entitlement, enablement and health metadata are not declared in the router.",
            ],
        })
    return routes, unresolved


def parse_menu(root: Path) -> tuple[list[dict], list[dict]]:
    path = root / MENU_SOURCE
    text = path.read_text(encoding="utf-8")
    body, base = array_body(text, "export const fallbackMenuItems")
    all_spans = object_spans(body, base, top_level_only=False)
    menu_entries: list[dict] = []
    unresolved: list[dict] = []
    for block, start, end in all_spans:
        label = string_prop(block, "label")
        route_path = string_prop(block, "path")
        menu_id = string_prop(block, "id")
        if not label or not route_path:
            continue
        depth = 1
        for _outer, outer_start, outer_end in all_spans:
            if outer_start < start and end < outer_end:
                depth += 1
        package, owner = package_for_route(route_path)
        menu_entries.append({
            "menuEntryId": stable_id("MENU", MENU_SOURCE, menu_id, route_path, start),
            "sourcePath": MENU_SOURCE.as_posix(),
            "line": line_number(text, start),
            "label": label,
            "l1": label if depth == 1 else "",
            "l2": label if depth == 2 else "",
            "targetL3Workspace": "",
            "routePath": route_path,
            "packageId": package,
            "owningModule": owner,
            "currentRoleVisibility": [],
            "currentPermissionMetadata": string_prop(block, "permission"),
            "currentEntitlementMetadata": "NOT_DECLARED",
            "currentEnabledMetadata": "NOT_DECLARED",
            "currentHealthMetadata": "NOT_DECLARED",
            "staticFallback": True,
            "currentVisibilityClass": "STATIC_ALWAYS_PRESENT",
            "targetVisibilityClass": (
                "VISIBLE_FOR_DIAGNOSTICS" if "diagnostic" in route_path
                else "ADMIN_ONLY" if route_path.startswith("/system")
                else "VISIBLE_WHEN_AUTHORIZED"
            ),
            "legacyStatus": "LEGACY_COMPATIBILITY_REQUIRED",
            "scannerConfidence": "HIGH",
            "notes": [
                f"Static fallback menu depth L{depth}.",
                "L3 is represented as workspace content, not a left-navigation level.",
            ],
        })
    return menu_entries, unresolved


def build(root: Path) -> dict:
    routes, route_unresolved = parse_routes(root)
    menus, menu_unresolved = parse_menu(root)
    menu_paths = {row["routePath"] for row in menus}
    for route in routes:
        route["currentMenuPresence"] = route["routePath"] in menu_paths
    routes.sort(key=lambda row: row["frontendRouteId"])
    menus.sort(key=lambda row: row["menuEntryId"])
    unresolved = sorted(route_unresolved + menu_unresolved, key=lambda row: row["declarationId"])
    route_package = Counter(row["targetPackageId"] or "UNRESOLVED" for row in routes)
    route_owner = Counter(row["owningModule"] for row in routes)
    route_access = Counter(row["targetAccessClass"] for row in routes)
    menu_package = Counter(row["packageId"] or "UNRESOLVED" for row in menus)
    route_summary = {
        "totalRoutes": len(routes),
        "productionRoutes": sum(row["runtimeClass"] == "PRODUCTION" for row in routes),
        "legacyRoutes": sum(row["runtimeClass"] == "LEGACY" for row in routes),
        "placeholderRoutes": sum(row["runtimeClass"] == "PLACEHOLDER" for row in routes),
        "testOnlyRoutes": sum(row["runtimeClass"] == "TEST_ONLY" for row in routes),
        "routesWithCurrentAuthGuard": sum(row["currentGuardClass"] in {"AUTHENTICATION_ONLY", "PERMISSION_AWARE", "PACKAGE_AWARE", "FULL_POLICY"} for row in routes),
        "routesWithCurrentPermissionMetadata": sum(bool(row["currentPermissionMetadata"]) for row in routes),
        "routesWithCurrentPackageMetadata": sum(bool(row["currentPackageId"]) for row in routes),
        "routesCurrentlyDirectAddressable": sum(row["directUrlCurrentlyAddressable"] for row in routes),
        "routesRequiringPackageMetadata": sum(not row["currentPackageId"] and row["targetAccessClass"] not in {"PUBLIC_ROUTE", "STATUS_ROUTE"} for row in routes),
        "routesRequiringPermissionMetadata": sum(not row["currentPermissionMetadata"] and bool(row["targetPermissions"]) for row in routes),
        "routesRequiringDirectUrlEnforcement": sum(row["directUrlCurrentlyAddressable"] and row["targetAccessClass"] not in {"PUBLIC_ROUTE", "STATUS_ROUTE"} for row in routes),
        "routesRequiringMultipleControls": sum(
            not row["currentPackageId"] and not row["currentPermissionMetadata"] and bool(row["targetPermissions"])
            for row in routes
        ),
        "routesByPackage": dict(sorted(route_package.items())),
        "routesByOwningModule": dict(sorted(route_owner.items())),
        "routesByTargetAccessClass": dict(sorted(route_access.items())),
    }
    menu_summary = {
        "totalMenuEntries": len(menus),
        "staticFallbackEntries": sum(row["staticFallback"] for row in menus),
        "entriesWithRoleMetadata": sum(bool(row["currentRoleVisibility"]) for row in menus),
        "entriesWithPermissionMetadata": sum(bool(row["currentPermissionMetadata"]) for row in menus),
        "entriesWithPackageMetadata": sum(bool(row["packageId"]) for row in menus),
        "l1Entries": sum(bool(row["l1"]) for row in menus),
        "l2Entries": sum(bool(row["l2"]) for row in menus),
        "l3EntriesIncorrectlyInLeftNavigation": sum(bool(row["targetL3Workspace"]) for row in menus),
        "entriesRequiringMigration": sum(row["legacyStatus"] in {"LEGACY_MIGRATE", "LEGACY_COMPATIBILITY_REQUIRED", "REMOVE_LATER", "REVIEW_REQUIRED"} for row in menus),
        "entriesByPackage": dict(sorted(menu_package.items())),
    }
    return {
        "registryName": "VANTARIS ONE Frontend Route Inventory",
        "registryVersion": "1.0.0",
        "authority": "ONE-A5-P0-06",
        "status": "FROZEN_FRONTEND_ROUTE_BASELINE",
        "generatedAtPolicy": "STATIC_ARCHITECTURE_BASELINE",
        "sourceRoots": [
            "AN_VANTARIS_IBMS-frontend/src/router",
            "AN_VANTARIS_IBMS-frontend/src/services/menu",
            "AN_VANTARIS_IBMS-frontend/src/components",
            "AN_VANTARIS_IBMS-frontend/src/modules",
        ],
        "extractionPolicy": {
            "mode": "STATIC_TEXT_ANALYSIS",
            "frontendExecution": False,
            "nodeDependency": False,
            "dynamicDeclarationPolicy": "RETAIN_IN_UNRESOLVED_DECLARATIONS",
            "l3NavigationPolicy": "WORKSPACE_CONTENT_NOT_LEFT_NAVIGATION",
        },
        "summary": {"routes": route_summary, "menus": menu_summary},
        "routes": routes,
        "menuEntries": menus,
        "unresolvedDeclarations": unresolved,
    }


def serialize(value: dict) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    default_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--format", choices=["json"], default="json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    value = build(root)
    output = args.output
    if output and not output.is_absolute():
        output = root / output
    default_output = root / "AN_VANTARIS_ONE/registries/frontend-route-inventory.v1.json"
    check_path = output or default_output
    rendered = serialize(value)
    if args.check:
        if not check_path.is_file() or check_path.read_text(encoding="utf-8") != rendered:
            print(f"frontend route inventory differs: {check_path}", file=sys.stderr)
            return 1
        print("ONE_FRONTEND_ROUTE_INVENTORY_CHECK_PASS")
        return 0
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
