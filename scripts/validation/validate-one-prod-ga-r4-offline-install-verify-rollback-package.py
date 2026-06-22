#!/usr/bin/env python3
"""Validate ONE-PROD-GA-R4 offline install/verify/rollback scaffold."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "ONE_PROD_GA_R4_OFFLINE_INSTALL_VERIFY_ROLLBACK_PACKAGE_PASS"
R3_PASS_MARKER = "ONE_PROD_GA_R3_FOUNDATION_PACKAGE_READONLY_API_HEALTH_PASS"

R3_REPORT = ROOT / "ONE_PROD_GA_R3_FOUNDATION_PACKAGE_READONLY_API_HEALTH_REPORT.md"
R4_REPORT = ROOT / "ONE_PROD_GA_R4_OFFLINE_INSTALL_VERIFY_ROLLBACK_PACKAGE_REPORT.md"
OFFLINE_DIR = ROOT / "deployment/prod-ga/offline-package"
MANIFEST = OFFLINE_DIR / "manifest/prod-ga-foundation-package-manifest.v1.json"
INSTALL_SCRIPT = OFFLINE_DIR / "scripts/install-prod-ga-foundation.sh"
VERIFY_SCRIPT = OFFLINE_DIR / "scripts/verify-prod-ga-foundation.sh"
ROLLBACK_SCRIPT = OFFLINE_DIR / "scripts/rollback-prod-ga-foundation.sh"

REQUIRED_PACKAGE_IDS = {"edge", "link", "db", "contracts"}
REQUIRED_PACKAGE_NAMES = {
    "AN_VANTARIS_EDGE",
    "AN_VANTARIS_LINK",
    "AN_VANTARIS_DB",
    "AN_VANTARIS_Contracts",
}
FALSE_SAFETY_FLAGS = {
    "installExecuted",
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
FORBIDDEN_NAMES = {".env", "node_modules", "dist", "build", ".runtime", "__pycache__"}
FORBIDDEN_SUFFIXES = {".pem", ".key", ".p12", ".crt"}


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


def script_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def main() -> int:
    checks: list[bool] = []
    r3_text = R3_REPORT.read_text(encoding="utf-8") if R3_REPORT.is_file() else ""
    r4_text = R4_REPORT.read_text(encoding="utf-8") if R4_REPORT.is_file() else ""
    manifest = load_json(MANIFEST) if MANIFEST.is_file() else {}

    checks.append(check("R3 PASS marker exists", R3_PASS_MARKER in r3_text))
    checks.append(check("Offline package directory exists", OFFLINE_DIR.is_dir()))
    checks.append(check("Manifest exists", MANIFEST.is_file()))
    checks.append(check("R4 report exists", R4_REPORT.is_file()))
    checks.append(check("R4 PASS marker exists", PASS_MARKER in r4_text and manifest.get("passMarker") == PASS_MARKER))

    for label, path in {
        "install script": INSTALL_SCRIPT,
        "verify script": VERIFY_SCRIPT,
        "rollback script": ROLLBACK_SCRIPT,
    }.items():
        checks.append(check(f"{label} exists", path.is_file()))
        checks.append(check(f"{label} is executable", os.access(path, os.X_OK)))

    install_text = script_text(INSTALL_SCRIPT)
    verify_text = script_text(VERIFY_SCRIPT)
    rollback_text = script_text(ROLLBACK_SCRIPT)
    checks.append(check("Install script defaults to dry-run", "MODE=\"dry-run\"" in install_text and "--execute" in install_text))
    checks.append(check("Verify script is read-only", "find \"$absolute_path\" -type f" in verify_text and "rm " not in verify_text))
    checks.append(check("Rollback script is dry-run by default and does not delete by default", "MODE=\"dry-run\"" in rollback_text and "No files are deleted" in rollback_text and "rm " not in rollback_text))

    packages = manifest.get("packages", [])
    package_ids = {package.get("packageId") for package in packages}
    package_names = {package.get("packageName") for package in packages}
    checks.append(check("Manifest references EDGE/LINK/DB/Contracts package IDs", package_ids == REQUIRED_PACKAGE_IDS, str(sorted(package_ids))))
    checks.append(check("Manifest references EDGE/LINK/DB/Contracts package names", package_names == REQUIRED_PACKAGE_NAMES, str(sorted(package_names))))
    checks.append(check("All manifest package file counts are > 0", all(int(package.get("fileCount", 0)) > 0 for package in packages)))

    package_paths = [ROOT / str(package.get("packagePath", "")) for package in packages]
    checks.append(check("All referenced package directories exist", all(path.is_dir() for path in package_paths)))
    matches = forbidden_scan(package_paths + [OFFLINE_DIR])
    checks.append(check("Forbidden scan remains empty", not matches, ", ".join(matches[:10])))

    safety = manifest.get("safety", {})
    checks.append(check("No install/DB/runtime/deployment execution occurred", all(safety.get(flag) is False for flag in FALSE_SAFETY_FLAGS)))

    install_manifest = manifest.get("scripts", {}).get("install", {})
    verify_manifest = manifest.get("scripts", {}).get("verify", {})
    rollback_manifest = manifest.get("scripts", {}).get("rollback", {})
    checks.append(check("Manifest declares install dry-run default", install_manifest.get("dryRunDefault") is True and install_manifest.get("requiresExplicitExecuteFlag") is True))
    checks.append(check("Manifest declares verify read-only", verify_manifest.get("dryRunDefault") is True and verify_manifest.get("readOnly") is True))
    checks.append(check("Manifest declares rollback dry-run/no default delete", rollback_manifest.get("dryRunDefault") is True and rollback_manifest.get("deletesFilesByDefault") is False))

    verify_ok, verify_output = run_validator([str(VERIFY_SCRIPT)], "PASS: verification completed read-only")
    checks.append(check("Verify script passes read-only package checks", verify_ok))
    if not verify_ok:
        print(verify_output)

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

