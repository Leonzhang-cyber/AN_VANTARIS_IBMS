#!/usr/bin/env python3
"""Validate GA-R4 UConsole Airport read-only page binding."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "AN_VANTARIS_IBMS-backend"
PACKAGE_REGISTRY = ROOT / "AN_VANTARIS_IBMS-backend/src/console/module_package_registry.py"
CONSOLE_FRONTEND = ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/console/PlatformOperationsDashboard.vue"
ROUTES = ROOT / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts"
MENU = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts"
AIRPORT_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts"
CONSOLE_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/console.ts"
REPORT = ROOT / "ONE_AIRPORT_GA_R4_UCONSOLE_AIRPORT_READONLY_PAGE_BINDING_REPORT.md"
PASS_MARKER = "ONE_AIRPORT_GA_R4_UCONSOLE_AIRPORT_READONLY_PAGE_BINDING_PASS"

ALLOWED_CHANGED_PREFIXES = (
    "AN_VANTARIS_IBMS-backend/src/console/module_package_registry.py",
    "AN_VANTARIS_IBMS-frontend/src/modules/console/PlatformOperationsDashboard.vue",
    "AN_VANTARIS_IBMS-frontend/src/services/api/console.ts",
    "AN_VANTARIS_ONE/tests/airport_ga_readonly_frontend/",
    "scripts/validation/validate-one-airport-ga-r4-uconsole-binding.py",
    "ONE_AIRPORT_GA_R4_UCONSOLE_AIRPORT_READONLY_PAGE_BINDING_REPORT.md",
)
FORBIDDEN_CHANGED_PREFIXES = (
    "/Volumes/Work/VANTARIS_UFMS_FULL",
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_LINK/",
    "AN_VANTARIS_Contracts/",
    "database/",
    "migrations/",
)
FORBIDDEN_CLIENT_METHODS = (".post", ".put", ".patch", ".delete")
FORBIDDEN_CUSTOMER_TERMS = ("customerAssetIdentifier", '"assetId"', '"deviceId"', "/Users/")


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)


def _changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        paths.update(line for line in _run(command).stdout.splitlines() if line)
    return paths


def _airport_package() -> dict:
    if str(BACKEND_SRC) not in sys.path:
        sys.path.insert(0, str(BACKEND_SRC))
    from src.console.module_package_registry import get_module_package

    package = get_module_package("airport-ga-readonly")
    if not isinstance(package, dict):
        return {}
    return package


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []

    checks.append(("GA-R4 report contains pass marker", REPORT.is_file() and PASS_MARKER in REPORT.read_text(encoding="utf-8")))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to GA-R4 UConsole binding scope", not disallowed))
    checks.append(("Forbidden workspaces untouched", not forbidden))
    if disallowed:
        errors.append(f"changes outside GA-R4 scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    route_text = ROUTES.read_text(encoding="utf-8")
    menu_text = MENU.read_text(encoding="utf-8")
    registry_text = PACKAGE_REGISTRY.read_text(encoding="utf-8")
    console_text = CONSOLE_FRONTEND.read_text(encoding="utf-8")
    airport_client_text = AIRPORT_CLIENT.read_text(encoding="utf-8")
    console_client_text = CONSOLE_CLIENT.read_text(encoding="utf-8")
    combined_visible = "\n".join([route_text, menu_text, registry_text, console_text, console_client_text])

    package = _airport_package()
    customer_entry = package.get("customerEntry", {}) if package else {}
    engineer_entry = package.get("engineerEntry", {}) if package else {}
    role_visibility = package.get("roleVisibility", {}) if package else {}

    checks.append(("GA-R3 route still exists", "/one/airport/overview" in route_text))
    checks.append(("Airport UConsole package entry exists", package.get("packageId") == "airport-ga-readonly"))
    checks.append(("Package entry routes to GA-R3 page", customer_entry.get("route") == "/one/airport/overview"))
    checks.append(("Package entry labels preferred wording", package.get("packageName") == "Airport GA Read-only" and "Airport Industry Solution" == package.get("moduleName")))
    checks.append(("Read-only metadata present", package.get("readOnly") is True and package.get("dbWrite") is False))
    checks.append(("Production activation disabled", package.get("productionActivation") is False))
    checks.append(("Runtime activation disabled", package.get("runtimeActivation") is False))
    checks.append(("Deployment execution disabled", package.get("deploymentExecution") is False))
    checks.append(("Approval execution disabled", package.get("approvalExecution") is False))
    checks.append(("EDGE/LINK runtime call disabled", package.get("edgeLinkRuntimeCall") is False))
    checks.append(("Customer identifier leakage disabled", package.get("customerIdentifierLeakage") is False))
    checks.append(("Customer/Engineer/Admin visibility supported", all(role_visibility.get(role) is True for role in ("customer", "engineer", "admin")) and engineer_entry.get("route") == "/one/airport/overview"))
    checks.append(("UConsole frontend shows safety metadata", all(term in console_text for term in ("productionActivation", "runtimeActivation", "deploymentExecution", "approvalExecution", "edgeLinkRuntimeCall"))))
    checks.append(("No forbidden preferred wording violations", not any(term in combined_visible.lower() for term in ("poc", "mock", "demo", "coming soon"))))
    checks.append(("No frontend-visible customer/local path leakage", not any(term in combined_visible for term in FORBIDDEN_CUSTOMER_TERMS)))
    checks.append(("No Airport non-GET client methods", not any(term in airport_client_text for term in FORBIDDEN_CLIENT_METHODS)))
    airport_package_text = "\n".join(
        line for line in registry_text.splitlines()
        if "airport-ga-readonly" in line or "Airport GA Read-only" in line or "/one/airport/overview" in line
    )
    checks.append(("No deployment/approval execution controls", not any(term in airport_package_text for term in ("Activate", "Deploy", "Sync", "Approve", "Execute", "Create", "Update", "Delete"))))
    checks.append(("No UFMS live repository/source usage", "VANTARIS_UFMS_FULL" not in combined_visible and "/Volumes/Work/VANTARIS_UFMS_FULL" not in combined_visible))

    package_route = _run(["python3", "scripts/validation/validate-one-package-route-enforcement.py"])
    checks.append(("Package route enforcement passes", package_route.returncode == 0 and "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS" in package_route.stdout))
    if package_route.returncode != 0:
        errors.append(package_route.stdout[-4000:] or package_route.stderr[-4000:] or "package route enforcement failed")

    print("ONE_AIRPORT_GA_R4_UCONSOLE_AIRPORT_READONLY_PAGE_BINDING_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_AIRPORT_GA_R4_UCONSOLE_AIRPORT_READONLY_PAGE_BINDING_FAIL")
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
