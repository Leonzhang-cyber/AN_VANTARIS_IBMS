#!/usr/bin/env python3
"""Validate UMMS-R12 read-only frontend / UConsole card entry."""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SERVICE = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/umms.ts"
COMPONENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/umms/UmmsReadonlyOverview.vue"
ROUTES = ROOT / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts"
REPORT = ROOT / "ONE_UMMS_R12_READONLY_FRONTEND_UCONSOLE_CARD_ENTRY_REPORT.md"
PASS_MARKER = "ONE_UMMS_R12_READONLY_FRONTEND_UCONSOLE_CARD_ENTRY_PASS"

EXPECTED_ENDPOINTS = (
    "/v1/one/umms/package-entry",
    "/v1/one/umms/stakeholder-review",
    "/v1/one/umms/readiness-summary",
    "/v1/one/umms/customer-core-functions",
    "/v1/one/umms/safety-posture",
)
EXPECTED_ROUTE = "/one/umms/overview"
CAPABILITY_TERMS = (
    "Work Order Management",
    "Asset Registry",
    "Preventive Maintenance",
    "Spare Parts / Inventory",
    "Vendor / Contract / SLA",
    "UCDE Evidence Closure Alignment",
    "HMI Locator Binding",
    "Existing System Onboarding",
    "Engineer Commissioning Diagnostics",
    "Remote / Distributed Deployment Readiness",
)
SAFETY_TERMS = (
    "No DB write",
    "No workflow",
    "No approval execution",
    "No runtime activation",
    "No production activation",
    "No EDGE/LINK runtime call",
)
FORBIDDEN_ACTION_TERMS = (
    "<el-button",
    "write button",
    "approval button",
    "activation button",
    "deployment button",
    "workflow action",
    "work order runtime action",
    "pm execution action",
    "inventory transaction action",
    "vendor/contract/sla runtime action",
    "evidence closure action",
    "hmi runtime/control action",
)
FORBIDDEN_CLIENT_TERMS = (
    "request.post(",
    "request.put(",
    "request.patch(",
    "request.delete(",
    "axios.post(",
    "axios.put(",
    "axios.patch(",
    "axios.delete(",
)
FORBIDDEN_WRITE_TERMS = (
    ".session.add",
    ".session.commit",
    ".save(",
    "INSERT ",
    "UPDATE ",
    "DELETE FROM",
)
ALLOWED_CHANGED_PREFIXES = (
    "AN_VANTARIS_IBMS-frontend/src/services/api/umms.ts",
    "AN_VANTARIS_IBMS-frontend/src/modules/umms/UmmsReadonlyOverview.vue",
    "AN_VANTARIS_IBMS-frontend/src/router/routes.ts",
    "AN_VANTARIS_ONE/registries/frontend-route-inventory.v1.json",
    "AN_VANTARIS_ONE/registries/package-route-enforcement.v1.json",
    "scripts/validation/build-one-frontend-route-inventory.py",
    "scripts/validation/validate-one-umms-r12-readonly-frontend-uconsole-card-entry.py",
    "ONE_UMMS_R12_READONLY_FRONTEND_UCONSOLE_CARD_ENTRY_REPORT.md",
)
FORBIDDEN_CHANGED_PREFIXES = (
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_LINK/",
    "AN_VANTARIS_Contracts/",
    "/Volumes/Work/VANTARIS_UFMS_FULL",
    "AN_VANTARIS_IBMS-backend/",
    "database/",
    "migrations/",
)
REGRESSION_COMMANDS = (
    ("Package route enforcement still passes", ["python3", "scripts/validation/validate-one-package-route-enforcement.py"], "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS", {"PYTHONPATH": "AN_VANTARIS_ONE"}),
    ("Boundary baseline still passes", ["python3", "scripts/validation/validate-one-boundaries.py"], "ONE_BOUNDARY_BASELINE_PASS", {"PYTHONPATH": "AN_VANTARIS_ONE"}),
)
ARCHIVED_MARKER_CHECKS = (
    ("UMMS-R11A archived validator marker is present", "ONE_UMMS_R11A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS"),
    ("UMMS-R11 archived validator marker is present", "ONE_UMMS_R11_READONLY_API_ENTRY_SKELETON_PASS"),
    ("UMMS Package / UConsole stakeholder entry local freeze marker is present", "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS"),
    ("UMMS Package / UConsole stakeholder entry readiness marker is present", "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_READINESS_PASS"),
    ("UMMS-R10A archived validator marker is present", "ONE_UMMS_R10A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS"),
    ("UMMS-R10 archived validator marker is present", "ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE_PASS"),
)


def _run(command: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False, env=merged_env)


def _changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        paths.update(line for line in _run(command).stdout.splitlines() if line)
    if _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip() == "feat(one): add umms readonly frontend uconsole card entry":
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _service_get_paths(source: str) -> set[str]:
    return set(re.findall(r"request\.get\('([^']+)'\)", source))


def _marker_exists(marker: str) -> bool:
    result = _run(["git", "grep", "-q", marker])
    return result.returncode == 0


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    service_text = SERVICE.read_text(encoding="utf-8") if SERVICE.exists() else ""
    component_text = COMPONENT.read_text(encoding="utf-8") if COMPONENT.exists() else ""
    routes_text = ROUTES.read_text(encoding="utf-8") if ROUTES.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    combined = "\n".join([service_text, component_text, routes_text, report_text])

    checks.append(("UMMS-R12 report exists", REPORT.is_file()))
    checks.append(("Frontend/UConsole UMMS card or entry exists", COMPONENT.is_file() and EXPECTED_ROUTE in routes_text and "UmmsReadonlyOverview" in routes_text))
    get_paths = _service_get_paths(service_text)
    checks.append(("Frontend service uses only GET UMMS endpoints", all(endpoint in get_paths for endpoint in EXPECTED_ENDPOINTS)))
    checks.append(("No POST / PUT / PATCH / DELETE UMMS API client methods were added", not any(term in service_text for term in FORBIDDEN_CLIENT_TERMS)))
    checks.append(("UMMS package/card entry displays read-only status", "Read-only" in component_text and "readOnly" in service_text))
    checks.append(("UMMS package/card entry displays stakeholder review ready status", "Stakeholder Review Ready" in component_text))
    checks.append(("UMMS package/card entry displays runtime disabled status", "Runtime" in component_text and "Disabled" in component_text))
    checks.append(("UMMS package/card entry references latest R11 tag", "umms-r11-readonly-api-entry-skeleton-local-freeze-20260621" in component_text and "umms-r11-readonly-api-entry-skeleton-local-freeze-20260621" in service_text))
    checks.append(("UMMS card includes customer core function/capability coverage", all(term in component_text or term in service_text for term in CAPABILITY_TERMS)))
    checks.append(("UMMS card includes safety posture", all(term in component_text for term in SAFETY_TERMS)))
    lower_component = component_text.lower()
    checks.append(("UMMS card has no write/approval/activation/deployment/runtime action buttons", not any(term in lower_component for term in FORBIDDEN_ACTION_TERMS)))
    checks.append(("Fallback behavior is read-only and safe", "UMMS readiness data unavailable, read-only fallback active." in service_text and "fallbackActive" in component_text))
    changed = _changed_paths()
    checks.append(("No DB migration added", not any(path.startswith("database/") or path.startswith("migrations/") for path in changed)))
    checks.append(("No DB write path added", not any(term in combined for term in FORBIDDEN_WRITE_TERMS)))
    checks.append(("No ONE Adapter introduced", "oneAdapterIntroduced" in service_text and "one adapter introduced: yes" not in combined.lower()))
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to UMMS-R12 frontend scope", not disallowed))
    checks.append(("No EDGE/LINK/Contracts/UFMS files modified", not forbidden and not any("VANTARIS_UFMS_FULL" in path for path in changed)))
    if disallowed:
        errors.append(f"changes outside UMMS-R12 scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")
    checks.append(("No customer identifier leakage", "customerAssetIdentifier" not in combined and "customer identifier" not in combined.lower()))
    checks.append(("No local absolute path leakage in stakeholder-facing frontend text", "/Users/" not in component_text and "/Users/" not in report_text and "/Volumes/Work/VANTARIS_UFMS_FULL" not in combined))

    frontend_smoke = _run(["npm", "run", "type-check", "--prefix", "AN_VANTARIS_IBMS-frontend"])
    checks.append(("Frontend type-check smoke passes", frontend_smoke.returncode == 0))
    if frontend_smoke.returncode != 0:
        errors.append(frontend_smoke.stdout[-4000:] or frontend_smoke.stderr[-4000:] or "frontend type-check failed")

    for label, marker in ARCHIVED_MARKER_CHECKS:
        checks.append((label, _marker_exists(marker)))

    for label, command, marker, env in REGRESSION_COMMANDS:
        print(f"[RUN] {label}", flush=True)
        result = _run(command, env=env)
        passed = result.returncode == 0 and marker in result.stdout
        checks.append((label, passed))
        if not passed:
            errors.append(result.stdout[-3000:] or result.stderr[-3000:] or f"{label} failed")

    print("ONE_UMMS_R12_READONLY_FRONTEND_UCONSOLE_CARD_ENTRY_VALIDATION")
    failed = False
    for label, passed in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {label}")
        failed = failed or not passed
    if errors:
        print("\nErrors:")
        for error in errors:
            print(error)
        failed = True
    if failed:
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
