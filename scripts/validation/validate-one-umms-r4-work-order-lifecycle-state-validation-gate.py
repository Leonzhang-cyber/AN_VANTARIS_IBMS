#!/usr/bin/env python3
"""Validate UMMS-R4 work order lifecycle state model + validation gate."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTION = ROOT / "AN_VANTARIS_ONE/projections/umms-work-order-lifecycle-state-validation-gate.v1.json"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-work-order-lifecycle-state-validation-gate-registry.v1.json"
REPORT = ROOT / "ONE_UMMS_R4_WORK_ORDER_LIFECYCLE_STATE_VALIDATION_GATE_REPORT.md"
AIRPORT_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts"
PASS_MARKER = "ONE_UMMS_R4_WORK_ORDER_LIFECYCLE_STATE_VALIDATION_GATE_PASS"

SAFETY_EXPECTED = {
    "readOnly": True,
    "runtimeActivation": False,
    "productionActivation": False,
    "dbWrite": False,
    "approvalExecution": False,
    "workflowExecution": False,
    "stateTransitionExecution": False,
    "workOrderCreation": False,
    "workOrderUpdate": False,
    "workOrderAssignment": False,
    "workOrderApproval": False,
    "workOrderClosure": False,
    "pmScheduleExecution": False,
    "assetLifecycleWrite": False,
    "inventoryTransaction": False,
    "vendorContractExecution": False,
    "connectorExecution": False,
    "deviceConnection": False,
    "edgeRuntimeCall": False,
    "linkRuntimeCall": False,
    "oneAdapterIntroduced": False,
}
STATES = {"candidate", "draft", "triaged", "assigned", "accepted", "in_progress", "pending_parts", "pending_vendor", "pending_customer", "on_hold", "resolved", "verification_pending", "verified", "closed", "cancelled", "rejected", "expired"}
TRANSITIONS = {"candidate_to_draft", "draft_to_triaged", "triaged_to_assigned", "assigned_to_accepted", "accepted_to_in_progress", "in_progress_to_pending_parts", "in_progress_to_pending_vendor", "in_progress_to_pending_customer", "in_progress_to_on_hold", "in_progress_to_resolved", "resolved_to_verification_pending", "verification_pending_to_verified", "verified_to_closed", "any_active_to_cancelled", "draft_to_rejected", "stale_draft_to_expired"}
GATES = {"Draft completeness gate", "Asset reference gate", "Location reference gate", "Assignment readiness gate", "SLA readiness gate", "Evidence readiness gate", "HMI locator readiness gate", "PM linkage gate", "Spare parts readiness gate", "Vendor / contract readiness gate", "Safety / compliance gate", "UCDE evidence gate", "Duplicate work order gate", "Conflicting open work order gate", "Closure evidence gate"}
ROLE_GATES = {"operator_review", "engineer_acceptance", "supervisor_verification", "admin_override_future", "vendor_acknowledgement_future", "customer_approval_future"}
EVIDENCE_TYPES = {"faultEvidence", "assetEvidence", "locationEvidence", "hmiLocatorEvidence", "assignmentEvidence", "workBeforeEvidence", "workAfterEvidence", "partsEvidence", "vendorEvidence", "customerCommunicationEvidence", "resolutionEvidence", "verificationEvidence", "closureEvidence", "auditTrailEvidence"}
SLA_GATES = {"responseTimeGate", "acceptanceTimeGate", "resolutionTimeGate", "verificationTimeGate", "closureTimeGate", "vendorSlaGate", "contractSlaGate", "escalationGate"}
AIRPORT_MAPPINGS = {"Airport Fault Cases", "Airport Alarms & Events", "Airport Maintenance Work Orders", "Airport Evidence Investigation", "Airport Assets & Topology", "Airport HMI Locator Readiness", "Airport Reports"}
CUSTOMER_FUNCTIONS = {"Work Order Management, auto + manual", "Asset Registry, full lifecycle tracking", "Preventive Maintenance Scheduler", "Spare Parts / Inventory Management", "Vendor / Contract Management", "Graphics HMI to locate Equipment", "Existing system onboarding", "Engineer commissioning diagnostics", "Remote overseas deployment", "Distributed independent installation"}
EDGE_DEPENDENCIES = {"Asset/location mapping preview", "Tag mapping and normalization", "HMI locator data foundation", "Engineer diagnostics", "Runtime status signals, future", "Condition signals for PM, future"}
LINK_DEPENDENCIES = {"Work-order trigger contract", "Alarm/event/fault candidate references", "Asset/location reference contract", "HMI drawing/symbol reference fields", "Audit/evidence chain profile", "Source-system health contract", "Delivery / ACK / retry / DLQ status"}
UCDE_DEPENDENCIES = {"EvidenceRecord", "WorkOrderEvidence", "Draft review evidence", "State transition evidence", "Closure evidence", "Verification evidence", "Audit trail", "Handoff package", "Report evidence"}
ROADMAP = {"UMMS-R4A Local Freeze + Optional Tag Plan", "UMMS-R5 Preventive Maintenance Schedule Readiness", "UMMS-R6 Spare Parts / Inventory Readiness", "UMMS-R7 Vendor / Contract / SLA Readiness", "UMMS-R8 UMMS + UCDE Evidence Closure Alignment", "UMMS-R9 UMMS + Airport HMI Locator Binding Readiness", "UMMS-R10 UMMS Stakeholder Review Package"}
ALLOWED_CHANGED_PREFIXES = (
    "AN_VANTARIS_ONE/projections/umms-work-order-lifecycle-state-validation-gate.v1.json",
    "AN_VANTARIS_ONE/registries/umms-work-order-lifecycle-state-validation-gate-registry.v1.json",
    "ONE_UMMS_R4_WORK_ORDER_LIFECYCLE_STATE_VALIDATION_GATE_REPORT.md",
    "scripts/validation/validate-one-umms-r4-work-order-lifecycle-state-validation-gate.py",
    "AN_VANTARIS_ONE/tests/",
)
FORBIDDEN_CHANGED_PREFIXES = ("AN_VANTARIS_EDGE/", "AN_VANTARIS_LINK/", "AN_VANTARIS_Contracts/", "/Volumes/Work/VANTARIS_UFMS_FULL", "AN_VANTARIS_IBMS-backend/", "AN_VANTARIS_IBMS-frontend/", "database/", "migrations/")
FORBIDDEN_CLIENT_METHODS = (".post", ".put", ".patch", ".delete")
LEAKAGE_TERMS = ("/Users/", "/Volumes/Work/VANTARIS_UFMS_FULL", "customerAssetIdentifier")
REGRESSION_MARKERS = {
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


def _load_json(path: Path) -> tuple[dict, str]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), ""
    except Exception as exc:
        return {}, str(exc)


def _changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (["git", "diff", "--name-only", "HEAD"], ["git", "diff", "--cached", "--name-only"], ["git", "ls-files", "--others", "--exclude-standard"]):
        paths.update(line for line in _run(command).stdout.splitlines() if line)
    last_subject = _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip()
    if last_subject == "docs(one): add umms work order lifecycle validation gate":
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _json_valid(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except Exception:
        return False


def _frozen_marker_present(marker: str) -> bool:
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

    checks.append(("UMMS-R4 projection artifact exists", PROJECTION.is_file() and not projection_error))
    checks.append(("UMMS-R4 registry exists", REGISTRY.is_file() and not registry_error))
    checks.append(("UMMS-R4 report exists", REPORT.is_file()))
    metadata = projection.get("metadata", {})
    scope = projection.get("r4ScopeSummary", {})
    checks.append(("Projection metadata contains platform = VANTARIS ONE", metadata.get("platform") == "VANTARIS ONE"))
    checks.append(("Projection metadata contains module = UMMS", metadata.get("module") == "UMMS"))
    checks.append(("Projection safety flags are correct", all(metadata.get(k) is v for k, v in SAFETY_EXPECTED.items() if k in metadata)))
    checks.append(("r4ScopeSummary confirms UMMS is generic and Airport-specific logic is not in core", scope.get("genericModuleScope") == "cross_industry_maintenance_management" and scope.get("airportSpecificLogicInCore") is False))
    checks.append(("r4ScopeSummary confirms stateTransitionEnabled is false", scope.get("stateTransitionEnabled") is False and scope.get("validationGateExecutionEnabled") is False))
    checks.append(("workOrderLifecycleStateModel includes all required lifecycle states", STATES.issubset({item.get("state") for item in projection.get("workOrderLifecycleStateModel", [])})))
    checks.append(("workOrderLifecycleStateModel sets executionAllowedInR4 false for every state", all(item.get("executionAllowedInR4") is False for item in projection.get("workOrderLifecycleStateModel", []))))
    checks.append(("transitionValidationModel includes all required transition groups", TRANSITIONS.issubset({item.get("transitionId") for item in projection.get("transitionValidationModel", [])})))
    checks.append(("transitionValidationModel sets executionAllowedInR4 false for every transition", all(item.get("executionAllowedInR4") is False for item in projection.get("transitionValidationModel", []))))
    checks.append(("validationGateModel includes all required gate categories", GATES.issubset({item.get("gateName") for item in projection.get("validationGateModel", [])})))
    checks.append(("roleGateModel includes all required role gates and executionAllowedInR4 false", ROLE_GATES.issubset({item.get("roleGateId") for item in projection.get("roleGateModel", [])}) and all(item.get("executionAllowedInR4") is False for item in projection.get("roleGateModel", []))))
    checks.append(("evidenceGateModel includes all required evidence types and executionAllowedInR4 false", EVIDENCE_TYPES.issubset({item.get("evidenceType") for item in projection.get("evidenceGateModel", [])}) and all(item.get("executionAllowedInR4") is False for item in projection.get("evidenceGateModel", []))))
    checks.append(("slaGateModel includes all required SLA gates and executionAllowedInR4 false", SLA_GATES.issubset({item.get("slaGateId") for item in projection.get("slaGateModel", [])}) and all(item.get("executionAllowedInR4") is False for item in projection.get("slaGateModel", []))))
    checks.append(("airportToLifecycleMapping includes all required mappings", AIRPORT_MAPPINGS.issubset({item.get("airportSource") for item in projection.get("airportToLifecycleMapping", [])})))
    checks.append(("customerCoreFunctionR4Alignment includes all 10 customer core functions", CUSTOMER_FUNCTIONS.issubset({item.get("function") for item in projection.get("customerCoreFunctionR4Alignment", [])})))
    dependencies = projection.get("sharedFoundationDependencyMap", {})
    checks.append(("sharedFoundationDependencyMap includes required EDGE dependencies", _has_all(dependencies.get("edgeDependencies", []), EDGE_DEPENDENCIES)))
    checks.append(("sharedFoundationDependencyMap includes required LINK dependencies", _has_all(dependencies.get("linkDependencies", []), LINK_DEPENDENCIES)))
    checks.append(("sharedFoundationDependencyMap includes required UCDE dependencies", _has_all(dependencies.get("ucdeDependencies", []), UCDE_DEPENDENCIES)))
    checks.append(("futureImplementationRoadmap includes UMMS-R4A through UMMS-R10", _has_all(projection.get("futureImplementationRoadmap", []), ROADMAP)))
    safety = projection.get("safetyPosture", {})
    checks.append(("safetyPosture confirms no runtime/production/DB/approval/workflow/state transition/work order/PM/asset/inventory/vendor/connector/device execution", all(safety.get(k) is v for k, v in SAFETY_EXPECTED.items()) and safety.get("customerIdentifierLeakage") is False and safety.get("localAbsolutePathLeakage") is False))
    checks.append(("No ONE Adapter introduced", metadata.get("oneAdapterIntroduced") is False and safety.get("oneAdapterIntroduced") is False and "ONE Adapter introduced: no" in report_text))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("No AN_VANTARIS_EDGE files modified", not any(path.startswith("AN_VANTARIS_EDGE/") for path in changed)))
    checks.append(("No AN_VANTARIS_LINK files modified", not any(path.startswith("AN_VANTARIS_LINK/") for path in changed)))
    checks.append(("No AN_VANTARIS_Contracts files modified", not any(path.startswith("AN_VANTARIS_Contracts/") for path in changed)))
    checks.append(("No UFMS source modified", not any("VANTARIS_UFMS_FULL" in path for path in changed)))
    checks.append(("No backend API behavior modified unless explicitly allowed and documented", not any(path.startswith("AN_VANTARIS_IBMS-backend/") for path in changed)))
    checks.append(("No frontend behavior modified unless explicitly allowed and documented", not any(path.startswith("AN_VANTARIS_IBMS-frontend/") for path in changed)))
    checks.append(("Changes limited to UMMS-R4 projection scope", not disallowed and not forbidden))
    if disallowed:
        errors.append(f"changes outside UMMS-R4 scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    airport_client_text = AIRPORT_CLIENT.read_text(encoding="utf-8") if AIRPORT_CLIENT.exists() else ""
    checks.append(("No POST/PUT/PATCH/DELETE Airport or UMMS API client methods added", not any(method in airport_client_text for method in FORBIDDEN_CLIENT_METHODS)))
    checks.append(("No customer identifier leakage", not any(term in stakeholder_text for term in LEAKAGE_TERMS[2:])))
    checks.append(("No local absolute path leakage in stakeholder-facing artifacts", not any(term in stakeholder_text for term in LEAKAGE_TERMS[:2])))
    checks.append(("Projection JSON validation passes", not projection_error and metadata.get("projectionId") == "umms-work-order-lifecycle-state-validation-gate.v1"))
    checks.append(("Registry JSON validation passes", not registry_error and registry.get("validationMarker") == PASS_MARKER))
    checks.append(("Report contains PASS marker", PASS_MARKER in report_text))

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

    print("ONE_UMMS_R4_WORK_ORDER_LIFECYCLE_STATE_VALIDATION_GATE_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_UMMS_R4_WORK_ORDER_LIFECYCLE_STATE_VALIDATION_GATE_FAIL")
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
