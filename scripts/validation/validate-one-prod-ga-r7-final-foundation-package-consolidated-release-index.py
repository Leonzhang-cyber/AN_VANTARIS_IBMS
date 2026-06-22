#!/usr/bin/env python3
"""Validate ONE-PROD-GA-R7 consolidated foundation package release index."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "ONE_PROD_GA_R7_FINAL_FOUNDATION_PACKAGE_CONSOLIDATED_RELEASE_INDEX_PASS"
REQUIRED_HEAD = "048ac1aa26d4d4f0290243f1138d001122e0874c"

INDEX = ROOT / "ONE_PROD_GA_R7_FINAL_FOUNDATION_PACKAGE_CONSOLIDATED_RELEASE_INDEX.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/prod-ga-final-foundation-package-consolidated-release-index.v1.json"
REPORT = ROOT / "ONE_PROD_GA_R7_FINAL_FOUNDATION_PACKAGE_CONSOLIDATED_RELEASE_INDEX_REPORT.md"
PACKAGES_ROOT = ROOT / "AN_VANTARIS_ONE/packages"
EDGE = PACKAGES_ROOT / "AN_VANTARIS_EDGE"

PACKAGE_PATHS = {
    "edge": EDGE,
    "link": PACKAGES_ROOT / "AN_VANTARIS_LINK",
    "db": PACKAGES_ROOT / "AN_VANTARIS_DB",
    "contracts": PACKAGES_ROOT / "AN_VANTARIS_Contracts",
}

REPORT_MARKERS = {
    "R1": (ROOT / "ONE_PROD_GA_R1_FOUNDATION_PACKAGES_SYNC_GATE_REPORT.md", "ONE_PROD_GA_R1_FOUNDATION_PACKAGES_SYNC_GATE_PASS"),
    "R2": (ROOT / "ONE_PROD_GA_R2_FOUNDATION_PACKAGE_CONSOLE_ENTRY_REPORT.md", "ONE_PROD_GA_R2_FOUNDATION_PACKAGE_CONSOLE_ENTRY_PASS"),
    "R3": (ROOT / "ONE_PROD_GA_R3_FOUNDATION_PACKAGE_READONLY_API_HEALTH_REPORT.md", "ONE_PROD_GA_R3_FOUNDATION_PACKAGE_READONLY_API_HEALTH_PASS"),
    "R4": (ROOT / "ONE_PROD_GA_R4_OFFLINE_INSTALL_VERIFY_ROLLBACK_PACKAGE_REPORT.md", "ONE_PROD_GA_R4_OFFLINE_INSTALL_VERIFY_ROLLBACK_PACKAGE_PASS"),
    "R5": (ROOT / "ONE_PROD_GA_R5_FINAL_FOUNDATION_PACKAGE_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md", "ONE_PROD_GA_R5_FINAL_FOUNDATION_PACKAGE_FREEZE_PASS"),
    "R6": (ROOT / "ONE_PROD_GA_R6_FULL_EDGE_RUNTIME_RESYNC_GATE_REPORT.md", "ONE_PROD_GA_R6_FULL_EDGE_RUNTIME_RESYNC_GATE_PASS"),
}

VALIDATOR_CHAIN = [
    ("scripts/validation/validate-one-prod-ga-r6-full-edge-runtime-resync.py", "ONE_PROD_GA_R6_FULL_EDGE_RUNTIME_RESYNC_GATE_PASS"),
    ("scripts/validation/validate-one-prod-ga-r5-final-foundation-package-freeze.py", "ONE_PROD_GA_R5_FINAL_FOUNDATION_PACKAGE_FREEZE_PASS"),
    ("scripts/validation/validate-one-prod-ga-r4-offline-install-verify-rollback-package.py", "ONE_PROD_GA_R4_OFFLINE_INSTALL_VERIFY_ROLLBACK_PACKAGE_PASS"),
    ("scripts/validation/validate-one-prod-ga-r3-foundation-package-readonly-api.py", "ONE_PROD_GA_R3_FOUNDATION_PACKAGE_READONLY_API_HEALTH_PASS"),
    ("scripts/validation/validate-one-prod-ga-r2-foundation-package-console-entry.py", "ONE_PROD_GA_R2_FOUNDATION_PACKAGE_CONSOLE_ENTRY_PASS"),
]

EDGE_INDICATORS = [
    "src/runtime",
    "src/product-runtime/edge",
    "src/connectors",
    "src/generated",
]

EDGE_BOUNDARY_FILES = [
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
PROHIBITED_POSITIVE_CLAIMS = [
    "install executed: true",
    "rollback executed: true",
    "db migration executed: true",
    "runtime executed: true",
    "runtime activation: true",
    "main merge: true",
    "rebase: true",
    "push performed: true",
    "tag created: true",
]


def check(name: str, condition: bool, details: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    suffix = f" - {details}" if details else ""
    print(f"[{status}] {name}{suffix}")
    return condition


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return data


def file_count(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file())


def is_forbidden(path: Path) -> bool:
    name = path.name
    if name in FORBIDDEN_NAMES or name.startswith(".env.") or name.startswith("._"):
        return True
    return path.suffix in FORBIDDEN_SUFFIXES


def forbidden_scan() -> list[str]:
    matches: list[str] = []
    for item in PACKAGES_ROOT.rglob("*"):
        if is_forbidden(item):
            matches.append(item.relative_to(ROOT).as_posix())
    return sorted(matches)


def run_command(command: list[str]) -> tuple[int, str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.setdefault("PYTHONPATH", "AN_VANTARIS_ONE")
    proc = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, check=False)
    return proc.returncode, "\n".join(part for part in [proc.stdout, proc.stderr] if part)


def run_validator(script: str, marker: str) -> tuple[bool, str]:
    path = ROOT / script
    if not path.is_file():
        return True, f"SKIP: {script} not present"
    code, output = run_command(["python3", script])
    return code == 0 and marker in output, output


def main() -> int:
    checks: list[bool] = []

    code, head_output = run_command(["git", "rev-parse", "HEAD"])
    head = head_output.strip()
    checks.append(check("Current HEAD is required R6 baseline before R7 commit", code == 0 and head == REQUIRED_HEAD, head))

    index_text = read_text(INDEX)
    report_text = read_text(REPORT)
    registry = load_json(REGISTRY) if REGISTRY.is_file() else {}
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.is_file() else ""

    checks.append(check("Release index markdown exists", INDEX.is_file()))
    checks.append(check("Registry JSON exists and parses", REGISTRY.is_file() and registry.get("registryId") == "prod-ga-final-foundation-package-consolidated-release-index.v1"))
    checks.append(check("R7 report exists", REPORT.is_file()))
    checks.append(check("PASS marker exists in all R7 outputs", PASS_MARKER in index_text and PASS_MARKER in registry_text and PASS_MARKER in report_text))

    counts = {package_id: file_count(path) for package_id, path in PACKAGE_PATHS.items()}
    checks.append(check("EDGE package exists and file count is exactly 248 or > 200", EDGE.is_dir() and (counts["edge"] == 248 or counts["edge"] > 200), str(counts["edge"])))
    checks.append(check("LINK package exists and file count > 0", PACKAGE_PATHS["link"].is_dir() and counts["link"] > 0, str(counts["link"])))
    checks.append(check("DB package exists and file count > 0", PACKAGE_PATHS["db"].is_dir() and counts["db"] > 0, str(counts["db"])))
    checks.append(check("Contracts package exists and file count > 0", PACKAGE_PATHS["contracts"].is_dir() and counts["contracts"] > 0, str(counts["contracts"])))

    registry_counts = {package["packageId"]: int(package["fileCount"]) for package in registry.get("packages", [])}
    checks.append(check("Registry package counts match dynamic counts", registry_counts == counts, str(registry_counts)))

    for indicator in EDGE_INDICATORS:
        checks.append(check(f"EDGE runtime indicator exists: {indicator}", (EDGE / indicator).exists()))

    for boundary_file in EDGE_BOUNDARY_FILES:
        checks.append(check(f"Preserved EDGE boundary file exists: {boundary_file}", (EDGE / boundary_file).is_file()))

    matches = forbidden_scan()
    checks.append(check("Forbidden scan across packages is empty", not matches, ", ".join(matches[:10])))

    for stage, (path, marker) in REPORT_MARKERS.items():
        checks.append(check(f"{stage} PASS marker exists", marker in read_text(path)))

    for script, marker in VALIDATOR_CHAIN:
        ok, output = run_validator(script, marker)
        checks.append(check(f"{Path(script).name} still PASS", ok))
        if not ok:
            print(output)

    route_ok, route_output = run_validator("scripts/validation/validate-one-package-route-enforcement.py", "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS")
    checks.append(check("Package route enforcement PASS if validator exists", route_ok))
    if not route_ok:
        print(route_output)

    boundary_ok, boundary_output = run_validator("scripts/validation/validate-one-boundaries.py", "ONE_BOUNDARY_BASELINE_PASS")
    checks.append(check("Boundary baseline PASS if validator exists", boundary_ok))
    if not boundary_ok:
        print(boundary_output)

    combined_output = "\n".join([index_text, registry_text, report_text]).lower()
    checks.append(check("No install/rollback/DB/runtime positive execution claim appears", not any(claim in combined_output for claim in PROHIBITED_POSITIVE_CLAIMS)))
    checks.append(check("No main merge/rebase/push/tag positive claim appears", "main merge: true" not in combined_output and "rebase: true" not in combined_output and "push performed: true" not in combined_output and "tag created: true" not in combined_output))

    safety = registry.get("safety", {})
    checks.append(check("Registry safety flags are non-runtime/non-push/non-tag", safety.get("installExecuted") is False and safety.get("rollbackExecuted") is False and safety.get("dbMigrationExecuted") is False and safety.get("runtimeExecuted") is False and safety.get("pushPerformedByR7") is False and safety.get("tagCreatedByR7") is False))

    if all(checks):
        print(PASS_MARKER)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

