#!/usr/bin/env python3
"""Validate UMMS package / UConsole stakeholder entry readiness."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-package-uconsole-stakeholder-entry-readiness.v1.json"
REPORT = ROOT / "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_READINESS_REPORT.md"
AIRPORT_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts"
PASS_MARKER = "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_READINESS_PASS"

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
    "AN_VANTARIS_ONE/registries/umms-package-uconsole-stakeholder-entry-readiness.v1.json",
    "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_READINESS_REPORT.md",
    "scripts/validation/validate-one-umms-package-uconsole-stakeholder-entry-readiness.py",
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
    if _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip() == "docs(one): add umms package uconsole stakeholder entry readiness":
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _json_valid(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except Exception:
        return False


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    combined = "\n".join([registry_text, report_text])

    checks.append(("UMMS package / UConsole stakeholder entry registry exists", REGISTRY.is_file()))
    checks.append(("UMMS package / UConsole stakeholder entry report exists", REPORT.is_file()))
    try:
        registry = json.loads(registry_text)
    except Exception as exc:
        registry = {}
        errors.append(f"registry json invalid: {exc}")
    metadata = registry.get("metadata", {})
    package_entry = registry.get("packageEntry", {})
    reference = registry.get("stakeholderReviewPackageReference", {})
    chain = registry.get("ummsReadinessChainReference", [])
    uconsole = registry.get("uconsoleEntryReadiness", {})
    card = registry.get("uconsoleCardModel", {})
    coverage = registry.get("customerCoreFunctionCoverage", [])
    safety = registry.get("safetyPosture", {})

    checks.append(("Registry metadata contains platform = VANTARIS ONE", metadata.get("platform") == "VANTARIS ONE"))
    checks.append(("Registry metadata contains module = UMMS", metadata.get("module") == "UMMS"))
    checks.append(("Registry metadata confirms readOnly = true", metadata.get("readOnly") is True))
    checks.append(("Registry metadata confirms runtimeActivation = false", metadata.get("runtimeActivation") is False))
    checks.append(("Registry metadata confirms productionActivation = false", metadata.get("productionActivation") is False))
    checks.append(("Registry metadata confirms dbWrite = false", metadata.get("dbWrite") is False))
    checks.append(("Registry metadata confirms approvalExecution = false", metadata.get("approvalExecution") is False))
    checks.append(("Registry metadata confirms workflowExecution = false", metadata.get("workflowExecution") is False))
    runtime_flags = ("workOrderRuntimeExecution", "pmExecution", "inventoryTransaction", "vendorContractSlaRuntime", "evidenceClosureExecution", "hmiRuntimeExecution")
    checks.append(("Registry metadata confirms no work order / PM / inventory / vendor / evidence / HMI runtime", all(metadata.get(flag) is False for flag in runtime_flags)))
    checks.append(("packageEntry exists", bool(package_entry)))
    checks.append(("packageEntry packageId = umms", package_entry.get("packageId") == "umms"))
    checks.append(("packageEntry packageStatus = stakeholder_review_ready", package_entry.get("packageStatus") == "stakeholder_review_ready"))
    checks.append(("packageEntry runtimeEnabled = false", package_entry.get("runtimeEnabled") is False))
    checks.append(("packageEntry activationEnabled = false", package_entry.get("activationEnabled") is False))
    checks.append(("packageEntry workflowEnabled = false", package_entry.get("workflowEnabled") is False))
    checks.append(("packageEntry approvalEnabled = false", package_entry.get("approvalEnabled") is False))
    checks.append(("stakeholderReviewPackageReference references UMMS-R10 package/report/registry", reference.get("packageDocument") == "ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE.md" and reference.get("packageReport") == "ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE_REPORT.md" and reference.get("packageRegistry") == "AN_VANTARIS_ONE/registries/umms-stakeholder-review-package.v1.json"))
    checks.append(("stakeholderReviewPackageReference references R10 tag", reference.get("publishedTag") == "umms-r10-stakeholder-review-package-local-freeze-20260621"))
    stages = {item.get("stage") for item in chain}
    checks.append(("ummsReadinessChainReference includes UMMS-R2 through UMMS-R10", all(f"UMMS-R{i}" in stages for i in range(2, 11))))
    checks.append(("uconsoleEntryReadiness exists", bool(uconsole)))
    checks.append(("uconsoleEntryReadiness entryVisibility = visible", uconsole.get("entryVisibility") == "visible"))
    checks.append(("uconsoleEntryReadiness entryPermissions = read_only", uconsole.get("entryPermissions") == "read_only"))
    checks.append(("uconsoleEntryReadiness runtimeActionsVisible = false", uconsole.get("runtimeActionsVisible") is False))
    checks.append(("uconsoleEntryReadiness approvalActionsVisible = false", uconsole.get("approvalActionsVisible") is False))
    checks.append(("uconsoleEntryReadiness activationActionsVisible = false", uconsole.get("activationActionsVisible") is False))
    checks.append(("uconsoleEntryReadiness writeActionsVisible = false", uconsole.get("writeActionsVisible") is False))
    checks.append(("uconsoleEntryReadiness deploymentActionsVisible = false", uconsole.get("deploymentActionsVisible") is False))
    checks.append(("uconsoleCardModel exists and is read-only", bool(card) and card.get("readOnly") is True))
    functions = {item.get("function") for item in coverage}
    checks.append(("customerCoreFunctionCoverage includes all 10 required functions", all(function in functions for function in CUSTOMER_FUNCTIONS)))
    checks.append(("All customerCoreFunctionCoverage runtimeEnabled values are false", all(item.get("runtimeEnabled") is False for item in coverage) and len(coverage) >= 10))
    checks.append(("safetyPosture includes all required flags", all(flag in safety for flag in SAFETY_FLAGS) and safety.get("readOnly") is True and all(safety.get(flag) is False for flag in SAFETY_FLAGS if flag != "readOnly")))
    checks.append(("No ONE Adapter introduced", metadata.get("oneAdapterIntroduced") is False and safety.get("oneAdapterIntroduced") is False and "one adapter introduced: yes" not in combined.lower()))
    checks.append(("No customer ID leakage", "customerAssetIdentifier" not in combined))
    checks.append(("No local absolute path leakage in stakeholder-facing output", "/Users/" not in report_text and "/Users/" not in registry_text and "/Volumes/Work/VANTARIS_UFMS_FULL" not in combined))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to UMMS package / UConsole readiness scope", not disallowed))
    checks.append(("No EDGE/LINK/Contracts/UFMS files modified", not forbidden and not any("VANTARIS_UFMS_FULL" in path for path in changed)))
    if disallowed:
        errors.append(f"changes outside UMMS package/UConsole readiness scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    airport_client_text = AIRPORT_CLIENT.read_text(encoding="utf-8") if AIRPORT_CLIENT.exists() else ""
    checks.append(("No POST/PUT/PATCH/DELETE Airport, UMMS, UCDE, or HMI API client methods added", not any(method in airport_client_text for method in FORBIDDEN_CLIENT_METHODS)))

    for label, command, marker, env in REGRESSION_COMMANDS:
        print(f"[RUN] {label}", flush=True)
        result = _run(command, env=env)
        passed = result.returncode == 0 and marker in result.stdout
        checks.append((label, passed))
        if not passed:
            errors.append(result.stdout[-3000:] or result.stderr[-3000:] or f"{label} failed")

    checks.append(("Registry JSON validation passes", _json_valid(REGISTRY)))

    print("ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_READINESS_VALIDATION")
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
