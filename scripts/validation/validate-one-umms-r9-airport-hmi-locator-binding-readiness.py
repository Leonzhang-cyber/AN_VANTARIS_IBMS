#!/usr/bin/env python3
"""Validate UMMS-R9 Airport HMI locator binding readiness."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTION = ROOT / "AN_VANTARIS_ONE/projections/umms-airport-hmi-locator-binding-readiness.v1.json"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-airport-hmi-locator-binding-readiness-registry.v1.json"
REPORT = ROOT / "ONE_UMMS_R9_AIRPORT_HMI_LOCATOR_BINDING_READINESS_REPORT.md"
AIRPORT_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts"
PASS_MARKER = "ONE_UMMS_R9_AIRPORT_HMI_LOCATOR_BINDING_READINESS_PASS"

SAFETY_EXPECTED = {"readOnly": True, "runtimeActivation": False, "productionActivation": False, "dbWrite": False, "approvalExecution": False, "workflowExecution": False, "hmiRuntimeExecution": False, "hmiControlExecution": False, "drawingUpload": False, "bimRuntimeIntegration": False, "topologyRuntimeIntegration": False, "equipmentControl": False, "workOrderRuntimeExecution": False, "pmExecution": False, "inventoryTransaction": False, "vendorContractExecution": False, "evidenceUpload": False, "evidenceClosureExecution": False, "auditTrailWrite": False, "connectorExecution": False, "deviceConnection": False, "edgeRuntimeCall": False, "linkRuntimeCall": False, "oneAdapterIntroduced": False}
VALIDATION_CHECKS = {"assetRef presence", "locationRef presence", "hmiLocatorRef presence", "drawingRef presence", "hmiSymbolRef presence", "floorPlanRef presence, optional", "topologyNodeRef presence, optional", "bimObjectRef presence, future optional", "duplicate symbol detection", "conflicting location detection", "stale drawing version detection", "missing equipment space detection", "missing evidence context", "missing work order context", "missing PM context", "missing vendor/contract context, optional"}
GATES = {"Asset locator reference gate", "Location hierarchy gate", "Drawing reference gate", "HMI symbol reference gate", "Work order locator gate", "Fault case locator gate", "PM locator gate", "Inventory locator context gate", "Vendor / contract locator context gate", "UCDE evidence locator context gate", "Drawing version readiness gate", "Symbol library readiness gate", "Customer drawing redaction gate", "Local path leakage gate", "Runtime HMI activation gate, future only"}
AIRPORT_MAPPINGS = {"Airport Graphics HMI Equipment Locator Readiness", "Airport Assets & Topology", "Airport Alarms & Events", "Airport Fault Cases", "Airport Maintenance Work Orders", "Airport Evidence Investigation", "Airport PM Readiness", "Airport Inventory Readiness", "Airport Vendor / Contract / SLA Readiness"}
CUSTOMER_FUNCTIONS = {"Work Order Management, auto + manual", "Asset Registry, full lifecycle tracking", "Preventive Maintenance Scheduler", "Spare Parts / Inventory Management", "Vendor / Contract Management", "Graphics HMI to locate Equipment", "Existing system onboarding", "Engineer commissioning diagnostics", "Remote overseas deployment", "Distributed independent installation"}
EDGE_DEPS = {"assetRef / locationRef capture from connector mapping", "hmiSymbolRef mapping support", "drawingRef mapping support", "source tag to asset/location mapping preview", "asset-location mapping diagnostics", "HMI locator data foundation", "sample payload with asset/location references", "normalization preview with locator references"}
LINK_DEPS = {"asset/location reference contract", "hmiSymbolRef / drawingRef reference fields", "delivery envelope with asset/location references", "work-order trigger with asset/location/hmi references", "evidence chain with asset/location context", "mapping profile contract", "distributed topology with site/building/floor references"}
UCDE_DEPS = {"EvidenceRecord", "HmiLocatorEvidenceContext", "WorkOrderEvidence", "FaultCaseEvidence", "PmEvidence", "InventoryEvidence", "VendorContractEvidence", "AuditTrail", "HandoffPackage"}
RENDERING_DEPS = {"2D floor plan renderer", "Symbol library", "Equipment locator overlay", "Asset topology graph", "System topology view", "Alarm/event highlight overlay", "Work order location overlay", "PM task location overlay", "Inventory location overlay", "Vendor support location overlay", "Evidence-linked location view", "BIM integration, future optional", "Mobile locator view, future optional"}
ROADMAP = {"UMMS-R9A Local Freeze + Optional Tag Plan", "UMMS-R10 UMMS Stakeholder Review Package"}
ALLOWED_CHANGED_PREFIXES = ("AN_VANTARIS_ONE/projections/umms-airport-hmi-locator-binding-readiness.v1.json", "AN_VANTARIS_ONE/registries/umms-airport-hmi-locator-binding-readiness-registry.v1.json", "ONE_UMMS_R9_AIRPORT_HMI_LOCATOR_BINDING_READINESS_REPORT.md", "scripts/validation/validate-one-umms-r9-airport-hmi-locator-binding-readiness.py", "AN_VANTARIS_ONE/tests/")
FORBIDDEN_CHANGED_PREFIXES = ("AN_VANTARIS_EDGE/", "AN_VANTARIS_LINK/", "AN_VANTARIS_Contracts/", "/Volumes/Work/VANTARIS_UFMS_FULL", "AN_VANTARIS_IBMS-backend/", "AN_VANTARIS_IBMS-frontend/", "database/", "migrations/")
FORBIDDEN_CLIENT_METHODS = (".post", ".put", ".patch", ".delete")
LEAKAGE_TERMS = ("/Users/", "/Volumes/Work/VANTARIS_UFMS_FULL", "customerAssetIdentifier")
REGRESSION_MARKERS = {
    "scripts/validation/validate-one-umms-r8a-local-freeze.py": "ONE_UMMS_R8A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "scripts/validation/validate-one-umms-r8-ucde-evidence-closure-alignment.py": "ONE_UMMS_R8_UCDE_EVIDENCE_CLOSURE_ALIGNMENT_PASS",
    "scripts/validation/validate-one-umms-r7a-local-freeze.py": "ONE_UMMS_R7A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "scripts/validation/validate-one-umms-r7-vendor-contract-sla-readiness.py": "ONE_UMMS_R7_VENDOR_CONTRACT_SLA_READINESS_PASS",
    "scripts/validation/validate-one-umms-r6a-local-freeze.py": "ONE_UMMS_R6A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
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
    if _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip() == "docs(one): add umms airport hmi locator binding readiness":
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _marker(marker: str) -> bool:
    result = _run(["git", "grep", "-n", marker, "HEAD"])
    return result.returncode == 0 and marker in result.stdout


def _has_all(items: list | set, required: set[str]) -> bool:
    return required.issubset(set(items))


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    projection, projection_error = _load_json(PROJECTION)
    registry, registry_error = _load_json(REGISTRY)
    projection_text = PROJECTION.read_text(encoding="utf-8") if PROJECTION.exists() else ""
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    stakeholder_text = "\n".join([projection_text, registry_text, report_text])

    checks.extend([("UMMS-R9 projection artifact exists", PROJECTION.is_file() and not projection_error), ("UMMS-R9 registry exists", REGISTRY.is_file() and not registry_error), ("UMMS-R9 report exists", REPORT.is_file())])
    metadata = projection.get("metadata", {})
    scope = projection.get("r9ScopeSummary", {})
    checks.append(("Projection metadata contains platform = VANTARIS ONE", metadata.get("platform") == "VANTARIS ONE"))
    checks.append(("Projection metadata contains module = UMMS", metadata.get("module") == "UMMS"))
    checks.append(("Projection metadata contains relatedIndustryProjection = airport", metadata.get("relatedIndustryProjection") == "airport"))
    checks.append(("Projection safety flags are correct", all(metadata.get(k) is v for k, v in SAFETY_EXPECTED.items() if k in metadata)))
    checks.append(("r9ScopeSummary confirms UMMS is generic and Airport-specific logic is not in core", scope.get("genericModuleScope") == "cross_industry_maintenance_management" and scope.get("airportSpecificLogicInCore") is False))
    checks.append(("r9ScopeSummary confirms hmiRuntimeEnabled is false", scope.get("hmiRuntimeEnabled") is False))
    checks.append(("r9ScopeSummary confirms drawingUploadEnabled is false", scope.get("drawingUploadEnabled") is False))
    checks.append(("r9ScopeSummary confirms equipmentControlEnabled is false", scope.get("equipmentControlEnabled") is False))

    readiness = projection.get("hmiLocatorBindingReadinessModel", {})
    wo = projection.get("workOrderHmiLocatorBindingModel", {})
    pm = projection.get("pmHmiLocatorBindingModel", {})
    inventory = projection.get("inventoryHmiLocatorBindingModel", {})
    vendor = projection.get("vendorContractHmiLocatorBindingModel", {})
    ucde = projection.get("ucdeEvidenceHmiContextModel", {})
    checks.append(("hmiLocatorBindingReadinessModel exists and activationAllowed is false", readiness.get("activationAllowed") is False))
    checks.append(("hmiLocatorBindingReadinessModel states no HMI runtime or locator binding execution is implemented", "No HMI runtime or locator binding execution is implemented" in readiness.get("statement", "")))
    checks.append(("workOrderHmiLocatorBindingModel exists and states no work order HMI runtime binding or work order execution is implemented", "No work order HMI runtime binding or work order execution is implemented" in wo.get("statement", "")))
    checks.append(("pmHmiLocatorBindingModel exists and states no PM HMI runtime binding or PM execution is implemented", "No PM HMI runtime binding or PM execution is implemented" in pm.get("statement", "")))
    checks.append(("inventoryHmiLocatorBindingModel exists and states no inventory transaction or HMI runtime binding is implemented", "No inventory transaction or HMI runtime binding is implemented" in inventory.get("statement", "")))
    checks.append(("vendorContractHmiLocatorBindingModel exists and states no vendor / contract / SLA runtime or HMI runtime binding is implemented", "No vendor / contract / SLA runtime or HMI runtime binding is implemented" in vendor.get("statement", "")))
    checks.append(("ucdeEvidenceHmiContextModel exists and states no UCDE evidence write/upload/runtime HMI context binding is implemented", "No UCDE evidence write, upload, or runtime HMI context binding is implemented" in ucde.get("statement", "")))
    checks.append(("locatorReferenceValidationModel includes all required validation checks", VALIDATION_CHECKS.issubset({c.get("checkName") for c in projection.get("locatorReferenceValidationModel", [])})))
    checks.append(("hmiLocatorValidationGateModel includes all required validation gates", GATES.issubset({g.get("gateName") for g in projection.get("hmiLocatorValidationGateModel", [])})))
    checks.append(("airportHmiReadinessDependencyMap includes all required mappings", AIRPORT_MAPPINGS.issubset({m.get("airportSource") for m in projection.get("airportHmiReadinessDependencyMap", [])})))
    checks.append(("customerCoreFunctionR9Alignment includes all 10 customer core functions", CUSTOMER_FUNCTIONS.issubset({f.get("function") for f in projection.get("customerCoreFunctionR9Alignment", [])})))
    deps = projection.get("sharedFoundationDependencyMap", {})
    checks.append(("sharedFoundationDependencyMap includes required EDGE dependencies", _has_all(deps.get("edgeDependencies", []), EDGE_DEPS)))
    checks.append(("sharedFoundationDependencyMap includes required LINK dependencies", _has_all(deps.get("linkDependencies", []), LINK_DEPS)))
    checks.append(("sharedFoundationDependencyMap includes required UCDE dependencies", _has_all(deps.get("ucdeDependencies", []), UCDE_DEPS)))
    rendering = projection.get("futureRenderingDependencyModel", {})
    checks.append(("futureRenderingDependencyModel includes all required dependencies and states UMMS-R9 does not implement rendering", _has_all(rendering.get("dependencies", []), RENDERING_DEPS) and "UMMS-R9 does not implement rendering" in rendering.get("statement", "")))
    checks.append(("futureImplementationRoadmap includes UMMS-R9A and UMMS-R10", _has_all(projection.get("futureImplementationRoadmap", []), ROADMAP)))
    safety = projection.get("safetyPosture", {})
    checks.append(("safetyPosture confirms no runtime/production/DB/approval/workflow/HMI/drawing/BIM/device/work order/PM/inventory/vendor/evidence/connector execution", all(safety.get(k) is v for k, v in SAFETY_EXPECTED.items()) and safety.get("customerIdentifierLeakage") is False and safety.get("localAbsolutePathLeakage") is False))
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
    checks.append(("Changes limited to UMMS-R9 projection scope", not disallowed and not forbidden))
    if disallowed:
        errors.append(f"changes outside UMMS-R9 scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    airport_client_text = AIRPORT_CLIENT.read_text(encoding="utf-8") if AIRPORT_CLIENT.exists() else ""
    checks.append(("No POST/PUT/PATCH/DELETE Airport, UMMS, UCDE, or HMI API client methods added", not any(method in airport_client_text for method in FORBIDDEN_CLIENT_METHODS)))
    checks.append(("No customer identifier leakage", not any(term in stakeholder_text for term in LEAKAGE_TERMS[2:])))
    checks.append(("No local absolute path leakage in stakeholder-facing artifacts", not any(term in stakeholder_text for term in LEAKAGE_TERMS[:2])))
    checks.append(("Projection JSON validation passes", not projection_error and metadata.get("projectionId") == "umms-airport-hmi-locator-binding-readiness.v1"))
    checks.append(("Registry JSON validation passes", not registry_error and registry.get("validationMarker") == PASS_MARKER))
    checks.append(("Report contains PASS marker", PASS_MARKER in report_text))
    for script, marker in REGRESSION_MARKERS.items():
        checks.append((f"{Path(script).name} frozen PASS marker remains available", _marker(marker)))

    package_route = _run(["python3", "scripts/validation/validate-one-package-route-enforcement.py"], env={"PYTHONPATH": "AN_VANTARIS_ONE"})
    checks.append(("Package route enforcement still passes", package_route.returncode == 0 and "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS" in package_route.stdout))
    boundary = _run(["python3", "scripts/validation/validate-one-boundaries.py"], env={"PYTHONPATH": "AN_VANTARIS_ONE"})
    checks.append(("Boundary baseline still passes", boundary.returncode == 0 and "ONE_BOUNDARY_BASELINE_PASS" in boundary.stdout))

    print("ONE_UMMS_R9_AIRPORT_HMI_LOCATOR_BINDING_READINESS_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_UMMS_R9_AIRPORT_HMI_LOCATOR_BINDING_READINESS_FAIL")
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
