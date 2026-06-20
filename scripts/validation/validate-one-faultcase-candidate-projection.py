#!/usr/bin/env python3
"""Validate A3-03 UFMS FaultCase candidate projection."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/ufms-faultcase-candidate-projection.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/faultcase_candidate"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/faultcase_candidate_projection.py"
AIRPORT_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-faultcase-candidates.v1.json"
RUNNER = ROOT / "scripts/validation/_run_a3_03_faultcase_candidate_projection.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/faultcase_candidate/",
    "AN_VANTARIS_ONE/registries/ufms-faultcase-candidate-projection.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/faultcase_candidate_projection.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-faultcase-candidates.v1.json",
    "AN_VANTARIS_ONE/tests/faultcase_candidate/",
    "scripts/validation/validate-one-faultcase-candidate-projection.py",
    "scripts/validation/_run_a3_03_faultcase_candidate_projection.py",
    "ONE_AIRPORT_A3_03_UFMS_FAULTCASE_CANDIDATE_PROJECTION_REPORT.md",
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
    candidates = projection.get("faultCaseCandidates", [])
    cards = projection.get("reviewCards", [])
    by_key = {candidate.get("sourceSystemKey"): candidate for candidate in candidates}
    by_card = {card.get("reviewType"): card for card in cards}

    checks.append(("Implementation status frozen", projection.get("implementationStatus") == "UFMS_FAULTCASE_CANDIDATE_PROJECTION_COMPLETE"))
    checks.append(("Readiness outcome frozen", projection.get("readinessOutcome") == "FAULTCASE_CANDIDATES_COMPLETE_WITH_PENDING_REVIEWS"))
    checks.append(("Five candidates", len(candidates) == 5 and summary.get("faultCaseCandidateCount") == 5))
    checks.append(("Eight review cards", len(cards) == 8 and summary.get("reviewCardCount") == 8))
    checks.append(("Total evidence 470", summary.get("totalDeviceEvidenceCount") == 470))
    checks.append(("Expected source keys", set(by_key) == {"ACS", "RAS", "CCTV", "PA", "TEL"}))
    checks.append(("Expected fault types", {key: by_key.get(key, {}).get("proposedFaultCaseType") for key in ("ACS", "RAS", "CCTV", "PA", "TEL")} == {"ACS": "SECURITY_FAULT", "RAS": "COMMUNICATION_FAULT", "CCTV": "SECURITY_FAULT", "PA": "EQUIPMENT_FAULT", "TEL": "COMMUNICATION_FAULT"}))
    checks.append(("Fault type counts", summary.get("securityFaultCandidateCount") == 2 and summary.get("communicationFaultCandidateCount") == 2 and summary.get("equipmentFaultCandidateCount") == 1))
    checks.append(("All decision required", summary.get("decisionRequiredCount") == 5 and all(candidate.get("decisionRequired") is True for candidate in candidates)))
    checks.append(("All blocked/review-only", all(candidate.get("proposedFaultState") in {"REVIEW_REQUIRED", "BLOCKED"} for candidate in candidates)))
    checks.append(("Blocked by resolution", summary.get("blockedByResolutionCount") == 5))
    checks.append(("Blocked by source-system review", summary.get("blockedBySourceSystemReviewCount") == 5))
    checks.append(("Downstream not authorized", all(candidate.get("downstreamCreationState") == "NOT_AUTHORIZED" for candidate in candidates)))
    for key in ("ufmsFaultCaseCreatedCount", "workOrderIntentCreatedCount", "workOrderCreatedCount", "canonicalWriteCount", "databaseWriteCount", "runtimeAlarmObservedCount"):
        checks.append((f"{key} zero", summary.get(key) == 0))
    checks.append(("No customer identifiers", summary.get("containsCustomerAssetIdentifiers") is False))
    checks.append(("Cross-industry true", summary.get("crossIndustry") is True))
    checks.append(("Airport-specific false", summary.get("airportSpecific") is False))
    checks.append(("Deterministic ordering", candidates == sorted(candidates, key=lambda item: (item["sourceSystemKey"], item["candidateId"]))))
    checks.append(("Expected review cards", set(by_card) == {
        "FAULTCASE_CREATION_NOT_AUTHORIZED",
        "SOURCE_SYSTEM_REVIEW_REQUIRED",
        "ASSET_RESOLUTION_REQUIRED",
        "POINT_RESOLUTION_REQUIRED",
        "LOCATION_RESOLUTION_REQUIRED",
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
    checks.append(("Changes within A3-03 allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")
    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))
    if forbidden_touched:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden_touched))}")

    test_proc = _run(["python3", "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/faultcase_candidate", "-p", "test_*.py"], env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")})
    checks.append(("Focused A3-03 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-4000:] or test_proc.stderr[-4000:] or "focused A3-03 tests failed")
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

    print("ONE_AIRPORT_A3_03_UFMS_FAULTCASE_CANDIDATE_PROJECTION_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("UFMS_FAULTCASE_CANDIDATE_PROJECTION_COMPLETE")
    print("FAULTCASE_CANDIDATES_COMPLETE_WITH_PENDING_REVIEWS")
    print("ONE_AIRPORT_A3_03_UFMS_FAULTCASE_CANDIDATE_PROJECTION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
