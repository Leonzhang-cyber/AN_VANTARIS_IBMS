#!/usr/bin/env python3
"""Validate A7-04 read-only API implementation release gate."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/read-only-api-implementation-release-gate.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/read_only_api_release_gate"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/read_only_api_release_gate.py"
AIRPORT_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-api-implementation-release-gate.v1.json"
RUNNER = ROOT / "scripts/validation/_run_a7_04_airport_read_only_api_release_gate.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/read_only_api_release_gate/",
    "AN_VANTARIS_ONE/registries/read-only-api-implementation-release-gate.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/read_only_api_release_gate.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-api-implementation-release-gate.v1.json",
    "AN_VANTARIS_ONE/tests/read_only_api_release_gate/",
    "scripts/validation/validate-one-airport-read-only-api-release-gate.py",
    "scripts/validation/_run_a7_04_airport_read_only_api_release_gate.py",
    "ONE_AIRPORT_A7_04_READ_ONLY_API_IMPLEMENTATION_RELEASE_GATE_REPORT.md",
)
FORBIDDEN_IMPORT_PREFIXES = ("sqlalchemy", "flask", "fastapi", "requests", "urllib", "socket", "src.ufms", "src.umms")
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
    "a7StageCount": 3,
    "passedStageCount": 3,
    "failedStageCount": 0,
    "endpointCount": 8,
    "endpointSkeletonCount": 8,
    "endpointResponseContractCount": 8,
    "paginationContractCount": 8,
    "filterContractCount": 8,
    "facetContractCount": 8,
    "errorContractCount": 8,
    "authPolicyContractCount": 8,
    "mockRouteContractCount": 8,
    "localSmokeCaseCount": 8,
    "coverageEntryCount": 8,
    "mockRouteCoverageEntryCount": 8,
    "releaseGateCount": 19,
    "passedGateCount": 19,
    "blockingGateFailureCount": 0,
    "getEndpointCount": 8,
    "readOnlyEndpointCount": 8,
    "readOnlyRouteCount": 8,
    "authRequiredCount": 8,
    "rolePolicyRequiredCount": 8,
    "networkCallRequiredCount": 0,
    "localhostCallRequiredCount": 0,
    "backendRouteImplementationCount": 0,
    "productionEnabledEndpointCount": 0,
    "databaseAccessEnabledEndpointCount": 0,
    "writeOperationEnabledEndpointCount": 0,
    "runtimeActivationEnabledEndpointCount": 0,
    "readOnlyApiRouteImplementationAllowed": True,
    "productionApiAllowed": False,
    "backendRouteImplementationAllowed": False,
    "databaseAccessAllowed": False,
    "writeOperationAllowed": False,
    "runtimeActivationAllowed": False,
    "productionActivationAllowed": False,
    "frontendImplementationAllowed": False,
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
    checks.append(("Implementation status frozen", gate.get("implementationStatus") == "READ_ONLY_API_IMPLEMENTATION_RELEASE_GATE_COMPLETE"))
    checks.append(("Readiness outcome frozen", gate.get("readinessOutcome") == "READ_ONLY_API_READY_FOR_FUTURE_ROUTE_IMPLEMENTATION"))
    checks.append(("Expected summary freeze", all(summary.get(key) == value for key, value in EXPECTED_SUMMARY.items())))
    checks.append(("Three A7 stages", len(gate.get("stageResults", [])) == 3))
    checks.append(("All A7 stages pass", all(item.get("status") == "PASS" for item in gate.get("stageResults", []))))
    checks.append(("Eight endpoint coverage entries", len(gate.get("apiContractCoverageMatrix", [])) == 8))
    checks.append(("Eight mock route coverage entries", len(gate.get("mockRouteCoverageMatrix", [])) == 8))
    checks.append(("Nineteen release gates", len(gate.get("releaseGateResults", [])) == 19))
    checks.append(("All release gates pass", all(item.get("status") == "PASS" for item in gate.get("releaseGateResults", []))))
    checks.append(("Dependency gates pass", all(item.get("status") == "PASS" for item in gate.get("dependencyGateResults", []))))
    checks.append(("Coverage matrix pass", all(item.get("status") == "PASS" for item in gate.get("apiContractCoverageMatrix", []))))
    checks.append(("Mock route coverage pass", all(item.get("status") == "PASS" for item in gate.get("mockRouteCoverageMatrix", []))))
    decision = gate.get("implementationDecision", {})
    checks.append(("Read-only implementation decision", decision.get("decisionState") == "READY_FOR_READ_ONLY_ROUTE_IMPLEMENTATION" and decision.get("readOnlyApiRouteImplementationAllowed") is True))
    checks.append(("Production/runtime implementation blocked", all(decision.get(key) is False for key in ("productionApiAllowed", "backendRouteImplementationAllowed", "databaseAccessAllowed", "writeOperationAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "frontendImplementationAllowed", "pushAllowed"))))
    serialized = json.dumps(gate, sort_keys=True)
    checks.append(("No customer identifier text leakage", "customerAssetIdentifier" not in serialized and "assetId" not in serialized and "deviceId" not in serialized))


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    checks.append(("Registry exists", REGISTRY.is_file()))
    checks.append(("Generic package exists", GENERIC_DIR.is_dir()))
    checks.append(("Airport release gate module exists", AIRPORT_MODULE.is_file()))
    checks.append(("Airport release gate artifact exists", AIRPORT_PROJECTION.is_file()))
    checks.append(("Deterministic runner exists", RUNNER.is_file()))
    if REGISTRY.is_file():
        registry = _load_json(REGISTRY)
        checks.append(("Registry cross-industry", registry.get("crossIndustry") is True))
        checks.append(("Registry not airport-specific", registry.get("airportSpecific") is False))
        checks.append(("Registry API disabled", registry.get("apiEnabled") is False))
        checks.append(("Registry frontend disabled", registry.get("frontendEnabled") is False))
        checks.append(("Registry read-only implementation allowed", registry.get("readOnlyApiRouteImplementationAllowed") is True))
        checks.append(("Registry production API disabled", registry.get("productionApiAllowed") is False))

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
    checks.append(("Changes within A7-04 allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")
    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))
    if forbidden_touched:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden_touched))}")

    env = {**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")}
    test_proc = _run(["python3", "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/read_only_api_release_gate", "-p", "test_*.py"], env=env)
    checks.append(("Focused A7-04 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-4000:] or test_proc.stderr[-4000:] or "focused A7-04 tests failed")
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
            errors.append("read-only API implementation release gate generation is not byte-identical")

    print("ONE_AIRPORT_A7_04_READ_ONLY_API_IMPLEMENTATION_RELEASE_GATE_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("READ_ONLY_API_IMPLEMENTATION_RELEASE_GATE_COMPLETE")
    print("READ_ONLY_API_READY_FOR_FUTURE_ROUTE_IMPLEMENTATION")
    print("ONE_AIRPORT_A7_04_READ_ONLY_API_IMPLEMENTATION_RELEASE_GATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
