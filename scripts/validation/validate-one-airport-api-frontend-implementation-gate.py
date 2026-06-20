#!/usr/bin/env python3
"""Validate A6-02 API / Frontend implementation readiness release gate."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/api-frontend-implementation-readiness-gate.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/api_frontend_implementation_gate"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/api_frontend_implementation_gate.py"
AIRPORT_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-api-frontend-implementation-readiness-gate.v1.json"
RUNNER = ROOT / "scripts/validation/_run_a6_02_api_frontend_implementation_gate.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/api_frontend_implementation_gate/",
    "AN_VANTARIS_ONE/registries/api-frontend-implementation-readiness-gate.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/api_frontend_implementation_gate.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-api-frontend-implementation-readiness-gate.v1.json",
    "AN_VANTARIS_ONE/tests/api_frontend_implementation_gate/",
    "scripts/validation/validate-one-airport-api-frontend-implementation-gate.py",
    "scripts/validation/_run_a6_02_api_frontend_implementation_gate.py",
    "ONE_AIRPORT_A6_02_API_FRONTEND_IMPLEMENTATION_READINESS_RELEASE_GATE_REPORT.md",
)
FORBIDDEN_IMPORT_PREFIXES = ("sqlalchemy", "flask", "requests", "urllib", "socket", "src.ufms", "src.umms")
FORBIDDEN_TEXT = ("blueprint", "api.route", "live alarm timestamp", "last-seen", "last_seen", "packet loss")
FORBIDDEN_PATHS = ("AN_VANTARIS_EDGE/", "AN_VANTARIS_LINK/", "AN_VANTARIS_Contracts/", "AN_VANTARIS_IBMS-frontend/", "database/", "migrations/", "UFMS/", "UMMS/")

EXPECTED_SUMMARY = {
    "apiEndpointCandidateCount": 8,
    "readOnlyEndpointCandidateCount": 8,
    "frontendPageCandidateCount": 8,
    "frontendRouteCandidateCount": 8,
    "dataBindingContractCount": 15,
    "cardBindingContractCount": 8,
    "queueBindingContractCount": 8,
    "authPolicyRequiredCount": 8,
    "contractReadinessGateCount": 15,
    "contractPassedGateCount": 15,
    "implementationReleaseGateCount": 16,
    "implementationPassedGateCount": 16,
    "blockingGateFailureCount": 0,
    "a5HandoffAllowed": True,
    "a4ReleaseAllowed": True,
    "a3ReleaseAllowed": True,
    "apiSkeletonPhaseAllowed": True,
    "frontendSkeletonPhaseAllowed": True,
    "productionApiAllowed": False,
    "productionFrontendAllowed": False,
    "databaseWriteAllowed": False,
    "runtimeActivationAllowed": False,
    "productionActivationAllowed": False,
    "pushAllowed": False,
    "apiEnabled": False,
    "frontendEnabled": False,
    "databaseWriteCount": 0,
    "canonicalWriteCount": 0,
    "decisionWriteCount": 0,
    "approvalWriteCount": 0,
    "auditWriteCount": 0,
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
    gate = _load_json(AIRPORT_PROJECTION)
    summary = gate.get("summary", {})
    decision = gate.get("implementationDecision", {})
    checks.append(("Implementation status frozen", gate.get("implementationStatus") == "API_FRONTEND_IMPLEMENTATION_READINESS_RELEASE_GATE_COMPLETE"))
    checks.append(("Readiness outcome frozen", gate.get("readinessOutcome") == "API_FRONTEND_READY_FOR_READ_ONLY_SKELETON_PLANNING"))
    checks.append(("Expected summary freeze", all(summary.get(key) == value for key, value in EXPECTED_SUMMARY.items())))
    checks.append(("Sixteen release gates", len(gate.get("releaseGateResults", [])) == 16))
    checks.append(("All release gates pass", all(item.get("status") == "PASS" for item in gate.get("releaseGateResults", []))))
    checks.append(("Dependency gates pass", len(gate.get("dependencyGateResults", [])) == 3 and all(item.get("status") == "PASS" for item in gate.get("dependencyGateResults", []))))
    checks.append(("Coverage matrix pass", all(item.get("status") == "PASS" for item in gate.get("contractCoverageMatrix", []))))
    checks.append(("Boundary matrix pass", all(item.get("status") == "PASS" for item in gate.get("implementationBoundaryMatrix", []))))
    checks.append(("Skeleton planning allowed", decision.get("apiSkeletonPhaseAllowed") is True and decision.get("frontendSkeletonPhaseAllowed") is True))
    checks.append(("Production implementation blocked", decision.get("productionApiAllowed") is False and decision.get("productionFrontendAllowed") is False and decision.get("databaseWriteAllowed") is False and decision.get("runtimeActivationAllowed") is False and decision.get("productionActivationAllowed") is False and decision.get("pushAllowed") is False))
    serialized = json.dumps(gate, sort_keys=True)
    checks.append(("No customer identifier text leakage", "customerAssetIdentifier" not in serialized and "assetId" not in serialized and "deviceId" not in serialized))


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    checks.append(("Registry exists", REGISTRY.is_file()))
    checks.append(("Generic package exists", GENERIC_DIR.is_dir()))
    checks.append(("Airport implementation gate module exists", AIRPORT_MODULE.is_file()))
    checks.append(("Airport implementation gate artifact exists", AIRPORT_PROJECTION.is_file()))
    checks.append(("Deterministic runner exists", RUNNER.is_file()))
    if REGISTRY.is_file():
        registry = _load_json(REGISTRY)
        checks.append(("Registry cross-industry", registry.get("crossIndustry") is True))
        checks.append(("Registry not airport-specific", registry.get("airportSpecific") is False))
        checks.append(("Registry API disabled", registry.get("apiEnabled") is False))
        checks.append(("Registry frontend disabled", registry.get("frontendEnabled") is False))
        checks.append(("Registry skeleton allowed only", registry.get("apiSkeletonPhaseAllowed") is True and registry.get("frontendSkeletonPhaseAllowed") is True and registry.get("productionApiAllowed") is False and registry.get("productionFrontendAllowed") is False))

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
    checks.append(("Changes within A6-02 allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")
    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))
    if forbidden_touched:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden_touched))}")

    env = {**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")}
    test_proc = _run(["python3", "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/api_frontend_implementation_gate", "-p", "test_*.py"], env=env)
    checks.append(("Focused A6-02 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-4000:] or test_proc.stderr[-4000:] or "focused A6-02 tests failed")
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
            errors.append("API / Frontend implementation gate generation is not byte-identical")

    print("ONE_AIRPORT_A6_02_API_FRONTEND_IMPLEMENTATION_READINESS_RELEASE_GATE_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("API_FRONTEND_IMPLEMENTATION_READINESS_RELEASE_GATE_COMPLETE")
    print("API_FRONTEND_READY_FOR_READ_ONLY_SKELETON_PLANNING")
    print("ONE_AIRPORT_A6_02_API_FRONTEND_IMPLEMENTATION_READINESS_RELEASE_GATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
