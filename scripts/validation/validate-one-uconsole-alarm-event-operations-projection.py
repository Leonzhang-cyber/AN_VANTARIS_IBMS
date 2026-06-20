#!/usr/bin/env python3
"""Validate A3-06 read-only UConsole Alarm/Event Operations Projection."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/uconsole-alarm-event-operations-projection.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/uconsole_alarm_event_operations"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/uconsole_alarm_event_operations_projection.py"
AIRPORT_PROJECTION = (
    ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-uconsole-alarm-event-operations.v1.json"
)
RUNNER = ROOT / "scripts/validation/_run_a3_06_uconsole_alarm_event_operations_projection.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/uconsole_alarm_event_operations/",
    "AN_VANTARIS_ONE/registries/uconsole-alarm-event-operations-projection.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/uconsole_alarm_event_operations_projection.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-uconsole-alarm-event-operations.v1.json",
    "AN_VANTARIS_ONE/tests/uconsole_alarm_event_operations/",
    "scripts/validation/validate-one-uconsole-alarm-event-operations-projection.py",
    "scripts/validation/_run_a3_06_uconsole_alarm_event_operations_projection.py",
    "ONE_AIRPORT_A3_06_READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_REPORT.md",
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
    "operationsRowCount": 5,
    "operationsCardCount": 7,
    "alarmEventCandidateCount": 5,
    "resolutionRowCount": 5,
    "faultCaseCandidateCount": 5,
    "workOrderIntentCandidateCount": 5,
    "investigationCaseCount": 5,
    "totalDeviceEvidenceCount": 470,
    "decisionRequiredCount": 5,
    "reviewRequiredRowCount": 5,
    "blockedRowCount": 5,
    "runtimePendingCount": 5,
    "registryApprovalPendingCount": 2,
    "aliasApprovalPendingCount": 2,
    "namespaceReviewPendingCount": 1,
    "assetResolutionRequiredCount": 5,
    "faultCaseReviewRequiredCount": 5,
    "workOrderIntentReviewRequiredCount": 5,
    "evidenceInvestigationReviewRequiredCount": 5,
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
    rows = projection.get("operationsRows", [])
    cards = projection.get("operationsCards", [])
    by_key = {row.get("sourceSystemKey"): row for row in rows}
    checks.append(
        (
            "Implementation status frozen",
            projection.get("implementationStatus") == "READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_COMPLETE",
        )
    )
    checks.append(
        (
            "Readiness outcome frozen",
            projection.get("readinessOutcome")
            == "UCONSOLE_ALARM_EVENT_OPERATIONS_READ_ONLY_PROJECTION_COMPLETE_PENDING_REVIEWS",
        )
    )
    checks.append(("Expected summary freeze", all(summary.get(key) == value for key, value in EXPECTED_SUMMARY.items())))
    checks.append(("Five operations rows", len(rows) == 5))
    checks.append(("Seven operations cards", len(cards) == 7))
    checks.append(
        (
            "Expected source evidence counts",
            {key: by_key.get(key, {}).get("deviceEvidenceCount") for key in ("ACS", "RAS", "CCTV", "PA", "TEL")}
            == {"ACS": 129, "RAS": 28, "CCTV": 52, "PA": 247, "TEL": 14},
        )
    )
    checks.append(
        (
            "Rows link all upstream artifacts",
            all(
                row.get("alarmEventCandidateId")
                and row.get("resolutionRowId")
                and row.get("faultCaseCandidateId")
                and row.get("workOrderIntentCandidateId")
                and row.get("investigationCaseId")
                for row in rows
            ),
        )
    )
    checks.append(
        (
            "Rows blocked and decision-required",
            all(
                row.get("operationalStatus") == "BLOCKED"
                and row.get("decisionRequired") is True
                and int(row.get("pendingDecisionCount", 0)) >= 1
                for row in rows
            ),
        )
    )
    checks.append(
        (
            "Expected card types",
            [card.get("cardType") for card in cards]
            == [
                "ALARM_EVENT_QUEUE",
                "FAULTCASE_CANDIDATE_QUEUE",
                "WORKORDER_INTENT_QUEUE",
                "EVIDENCE_INVESTIGATION_QUEUE",
                "REVIEW_REQUIRED_SUMMARY",
                "RUNTIME_PENDING_SUMMARY",
                "SOURCE_SYSTEM_SUMMARY",
            ],
        )
    )
    for key in (
        "runtimeAlarmObservedCount",
        "ufmsFaultCaseCreatedCount",
        "workOrderIntentCreatedCount",
        "workOrderCreatedCount",
        "evidenceCenterWriteCount",
        "ummsWriteCount",
        "oneWorkManagementWriteCount",
        "canonicalWriteCount",
        "databaseWriteCount",
    ):
        checks.append((f"{key} zero", summary.get(key) == 0))
    checks.append(("API disabled", summary.get("apiEnabled") is False))
    checks.append(("Frontend disabled", summary.get("frontendEnabled") is False))
    checks.append(("No customer identifiers", summary.get("containsCustomerAssetIdentifiers") is False))
    checks.append(("Cross-industry true", summary.get("crossIndustry") is True))
    checks.append(("Airport-specific false", summary.get("airportSpecific") is False))
    checks.append(("Deterministic row ordering", rows == sorted(rows, key=lambda item: (item["sourceSystemKey"], item["rowId"]))))


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
    checks.append(("Changes within A3-06 allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")
    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))
    if forbidden_touched:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden_touched))}")

    env = {**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")}
    test_proc = _run(
        ["python3", "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/uconsole_alarm_event_operations", "-p", "test_*.py"],
        env=env,
    )
    checks.append(("Focused A3-06 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-4000:] or test_proc.stderr[-4000:] or "focused A3-06 tests failed")
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

    print("ONE_AIRPORT_A3_06_READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_COMPLETE")
    print("UCONSOLE_ALARM_EVENT_OPERATIONS_READ_ONLY_PROJECTION_COMPLETE_PENDING_REVIEWS")
    print("ONE_AIRPORT_A3_06_READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
