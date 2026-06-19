#!/usr/bin/env python3
"""Validate Evidence Adapter Contract and airport fixture projection."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/evidence-adapter-contract.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/evidence_adapter_contract"
AIRPORT_MODULE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/evidence_adapter_profile.py"
CONTRACT_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-evidence-adapter-contract.v1.json"
REAL_SCRIPT = ROOT / "scripts/validation/_run_a2_04_contract_fixture.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/evidence_adapter_contract/",
    "AN_VANTARIS_ONE/registries/evidence-adapter-contract.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/evidence_adapter_profile.py",
    "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-evidence-adapter-contract.v1.json",
    "AN_VANTARIS_ONE/industry_profiles/airport/__init__.py",
    "AN_VANTARIS_ONE/tests/evidence_adapter_contract/",
    "scripts/validation/validate-one-evidence-adapter-contract.py",
    "scripts/validation/_run_a2_04_contract_fixture.py",
    "ONE_AIRPORT_A2_04_EDGE_LINK_EVIDENCE_ADAPTER_CONTRACT_REPORT.md",
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
    checks.append(("Airport profile module exists", AIRPORT_MODULE.is_file()))

    if REGISTRY.is_file():
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        checks.append(("Cross-industry contract", registry.get("crossIndustry") is True))
        checks.append(("Not airport-specific contract", registry.get("airportSpecific") is False))
        checks.append(("databaseAccessEnabled false", registry.get("databaseAccessEnabled") is False))
        checks.append(("runtimeConnectorExecutionEnabled false", registry.get("runtimeConnectorExecutionEnabled") is False))

    module_text = (GENERIC_DIR / "models.py").read_text(encoding="utf-8")
    module_text += " " + (GENERIC_DIR / "validation.py").read_text(encoding="utf-8")
    module_text += " " + AIRPORT_MODULE.read_text(encoding="utf-8")
    checks.append(("No public API routes", "blueprint" not in module_text.lower()))
    checks.append(("No runtime execution", "execute_connector" not in module_text))

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

    a204_proc = _run(
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
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")},
    )
    checks.append(("Focused A2-04 tests pass", a204_proc.returncode == 0))
    if a204_proc.returncode != 0:
        errors.append(a204_proc.stdout[-3500:] or a204_proc.stderr[-3500:] or "A2-04 tests failed")

    for label, command in (
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

    real_proc = _run(
        ["python3", str(REAL_SCRIPT)],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")},
    )
    checks.append(("Real fixture deterministic execution", real_proc.returncode == 0))
    if real_proc.returncode != 0:
        errors.append(real_proc.stdout[-3500:] or real_proc.stderr[-3500:] or "real fixture execution failed")

    if CONTRACT_PROJECTION.is_file():
        projection = json.loads(CONTRACT_PROJECTION.read_text(encoding="utf-8"))
        summary = projection.get("summary", {})
        checks.append(("Five fixture envelopes", summary.get("evidenceEnvelopeCount") == 5))
        checks.append(("Five accepted envelopes", summary.get("acceptedAsEvidenceCount") == 5))
        checks.append(("Zero runtime observed", summary.get("runtimeObservedSystemCount") == 0))

    print("ONE_AIRPORT_A2_04_EDGE_LINK_EVIDENCE_ADAPTER_CONTRACT_VALIDATION")
    for label, ok in checks:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("ONE_AIRPORT_A2_04_EDGE_LINK_EVIDENCE_ADAPTER_CONTRACT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
