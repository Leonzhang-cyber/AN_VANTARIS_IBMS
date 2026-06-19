#!/usr/bin/env python3
"""Validate the bounded Governance Audit Integration Pilot."""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "AN_VANTARIS_ONE/registries/backend-route-inventory.v1.json"
ROUTE_FILE = ROOT / "AN_VANTARIS_IBMS-backend/src/api/system/menu_api.py"
PILOT_HELPER = ROOT / "AN_VANTARIS_IBMS-backend/src/governance/audit/pilot.py"
TEST_FILE = ROOT / "AN_VANTARIS_IBMS-backend/src/tests/governance/audit/test_audit_integration_pilot.py"
VALIDATOR = ROOT / "scripts/validation/validate-one-audit-integration-pilot.py"
PROVIDER_VALIDATOR = ROOT / "scripts/validation/validate-one-audit-provider-boundary.py"
SELECTED = {
    "ROUTE-POST-C39FFBE9F5DC": {
        "method": "POST",
        "path": "/api/system/versions",
        "source": "AN_VANTARIS_IBMS-backend/src/api/system/menu_api.py",
    }
}
ALLOWED = {
    "AN_VANTARIS_IBMS-backend/src/api/system/menu_api.py",
    "AN_VANTARIS_IBMS-backend/src/governance/audit/pilot.py",
    "AN_VANTARIS_IBMS-backend/src/governance/audit/__init__.py",
    "AN_VANTARIS_IBMS-backend/src/tests/governance/audit/test_audit_integration_pilot.py",
    "scripts/validation/validate-one-audit-provider-boundary.py",
    "scripts/validation/validate-one-audit-integration-pilot.py",
}


def changed_paths() -> set[str]:
    tracked = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"], cwd=ROOT,
        capture_output=True, text=True, check=False,
    ).stdout.splitlines()
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT,
        capture_output=True, text=True, check=False,
    ).stdout.splitlines()
    paths = set(tracked + untracked)
    if not paths:
        committed = subprocess.run(
            ["git", "diff", "--name-only", "HEAD^", "HEAD"], cwd=ROOT,
            capture_output=True, text=True, check=False,
        ).stdout.splitlines()
        paths = set(committed)
    return paths


def main() -> int:
    errors: list[str] = []
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    routes = {row["routeId"]: row for row in inventory["routes"]}
    for route_id, expected in SELECTED.items():
        route = routes.get(route_id)
        if not route:
            errors.append(f"selected route missing from inventory: {route_id}")
            continue
        if expected["method"] not in route["methods"] or route["fullPath"] != expected["path"]:
            errors.append(f"selected route signature mismatch: {route_id}")
        if route["sourcePath"] != expected["source"]:
            errors.append(f"selected route source mismatch: {route_id}")
        if route["runtimeClass"] == "TEST_ONLY" or route["authenticationClass"] != "AUTHENTICATED":
            errors.append(f"selected route is not authenticated production/legacy: {route_id}")
        if route["operationClass"] not in {"WRITE", "CONTROL"}:
            errors.append(f"selected route is not an administrative mutation: {route_id}")
    if len(SELECTED) > 3:
        errors.append("more than three pilot routes selected")

    route_text = ROUTE_FILE.read_text(encoding="utf-8")
    helper_text = PILOT_HELPER.read_text(encoding="utf-8")
    combined = route_text + "\n" + helper_text
    prohibited_route_terms = [
        "/login", "/logout", "refresh", "password", "private_key",
        "/api/iot", "/assets", "/work-orders", "/evidence",
        "/adapters/ufms", "/uedge", "/link", "/telemetry",
    ]
    integrated_section = route_text[
        route_text.index("def create_version"):route_text.index("@api_bp.route('/system/versions/<version_code>'")
    ]
    if any(term in integrated_section.lower() for term in prohibited_route_terms):
        errors.append("prohibited route category appears in selected integration")
    if "@audit_create_version_pilot" not in route_text or "AuditService" not in helper_text:
        errors.append("selected route does not call Governance Audit Service integration")
    if "Authorization" in helper_text or "request.headers)" in helper_text:
        errors.append("raw request or headers passed into AuditRecord")
    if "PilotAuditInput(" not in helper_text:
        errors.append("route does not pass explicit structured audit input")
    for term in ("reports", "ucde", "ufms", "uedge", "link"):
        if f"src.{term}" in combined.lower():
            errors.append(f"cross-module audit ownership import found: {term}")
    if ".jsonl" in combined.lower() or "open(" in helper_text or "write_text" in helper_text:
        errors.append("file or JSONL persistence added")
    if "__tablename__" in combined or "sqlalchemy" in helper_text.lower():
        errors.append("ORM audit persistence added")
    if "Blueprint" in helper_text or "@api_bp.route" in helper_text:
        errors.append("public audit API added")
    if "NON_PRODUCTION_IN_MEMORY_PROVIDER" not in helper_text:
        errors.append("pilot runtime limitation is not explicit")
    if "current_app.extensions" not in helper_text:
        errors.append("application-scoped provider lifecycle not used")
    if "canonical_state_digest" not in helper_text:
        errors.append("state digest helper not used")
    if not TEST_FILE.is_file():
        errors.append("focused pilot tests missing")

    try:
        tree = ast.parse(helper_text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Global, ast.Nonlocal)):
                errors.append("broad global mutable provider state found")
    except SyntaxError as exc:
        errors.append(f"pilot helper syntax error at line {exc.lineno}")

    changed = changed_paths()
    outside = sorted(changed - ALLOWED)
    if outside:
        errors.append("changed files outside declared pilot scope: " + ", ".join(outside))
    route_files = {
        path for path in changed
        if path.startswith("AN_VANTARIS_IBMS-backend/src/api/") and path.endswith(".py")
    }
    if route_files != {"AN_VANTARIS_IBMS-backend/src/api/system/menu_api.py"}:
        errors.append("pilot route-file scope is broader than the one selected file")
    if any(path.startswith("AN_VANTARIS_IBMS-backend/migrations/") for path in changed):
        errors.append("migration file added")

    checks = [
        ("Selected route scope", not any("selected route" in item or "three pilot" in item or "route-file scope" in item for item in errors)),
        ("Administrative mutation scope", not any("administrative mutation" in item or "prohibited route" in item for item in errors)),
        ("Audit service usage", not any("Audit Service" in item or "structured audit" in item for item in errors)),
        ("Secret exclusion", not any("raw request" in item for item in errors)),
        ("No JSONL persistence", not any("JSONL" in item or "file or JSONL persistence" in item for item in errors)),
        ("No ORM persistence", not any("ORM" in item or "migration file" in item for item in errors)),
        ("No public API", not any("public audit API" in item for item in errors)),
        ("No cross-module ownership", not any("cross-module" in item for item in errors)),
        ("Allowed path scope", not any("outside declared" in item for item in errors)),
        ("Runtime limitation honesty", not any("runtime limitation" in item or "provider lifecycle" in item or "global mutable" in item for item in errors)),
    ]
    print("[ONE AUDIT INTEGRATION PILOT VALIDATION]")
    for label, passed in checks:
        print(f"{label}: {'PASS' if passed else 'FAIL'}")
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        print("ONE_AUDIT_INTEGRATION_PILOT_FAIL")
        return 1
    print("ONE_AUDIT_INTEGRATION_PILOT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
