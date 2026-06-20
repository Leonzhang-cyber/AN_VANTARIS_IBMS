#!/usr/bin/env python3
"""Validate A3-05 Evidence Linkage and Investigation Projection."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/evidence-investigation-projection.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/evidence_investigation_projection"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/evidence_investigation_projection.py"
AIRPORT_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-evidence-investigation.v1.json"
RUNNER = ROOT / "scripts/validation/_run_a3_05_evidence_investigation_projection.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/evidence_investigation_projection/",
    "AN_VANTARIS_ONE/registries/evidence-investigation-projection.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/evidence_investigation_projection.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-evidence-investigation.v1.json",
    "AN_VANTARIS_ONE/tests/evidence_investigation_projection/",
    "scripts/validation/validate-one-evidence-investigation-projection.py",
    "scripts/validation/_run_a3_05_evidence_investigation_projection.py",
    "ONE_AIRPORT_A3_05_EVIDENCE_LINKAGE_AND_INVESTIGATION_PROJECTION_REPORT.md",
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
    cases = projection.get("investigationCases", [])
    links = projection.get("evidenceLinks", [])
    timeline = projection.get("investigationTimeline", [])
    cards = projection.get("reviewCards", [])
    by_key = {case.get("sourceSystemKey"): case for case in cases}
    by_card = {card.get("reviewType"): card for card in cards}
    checks.append(("Implementation status frozen", projection.get("implementationStatus") == "EVIDENCE_INVESTIGATION_PROJECTION_COMPLETE"))
    checks.append(("Readiness outcome frozen", projection.get("readinessOutcome") == "EVIDENCE_INVESTIGATION_LINKAGE_COMPLETE_WITH_PENDING_REVIEWS"))
    checks.append(("Five cases", len(cases) == 5 and summary.get("investigationCaseCount") == 5))
    checks.append(("At least twenty links", len(links) >= 20 and summary.get("evidenceLinkCount") == len(links)))
    checks.append(("At least twenty timeline items", len(timeline) >= 20 and summary.get("timelineItemCount") == len(timeline)))
    checks.append(("Nine review cards", len(cards) == 9 and summary.get("reviewCardCount") == 9))
    checks.append(("Total evidence 470", summary.get("totalDeviceEvidenceCount") == 470))
    checks.append(("Expected source counts", {key: by_key.get(key, {}).get("deviceEvidenceCount") for key in ("ACS", "RAS", "CCTV", "PA", "TEL")} == {"ACS": 129, "RAS": 28, "CCTV": 52, "PA": 247, "TEL": 14}))
    checks.append(("All decision required", summary.get("decisionRequiredCount") == 5 and all(case.get("decisionRequired") is True for case in cases)))
    checks.append(("Partial evidence count", summary.get("partialEvidenceCaseCount") == 5))
    checks.append(("Linked case count", summary.get("linkedCaseCount") == 5))
    checks.append(("Registry pending count", summary.get("registryApprovalPendingCount") == 2))
    checks.append(("Alias pending count", summary.get("aliasApprovalPendingCount") == 2))
    checks.append(("Namespace pending count", summary.get("namespaceReviewPendingCount") == 1))
    for key in ("evidenceCenterWriteCount", "ufmsFaultCaseCreatedCount", "workOrderIntentCreatedCount", "workOrderCreatedCount", "ummsWriteCount", "oneWorkManagementWriteCount", "canonicalWriteCount", "databaseWriteCount", "runtimeAlarmObservedCount"):
        checks.append((f"{key} zero", summary.get(key) == 0))
    checks.append(("No customer identifiers", summary.get("containsCustomerAssetIdentifiers") is False))
    checks.append(("Cross-industry true", summary.get("crossIndustry") is True))
    checks.append(("Airport-specific false", summary.get("airportSpecific") is False))
    checks.append(("Deterministic case ordering", cases == sorted(cases, key=lambda item: (item["sourceSystemKey"], item["investigationCaseId"]))))
    checks.append(("Expected review cards", set(by_card) == {
        "INVESTIGATION_REVIEW_REQUIRED",
        "EVIDENCE_CENTER_WRITE_NOT_AUTHORIZED",
        "FAULTCASE_REVIEW_REQUIRED",
        "WORKORDER_INTENT_REVIEW_REQUIRED",
        "ASSET_RESOLUTION_REQUIRED",
        "SOURCE_SYSTEM_REVIEW_REQUIRED",
        "REGISTRY_APPROVAL_REQUIRED",
        "ALIAS_APPROVAL_REQUIRED",
        "NAMESPACE_INTERPRETATION_REQUIRED",
    }))


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
    checks.append(("Changes within A3-05 allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")
    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))
    if forbidden_touched:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden_touched))}")

    test_proc = _run(["python3", "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/evidence_investigation_projection", "-p", "test_*.py"], env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")})
    checks.append(("Focused A3-05 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-4000:] or test_proc.stderr[-4000:] or "focused A3-05 tests failed")
    runner_proc = _run(["python3", str(RUNNER)], env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")})
    checks.append(("Deterministic runner pass", runner_proc.returncode == 0))
    if runner_proc.returncode != 0:
        errors.append(runner_proc.stdout[-4000:] or runner_proc.stderr[-4000:] or "runner failed")
    if AIRPORT_PROJECTION.is_file():
        _append_projection_checks(checks)
        before = AIRPORT_PROJECTION.read_text(encoding="utf-8")
        second = _run(["python3", str(RUNNER)], env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")})
        after = AIRPORT_PROJECTION.read_text(encoding="utf-8")
        checks.append(("Repeated generation byte-identical", second.returncode == 0 and before == after))
        if second.returncode != 0 or before != after:
            errors.append("projection generation is not byte-identical")

    print("ONE_AIRPORT_A3_05_EVIDENCE_LINKAGE_AND_INVESTIGATION_PROJECTION_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("EVIDENCE_INVESTIGATION_PROJECTION_COMPLETE")
    print("EVIDENCE_INVESTIGATION_LINKAGE_COMPLETE_WITH_PENDING_REVIEWS")
    print("ONE_AIRPORT_A3_05_EVIDENCE_LINKAGE_AND_INVESTIGATION_PROJECTION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
