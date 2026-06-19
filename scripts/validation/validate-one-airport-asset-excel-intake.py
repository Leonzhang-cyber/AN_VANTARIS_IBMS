#!/usr/bin/env python3
"""Validate airport asset Excel intake profile implementation."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/airport_intake"
TESTS_DIR = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/airport_intake"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/airport-asset-excel-intake-profile.v1.json"
RUNNER = ROOT / "scripts/validation/run-one-airport-asset-excel-intake.py"
VALIDATOR = ROOT / "scripts/validation/validate-one-airport-asset-excel-intake.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_IBMS-backend/src/asset_graph/airport_intake/",
    "AN_VANTARIS_IBMS-backend/tests/asset_graph/airport_intake/",
    "AN_VANTARIS_ONE/registries/airport-asset-excel-intake-profile.v1.json",
    "scripts/validation/run-one-airport-asset-excel-intake.py",
    "scripts/validation/validate-one-airport-asset-excel-intake.py",
)

FORBIDDEN_PATHS = (
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_IBMS-frontend/",
    "database/",
    "migrations/",
    "UFMS/",
)

FORBIDDEN_IMPORTS = ("sqlalchemy", "flask", "psycopg", "pymongo", "src.ufms", "src.umms", "src.Iot")
WORKBOOK_PATTERNS = ("Zonewise", "Asset_Database", "Asset Database")


def _run(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False, env=env)


def _changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        paths.update(line for line in _run(command).stdout.splitlines() if line)
    return paths


def _module_imports_forbidden() -> list[str]:
    errors: list[str] = []
    for path in MODULE_DIR.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            if isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            for name in names:
                if any(name.startswith(prefix) for prefix in FORBIDDEN_IMPORTS):
                    errors.append(f"{path.name}: forbidden import {name}")
    return errors


def main() -> int:
    errors: list[str] = []
    checks: list[tuple[str, bool]] = []

    checks.append(("Module directory exists", MODULE_DIR.is_dir()))
    checks.append(("Tests directory exists", TESTS_DIR.is_dir()))
    checks.append(("Runner script exists", RUNNER.is_file()))
    checks.append(("Registry exists", REGISTRY.is_file()))

    tracked_workbook = _run(["git", "ls-files", "*"]).stdout
    workbook_tracked = any(pattern.lower() in tracked_workbook.lower() for pattern in WORKBOOK_PATTERNS)
    checks.append(("Source workbook not tracked", not workbook_tracked))

    changed = _changed_paths()
    disallowed = [path for path in changed if path and not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)]
    checks.append(("Changes within allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")

    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden runtime paths touched", len(forbidden_touched) == 0))

    import_errors = _module_imports_forbidden()
    checks.append(("No DB/ORM/session imports", len(import_errors) == 0))
    errors.extend(import_errors)

    module_text = " ".join(path.read_text(encoding="utf-8") for path in MODULE_DIR.glob("*.py"))
    checks.append(("No provider writes", "InMemoryAssetGraphProvider" not in module_text))
    checks.append(("No public API routes", "blueprint" not in module_text.lower()))
    checks.append(("Maintenance fields separated", "maintenanceExtensionCandidates" in module_text))
    checks.append(("No fabricated points", '"pointCandidateCount": 0' in module_text))

    if REGISTRY.is_file():
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        checks.append(("Registry authority", registry.get("authority") == "ONE-AIRPORT-A1-01"))

    test_count = len(list(TESTS_DIR.glob("test_*.py")))
    checks.append(("Focused tests present", test_count >= 1))

    test_proc = _run(
        [
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "AN_VANTARIS_IBMS-backend/tests/asset_graph/airport_intake",
            "-p",
            "test_*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
    )
    checks.append(("Focused tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-2000:] or test_proc.stderr[-2000:] or "focused tests failed")

    aggregate_sample = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/airport_intake/test_airport_intake.py"
    checks.append(("Aggregate identifier exclusion tested", "aggregate_report_excludes_identifiers" in aggregate_sample.read_text()))

    print("VANTARIS ONE Airport Asset Excel Intake Validation")
    print("=" * 60)
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    all_pass = all(ok for _, ok in checks)
    if errors or not all_pass:
        if not all_pass:
            errors.append("one or more validation checks failed")
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nONE_AIRPORT_ASSET_EXCEL_INTAKE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
