#!/usr/bin/env python3
"""Validate A3-02 alarm/event asset resolution review projection."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/alarm-event-asset-resolution-review.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/alarm_event_resolution"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/alarm_event_asset_resolution_projection.py"
AIRPORT_PROJECTION = (
    ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-alarm-event-asset-resolution-review.v1.json"
)
RUNNER = ROOT / "scripts/validation/_run_a3_02_alarm_event_asset_resolution.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/alarm_event_resolution/",
    "AN_VANTARIS_ONE/registries/alarm-event-asset-resolution-review.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/alarm_event_asset_resolution_projection.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-alarm-event-asset-resolution-review.v1.json",
    "AN_VANTARIS_ONE/tests/alarm_event_resolution/",
    "scripts/validation/validate-one-alarm-event-asset-resolution-review.py",
    "scripts/validation/_run_a3_02_alarm_event_asset_resolution.py",
    "ONE_AIRPORT_A3_02_ALARM_EVENT_ASSET_RESOLUTION_REVIEW_PROJECTION_REPORT.md",
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
    rows = projection.get("resolutionRows", [])
    cards = projection.get("reviewCards", [])
    by_key = {row.get("sourceSystemKey"): row for row in rows}
    by_card = {card.get("reviewType"): card for card in cards}

    checks.append(("Implementation status frozen", projection.get("implementationStatus") == "ALARM_EVENT_ASSET_RESOLUTION_REVIEW_PROJECTION_COMPLETE"))
    checks.append(("Readiness outcome frozen", projection.get("readinessOutcome") == "ALARM_EVENT_RESOLUTION_REVIEW_COMPLETE_WITH_PENDING_DECISIONS"))
    checks.append(("Five resolution rows", len(rows) == 5 and summary.get("resolutionRowCount") == 5))
    checks.append(("Seven review cards", len(cards) == 7 and summary.get("reviewCardCount") == 7))
    checks.append(("Five alarm/event candidates", summary.get("alarmEventCandidateCount") == 5))
    checks.append(("Total evidence 470", summary.get("totalDeviceEvidenceCount") == 470))
    checks.append(("Expected evidence counts", {key: by_key.get(key, {}).get("deviceEvidenceCount") for key in ("ACS", "RAS", "CCTV", "PA", "TEL")} == {"ACS": 129, "RAS": 28, "CCTV": 52, "PA": 247, "TEL": 14}))
    checks.append(("Resolution states pending", all(row.get("assetResolutionState") in {"REVIEW_REQUIRED", "UNRESOLVED"} and row.get("pointResolutionState") in {"REVIEW_REQUIRED", "UNRESOLVED"} and row.get("locationResolutionState") in {"REVIEW_REQUIRED", "UNRESOLVED"} for row in rows)))
    checks.append(("Downstream not authorized", all(row.get("downstreamCreationState") == "NOT_AUTHORIZED" for row in rows)))
    checks.append(("All decisions required", all(row.get("decisionRequired") is True for row in rows)))
    checks.append(("Registry pending count", summary.get("registryApprovalPendingCount") == 2))
    checks.append(("Alias pending count", summary.get("aliasApprovalPendingCount") == 2))
    checks.append(("Namespace pending count", summary.get("namespaceReviewPendingCount") == 1))
    checks.append(("Resolution required counts", summary.get("assetResolutionRequiredCount") == 5 and summary.get("pointResolutionRequiredCount") == 5 and summary.get("locationResolutionRequiredCount") == 5))
    checks.append(("Downstream count", summary.get("downstreamCreationNotAuthorizedCount") == 5))
    checks.append(("Zero UFMS FaultCases", summary.get("ufmsFaultCaseCreatedCount") == 0))
    checks.append(("Zero WorkOrderIntents", summary.get("workOrderIntentCreatedCount") == 0))
    checks.append(("Zero WorkOrders", summary.get("workOrderCreatedCount") == 0))
    checks.append(("Zero canonical writes", summary.get("canonicalWriteCount") == 0))
    checks.append(("Zero DB writes", summary.get("databaseWriteCount") == 0))
    checks.append(("Zero runtime alarms", summary.get("runtimeAlarmObservedCount") == 0))
    checks.append(("No customer asset identifiers", summary.get("containsCustomerAssetIdentifiers") is False))
    checks.append(("Cross-industry true", summary.get("crossIndustry") is True))
    checks.append(("Airport-specific false", summary.get("airportSpecific") is False))
    checks.append(("Deterministic ordering", rows == sorted(rows, key=lambda row: (row["sourceSystemKey"], row["rowId"]))))
    checks.append(("Expected review cards", set(by_card) == {
        "REGISTRY_APPROVAL_REQUIRED",
        "ALIAS_APPROVAL_REQUIRED",
        "NAMESPACE_INTERPRETATION_REQUIRED",
        "ASSET_RESOLUTION_REQUIRED",
        "POINT_RESOLUTION_REQUIRED",
        "LOCATION_RESOLUTION_REQUIRED",
        "DOWNSTREAM_CREATION_NOT_AUTHORIZED",
    }))
    checks.append(("Aggregated review cards", by_card.get("REGISTRY_APPROVAL_REQUIRED", {}).get("affectedSourceSystemKeys") == ["ACS", "RAS"] and by_card.get("ALIAS_APPROVAL_REQUIRED", {}).get("affectedSourceSystemKeys") == ["CCTV", "PA"] and by_card.get("NAMESPACE_INTERPRETATION_REQUIRED", {}).get("affectedSourceSystemKeys") == ["TEL"]))


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
    checks.append(("Changes within A3-02 allowed paths", len(disallowed) == 0))
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
            "AN_VANTARIS_ONE/tests/alarm_event_resolution",
            "-p",
            "test_*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")},
    )
    checks.append(("Focused A3-02 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-3500:] or test_proc.stderr[-3500:] or "focused A3-02 tests failed")

    runner_proc = _run(["python3", str(RUNNER)], env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")})
    checks.append(("Deterministic runner pass", runner_proc.returncode == 0))
    if runner_proc.returncode != 0:
        errors.append(runner_proc.stdout[-3500:] or runner_proc.stderr[-3500:] or "runner failed")

    if AIRPORT_PROJECTION.is_file():
        _append_projection_checks(checks)
        before = AIRPORT_PROJECTION.read_text(encoding="utf-8")
        second = _run(["python3", str(RUNNER)], env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")})
        after = AIRPORT_PROJECTION.read_text(encoding="utf-8")
        checks.append(("Repeated generation byte-identical", second.returncode == 0 and before == after))
        if second.returncode != 0 or before != after:
            errors.append("projection generation is not byte-identical")

    print("ONE_AIRPORT_A3_02_ALARM_EVENT_ASSET_RESOLUTION_REVIEW_PROJECTION_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("ALARM_EVENT_ASSET_RESOLUTION_REVIEW_PROJECTION_COMPLETE")
    print("ALARM_EVENT_RESOLUTION_REVIEW_COMPLETE_WITH_PENDING_DECISIONS")
    print("ONE_AIRPORT_A3_02_ALARM_EVENT_ASSET_RESOLUTION_REVIEW_PROJECTION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
