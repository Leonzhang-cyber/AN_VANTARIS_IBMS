#!/usr/bin/env python3
"""Validate GA-R3 Airport read-only frontend route/page implementation."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "AN_VANTARIS_IBMS-frontend"
ROUTES = FRONTEND / "src/router/routes.ts"
MENU = FRONTEND / "src/services/menu/static-menu.ts"
API_CLIENT = FRONTEND / "src/services/api/airportGaReadonly.ts"
API_INDEX = FRONTEND / "src/services/api/index.ts"
PAGE = FRONTEND / "src/modules/airport/AirportGaReadonlyConsole.vue"
REPORT = ROOT / "ONE_AIRPORT_GA_R3_READONLY_FRONTEND_ROUTE_PAGE_IMPLEMENTATION_REPORT.md"
SKELETON = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-frontend-skeleton.v1.json"
API_SKELETON = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-api-skeleton.v1.json"
PASS_MARKER = "ONE_AIRPORT_GA_R3_READONLY_FRONTEND_ROUTE_PAGE_IMPLEMENTATION_PASS"

EXPECTED_FRONTEND_PATHS = {
    "/one/airport/overview",
    "/one/airport/systems-integration-health",
    "/one/airport/assets-topology",
    "/one/airport/alarms-events",
    "/one/airport/fault-cases",
    "/one/airport/maintenance-work-orders",
    "/one/airport/evidence-investigation",
    "/one/airport/reports",
}
EXPECTED_API_PATHS = {
    "/v1/one/airport/console/overview",
    "/v1/one/airport/console/systems-integration-health",
    "/v1/one/airport/console/assets-topology",
    "/v1/one/airport/console/alarms-events",
    "/v1/one/airport/console/fault-cases",
    "/v1/one/airport/console/maintenance-work-orders",
    "/v1/one/airport/console/evidence-investigation",
    "/v1/one/airport/console/reports",
}
FORBIDDEN_CHANGED_PREFIXES = (
    "/Volumes/Work/VANTARIS_UFMS_FULL",
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_LINK/",
    "AN_VANTARIS_Contracts/",
    "database/",
    "migrations/",
)
ALLOWED_CHANGED_PREFIXES = (
    "AN_VANTARIS_IBMS-frontend/src/modules/airport/",
    "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts",
    "AN_VANTARIS_IBMS-frontend/src/services/api/index.ts",
    "AN_VANTARIS_IBMS-frontend/src/router/routes.ts",
    "AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts",
    "AN_VANTARIS_ONE/registries/frontend-route-inventory.v1.json",
    "AN_VANTARIS_ONE/registries/package-route-enforcement.v1.json",
    "scripts/validation/build-one-frontend-route-inventory.py",
    "scripts/validation/validate-one-airport-ga-r3-readonly-frontend-page.py",
    "ONE_AIRPORT_GA_R3_READONLY_FRONTEND_ROUTE_PAGE_IMPLEMENTATION_REPORT.md",
)


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


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _literal_paths(text: str) -> set[str]:
    return set(re.findall(r"['\"](/(?:api/)?(?:v1/)?one/airport[^'\"]*)['\"]", text))


def _api_paths(text: str) -> set[str]:
    return set(re.findall(r"\bapiPath\s*:\s*['\"]([^'\"]+)['\"]", text))


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []

    checks.append(("Frontend route file exists", ROUTES.is_file()))
    checks.append(("Airport API client exists", API_CLIENT.is_file()))
    checks.append(("Airport page exists", PAGE.is_file()))
    checks.append(("GA-R3 report contains pass marker", REPORT.is_file() and PASS_MARKER in REPORT.read_text(encoding="utf-8")))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to GA-R3 frontend/report scope", not disallowed))
    checks.append(("Forbidden workspaces untouched", not forbidden))
    if disallowed:
        errors.append(f"changes outside GA-R3 scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    route_text = ROUTES.read_text(encoding="utf-8")
    menu_text = MENU.read_text(encoding="utf-8")
    api_text = API_CLIENT.read_text(encoding="utf-8")
    page_text = PAGE.read_text(encoding="utf-8")
    api_index_text = API_INDEX.read_text(encoding="utf-8")
    combined = "\n".join([route_text, menu_text, api_text, page_text, api_index_text])

    frontend_contract_paths = {row["pathCandidate"] for row in _load_json(SKELETON)["routeSkeletons"]}
    api_contract_paths = {
        item["path"].removeprefix("/api")
        for item in _load_json(API_SKELETON)["endpointSkeletons"]
        if item.get("method") == "GET"
    }
    route_paths = _literal_paths(route_text)
    api_paths = _api_paths(api_text)
    checks.append(("Eight A8 frontend paths implemented", EXPECTED_FRONTEND_PATHS.issubset(route_paths) and frontend_contract_paths == EXPECTED_FRONTEND_PATHS))
    checks.append(("Only GA-R1/R2 API paths used by client", api_paths == EXPECTED_API_PATHS and api_contract_paths == EXPECTED_API_PATHS))
    checks.append(("Airport menu entry present", "Airport GA Read-Only" in menu_text and all(path in menu_text for path in EXPECTED_FRONTEND_PATHS)))
    checks.append(("API client exported", "airportGaReadonlyApi" in api_index_text))
    checks.append(("Only GET calls in Airport API client", ".get<" in api_text and not any(term in api_text for term in (".post", ".put", ".patch", ".delete"))))
    checks.append(("No write/action controls in page", not any(term in page_text for term in ("Approve", "Dispatch", "Close Case", "@click=\"approve", "@click=\"dispatch"))))
    checks.append(("No customer identifier literal exposure", not any(term in combined for term in ("customerAssetIdentifier", "assetId", "deviceId"))))
    checks.append(("No local absolute path literal exposure", "/Users/" not in combined))
    checks.append(("Read-only guardrail text present", "read-only" in page_text.lower() and "No actions, writes" in page_text))
    checks.append(("No UFMS live path usage", "/Volumes/Work/VANTARIS_UFMS_FULL" not in combined and "VANTARIS_UFMS_FULL" not in combined))

    env = {**os.environ}
    typecheck = _run(["npm", "--prefix", "AN_VANTARIS_IBMS-frontend", "run", "type-check"], env=env | {"CI": "true"})
    checks.append(("Frontend type-check passes", typecheck.returncode == 0))
    if typecheck.returncode != 0:
        errors.append(typecheck.stdout[-4000:] or typecheck.stderr[-4000:] or "frontend type-check failed")

    print("ONE_AIRPORT_GA_R3_READONLY_FRONTEND_ROUTE_PAGE_IMPLEMENTATION_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_AIRPORT_GA_R3_READONLY_FRONTEND_ROUTE_PAGE_IMPLEMENTATION_FAIL")
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
