#!/usr/bin/env python3
"""Validate A8-01 read-only frontend skeleton foundation."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/read-only-frontend-skeleton.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/read_only_frontend_skeleton"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/read_only_frontend_skeleton.py"
AIRPORT_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-frontend-skeleton.v1.json"
RUNNER = ROOT / "scripts/validation/_run_a8_01_airport_read_only_frontend_skeleton.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/read_only_frontend_skeleton/",
    "AN_VANTARIS_ONE/registries/read-only-frontend-skeleton.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/read_only_frontend_skeleton.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-frontend-skeleton.v1.json",
    "AN_VANTARIS_ONE/tests/read_only_frontend_skeleton/",
    "scripts/validation/validate-one-airport-read-only-frontend-skeleton.py",
    "scripts/validation/_run_a8_01_airport_read_only_frontend_skeleton.py",
    "ONE_AIRPORT_A8_01_READ_ONLY_FRONTEND_SKELETON_FOUNDATION_REPORT.md",
)
FORBIDDEN_IMPORT_PREFIXES = ("sqlalchemy", "flask", "fastapi", "requests", "urllib", "socket", "src.ufms", "src.umms", "react", "vue")
FORBIDDEN_PATHS = (
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_LINK/",
    "AN_VANTARIS_Contracts/",
    "AN_VANTARIS_IBMS-frontend/",
    "AN_VANTARIS_IBMS-backend/src/routes/",
    "AN_VANTARIS_IBMS-backend/src/api/",
    "database/",
    "migrations/",
    "UFMS/",
    "UMMS/",
)
EXPECTED_SUMMARY = {
    "pageSkeletonCount": 8,
    "routeSkeletonCount": 8,
    "componentSkeletonCount": 24,
    "dataBindingSkeletonCount": 8,
    "cardSkeletonCount": 8,
    "queueSkeletonCount": 8,
    "frontendReadinessGateCount": 15,
    "passedGateCount": 15,
    "blockingGateFailureCount": 0,
    "staticOnlyPageCount": 8,
    "readOnlyPageCount": 8,
    "productionEnabledPageCount": 0,
    "liveApiCallEnabledPageCount": 0,
    "dataMutationEnabledPageCount": 0,
    "productionRouteEnabledCount": 0,
    "liveApiCallEnabledBindingCount": 0,
    "mockDataAllowedBindingCount": 8,
    "projectionBindingRequiredCount": 8,
    "a7ReadOnlyApiRouteImplementationAllowed": True,
    "a6FrontendSkeletonPhaseAllowed": True,
    "frontendSkeletonPhaseAllowed": True,
    "productionFrontendAllowed": False,
    "frontendEnabled": False,
    "apiEnabled": False,
    "databaseWriteCount": 0,
    "canonicalWriteCount": 0,
    "decisionWriteCount": 0,
    "approvalWriteCount": 0,
    "auditWriteCount": 0,
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
    skeleton = _load_json(AIRPORT_PROJECTION)
    summary = skeleton.get("summary", {})
    checks.append(("Implementation status frozen", skeleton.get("implementationStatus") == "READ_ONLY_FRONTEND_SKELETON_FOUNDATION_COMPLETE"))
    checks.append(("Readiness outcome frozen", skeleton.get("readinessOutcome") == "READ_ONLY_FRONTEND_SKELETON_READY_FOR_FUTURE_UI_IMPLEMENTATION"))
    checks.append(("Expected summary freeze", all(summary.get(key) == value for key, value in EXPECTED_SUMMARY.items())))
    checks.append(("Eight page skeletons", len(skeleton.get("pageSkeletons", [])) == 8))
    checks.append(("Eight route skeletons", len(skeleton.get("routeSkeletons", [])) == 8))
    checks.append(("Twenty-four component skeletons", len(skeleton.get("componentSkeletons", [])) == 24))
    checks.append(("Eight data binding skeletons", len(skeleton.get("dataBindingSkeletons", [])) == 8))
    checks.append(("Eight card skeletons", len(skeleton.get("cardSkeletons", [])) == 8))
    checks.append(("Eight queue skeletons", len(skeleton.get("queueSkeletons", [])) == 8))
    checks.append(("Fifteen frontend readiness gates", len(skeleton.get("frontendReadinessGates", [])) == 15))
    checks.append(("All readiness gates pass", all(gate.get("status") == "PASS" for gate in skeleton.get("frontendReadinessGates", []))))
    checks.append(("Pages static read-only disabled", all(item.get("staticOnly") is True and item.get("readOnly") is True and item.get("productionEnabled") is False and item.get("liveApiCallEnabled") is False and item.get("dataMutationEnabled") is False for item in skeleton.get("pageSkeletons", []))))
    checks.append(("Routes production disabled", all(item.get("productionRouteEnabled") is False for item in skeleton.get("routeSkeletons", []))))
    checks.append(("Bindings projection-bound no live API", all(item.get("liveApiCallEnabled") is False and item.get("mockDataAllowed") is True and item.get("projectionBindingRequired") is True for item in skeleton.get("dataBindingSkeletons", []))))
    serialized = json.dumps(skeleton, sort_keys=True)
    checks.append(("No customer identifier text leakage", "customerAssetIdentifier" not in serialized and "assetId" not in serialized and "deviceId" not in serialized))


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    checks.append(("Registry exists", REGISTRY.is_file()))
    checks.append(("Generic package exists", GENERIC_DIR.is_dir()))
    checks.append(("Airport frontend skeleton module exists", AIRPORT_MODULE.is_file()))
    checks.append(("Airport frontend skeleton artifact exists", AIRPORT_PROJECTION.is_file()))
    checks.append(("Deterministic runner exists", RUNNER.is_file()))
    if REGISTRY.is_file():
        registry = _load_json(REGISTRY)
        checks.append(("Registry cross-industry", registry.get("crossIndustry") is True))
        checks.append(("Registry not airport-specific", registry.get("airportSpecific") is False))
        checks.append(("Registry API disabled", registry.get("apiEnabled") is False))
        checks.append(("Registry frontend disabled", registry.get("frontendEnabled") is False))
        checks.append(("Registry frontend skeleton phase allowed", registry.get("frontendSkeletonPhaseAllowed") is True))
        checks.append(("Registry production frontend disabled", registry.get("productionFrontendAllowed") is False))

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

    changed = _changed_paths()
    disallowed = [path for path in changed if path and not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)]
    checks.append(("Changes within A8-01 allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")
    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))
    if forbidden_touched:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden_touched))}")

    env = {**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")}
    test_proc = _run(["python3", "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/read_only_frontend_skeleton", "-p", "test_*.py"], env=env)
    checks.append(("Focused A8-01 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-4000:] or test_proc.stderr[-4000:] or "focused A8-01 tests failed")
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
            errors.append("read-only frontend skeleton generation is not byte-identical")

    print("ONE_AIRPORT_A8_01_READ_ONLY_FRONTEND_SKELETON_FOUNDATION_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("READ_ONLY_FRONTEND_SKELETON_FOUNDATION_COMPLETE")
    print("READ_ONLY_FRONTEND_SKELETON_READY_FOR_FUTURE_UI_IMPLEMENTATION")
    print("ONE_AIRPORT_A8_01_READ_ONLY_FRONTEND_SKELETON_FOUNDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
