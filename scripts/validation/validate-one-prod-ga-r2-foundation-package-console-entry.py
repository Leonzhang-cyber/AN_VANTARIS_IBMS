#!/usr/bin/env python3
"""Validate ONE PROD GA R2 foundation package console entry."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/prod-ga-foundation-package-console-entry.v1.json"
REPORT = ROOT / "ONE_PROD_GA_R2_FOUNDATION_PACKAGE_CONSOLE_ENTRY_REPORT.md"
R1_REPORT = ROOT / "ONE_PROD_GA_R1_FOUNDATION_PACKAGES_SYNC_GATE_REPORT.md"
PASS_MARKER = "ONE_PROD_GA_R2_FOUNDATION_PACKAGE_CONSOLE_ENTRY_PASS"
R1_PASS_MARKER = "ONE_PROD_GA_R1_FOUNDATION_PACKAGES_SYNC_GATE_PASS"

REQUIRED_PACKAGES = {
    "AN_VANTARIS_EDGE",
    "AN_VANTARIS_LINK",
    "AN_VANTARIS_DB",
    "AN_VANTARIS_Contracts",
}

FALSE_FLAGS = (
    "runtimeEnabled",
    "deploymentEnabled",
    "dbMigrationEnabled",
    "writeActionsEnabled",
    "installActionsEnabled",
    "sourceWorkspaceModified",
)

FORBIDDEN_NAMES = {
    ".env",
    "node_modules",
    "dist",
    "build",
    ".runtime",
    "__pycache__",
}

FORBIDDEN_SUFFIXES = (
    ".pem",
    ".key",
    ".p12",
    ".crt",
)


def main() -> int:
    errors: list[str] = []

    errors.extend(_validate_r1_marker())
    registry = _load_registry(errors)
    errors.extend(_validate_report())

    if registry:
        errors.extend(_validate_registry(registry))
        errors.extend(_validate_packages(registry))

    errors.extend(_validate_optional_gate("scripts/validation/validate-one-package-route-enforcement.py"))
    errors.extend(_validate_optional_gate("scripts/validation/validate-one-boundaries.py"))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(PASS_MARKER)
    return 0


def _validate_r1_marker() -> list[str]:
    if not R1_REPORT.exists():
        return ["R1 report missing"]
    if R1_PASS_MARKER not in R1_REPORT.read_text(encoding="utf-8"):
        return ["R1 PASS marker missing"]
    return []


def _load_registry(errors: list[str]) -> dict | None:
    if not REGISTRY.exists():
        errors.append("R2 registry missing")
        return None
    try:
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"R2 registry invalid JSON: {exc}")
        return None


def _validate_report() -> list[str]:
    if not REPORT.exists():
        return ["R2 report missing"]
    report = REPORT.read_text(encoding="utf-8")
    required = [
        PASS_MARKER,
        "No runtime activation",
        "No DB migration execution",
        "No install script execution",
        "No write actions",
        "No deployment actions",
        "No UFMS source workspace modification",
    ]
    return [f"R2 report missing phrase: {phrase}" for phrase in required if phrase not in report]


def _validate_registry(registry: dict) -> list[str]:
    errors: list[str] = []
    if registry.get("passMarker") != PASS_MARKER:
        errors.append("registry PASS marker mismatch")
    if registry.get("sourceWorkspaceModified") is not False:
        errors.append("registry sourceWorkspaceModified must be false")

    safety = registry.get("safety", {})
    for flag in (
        "runtimeEnabled",
        "deploymentEnabled",
        "dbMigrationEnabled",
        "writeActionsEnabled",
        "installActionsEnabled",
        "ufmsSourceWorkspaceModified",
    ):
        if safety.get(flag) is not False:
            errors.append(f"registry safety.{flag} must be false")

    console_entry = registry.get("consoleEntry", {})
    if console_entry.get("visible") is not True:
        errors.append("consoleEntry.visible must be true")
    if console_entry.get("readOnly") is not True:
        errors.append("consoleEntry.readOnly must be true")
    if console_entry.get("actions") != []:
        errors.append("consoleEntry.actions must be empty")
    return errors


def _validate_packages(registry: dict) -> list[str]:
    errors: list[str] = []
    packages = registry.get("packages", [])
    by_name = {package.get("packageName"): package for package in packages}
    missing = REQUIRED_PACKAGES.difference(by_name)
    if missing:
        errors.append(f"missing package entries: {sorted(missing)}")

    for package_name in sorted(REQUIRED_PACKAGES):
        package = by_name.get(package_name)
        if not package:
            continue
        package_path = ROOT / str(package.get("packagePath", ""))
        if not package_path.exists():
            errors.append(f"{package_name}: package path missing")
            continue

        actual_count = _count_files(package_path)
        if actual_count <= 0:
            errors.append(f"{package_name}: file count must be greater than zero")
        if package.get("fileCount") != actual_count:
            errors.append(
                f"{package_name}: registry fileCount {package.get('fileCount')} != actual {actual_count}"
            )
        if package.get("consoleVisible") is not True:
            errors.append(f"{package_name}: consoleVisible must be true")
        if package.get("readOnly") is not True:
            errors.append(f"{package_name}: readOnly must be true")
        for flag in FALSE_FLAGS:
            if package.get(flag) is not False:
                errors.append(f"{package_name}: {flag} must be false")
        errors.extend(_scan_forbidden(package_path, package_name))

    return errors


def _count_files(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file())


def _scan_forbidden(path: Path, package_name: str) -> list[str]:
    errors: list[str] = []
    for item in path.rglob("*"):
        name = item.name
        if name.startswith(".env"):
            errors.append(f"{package_name}: forbidden env path {item.relative_to(ROOT)}")
        if name in FORBIDDEN_NAMES:
            errors.append(f"{package_name}: forbidden path {item.relative_to(ROOT)}")
        if item.is_file() and name.endswith(FORBIDDEN_SUFFIXES):
            errors.append(f"{package_name}: forbidden secret/cert path {item.relative_to(ROOT)}")
        if "pycache" in name.lower():
            errors.append(f"{package_name}: forbidden pycache path {item.relative_to(ROOT)}")
    return errors


def _validate_optional_gate(relative_script: str) -> list[str]:
    script = ROOT / relative_script
    if not script.exists():
        print(f"SKIP optional validator missing: {relative_script}")
        return []
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    print(result.stdout, end="")
    if result.returncode != 0:
        return [f"optional validator failed: {relative_script}"]
    return []


if __name__ == "__main__":
    raise SystemExit(main())
