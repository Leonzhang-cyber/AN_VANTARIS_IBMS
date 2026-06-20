#!/usr/bin/env python3
"""Validate A7-03 read-only API mock route contract and local smoke gate."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/read-only-api-mock-route-contract.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/read_only_api_mock_route_contract"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/read_only_api_mock_route_contract.py"
AIRPORT_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-api-mock-route-contract.v1.json"
RUNNER = ROOT / "scripts/validation/_run_a7_03_airport_read_only_api_mock_route_contract.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/read_only_api_mock_route_contract/",
    "AN_VANTARIS_ONE/registries/read-only-api-mock-route-contract.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/read_only_api_mock_route_contract.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-api-mock-route-contract.v1.json",
    "AN_VANTARIS_ONE/tests/read_only_api_mock_route_contract/",
    "scripts/validation/validate-one-airport-read-only-api-mock-route-contract.py",
    "scripts/validation/_run_a7_03_airport_read_only_api_mock_route_contract.py",
    "ONE_AIRPORT_A7_03_READ_ONLY_API_MOCK_ROUTE_CONTRACT_AND_LOCAL_SMOKE_GATE_REPORT.md",
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
    "mockRouteContractCount": 8,
    "localSmokeCaseCount": 8,
    "smokeGateCount": 15,
    "passedSmokeGateCount": 15,
    "blockingGateFailureCount": 0,
    "getRouteCount": 8,
    "readOnlyRouteCount": 8,
    "productionRouteEnabledCount": 0,
    "databaseAccessEnabledRouteCount": 0,
    "writeOperationEnabledRouteCount": 0,
    "runtimeActivationEnabledRouteCount": 0,
    "responseContractLinkedCount": 8,
    "authPolicyLinkedCount": 8,
    "expectedStatus200Count": 8,
    "expectedEnvelopeRequiredCount": 8,
    "expectedAuthRequiredCount": 8,
    "expectedPaginationSupportedCount": 8,
    "expectedFiltersSupportedCount": 8,
    "expectedFacetsSupportedCount": 8,
    "expectedNoWriteCount": 8,
    "networkCallRequiredCount": 0,
    "localhostCallRequiredCount": 0,
    "backendRouteImplementationCount": 0,
    "apiEnabled": False,
    "productionApiAllowed": False,
    "databaseWriteCount": 0,
    "canonicalWriteCount": 0,
    "decisionWriteCount": 0,
    "approvalWriteCount": 0,
    "auditWriteCount": 0,
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
    contract = _load_json(AIRPORT_PROJECTION)
    summary = contract.get("summary", {})
    checks.append(("Implementation status frozen", contract.get("implementationStatus") == "READ_ONLY_API_MOCK_ROUTE_CONTRACT_AND_LOCAL_SMOKE_GATE_COMPLETE"))
    checks.append(("Readiness outcome frozen", contract.get("readinessOutcome") == "READ_ONLY_API_MOCK_ROUTE_CONTRACT_READY_FOR_FUTURE_ROUTE_IMPLEMENTATION"))
    checks.append(("Expected summary freeze", all(summary.get(key) == value for key, value in EXPECTED_SUMMARY.items())))
    checks.append(("Eight mock route contracts", len(contract.get("mockRouteContracts", [])) == 8))
    checks.append(("Eight local smoke cases", len(contract.get("localSmokeCases", [])) == 8))
    checks.append(("Fifteen smoke gates", len(contract.get("smokeGateResults", [])) == 15))
    checks.append(("All smoke gates pass", all(gate.get("status") == "PASS" for gate in contract.get("smokeGateResults", []))))
    checks.append(
        (
            "GET read-only mock routes",
            all(
                item.get("method") == "GET"
                and item.get("readOnly") is True
                and item.get("productionRouteEnabled") is False
                and item.get("databaseAccessEnabled") is False
                and item.get("writeOperationEnabled") is False
                and item.get("runtimeActivationEnabled") is False
                for item in contract.get("mockRouteContracts", [])
            ),
        )
    )
    checks.append(
        (
            "Local smoke contract-only expectations",
            all(
                item.get("expectedStatusCode") == 200
                and item.get("expectedEnvelopeRequired") is True
                and item.get("expectedAuthRequired") is True
                and item.get("expectedPaginationSupported") is True
                and item.get("expectedFiltersSupported") is True
                and item.get("expectedFacetsSupported") is True
                and item.get("expectedReadOnly") is True
                and item.get("expectedNoWrite") is True
                and item.get("networkCallRequired") is False
                and item.get("localhostCallRequired") is False
                for item in contract.get("localSmokeCases", [])
            ),
        )
    )
    serialized = json.dumps(contract, sort_keys=True)
    checks.append(("No customer identifier text leakage", "customerAssetIdentifier" not in serialized and "assetId" not in serialized and "deviceId" not in serialized))


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    checks.append(("Registry exists", REGISTRY.is_file()))
    checks.append(("Generic package exists", GENERIC_DIR.is_dir()))
    checks.append(("Airport mock route contract module exists", AIRPORT_MODULE.is_file()))
    checks.append(("Airport mock route contract artifact exists", AIRPORT_PROJECTION.is_file()))
    checks.append(("Deterministic runner exists", RUNNER.is_file()))
    if REGISTRY.is_file():
        registry = _load_json(REGISTRY)
        checks.append(("Registry cross-industry", registry.get("crossIndustry") is True))
        checks.append(("Registry not airport-specific", registry.get("airportSpecific") is False))
        checks.append(("Registry API disabled", registry.get("apiEnabled") is False))
        checks.append(("Registry frontend disabled", registry.get("frontendEnabled") is False))
        checks.append(("Registry no network smoke", registry.get("networkCallRequiredCount") == 0))

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
    checks.append(("Changes within A7-03 allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")
    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))
    if forbidden_touched:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden_touched))}")

    env = {**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")}
    test_proc = _run(["python3", "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/read_only_api_mock_route_contract", "-p", "test_*.py"], env=env)
    checks.append(("Focused A7-03 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-4000:] or test_proc.stderr[-4000:] or "focused A7-03 tests failed")
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
            errors.append("read-only API mock route contract generation is not byte-identical")

    print("ONE_AIRPORT_A7_03_READ_ONLY_API_MOCK_ROUTE_CONTRACT_AND_LOCAL_SMOKE_GATE_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("READ_ONLY_API_MOCK_ROUTE_CONTRACT_AND_LOCAL_SMOKE_GATE_COMPLETE")
    print("READ_ONLY_API_MOCK_ROUTE_CONTRACT_READY_FOR_FUTURE_ROUTE_IMPLEMENTATION")
    print("ONE_AIRPORT_A7_03_READ_ONLY_API_MOCK_ROUTE_CONTRACT_AND_LOCAL_SMOKE_GATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
