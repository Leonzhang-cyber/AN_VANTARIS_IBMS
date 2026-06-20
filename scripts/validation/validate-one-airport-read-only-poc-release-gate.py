#!/usr/bin/env python3
"""Validate A9-01 Airport read-only POC release aggregation and final gate."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/airport-read-only-poc-release-gate.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/airport_read_only_poc_release_gate"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/airport_read_only_poc_release_gate.py"
AIRPORT_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-poc-release-gate.v1.json"
RUNNER = ROOT / "scripts/validation/_run_a9_01_airport_read_only_poc_release_gate.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/airport_read_only_poc_release_gate/",
    "AN_VANTARIS_ONE/registries/airport-read-only-poc-release-gate.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/airport_read_only_poc_release_gate.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-poc-release-gate.v1.json",
    "AN_VANTARIS_ONE/tests/airport_read_only_poc_release_gate/",
    "scripts/validation/validate-one-airport-read-only-poc-release-gate.py",
    "scripts/validation/_run_a9_01_airport_read_only_poc_release_gate.py",
    "ONE_AIRPORT_A9_01_AIRPORT_READ_ONLY_POC_RELEASE_AGGREGATION_AND_FINAL_GATE_REPORT.md",
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
    "stageGroupCount": 8,
    "passedStageGroupCount": 8,
    "failedStageGroupCount": 0,
    "businessCapabilityCount": 15,
    "releaseGateCount": 20,
    "passedGateCount": 20,
    "blockingGateFailureCount": 0,
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
    "pageDefinitionCount": 8,
    "apiEndpointCandidateCount": 8,
    "readOnlyEndpointCount": 8,
    "frontendPageCandidateCount": 8,
    "frontendRouteCandidateCount": 8,
    "pageSkeletonCount": 8,
    "pageContractCount": 8,
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
    "productionApiAllowed": False,
    "productionFrontendAllowed": False,
    "runtimeActivationAllowed": False,
    "productionActivationAllowed": False,
    "releaseCandidateAllowed": True,
    "pushAllowed": False,
    "tagAllowed": False,
    "containsCustomerAssetIdentifiers": False,
    "crossIndustry": True,
    "airportSpecific": False,
}


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


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _append_projection_checks(checks: list[tuple[str, bool]]) -> None:
    gate = _load_json(AIRPORT_PROJECTION)
    summary = gate.get("summary", {})
    checks.append(("Implementation status frozen", gate.get("implementationStatus") == "AIRPORT_READ_ONLY_POC_RELEASE_AGGREGATION_AND_FINAL_GATE_COMPLETE"))
    checks.append(("Readiness outcome frozen", gate.get("readinessOutcome") == "AIRPORT_READ_ONLY_POC_RELEASE_CANDIDATE_PASS"))
    checks.append(("Expected summary freeze", all(summary.get(key) == value for key, value in EXPECTED_SUMMARY.items())))
    checks.append(("Eight stage groups", len(gate.get("stageResults", [])) == 8))
    checks.append(("All stage groups pass", all(item.get("status") == "PASS" for item in gate.get("stageResults", []))))
    checks.append(("Fifteen business capabilities", len(gate.get("businessCapabilityMatrix", [])) == 15))
    checks.append(("Capabilities are read-only non-production", all(item.get("readOnly") is True and item.get("productionEnabled") is False for item in gate.get("businessCapabilityMatrix", []))))
    checks.append(("Twenty release gates", len(gate.get("releaseGateResults", [])) == 20))
    checks.append(("All release gates pass", all(item.get("status") == "PASS" for item in gate.get("releaseGateResults", []))))
    checks.append(("Required artifacts covered", all(item.get("present") is True and item.get("status") == "PASS" for item in gate.get("artifactCoverageMatrix", []))))
    checks.append(("Technical boundaries pass", all(item.get("status") == "PASS" for item in gate.get("technicalBoundaryMatrix", []))))
    decision = gate.get("releaseDecision", {})
    checks.append(("Release candidate allowed locally", decision.get("decisionState") == "READ_ONLY_POC_RELEASE_CANDIDATE_PASS" and decision.get("releaseCandidateAllowed") is True))
    checks.append(("Push/tag/production/runtime blocked", all(decision.get(key) is False for key in ("pushAllowed", "tagAllowed", "productionActivationAllowed", "runtimeActivationAllowed", "databaseWriteAllowed", "apiProductionAllowed", "frontendProductionAllowed", "approvalExecutionAllowed"))))
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
        checks.append(("Registry release candidate allowed", registry.get("releaseCandidateAllowed") is True))
        checks.append(("Registry push/tag blocked", registry.get("pushAllowed") is False and registry.get("tagAllowed") is False))
        checks.append(("Registry production/runtime disabled", all(registry.get(key) is False for key in ("apiEnabled", "frontendEnabled", "productionApiAllowed", "productionFrontendAllowed", "runtimeActivationAllowed", "productionActivationAllowed"))))

    import_errors: list[str] = []
    for path in list(GENERIC_DIR.glob("*.py")) + [AIRPORT_MODULE, RUNNER]:
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
    checks.append(("Changes within A9-01 allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")
    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))
    if forbidden_touched:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden_touched))}")

    env = {**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")}
    test_proc = _run(["python3", "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/airport_read_only_poc_release_gate", "-p", "test_*.py"], env=env)
    checks.append(("Focused A9-01 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-4000:] or test_proc.stderr[-4000:] or "focused A9-01 tests failed")
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
            errors.append("A9 release gate generation is not byte-identical")

    print("ONE_AIRPORT_A9_01_AIRPORT_READ_ONLY_POC_RELEASE_AGGREGATION_AND_FINAL_GATE_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("AIRPORT_READ_ONLY_POC_RELEASE_AGGREGATION_AND_FINAL_GATE_COMPLETE")
    print("AIRPORT_READ_ONLY_POC_RELEASE_CANDIDATE_PASS")
    print("ONE_AIRPORT_A9_01_AIRPORT_READ_ONLY_POC_RELEASE_AGGREGATION_AND_FINAL_GATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
