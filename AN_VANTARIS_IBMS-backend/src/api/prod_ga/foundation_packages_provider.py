"""Registry-backed Production GA foundation package read-only provider.

This provider reads the frozen R2 console-entry registry and exposes normalized
package status/health projections for the Production GA API layer. It performs
local filesystem reads only; it does not start runtimes, execute validators,
write to databases, or mutate package/source workspaces.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


R2_REGISTRY = "AN_VANTARIS_ONE/registries/prod-ga-foundation-package-console-entry.v1.json"
R2_REPORT = "ONE_PROD_GA_R2_FOUNDATION_PACKAGE_CONSOLE_ENTRY_REPORT.md"

PUBLIC_PACKAGE_IDS = {
    "AN_VANTARIS_EDGE": "edge",
    "AN_VANTARIS_LINK": "link",
    "AN_VANTARIS_DB": "db",
    "AN_VANTARIS_Contracts": "contracts",
}

FORBIDDEN_NAMES = {
    ".env",
    "node_modules",
    "dist",
    "build",
    ".runtime",
    "__pycache__",
}
FORBIDDEN_SUFFIXES = {
    ".pem",
    ".key",
    ".p12",
    ".crt",
}


def repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "AN_VANTARIS_ONE").is_dir() and (parent / "AN_VANTARIS_IBMS-backend").is_dir():
            return parent
    raise RuntimeError("VANTARIS ONE repository root not found")


def _load_json(relative_path: str) -> dict[str, Any]:
    path = repo_root() / relative_path
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{relative_path} must contain a JSON object")
    return data


def _is_forbidden(path: Path) -> bool:
    name = path.name
    if name in FORBIDDEN_NAMES:
        return True
    if name.startswith(".env."):
        return True
    return path.suffix in FORBIDDEN_SUFFIXES


def scan_forbidden_package_files() -> list[str]:
    registry = _load_json(R2_REGISTRY)
    root = repo_root()
    matches: list[str] = []
    for package in registry.get("packages", []):
        package_path = root / str(package.get("packagePath", ""))
        if not package_path.exists():
            continue
        for candidate in package_path.rglob("*"):
            if _is_forbidden(candidate):
                matches.append(candidate.relative_to(root).as_posix())
    return sorted(matches)


def _normalized_package(package: dict[str, Any]) -> dict[str, Any]:
    package_name = str(package["packageName"])
    public_id = PUBLIC_PACKAGE_IDS[package_name]
    return {
        "packageId": public_id,
        "packageName": package_name,
        "packagePath": package["packagePath"],
        "fileCount": int(package["fileCount"]),
        "consoleVisible": bool(package["consoleVisible"]),
        "readOnly": True,
        "runtimeEnabled": False,
        "deploymentEnabled": False,
        "installActionsEnabled": False,
        "writeActionsEnabled": False,
        "dbMigrationEnabled": False,
        "sourceWorkspaceModified": False,
        "status": package.get("status", "synced"),
    }


def list_foundation_packages() -> list[dict[str, Any]]:
    registry = _load_json(R2_REGISTRY)
    packages = [_normalized_package(package) for package in registry.get("packages", [])]
    packages.sort(key=lambda item: ["edge", "link", "db", "contracts"].index(item["packageId"]))
    return packages


def get_foundation_package(package_id: str) -> dict[str, Any] | None:
    normalized_id = package_id.strip().lower()
    for package in list_foundation_packages():
        if package["packageId"] == normalized_id:
            return package
    return None


def _r2_report_contains(marker: str) -> bool:
    report_path = repo_root() / R2_REPORT
    if not report_path.is_file():
        return False
    return marker in report_path.read_text(encoding="utf-8")


def foundation_package_health() -> dict[str, Any]:
    packages = list_foundation_packages()
    forbidden_matches = scan_forbidden_package_files()
    all_packages_ready = (
        len(packages) == 4
        and all(package["fileCount"] > 0 for package in packages)
        and all(package["readOnly"] is True for package in packages)
        and all(package["runtimeEnabled"] is False for package in packages)
        and all(package["deploymentEnabled"] is False for package in packages)
        and all(package["installActionsEnabled"] is False for package in packages)
        and all(package["writeActionsEnabled"] is False for package in packages)
        and all(package["dbMigrationEnabled"] is False for package in packages)
        and all(package["sourceWorkspaceModified"] is False for package in packages)
    )
    forbidden_ok = len(forbidden_matches) == 0
    boundary_ok = _r2_report_contains("ONE_BOUNDARY_BASELINE_PASS")
    route_ok = _r2_report_contains("ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS")
    overall_ok = all_packages_ready and forbidden_ok and boundary_ok and route_ok
    return {
        "overallStatus": "PASS" if overall_ok else "ATTENTION_REQUIRED",
        "packageCount": len(packages),
        "packages": packages,
        "forbiddenScanStatus": "PASS" if forbidden_ok else "FAIL",
        "forbiddenMatches": forbidden_matches,
        "boundaryStatus": "PASS" if boundary_ok else "UNKNOWN",
        "routeEnforcementStatus": "PASS" if route_ok else "UNKNOWN",
        "runtimeActivation": False,
        "productionActivation": False,
        "dbWrite": False,
        "deploymentExecution": False,
    }


def list_foundation_packages_response() -> dict[str, Any]:
    packages = list_foundation_packages()
    return {
        "packages": packages,
        "packageCount": len(packages),
        "readOnly": True,
        "runtimeActivation": False,
        "productionActivation": False,
        "dbWrite": False,
        "deploymentExecution": False,
    }

