#!/usr/bin/env python3
"""Validate generic source-system registry foundation and airport consumer profile."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/source-system-registry.v1.json"
AIRPORT_PROFILE = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/source-system-profile.v1.json"
AIRPORT_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-source-system-candidates.v1.json"
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/source_system_registry"
AIRPORT_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport"
TESTS_DIR = ROOT / "AN_VANTARIS_ONE/tests/source_system_registry"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/registries/source-system-registry.v1.json",
    "AN_VANTARIS_ONE/source_system_registry/",
    "AN_VANTARIS_ONE/industry_profiles/",
    "AN_VANTARIS_ONE/tests/source_system_registry/",
    "scripts/validation/validate-one-source-system-registry.py",
    "scripts/validation/_run_a2_01_real_evidence.py",
    "ONE_AIRPORT_A2_01_GENERIC_SOURCE_SYSTEM_REGISTRY_FOUNDATION_REPORT.md",
)

FORBIDDEN_PATHS = (
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_LINK/",
    "AN_VANTARIS_IBMS-frontend/",
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

    checks.append(("Generic registry spec exists", REGISTRY.is_file()))
    checks.append(("Airport consumer profile exists", AIRPORT_PROFILE.is_file()))
    checks.append(("Generic module directory exists", GENERIC_DIR.is_dir()))

    if REGISTRY.is_file():
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        checks.append(("Cross-industry registry", registry.get("crossIndustry") is True))
        checks.append(("Not airport-specific registry", registry.get("airportSpecific") is False))
        checks.append(("Read-only foundation", registry.get("implementationMode") == "READ_ONLY_REGISTRY_FOUNDATION"))
        checks.append(("databaseAccessEnabled false", registry.get("databaseAccessEnabled") is False))
        checks.append(("runtimeConnectorExecutionEnabled false", registry.get("runtimeConnectorExecutionEnabled") is False))
        checks.append(("productionActivationEnabled false", registry.get("productionActivationEnabled") is False))

    if AIRPORT_PROFILE.is_file():
        profile = json.loads(AIRPORT_PROFILE.read_text(encoding="utf-8"))
        checks.append(("Airport alias CCT declared", profile.get("aliasProposals", {}).get("CCT", {}).get("autoApprove") is False))
        checks.append(("Airport alias PAS declared", profile.get("aliasProposals", {}).get("PAS", {}).get("autoApprove") is False))
        checks.append(("SCN namespace rule present", "SCN" in profile.get("sourceNamespaceRules", {})))

    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.is_file() else ""
    checks.append(("Generic spec has no airport canonical fields", all(token not in registry_text for token in ("Terminal", "DA21", "TE3"))))

    import_errors: list[str] = []
    for path in list(GENERIC_DIR.rglob("*.py")) + list(AIRPORT_DIR.rglob("*.py")):
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

    module_text = " ".join(path.read_text(encoding="utf-8") for path in GENERIC_DIR.rglob("*.py"))
    module_text += " " + " ".join(path.read_text(encoding="utf-8") for path in AIRPORT_DIR.rglob("*.py"))
    checks.append(("No public API routes", "blueprint" not in module_text.lower()))
    checks.append(("No connector execution", "execute_connector" not in module_text))

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
            "AN_VANTARIS_ONE/tests/source_system_registry",
            "-p",
            "test_*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")},
    )
    checks.append(("Focused A2-01 tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-3500:] or test_proc.stderr[-3500:] or "A2-01 tests failed")

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

    real_script = ROOT / "scripts/validation/_run_a2_01_real_evidence.py"
    real_proc = _run(
        ["python3", str(real_script)],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_ONE")},
    )
    checks.append(("Real evidence deterministic execution", real_proc.returncode == 0))
    if real_proc.returncode != 0:
        errors.append(real_proc.stdout[-3500:] or real_proc.stderr[-3500:] or "real evidence execution failed")

    if AIRPORT_PROJECTION.is_file():
        projection = json.loads(AIRPORT_PROJECTION.read_text(encoding="utf-8"))
        summary = projection.get("summary", {})
        checks.append(("Committed projection has five candidates", summary.get("sourceSystemCandidateCount") == 5))
        checks.append(("Committed projection zero active", summary.get("activeSystemCount") == 0))

    print("ONE_AIRPORT_A2_01_GENERIC_SOURCE_SYSTEM_REGISTRY_FOUNDATION_VALIDATION")
    for label, ok in checks:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("ONE_AIRPORT_A2_01_GENERIC_SOURCE_SYSTEM_REGISTRY_FOUNDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
