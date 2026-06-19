#!/usr/bin/env python3
"""Validate generic Integration Health read model and airport projection."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/integration-health-read-model.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/integration_health"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/integration_health_projection.py"
HEALTH_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-integration-health.v1.json"
REAL_SCRIPT = ROOT / "scripts/validation/_run_a2_03_real_evidence.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/registries/integration-health-read-model.v1.json",
    "AN_VANTARIS_ONE/integration_health/",
    "AN_VANTARIS_ONE/industry_profiles/airport/integration_health_projection.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/__init__.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-integration-health.v1.json",
    "AN_VANTARIS_ONE/tests/integration_health/",
    "scripts/validation/validate-one-integration-health-read-model.py",
    "scripts/validation/_run_a2_03_real_evidence.py",
    "ONE_AIRPORT_A2_03_GENERIC_INTEGRATION_HEALTH_READ_MODEL_REPORT.md",
)

FORBIDDEN_PATHS = (
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_LINK/",
    "AN_VANTARIS_IBMS-frontend/",
    "AN_VANTARIS_ONE/source_system_registry/",
    "database/",
    "migrations/",
    "UFMS/",
    "AN_VANTARIS_Contracts/",
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
    checks.append(("Generic module exists", GENERIC_DIR.is_dir()))
    checks.append(("Airport projection module exists", AIRPORT_MODULE.is_file()))

    if REGISTRY.is_file():
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        checks.append(("Cross-industry registry", registry.get("crossIndustry") is True))
        checks.append(("Not airport-specific registry", registry.get("airportSpecific") is False))
        checks.append(("Projection only", registry.get("projectionOnly") is True))
        checks.append(("databaseAccessEnabled false", registry.get("databaseAccessEnabled") is False))

    module_text = (GENERIC_DIR / "evaluation.py").read_text(encoding="utf-8")
    module_text += " " + (GENERIC_DIR / "projection.py").read_text(encoding="utf-8")
    module_text += " " + AIRPORT_MODULE.read_text(encoding="utf-8")
    checks.append(("No heartbeat collection", "collect_heartbeat" not in module_text.lower()))
    checks.append(("No public API routes", "blueprint" not in module_text.lower()))

    import_errors: list[str] = []
    for path in list(GENERIC_DIR.rglob("*.py")) + [AIRPORT_MODULE]:
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

    changed = _changed_paths()
    generic_registry_changed = [path for path in changed if path.startswith("AN_VANTARIS_ONE/source_system_registry/")]
    checks.append(("Generic source-system registry core unchanged", len(generic_registry_changed) == 0))

    disallowed = [path for path in changed if path and not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)]
    checks.append(("Changes within allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")

    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))

    a203_proc = _run(
        [
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "AN_VANTARIS_ONE/tests/integration_health",
            "-p",
            "test_*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")},
    )
    checks.append(("Focused A2-03 tests pass", a203_proc.returncode == 0))
    if a203_proc.returncode != 0:
        errors.append(a203_proc.stdout[-3500:] or a203_proc.stderr[-3500:] or "A2-03 tests failed")

    a202_proc = _run(
        [
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "AN_VANTARIS_ONE/tests/source_system_registry",
            "-p",
            "test_airport_source_system_review_projection.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")},
    )
    checks.append(("A2-02 regression tests pass", a202_proc.returncode == 0))
    if a202_proc.returncode != 0:
        errors.append(a202_proc.stdout[-2500:] or a202_proc.stderr[-2500:] or "A2-02 regression failed")

    a201_proc = _run(
        [
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "AN_VANTARIS_ONE/tests/source_system_registry",
            "-p",
            "test_source_system_registry.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")},
    )
    checks.append(("A2-01 regression tests pass", a201_proc.returncode == 0))
    if a201_proc.returncode != 0:
        errors.append(a201_proc.stdout[-2500:] or a201_proc.stderr[-2500:] or "A2-01 regression failed")

    airport_proc = _run(
        [
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "AN_VANTARIS_IBMS-backend/tests/asset_graph/industry_profiles",
            "-p",
            "test_airport*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
    )
    checks.append(("Airport industry profile regression tests pass", airport_proc.returncode == 0))
    if airport_proc.returncode != 0:
        errors.append(airport_proc.stdout[-2500:] or airport_proc.stderr[-2500:] or "airport regression failed")

    asset_graph_proc = _run(
        [
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "AN_VANTARIS_IBMS-backend/tests/asset_graph",
            "-p",
            "test_*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
    )
    checks.append(("Asset Graph full regression tests pass", asset_graph_proc.returncode == 0))
    if asset_graph_proc.returncode != 0:
        errors.append(asset_graph_proc.stdout[-2500:] or asset_graph_proc.stderr[-2500:] or "asset graph regression failed")

    real_proc = _run(
        ["python3", str(REAL_SCRIPT)],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")},
    )
    checks.append(("Real evidence deterministic execution", real_proc.returncode == 0))
    if real_proc.returncode != 0:
        errors.append(real_proc.stdout[-3500:] or real_proc.stderr[-3500:] or "real evidence execution failed")

    if HEALTH_PROJECTION.is_file():
        projection = json.loads(HEALTH_PROJECTION.read_text(encoding="utf-8"))
        summary = projection.get("summary", {})
        checks.append(("Five health records", summary.get("integrationHealthRecordCount") == 5))
        checks.append(("470 evidence devices", summary.get("totalEvidenceDeviceCount") == 470))
        checks.append(
            (
                "Readiness outcome",
                projection.get("readinessOutcome") == "INTEGRATION_HEALTH_DECLARATION_COMPLETE_RUNTIME_EVIDENCE_PENDING",
            )
        )

    print("ONE_AIRPORT_A2_03_GENERIC_INTEGRATION_HEALTH_READ_MODEL_VALIDATION")
    for label, ok in checks:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("ONE_AIRPORT_A2_03_GENERIC_INTEGRATION_HEALTH_READ_MODEL_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
