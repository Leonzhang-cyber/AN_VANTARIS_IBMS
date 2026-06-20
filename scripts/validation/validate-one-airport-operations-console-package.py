#!/usr/bin/env python3
"""Validate A5-01 read-only Airport Operations Console Package foundation."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/read-only-operations-console-package.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/operations_console_package"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/operations_console_package.py"
AIRPORT_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-operations-console-package.v1.json"
RUNNER = ROOT / "scripts/validation/_run_a5_01_airport_operations_console_package.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/operations_console_package/",
    "AN_VANTARIS_ONE/registries/read-only-operations-console-package.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/operations_console_package.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-operations-console-package.v1.json",
    "AN_VANTARIS_ONE/tests/operations_console_package/",
    "scripts/validation/validate-one-airport-operations-console-package.py",
    "scripts/validation/_run_a5_01_airport_operations_console_package.py",
    "ONE_AIRPORT_A5_01_READ_ONLY_AIRPORT_OPERATIONS_CONSOLE_PACKAGE_FOUNDATION_REPORT.md",
)
FORBIDDEN_IMPORT_PREFIXES = ("sqlalchemy", "flask", "requests", "urllib", "socket", "src.ufms", "src.umms")
FORBIDDEN_TEXT = ("blueprint", "api.route", "react", "live alarm timestamp", "last-seen", "last_seen", "packet loss")
FORBIDDEN_PATHS = (
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_LINK/",
    "AN_VANTARIS_Contracts/",
    "AN_VANTARIS_IBMS-frontend/",
    "database/",
    "migrations/",
    "UFMS/",
    "UMMS/",
)

EXPECTED_SUMMARY = {
    "pageDefinitionCount": 8,
    "navigationGroupCount": 3,
    "consoleCardCount": 8,
    "packageDataSourceCount": 15,
    "packageReadinessGateCount": 12,
    "sourceSystemCandidateCount": 5,
    "alarmEventCandidateCount": 5,
    "faultCaseCandidateCount": 5,
    "workOrderIntentCandidateCount": 5,
    "investigationCaseCount": 5,
    "operationsRowCount": 5,
    "decisionItemCount": 46,
    "queueRowCount": 46,
    "policyGuardResultCount": 46,
    "auditPreviewCount": 46,
    "totalDeviceEvidenceCount": 470,
    "pendingDecisionCount": 46,
    "blockingDecisionCount": 45,
    "runtimeObservedCount": 0,
    "runtimeAlarmObservedCount": 0,
    "ufmsFaultCaseCreatedCount": 0,
    "workOrderIntentCreatedCount": 0,
    "workOrderCreatedCount": 0,
    "evidenceCenterWriteCount": 0,
    "ummsWriteCount": 0,
    "oneWorkManagementWriteCount": 0,
    "decisionWriteCount": 0,
    "approvalWriteCount": 0,
    "auditWriteCount": 0,
    "canonicalWriteCount": 0,
    "databaseWriteCount": 0,
    "apiEnabled": False,
    "frontendEnabled": False,
    "runtimeActivationAllowed": False,
    "productionActivationAllowed": False,
    "pushAllowed": False,
    "containsCustomerAssetIdentifiers": False,
    "crossIndustry": True,
    "airportSpecific": False,
}


def _run(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False, env=env)


def _changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (["git", "diff", "--name-only", "HEAD"], ["git", "diff", "--cached", "--name-only"], ["git", "ls-files", "--others", "--exclude-standard"]):
        paths.update(line for line in _run(command).stdout.splitlines() if line)
    return paths


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _append_projection_checks(checks: list[tuple[str, bool]]) -> None:
    package = _load_json(AIRPORT_PROJECTION)
    summary = package.get("summary", {})
    checks.append(("Implementation status frozen", package.get("implementationStatus") == "READ_ONLY_AIRPORT_OPERATIONS_CONSOLE_PACKAGE_FOUNDATION_COMPLETE"))
    checks.append(("Readiness outcome frozen", package.get("readinessOutcome") == "AIRPORT_OPERATIONS_CONSOLE_PACKAGE_READY_FOR_READ_ONLY_CONSUMPTION"))
    checks.append(("Expected summary freeze", all(summary.get(key) == value for key, value in EXPECTED_SUMMARY.items())))
    checks.append(("Eight page definitions", len(package.get("pageDefinitions", [])) == 8))
    checks.append(("Three navigation groups", len(package.get("navigationGroups", [])) == 3))
    checks.append(("Eight console cards", len(package.get("consoleCards", [])) == 8))
    checks.append(("Fifteen data sources", len(package.get("packageDataSources", [])) == 15))
    checks.append(("Twelve readiness gates", len(package.get("packageReadinessGates", [])) == 12))
    checks.append(("All gates pass", all(gate.get("status") == "PASS" for gate in package.get("packageReadinessGates", []))))
    checks.append(("All data sources read-only", all(source.get("readOnly") is True for source in package.get("packageDataSources", []))))
    checks.append(("All data source boundaries disabled", all(source.get("apiEnabled") is False and source.get("frontendEnabled") is False and source.get("databaseAccessEnabled") is False for source in package.get("packageDataSources", []))))
    checks.append(("Default pagination", package.get("defaultPage", {}).get("pageSize") == 25 and package.get("defaultPage", {}).get("orderBy") == ["pageKey", "pageId"]))
    serialized = json.dumps(package, sort_keys=True)
    checks.append(("No customer identifier text leakage", "customerAssetIdentifier" not in serialized and "assetId" not in serialized and "deviceId" not in serialized))


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    checks.append(("Registry exists", REGISTRY.is_file()))
    checks.append(("Generic package exists", GENERIC_DIR.is_dir()))
    checks.append(("Airport package module exists", AIRPORT_MODULE.is_file()))
    checks.append(("Airport package artifact exists", AIRPORT_PROJECTION.is_file()))
    checks.append(("Deterministic runner exists", RUNNER.is_file()))
    if REGISTRY.is_file():
        registry = _load_json(REGISTRY)
        checks.append(("Registry cross-industry", registry.get("crossIndustry") is True))
        checks.append(("Registry not airport-specific", registry.get("airportSpecific") is False))
        checks.append(("Registry DB disabled", registry.get("databaseAccessEnabled") is False))
        checks.append(("Registry API disabled", registry.get("apiEnabled") is False))
        checks.append(("Registry frontend disabled", registry.get("frontendEnabled") is False))

    owned_py = list(GENERIC_DIR.glob("*.py")) + [AIRPORT_MODULE, RUNNER]
    import_errors: list[str] = []
    for path in owned_py:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            for name in names:
                if any(name.startswith(prefix) for prefix in FORBIDDEN_IMPORT_PREFIXES):
                    import_errors.append(f"{path.relative_to(ROOT)}: {name}")
    checks.append(("No forbidden runtime imports", len(import_errors) == 0))
    errors.extend(import_errors)
    text_errors = [token for token in FORBIDDEN_TEXT if token in "\n".join(p.read_text(encoding="utf-8") for p in owned_py).lower()]
    checks.append(("No forbidden runtime/API/frontend text", len(text_errors) == 0))
    if text_errors:
        errors.append(f"forbidden text present: {', '.join(text_errors)}")

    changed = _changed_paths()
    disallowed = [path for path in changed if path and not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)]
    checks.append(("Changes within A5-01 allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")
    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))
    if forbidden_touched:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden_touched))}")

    env = {**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")}
    test_proc = _run(["python3", "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/operations_console_package", "-p", "test_*.py"], env=env)
    checks.append(("Focused A5-01 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-4000:] or test_proc.stderr[-4000:] or "focused A5-01 tests failed")
    runner_proc = _run(["python3", str(RUNNER)], env=env)
    checks.append(("Deterministic runner pass", runner_proc.returncode == 0))
    if runner_proc.returncode != 0:
        errors.append(runner_proc.stdout[-4000:] or runner_proc.stderr[-4000:] or "runner failed")
    boundary_proc = _run(["python3", "scripts/validation/validate-one-boundaries.py"], env=env)
    checks.append(("Boundary validator baseline pass", boundary_proc.returncode == 0 and "ONE_BOUNDARY_BASELINE_PASS" in boundary_proc.stdout))
    if boundary_proc.returncode != 0 or "ONE_BOUNDARY_BASELINE_PASS" not in boundary_proc.stdout:
        errors.append(boundary_proc.stdout[-4000:] or boundary_proc.stderr[-4000:] or "boundary validator failed")

    if AIRPORT_PROJECTION.is_file():
        _append_projection_checks(checks)
        before = AIRPORT_PROJECTION.read_text(encoding="utf-8")
        second = _run(["python3", str(RUNNER)], env=env)
        after = AIRPORT_PROJECTION.read_text(encoding="utf-8")
        checks.append(("Repeated generation byte-identical", second.returncode == 0 and before == after))
        if second.returncode != 0 or before != after:
            errors.append("operations console package generation is not byte-identical")

    print("ONE_AIRPORT_A5_01_READ_ONLY_AIRPORT_OPERATIONS_CONSOLE_PACKAGE_FOUNDATION_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("READ_ONLY_AIRPORT_OPERATIONS_CONSOLE_PACKAGE_FOUNDATION_COMPLETE")
    print("AIRPORT_OPERATIONS_CONSOLE_PACKAGE_READY_FOR_READ_ONLY_CONSUMPTION")
    print("ONE_AIRPORT_A5_01_READ_ONLY_AIRPORT_OPERATIONS_CONSOLE_PACKAGE_FOUNDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
