#!/usr/bin/env python3
"""Validate airport reconciled asset review projection implementation."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/airport-asset-review-projection.v1.json"
MODULE_DIR = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/industry_profiles/airport_review_projection"
TESTS_DIR = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/industry_profiles"
MODELS = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/models.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/registries/airport-asset-review-projection.v1.json",
    "AN_VANTARIS_IBMS-backend/src/asset_graph/industry_profiles/airport_review_projection/",
    "AN_VANTARIS_IBMS-backend/tests/asset_graph/industry_profiles/",
    "AN_VANTARIS_IBMS-backend/src/asset_graph/industry_profiles/__init__.py",
    "scripts/validation/validate-one-airport-review-projection.py",
)

FORBIDDEN_PATHS = (
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_IBMS-frontend/",
    "database/",
    "migrations/",
    "UFMS/",
)

FORBIDDEN_IMPORTS = ("sqlalchemy", "flask", "psycopg", "pymongo", "src.ufms", "src.umms")
FORBIDDEN_READINESS = (
    "READY_FOR_DATABASE_IMPORT",
    "READY_FOR_CANONICAL_WRITE",
    "READY_FOR_WRITE_CUTOVER",
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


def main() -> int:
    errors: list[str] = []
    checks: list[tuple[str, bool]] = []

    checks.append(("Registry exists", REGISTRY.is_file()))
    checks.append(("Module directory exists", MODULE_DIR.is_dir()))

    if REGISTRY.is_file():
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        checks.append(("INDUSTRY_PROJECTION type", registry.get("profileType") == "INDUSTRY_PROJECTION"))
        checks.append(("Read-only projection", registry.get("implementationMode") == "READ_ONLY_PROJECTION"))
        checks.append(("platformCoreAirportized false", registry.get("platformCoreAirportized") is False))
        checks.append(("canonicalWriteEnabled false", registry.get("canonicalWriteEnabled") is False))
        checks.append(("decisionWriteEnabled false", registry.get("decisionWriteEnabled") is False))
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
    checks.append(("Context review aggregated", "build_context_review_card" in module_text))
    checks.append(("Expected shared locations informational", "INFORMATIONAL_LOCATION_STATUSES" in module_text))
    checks.append(("No duplicate winner auto-select", "canonicalWinnerDigest" not in module_text))
    checks.append(("Alias approval required", "APPROVAL_REQUIRED" in module_text))
    checks.append(("SCN review preserved", "SOURCE_NAMESPACE" in module_text))

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
            "test_airport_review_projection*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
    )
    checks.append(("Focused review projection tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-3500:] or test_proc.stderr[-3500:] or "review projection tests failed")

    real_proc = _run(
        [
            "python3",
            "-c",
            (
                "import json; from pathlib import Path; "
                "import sys; sys.path.insert(0, 'AN_VANTARIS_IBMS-backend'); "
                "from src.asset_graph.industry_profiles.airport_review_projection import run_airport_review_projection, compare_deterministic_outputs; "
                "from src.asset_graph.industry_profiles.airport_review_projection.context import AirportReviewProjectionContext; "
                "summary=json.load(open('/tmp/one-airport-a1-04/run-1/airport-asset-reconciliation-summary.json')); "
                "ctx=AirportReviewProjectionContext(tenant_id='AIRPORT-TENANT-001', site_id='AIRPORT-SITE-001', source_workbook_digest='60eac97282b1cae4d1697ad1b0505d66f530a638b3de3d095f9e5f9c620a3d48', reconciliation_result_digest=summary['resultDigest']); "
                "run_airport_review_projection(reconciliation_dir=Path('/tmp/one-airport-a1-04/run-1'), output_dir=Path('/tmp/one-airport-a1-05/run-1'), context=ctx, run_id='AIRPORT-REVIEW-001'); "
                "run_airport_review_projection(reconciliation_dir=Path('/tmp/one-airport-a1-04/run-1'), output_dir=Path('/tmp/one-airport-a1-05/run-2'), context=ctx, run_id='AIRPORT-REVIEW-002'); "
                "artifacts=['airport-asset-review-rows.json','airport-review-groups.json','airport-review-dashboard.json','airport-review-facets.json','airport-review-readiness-cards.json','airport-review-summary.json','artifact-manifest.json']; "
                "assert all(compare_deterministic_outputs(Path('/tmp/one-airport-a1-05/run-1')/name, Path('/tmp/one-airport-a1-05/run-2')/name)[0] for name in artifacts); "
                "s=json.load(open('/tmp/one-airport-a1-05/run-1/airport-review-summary.json')); "
                "assert s['assetReviewRowCount']==470; "
                "assert s['duplicateReviewCardCount']==4; "
                "assert s['contextReviewCardCount']==1; "
                "assert s['aliasReviewCardCount']==2; "
                "assert s['namespaceReviewCardCount']==1; "
                "assert s['locationReviewCardCount']==4; "
                "assert s['informationalLocationGroupCount']==67; "
                "assert s['aggregateCustomerIdentifierCount']==0; "
                "assert s['readinessOutcome']=='REVIEW_PROJECTION_COMPLETE_WITH_PENDING_DECISIONS'; "
                "assert s['readinessOutcome'] not in {'READY_FOR_DATABASE_IMPORT','READY_FOR_CANONICAL_WRITE','READY_FOR_WRITE_CUTOVER'}; "
                "groups=json.load(open('/tmp/one-airport-a1-05/run-1/airport-review-groups.json')); "
                "assert sum(1 for item in groups if item.get('cardType')=='ContextReviewCard')==1; "
                "assert all(item.get('decisionState')!='APPROVED' for item in groups if item.get('cardType') in {'AliasReviewCard','NamespaceReviewCard','DuplicateReviewCard'}); "
                "assert 'TE3-CCT' not in json.dumps(groups); "
                "info=[item for item in groups if item.get('cardType')=='LocationReviewCard' and item.get('informationalOnly')]; "
                "assert len(info)==67; "
                "conflicts=[item for item in groups if item.get('cardType')=='LocationReviewCard' and not item.get('informationalOnly')]; "
                "assert len(conflicts)==4"
            ),
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
    )
    checks.append(("Real evidence deterministic execution", real_proc.returncode == 0))
    if real_proc.returncode != 0:
        errors.append(real_proc.stdout[-3500:] or real_proc.stderr[-3500:] or "real evidence execution failed")

    print("ONE_AIRPORT_REVIEW_PROJECTION_VALIDATION")
    for label, ok in checks:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("ONE_AIRPORT_REVIEW_PROJECTION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
