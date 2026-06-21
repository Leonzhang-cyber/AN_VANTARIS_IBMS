#!/usr/bin/env python3
"""Validate UMMS-R11 read-only API entry skeleton."""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
API_MODULE = ROOT / "AN_VANTARIS_IBMS-backend/src/api/umms/umms_api.py"
PROVIDER = ROOT / "AN_VANTARIS_IBMS-backend/src/umms/umms_provider.py"
SERVICE = ROOT / "AN_VANTARIS_IBMS-backend/src/umms/umms_service.py"
REPORT = ROOT / "ONE_UMMS_R11_READONLY_API_ENTRY_SKELETON_REPORT.md"
TEST_DIR = ROOT / "AN_VANTARIS_ONE/tests/umms_r11_readonly_api"
BACKEND_PYTHON = ROOT / "AN_VANTARIS_IBMS-backend/.venv/bin/python"
PACKAGE_ENTRY_REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-package-uconsole-stakeholder-entry-readiness.v1.json"
PASS_MARKER = "ONE_UMMS_R11_READONLY_API_ENTRY_SKELETON_PASS"

EXPECTED_ENDPOINTS = {
    "/v1/one/umms/package-entry",
    "/v1/one/umms/stakeholder-review",
    "/v1/one/umms/readiness-summary",
    "/v1/one/umms/customer-core-functions",
    "/v1/one/umms/safety-posture",
}
CUSTOMER_FUNCTIONS = (
    "Work Order Management, auto + manual",
    "Asset Registry, full lifecycle tracking",
    "Preventive Maintenance Scheduler",
    "Spare Parts / Inventory Management",
    "Vendor / Contract Management",
    "Graphics HMI to locate Equipment",
    "Existing system onboarding",
    "Engineer commissioning diagnostics",
    "Remote overseas deployment",
    "Distributed independent installation",
)
COMMON_GUARD_TERMS = (
    '"readOnly": True',
    '"runtimeEnabled": False',
    '"productionEnabled": False',
    '"dbWriteEnabled": False',
    '"workflowEnabled": False',
    '"approvalEnabled": False',
    '"writeActionsEnabled": False',
    '"edgeRuntimeCall": False',
    '"linkRuntimeCall": False',
    '"oneAdapterIntroduced": False',
)
SAFETY_FALSE_FLAGS = (
    "productionActivation",
    "runtimeActivation",
    "dbWrite",
    "approvalExecution",
    "workflowExecution",
    "workOrderRuntimeExecution",
    "pmExecution",
    "inventoryTransaction",
    "vendorContractSlaRuntime",
    "evidenceClosureExecution",
    "hmiRuntimeExecution",
    "deviceConnection",
    "connectorExecution",
    "edgeRuntimeCall",
    "linkRuntimeCall",
    "oneAdapterIntroduced",
)
ALLOWED_CHANGED_PREFIXES = (
    "AN_VANTARIS_IBMS-backend/src/api/umms/umms_api.py",
    "AN_VANTARIS_IBMS-backend/src/umms/umms_provider.py",
    "AN_VANTARIS_IBMS-backend/src/umms/umms_service.py",
    "AN_VANTARIS_ONE/tests/umms_r11_readonly_api/",
    "scripts/validation/validate-one-umms-r11-readonly-api-entry-skeleton.py",
    "ONE_UMMS_R11_READONLY_API_ENTRY_SKELETON_REPORT.md",
)
FORBIDDEN_CHANGED_PREFIXES = (
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_LINK/",
    "AN_VANTARIS_Contracts/",
    "/Volumes/Work/VANTARIS_UFMS_FULL",
    "AN_VANTARIS_IBMS-frontend/",
    "database/",
    "migrations/",
)
FORBIDDEN_WRITE_TERMS = (
    ".session.add",
    ".session.commit",
    ".save(",
    ".delete(",
    "INSERT ",
    "UPDATE ",
    "DELETE ",
    "requests.",
    "urllib.",
    "socket.",
)
REGRESSION_COMMANDS = (
    ("UMMS package / UConsole stakeholder entry local freeze validator still passes", ["python3", "scripts/validation/validate-one-umms-package-uconsole-stakeholder-entry-local-freeze.py"], "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS", None),
    ("UMMS package / UConsole stakeholder entry readiness validator still passes", ["python3", "scripts/validation/validate-one-umms-package-uconsole-stakeholder-entry-readiness.py"], "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_READINESS_PASS", None),
    ("UMMS-R10A validator still passes", ["python3", "scripts/validation/validate-one-umms-r10a-local-freeze.py"], "ONE_UMMS_R10A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS", None),
    ("UMMS-R10 validator still passes", ["python3", "scripts/validation/validate-one-umms-r10-stakeholder-review-package.py"], "ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE_PASS", None),
    ("Package route enforcement still passes", ["python3", "scripts/validation/validate-one-package-route-enforcement.py"], "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS", {"PYTHONPATH": "AN_VANTARIS_ONE"}),
    ("Boundary baseline still passes", ["python3", "scripts/validation/validate-one-boundaries.py"], "ONE_BOUNDARY_BASELINE_PASS", {"PYTHONPATH": "AN_VANTARIS_ONE"}),
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
    if _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip() == "feat(one): add umms readonly api entry skeleton":
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _route_methods(source: str) -> dict[str, set[str]]:
    route_methods: dict[str, set[str]] = {}
    pattern = re.compile(r'@api_bp\.route\("([^"]+)",\s*methods=\[([^\]]+)\]\)')
    for route, methods_expr in pattern.findall(source):
        if route.startswith("/v1/one/umms/"):
            methods = {item.strip().strip('"').strip("'") for item in methods_expr.split(",")}
            route_methods[route] = methods
    return route_methods


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    api_text = API_MODULE.read_text(encoding="utf-8") if API_MODULE.exists() else ""
    provider_text = PROVIDER.read_text(encoding="utf-8") if PROVIDER.exists() else ""
    service_text = SERVICE.read_text(encoding="utf-8") if SERVICE.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    registry_text = PACKAGE_ENTRY_REGISTRY.read_text(encoding="utf-8") if PACKAGE_ENTRY_REGISTRY.exists() else ""
    combined = "\n".join([api_text, provider_text, service_text, report_text])
    implementation_text = "\n".join([api_text, provider_text, service_text])

    checks.append(("UMMS-R11 report exists", REPORT.is_file()))
    checks.append(("GET-only UMMS API route/controller/service exists", API_MODULE.is_file() and PROVIDER.is_file() and SERVICE.is_file()))

    route_methods = _route_methods(api_text)
    checks.append(("Required endpoints are present", set(route_methods) >= EXPECTED_ENDPOINTS and all(f"GET `/api{path}`" in report_text for path in EXPECTED_ENDPOINTS)))
    checks.append(("No POST/PUT/PATCH/DELETE UMMS endpoints were added", all(methods == {"GET"} for route, methods in route_methods.items() if route in EXPECTED_ENDPOINTS) and all(term not in api_text for term in ('methods=["POST"]', 'methods=["PUT"]', 'methods=["PATCH"]', 'methods=["DELETE"]'))))
    checks.append(("API response source is projection/registry-backed", "local_projection_registry" in provider_text and "AN_VANTARIS_ONE/registries/" in provider_text))
    checks.append(("API response includes readOnly = true", '"readOnly": True' in provider_text))
    checks.append(("API response includes runtimeEnabled = false", '"runtimeEnabled": False' in provider_text))
    checks.append(("API response includes dbWriteEnabled = false", '"dbWriteEnabled": False' in provider_text))
    checks.append(("API response includes workflowEnabled = false", '"workflowEnabled": False' in provider_text))
    checks.append(("API response includes approvalEnabled = false", '"approvalEnabled": False' in provider_text))
    checks.append(("API response includes edgeRuntimeCall = false", '"edgeRuntimeCall": False' in provider_text))
    checks.append(("API response includes linkRuntimeCall = false", '"linkRuntimeCall": False' in provider_text))
    checks.append(("API response includes oneAdapterIntroduced = false", '"oneAdapterIntroduced": False' in provider_text))
    checks.append(("Customer core function list includes all 10 functions", all(function in registry_text for function in CUSTOMER_FUNCTIONS)))
    checks.append(("All customer function runtimeEnabled values are false", '"runtimeEnabled": False' in provider_text and "all(item[\"runtimeEnabled\"] is False" in (TEST_DIR / "test_umms_r11_readonly_api.py").read_text(encoding="utf-8")))
    checks.append(("Safety posture contains all required false flags", all(flag in provider_text for flag in SAFETY_FALSE_FLAGS)))
    checks.append(("No DB migration added", not any(path.startswith("AN_VANTARIS_IBMS-backend/migrations/") or path.startswith("migrations/") for path in _changed_paths())))
    checks.append(("No DB write path added", all(term not in implementation_text for term in FORBIDDEN_WRITE_TERMS)))
    checks.append(("No ONE Adapter introduced", "oneAdapterIntroduced" in provider_text and "one adapter introduced: yes" not in combined.lower()))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to UMMS-R11 scope", not disallowed))
    checks.append(("No EDGE/LINK/Contracts/UFMS files modified", not forbidden and not any("VANTARIS_UFMS_FULL" in path for path in changed)))
    if disallowed:
        errors.append(f"changes outside UMMS-R11 scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    checks.append(("No local absolute path leakage in stakeholder-facing report", "/Users/" not in report_text and "/Volumes/Work/VANTARIS_UFMS_FULL" not in combined))
    checks.append(("Focused UMMS-R11 read-only API smoke test exists", TEST_DIR.is_dir()))
    smoke_python = str(BACKEND_PYTHON if BACKEND_PYTHON.exists() else Path(sys.executable))
    smoke = _run([smoke_python, "-m", "unittest", "discover", "-s", "AN_VANTARIS_ONE/tests/umms_r11_readonly_api", "-p", "test_*.py"])
    checks.append(("Focused UMMS-R11 read-only API smoke passes", smoke.returncode == 0))
    if smoke.returncode != 0:
        errors.append(smoke.stdout[-4000:] or smoke.stderr[-4000:] or "focused UMMS-R11 smoke failed")

    for label, command, marker, env in REGRESSION_COMMANDS:
        print(f"[RUN] {label}", flush=True)
        result = _run(command, env=env)
        passed = result.returncode == 0 and marker in result.stdout
        checks.append((label, passed))
        if not passed:
            errors.append(result.stdout[-3000:] or result.stderr[-3000:] or f"{label} failed")

    print("ONE_UMMS_R11_READONLY_API_ENTRY_SKELETON_VALIDATION")
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
