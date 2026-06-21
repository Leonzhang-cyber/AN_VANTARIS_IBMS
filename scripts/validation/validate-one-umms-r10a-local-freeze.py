#!/usr/bin/env python3
"""Validate UMMS-R10A local freeze and optional tag plan."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FREEZE_DOC = ROOT / "ONE_UMMS_R10A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-r10a-local-freeze.v1.json"
REPORT = ROOT / "ONE_UMMS_R10A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md"
AIRPORT_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts"
PASS_MARKER = "ONE_UMMS_R10A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS"
UMMS_R10_COMMIT = "aa0142189e497661112aafd98a3f7f0c4bdc9466"
UMMS_R10_MARKER = "ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE_PASS"

MILESTONES = tuple(f"UMMS-R{i}" for i in range(2, 11))
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
SAFETY_TERMS = (
    "readOnly | true",
    "productionActivation | false",
    "runtimeActivation | false",
    "dbWrite | false",
    "approvalExecution | false",
    "workflowExecution | false",
    "workOrderRuntimeExecution | false",
    "pmExecution | false",
    "inventoryTransaction | false",
    "vendorContractSlaRuntime | false",
    "evidenceClosureExecution | false",
    "hmiRuntimeExecution | false",
    "deviceConnection | false",
    "connectorExecution | false",
    "edgeRuntimeCall | false",
    "linkRuntimeCall | false",
    "oneAdapterIntroduced | false",
    "customerIdentifierLeakage | false",
    "localAbsolutePathLeakage | false",
)
ALLOWED_CHANGED_PREFIXES = (
    "ONE_UMMS_R10A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN.md",
    "AN_VANTARIS_ONE/registries/umms-r10a-local-freeze.v1.json",
    "ONE_UMMS_R10A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md",
    "scripts/validation/validate-one-umms-r10a-local-freeze.py",
    "AN_VANTARIS_ONE/tests/",
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
    if _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip() == "docs(one): freeze umms stakeholder review package":
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _workspace_path_only_in_baseline(text: str) -> bool:
    allowed = "`/Users/leon/Desktop/AN_VANTARIS_IBMS`"
    return "/Users/" not in text.replace(allowed, "")


def _json_valid(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except Exception:
        return False


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    freeze_text = FREEZE_DOC.read_text(encoding="utf-8") if FREEZE_DOC.exists() else ""
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    combined = "\n".join([freeze_text, registry_text, report_text])
    lower_combined = combined.lower()

    checks.append(("UMMS-R10A freeze document exists", FREEZE_DOC.is_file()))
    checks.append(("Optional registry exists", REGISTRY.is_file()))
    checks.append(("UMMS-R10A report exists", REPORT.is_file()))
    checks.append(("UMMS-R10 commit reference is present", UMMS_R10_COMMIT in freeze_text and UMMS_R10_COMMIT in registry_text and UMMS_R10_COMMIT in report_text))
    checks.append(("UMMS-R10 PASS marker is referenced", UMMS_R10_MARKER in combined))
    checks.append(("Freeze scope includes UMMS-R2 through UMMS-R10", all(milestone in freeze_text for milestone in MILESTONES)))
    checks.append(("UMMS readiness chain summary includes UMMS-R2 through UMMS-R10", all(f"| {milestone} |" in freeze_text for milestone in MILESTONES)))
    checks.append(("Customer core function coverage matrix includes all 10 customer functions", all(function in freeze_text for function in CUSTOMER_FUNCTIONS)))
    checks.append(("Safety freeze matrix contains all required flags", all(term in freeze_text for term in SAFETY_TERMS)))
    checks.append(("Optional tag plan is documented as not executed", "Suggested commands for future use only, not executed" in freeze_text and "Tag created: no" in freeze_text and "Push performed: no" in freeze_text))
    checks.append(("No claim that push was performed", "push performed: yes" not in lower_combined and "Push performed: no" in freeze_text and "Push performed: no" in report_text))
    checks.append(("No claim that tag was created", "tag created: yes" not in lower_combined and "Tag created: no" in freeze_text and "Tag created: no" in report_text))
    checks.append(("No production activation claim", "This is not production activation." in freeze_text and "production activation enabled" not in lower_combined))
    checks.append(("No runtime activation claim", "This is not runtime activation." in freeze_text and "runtime activation enabled" not in lower_combined))
    checks.append(("No DB write claim", "This is not DB write enablement." in freeze_text and "db write enabled" not in lower_combined))
    checks.append(("No approval execution claim", "This is not approval execution." in freeze_text and "approval execution enabled" not in lower_combined))
    checks.append(("No workflow execution claim", "This is not workflow execution." in freeze_text and "workflow execution enabled" not in lower_combined))
    checks.append(("No work order runtime execution claim", "This is not real work order execution." in freeze_text and "work order runtime execution enabled" not in lower_combined))
    checks.append(("No PM execution claim", "This is not real PM execution." in freeze_text and "pm execution enabled" not in lower_combined))
    checks.append(("No inventory transaction claim", "This is not inventory transaction." in freeze_text and "inventory transaction enabled" not in lower_combined))
    checks.append(("No vendor / contract / SLA runtime claim", "This is not vendor / contract / SLA runtime." in freeze_text and "vendor / contract / sla runtime enabled" not in lower_combined))
    checks.append(("No evidence closure execution claim", "This is not evidence upload / closure execution." in freeze_text and "evidence closure execution enabled" not in lower_combined))
    checks.append(("No HMI runtime claim", "This is not HMI runtime." in freeze_text and "hmi runtime enabled" not in lower_combined))
    checks.append(("No EDGE/LINK runtime integration claim", "This is not EDGE/LINK runtime integration." in freeze_text and "edge/link runtime integration enabled" not in lower_combined))
    checks.append(("No ONE Adapter introduction", "oneAdapterIntroduced | false" in freeze_text and "one adapter introduced: yes" not in lower_combined))
    checks.append(("No customer identifier leakage", "customerAssetIdentifier" not in combined and "customer identifier" not in lower_combined))
    checks.append(("No local absolute path leakage except baseline workspace", _workspace_path_only_in_baseline(freeze_text) and "/Users/" not in report_text and "/Users/" not in registry_text))
    checks.append(("UMMS-R10A PASS marker present", PASS_MARKER in combined))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to UMMS-R10A freeze scope", not disallowed))
    checks.append(("No EDGE/LINK/Contracts/UFMS files modified", not forbidden and not any("VANTARIS_UFMS_FULL" in path for path in changed)))
    if disallowed:
        errors.append(f"changes outside UMMS-R10A scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    airport_client_text = AIRPORT_CLIENT.read_text(encoding="utf-8") if AIRPORT_CLIENT.exists() else ""
    checks.append(("No POST/PUT/PATCH/DELETE Airport, UMMS, UCDE, or HMI API client methods added", not any(method in airport_client_text for method in FORBIDDEN_CLIENT_METHODS)))

    try:
        registry_data = json.loads(registry_text)
    except Exception as exc:
        registry_data = {}
        errors.append(f"registry json invalid: {exc}")
    safety = registry_data.get("safetyMatrix", {})
    checks.append(("Registry freeze id present", registry_data.get("releaseFreezeId") == "umms-r10a-local-freeze-20260621"))
    checks.append(("Registry tag and push false", registry_data.get("pushPerformed") is False and registry_data.get("tagCreated") is False and registry_data.get("optionalTagPlan", {}).get("commandsExecuted") is False))
    checks.append(("Registry safety matrix frozen", safety.get("readOnly") is True and safety.get("dbWrite") is False and safety.get("oneAdapterIntroduced") is False and safety.get("hmiRuntimeExecution") is False))
    checks.append(("Registry JSON validation passes if registry is created", _json_valid(REGISTRY)))

    for label, command, marker, env in REGRESSION_COMMANDS:
        result = _run(command, env=env)
        passed = result.returncode == 0 and marker in result.stdout
        checks.append((label, passed))
        if not passed:
            errors.append(result.stdout[-3000:] or result.stderr[-3000:] or f"{label} failed")

    print("ONE_UMMS_R10A_LOCAL_FREEZE_VALIDATION")
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
