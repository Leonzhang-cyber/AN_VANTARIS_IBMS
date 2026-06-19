#!/usr/bin/env python3
"""Validate airport asset reconciliation and readiness gate implementation."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/airport-asset-reconciliation-profile.v1.json"
MODULE_DIR = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/industry_profiles/airport_reconciliation"
TESTS_DIR = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/industry_profiles"
MODELS = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/models.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/registries/airport-asset-reconciliation-profile.v1.json",
    "AN_VANTARIS_IBMS-backend/src/asset_graph/industry_profiles/",
    "AN_VANTARIS_IBMS-backend/tests/asset_graph/industry_profiles/",
    "scripts/validation/validate-one-airport-asset-reconciliation.py",
)

FORBIDDEN_PATHS = (
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_IBMS-frontend/",
    "database/",
    "migrations/",
    "UFMS/",
)

FORBIDDEN_IMPORTS = ("sqlalchemy", "flask", "psycopg", "pymongo", "src.ufms", "src.umms")


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


def main() -> int:
    errors: list[str] = []
    checks: list[tuple[str, bool]] = []

    checks.append(("Registry exists", REGISTRY.is_file()))
    checks.append(("Module directory exists", MODULE_DIR.is_dir()))

    if REGISTRY.is_file():
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        checks.append(("INDUSTRY_PROFILE type", registry.get("profileType") == "INDUSTRY_PROFILE"))
        checks.append(("Read-only reconciliation", registry.get("implementationMode") == "READ_ONLY_RECONCILIATION"))
        checks.append(("platformCoreAirportized false", registry.get("platformCoreAirportized") is False))
        checks.append(("canonicalWriteEnabled false", registry.get("canonicalWriteEnabled") is False))
        checks.append(("databaseAccessEnabled false", registry.get("databaseAccessEnabled") is False))

    models_text = MODELS.read_text(encoding="utf-8") if MODELS.is_file() else ""
    checks.append(("Generic models unchanged", "SCN" not in models_text and "CCT" not in models_text))

    import_errors: list[str] = []
    for path in MODULE_DIR.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            if isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            for name in names:
                if any(name.startswith(prefix) for prefix in FORBIDDEN_IMPORTS):
                    import_errors.append(f"{path.name}: {name}")
    checks.append(("No DB/ORM imports", len(import_errors) == 0))
    errors.extend(import_errors)

    module_text = " ".join(path.read_text(encoding="utf-8") for path in MODULE_DIR.rglob("*.py"))
    checks.append(("No provider writes", "InMemoryAssetGraphProvider" not in module_text))
    checks.append(("No public API routes", "blueprint" not in module_text.lower()))
    checks.append(("Legacy unclassified not blocker", "legacyUnclassifiedCountUsedAsBlocker" in module_text))
    checks.append(("No canonical winner auto-select", "canonicalWinnerDigest" not in module_text))
    checks.append(("SCN review preserved", "SCN_SEMANTIC_REVIEW_REQUIRED" in module_text))
    checks.append(("Alias approval required", "APPROVAL_REQUIRED" in module_text))

    changed = _changed_paths()
    disallowed = [path for path in changed if path and not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)]
    checks.append(("Changes within allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")

    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))

    test_proc = _run(
        [
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "AN_VANTARIS_IBMS-backend/tests/asset_graph/industry_profiles",
            "-p",
            "test_airport_reconciliation*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
    )
    checks.append(("Focused reconciliation tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-2500:] or test_proc.stderr[-2500:] or "reconciliation tests failed")

    real_proc = _run(
        [
            "python3",
            "-c",
            (
                "import json; from pathlib import Path; "
                "import sys; sys.path.insert(0, 'AN_VANTARIS_IBMS-backend'); "
                "from src.asset_graph.industry_profiles.airport_reconciliation import run_airport_asset_reconciliation, compare_deterministic_outputs; "
                "from src.asset_graph.industry_profiles.airport_reconciliation.context import AirportReconciliationContext; "
                "ctx=AirportReconciliationContext(tenant_id='AIRPORT-TENANT-001', site_id='AIRPORT-SITE-001', source_workbook_digest='60eac97282b1cae4d1697ad1b0505d66f530a638b3de3d095f9e5f9c620a3d48'); "
                "kwargs=dict("
                "intake_evidence_path=Path('/tmp/one-airport-a1-01/run-1/airport-asset-intake-evidence.json'), "
                "spatial_result_path=Path('/tmp/one-airport-a1-02/run-1/airport-spatial-profile-result.json'), "
                "spatial_bindings_path=Path('/tmp/one-airport-a1-02/run-1/airport-device-spatial-bindings.json'), "
                "system_classification_path=Path('/tmp/one-airport-a1-03/run-1/airport-system-classification-result.json'), "
                "device_type_classification_path=Path('/tmp/one-airport-a1-03/run-1/airport-device-type-classification-result.json'), "
                "classification_bindings_path=Path('/tmp/one-airport-a1-03/run-1/airport-device-classification-bindings.json'), "
                "classification_reviews_path=Path('/tmp/one-airport-a1-03/run-1/airport-classification-review-findings.json'), "
                "classification_summary_path=Path('/tmp/one-airport-a1-03/run-1/airport-classification-summary.json'), "
                "coverage_analysis_path=Path('/tmp/one-airport-a1-03a/run-1/classification-coverage-analysis.json'), "
                "context=ctx, run_id='AIRPORT-RECONCILIATION-001'); "
                "run_airport_asset_reconciliation(output_dir=Path('/tmp/one-airport-a1-04/run-1'), **kwargs); "
                "run_airport_asset_reconciliation(output_dir=Path('/tmp/one-airport-a1-04/run-2'), **kwargs); "
                "artifacts=['airport-asset-reconciliation-result.json','airport-canonical-proposal-candidates.json','airport-duplicate-reconciliation-groups.json','airport-alias-approval-package.json','airport-location-reconciliation-groups.json','airport-asset-reconciliation-summary.json','airport-asset-reconciliation-review-findings.json','airport-asset-readiness-gates.json','artifact-manifest.json']; "
                "assert all(compare_deterministic_outputs(Path('/tmp/one-airport-a1-04/run-1')/name, Path('/tmp/one-airport-a1-04/run-2')/name)[0] for name in artifacts); "
                "summary=json.load(open('/tmp/one-airport-a1-04/run-1/airport-asset-reconciliation-summary.json')); "
                "assert summary['sourceRecordCount']==470; "
                "assert summary['reconciliationRecordCount']==470; "
                "assert summary['legacyUnclassifiedCountUsedAsBlocker'] is False; "
                "assert summary['readinessOutcome']=='RECONCILIATION_COMPLETE_WITH_REVIEWS'; "
                "assert not summary['containsCustomerAssetIdentifiers']; "
                "assert 'TE3-CCT' not in json.dumps(summary); "
                "package=json.load(open('/tmp/one-airport-a1-04/run-1/airport-alias-approval-package.json')); "
                "assert all(item['decisionStatus']!='APPROVED' for item in package)"
            ),
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
    )
    checks.append(("Real evidence deterministic execution", real_proc.returncode == 0))
    if real_proc.returncode != 0:
        errors.append(real_proc.stdout[-2500:] or real_proc.stderr[-2500:] or "real evidence execution failed")

    print("ONE_AIRPORT_ASSET_RECONCILIATION_VALIDATION")
    for label, ok in checks:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("ONE_AIRPORT_ASSET_RECONCILIATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
