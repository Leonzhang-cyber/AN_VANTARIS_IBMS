#!/usr/bin/env python3
"""Validate GA-04 Airport International GA final local verification."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/international-ga-final-local-verification.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/international_ga_final_verification"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/international_ga_final_verification.py"
AIRPORT_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-international-ga-final-local-verification.v1.json"
RUNNER = ROOT / "scripts/validation/_run_ga_04_airport_international_ga_final_verification.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/international_ga_final_verification/",
    "AN_VANTARIS_ONE/registries/international-ga-final-local-verification.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/international_ga_final_verification.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-international-ga-final-local-verification.v1.json",
    "AN_VANTARIS_ONE/tests/international_ga_final_verification/",
    "scripts/validation/validate-one-airport-international-ga-final-verification.py",
    "scripts/validation/_run_ga_04_airport_international_ga_final_verification.py",
    "ONE_AIRPORT_GA_04_INTERNATIONAL_GA_FINAL_LOCAL_VERIFICATION_AND_OPTIONAL_RELEASE_TAG_PLAN_REPORT.md",
)
FORBIDDEN_IMPORT_PREFIXES = ("sqlalchemy", "flask", "fastapi", "requests", "urllib", "socket", "src.ufms", "src.umms", "react", "vue")
FORBIDDEN_PATHS = ("AN_VANTARIS_EDGE/", "AN_VANTARIS_LINK/", "AN_VANTARIS_Contracts/", "AN_VANTARIS_IBMS-frontend/", "AN_VANTARIS_IBMS-backend/src/routes/", "AN_VANTARIS_IBMS-backend/src/api/", "database/", "migrations/", "UFMS/", "UMMS/")


def _run(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False, env=env)


def _changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (["git", "diff", "--name-only", "HEAD"], ["git", "diff", "--cached", "--name-only"], ["git", "ls-files", "--others", "--exclude-standard"]):
        paths.update(line for line in _run(command).stdout.splitlines() if line)
    return paths


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    checks.append(("Registry exists", REGISTRY.is_file()))
    checks.append(("Generic package exists", GENERIC_DIR.is_dir()))
    checks.append(("Airport module exists", AIRPORT_MODULE.is_file()))
    checks.append(("Airport projection exists", AIRPORT_PROJECTION.is_file()))
    checks.append(("Deterministic runner exists", RUNNER.is_file()))

    import_errors = []
    for path in list(GENERIC_DIR.glob("*.py")) + [AIRPORT_MODULE, RUNNER]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else ([node.module or ""] if isinstance(node, ast.ImportFrom) else [])
            for name in names:
                if any(name.startswith(prefix) for prefix in FORBIDDEN_IMPORT_PREFIXES):
                    import_errors.append(f"{path.relative_to(ROOT)}: {name}")
    checks.append(("No forbidden runtime imports", not import_errors))
    errors.extend(import_errors)

    changed = _changed_paths()
    disallowed = [p for p in changed if p and not any(p.startswith(prefix) for prefix in ALLOWED_PREFIXES)]
    checks.append(("Changes within GA-04 allowed paths", not disallowed))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")
    forbidden_touched = [p for p in changed if any(p.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", not forbidden_touched))
    if forbidden_touched:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden_touched))}")

    env = {**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")}
    test_proc = _run(["python3", "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/international_ga_final_verification", "-p", "test_*.py"], env=env)
    checks.append(("Focused GA-04 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-4000:] or test_proc.stderr[-4000:] or "focused GA-04 tests failed")
    runner_proc = _run(["python3", str(RUNNER)], env=env)
    checks.append(("Deterministic runner pass", runner_proc.returncode == 0))
    if runner_proc.returncode != 0:
        errors.append(runner_proc.stdout[-4000:] or runner_proc.stderr[-4000:] or "runner failed")

    if AIRPORT_PROJECTION.is_file():
        artifact = json.loads(AIRPORT_PROJECTION.read_text(encoding="utf-8"))
        s = artifact["summary"]
        checks.append(("Expected summary counts", s.get("localVerificationEntryCount") == 18 and s.get("commitChainEntryCount") == 12 and s.get("activeArtifactSnapshotCount") == 10 and s.get("verificationGateCount") == 15))
        checks.append(("Tag and push are plan-only", artifact["optionalTagPlan"]["tagAllowedNow"] is False and artifact["optionalPushPlan"]["pushAllowedNow"] is False and artifact["optionalTagPlan"]["requiresExplicitUserApproval"] is True and artifact["optionalPushPlan"]["requiresExplicitUserApproval"] is True))
        checks.append(("Final decision pass", artifact["finalReleaseDecision"]["decisionState"] == "INTERNATIONAL_GA_LOCAL_VERIFICATION_PASS" and artifact["finalReleaseDecision"]["internationalGaReleaseCandidateReady"] is True))
        serialized = json.dumps(artifact, sort_keys=True)
        checks.append(("No customer identifier text leakage", "customerAssetIdentifier" not in serialized and "assetId" not in serialized and "deviceId" not in serialized))
        before = AIRPORT_PROJECTION.read_text(encoding="utf-8")
        second = _run(["python3", str(RUNNER)], env=env)
        after = AIRPORT_PROJECTION.read_text(encoding="utf-8")
        checks.append(("Repeated generation byte-identical", second.returncode == 0 and before == after))
        if second.returncode != 0 or before != after:
            errors.append("GA-04 generation is not byte-identical")

    print("ONE_AIRPORT_GA_04_INTERNATIONAL_GA_FINAL_LOCAL_VERIFICATION_AND_OPTIONAL_RELEASE_TAG_PLAN_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("INTERNATIONAL_GA_FINAL_LOCAL_VERIFICATION_AND_OPTIONAL_RELEASE_TAG_PLAN_COMPLETE")
    print("INTERNATIONAL_GA_LOCAL_VERIFICATION_PASS_READY_FOR_EXPLICIT_PUSH_TAG_DECISION")
    print("ONE_AIRPORT_GA_04_INTERNATIONAL_GA_FINAL_LOCAL_VERIFICATION_AND_OPTIONAL_RELEASE_TAG_PLAN_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
