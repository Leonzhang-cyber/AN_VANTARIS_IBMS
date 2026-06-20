#!/usr/bin/env python3
"""Validate GA-R2 Airport read-only API local smoke and contract regression."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TEST_MODULE = ROOT / "AN_VANTARIS_ONE/tests/airport_ga_readonly_api/test_airport_ga_readonly_api.py"
SKELETON = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-api-skeleton.v1.json"
MOCK_CONTRACT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-api-mock-route-contract.v1.json"
BACKEND_INVENTORY = ROOT / "AN_VANTARIS_ONE/registries/backend-route-inventory.v1.json"
GA_R1_REPORT = ROOT / "ONE_AIRPORT_GA_R1_READONLY_API_ROUTE_IMPLEMENTATION_REPORT.md"
GA_R2_REPORT = ROOT / "ONE_AIRPORT_GA_R2_READONLY_API_LOCAL_SMOKE_AND_CONTRACT_REGRESSION_REPORT.md"
GA_R1_COMMIT = "c78fb35190c76027115b4bb92fc8322bf07b73c7"
PASS_MARKER = "ONE_AIRPORT_GA_R2_READONLY_API_LOCAL_SMOKE_AND_CONTRACT_REGRESSION_PASS"

EXPECTED_PATHS = {
    "AIRPORT_OVERVIEW": "/api/v1/one/airport/console/overview",
    "SYSTEMS_INTEGRATION_HEALTH": "/api/v1/one/airport/console/systems-integration-health",
    "ASSETS_TOPOLOGY": "/api/v1/one/airport/console/assets-topology",
    "ALARMS_EVENTS": "/api/v1/one/airport/console/alarms-events",
    "FAULT_CASES": "/api/v1/one/airport/console/fault-cases",
    "MAINTENANCE_WORK_ORDERS": "/api/v1/one/airport/console/maintenance-work-orders",
    "EVIDENCE_INVESTIGATION": "/api/v1/one/airport/console/evidence-investigation",
    "REPORTS": "/api/v1/one/airport/console/reports",
}
EXPECTED_PAYLOAD_KEYS = {
    "platform",
    "industryProjection",
    "releaseCandidate",
    "endpointKey",
    "route",
    "method",
    "readOnly",
    "productionActivation",
    "runtimeActivation",
    "databaseAccess",
    "dbWrite",
    "approvalExecution",
    "customerIdentifierLeakage",
    "source",
    "summary",
    "data",
    "filters",
    "facets",
    "pagination",
}
FORBIDDEN_RESPONSE_TERMS = ("customerAssetIdentifier", '"assetId"', '"deviceId"', "/Users/")
ALLOWED_CHANGED_PREFIXES = (
    "AN_VANTARIS_ONE/tests/airport_ga_readonly_api/",
    "scripts/validation/validate-one-airport-ga-r2-readonly-api-smoke-regression.py",
    "ONE_AIRPORT_GA_R2_READONLY_API_LOCAL_SMOKE_AND_CONTRACT_REGRESSION_REPORT.md",
    "AN_VANTARIS_ONE/registries/",
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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_test_module():
    spec = importlib.util.spec_from_file_location("ga_r2_airport_ga_readonly_test_module", TEST_MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _collect_smoke() -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    test_module = _load_test_module()
    ga_module, api_bp = test_module._load_isolated_ga_module()
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(api_bp)
    client = app.test_client()
    get_matrix: list[dict[str, Any]] = []
    non_get_matrix: list[dict[str, Any]] = []
    serialized_responses: list[str] = []
    for endpoint_key, path in EXPECTED_PATHS.items():
        response = client.get(path)
        body = response.get_json()
        payload = body.get("data", {}) if isinstance(body, dict) else {}
        serialized_responses.append(json.dumps(body, sort_keys=True))
        get_matrix.append(
            {
                "endpointKey": endpoint_key,
                "path": path,
                "statusCode": response.status_code,
                "json": response.is_json,
                "platform": payload.get("platform"),
                "industryProjection": payload.get("industryProjection"),
                "readOnly": payload.get("readOnly"),
                "productionActivation": payload.get("productionActivation"),
                "runtimeActivation": payload.get("runtimeActivation"),
                "dbWrite": payload.get("dbWrite"),
                "approvalExecution": payload.get("approvalExecution"),
                "customerIdentifierLeakage": payload.get("customerIdentifierLeakage"),
                "sourcePath": payload.get("source", {}).get("path"),
                "sourceRootKey": payload.get("source", {}).get("rootKey"),
                "payloadKeys": sorted(payload.keys()),
                "pass": (
                    response.status_code == 200
                    and response.is_json
                    and body.get("code") == 200
                    and payload.get("platform") == "VANTARIS ONE"
                    and payload.get("industryProjection") == "airport"
                    and payload.get("readOnly") is True
                    and payload.get("productionActivation") is False
                    and payload.get("runtimeActivation") is False
                    and payload.get("dbWrite") is False
                    and payload.get("approvalExecution") is False
                    and payload.get("customerIdentifierLeakage") is False
                    and set(payload) == EXPECTED_PAYLOAD_KEYS
                    and payload.get("source", {}).get("type") == "local_projection_artifact"
                ),
            }
        )
        for method in ("post", "put", "patch", "delete"):
            non_get = getattr(client, method)(path)
            non_get_matrix.append(
                {
                    "endpointKey": endpoint_key,
                    "path": path,
                    "method": method.upper(),
                    "statusCode": non_get.status_code,
                    "businessSuccess": bool(non_get.is_json and (non_get.get_json() or {}).get("code") == 200),
                    "pass": non_get.status_code in {404, 405} and not (non_get.is_json and (non_get.get_json() or {}).get("code") == 200),
                }
            )
    assert set(ga_module.ROUTES) == set(EXPECTED_PATHS)
    return get_matrix, non_get_matrix, "\n".join(serialized_responses)


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []

    head = _run(["git", "rev-parse", "HEAD"]).stdout.strip()
    status = _run(["git", "status", "-sb"]).stdout.strip()
    checks.append(("Baseline includes GA-R1 ancestor", _run(["git", "merge-base", "--is-ancestor", GA_R1_COMMIT, "HEAD"]).returncode == 0))
    checks.append(("Working branch is main ahead/not pushed state visible", status.startswith("## main...origin/main")))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to GA-R2 validation/report scope", not disallowed))
    checks.append(("Forbidden workspaces untouched", not forbidden))
    if disallowed:
        errors.append(f"changes outside GA-R2 scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    skeleton = _load_json(SKELETON)
    mock = _load_json(MOCK_CONTRACT)
    inventory = _load_json(BACKEND_INVENTORY)
    skeleton_paths = {item["endpointKey"]: item["path"] for item in skeleton["endpointSkeletons"] if item["method"] == "GET"}
    response_contracts = {item["endpointKey"]: item for item in skeleton["responseContracts"]}
    mock_paths = {item["endpointKey"]: item["path"] for item in mock["mockRouteContracts"]}
    inventory_paths = {item["fullPath"] for item in inventory["routes"] if item["sourcePath"].endswith("airport_ga_readonly_api.py")}
    checks.append(("A7 skeleton paths unchanged", skeleton_paths == EXPECTED_PATHS))
    checks.append(("A7 mock route paths unchanged", mock_paths == EXPECTED_PATHS))
    checks.append(("Backend route inventory contains exactly 8 GA-R1 routes", inventory_paths == set(EXPECTED_PATHS.values())))

    ga_r1_report = GA_R1_REPORT.read_text(encoding="utf-8")
    checks.append(("GA-R1 report route list matches frozen paths", all(f"GET `{path}`" in ga_r1_report for path in EXPECTED_PATHS.values()) and ga_r1_report.count("GET `/api/v1/one/airport/console/") == 8))
    checks.append(("GA-R2 report contains pass marker", GA_R2_REPORT.is_file() and PASS_MARKER in GA_R2_REPORT.read_text(encoding="utf-8")))

    env = {
        **os.environ,
        "PYTHONPATH": f"{ROOT / 'AN_VANTARIS_IBMS-backend'}:{ROOT / 'AN_VANTARIS_ONE'}",
        "IBMS_LOCAL_SMOKE": "true",
    }
    unit_proc = _run([sys.executable, "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/airport_ga_readonly_api", "-p", "test_*.py"], env=env)
    checks.append(("Focused local smoke unittest passes", unit_proc.returncode == 0))
    if unit_proc.returncode != 0:
        errors.append(unit_proc.stdout[-4000:] or unit_proc.stderr[-4000:] or "focused local smoke unittest failed")

    try:
        get_matrix, non_get_matrix, serialized = _collect_smoke()
        checks.append(("Eight GET smoke rows pass", len(get_matrix) == 8 and all(row["pass"] for row in get_matrix)))
        checks.append(("Thirty-two non-GET rows reject business success", len(non_get_matrix) == 32 and all(row["pass"] for row in non_get_matrix)))
        checks.append(("No customer identifier or absolute path leakage", not any(term in serialized for term in FORBIDDEN_RESPONSE_TERMS)))
        contract_mapping_ok = all(
            row["sourcePath"] == response_contracts[row["endpointKey"]]["sourceArtifactPath"]
            and row["sourceRootKey"] == response_contracts[row["endpointKey"]]["projectionRootKey"]
            for row in get_matrix
        )
        checks.append(("Artifact source mapping matches A7 response contracts", contract_mapping_ok))
    except Exception as exc:
        checks.extend(
            [
                ("Eight GET smoke rows pass", False),
                ("Thirty-two non-GET rows reject business success", False),
                ("No customer identifier or absolute path leakage", False),
                ("Artifact source mapping matches A7 response contracts", False),
            ]
        )
        errors.append(f"smoke collection failed: {exc}")

    print("ONE_AIRPORT_GA_R2_READONLY_API_LOCAL_SMOKE_AND_CONTRACT_REGRESSION_VALIDATION")
    print(f"HEAD={head}")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_AIRPORT_GA_R2_READONLY_API_LOCAL_SMOKE_AND_CONTRACT_REGRESSION_FAIL")
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

