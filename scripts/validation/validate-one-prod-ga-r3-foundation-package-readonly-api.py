#!/usr/bin/env python3
"""Validate ONE-PROD-GA-R3 foundation package read-only API + health gate."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "ONE_PROD_GA_R3_FOUNDATION_PACKAGE_READONLY_API_HEALTH_PASS"
R2_PASS_MARKER = "ONE_PROD_GA_R2_FOUNDATION_PACKAGE_CONSOLE_ENTRY_PASS"

R2_REPORT = ROOT / "ONE_PROD_GA_R2_FOUNDATION_PACKAGE_CONSOLE_ENTRY_REPORT.md"
R3_REPORT = ROOT / "ONE_PROD_GA_R3_FOUNDATION_PACKAGE_READONLY_API_HEALTH_REPORT.md"
R3_REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/prod-ga-foundation-package-readonly-api.v1.json"
API_ROUTE = ROOT / "AN_VANTARIS_IBMS-backend/src/api/prod_ga/foundation_packages_api.py"
PROVIDER = ROOT / "AN_VANTARIS_IBMS-backend/src/api/prod_ga/foundation_packages_provider.py"

REQUIRED_ENDPOINTS = {
    "/v1/one/prod-ga/foundation-packages",
    "/v1/one/prod-ga/foundation-packages/health",
    "/v1/one/prod-ga/foundation-packages/<string:package_id>",
}
REQUIRED_PUBLIC_ENDPOINTS = {
    "/api/v1/one/prod-ga/foundation-packages",
    "/api/v1/one/prod-ga/foundation-packages/health",
    "/api/v1/one/prod-ga/foundation-packages/{packageId}",
}
REQUIRED_PACKAGE_IDS = {"edge", "link", "db", "contracts"}
MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
HEALTH_FIELDS = {
    "overallStatus",
    "packageCount",
    "packages",
    "forbiddenScanStatus",
    "boundaryStatus",
    "routeEnforcementStatus",
    "runtimeActivation",
    "productionActivation",
    "dbWrite",
    "deploymentExecution",
}
FALSE_FLAGS = {
    "runtimeEnabled",
    "deploymentEnabled",
    "installActionsEnabled",
    "writeActionsEnabled",
    "dbMigrationEnabled",
    "sourceWorkspaceModified",
}
HEALTH_FALSE_FLAGS = {
    "runtimeActivation",
    "productionActivation",
    "dbWrite",
    "deploymentExecution",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return data


def load_provider():
    spec = importlib.util.spec_from_file_location("prod_ga_foundation_packages_provider", PROVIDER)
    if spec is None or spec.loader is None:
        raise AssertionError("Unable to load foundation package provider")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_validator(command: list[str], expected_marker: str) -> tuple[bool, str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.setdefault("PYTHONPATH", "AN_VANTARIS_ONE")
    proc = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, check=False)
    output = "\n".join(part for part in [proc.stdout, proc.stderr] if part)
    return proc.returncode == 0 and expected_marker in output, output


def check(name: str, condition: bool, details: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    suffix = f" - {details}" if details else ""
    print(f"[{status}] {name}{suffix}")
    return condition


def main() -> int:
    checks: list[bool] = []

    r2_report_text = R2_REPORT.read_text(encoding="utf-8") if R2_REPORT.is_file() else ""
    r3_report_text = R3_REPORT.read_text(encoding="utf-8") if R3_REPORT.is_file() else ""
    route_text = API_ROUTE.read_text(encoding="utf-8") if API_ROUTE.is_file() else ""

    registry = load_json(R3_REGISTRY) if R3_REGISTRY.is_file() else {}
    provider = load_provider() if PROVIDER.is_file() else None
    packages = provider.list_foundation_packages() if provider else []
    health = provider.foundation_package_health() if provider else {}

    checks.append(check("R2 PASS marker exists", R2_PASS_MARKER in r2_report_text))
    checks.append(check("R3 registry exists", R3_REGISTRY.is_file()))
    checks.append(check("R3 report exists", R3_REPORT.is_file()))
    checks.append(check("R3 PASS marker exists", PASS_MARKER in r3_report_text and registry.get("passMarker") == PASS_MARKER))

    checks.append(check("Backend route file exists", API_ROUTE.is_file()))
    checks.append(check("Provider file exists", PROVIDER.is_file()))
    checks.append(check("Required Flask GET endpoints are present", REQUIRED_ENDPOINTS.issubset(set(token for token in REQUIRED_ENDPOINTS if token in route_text))))
    registry_endpoints = {item.get("path") for item in registry.get("endpoints", []) if item.get("method") == "GET"}
    checks.append(check("Required public endpoint contracts are present", REQUIRED_PUBLIC_ENDPOINTS.issubset(registry_endpoints)))
    mutating_found = [
        method
        for method in MUTATING_METHODS
        if f'methods=["{method}"]' in route_text or f"methods=['{method}']" in route_text
    ]
    checks.append(check("No mutating prod-ga foundation endpoints added", not mutating_found, ", ".join(mutating_found)))

    package_ids = {package.get("packageId") for package in packages}
    checks.append(check("All 4 package IDs are represented", package_ids == REQUIRED_PACKAGE_IDS, str(sorted(package_ids))))
    checks.append(check("All packages have fileCount > 0", all(int(package.get("fileCount", 0)) > 0 for package in packages)))
    checks.append(check("All packages are consoleVisible", all(package.get("consoleVisible") is True for package in packages)))
    checks.append(check("All packages are readOnly", all(package.get("readOnly") is True for package in packages)))
    checks.append(check("All package runtime/deployment/write/install/db flags are false", all(package.get(flag) is False for package in packages for flag in FALSE_FLAGS)))

    checks.append(check("Health response fields are defined", HEALTH_FIELDS.issubset(set(health.keys()))))
    checks.append(check("Health execution flags are false", all(health.get(flag) is False for flag in HEALTH_FALSE_FLAGS)))
    checks.append(check("Forbidden package scan remains empty", health.get("forbiddenScanStatus") == "PASS" and not health.get("forbiddenMatches")))
    checks.append(check("Health package count is 4", health.get("packageCount") == 4))
    checks.append(check("Health status is PASS", health.get("overallStatus") == "PASS"))

    safety = registry.get("safety", {})
    checks.append(check("UFMS source workspace not modified", safety.get("ufmsSourceWorkspaceModified") is False))
    checks.append(check("No push/no tag claimed", safety.get("pushPerformed") is False and safety.get("tagCreated") is False))

    route_ok, route_output = run_validator(
        ["python3", "scripts/validation/validate-one-package-route-enforcement.py"],
        "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS",
    )
    checks.append(check("Package route enforcement still passes", route_ok))
    if not route_ok:
        print(route_output)

    boundary_ok, boundary_output = run_validator(
        ["python3", "scripts/validation/validate-one-boundaries.py"],
        "ONE_BOUNDARY_BASELINE_PASS",
    )
    checks.append(check("Boundary baseline still passes", boundary_ok))
    if not boundary_ok:
        print(boundary_output)

    if all(checks):
        print(PASS_MARKER)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

