#!/usr/bin/env python3
"""Validate UMMS-R6A local freeze and optional tag plan."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FREEZE_DOC = ROOT / "ONE_UMMS_R6A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-r6a-local-freeze.v1.json"
REPORT = ROOT / "ONE_UMMS_R6A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md"
UMMS_R6_PROJECTION = ROOT / "AN_VANTARIS_ONE/projections/umms-spare-parts-inventory-readiness.v1.json"
UMMS_R6_REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-spare-parts-inventory-readiness-registry.v1.json"
AIRPORT_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts"
PASS_MARKER = "ONE_UMMS_R6A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS"

UMMS_R6_COMMIT = "6a6520208604569f6d558b18a38d8edf060cd23e"
UMMS_R6_MARKER = "ONE_UMMS_R6_SPARE_PARTS_INVENTORY_READINESS_PASS"
FREEZE_SCOPE = (
    "Spare Part Catalog model",
    "Inventory Item model",
    "Inventory Location model",
    "Spare Part Requirement model",
    "Work Order spare part readiness",
    "PM spare part readiness",
    "Inventory policy model",
    "Procurement suggestion readiness",
    "Inventory validation gate model",
    "Asset spare part linkage model",
    "Airport-to-inventory mapping",
    "Customer core function R6 alignment",
    "Shared EDGE/LINK/UCDE dependency map",
    "Future UMMS roadmap",
)
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
    "inventoryTransaction | false",
    "stockReservation | false",
    "stockDeduction | false",
    "stockReturn | false",
    "procurementExecution | false",
    "purchaseOrderExecution | false",
    "warehouseTransferExecution | false",
    "workOrderSparePartConsumption | false",
    "pmExecution | false",
    "pmScheduleExecution | false",
    "automaticWorkOrderGeneration | false",
    "workOrderCreation | false",
    "workOrderUpdate | false",
    "workOrderAssignment | false",
    "workOrderApproval | false",
    "workOrderClosure | false",
    "assetLifecycleWrite | false",
    "vendorContractExecution | false",
    "deploymentExecution | false",
    "remoteCommandExecution | false",
    "connectorExecution | false",
    "deviceConnection | false",
    "edgeRuntimeCall | false",
    "linkRuntimeCall | false",
    "oneAdapterIntroduced | false",
    "customerIdentifierLeakage | false",
    "localAbsolutePathLeakage | false",
)
ALLOWED_CHANGED_PREFIXES = (
    "ONE_UMMS_R6A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN.md",
    "AN_VANTARIS_ONE/registries/umms-r6a-local-freeze.v1.json",
    "ONE_UMMS_R6A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md",
    "scripts/validation/validate-one-umms-r6a-local-freeze.py",
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
LEAKAGE_TERMS = ("customerAssetIdentifier",)
REGRESSION_MARKERS = {
    "scripts/validation/validate-one-umms-r6-spare-parts-inventory-readiness.py": "ONE_UMMS_R6_SPARE_PARTS_INVENTORY_READINESS_PASS",
    "scripts/validation/validate-one-umms-r5a-local-freeze.py": "ONE_UMMS_R5A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "scripts/validation/validate-one-umms-r5-preventive-maintenance-schedule-readiness.py": "ONE_UMMS_R5_PREVENTIVE_MAINTENANCE_SCHEDULE_READINESS_PASS",
    "scripts/validation/validate-one-umms-r4a-local-freeze.py": "ONE_UMMS_R4A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "scripts/validation/validate-one-umms-r4-work-order-lifecycle-state-validation-gate.py": "ONE_UMMS_R4_WORK_ORDER_LIFECYCLE_STATE_VALIDATION_GATE_PASS",
    "scripts/validation/validate-one-umms-r3a-local-freeze.py": "ONE_UMMS_R3A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "scripts/validation/validate-one-umms-r3-manual-work-order-readonly-queue-draft-model.py": "ONE_UMMS_R3_MANUAL_WORK_ORDER_READONLY_QUEUE_DRAFT_MODEL_PASS",
    "scripts/validation/validate-one-umms-r2a-local-freeze.py": "ONE_UMMS_R2A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "scripts/validation/validate-one-umms-r2-work-order-asset-pm-domain-alignment.py": "ONE_UMMS_R2_WORK_ORDER_ASSET_PM_DOMAIN_ALIGNMENT_PASS",
}


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
    if _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip() == "docs(one): freeze umms spare parts inventory readiness":
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


def _frozen_marker_present(marker: str) -> bool:
    result = _run(["git", "grep", "-n", marker, "HEAD"])
    return result.returncode == 0 and marker in result.stdout


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    freeze_text = FREEZE_DOC.read_text(encoding="utf-8") if FREEZE_DOC.exists() else ""
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    combined = "\n".join([freeze_text, registry_text, report_text])
    lower_combined = combined.lower()

    checks.append(("UMMS-R6A freeze document exists", FREEZE_DOC.is_file()))
    checks.append(("Optional registry exists", REGISTRY.is_file()))
    checks.append(("UMMS-R6A report exists", REPORT.is_file()))
    checks.append(("UMMS-R6 commit reference is present", UMMS_R6_COMMIT in freeze_text and UMMS_R6_COMMIT in registry_text))
    checks.append(("UMMS-R6 PASS marker is referenced", UMMS_R6_MARKER in combined))
    checks.append(("Freeze scope includes all required UMMS-R6 scope items", all(item in freeze_text for item in FREEZE_SCOPE)))
    checks.append(("UMMS-R6 summary states UMMS is generic and not Airport-specific", "UMMS remains a generic cross-industry maintenance management module." in freeze_text and "not UMMS core identity" in freeze_text and "not Airport-specific logic" in freeze_text))
    checks.append(("UMMS-R6 summary states no inventory transaction, stock mutation, procurement execution, purchase order execution, warehouse transfer, or work-order spare-part consumption exists", "No inventory transaction, stock mutation, procurement execution, purchase order execution, warehouse transfer, or work-order spare-part consumption exists." in freeze_text))
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
    checks.append(("No inventory transaction claim", "This is not inventory transaction." in freeze_text and "inventory transaction enabled" not in lower_combined))
    checks.append(("No stock reservation/deduction/return claim", "This is not stock reservation, stock deduction, or stock return." in freeze_text and "stock reservation enabled" not in lower_combined and "stock deduction enabled" not in lower_combined and "stock return enabled" not in lower_combined))
    checks.append(("No procurement execution claim", "This is not procurement execution." in freeze_text and "procurement execution enabled" not in lower_combined))
    checks.append(("No purchase order execution claim", "This is not purchase order execution." in freeze_text and "purchase order execution enabled" not in lower_combined))
    checks.append(("No warehouse transfer execution claim", "This is not warehouse transfer execution." in freeze_text and "warehouse transfer execution enabled" not in lower_combined))
    checks.append(("No work-order spare-part consumption claim", "This is not work-order spare-part consumption." in freeze_text and "work-order spare-part consumption enabled" not in lower_combined))
    checks.append(("No PM execution claim", "This is not PM execution." in freeze_text and "pm execution enabled" not in lower_combined))
    checks.append(("No automatic work order generation claim", "This is not automatic work order generation." in freeze_text and "automatic work order generation enabled" not in lower_combined))
    checks.append(("No asset lifecycle write claim", "This is not asset lifecycle write." in freeze_text and "asset lifecycle write enabled" not in lower_combined))
    checks.append(("No vendor/contract execution claim", "This is not vendor/contract execution." in freeze_text and "vendor/contract execution enabled" not in lower_combined))
    checks.append(("No EDGE/LINK runtime integration claim", "This is not EDGE/LINK runtime integration." in freeze_text and "edge/link runtime integration enabled" not in lower_combined))
    checks.append(("No ONE Adapter introduction", "oneAdapterIntroduced | false" in freeze_text and "one adapter introduced: yes" not in lower_combined))
    checks.append(("No customer identifier leakage", not any(term in combined for term in LEAKAGE_TERMS)))
    checks.append(("No local absolute path leakage except baseline workspace", _workspace_path_only_in_baseline(freeze_text) and "/Users/" not in report_text and "/Users/" not in registry_text))
    checks.append(("UMMS-R6A PASS marker present", PASS_MARKER in combined))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to UMMS-R6A freeze scope", not disallowed))
    checks.append(("No EDGE/LINK/Contracts/UFMS files modified", not forbidden and not any("VANTARIS_UFMS_FULL" in path for path in changed)))
    if disallowed:
        errors.append(f"changes outside UMMS-R6A scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    try:
        registry_data = json.loads(registry_text)
    except Exception as exc:
        registry_data = {}
        errors.append(f"registry json invalid: {exc}")
    checks.append(("Registry freeze id present", registry_data.get("releaseFreezeId") == "umms-r6a-local-freeze-20260621"))
    safety = registry_data.get("safetyMatrix", {})
    checks.append(("Registry tag and push false", registry_data.get("pushPerformed") is False and registry_data.get("tagCreated") is False and registry_data.get("optionalTagPlan", {}).get("commandsExecuted") is False))
    checks.append(("Registry safety matrix frozen", safety.get("readOnly") is True and safety.get("oneAdapterIntroduced") is False and safety.get("inventoryTransaction") is False and safety.get("stockReservation") is False and safety.get("procurementExecution") is False))
    checks.append(("Registry validation matrix includes UMMS-R6 marker", UMMS_R6_MARKER in registry_data.get("validationMatrix", {})))

    airport_client_text = AIRPORT_CLIENT.read_text(encoding="utf-8") if AIRPORT_CLIENT.exists() else ""
    checks.append(("No POST/PUT/PATCH/DELETE Airport or UMMS API client methods added", not any(method in airport_client_text for method in FORBIDDEN_CLIENT_METHODS)))

    for script, marker in REGRESSION_MARKERS.items():
        checks.append((f"{Path(script).name} frozen PASS marker remains available", _frozen_marker_present(marker)))

    package_route = _run(["python3", "scripts/validation/validate-one-package-route-enforcement.py"], env={"PYTHONPATH": "AN_VANTARIS_ONE"})
    checks.append(("Package route enforcement still passes", package_route.returncode == 0 and "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS" in package_route.stdout))
    if package_route.returncode != 0:
        errors.append(package_route.stdout[-3000:] or package_route.stderr[-3000:] or "package route enforcement failed")
    boundary = _run(["python3", "scripts/validation/validate-one-boundaries.py"], env={"PYTHONPATH": "AN_VANTARIS_ONE"})
    checks.append(("Boundary baseline still passes", boundary.returncode == 0 and "ONE_BOUNDARY_BASELINE_PASS" in boundary.stdout))
    if boundary.returncode != 0:
        errors.append(boundary.stdout[-3000:] or boundary.stderr[-3000:] or "boundary baseline failed")
    checks.append(("Projection JSON validation passes", _json_valid(UMMS_R6_PROJECTION)))
    checks.append(("Registry JSON validation passes", _json_valid(UMMS_R6_REGISTRY) and _json_valid(REGISTRY)))

    print("ONE_UMMS_R6A_LOCAL_FREEZE_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_UMMS_R6A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_FAIL")
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
