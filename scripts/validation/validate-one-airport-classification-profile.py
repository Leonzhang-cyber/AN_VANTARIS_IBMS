#!/usr/bin/env python3
"""Validate airport system and device classification profile implementation."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/airport-classification-profile.v1.json"
MODULE_DIR = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/industry_profiles/airport_classification"
TESTS_DIR = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/industry_profiles"
MODELS = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/models.py"
VALIDATOR = Path(__file__)

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/registries/airport-classification-profile.v1.json",
    "AN_VANTARIS_IBMS-backend/src/asset_graph/industry_profiles/",
    "AN_VANTARIS_IBMS-backend/tests/asset_graph/industry_profiles/",
    "scripts/validation/validate-one-airport-classification-profile.py",
)

FORBIDDEN_PATHS = (
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_IBMS-frontend/",
    "database/",
    "migrations/",
    "UFMS/",
)

FORBIDDEN_IMPORTS = ("sqlalchemy", "flask", "psycopg", "pymongo", "src.ufms", "src.umms")
REAL_INTAKE = Path("/tmp/one-airport-a1-01/run-1/airport-asset-intake-evidence.json")
REAL_SPATIAL = Path("/tmp/one-airport-a1-02/run-1/airport-spatial-profile-result.json")
REAL_BINDINGS = Path("/tmp/one-airport-a1-02/run-1/airport-device-spatial-bindings.json")


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
        checks.append(("Authority ONE-AIRPORT-A1-03", registry.get("authority") == "ONE-AIRPORT-A1-03"))
        checks.append(("SCN listed as namespace", "SCN" in registry.get("sourceNamespaceCodes", [])))
        checks.append(("CCT alias candidate declared", registry.get("embeddedSystemAliasCandidates", {}).get("CCT") == "CCTV"))

    models_text = MODELS.read_text(encoding="utf-8") if MODELS.is_file() else ""
    checks.append(("Generic models not airportized", "TE3" not in models_text and "SCN" not in models_text))

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
    checks.append(("Read-only classification mode", "READ_ONLY_CLASSIFICATION" in module_text))
    checks.append(("SCN semantic review required", "SCN_SEMANTIC_REVIEW_REQUIRED" in module_text))
    checks.append(("SCN not auto mapped to TEL", "SCN" not in module_text or "KNOWN_SOURCE_NAMESPACES" in module_text))
    checks.append(("Source namespace separation", "source_namespace_code" in module_text))
    checks.append(("Unknown type review path", "UNKNOWN_DEVICE_TYPE_CODE" in module_text))

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
            "test_airport_classification*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
    )
    checks.append(("Focused classification tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-2500:] or test_proc.stderr[-2500:] or "classification tests failed")

    if REAL_INTAKE.is_file() and REAL_SPATIAL.is_file() and REAL_BINDINGS.is_file():
        real_proc = _run(
            [
                "python3",
                "-c",
                (
                    "import json; from pathlib import Path; "
                    "import sys; sys.path.insert(0, 'AN_VANTARIS_IBMS-backend'); "
                    "from src.asset_graph.industry_profiles.airport_classification import run_airport_classification, compare_deterministic_outputs; "
                    "from src.asset_graph.industry_profiles.airport_classification.context import AirportClassificationContext; "
                    "ev=json.load(open('/tmp/one-airport-a1-01/run-1/airport-asset-intake-evidence.json')); "
                    "sp=json.load(open('/tmp/one-airport-a1-02/run-1/airport-spatial-profile-result.json')); "
                    "ctx=AirportClassificationContext("
                    "tenant_id='AIRPORT-TENANT-001', site_id='AIRPORT-SITE-001', "
                    "source_workbook_digest=ev['sourceWorkbook']['sha256'], "
                    "expected_intake_result_digest=ev['resultDigest'], "
                    "expected_spatial_result_digest=sp['resultDigest']); "
                    "run_airport_classification("
                    "intake_evidence_path=Path('/tmp/one-airport-a1-01/run-1/airport-asset-intake-evidence.json'), "
                    "spatial_result_path=Path('/tmp/one-airport-a1-02/run-1/airport-spatial-profile-result.json'), "
                    "spatial_bindings_path=Path('/tmp/one-airport-a1-02/run-1/airport-device-spatial-bindings.json'), "
                    "output_dir=Path('/tmp/one-airport-a1-03/run-1'), context=ctx, run_id='AIRPORT-CLASSIFICATION-001'); "
                    "run_airport_classification("
                    "intake_evidence_path=Path('/tmp/one-airport-a1-01/run-1/airport-asset-intake-evidence.json'), "
                    "spatial_result_path=Path('/tmp/one-airport-a1-02/run-1/airport-spatial-profile-result.json'), "
                    "spatial_bindings_path=Path('/tmp/one-airport-a1-02/run-1/airport-device-spatial-bindings.json'), "
                    "output_dir=Path('/tmp/one-airport-a1-03/run-2'), context=ctx, run_id='AIRPORT-CLASSIFICATION-001'); "
                    "artifacts=["
                    "'airport-system-classification-result.json',"
                    "'airport-device-type-classification-result.json',"
                    "'airport-device-classification-bindings.json',"
                    "'airport-classification-review-findings.json',"
                    "'airport-classification-summary.json',"
                    "'artifact-manifest.json'"
                    "]; "
                    "assert all(compare_deterministic_outputs(Path('/tmp/one-airport-a1-03/run-1')/name, Path('/tmp/one-airport-a1-03/run-2')/name)[0] for name in artifacts); "
                    "summary=json.load(open('/tmp/one-airport-a1-03/run-1/airport-classification-summary.json')); "
                    "assert summary['readinessOutcome']=='CLASSIFICATION_COMPLETE_WITH_REVIEWS'; "
                    "assert not summary['containsCustomerAssetIdentifiers']; "
                    "assert 'TE3-CCT' not in json.dumps(summary); "
                    "sys_doc=json.load(open('/tmp/one-airport-a1-03/run-1/airport-system-classification-result.json')); "
                    "scn=[c for c in sys_doc['candidates'] if c.get('sourceNamespace')=='SCN']; "
                    "assert scn and scn[0]['mappingStatus']=='REVIEW_REQUIRED'"
                ),
            ],
            env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
        )
        checks.append(("Real evidence deterministic execution", real_proc.returncode == 0))
        if real_proc.returncode != 0:
            errors.append(real_proc.stdout[-2500:] or real_proc.stderr[-2500:] or "real evidence execution failed")
    else:
        checks.append(("Real evidence available", False))
        errors.append("real intake/spatial evidence not found under /tmp")

    print("ONE_AIRPORT_CLASSIFICATION_PROFILE_VALIDATION")
    for label, ok in checks:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("ONE_AIRPORT_CLASSIFICATION_PROFILE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
