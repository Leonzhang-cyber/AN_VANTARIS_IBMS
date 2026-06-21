#!/usr/bin/env python3
"""Validate UMMS-R12A local freeze + optional tag plan."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FREEZE_DOC = ROOT / "ONE_UMMS_R12A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-r12a-local-freeze.v1.json"
REPORT = ROOT / "ONE_UMMS_R12A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md"
SERVICE = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/umms.ts"
COMPONENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/umms/UmmsReadonlyOverview.vue"
ROUTES = ROOT / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts"
BASE_COMMIT = "72f057b3db4882af73c901d0c81d362477f10885"
PASS_MARKER = "ONE_UMMS_R12A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS"

EXPECTED_ROUTE = "/one/umms/overview"
EXPECTED_COMPONENT = "UmmsReadonlyOverview"
EXPECTED_ENDPOINTS = (
    "/v1/one/umms/package-entry",
    "/v1/one/umms/stakeholder-review",
    "/v1/one/umms/readiness-summary",
    "/v1/one/umms/customer-core-functions",
    "/v1/one/umms/safety-posture",
)
EXPECTED_ENDPOINTS_DOC = tuple(f"GET `/api{path}`" for path in EXPECTED_ENDPOINTS)
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
FORBIDDEN_RUNTIME_TERMS = (
    "<el-button",
    "approval execution enabled",
    "workflow execution enabled",
    "runtime activation enabled",
    "production activation enabled",
    "db write enabled",
    "one adapter introduced: yes",
)
SAFETY_FLAGS = (
    "readOnly",
    "getOnly",
    "productionActivation",
    "runtimeActivation",
    "dbWrite",
    "approvalExecution",
    "workflowExecution",
    "writeActionsEnabled",
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
    "customerIdentifierLeakage",
    "localAbsolutePathLeakage",
)
CHAIN_MARKERS = (
    "ONE_UMMS_R2_WORK_ORDER_ASSET_PM_DOMAIN_ALIGNMENT_PASS",
    "ONE_UMMS_R2A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R3_MANUAL_WORK_ORDER_READONLY_QUEUE_DRAFT_MODEL_PASS",
    "ONE_UMMS_R3A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R4_WORK_ORDER_LIFECYCLE_STATE_VALIDATION_GATE_PASS",
    "ONE_UMMS_R4A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R5_PREVENTIVE_MAINTENANCE_SCHEDULE_READINESS_PASS",
    "ONE_UMMS_R5A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R6_SPARE_PARTS_INVENTORY_READINESS_PASS",
    "ONE_UMMS_R6A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R7_VENDOR_CONTRACT_SLA_READINESS_PASS",
    "ONE_UMMS_R7A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R8_UCDE_EVIDENCE_CLOSURE_ALIGNMENT_PASS",
    "ONE_UMMS_R8A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R9_AIRPORT_HMI_LOCATOR_BINDING_READINESS_PASS",
    "ONE_UMMS_R9A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE_PASS",
    "ONE_UMMS_R10A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_READINESS_PASS",
    "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R11_READONLY_API_ENTRY_SKELETON_PASS",
    "ONE_UMMS_R11A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R12_READONLY_FRONTEND_UCONSOLE_CARD_ENTRY_PASS",
)
ALLOWED_CHANGED_PREFIXES = (
    "ONE_UMMS_R12A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN.md",
    "AN_VANTARIS_ONE/registries/umms-r12a-local-freeze.v1.json",
    "ONE_UMMS_R12A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md",
    "scripts/validation/validate-one-umms-r12a-local-freeze.py",
)
FORBIDDEN_CHANGED_PREFIXES = (
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_LINK/",
    "AN_VANTARIS_Contracts/",
    "/Volumes/Work/VANTARIS_UFMS_FULL",
    "AN_VANTARIS_IBMS-backend/",
    "AN_VANTARIS_IBMS-frontend/",
    "database/",
    "migrations/",
)
REGRESSION_COMMANDS = (
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
    if _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip() == "docs(one): freeze umms r12 read-only frontend uconsole entry":
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

    freeze_text = FREEZE_DOC.read_text(encoding="utf-8") if FREEZE_DOC.exists() else ""
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    service_text = SERVICE.read_text(encoding="utf-8") if SERVICE.exists() else ""
    component_text = COMPONENT.read_text(encoding="utf-8") if COMPONENT.exists() else ""
    routes_text = ROUTES.read_text(encoding="utf-8") if ROUTES.exists() else ""
    combined = "\n".join([freeze_text, registry_text, report_text, service_text, component_text, routes_text])
    lower_combined = combined.lower()

    checks.append(("Freeze document exists", FREEZE_DOC.is_file()))
    checks.append(("Freeze registry exists", REGISTRY.is_file()))
    checks.append(("Freeze report exists", REPORT.is_file()))
    checks.append(("Baseline commit reference is present", all(BASE_COMMIT in text for text in (freeze_text, registry_text, report_text))))

    try:
        registry = json.loads(registry_text)
    except Exception as exc:
        registry = {}
        errors.append(f"registry json invalid: {exc}")

    checks.append(("R12 UI exists", COMPONENT.is_file() and EXPECTED_ROUTE in routes_text and EXPECTED_COMPONENT in routes_text))
    get_paths = _service_get_paths(service_text)
    checks.append(("R12 API usage is GET-only", all(path in get_paths for path in EXPECTED_ENDPOINTS)))
    checks.append(("No POST / PUT / PATCH / DELETE UMMS endpoints used", not any(term in service_text for term in FORBIDDEN_CLIENT_TERMS)))
    checks.append(("API dependency list includes 5 GET endpoints", all(endpoint in freeze_text and endpoint in report_text for endpoint in EXPECTED_ENDPOINTS_DOC)))
    checks.append(("UI behavior is read-only only", "Read-only" in component_text and not any(term in component_text.lower() for term in FORBIDDEN_RUNTIME_TERMS)))

    safety = registry.get("safetyFlags", {})
    checks.append((
        "Safety matrix correctness",
        all(flag in safety for flag in SAFETY_FLAGS)
        and safety.get("readOnly") is True
        and safety.get("getOnly") is True
        and all(safety.get(flag) is False for flag in SAFETY_FLAGS if flag not in {"readOnly", "getOnly"})
    ))
    checks.append(("No runtime flags enabled", not any(term in lower_combined for term in FORBIDDEN_RUNTIME_TERMS)))
    checks.append(("No DB write", safety.get("dbWrite") is False and "This is not DB write enablement." in freeze_text))
    checks.append(("No workflow execution", safety.get("workflowExecution") is False and "This is not workflow execution." in freeze_text))
    checks.append(("No ONE Adapter", safety.get("oneAdapterIntroduced") is False and "one adapter introduced: yes" not in lower_combined))
    checks.append(("No tag/push claims", registry.get("tagCreated") is False and registry.get("pushPerformed") is False and "tag created: yes" not in lower_combined and "push performed: yes" not in lower_combined))
    checks.append(("Optional tag plan is not executed", registry.get("optionalTagPlan", {}).get("commandsExecuted") is False and "Not executed." in freeze_text))

    registry_chain = set(registry.get("dependencyChainR2ToR12", []))
    missing_chain = [marker for marker in CHAIN_MARKERS if marker not in registry_chain or not _marker_exists(marker)]
    checks.append(("R2–R12 chain intact", not missing_chain))
    if missing_chain:
        errors.append(f"missing R2-R12 markers: {', '.join(missing_chain)}")

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to UMMS-R12A freeze scope", not disallowed))
    checks.append(("No EDGE/LINK/Contracts/UFMS files modified", not forbidden and not any("VANTARIS_UFMS_FULL" in path for path in changed)))
    if disallowed:
        errors.append(f"changes outside UMMS-R12A freeze scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    checks.append(("No local absolute path leakage in freeze artifacts", "/Users/" not in freeze_text and "/Users/" not in registry_text and "/Users/" not in report_text and "/Volumes/Work/VANTARIS_UFMS_FULL" not in combined))
    checks.append(("No customer identifier leakage", "customerAssetIdentifier" not in combined and "customer identifier" not in lower_combined))

    for label, command, marker, env in REGRESSION_COMMANDS:
        print(f"[RUN] {label}", flush=True)
        result = _run(command, env=env)
        passed = result.returncode == 0 and marker in result.stdout
        checks.append((label, passed))
        if not passed:
            errors.append(result.stdout[-3000:] or result.stderr[-3000:] or f"{label} failed")

    print("ONE_UMMS_R12A_LOCAL_FREEZE_VALIDATION")
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
