#!/usr/bin/env python3
"""Validate read-only UConsole Integration Health projection."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/uconsole-integration-health-projection.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/uconsole_projection"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/uconsole_integration_health_projection.py"
UCONSOLE_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-uconsole-integration-health.v1.json"
REAL_SCRIPT = ROOT / "scripts/validation/_run_a2_05_uconsole_projection.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/uconsole_projection/",
    "AN_VANTARIS_ONE/registries/uconsole-integration-health-projection.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/uconsole_integration_health_projection.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-uconsole-integration-health.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/__init__.py",
    "AN_VANTARIS_ONE/tests/uconsole_projection/",
    "scripts/validation/validate-one-uconsole-integration-health-projection.py",
    "scripts/validation/_run_a2_05_uconsole_projection.py",
    "ONE_AIRPORT_A2_05_READ_ONLY_UCONSOLE_INTEGRATION_HEALTH_PROJECTION_REPORT.md",
)

FORBIDDEN_PATHS = (
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_LINK/",
    "AN_VANTARIS_Contracts/",
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
    checks.append(("Generic module exists", GENERIC_DIR.is_dir()))
    checks.append(("Airport projection module exists", AIRPORT_MODULE.is_file()))

    if REGISTRY.is_file():
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        checks.append(("Cross-industry registry", registry.get("crossIndustry") is True))
        checks.append(("Not airport-specific registry", registry.get("airportSpecific") is False))
        checks.append(("databaseAccessEnabled false", registry.get("databaseAccessEnabled") is False))
        checks.append(("frontendEnabled false", registry.get("frontendEnabled") is False))
        checks.append(("apiEnabled false", registry.get("apiEnabled") is False))

    module_text = (GENERIC_DIR / "models.py").read_text(encoding="utf-8")
    module_text += " " + (GENERIC_DIR / "validation.py").read_text(encoding="utf-8")
    module_text += " " + AIRPORT_MODULE.read_text(encoding="utf-8")
    checks.append(("No public API routes", "blueprint" not in module_text.lower()))
    checks.append(("No frontend runtime", "react" not in module_text.lower()))

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
    disallowed = [path for path in changed if path and not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)]
    checks.append(("Changes within allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")

    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))

    a205_proc = _run(
        [
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "AN_VANTARIS_ONE/tests/uconsole_projection",
            "-p",
            "test_*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")},
    )
    checks.append(("Focused A2-05 tests pass", a205_proc.returncode == 0))
    if a205_proc.returncode != 0:
        errors.append(a205_proc.stdout[-3500:] or a205_proc.stderr[-3500:] or "A2-05 tests failed")

    for label, command in (
        (
            "A2-04 regression tests pass",
            [
                "python3",
                "-m",
                "unittest",
                "discover",
                "-s",
                "AN_VANTARIS_ONE/tests/evidence_adapter_contract",
                "-p",
                "test_*.py",
            ],
        ),
        (
            "A2-03 regression tests pass",
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
        ),
        (
            "A2-02 regression tests pass",
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
        ),
        (
            "A2-01 regression tests pass",
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
        ),
    ):
        proc = _run(command, env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")})
        checks.append((label, proc.returncode == 0))
        if proc.returncode != 0:
            errors.append(proc.stdout[-2500:] or proc.stderr[-2500:] or f"{label} failed")

    for label, script in (
        ("A2-04 validator pass", "scripts/validation/validate-one-evidence-adapter-contract.py"),
        ("A2-03 validator pass", "scripts/validation/validate-one-integration-health-read-model.py"),
        ("A2-02 validator pass", "scripts/validation/validate-one-airport-source-system-review.py"),
        ("A2-01 validator pass", "scripts/validation/validate-one-source-system-registry.py"),
        ("Boundary validator pass", "scripts/validation/validate-one-boundaries.py"),
    ):
        proc = _run(["python3", str(ROOT / script)], env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")})
        checks.append((label, proc.returncode == 0))
        if proc.returncode != 0:
            errors.append(proc.stdout[-2000:] or proc.stderr[-2000:] or f"{label} failed")

    real_proc = _run(
        ["python3", str(REAL_SCRIPT)],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")},
    )
    checks.append(("Real fixture deterministic execution", real_proc.returncode == 0))
    if real_proc.returncode != 0:
        errors.append(real_proc.stdout[-3500:] or real_proc.stderr[-3500:] or "real fixture execution failed")

    if UCONSOLE_PROJECTION.is_file():
        projection = json.loads(UCONSOLE_PROJECTION.read_text(encoding="utf-8"))
        summary = projection.get("summary", {})
        checks.append(("Five source-system rows", summary.get("sourceSystemRowCount") == 5))
        checks.append(("Five dashboard cards", summary.get("dashboardCardCount") == 5))
        checks.append(("470 evidence devices", summary.get("totalEvidenceDeviceCount") == 470))
        checks.append(("Zero runtime observed", summary.get("runtimeObservedSystemCount") == 0))
        checks.append(("Frontend disabled", summary.get("frontendEnabled") is False))
        checks.append(("API disabled", summary.get("apiEnabled") is False))

    print("ONE_AIRPORT_A2_05_READ_ONLY_UCONSOLE_INTEGRATION_HEALTH_PROJECTION_VALIDATION")
    for label, ok in checks:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("ONE_AIRPORT_A2_05_READ_ONLY_UCONSOLE_INTEGRATION_HEALTH_PROJECTION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
