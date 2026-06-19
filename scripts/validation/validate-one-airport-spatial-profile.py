#!/usr/bin/env python3
"""Validate airport spatial hierarchy profile implementation."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/airport-spatial-profile.v1.json"
MODULE_DIR = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/industry_profiles"
TESTS_DIR = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/industry_profiles"
MODELS = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/models.py"
VALIDATOR = Path(__file__)

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/registries/airport-spatial-profile.v1.json",
    "AN_VANTARIS_IBMS-backend/src/asset_graph/industry_profiles/",
    "AN_VANTARIS_IBMS-backend/tests/asset_graph/industry_profiles/",
    "scripts/validation/validate-one-airport-spatial-profile.py",
)

FORBIDDEN_PATHS = (
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_IBMS-frontend/",
    "database/",
    "migrations/",
    "UFMS/",
)

FORBIDDEN_IMPORTS = ("sqlalchemy", "flask", "psycopg", "pymongo", "src.ufms", "src.umms")
CUSTOMER_CODES = ("TE3", "DA21", "DA31", "Z1", "Z2")
REAL_EVIDENCE = Path("/tmp/one-airport-a1-01/run-1/airport-asset-intake-evidence.json")


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
    checks.append(("Tests directory exists", TESTS_DIR.is_dir()))

    if REGISTRY.is_file():
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        checks.append(("INDUSTRY_PROFILE type", registry.get("profileType") == "INDUSTRY_PROFILE"))
        checks.append(("platformCoreAirportized false", registry.get("platformCoreAirportized") is False))
        checks.append(("Authority ONE-AIRPORT-A1-02", registry.get("authority") == "ONE-AIRPORT-A1-02"))

    models_text = MODELS.read_text(encoding="utf-8") if MODELS.is_file() else ""
    checks.append(("Generic models not airportized", "TE3" not in models_text and "DistributionArea" not in models_text))

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
    checks.append(("Read-only mapping mode", "READ_ONLY_MAPPING" in module_text))

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
            "test_*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
    )
    checks.append(("Focused tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-2500:] or test_proc.stderr[-2500:] or "tests failed")

    if REAL_EVIDENCE.is_file():
        real_proc = _run(
            [
                "python3",
                "-c",
                (
                    "import json; from pathlib import Path; "
                    "import sys; sys.path.insert(0, 'AN_VANTARIS_IBMS-backend'); "
                    "from src.asset_graph.industry_profiles import AirportSpatialContext, run_airport_spatial_mapping, compare_deterministic_outputs; "
                    "ev=json.load(open('/tmp/one-airport-a1-01/run-1/airport-asset-intake-evidence.json')); "
                    "ctx=AirportSpatialContext.create("
                    "tenant_id='AIRPORT-TENANT-001', site_id='AIRPORT-SITE-001', "
                    "airport_context_id='AIRPORT-CONTEXT-REQUIRED', terminal_context_id='TERMINAL-CONTEXT-REQUIRED', "
                    f"source_workbook_digest=ev['sourceWorkbook']['sha256'], "
                    "allowed_terminal_codes=['TERMINAL-CONTEXT-REQUIRED'], allowed_building_codes=['TE3'], "
                    "allowed_level_codes=['BAS','GRD','1ST','2ND','ROF'], allowed_zone_codes=['Z1','Z2'], "
                    "allowed_distribution_area_codes=['DA21','DA31']); "
                    "run_airport_spatial_mapping(intake_evidence_path=Path('/tmp/one-airport-a1-01/run-1/airport-asset-intake-evidence.json'), output_dir=Path('/tmp/one-airport-a1-02/run-1'), context=ctx, run_id='AIRPORT-SPATIAL-001'); "
                    "run_airport_spatial_mapping(intake_evidence_path=Path('/tmp/one-airport-a1-01/run-1/airport-asset-intake-evidence.json'), output_dir=Path('/tmp/one-airport-a1-02/run-2'), context=ctx, run_id='AIRPORT-SPATIAL-001'); "
                    "assert compare_deterministic_outputs(Path('/tmp/one-airport-a1-02/run-1/airport-spatial-profile-result.json'), Path('/tmp/one-airport-a1-02/run-2/airport-spatial-profile-result.json'))[0]; "
                    "summary=json.load(open('/tmp/one-airport-a1-02/run-1/airport-spatial-hierarchy-summary.json')); "
                    "assert not summary['containsCustomerAssetIdentifiers']; "
                    "blob=json.dumps(summary); "
                    "assert 'TE3-CCT' not in blob"
                ),
            ],
            env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
        )
        checks.append(("Real evidence execution deterministic", real_proc.returncode == 0))
        if real_proc.returncode != 0:
            errors.append(real_proc.stdout + real_proc.stderr)
    else:
        checks.append(("Real evidence execution deterministic", False))
        errors.append("real intake evidence not found at /tmp/one-airport-a1-01/run-1/")

    print("VANTARIS ONE Airport Spatial Profile Validation")
    print("=" * 60)
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    all_pass = all(ok for _, ok in checks)
    if errors or not all_pass:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nONE_AIRPORT_SPATIAL_PROFILE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
