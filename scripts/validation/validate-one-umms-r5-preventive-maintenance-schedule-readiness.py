#!/usr/bin/env python3
"""Validate UMMS-R5 preventive maintenance schedule readiness."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTION = ROOT / "AN_VANTARIS_ONE/projections/umms-preventive-maintenance-schedule-readiness.v1.json"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-preventive-maintenance-schedule-readiness-registry.v1.json"
REPORT = ROOT / "ONE_UMMS_R5_PREVENTIVE_MAINTENANCE_SCHEDULE_READINESS_REPORT.md"
AIRPORT_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts"
PASS_MARKER = "ONE_UMMS_R5_PREVENTIVE_MAINTENANCE_SCHEDULE_READINESS_PASS"

SAFETY_EXPECTED = {"readOnly": True, "runtimeActivation": False, "productionActivation": False, "dbWrite": False, "approvalExecution": False, "workflowExecution": False, "pmScheduleCreation": False, "pmScheduleUpdate": False, "pmScheduleExecution": False, "pmTaskExecution": False, "automaticWorkOrderGeneration": False, "workOrderCreation": False, "workOrderUpdate": False, "workOrderAssignment": False, "workOrderApproval": False, "workOrderClosure": False, "stateTransitionExecution": False, "assetLifecycleWrite": False, "inventoryTransaction": False, "vendorContractExecution": False, "connectorExecution": False, "deviceConnection": False, "edgeRuntimeCall": False, "linkRuntimeCall": False, "oneAdapterIntroduced": False}
TRIGGERS = {"calendar_based", "runtime_hours_based", "event_count_based", "fault_count_based", "condition_based", "vendor_recommended", "contract_sla_based", "manual_review_based"}
GATES = {"Asset reference gate", "Location reference gate", "PM plan completeness gate", "Schedule completeness gate", "Checklist readiness gate", "Assignment readiness gate", "SLA readiness gate", "Evidence readiness gate", "Spare parts readiness gate", "Vendor / contract readiness gate", "Runtime input readiness gate", "Condition data freshness gate", "Work order generation policy gate", "UCDE evidence gate", "Customer approval gate, future optional"}
AIRPORT_MAPPINGS = {"Airport Assets & Topology", "Airport Fault Cases", "Airport Alarms & Events", "Airport Maintenance Work Orders", "Airport Evidence Investigation", "Airport HMI Locator Readiness", "Airport Deployment Readiness", "Airport Reports"}
CUSTOMER_FUNCTIONS = {"Work Order Management, auto + manual", "Asset Registry, full lifecycle tracking", "Preventive Maintenance Scheduler", "Spare Parts / Inventory Management", "Vendor / Contract Management", "Graphics HMI to locate Equipment", "Existing system onboarding", "Engineer commissioning diagnostics", "Remote overseas deployment", "Distributed independent installation"}
EDGE_DEPS = {"Runtime hours signal, future", "Event count signal, future", "Fault count signal, future", "Condition signal / health score, future", "Asset/location mapping preview", "Tag mapping and normalization", "HMI locator data foundation", "Engineer diagnostics"}
LINK_DEPS = {"Source-system health contract", "Delivery readiness contract", "Alarm/event/fault candidate references", "Asset/location reference contract", "Audit/evidence chain profile", "Delivery / ACK / retry / DLQ status", "Work-order trigger contract, future PM-generated work order", "Distributed topology contract"}
UCDE_DEPS = {"PM plan evidence", "PM task evidence", "PM checklist evidence", "PM completion evidence", "PM review evidence", "Work order evidence", "Closure evidence", "Audit trail", "Report evidence"}
ROADMAP = {"UMMS-R5A Local Freeze + Optional Tag Plan", "UMMS-R6 Spare Parts / Inventory Readiness", "UMMS-R7 Vendor / Contract / SLA Readiness", "UMMS-R8 UMMS + UCDE Evidence Closure Alignment", "UMMS-R9 UMMS + Airport HMI Locator Binding Readiness", "UMMS-R10 UMMS Stakeholder Review Package"}
ALLOWED_CHANGED_PREFIXES = ("AN_VANTARIS_ONE/projections/umms-preventive-maintenance-schedule-readiness.v1.json", "AN_VANTARIS_ONE/registries/umms-preventive-maintenance-schedule-readiness-registry.v1.json", "ONE_UMMS_R5_PREVENTIVE_MAINTENANCE_SCHEDULE_READINESS_REPORT.md", "scripts/validation/validate-one-umms-r5-preventive-maintenance-schedule-readiness.py", "AN_VANTARIS_ONE/tests/")
FORBIDDEN_CHANGED_PREFIXES = ("AN_VANTARIS_EDGE/", "AN_VANTARIS_LINK/", "AN_VANTARIS_Contracts/", "/Volumes/Work/VANTARIS_UFMS_FULL", "AN_VANTARIS_IBMS-backend/", "AN_VANTARIS_IBMS-frontend/", "database/", "migrations/")
FORBIDDEN_CLIENT_METHODS = (".post", ".put", ".patch", ".delete")
LEAKAGE_TERMS = ("/Users/", "/Volumes/Work/VANTARIS_UFMS_FULL", "customerAssetIdentifier")
REGRESSION_MARKERS = {
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
    if _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip() == "docs(one): add umms preventive maintenance readiness":
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
        ("UMMS-R5 projection artifact exists", PROJECTION.is_file() and not projection_error),
        ("UMMS-R5 registry exists", REGISTRY.is_file() and not registry_error),
        ("UMMS-R5 report exists", REPORT.is_file()),
    ])
    metadata = projection.get("metadata", {})
    scope = projection.get("r5ScopeSummary", {})
    checks.append(("Projection metadata contains platform = VANTARIS ONE", metadata.get("platform") == "VANTARIS ONE"))
    checks.append(("Projection metadata contains module = UMMS", metadata.get("module") == "UMMS"))
    checks.append(("Projection safety flags are correct", all(metadata.get(k) is v for k, v in SAFETY_EXPECTED.items() if k in metadata)))
    checks.append(("r5ScopeSummary confirms UMMS is generic and Airport-specific logic is not in core", scope.get("genericModuleScope") == "cross_industry_maintenance_management" and scope.get("airportSpecificLogicInCore") is False))
    checks.append(("r5ScopeSummary confirms pmExecutionEnabled is false", scope.get("pmExecutionEnabled") is False))
    checks.append(("r5ScopeSummary confirms automaticWorkOrderGenerationEnabled is false", scope.get("automaticWorkOrderGenerationEnabled") is False))
    plan = projection.get("pmPlanModel", {})
    schedule = projection.get("pmScheduleModel", {})
    task = projection.get("pmTaskModel", {})
    checklist = projection.get("pmChecklistModel", {})
    policy = projection.get("workOrderGenerationPolicyModel", {})
    checks.append(("pmPlanModel exists and activationAllowed is false", plan.get("activationAllowed") is False))
    checks.append(("pmPlanModel states no PM plan creation/update/approval/activation is implemented", "No PM plan creation, update, approval, or activation is implemented" in plan.get("statement", "")))
    checks.append(("pmScheduleModel exists and activationAllowed is false", schedule.get("activationAllowed") is False))
    checks.append(("pmScheduleModel states no PM schedule execution is implemented", "No PM schedule execution is implemented" in schedule.get("statement", "")))
    checks.append(("pmTaskModel exists and executionAllowedInR5 is false", task.get("executionAllowedInR5") is False))
    checks.append(("pmChecklistModel exists and executionAllowedInR5 is false", checklist.get("executionAllowedInR5") is False))
    checks.append(("pmTriggerTypeModel includes all required trigger types and executionAllowedInR5 is false", TRIGGERS.issubset({item.get("triggerType") for item in projection.get("pmTriggerTypeModel", [])}) and all(item.get("executionAllowedInR5") is False for item in projection.get("pmTriggerTypeModel", []))))
    checks.append(("calendarBasedPmReadiness exists and states no due-date calculation runtime is implemented", "No due-date calculation runtime is implemented" in projection.get("calendarBasedPmReadiness", {}).get("statement", "")))
    checks.append(("conditionBasedPmReadiness exists and states no EDGE/LINK runtime call is implemented", "No EDGE/LINK runtime call is implemented" in projection.get("conditionBasedPmReadiness", {}).get("statement", "")))
    checks.append(("workOrderGenerationPolicyModel exists and autoGenerationAllowed is false", policy.get("autoGenerationAllowed") is False))
    checks.append(("workOrderGenerationPolicyModel states no work order generation is implemented", "No work order generation is implemented" in policy.get("statement", "")))
    checks.append(("pmValidationGateModel includes all required validation gates", GATES.issubset({item.get("gateName") for item in projection.get("pmValidationGateModel", [])})))
    checks.append(("assetPmLinkageModel exists and states UMMS-R5 does not write canonical Asset Graph", "UMMS-R5 does not write canonical Asset Graph" in projection.get("assetPmLinkageModel", {}).get("statement", "")))
    checks.append(("airportToPmMapping includes all required mappings", AIRPORT_MAPPINGS.issubset({item.get("airportSource") for item in projection.get("airportToPmMapping", [])})))
    checks.append(("customerCoreFunctionR5Alignment includes all 10 customer core functions", CUSTOMER_FUNCTIONS.issubset({item.get("function") for item in projection.get("customerCoreFunctionR5Alignment", [])})))
    deps = projection.get("sharedFoundationDependencyMap", {})
    checks.append(("sharedFoundationDependencyMap includes required EDGE dependencies", _has_all(deps.get("edgeDependencies", []), EDGE_DEPS)))
    checks.append(("sharedFoundationDependencyMap includes required LINK dependencies", _has_all(deps.get("linkDependencies", []), LINK_DEPS)))
    checks.append(("sharedFoundationDependencyMap includes required UCDE dependencies", _has_all(deps.get("ucdeDependencies", []), UCDE_DEPS)))
    checks.append(("futureImplementationRoadmap includes UMMS-R5A through UMMS-R10", _has_all(projection.get("futureImplementationRoadmap", []), ROADMAP)))
    safety = projection.get("safetyPosture", {})
    checks.append(("safetyPosture confirms no runtime/production/DB/approval/workflow/PM/work order/asset/inventory/vendor/connector/device execution", all(safety.get(k) is v for k, v in SAFETY_EXPECTED.items()) and safety.get("customerIdentifierLeakage") is False and safety.get("localAbsolutePathLeakage") is False))
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
    checks.append(("Changes limited to UMMS-R5 projection scope", not disallowed and not forbidden))
    if disallowed:
        errors.append(f"changes outside UMMS-R5 scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    airport_client_text = AIRPORT_CLIENT.read_text(encoding="utf-8") if AIRPORT_CLIENT.exists() else ""
    checks.append(("No POST/PUT/PATCH/DELETE Airport or UMMS API client methods added", not any(method in airport_client_text for method in FORBIDDEN_CLIENT_METHODS)))
    checks.append(("No customer identifier leakage", not any(term in stakeholder_text for term in LEAKAGE_TERMS[2:])))
    checks.append(("No local absolute path leakage in stakeholder-facing artifacts", not any(term in stakeholder_text for term in LEAKAGE_TERMS[:2])))
    checks.append(("Projection JSON validation passes", not projection_error and metadata.get("projectionId") == "umms-preventive-maintenance-schedule-readiness.v1"))
    checks.append(("Registry JSON validation passes", not registry_error and registry.get("validationMarker") == PASS_MARKER))
    checks.append(("Report contains PASS marker", PASS_MARKER in report_text))
    for script, marker in REGRESSION_MARKERS.items():
        checks.append((f"{Path(script).name} frozen PASS marker remains available", _marker(marker)))

    package_route = _run(["python3", "scripts/validation/validate-one-package-route-enforcement.py"], env={"PYTHONPATH": "AN_VANTARIS_ONE"})
    checks.append(("Package route enforcement still passes", package_route.returncode == 0 and "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS" in package_route.stdout))
    boundary = _run(["python3", "scripts/validation/validate-one-boundaries.py"], env={"PYTHONPATH": "AN_VANTARIS_ONE"})
    checks.append(("Boundary baseline still passes", boundary.returncode == 0 and "ONE_BOUNDARY_BASELINE_PASS" in boundary.stdout))

    print("ONE_UMMS_R5_PREVENTIVE_MAINTENANCE_SCHEDULE_READINESS_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_UMMS_R5_PREVENTIVE_MAINTENANCE_SCHEDULE_READINESS_FAIL")
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
