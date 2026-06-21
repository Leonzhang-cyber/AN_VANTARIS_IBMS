#!/usr/bin/env python3
"""Validate UMMS package / UConsole stakeholder entry local freeze."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FREEZE_DOC = ROOT / "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-package-uconsole-stakeholder-entry-local-freeze.v1.json"
REPORT = ROOT / "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md"
AIRPORT_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts"
BASE_COMMIT = "63e8e3bc3c258e0e329fdbb974de9f566fd21037"
READINESS_MARKER = "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_READINESS_PASS"
PASS_MARKER = "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS"

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
SAFETY_FLAGS = (
    "readOnly",
    "productionActivation",
    "runtimeActivation",
    "dbWrite",
    "approvalExecution",
    "workflowExecution",
    "uconsoleWriteBehavior",
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
ALLOWED_CHANGED_PREFIXES = (
    "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN.md",
    "AN_VANTARIS_ONE/registries/umms-package-uconsole-stakeholder-entry-local-freeze.v1.json",
    "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md",
    "scripts/validation/validate-one-umms-package-uconsole-stakeholder-entry-local-freeze.py",
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
FORBIDDEN_CLIENT_METHODS = (".post", ".put", ".patch", ".delete")
REGRESSION_COMMANDS = (
    ("UMMS package / UConsole stakeholder entry validator still passes", ["python3", "scripts/validation/validate-one-umms-package-uconsole-stakeholder-entry-readiness.py"], "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_READINESS_PASS", None),
    ("UMMS-R10A validator still passes", ["python3", "scripts/validation/validate-one-umms-r10a-local-freeze.py"], "ONE_UMMS_R10A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS", None),
    ("UMMS-R10 validator still passes", ["python3", "scripts/validation/validate-one-umms-r10-stakeholder-review-package.py"], "ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE_PASS", None),
    ("UMMS-R9A validator still passes", ["python3", "scripts/validation/validate-one-umms-r9a-local-freeze.py"], "ONE_UMMS_R9A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS", None),
    ("UMMS-R9 validator still passes", ["python3", "scripts/validation/validate-one-umms-r9-airport-hmi-locator-binding-readiness.py"], "ONE_UMMS_R9_AIRPORT_HMI_LOCATOR_BINDING_READINESS_PASS", None),
    ("UMMS-R8A validator still passes", ["python3", "scripts/validation/validate-one-umms-r8a-local-freeze.py"], "ONE_UMMS_R8A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS", None),
    ("UMMS-R8 validator still passes", ["python3", "scripts/validation/validate-one-umms-r8-ucde-evidence-closure-alignment.py"], "ONE_UMMS_R8_UCDE_EVIDENCE_CLOSURE_ALIGNMENT_PASS", None),
    ("UMMS-R7A validator still passes", ["python3", "scripts/validation/validate-one-umms-r7a-local-freeze.py"], "ONE_UMMS_R7A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS", None),
    ("UMMS-R7 validator still passes", ["python3", "scripts/validation/validate-one-umms-r7-vendor-contract-sla-readiness.py"], "ONE_UMMS_R7_VENDOR_CONTRACT_SLA_READINESS_PASS", None),
    ("UMMS-R6A validator still passes", ["python3", "scripts/validation/validate-one-umms-r6a-local-freeze.py"], "ONE_UMMS_R6A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS", None),
    ("UMMS-R6 validator still passes", ["python3", "scripts/validation/validate-one-umms-r6-spare-parts-inventory-readiness.py"], "ONE_UMMS_R6_SPARE_PARTS_INVENTORY_READINESS_PASS", None),
    ("UMMS-R5A validator still passes", ["python3", "scripts/validation/validate-one-umms-r5a-local-freeze.py"], "ONE_UMMS_R5A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS", None),
    ("UMMS-R5 validator still passes", ["python3", "scripts/validation/validate-one-umms-r5-preventive-maintenance-schedule-readiness.py"], "ONE_UMMS_R5_PREVENTIVE_MAINTENANCE_SCHEDULE_READINESS_PASS", None),
    ("UMMS-R4A validator still passes", ["python3", "scripts/validation/validate-one-umms-r4a-local-freeze.py"], "ONE_UMMS_R4A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS", None),
    ("UMMS-R4 validator still passes", ["python3", "scripts/validation/validate-one-umms-r4-work-order-lifecycle-state-validation-gate.py"], "ONE_UMMS_R4_WORK_ORDER_LIFECYCLE_STATE_VALIDATION_GATE_PASS", None),
    ("UMMS-R3A validator still passes", ["python3", "scripts/validation/validate-one-umms-r3a-local-freeze.py"], "ONE_UMMS_R3A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS", None),
    ("UMMS-R3 validator still passes", ["python3", "scripts/validation/validate-one-umms-r3-manual-work-order-readonly-queue-draft-model.py"], "ONE_UMMS_R3_MANUAL_WORK_ORDER_READONLY_QUEUE_DRAFT_MODEL_PASS", None),
    ("UMMS-R2A validator still passes", ["python3", "scripts/validation/validate-one-umms-r2a-local-freeze.py"], "ONE_UMMS_R2A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS", None),
    ("UMMS-R2 validator still passes", ["python3", "scripts/validation/validate-one-umms-r2-work-order-asset-pm-domain-alignment.py"], "ONE_UMMS_R2_WORK_ORDER_ASSET_PM_DOMAIN_ALIGNMENT_PASS", None),
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
    if _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip() == "docs(one): freeze umms package uconsole stakeholder entry readiness":
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _json_valid(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except Exception:
        return False


def _strip_allowed_workspace_path(text: str) -> str:
    return text.replace("/Users/leon/Desktop/AN_VANTARIS_IBMS", "")


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    freeze_text = FREEZE_DOC.read_text(encoding="utf-8") if FREEZE_DOC.exists() else ""
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    combined = "\n".join([freeze_text, registry_text, report_text])
    lower_combined = combined.lower()

    checks.append(("Freeze document exists", FREEZE_DOC.is_file()))
    checks.append(("Freeze registry exists", REGISTRY.is_file()))
    checks.append(("Freeze report exists", REPORT.is_file()))
    checks.append(("Current commit reference is present", BASE_COMMIT in freeze_text and BASE_COMMIT in registry_text and BASE_COMMIT in report_text))
    checks.append(("Readiness PASS marker is referenced", READINESS_MARKER in combined))
    checks.append(("Freeze scope includes UMMS package registry metadata", "UMMS package registry metadata" in freeze_text and "UMMS package registry metadata" in registry_text))
    checks.append(("Freeze scope includes UConsole stakeholder entry readiness metadata", "UMMS UConsole stakeholder entry readiness metadata" in freeze_text and "UMMS UConsole stakeholder entry readiness metadata" in registry_text))
    checks.append(("Freeze scope includes stakeholder review package reference", "UMMS stakeholder review package reference" in freeze_text and "UMMS stakeholder review package reference" in registry_text))
    checks.append(("Freeze scope includes UMMS-R2 through UMMS-R10 readiness chain reference", "UMMS-R2 through UMMS-R10 readiness chain reference" in freeze_text and "UMMS-R2 through UMMS-R10 readiness chain reference" in registry_text))
    checks.append(("Package / UConsole entry summary states entry is metadata-backed and read-only", "metadata-backed and read-only" in freeze_text and '"metadataBacked": true' in registry_text and '"readOnly": true' in registry_text))
    checks.append(("Package / UConsole entry summary states runtime/approval/activation/write/deployment actions are hidden or disabled", all(term in freeze_text for term in ("Runtime actions are hidden/disabled", "Approval actions are hidden/disabled", "Activation actions are hidden/disabled", "Write actions are hidden/disabled", "Deployment actions are hidden/disabled"))))
    checks.append(("Customer core function coverage includes all 10 functions", all(function in freeze_text and function in registry_text for function in CUSTOMER_FUNCTIONS)))

    try:
        registry_data = json.loads(registry_text)
    except Exception as exc:
        registry_data = {}
        errors.append(f"registry json invalid: {exc}")
    coverage = registry_data.get("customerCoreFunctionCoverage", [])
    safety = registry_data.get("safetyMatrix", {})
    optional_tag_plan = registry_data.get("optionalTagPlan", {})

    checks.append(("All customer core function runtimeEnabled values are false", len(coverage) >= 10 and all(item.get("runtimeEnabled") is False for item in coverage)))
    checks.append(("Safety freeze matrix contains all required flags", all(flag in safety for flag in SAFETY_FLAGS) and safety.get("readOnly") is True and all(safety.get(flag) is False for flag in SAFETY_FLAGS if flag != "readOnly")))
    checks.append(("Optional tag plan is documented as not executed", "Suggested commands for future use only, not executed" in freeze_text and "Tag created: no" in freeze_text and "Push performed: no" in freeze_text and optional_tag_plan.get("commandsExecuted") is False))
    checks.append(("No claim that push was performed", "push performed: yes" not in lower_combined and '"pushPerformed": false' in registry_text))
    checks.append(("No claim that tag was created", "tag created: yes" not in lower_combined and '"tagCreated": false' in registry_text))
    checks.append(("No production activation claim", "This is not production activation." in freeze_text and "production activation enabled" not in lower_combined))
    checks.append(("No runtime activation claim", "This is not runtime activation." in freeze_text and "runtime activation enabled" not in lower_combined))
    checks.append(("No DB write claim", "This is not DB write enablement." in freeze_text and "db write enabled" not in lower_combined))
    checks.append(("No approval execution claim", "This is not approval execution." in freeze_text and "approval execution enabled" not in lower_combined))
    checks.append(("No workflow execution claim", "This is not workflow execution." in freeze_text and "workflow execution enabled" not in lower_combined))
    checks.append(("No UConsole write behavior claim", "This is not UConsole write behavior." in freeze_text and "uconsole write behavior enabled" not in lower_combined))
    runtime_phrases = (
        "This is not work order runtime execution.",
        "This is not PM execution.",
        "This is not inventory transaction.",
        "This is not vendor / contract / SLA runtime.",
        "This is not evidence upload or closure execution.",
        "This is not HMI runtime.",
    )
    checks.append(("No work order/PM/inventory/vendor/evidence/HMI runtime claim", all(phrase in freeze_text for phrase in runtime_phrases) and not any(term in lower_combined for term in ("work order runtime execution enabled", "pm execution enabled", "inventory transaction enabled", "vendor / contract / sla runtime enabled", "evidence closure execution enabled", "hmi runtime enabled"))))
    checks.append(("No EDGE/LINK runtime integration claim", "This is not EDGE/LINK runtime integration." in freeze_text and "edge/link runtime integration enabled" not in lower_combined))
    checks.append(("No ONE Adapter introduction", safety.get("oneAdapterIntroduced") is False and "one adapter introduced: yes" not in lower_combined))
    checks.append(("No customer identifier leakage", "customerAssetIdentifier" not in combined and "customer identifier" not in lower_combined))
    no_local_path_leak = "/Users/" not in _strip_allowed_workspace_path(freeze_text) and "/Users/" not in _strip_allowed_workspace_path(report_text) and "/Users/" not in registry_text
    checks.append(("No local absolute path leakage except internal workspace baseline", no_local_path_leak and "/Volumes/Work/VANTARIS_UFMS_FULL" not in combined))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to UMMS package / UConsole local freeze scope", not disallowed))
    checks.append(("No EDGE/LINK/Contracts/UFMS files modified", not forbidden and not any("VANTARIS_UFMS_FULL" in path for path in changed)))
    if disallowed:
        errors.append(f"changes outside UMMS package/UConsole local freeze scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    airport_client_text = AIRPORT_CLIENT.read_text(encoding="utf-8") if AIRPORT_CLIENT.exists() else ""
    checks.append(("No POST/PUT/PATCH/DELETE Airport, UMMS, UCDE, or HMI API client methods added", not any(method in airport_client_text for method in FORBIDDEN_CLIENT_METHODS)))
    checks.append(("Registry JSON validation passes", _json_valid(REGISTRY)))

    for label, command, marker, env in REGRESSION_COMMANDS:
        print(f"[RUN] {label}", flush=True)
        result = _run(command, env=env)
        passed = result.returncode == 0 and marker in result.stdout
        checks.append((label, passed))
        if not passed:
            errors.append(result.stdout[-3000:] or result.stderr[-3000:] or f"{label} failed")

    print("ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_LOCAL_FREEZE_VALIDATION")
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

