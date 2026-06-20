#!/usr/bin/env python3
"""Validate A3-07 readiness aggregation and release gate."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/a3-readiness-release-gate.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/a3_readiness_gate"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/a3_readiness_release_gate.py"
AIRPORT_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-a3-readiness-release-gate.v1.json"
RUNNER = ROOT / "scripts/validation/_run_a3_07_readiness_release_gate.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/a3_readiness_gate/",
    "AN_VANTARIS_ONE/registries/a3-readiness-release-gate.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/a3_readiness_release_gate.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-a3-readiness-release-gate.v1.json",
    "AN_VANTARIS_ONE/tests/a3_readiness_gate/",
    "scripts/validation/validate-one-airport-a3-readiness-release-gate.py",
    "scripts/validation/_run_a3_07_readiness_release_gate.py",
    "ONE_AIRPORT_A3_07_A3_READINESS_AGGREGATION_AND_RELEASE_GATE_REPORT.md",
)
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
FORBIDDEN_IMPORT_PREFIXES = ("sqlalchemy", "flask", "requests", "urllib", "socket", "src.ufms", "src.umms")
FORBIDDEN_TEXT = ("blueprint", "api.route", "react", "live alarm timestamp", "last-seen", "last_seen", "packet loss")

EXPECTED_SUMMARY = {
    "a3StageCount": 6,
    "passedStageCount": 6,
    "failedStageCount": 0,
    "gateCount": 12,
    "passedGateCount": 12,
    "blockingGateFailureCount": 0,
    "alarmEventCandidateCount": 5,
    "resolutionRowCount": 5,
    "faultCaseCandidateCount": 5,
    "workOrderIntentCandidateCount": 5,
    "investigationCaseCount": 5,
    "operationsRowCount": 5,
    "totalDeviceEvidenceCount": 470,
    "decisionRequiredCount": 5,
    "runtimeObservedCount": 0,
    "runtimeAlarmObservedCount": 0,
    "ufmsFaultCaseCreatedCount": 0,
    "workOrderIntentCreatedCount": 0,
    "workOrderCreatedCount": 0,
    "evidenceCenterWriteCount": 0,
    "ummsWriteCount": 0,
    "oneWorkManagementWriteCount": 0,
    "canonicalWriteCount": 0,
    "databaseWriteCount": 0,
    "apiEnabled": False,
    "frontendEnabled": False,
    "releaseAllowed": True,
    "pushAllowed": False,
    "productionActivationAllowed": False,
    "runtimeActivationAllowed": False,
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
    release_gate = _load_json(AIRPORT_PROJECTION)
    summary = release_gate.get("summary", {})
    stages = release_gate.get("stageResults", [])
    gates = release_gate.get("gateResults", [])
    decision = release_gate.get("releaseDecision", {})
    checks.append(("Implementation status frozen", release_gate.get("implementationStatus") == "A3_READINESS_AGGREGATION_AND_RELEASE_GATE_COMPLETE"))
    checks.append(("Readiness outcome frozen", release_gate.get("readinessOutcome") == "A3_READ_ONLY_RELEASE_GATE_PASS"))
    checks.append(("Expected summary freeze", all(summary.get(key) == value for key, value in EXPECTED_SUMMARY.items())))
    checks.append(("Six A3 stages", len(stages) == 6))
    checks.append(("Twelve gate results", len(gates) == 12))
    checks.append(("All stages pass", all(stage.get("status") == "PASS" for stage in stages)))
    checks.append(("All gates pass", all(gate.get("status") == "PASS" for gate in gates)))
    checks.append(("No blocking failures", summary.get("blockingGateFailureCount") == 0))
    checks.append(("Release allowed", decision.get("releaseAllowed") is True))
    checks.append(("Push disabled", decision.get("pushAllowed") is False))
    checks.append(("Production activation disabled", decision.get("productionActivationAllowed") is False))
    checks.append(("Runtime activation disabled", decision.get("runtimeActivationAllowed") is False))
    checks.append(("Database writes disabled", decision.get("databaseWriteAllowed") is False))
    checks.append(("API disabled", decision.get("apiEnabled") is False))
    checks.append(("Frontend disabled", decision.get("frontendEnabled") is False))
    checks.append(("Regression matrix pass", all(entry.get("status") == "PASS" for entry in release_gate.get("regressionMatrix", []))))
    checks.append(("Boundary matrix pass", all(entry.get("status") == "PASS" for entry in release_gate.get("boundaryMatrix", []))))
    checks.append(("Six artifact references", len(release_gate.get("artifactReferences", [])) == 6))


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
        checks.append(("Registry DB disabled", registry.get("databaseAccessEnabled") is False))
        checks.append(("Registry API disabled", registry.get("apiEnabled") is False))
        checks.append(("Registry frontend disabled", registry.get("frontendEnabled") is False))

    import_errors: list[str] = []
    owned_py = list(GENERIC_DIR.glob("*.py")) + [AIRPORT_MODULE, RUNNER]
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
    owned_text = "\n".join(path.read_text(encoding="utf-8") for path in owned_py).lower()
    text_errors = [token for token in FORBIDDEN_TEXT if token in owned_text]
    checks.append(("No forbidden runtime/API/frontend text", len(text_errors) == 0))
    if text_errors:
        errors.append(f"forbidden text present: {', '.join(text_errors)}")

    changed = _changed_paths()
    disallowed = [path for path in changed if path and not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)]
    checks.append(("Changes within A3-07 allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")
    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))
    if forbidden_touched:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden_touched))}")

    env = {**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")}
    test_proc = _run(["python3", "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/a3_readiness_gate", "-p", "test_*.py"], env=env)
    checks.append(("Focused A3-07 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-4000:] or test_proc.stderr[-4000:] or "focused A3-07 tests failed")
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
            errors.append("release gate generation is not byte-identical")

    print("ONE_AIRPORT_A3_07_A3_READINESS_AGGREGATION_AND_RELEASE_GATE_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("A3_READINESS_AGGREGATION_AND_RELEASE_GATE_COMPLETE")
    print("A3_READ_ONLY_RELEASE_GATE_PASS")
    print("ONE_AIRPORT_A3_07_A3_READINESS_AGGREGATION_AND_RELEASE_GATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
