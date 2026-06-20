#!/usr/bin/env python3
"""Validate A6-01 API / Frontend readiness contract freeze."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/api-frontend-readiness-contract.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/api_frontend_readiness_contract"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/api_frontend_readiness_contract.py"
AIRPORT_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-api-frontend-readiness-contract.v1.json"
RUNNER = ROOT / "scripts/validation/_run_a6_01_api_frontend_readiness_contract.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/api_frontend_readiness_contract/",
    "AN_VANTARIS_ONE/registries/api-frontend-readiness-contract.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/api_frontend_readiness_contract.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-api-frontend-readiness-contract.v1.json",
    "AN_VANTARIS_ONE/tests/api_frontend_readiness_contract/",
    "scripts/validation/validate-one-airport-api-frontend-readiness-contract.py",
    "scripts/validation/_run_a6_01_api_frontend_readiness_contract.py",
    "ONE_AIRPORT_A6_01_API_FRONTEND_READINESS_CONTRACT_FREEZE_REPORT.md",
)
FORBIDDEN_IMPORT_PREFIXES = ("sqlalchemy", "flask", "requests", "urllib", "socket", "src.ufms", "src.umms")
FORBIDDEN_TEXT = ("blueprint", "api.route", "live alarm timestamp", "last-seen", "last_seen", "packet loss")
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
    "apiEndpointCandidateCount": 8,
    "frontendPageCandidateCount": 8,
    "frontendRouteCandidateCount": 8,
    "dataBindingContractCount": 15,
    "cardBindingContractCount": 8,
    "queueBindingContractCount": 8,
    "readinessGateCount": 15,
    "passedGateCount": 15,
    "blockingGateFailureCount": 0,
    "readOnlyEndpointCandidateCount": 8,
    "apiImplementationAllowedCount": 0,
    "frontendImplementationAllowedCount": 0,
    "routeImplementationAllowedCount": 0,
    "databaseAccessAllowedCount": 0,
    "writeOperationAllowedCount": 0,
    "authPolicyRequiredCount": 8,
    "pageCandidateCount": 8,
    "cardCandidateCount": 8,
    "sourceSystemCandidateCount": 5,
    "alarmEventCandidateCount": 5,
    "faultCaseCandidateCount": 5,
    "workOrderIntentCandidateCount": 5,
    "investigationCaseCount": 5,
    "decisionItemCount": 46,
    "queueRowCount": 46,
    "totalDeviceEvidenceCount": 470,
    "apiEnabled": False,
    "frontendEnabled": False,
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
    contract = _load_json(AIRPORT_PROJECTION)
    summary = contract.get("summary", {})
    checks.append(("Implementation status frozen", contract.get("implementationStatus") == "API_FRONTEND_READINESS_CONTRACT_FREEZE_COMPLETE"))
    checks.append(("Readiness outcome frozen", contract.get("readinessOutcome") == "API_FRONTEND_CONTRACT_FROZEN_FOR_FUTURE_IMPLEMENTATION_PLANNING"))
    checks.append(("Expected summary freeze", all(summary.get(key) == value for key, value in EXPECTED_SUMMARY.items())))
    checks.append(("Eight endpoint candidates", len(contract.get("apiEndpointCandidates", [])) == 8))
    checks.append(("Eight frontend page candidates", len(contract.get("frontendPageCandidates", [])) == 8))
    checks.append(("Eight frontend route candidates", len(contract.get("frontendRouteCandidates", [])) == 8))
    checks.append(("Fifteen datasource bindings", len(contract.get("dataBindingContracts", [])) == 15))
    checks.append(("Eight card bindings", len(contract.get("cardBindingContracts", [])) == 8))
    checks.append(("Eight queue bindings", len(contract.get("queueBindingContracts", [])) == 8))
    checks.append(("Fifteen readiness gates", len(contract.get("readinessGates", [])) == 15))
    checks.append(("All readiness gates pass", all(item.get("status") == "PASS" for item in contract.get("readinessGates", []))))
    checks.append(("Endpoint candidates frozen read-only", all(item.get("method") == "GET" and item.get("readOnly") is True and item.get("implementationAllowed") is False and item.get("publicApiEnabled") is False and item.get("databaseAccessAllowed") is False and item.get("writeOperationAllowed") is False and item.get("authPolicyRequired") is True and item.get("responseContractState") == "FROZEN_FOR_PLANNING" for item in contract.get("apiEndpointCandidates", []))))
    checks.append(("Frontend candidates disabled", all(item.get("implementationAllowed") is False and item.get("routeImplementationAllowed") is False and item.get("runtimeDataMutationAllowed") is False for item in contract.get("frontendPageCandidates", []))))
    checks.append(("Route candidates disabled", all(item.get("implementationAllowed") is False and item.get("runtimeDataMutationAllowed") is False for item in contract.get("frontendRouteCandidates", []))))
    serialized = json.dumps(contract, sort_keys=True)
    checks.append(("No customer identifier text leakage", "customerAssetIdentifier" not in serialized and "assetId" not in serialized and "deviceId" not in serialized))


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    checks.append(("Registry exists", REGISTRY.is_file()))
    checks.append(("Generic package exists", GENERIC_DIR.is_dir()))
    checks.append(("Airport contract module exists", AIRPORT_MODULE.is_file()))
    checks.append(("Airport contract artifact exists", AIRPORT_PROJECTION.is_file()))
    checks.append(("Deterministic runner exists", RUNNER.is_file()))
    if REGISTRY.is_file():
        registry = _load_json(REGISTRY)
        checks.append(("Registry cross-industry", registry.get("crossIndustry") is True))
        checks.append(("Registry not airport-specific", registry.get("airportSpecific") is False))
        checks.append(("Registry API disabled", registry.get("apiEnabled") is False))
        checks.append(("Registry frontend disabled", registry.get("frontendEnabled") is False))
        checks.append(("Registry DB writes disabled", registry.get("databaseWriteCount") == 0))

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
    checks.append(("Changes within A6-01 allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")
    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))
    if forbidden_touched:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden_touched))}")

    env = {**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")}
    test_proc = _run(["python3", "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/api_frontend_readiness_contract", "-p", "test_*.py"], env=env)
    checks.append(("Focused A6-01 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-4000:] or test_proc.stderr[-4000:] or "focused A6-01 tests failed")
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
            errors.append("API / Frontend readiness contract generation is not byte-identical")

    print("ONE_AIRPORT_A6_01_API_FRONTEND_READINESS_CONTRACT_FREEZE_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("API_FRONTEND_READINESS_CONTRACT_FREEZE_COMPLETE")
    print("API_FRONTEND_CONTRACT_FROZEN_FOR_FUTURE_IMPLEMENTATION_PLANNING")
    print("ONE_AIRPORT_A6_01_API_FRONTEND_READINESS_CONTRACT_FREEZE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
