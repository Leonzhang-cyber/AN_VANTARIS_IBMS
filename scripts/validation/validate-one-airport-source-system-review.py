#!/usr/bin/env python3
"""Validate airport source-system evidence binding and review projection."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GENERIC_DIR = ROOT / "AN_VANTARIS_ONE/source_system_registry"
AIRPORT_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport"
REVIEW_PROJECTION = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-source-system-review.v1.json"
REAL_SCRIPT = ROOT / "scripts/validation/_run_a2_02_real_evidence.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/industry_profiles/airport/",
    "AN_VANTARIS_ONE/tests/source_system_registry/",
    "scripts/validation/validate-one-airport-source-system-review.py",
    "scripts/validation/_run_a2_02_real_evidence.py",
    "ONE_AIRPORT_A2_02_SOURCE_SYSTEM_EVIDENCE_BINDING_AND_REVIEW_PROJECTION_REPORT.md",
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

    checks.append(("Review projection artifact exists", REVIEW_PROJECTION.is_file()))
    checks.append(("Evidence binding module exists", (AIRPORT_DIR / "source_system_evidence_binding.py").is_file()))
    checks.append(("Review projection module exists", (AIRPORT_DIR / "source_system_review_projection.py").is_file()))

    if REVIEW_PROJECTION.is_file():
        projection = json.loads(REVIEW_PROJECTION.read_text(encoding="utf-8"))
        summary = projection.get("summary", {})
        checks.append(("Five evidence bindings", summary.get("sourceSystemEvidenceBindingCount") == 5))
        checks.append(("470 bound devices", summary.get("totalBoundDeviceEvidenceCount") == 470))
        checks.append(("Five pending decisions", summary.get("pendingDecisionCount") == 5))
        checks.append(("Zero active systems", summary.get("activeSystemCount") == 0))
        checks.append(
            (
                "Readiness outcome",
                projection.get("readinessOutcome") == "SOURCE_SYSTEM_REVIEW_PROJECTION_COMPLETE_WITH_PENDING_DECISIONS",
            )
        )

    import_errors: list[str] = []
    for path in AIRPORT_DIR.rglob("*.py"):
        if path.name == "candidate_projection.py":
            continue
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

    module_text = " ".join(
        path.read_text(encoding="utf-8")
        for path in AIRPORT_DIR.rglob("*.py")
        if path.name in {"source_system_evidence_binding.py", "source_system_review_projection.py"}
    )
    checks.append(("No public API routes", "blueprint" not in module_text.lower()))
    checks.append(("No runtime health invention", "heartbeat" not in module_text))

    changed = _changed_paths()
    generic_changed = [path for path in changed if path.startswith("AN_VANTARIS_ONE/source_system_registry/")]
    checks.append(("Generic registry core unchanged", len(generic_changed) == 0))

    disallowed = [path for path in changed if path and not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)]
    checks.append(("Changes within allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")

    forbidden_touched = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_PATHS)]
    checks.append(("No forbidden paths touched", len(forbidden_touched) == 0))

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
    checks.append(("Focused A2-02 tests pass", a202_proc.returncode == 0))
    if a202_proc.returncode != 0:
        errors.append(a202_proc.stdout[-3500:] or a202_proc.stderr[-3500:] or "A2-02 tests failed")

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
    checks.append(("Existing A2-01 tests pass", a201_proc.returncode == 0))
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

    print("ONE_AIRPORT_A2_02_SOURCE_SYSTEM_EVIDENCE_BINDING_AND_REVIEW_PROJECTION_VALIDATION")
    for label, ok in checks:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {label}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("ONE_AIRPORT_A2_02_SOURCE_SYSTEM_EVIDENCE_BINDING_AND_REVIEW_PROJECTION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
