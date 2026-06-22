#!/usr/bin/env python3
"""Validate ONE-PROD-GA-R6 full EDGE runtime resync gate."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
EDGE = ROOT / "AN_VANTARIS_ONE/packages/AN_VANTARIS_EDGE"
REPORT = ROOT / "ONE_PROD_GA_R6_FULL_EDGE_RUNTIME_RESYNC_GATE_REPORT.md"
PASS_MARKER = "ONE_PROD_GA_R6_FULL_EDGE_RUNTIME_RESYNC_GATE_PASS"

REPORT_MARKERS = {
    "R1": (ROOT / "ONE_PROD_GA_R1_FOUNDATION_PACKAGES_SYNC_GATE_REPORT.md", "ONE_PROD_GA_R1_FOUNDATION_PACKAGES_SYNC_GATE_PASS"),
    "R2": (ROOT / "ONE_PROD_GA_R2_FOUNDATION_PACKAGE_CONSOLE_ENTRY_REPORT.md", "ONE_PROD_GA_R2_FOUNDATION_PACKAGE_CONSOLE_ENTRY_PASS"),
    "R3": (ROOT / "ONE_PROD_GA_R3_FOUNDATION_PACKAGE_READONLY_API_HEALTH_REPORT.md", "ONE_PROD_GA_R3_FOUNDATION_PACKAGE_READONLY_API_HEALTH_PASS"),
    "R4": (ROOT / "ONE_PROD_GA_R4_OFFLINE_INSTALL_VERIFY_ROLLBACK_PACKAGE_REPORT.md", "ONE_PROD_GA_R4_OFFLINE_INSTALL_VERIFY_ROLLBACK_PACKAGE_PASS"),
    "R5": (ROOT / "ONE_PROD_GA_R5_FINAL_FOUNDATION_PACKAGE_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md", "ONE_PROD_GA_R5_FINAL_FOUNDATION_PACKAGE_FREEZE_PASS"),
}

REQUIRED_FOLDERS = [
    "buffer",
    "config",
    "evidence",
    "manifests",
    "src",
]

RUNTIME_INDICATORS = [
    "src/runtime",
    "src/product-runtime/edge",
    "src/connectors",
    "src/generated",
]

PRESERVED_BOUNDARY_FILES = [
    ".placeholder",
    "BOUNDARY.md",
    "MIGRATION_SOURCE.md",
    "README.md",
    "tsconfig.typecheck.json",
]

FORBIDDEN_NAMES = {
    ".env",
    "node_modules",
    "dist",
    "build",
    ".runtime",
    "__pycache__",
}
FORBIDDEN_SUFFIXES = {
    ".pem",
    ".key",
    ".p12",
    ".crt",
}


def check(name: str, condition: bool, details: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    suffix = f" - {details}" if details else ""
    print(f"[{status}] {name}{suffix}")
    return condition


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def file_count(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file())


def is_forbidden(path: Path) -> bool:
    name = path.name
    if name in FORBIDDEN_NAMES or name.startswith(".env.") or name.startswith("._"):
        return True
    return path.suffix in FORBIDDEN_SUFFIXES


def forbidden_scan() -> list[str]:
    matches: list[str] = []
    if not EDGE.exists():
        return matches
    for item in EDGE.rglob("*"):
        if is_forbidden(item):
            matches.append(item.relative_to(ROOT).as_posix())
    return sorted(matches)


def run_optional_validator(script: str, marker: str) -> tuple[bool, str]:
    path = ROOT / script
    if not path.is_file():
        return True, f"SKIP: {script} not present"
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.setdefault("PYTHONPATH", "AN_VANTARIS_ONE")
    proc = subprocess.run(["python3", script], cwd=ROOT, env=env, text=True, capture_output=True, check=False)
    output = "\n".join(part for part in [proc.stdout, proc.stderr] if part)
    return proc.returncode == 0 and marker in output, output


def main() -> int:
    checks: list[bool] = []
    report_text = read_text(REPORT)

    checks.append(check("R6 report exists", REPORT.is_file()))
    checks.append(check("R6 PASS marker exists in report", PASS_MARKER in report_text))
    checks.append(check("EDGE package exists", EDGE.is_dir()))

    count = file_count(EDGE)
    checks.append(check("EDGE file count is greater than 50", count > 50, str(count)))

    for folder in REQUIRED_FOLDERS:
        checks.append(check(f"Required folder exists: {folder}", (EDGE / folder).is_dir()))

    for indicator in RUNTIME_INDICATORS:
        checks.append(check(f"Runtime/source indicator exists: {indicator}", (EDGE / indicator).exists()))

    for boundary_file in PRESERVED_BOUNDARY_FILES:
        checks.append(check(f"Preserved boundary file exists: {boundary_file}", (EDGE / boundary_file).is_file()))

    matches = forbidden_scan()
    checks.append(check("Forbidden scan is empty", not matches, ", ".join(matches[:10])))

    for stage, (path, marker) in REPORT_MARKERS.items():
        checks.append(check(f"{stage} PASS marker exists", marker in read_text(path)))

    safety_phrases = [
        "UFMS source workspace modified: false",
        "Install executed: false",
        "Rollback executed: false",
        "DB migration executed: false",
        "Runtime action executed: false",
    ]
    for phrase in safety_phrases:
        checks.append(check(f"Report confirms {phrase}", phrase in report_text))

    route_ok, route_output = run_optional_validator(
        "scripts/validation/validate-one-package-route-enforcement.py",
        "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS",
    )
    checks.append(check("Package route enforcement PASS if validator exists", route_ok))
    if not route_ok:
        print(route_output)

    boundary_ok, boundary_output = run_optional_validator(
        "scripts/validation/validate-one-boundaries.py",
        "ONE_BOUNDARY_BASELINE_PASS",
    )
    checks.append(check("Boundary baseline PASS if validator exists", boundary_ok))
    if not boundary_ok:
        print(boundary_output)

    if all(checks):
        print(PASS_MARKER)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

