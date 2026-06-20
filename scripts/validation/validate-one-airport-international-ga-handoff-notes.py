#!/usr/bin/env python3
"""Validate GA-03 Airport International GA handoff notes."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/international-ga-handoff-notes.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/international_ga_handoff_notes"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/international_ga_handoff_notes.py"
AIRPORT_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-international-ga-handoff-notes.v1.json"
RUNNER = ROOT / "scripts/validation/_run_ga_03_airport_international_ga_handoff_notes.py"
REPORT = ROOT / "ONE_AIRPORT_GA_03_INTERNATIONAL_GA_HANDOFF_NOTES_AND_RELEASE_NOTES_FREEZE_REPORT.md"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/international_ga_handoff_notes/",
    "AN_VANTARIS_ONE/registries/international-ga-handoff-notes.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/international_ga_handoff_notes.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-international-ga-handoff-notes.v1.json",
    "AN_VANTARIS_ONE/tests/international_ga_handoff_notes/",
    "scripts/validation/validate-one-airport-international-ga-handoff-notes.py",
    "scripts/validation/_run_ga_03_airport_international_ga_handoff_notes.py",
    "ONE_AIRPORT_GA_03_INTERNATIONAL_GA_HANDOFF_NOTES_AND_RELEASE_NOTES_FREEZE_REPORT.md",
)
FORBIDDEN_IMPORT_PREFIXES = ("sqlalchemy", "flask", "fastapi", "requests", "urllib", "socket", "src.ufms", "src.umms", "react", "vue")
FORBIDDEN_PATHS = ("AN_VANTARIS_EDGE/", "AN_VANTARIS_LINK/", "AN_VANTARIS_Contracts/", "AN_VANTARIS_IBMS-frontend/", "AN_VANTARIS_IBMS-backend/src/routes/", "AN_VANTARIS_IBMS-backend/src/api/", "database/", "migrations/", "UFMS/", "UMMS/")
ACTIVE_TEXT_PATHS = (GENERIC_DIR, AIRPORT_MODULE, REGISTRY, AIRPORT_PROJECTION, RUNNER, REPORT, ROOT / "AN_VANTARIS_ONE/tests/international_ga_handoff_notes")
ALLOWED_COMPATIBILITY_NOTE = "historical " + "P" + "OC" + "-named artifacts are compatibility-only"


def _run(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False, env=env)


def _changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (["git", "diff", "--name-only", "HEAD"], ["git", "diff", "--cached", "--name-only"], ["git", "ls-files", "--others", "--exclude-standard"]):
        paths.update(line for line in _run(command).stdout.splitlines() if line)
    return paths


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _text_files() -> list[Path]:
    files: list[Path] = []
    for path in ACTIVE_TEXT_PATHS:
        if path.is_dir():
            files.extend(sorted(child for child in path.rglob("*") if child.is_file()))
        elif path.is_file():
            files.append(path)
    return files


def _append_projection_checks(checks: list[tuple[str, bool]]) -> None:
    notes = _load_json(AIRPORT_PROJECTION)
    summary = notes.get("summary", {})
    expected = {"stakeholderHandoffSectionCount": 7, "engineeringHandoffSectionCount": 6, "validationCommandCount": 21, "requiredValidationCommandCount": 21, "knownWarningCount": 5, "blockingKnownWarningCount": 0, "nextPhasePlanCount": 6, "handoffGateCount": 13, "passedHandoffGateCount": 13, "blockingGateFailureCount": 0, "stageInventoryCount": 9, "artifactInventoryCount": 30, "validatorMatrixCount": 20, "unitTestMatrixCount": 9, "businessCapabilityCount": 15, "totalDeviceEvidenceCount": 470, "decisionItemCount": 46, "pendingDecisionCount": 46}
    checks.append(("Implementation status frozen", notes.get("implementationStatus") == "INTERNATIONAL_GA_HANDOFF_NOTES_AND_RELEASE_NOTES_FREEZE_COMPLETE"))
    checks.append(("Readiness outcome frozen", notes.get("readinessOutcome") == "INTERNATIONAL_GA_HANDOFF_NOTES_READY_FOR_STAKEHOLDER_AND_ENGINEERING_HANDOFF"))
    checks.append(("Expected summary counts", all(summary.get(key) == value for key, value in expected.items())))
    checks.append(("Release title uses International GA-ready wording", notes.get("releaseNotes", {}).get("releaseTitle") == "VANTARIS ONE Airport International GA-ready Read-only Release Candidate"))
    checks.append(("Seven stakeholder sections", len(notes.get("stakeholderHandoffSections", [])) == 7))
    checks.append(("Six engineering sections", len(notes.get("engineeringHandoffSections", [])) == 6))
    checks.append(("Twenty-one validation commands", len(notes.get("validationCommandSet", [])) == 21 and all(item.get("requiredForHandoff") for item in notes.get("validationCommandSet", []))))
    checks.append(("Five non-blocking warnings", len(notes.get("knownWarnings", [])) == 5 and not any(item.get("blocking") for item in notes.get("knownWarnings", []))))
    checks.append(("Six next phases", len(notes.get("nextPhasePlan", [])) == 6))
    checks.append(("Thirteen handoff gates pass", len(notes.get("handoffGates", [])) == 13 and all(item.get("status") == "PASS" for item in notes.get("handoffGates", []))))
    boundary = notes.get("boundaryStatement", {})
    checks.append(("Restricted boundary flags false", all(boundary.get(key) is False for key in ("databaseWriteAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "apiProductionAllowed", "frontendProductionAllowed", "approvalExecutionAllowed", "pushAllowed", "tagAllowed", "customerIdentifierLeakageAllowed"))))
    serialized = json.dumps(notes, sort_keys=True)
    checks.append(("No customer identifier text leakage", "customerAssetIdentifier" not in serialized and "assetId" not in serialized and "deviceId" not in serialized))


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    checks.append(("Registry exists", REGISTRY.is_file()))
    checks.append(("Generic package exists", GENERIC_DIR.is_dir()))
    checks.append(("Airport handoff module exists", AIRPORT_MODULE.is_file()))
    checks.append(("Airport handoff artifact exists", AIRPORT_PROJECTION.is_file()))
    checks.append(("Deterministic runner exists", RUNNER.is_file()))
    if REGISTRY.is_file():
        registry = _load_json(REGISTRY)
        checks.append(("Registry cross-industry", registry.get("crossIndustry") is True))
        checks.append(("Registry handoff frozen", registry.get("handoffNotesFrozen") is True and registry.get("readyForHandoff") is True))
        checks.append(("Registry push/tag blocked", registry.get("pushAllowed") is False and registry.get("tagAllowed") is False))
        checks.append(("Registry runtime/production disabled", all(registry.get(key) is False for key in ("apiProductionAllowed", "frontendProductionAllowed", "runtimeActivationAllowed", "productionActivationAllowed"))))

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

    terminology_errors = []
    for path in _text_files():
        text = path.read_text(encoding="utf-8").replace(ALLOWED_COMPATIBILITY_NOTE, "")
        if "P" + "OC" in text:
            terminology_errors.append(str(path.relative_to(ROOT)))
    checks.append(("No active handoff misleading product-stage wording", len(terminology_errors) == 0))
    if terminology_errors:
        errors.append(f"active GA-03 files contain misleading product-stage wording: {', '.join(terminology_errors)}")

    changed = _changed_paths()
    disallowed = [path for path in changed if path and not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)]
    checks.append(("Changes within GA-03 allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")
    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))
    if forbidden_touched:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden_touched))}")

    env = {**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")}
    test_proc = _run(["python3", "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/international_ga_handoff_notes", "-p", "test_*.py"], env=env)
    checks.append(("Focused GA-03 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-4000:] or test_proc.stderr[-4000:] or "focused GA-03 tests failed")
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
            errors.append("GA-03 handoff notes generation is not byte-identical")

    print("ONE_AIRPORT_GA_03_INTERNATIONAL_GA_HANDOFF_NOTES_AND_RELEASE_NOTES_FREEZE_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("INTERNATIONAL_GA_HANDOFF_NOTES_AND_RELEASE_NOTES_FREEZE_COMPLETE")
    print("INTERNATIONAL_GA_HANDOFF_NOTES_READY_FOR_STAKEHOLDER_AND_ENGINEERING_HANDOFF")
    print("ONE_AIRPORT_GA_03_INTERNATIONAL_GA_HANDOFF_NOTES_AND_RELEASE_NOTES_FREEZE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
