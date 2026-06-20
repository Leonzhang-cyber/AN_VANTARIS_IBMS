#!/usr/bin/env python3
"""Validate canonical alarm/event intake foundation and airport projection."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/canonical-alarm-event-intake.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/alarm_event_intake"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/alarm_event_intake_profile.py"
AIRPORT_PROJECTION = (
    ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-alarm-event-intake-candidates.v1.json"
)
RUNNER = ROOT / "scripts/validation/_run_a3_01_alarm_event_intake_fixture.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/alarm_event_intake/",
    "AN_VANTARIS_ONE/registries/canonical-alarm-event-intake.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/alarm_event_intake_profile.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-alarm-event-intake-candidates.v1.json",
    "AN_VANTARIS_ONE/tests/alarm_event_intake/",
    "scripts/validation/validate-one-alarm-event-intake-foundation.py",
    "scripts/validation/_run_a3_01_alarm_event_intake_fixture.py",
    "ONE_AIRPORT_A3_01_CANONICAL_ALARM_EVENT_INTAKE_FOUNDATION_REPORT.md",
)

FORBIDDEN_PATHS = (
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_LINK/",
    "AN_VANTARIS_Contracts/",
    "AN_VANTARIS_IBMS-frontend/",
    "database/",
    "migrations/",
    "UFMS/",
)

FORBIDDEN_IMPORT_PREFIXES = (
    "sqlalchemy",
    "flask",
    "requests",
    "urllib",
    "socket",
    "src.ufms",
    "src.umms",
)

FORBIDDEN_TEXT = (
    "blueprint",
    "api.route",
    "react",
    "live alarm timestamp",
    "last-seen",
    "last_seen",
    "availability percentage",
    "packet loss",
    "faultcase_created",
    "work_order_created",
)


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
    candidates = projection.get("candidates", [])
    cards = projection.get("reviewCards", [])

    checks.append(("Implementation status frozen", projection.get("implementationStatus") == "CANONICAL_ALARM_EVENT_INTAKE_FOUNDATION_COMPLETE"))
    checks.append(("Readiness outcome frozen", projection.get("readinessOutcome") == "ALARM_EVENT_INTAKE_CANDIDATES_COMPLETE_WITH_PENDING_REVIEWS"))
    checks.append(("Five source systems", summary.get("sourceSystemCandidateCount") == 5))
    checks.append(("Five envelopes", summary.get("intakeEnvelopeCount") == 5))
    checks.append(("Five candidates", summary.get("canonicalAlarmEventCandidateCount") == 5))
    checks.append(("Five accepted candidates", summary.get("acceptedAsCandidateCount") == 5))
    checks.append(("Zero rejected envelopes", summary.get("rejectedEnvelopeCount") == 0))
    checks.append(("Five review-required candidates", summary.get("reviewRequiredCandidateCount") == 5))
    checks.append(("Zero runtime alarms", summary.get("runtimeAlarmObservedCount") == 0))
    checks.append(("Polling disabled", summary.get("liveAlarmPollingEnabled") is False))
    checks.append(("Connector execution disabled", summary.get("connectorExecutionEnabled") is False))
    checks.append(("Database access disabled", summary.get("databaseAccessEnabled") is False))
    checks.append(("Zero DB writes", summary.get("databaseWriteCount") == 0))
    checks.append(("Zero canonical writes", summary.get("canonicalWriteCount") == 0))
    checks.append(("Zero UFMS FaultCases", summary.get("ufmsFaultCaseCreatedCount") == 0))
    checks.append(("Zero WorkOrderIntents", summary.get("workOrderIntentCreatedCount") == 0))
    checks.append(("Zero WorkOrders", summary.get("workOrderCreatedCount") == 0))
    checks.append(("Zero Evidence Center writes", summary.get("evidenceCenterWriteCount") == 0))
    checks.append(("Production activation disabled", summary.get("productionActivationEnabled") is False))
    checks.append(("No customer asset identifiers", summary.get("containsCustomerAssetIdentifiers") is False))
    checks.append(("Cross-industry true", summary.get("crossIndustry") is True))
    checks.append(("Airport-specific false", summary.get("airportSpecific") is False))
    checks.append(("Expected source keys", {item.get("sourceSystemKey") for item in candidates} == {"ACS", "RAS", "CCTV", "PA", "TEL"}))
    checks.append(("No downstream candidates created", all(item.get("ufmsFaultCaseCandidateState") == "BLOCKED" and item.get("workOrderIntentCandidateState") == "BLOCKED" for item in candidates)))
    checks.append(("Deterministic ordering", candidates == sorted(candidates, key=lambda row: (row["sourceSystemKey"], row["candidateId"]))))
    checks.append(("Review cards aggregated", len(cards) == 7))
    checks.append(("All required review reasons", {card.get("reason") for card in cards} == {
        "REGISTRY_APPROVAL_REQUIRED",
        "ALIAS_APPROVAL_REQUIRED",
        "NAMESPACE_INTERPRETATION_REQUIRED",
        "ASSET_RESOLUTION_REQUIRED",
        "POINT_RESOLUTION_REQUIRED",
        "LOCATION_RESOLUTION_REQUIRED",
        "DOWNSTREAM_CREATION_NOT_AUTHORIZED",
    }))


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []

    checks.append(("Registry exists", REGISTRY.is_file()))
    checks.append(("Generic package exists", GENERIC_DIR.is_dir()))
    checks.append(("Airport profile exists", AIRPORT_MODULE.is_file()))
    checks.append(("Airport projection exists", AIRPORT_PROJECTION.is_file()))
    checks.append(("Deterministic runner exists", RUNNER.is_file()))

    if REGISTRY.is_file():
        registry = _load_json(REGISTRY)
        checks.append(("Registry cross-industry", registry.get("crossIndustry") is True))
        checks.append(("Registry not airport-specific", registry.get("airportSpecific") is False))
        checks.append(("Registry DB disabled", registry.get("databaseAccessEnabled") is False))
        checks.append(("Registry API disabled", registry.get("apiEnabled") is False))
        checks.append(("Registry frontend disabled", registry.get("frontendEnabled") is False))
        checks.append(("Registry runtime disabled", registry.get("runtimeAlarmObservedCount") == 0))

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
    checks.append(("Changes within A3-01 allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")
    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))
    if forbidden_touched:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden_touched))}")

    test_proc = _run(
        [
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "AN_VANTARIS_ONE/tests/alarm_event_intake",
            "-p",
            "test_*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")},
    )
    checks.append(("Focused A3-01 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-3000:] or test_proc.stderr[-3000:] or "focused A3-01 tests failed")

    runner_proc = _run(["python3", str(RUNNER)], env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")})
    checks.append(("Deterministic runner pass", runner_proc.returncode == 0))
    if runner_proc.returncode != 0:
        errors.append(runner_proc.stdout[-3000:] or runner_proc.stderr[-3000:] or "runner failed")

    if AIRPORT_PROJECTION.is_file():
        _append_projection_checks(checks)
        before = AIRPORT_PROJECTION.read_text(encoding="utf-8")
        second = _run(["python3", str(RUNNER)], env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")})
        after = AIRPORT_PROJECTION.read_text(encoding="utf-8")
        checks.append(("Repeated generation byte-identical", second.returncode == 0 and before == after))
        if second.returncode != 0 or before != after:
            errors.append("projection generation is not byte-identical")

    print("ONE_AIRPORT_A3_01_CANONICAL_ALARM_EVENT_INTAKE_FOUNDATION_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("CANONICAL_ALARM_EVENT_INTAKE_FOUNDATION_COMPLETE")
    print("ALARM_EVENT_INTAKE_CANDIDATES_COMPLETE_WITH_PENDING_REVIEWS")
    print("ONE_AIRPORT_A3_01_CANONICAL_ALARM_EVENT_INTAKE_FOUNDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
