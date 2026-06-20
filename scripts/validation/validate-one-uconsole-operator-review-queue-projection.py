#!/usr/bin/env python3
"""Validate A4-02 UConsole Operator Review Queue Projection."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/uconsole-operator-review-queue-projection.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/uconsole_operator_review_queue"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/uconsole_operator_review_queue_projection.py"
AIRPORT_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-uconsole-operator-review-queue.v1.json"
RUNNER = ROOT / "scripts/validation/_run_a4_02_uconsole_operator_review_queue_projection.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/uconsole_operator_review_queue/",
    "AN_VANTARIS_ONE/registries/uconsole-operator-review-queue-projection.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/uconsole_operator_review_queue_projection.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-uconsole-operator-review-queue.v1.json",
    "AN_VANTARIS_ONE/tests/uconsole_operator_review_queue/",
    "scripts/validation/validate-one-uconsole-operator-review-queue-projection.py",
    "scripts/validation/_run_a4_02_uconsole_operator_review_queue_projection.py",
    "ONE_AIRPORT_A4_02_OPERATOR_REVIEW_UCONSOLE_QUEUE_PROJECTION_REPORT.md",
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
    "decisionItemCount": 46,
    "queueRowCount": 46,
    "queueGroupCount": 8,
    "queueCardCount": 8,
    "pendingDecisionCount": 46,
    "blockingDecisionCount": 45,
    "nonBlockingDecisionCount": 1,
    "sourceSystemRegistryDecisionCount": 5,
    "assetResolutionDecisionCount": 5,
    "pointResolutionDecisionCount": 5,
    "locationResolutionDecisionCount": 5,
    "alarmEventReviewDecisionCount": 5,
    "faultCaseReviewDecisionCount": 5,
    "workOrderIntentReviewDecisionCount": 5,
    "evidenceInvestigationDecisionCount": 5,
    "downstreamCreationAuthorizationDecisionCount": 5,
    "releaseGateDecisionCount": 1,
    "affectedSourceSystemCount": 5,
    "totalDeviceEvidenceCount": 470,
    "decisionWriteCount": 0,
    "approvalWriteCount": 0,
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
    projection = _load_json(AIRPORT_PROJECTION)
    summary = projection.get("summary", {})
    rows = projection.get("queueRows", [])
    groups = projection.get("queueGroups", [])
    cards = projection.get("queueCards", [])
    checks.append(("Implementation status frozen", projection.get("implementationStatus") == "OPERATOR_REVIEW_UCONSOLE_QUEUE_PROJECTION_COMPLETE"))
    checks.append(("Readiness outcome frozen", projection.get("readinessOutcome") == "UCONSOLE_OPERATOR_REVIEW_QUEUE_READY_FOR_READ_ONLY_CONSUMPTION"))
    checks.append(("Expected summary freeze", all(summary.get(key) == value for key, value in EXPECTED_SUMMARY.items())))
    checks.append(("Forty-six queue rows", len(rows) == 46))
    checks.append(("Eight queue groups", len(groups) == 8))
    checks.append(("Eight queue cards", len(cards) == 8))
    checks.append(("No approved rows", all(row.get("decisionState") != "APPROVED" for row in rows)))
    checks.append(("Blocking/non-blocking counts", summary.get("blockingDecisionCount") == 45 and summary.get("nonBlockingDecisionCount") == 1))
    checks.append(("Total evidence 470", summary.get("totalDeviceEvidenceCount") == 470))
    checks.append(("Decision writes zero", summary.get("decisionWriteCount") == 0 and summary.get("approvalWriteCount") == 0))
    checks.append(("Runtime surfaces disabled", summary.get("apiEnabled") is False and summary.get("frontendEnabled") is False))
    checks.append(("Activation disabled", summary.get("runtimeActivationAllowed") is False and summary.get("productionActivationAllowed") is False and summary.get("pushAllowed") is False))
    checks.append(("No customer identifiers", summary.get("containsCustomerAssetIdentifiers") is False))
    checks.append(("Cross-industry true", summary.get("crossIndustry") is True))
    checks.append(("Airport-specific false", summary.get("airportSpecific") is False))
    checks.append(("Deterministic row ordering", rows == sorted(rows, key=lambda row: (row["queueType"], row["decisionType"], row.get("sourceSystemKey") or "", row["rowId"]))))


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    checks.append(("Registry exists", REGISTRY.is_file()))
    checks.append(("Generic package exists", GENERIC_DIR.is_dir()))
    checks.append(("Airport projection module exists", AIRPORT_MODULE.is_file()))
    checks.append(("Airport projection exists", AIRPORT_PROJECTION.is_file()))
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
    checks.append(("Changes within A4-02 allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")
    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))
    if forbidden_touched:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden_touched))}")

    env = {**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")}
    test_proc = _run(["python3", "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/uconsole_operator_review_queue", "-p", "test_*.py"], env=env)
    checks.append(("Focused A4-02 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-4000:] or test_proc.stderr[-4000:] or "focused A4-02 tests failed")
    runner_proc = _run(["python3", str(RUNNER)], env=env)
    checks.append(("Deterministic runner pass", runner_proc.returncode == 0))
    if runner_proc.returncode != 0:
        errors.append(runner_proc.stdout[-4000:] or runner_proc.stderr[-4000:] or "runner failed")
    if AIRPORT_PROJECTION.is_file():
        _append_projection_checks(checks)
        before = AIRPORT_PROJECTION.read_text(encoding="utf-8")
        second = _run(["python3", str(RUNNER)], env=env)
        after = AIRPORT_PROJECTION.read_text(encoding="utf-8")
        checks.append(("Repeated generation byte-identical", second.returncode == 0 and before == after))
        if second.returncode != 0 or before != after:
            errors.append("projection generation is not byte-identical")

    print("ONE_AIRPORT_A4_02_OPERATOR_REVIEW_UCONSOLE_QUEUE_PROJECTION_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OPERATOR_REVIEW_UCONSOLE_QUEUE_PROJECTION_COMPLETE")
    print("UCONSOLE_OPERATOR_REVIEW_QUEUE_READY_FOR_READ_ONLY_CONSUMPTION")
    print("ONE_AIRPORT_A4_02_OPERATOR_REVIEW_UCONSOLE_QUEUE_PROJECTION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
