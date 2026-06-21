#!/usr/bin/env python3
"""Validate UMMS-R6 spare parts / inventory readiness."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTION = ROOT / "AN_VANTARIS_ONE/projections/umms-spare-parts-inventory-readiness.v1.json"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-spare-parts-inventory-readiness-registry.v1.json"
REPORT = ROOT / "ONE_UMMS_R6_SPARE_PARTS_INVENTORY_READINESS_REPORT.md"
AIRPORT_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts"
PASS_MARKER = "ONE_UMMS_R6_SPARE_PARTS_INVENTORY_READINESS_PASS"

SAFETY_EXPECTED = {
    "readOnly": True,
    "runtimeActivation": False,
    "productionActivation": False,
    "dbWrite": False,
    "approvalExecution": False,
    "workflowExecution": False,
    "inventoryTransaction": False,
    "stockReservation": False,
    "stockDeduction": False,
    "stockReturn": False,
    "procurementExecution": False,
    "purchaseOrderExecution": False,
    "warehouseTransferExecution": False,
    "workOrderSparePartConsumption": False,
    "pmScheduleExecution": False,
    "automaticWorkOrderGeneration": False,
    "workOrderCreation": False,
    "workOrderUpdate": False,
    "workOrderAssignment": False,
    "workOrderApproval": False,
    "workOrderClosure": False,
    "assetLifecycleWrite": False,
    "vendorContractExecution": False,
    "connectorExecution": False,
    "deviceConnection": False,
    "edgeRuntimeCall": False,
    "linkRuntimeCall": False,
    "oneAdapterIntroduced": False,
}
POLICIES = {"minimum_stock_policy", "reorder_point_policy", "reservation_policy", "issue_policy", "return_policy", "stock_count_policy", "expiry_policy", "substitution_policy", "vendor_lead_time_policy", "critical_spares_policy"}
GATES = {"Spare part catalog completeness gate", "Inventory item reference gate", "Inventory location reference gate", "Minimum stock readiness gate", "Work order spare part requirement gate", "PM spare part requirement gate", "Reservation readiness gate", "Issue readiness gate", "Return readiness gate", "Substitute part readiness gate", "Vendor / contract readiness gate", "Procurement suggestion readiness gate", "Evidence readiness gate", "Stock count readiness gate", "Expiry / warranty readiness gate"}
AIRPORT_MAPPINGS = {"Airport Assets & Topology", "Airport Maintenance Work Orders", "Airport Preventive Maintenance readiness", "Airport Fault Cases", "Airport Evidence Investigation", "Airport HMI Locator Readiness", "Airport Reports"}
CUSTOMER_FUNCTIONS = {"Work Order Management, auto + manual", "Asset Registry, full lifecycle tracking", "Preventive Maintenance Scheduler", "Spare Parts / Inventory Management", "Vendor / Contract Management", "Graphics HMI to locate Equipment", "Existing system onboarding", "Engineer commissioning diagnostics", "Remote overseas deployment", "Distributed independent installation"}
EDGE_DEPS = {"Asset/location mapping preview", "Tag mapping and normalization", "HMI locator data foundation", "Engineer diagnostics", "Condition signals for critical spares planning, future"}
LINK_DEPS = {"Source-system health contract", "Delivery readiness contract", "Asset/location reference contract", "Work-order trigger contract", "Audit/evidence chain profile", "Delivery / ACK / retry / DLQ status", "Distributed topology contract"}
UCDE_DEPS = {"Spare part catalog evidence", "Inventory item evidence", "Reservation evidence", "Issue/return evidence", "Procurement suggestion evidence", "Work order spare part evidence", "PM spare part evidence", "Audit trail", "Report evidence"}
ROADMAP = {"UMMS-R6A Local Freeze + Optional Tag Plan", "UMMS-R7 Vendor / Contract / SLA Readiness", "UMMS-R8 UMMS + UCDE Evidence Closure Alignment", "UMMS-R9 UMMS + Airport HMI Locator Binding Readiness", "UMMS-R10 UMMS Stakeholder Review Package"}
ALLOWED_CHANGED_PREFIXES = (
    "AN_VANTARIS_ONE/projections/umms-spare-parts-inventory-readiness.v1.json",
    "AN_VANTARIS_ONE/registries/umms-spare-parts-inventory-readiness-registry.v1.json",
    "ONE_UMMS_R6_SPARE_PARTS_INVENTORY_READINESS_REPORT.md",
    "scripts/validation/validate-one-umms-r6-spare-parts-inventory-readiness.py",
    "AN_VANTARIS_ONE/tests/",
)
FORBIDDEN_CHANGED_PREFIXES = ("AN_VANTARIS_EDGE/", "AN_VANTARIS_LINK/", "AN_VANTARIS_Contracts/", "/Volumes/Work/VANTARIS_UFMS_FULL", "AN_VANTARIS_IBMS-backend/", "AN_VANTARIS_IBMS-frontend/", "database/", "migrations/")
FORBIDDEN_CLIENT_METHODS = (".post", ".put", ".patch", ".delete")
LEAKAGE_TERMS = ("/Users/", "/Volumes/Work/VANTARIS_UFMS_FULL", "customerAssetIdentifier")
REGRESSION_MARKERS = {
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
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False, env=merged)


def _load_json(path: Path) -> tuple[dict, str]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), ""
    except Exception as exc:
        return {}, str(exc)


def _changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (["git", "diff", "--name-only", "HEAD"], ["git", "diff", "--cached", "--name-only"], ["git", "ls-files", "--others", "--exclude-standard"]):
        paths.update(line for line in _run(command).stdout.splitlines() if line)
    if _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip() == "docs(one): add umms spare parts inventory readiness":
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _has_all(items: list | set, required: set[str]) -> bool:
    return required.issubset(set(items))


def _marker(marker: str) -> bool:
    result = _run(["git", "grep", "-n", marker, "HEAD"])
    return result.returncode == 0 and marker in result.stdout


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    projection, projection_error = _load_json(PROJECTION)
    registry, registry_error = _load_json(REGISTRY)
    projection_text = PROJECTION.read_text(encoding="utf-8") if PROJECTION.exists() else ""
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    stakeholder_text = "\n".join([projection_text, registry_text, report_text])

    checks.extend([
        ("UMMS-R6 projection artifact exists", PROJECTION.is_file() and not projection_error),
        ("UMMS-R6 registry exists", REGISTRY.is_file() and not registry_error),
        ("UMMS-R6 report exists", REPORT.is_file()),
    ])
    metadata = projection.get("metadata", {})
    scope = projection.get("r6ScopeSummary", {})
    checks.append(("Projection metadata contains platform = VANTARIS ONE", metadata.get("platform") == "VANTARIS ONE"))
    checks.append(("Projection metadata contains module = UMMS", metadata.get("module") == "UMMS"))
    checks.append(("Projection safety flags are correct", all(metadata.get(k) is v for k, v in SAFETY_EXPECTED.items() if k in metadata)))
    checks.append(("r6ScopeSummary confirms UMMS is generic and Airport-specific logic is not in core", scope.get("genericModuleScope") == "cross_industry_maintenance_management" and scope.get("airportSpecificLogicInCore") is False))
    checks.append(("r6ScopeSummary confirms inventoryExecutionEnabled is false", scope.get("inventoryExecutionEnabled") is False))
    checks.append(("r6ScopeSummary confirms stockReservationEnabled is false", scope.get("stockReservationEnabled") is False))
    checks.append(("r6ScopeSummary confirms procurementExecutionEnabled is false", scope.get("procurementExecutionEnabled") is False))
    catalog = projection.get("sparePartCatalogModel", {})
    item = projection.get("inventoryItemModel", {})
    location = projection.get("inventoryLocationModel", {})
    requirement = projection.get("sparePartRequirementModel", {})
    wo_readiness = projection.get("workOrderSparePartReadiness", {})
    pm_readiness = projection.get("pmSparePartReadiness", {})
    procurement = projection.get("procurementSuggestionReadiness", {})
    checks.append(("sparePartCatalogModel exists and activationAllowed is false", catalog.get("activationAllowed") is False))
    checks.append(("sparePartCatalogModel states no spare part catalog creation/update/delete/approval/activation is implemented", "No spare part catalog creation, update, deletion, approval, or activation is implemented" in catalog.get("statement", "")))
    checks.append(("inventoryItemModel exists and activationAllowed is false", item.get("activationAllowed") is False))
    checks.append(("inventoryItemModel states no inventory item write or quantity mutation is implemented", "No inventory item write or quantity mutation is implemented" in item.get("statement", "")))
    checks.append(("inventoryLocationModel exists and states no inventory location creation/update is implemented", "No inventory location creation/update is implemented" in location.get("statement", "")))
    checks.append(("sparePartRequirementModel exists and states no reservation/issue/deduction/consumption is implemented", "No reservation, issue, deduction, or consumption is implemented" in requirement.get("statement", "")))
    checks.append(("workOrderSparePartReadiness exists and states no work order spare part consumption is implemented", "No work order spare part consumption is implemented" in wo_readiness.get("statement", "")))
    checks.append(("pmSparePartReadiness exists and states no PM spare part reservation or consumption is implemented", "No PM spare part reservation or consumption is implemented" in pm_readiness.get("statement", "")))
    checks.append(("inventoryPolicyModel includes all required policies and executionAllowedInR6 is false", POLICIES.issubset({p.get("policyType") for p in projection.get("inventoryPolicyModel", [])}) and all(p.get("executionAllowedInR6") is False for p in projection.get("inventoryPolicyModel", []))))
    checks.append(("procurementSuggestionReadiness exists and purchaseOrderAllowed is false", procurement.get("purchaseOrderAllowed") is False))
    checks.append(("procurementSuggestionReadiness states no procurement request or purchase order execution is implemented", "No procurement request or purchase order execution is implemented" in procurement.get("statement", "")))
    checks.append(("inventoryValidationGateModel includes all required validation gates", GATES.issubset({g.get("gateName") for g in projection.get("inventoryValidationGateModel", [])})))
    checks.append(("assetSparePartLinkageModel exists and states UMMS-R6 does not write canonical Asset Graph", "UMMS-R6 does not write canonical Asset Graph" in projection.get("assetSparePartLinkageModel", {}).get("statement", "")))
    checks.append(("airportToInventoryMapping includes all required mappings", AIRPORT_MAPPINGS.issubset({m.get("airportSource") for m in projection.get("airportToInventoryMapping", [])})))
    checks.append(("customerCoreFunctionR6Alignment includes all 10 customer core functions", CUSTOMER_FUNCTIONS.issubset({f.get("function") for f in projection.get("customerCoreFunctionR6Alignment", [])})))
    deps = projection.get("sharedFoundationDependencyMap", {})
    checks.append(("sharedFoundationDependencyMap includes required EDGE dependencies", _has_all(deps.get("edgeDependencies", []), EDGE_DEPS)))
    checks.append(("sharedFoundationDependencyMap includes required LINK dependencies", _has_all(deps.get("linkDependencies", []), LINK_DEPS)))
    checks.append(("sharedFoundationDependencyMap includes required UCDE dependencies", _has_all(deps.get("ucdeDependencies", []), UCDE_DEPS)))
    checks.append(("futureImplementationRoadmap includes UMMS-R6A through UMMS-R10", _has_all(projection.get("futureImplementationRoadmap", []), ROADMAP)))
    safety = projection.get("safetyPosture", {})
    checks.append(("safetyPosture confirms no runtime/production/DB/approval/workflow/inventory/stock/procurement/work order/PM/asset/vendor/connector/device execution", all(safety.get(k) is v for k, v in SAFETY_EXPECTED.items()) and safety.get("customerIdentifierLeakage") is False and safety.get("localAbsolutePathLeakage") is False))
    checks.append(("No ONE Adapter introduced", metadata.get("oneAdapterIntroduced") is False and safety.get("oneAdapterIntroduced") is False and "ONE Adapter introduced: no" in report_text))

    changed = _changed_paths()
    disallowed = [p for p in changed if not any(p.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [p for p in changed if any(p.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("No AN_VANTARIS_EDGE files modified", not any(p.startswith("AN_VANTARIS_EDGE/") for p in changed)))
    checks.append(("No AN_VANTARIS_LINK files modified", not any(p.startswith("AN_VANTARIS_LINK/") for p in changed)))
    checks.append(("No AN_VANTARIS_Contracts files modified", not any(p.startswith("AN_VANTARIS_Contracts/") for p in changed)))
    checks.append(("No UFMS source modified", not any("VANTARIS_UFMS_FULL" in p for p in changed)))
    checks.append(("No backend API behavior modified unless explicitly allowed and documented", not any(p.startswith("AN_VANTARIS_IBMS-backend/") for p in changed)))
    checks.append(("No frontend behavior modified unless explicitly allowed and documented", not any(p.startswith("AN_VANTARIS_IBMS-frontend/") for p in changed)))
    checks.append(("Changes limited to UMMS-R6 projection scope", not disallowed and not forbidden))
    if disallowed:
        errors.append(f"changes outside UMMS-R6 scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    airport_client_text = AIRPORT_CLIENT.read_text(encoding="utf-8") if AIRPORT_CLIENT.exists() else ""
    checks.append(("No POST/PUT/PATCH/DELETE Airport or UMMS API client methods added", not any(method in airport_client_text for method in FORBIDDEN_CLIENT_METHODS)))
    checks.append(("No customer identifier leakage", not any(term in stakeholder_text for term in LEAKAGE_TERMS[2:])))
    checks.append(("No local absolute path leakage in stakeholder-facing artifacts", not any(term in stakeholder_text for term in LEAKAGE_TERMS[:2])))
    checks.append(("Projection JSON validation passes", not projection_error and metadata.get("projectionId") == "umms-spare-parts-inventory-readiness.v1"))
    checks.append(("Registry JSON validation passes", not registry_error and registry.get("validationMarker") == PASS_MARKER))
    checks.append(("Report contains PASS marker", PASS_MARKER in report_text))
    for script, marker in REGRESSION_MARKERS.items():
        checks.append((f"{Path(script).name} frozen PASS marker remains available", _marker(marker)))

    package_route = _run(["python3", "scripts/validation/validate-one-package-route-enforcement.py"], env={"PYTHONPATH": "AN_VANTARIS_ONE"})
    checks.append(("Package route enforcement still passes", package_route.returncode == 0 and "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS" in package_route.stdout))
    boundary = _run(["python3", "scripts/validation/validate-one-boundaries.py"], env={"PYTHONPATH": "AN_VANTARIS_ONE"})
    checks.append(("Boundary baseline still passes", boundary.returncode == 0 and "ONE_BOUNDARY_BASELINE_PASS" in boundary.stdout))

    print("ONE_UMMS_R6_SPARE_PARTS_INVENTORY_READINESS_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_UMMS_R6_SPARE_PARTS_INVENTORY_READINESS_FAIL")
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
