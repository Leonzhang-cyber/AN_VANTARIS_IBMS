#!/usr/bin/env python3
"""Validate ONE-PROD-GA-R5 final foundation package freeze."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "ONE_PROD_GA_R5_FINAL_FOUNDATION_PACKAGE_FREEZE_PASS"

REPORTS = {
    "R1": (ROOT / "ONE_PROD_GA_R1_FOUNDATION_PACKAGES_SYNC_GATE_REPORT.md", "ONE_PROD_GA_R1_FOUNDATION_PACKAGES_SYNC_GATE_PASS"),
    "R2": (ROOT / "ONE_PROD_GA_R2_FOUNDATION_PACKAGE_CONSOLE_ENTRY_REPORT.md", "ONE_PROD_GA_R2_FOUNDATION_PACKAGE_CONSOLE_ENTRY_PASS"),
    "R3": (ROOT / "ONE_PROD_GA_R3_FOUNDATION_PACKAGE_READONLY_API_HEALTH_REPORT.md", "ONE_PROD_GA_R3_FOUNDATION_PACKAGE_READONLY_API_HEALTH_PASS"),
    "R4": (ROOT / "ONE_PROD_GA_R4_OFFLINE_INSTALL_VERIFY_ROLLBACK_PACKAGE_REPORT.md", "ONE_PROD_GA_R4_OFFLINE_INSTALL_VERIFY_ROLLBACK_PACKAGE_PASS"),
}

FREEZE_DOC = ROOT / "ONE_PROD_GA_R5_FINAL_FOUNDATION_PACKAGE_FREEZE_AND_OPTIONAL_TAG_PLAN.md"
FREEZE_REPORT = ROOT / "ONE_PROD_GA_R5_FINAL_FOUNDATION_PACKAGE_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md"
FREEZE_REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/prod-ga-final-foundation-package-freeze.v1.json"
R3_API_REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/prod-ga-foundation-package-readonly-api.v1.json"
R4_OFFLINE_DIR = ROOT / "deployment/prod-ga/offline-package"
R4_MANIFEST = R4_OFFLINE_DIR / "manifest/prod-ga-foundation-package-manifest.v1.json"
INSTALL_SCRIPT = R4_OFFLINE_DIR / "scripts/install-prod-ga-foundation.sh"
ROLLBACK_SCRIPT = R4_OFFLINE_DIR / "scripts/rollback-prod-ga-foundation.sh"

REQUIRED_PACKAGE_IDS = {"edge", "link", "db", "contracts"}
FORBIDDEN_NAMES = {".env", "node_modules", "dist", "build", ".runtime", "__pycache__"}
FORBIDDEN_SUFFIXES = {".pem", ".key", ".p12", ".crt"}
FALSE_SAFETY_FLAGS = {
    "installExecuted",
    "rollbackExecuted",
    "dbMigrationExecuted",
    "runtimeActivation",
    "edgeStarted",
    "linkStarted",
    "dbWrite",
    "deploymentExecution",
    "ufmsSourceWorkspaceModified",
    "pushPerformed",
    "tagCreated",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return data


def is_forbidden(path: Path) -> bool:
    name = path.name
    if name in FORBIDDEN_NAMES or name.startswith(".env."):
        return True
    return path.suffix in FORBIDDEN_SUFFIXES


def forbidden_scan(paths: list[Path]) -> list[str]:
    matches: list[str] = []
    for base in paths:
        if not base.exists():
            continue
        for candidate in base.rglob("*"):
            if is_forbidden(candidate):
                matches.append(candidate.relative_to(ROOT).as_posix())
    return sorted(matches)


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def script_dry_run(path: Path) -> bool:
    text = read_text(path)
    return path.is_file() and os.access(path, os.X_OK) and 'MODE="dry-run"' in text and "--execute" in text


def main() -> int:
    checks: list[bool] = []

    for stage, (path, marker) in REPORTS.items():
        text = read_text(path)
        checks.append(check(f"{stage} PASS marker exists", marker in text))

    freeze_doc_text = read_text(FREEZE_DOC)
    freeze_report_text = read_text(FREEZE_REPORT)
    registry = load_json(FREEZE_REGISTRY) if FREEZE_REGISTRY.is_file() else {}

    checks.append(check("Final freeze document exists", FREEZE_DOC.is_file()))
    checks.append(check("Final freeze registry exists", FREEZE_REGISTRY.is_file()))
    checks.append(check("Final freeze report exists", FREEZE_REPORT.is_file()))
    checks.append(check("Final PASS marker exists", PASS_MARKER in freeze_doc_text and PASS_MARKER in freeze_report_text and registry.get("passMarker") == PASS_MARKER))

    packages = registry.get("packages", [])
    package_ids = {package.get("packageId") for package in packages}
    package_paths = [ROOT / str(package.get("packagePath", "")) for package in packages]
    checks.append(check("All four package IDs are represented", package_ids == REQUIRED_PACKAGE_IDS, str(sorted(package_ids))))
    checks.append(check("All four package directories exist", all(path.is_dir() for path in package_paths)))
    checks.append(check("All package file counts are greater than zero", all(int(package.get("fileCount", 0)) > 0 for package in packages)))

    actual_counts = {
        package.get("packageId"): sum(1 for _ in (ROOT / str(package.get("packagePath", ""))).rglob("*") if _.is_file())
        for package in packages
    }
    expected_counts = {package.get("packageId"): int(package.get("fileCount", 0)) for package in packages}
    checks.append(check("Registry file counts match package directories", actual_counts == expected_counts, str(actual_counts)))

    matches = forbidden_scan(package_paths)
    checks.append(check("Forbidden scan remains empty", not matches, ", ".join(matches[:10])))
    checks.append(check("Registry forbidden scan claims PASS", registry.get("forbiddenScan", {}).get("status") == "PASS" and registry.get("forbiddenScan", {}).get("matches") == []))

    checks.append(check("R3 GET-only API registry exists", R3_API_REGISTRY.is_file()))
    r3_api = load_json(R3_API_REGISTRY) if R3_API_REGISTRY.is_file() else {}
    checks.append(check("R3 API registry has only GET endpoint contracts", all(endpoint.get("method") == "GET" for endpoint in r3_api.get("endpoints", []))))
    checks.append(check("R4 offline package exists", R4_OFFLINE_DIR.is_dir() and R4_MANIFEST.is_file()))
    checks.append(check("Install script remains dry-run by default", script_dry_run(INSTALL_SCRIPT)))
    checks.append(check("Rollback script remains dry-run by default", script_dry_run(ROLLBACK_SCRIPT)))

    safety = registry.get("safety", {})
    checks.append(check("No push/tag claim is made", safety.get("pushPerformed") is False and safety.get("tagCreated") is False and registry.get("optionalTagPlan", {}).get("tagCreated") is False))
    checks.append(check("No install/rollback/DB/runtime execution claim is made", all(safety.get(flag) is False for flag in FALSE_SAFETY_FLAGS)))
    checks.append(check("Optional tag plan is documented but not executed", registry.get("optionalTagPlan", {}).get("tagName") == "one-prod-ga-foundation-packages-local-freeze-20260622"))

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

