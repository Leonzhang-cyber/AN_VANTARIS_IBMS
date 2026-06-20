#!/usr/bin/env python3
"""Validate GA-02 Airport International GA release candidate package."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/international-ga-release-candidate-package.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/international_ga_release_package"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/international_ga_release_package.py"
AIRPORT_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-international-ga-release-candidate-package.v1.json"
RUNNER = ROOT / "scripts/validation/_run_ga_02_airport_international_ga_release_package.py"
REPORT = ROOT / "ONE_AIRPORT_GA_02_INTERNATIONAL_GA_RELEASE_CANDIDATE_PACKAGING_AND_VALIDATION_MATRIX_REPORT.md"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/international_ga_release_package/",
    "AN_VANTARIS_ONE/registries/international-ga-release-candidate-package.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/international_ga_release_package.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-international-ga-release-candidate-package.v1.json",
    "AN_VANTARIS_ONE/tests/international_ga_release_package/",
    "scripts/validation/validate-one-airport-international-ga-release-package.py",
    "scripts/validation/_run_ga_02_airport_international_ga_release_package.py",
    "ONE_AIRPORT_GA_02_INTERNATIONAL_GA_RELEASE_CANDIDATE_PACKAGING_AND_VALIDATION_MATRIX_REPORT.md",
)
FORBIDDEN_IMPORT_PREFIXES = ("sqlalchemy", "flask", "fastapi", "requests", "urllib", "socket", "src.ufms", "src.umms", "react", "vue")
FORBIDDEN_PATHS = ("AN_VANTARIS_EDGE/", "AN_VANTARIS_LINK/", "AN_VANTARIS_Contracts/", "AN_VANTARIS_IBMS-frontend/", "AN_VANTARIS_IBMS-backend/src/routes/", "AN_VANTARIS_IBMS-backend/src/api/", "database/", "migrations/", "UFMS/", "UMMS/")
ACTIVE_TEXT_PATHS = (GENERIC_DIR, AIRPORT_MODULE, REGISTRY, AIRPORT_PROJECTION, RUNNER, REPORT, ROOT / "AN_VANTARIS_ONE/tests/international_ga_release_package")


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
    package = _load_json(AIRPORT_PROJECTION)
    summary = package.get("summary", {})
    checks.append(("Implementation status frozen", package.get("implementationStatus") == "INTERNATIONAL_GA_RELEASE_CANDIDATE_PACKAGING_AND_VALIDATION_MATRIX_COMPLETE"))
    checks.append(("Readiness outcome frozen", package.get("readinessOutcome") == "INTERNATIONAL_GA_RELEASE_CANDIDATE_PACKAGE_READY_FOR_HANDOFF"))
    expected = {"stageInventoryCount": 9, "activeStageCount": 9, "failedStageCount": 0, "artifactInventoryCount": 30, "requiredArtifactCount": 30, "presentRequiredArtifactCount": 30, "validatorMatrixCount": 20, "requiredValidatorCount": 20, "passedValidatorCount": 20, "unitTestMatrixCount": 9, "handoffInventoryCount": 6, "packagingGateCount": 18, "passedPackagingGateCount": 18, "blockingGateFailureCount": 0, "totalDeviceEvidenceCount": 470, "decisionItemCount": 46, "queueRowCount": 46}
    checks.append(("Expected package summary counts", all(summary.get(key) == value for key, value in expected.items())))
    checks.append(("Thirty active required artifacts", len(package.get("artifactInventory", [])) == 30 and all(item.get("required") and item.get("present") and item.get("active") and not item.get("legacyCompatibility") for item in package.get("artifactInventory", []))))
    checks.append(("No required artifact uses superseded wording", all("poc" not in item.get("artifactPath", "").lower() for item in package.get("artifactInventory", []) if item.get("required"))))
    checks.append(("Twenty validators pass", len(package.get("validatorMatrix", [])) == 20 and all(item.get("requiredForGa") and item.get("status") == "PASS" for item in package.get("validatorMatrix", []))))
    checks.append(("Nine unit test suites represented", len(package.get("unitTestMatrix", [])) == 9))
    checks.append(("Six handoff entries", len(package.get("handoffInventory", [])) == 6))
    checks.append(("Eighteen packaging gates pass", len(package.get("packagingGates", [])) == 18 and all(item.get("status") == "PASS" for item in package.get("packagingGates", []))))
    decision = package.get("releaseDecision", {})
    checks.append(("Release package decision pass", decision.get("decisionState") == "INTERNATIONAL_GA_RELEASE_PACKAGE_PASS" and decision.get("internationalGaPackageAllowed") is True and decision.get("internationalGaReadinessAllowed") is True and decision.get("releaseCandidateAllowed") is True))
    checks.append(("Push/tag/production/runtime blocked", all(decision.get(key) is False for key in ("pushAllowed", "tagAllowed", "productionActivationAllowed", "runtimeActivationAllowed", "databaseWriteAllowed", "apiProductionAllowed", "frontendProductionAllowed", "approvalExecutionAllowed"))))
    serialized = json.dumps(package, sort_keys=True)
    checks.append(("No customer identifier text leakage", "customerAssetIdentifier" not in serialized and "assetId" not in serialized and "deviceId" not in serialized))


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    checks.append(("Registry exists", REGISTRY.is_file()))
    checks.append(("Generic package exists", GENERIC_DIR.is_dir()))
    checks.append(("Airport package module exists", AIRPORT_MODULE.is_file()))
    checks.append(("Airport package artifact exists", AIRPORT_PROJECTION.is_file()))
    checks.append(("Deterministic runner exists", RUNNER.is_file()))
    if REGISTRY.is_file():
        registry = _load_json(REGISTRY)
        checks.append(("Registry cross-industry", registry.get("crossIndustry") is True))
        checks.append(("Registry package allowed", registry.get("internationalGaPackageAllowed") is True))
        checks.append(("Registry push/tag blocked", registry.get("pushAllowed") is False and registry.get("tagAllowed") is False))
        checks.append(("Registry runtime/production disabled", all(registry.get(key) is False for key in ("apiEnabled", "frontendEnabled", "productionApiAllowed", "productionFrontendAllowed", "runtimeActivationAllowed", "productionActivationAllowed"))))

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

    terminology_errors = [str(path.relative_to(ROOT)) for path in _text_files() if "POC" in path.read_text(encoding="utf-8")]
    checks.append(("No active package misleading product-stage wording", len(terminology_errors) == 0))
    if terminology_errors:
        errors.append(f"active package files contain misleading product-stage wording: {', '.join(terminology_errors)}")

    changed = _changed_paths()
    disallowed = [path for path in changed if path and not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)]
    checks.append(("Changes within GA-02 allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")
    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))
    if forbidden_touched:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden_touched))}")

    env = {**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")}
    test_proc = _run(["python3", "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/international_ga_release_package", "-p", "test_*.py"], env=env)
    checks.append(("Focused GA-02 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-4000:] or test_proc.stderr[-4000:] or "focused GA-02 tests failed")
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
            errors.append("GA-02 package generation is not byte-identical")

    print("ONE_AIRPORT_GA_02_INTERNATIONAL_GA_RELEASE_CANDIDATE_PACKAGING_AND_VALIDATION_MATRIX_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("INTERNATIONAL_GA_RELEASE_CANDIDATE_PACKAGING_AND_VALIDATION_MATRIX_COMPLETE")
    print("INTERNATIONAL_GA_RELEASE_CANDIDATE_PACKAGE_READY_FOR_HANDOFF")
    print("ONE_AIRPORT_GA_02_INTERNATIONAL_GA_RELEASE_CANDIDATE_PACKAGING_AND_VALIDATION_MATRIX_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
