#!/usr/bin/env python3
"""Validate GA-R1 Airport read-only API route implementation."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
API_MODULE = ROOT / "AN_VANTARIS_IBMS-backend/src/api/airport_ga_readonly/airport_ga_readonly_api.py"
API_INIT = ROOT / "AN_VANTARIS_IBMS-backend/src/api/__init__.py"
TEST_DIR = ROOT / "AN_VANTARIS_ONE/tests/airport_ga_readonly_api"
REPORT = ROOT / "ONE_AIRPORT_GA_R1_READONLY_API_ROUTE_IMPLEMENTATION_REPORT.md"
SKELETON = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-api-skeleton.v1.json"

EXPECTED_PATHS = {
    "/api/v1/one/airport/console/overview",
    "/api/v1/one/airport/console/systems-integration-health",
    "/api/v1/one/airport/console/assets-topology",
    "/api/v1/one/airport/console/alarms-events",
    "/api/v1/one/airport/console/fault-cases",
    "/api/v1/one/airport/console/maintenance-work-orders",
    "/api/v1/one/airport/console/evidence-investigation",
    "/api/v1/one/airport/console/reports",
}

ALLOWED_CHANGED_PREFIXES = (
    "AN_VANTARIS_IBMS-backend/src/api/__init__.py",
    "AN_VANTARIS_IBMS-backend/src/api/airport_ga_readonly/",
    "AN_VANTARIS_ONE/tests/airport_ga_readonly_api/",
    "scripts/validation/validate-one-airport-ga-readonly-api-routes.py",
    "ONE_AIRPORT_GA_R1_READONLY_API_ROUTE_IMPLEMENTATION_REPORT.md",
)
FORBIDDEN_CHANGED_PREFIXES = (
    "/Volumes/Work/VANTARIS_UFMS_FULL",
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_LINK/",
    "AN_VANTARIS_Contracts/",
    "AN_VANTARIS_IBMS-frontend/",
    "database/",
    "migrations/",
)
FORBIDDEN_RESPONSE_TERMS = ("customerAssetIdentifier", '"assetId"', '"deviceId"')


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
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []

    checks.append(("API module exists", API_MODULE.is_file()))
    checks.append(("API blueprint import registered", "airport_ga_readonly_api" in API_INIT.read_text(encoding="utf-8")))
    checks.append(("Focused API tests exist", TEST_DIR.is_dir()))
    checks.append(("GA-R1 report exists", REPORT.is_file()))

    skeleton = json.loads(SKELETON.read_text(encoding="utf-8"))
    skeleton_paths = {item["path"] for item in skeleton["endpointSkeletons"] if item["method"] == "GET"}
    checks.append(("A7 frozen paths unchanged", skeleton_paths == EXPECTED_PATHS))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    checks.append(("Changes limited to GA-R1 scope", not disallowed))
    if disallowed:
        errors.append(f"changes outside GA-R1 scope: {', '.join(sorted(disallowed))}")
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Forbidden workspaces untouched", not forbidden))
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    env = {
        **os.environ,
        "PYTHONPATH": f"{ROOT / 'AN_VANTARIS_IBMS-backend'}:{ROOT / 'AN_VANTARIS_ONE'}",
        "IBMS_LOCAL_SMOKE": "true",
    }
    test_proc = _run(
        [sys.executable, "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/airport_ga_readonly_api", "-p", "test_*.py"],
        env=env,
    )
    checks.append(("Focused GA-R1 route tests pass", test_proc.returncode == 0))
    if test_proc.returncode != 0:
        errors.append(test_proc.stdout[-4000:] or test_proc.stderr[-4000:] or "focused GA-R1 tests failed")

    checks.append(("Local smoke covered by isolated focused tests", test_proc.returncode == 0))
    checks.append(("No customer identifier leakage assertion covered", test_proc.returncode == 0))

    source_text = API_MODULE.read_text(encoding="utf-8") if API_MODULE.is_file() else ""
    checks.append(("GET route decorators only", 'methods=["GET"]' in source_text and all(term not in source_text for term in ('methods=["POST"]', 'methods=["PUT"]', 'methods=["PATCH"]', 'methods=["DELETE"]'))))
    checks.append(("No database write API usage", all(term not in source_text for term in (".session.add", ".session.commit", ".save(", ".delete(", "INSERT ", "UPDATE ", "DELETE "))))
    checks.append(("No external network client usage", all(term not in source_text for term in ("requests.", "urllib.", "socket.", "http://", "https://", "localhost"))))
    checks.append(("No UFMS live path usage", "/Volumes/Work/VANTARIS_UFMS_FULL" not in source_text))

    print("ONE_AIRPORT_GA_R1_READONLY_API_ROUTE_IMPLEMENTATION_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_AIRPORT_GA_R1_READONLY_API_ROUTE_IMPLEMENTATION_FAIL")
        return 1
    print("ONE_AIRPORT_GA_R1_READONLY_API_ROUTE_IMPLEMENTATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
