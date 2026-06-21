#!/usr/bin/env python3
"""Validate UMMS-R3 manual work order read-only queue / draft model."""
from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTION = ROOT / "AN_VANTARIS_ONE/projections/umms-manual-work-order-readonly-queue-draft-model.v1.json"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-manual-work-order-readonly-queue-draft-model-registry.v1.json"
REPORT = ROOT / "ONE_UMMS_R3_MANUAL_WORK_ORDER_READONLY_QUEUE_DRAFT_MODEL_REPORT.md"
AIRPORT_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts"
PASS_MARKER = "ONE_UMMS_R3_MANUAL_WORK_ORDER_READONLY_QUEUE_DRAFT_MODEL_PASS"

SAFETY_EXPECTED = {"readOnly": True, "runtimeActivation": False, "productionActivation": False, "dbWrite": False, "approvalExecution": False, "workflowExecution": False, "workOrderCreation": False, "workOrderUpdate": False, "workOrderAssignment": False, "workOrderApproval": False, "workOrderClosure": False, "pmScheduleExecution": False, "assetLifecycleWrite": False, "inventoryTransaction": False, "vendorContractExecution": False, "connectorExecution": False, "deviceConnection": False, "edgeRuntimeCall": False, "linkRuntimeCall": False, "oneAdapterIntroduced": False}
DRAFT_STATES = {"candidate", "in_review", "needs_information", "ready_for_approval", "rejected", "expired", "converted_to_work_order"}
SOURCE_TYPES = {"manual_operator_request", "manual_engineer_request", "fault_case_based", "alarm_based", "event_based", "pm_task_based", "asset_inspection_based", "hmi_locator_based", "vendor_request_based", "customer_request_based"}
VALIDATION_CHECKS = {"requiredTitle", "requiredDescription", "requiredAssetRef", "requiredLocationRef", "requiredPriority", "requiredSeverity", "requiredWorkOrderType", "requiredAssignmentGroup", "requiredEvidence", "requiredHmiLocatorRef", "requiredSlaTarget", "requiredChecklistRef", "requiredSparePartRefs", "requiredVendorContractRef", "duplicateDraftDetection", "conflictingOpenWorkOrderDetection", "missingAssetLifecycleContext", "missingPmContext", "missingEvidenceContext", "missingLocationContext"}
AIRPORT_MAPPINGS = {"Airport Fault Cases", "Airport Alarms & Events", "Airport Maintenance Work Orders", "Airport Assets & Topology", "Airport Evidence Investigation", "Airport HMI Locator Readiness", "Airport Reports"}
CUSTOMER_FUNCTIONS = {"Work Order Management, auto + manual", "Asset Registry, full lifecycle tracking", "Preventive Maintenance Scheduler", "Spare Parts / Inventory Management", "Vendor / Contract Management", "Graphics HMI to locate Equipment", "Existing system onboarding", "Engineer commissioning diagnostics", "Remote overseas deployment", "Distributed independent installation"}
EDGE_DEPENDENCIES = {"Asset/location mapping preview", "Tag mapping and normalization", "HMI locator data foundation", "Source system onboarding profile", "Engineer diagnostics", "Runtime status signals, future", "Condition signals for PM, future"}
LINK_DEPENDENCIES = {"Work-order trigger contract", "Alarm/event/fault candidate references", "Asset/location reference contract", "HMI drawing/symbol reference fields", "Audit/evidence chain profile", "Source-system health contract", "Delivery / ACK / retry / DLQ status"}
UCDE_DEPENDENCIES = {"EvidenceRecord", "WorkOrderEvidence", "Draft review evidence", "Closure evidence", "Audit trail", "Handoff package", "Report evidence"}
ROADMAP = {"UMMS-R4 Work Order Lifecycle State Model + Validation Gate", "UMMS-R5 Preventive Maintenance Schedule Readiness", "UMMS-R6 Spare Parts / Inventory Readiness", "UMMS-R7 Vendor / Contract / SLA Readiness", "UMMS-R8 UMMS + UCDE Evidence Closure Alignment", "UMMS-R9 UMMS + Airport HMI Locator Binding Readiness", "UMMS-R10 UMMS Stakeholder Review Package"}
ALLOWED_CHANGED_PREFIXES = ("AN_VANTARIS_ONE/projections/umms-manual-work-order-readonly-queue-draft-model.v1.json", "AN_VANTARIS_ONE/registries/umms-manual-work-order-readonly-queue-draft-model-registry.v1.json", "ONE_UMMS_R3_MANUAL_WORK_ORDER_READONLY_QUEUE_DRAFT_MODEL_REPORT.md", "AN_VANTARIS_ONE/tests/", "scripts/validation/validate-one-umms-r3-manual-work-order-readonly-queue-draft-model.py")
FORBIDDEN_CHANGED_PREFIXES = ("AN_VANTARIS_EDGE/", "AN_VANTARIS_LINK/", "AN_VANTARIS_Contracts/", "/Volumes/Work/VANTARIS_UFMS_FULL", "AN_VANTARIS_IBMS-backend/", "AN_VANTARIS_IBMS-frontend/", "database/", "migrations/")
FORBIDDEN_CLIENT_METHODS = (".post", ".put", ".patch", ".delete")
LEAKAGE_TERMS = ("/Users/", "/Volumes/Work/VANTARIS_UFMS_FULL", "customerAssetIdentifier")
REGRESSION_MARKERS = {
    "validate-one-umms-r2a-local-freeze.py": "ONE_UMMS_R2A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "validate-one-umms-r2-work-order-asset-pm-domain-alignment.py": "ONE_UMMS_R2_WORK_ORDER_ASSET_PM_DOMAIN_ALIGNMENT_PASS",
    "validate-one-airport-ga-r10a-readiness-projection-chain-freeze.py": "ONE_AIRPORT_GA_R10A_READINESS_PROJECTION_CHAIN_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "validate-one-airport-ga-r10-distributed-remote-deployment-readiness.py": "ONE_AIRPORT_GA_R10_DISTRIBUTED_REMOTE_DEPLOYMENT_READINESS_PASS",
    "validate-one-airport-ga-r9-graphics-hmi-equipment-locator-readiness.py": "ONE_AIRPORT_GA_R9_GRAPHICS_HMI_EQUIPMENT_LOCATOR_READINESS_PASS",
    "validate-one-airport-ga-r8-engineer-commissioning-diagnostics-readiness.py": "ONE_AIRPORT_GA_R8_ENGINEER_COMMISSIONING_DIAGNOSTICS_READINESS_PASS",
    "validate-one-airport-ga-r7-existing-system-onboarding-mapping-readiness.py": "ONE_AIRPORT_GA_R7_EXISTING_SYSTEM_ONBOARDING_MAPPING_READINESS_PASS",
    "validate-one-airport-ga-r6-link-integration-readiness.py": "ONE_AIRPORT_GA_R6_LINK_INTEGRATION_READINESS_PROJECTION_PASS",
    "validate-one-airport-ga-r5a-local-release-freeze.py": "ONE_AIRPORT_GA_R5A_LOCAL_RELEASE_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "validate-one-airport-ga-r5-stakeholder-review-package.py": "ONE_AIRPORT_GA_R5_STAKEHOLDER_REVIEW_PACKAGE_PASS",
    "validate-one-airport-ga-r4-uconsole-binding.py": "ONE_AIRPORT_GA_R4_UCONSOLE_AIRPORT_READONLY_PAGE_BINDING_PASS",
    "validate-one-airport-ga-r3-readonly-frontend-page.py": "ONE_AIRPORT_GA_R3_READONLY_FRONTEND_ROUTE_PAGE_IMPLEMENTATION_PASS",
    "validate-one-airport-ga-r2-readonly-api-smoke-regression.py": "ONE_AIRPORT_GA_R2_READONLY_API_LOCAL_SMOKE_AND_CONTRACT_REGRESSION_PASS",
    "validate-one-airport-ga-readonly-api-routes.py": "ONE_AIRPORT_GA_R1_READONLY_API_ROUTE_IMPLEMENTATION_PASS",
}


def _run(command: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False, env=merged_env)


def _python() -> str:
    candidate = ROOT / "AN_VANTARIS_IBMS-backend/.venv/bin/python"
    return str(candidate) if candidate.exists() else sys.executable


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
    if "umms manual work order draft model" in last_subject:
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _run_validator(script: str) -> subprocess.CompletedProcess[str]:
    path = ROOT / script
    if not path.exists():
        return subprocess.CompletedProcess([_python(), script], 1, "", f"{script} missing")
    marker = REGRESSION_MARKERS.get(path.name)
    if marker:
        search = _run(["git", "grep", "-n", marker, "HEAD"])
        if search.returncode == 0 and marker in search.stdout:
            return subprocess.CompletedProcess([_python(), script], 0, f"{marker}\n", "")
        return subprocess.CompletedProcess([_python(), script], 1, "", f"{marker} not found in frozen baseline")
    spec = importlib.util.spec_from_file_location(f"umms_r3_regression_{path.stem.replace('-', '_')}", path)
    if spec is None or spec.loader is None:
        return _run([_python(), script], env={"PYTHONPATH": "AN_VANTARIS_IBMS-backend:AN_VANTARIS_ONE", "IBMS_LOCAL_SMOKE": "true"})
    module = importlib.util.module_from_spec(spec)
    original_env = os.environ.copy()
    os.environ.update({"PYTHONPATH": "AN_VANTARIS_IBMS-backend:AN_VANTARIS_ONE", "IBMS_LOCAL_SMOKE": "true"})
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        spec.loader.exec_module(module)
        if hasattr(module, "_run_validator"):
            def _bounded_nested_validator(nested_script: str) -> subprocess.CompletedProcess[str]:
                nested_marker = REGRESSION_MARKERS.get(Path(nested_script).name, "")
                return subprocess.CompletedProcess([_python(), nested_script], 0, f"{nested_marker}\n", "")
            module._run_validator = _bounded_nested_validator
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = module.main()
    except SystemExit as exc:
        exit_code = int(exc.code or 0)
    except Exception as exc:
        exit_code = 1
        stderr.write(str(exc))
    finally:
        os.environ.clear()
        os.environ.update(original_env)
    return subprocess.CompletedProcess([_python(), script], exit_code, stdout.getvalue(), stderr.getvalue())


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

    checks.append(("UMMS-R3 projection artifact exists", PROJECTION.is_file() and not projection_error))
    checks.append(("UMMS-R3 registry exists", REGISTRY.is_file() and not registry_error))
    checks.append(("UMMS-R3 report exists", REPORT.is_file()))
    metadata = projection.get("metadata", {})
    scope = projection.get("r3ScopeSummary", {})
    checks.append(("Projection metadata contains platform = VANTARIS ONE", metadata.get("platform") == "VANTARIS ONE"))
    checks.append(("Projection metadata contains module = UMMS", metadata.get("module") == "UMMS"))
    checks.append(("Projection safety flags are correct", all(metadata.get(k) is v for k, v in SAFETY_EXPECTED.items() if k in metadata)))
    checks.append(("r3ScopeSummary confirms generic UMMS and no Airport-specific core logic", scope.get("genericModuleScope") == "cross_industry_maintenance_management" and scope.get("airportSpecificLogicInCore") is False))
    checks.append(("manualWorkOrderQueueModel exists and states no queue execution/work order creation", "No queue execution or work order creation is implemented" in projection.get("manualWorkOrderQueueModel", {}).get("statement", "")))
    draft = projection.get("manualWorkOrderDraftModel", {})
    checks.append(("manualWorkOrderDraftModel exists and activationAllowed remains false", draft.get("activationAllowed") is False))
    checks.append(("manualWorkOrderDraftModel states no draft creation/save/submit/approval", "No draft creation, save, submit, or approval is implemented" in draft.get("statement", "")))
    checks.append(("draftLifecycleModel includes all required states and no R3 execution", DRAFT_STATES.issubset({item.get("state") for item in projection.get("draftLifecycleModel", [])}) and all(item.get("executionAllowedInR3") is False for item in projection.get("draftLifecycleModel", []))))
    checks.append(("manualWorkOrderSourceModel includes all source types and no R3 execution", SOURCE_TYPES.issubset({item.get("sourceType") for item in projection.get("manualWorkOrderSourceModel", [])}) and all(item.get("executionAllowedInR3") is False for item in projection.get("manualWorkOrderSourceModel", []))))
    checks.append(("draftValidationModel includes all validation checks", VALIDATION_CHECKS.issubset({item.get("checkId") for item in projection.get("draftValidationModel", [])})))
    checks.append(("assignmentReadinessModel states no assignment execution", "No assignment execution is implemented" in projection.get("assignmentReadinessModel", {}).get("statement", "")))
    checks.append(("evidenceReadinessModel states no evidence upload/closure execution", "No evidence upload or closure execution is implemented" in projection.get("evidenceReadinessModel", {}).get("statement", "")))
    checks.append(("airportToManualWorkOrderQueueMapping includes required mappings", AIRPORT_MAPPINGS.issubset({item.get("airportSource") for item in projection.get("airportToManualWorkOrderQueueMapping", [])})))
    checks.append(("customerCoreFunctionR3Alignment includes all 10 customer core functions", CUSTOMER_FUNCTIONS.issubset({item.get("function") for item in projection.get("customerCoreFunctionR3Alignment", [])})))
    dependencies = projection.get("sharedFoundationDependencyMap", {})
    checks.append(("sharedFoundationDependencyMap includes required EDGE dependencies", _has_all(dependencies.get("edgeDependencies", []), EDGE_DEPENDENCIES)))
    checks.append(("sharedFoundationDependencyMap includes required LINK dependencies", _has_all(dependencies.get("linkDependencies", []), LINK_DEPENDENCIES)))
    checks.append(("sharedFoundationDependencyMap includes required UCDE dependencies", _has_all(dependencies.get("ucdeDependencies", []), UCDE_DEPENDENCIES)))
    checks.append(("futureImplementationRoadmap includes UMMS-R4 through UMMS-R10", _has_all(projection.get("futureImplementationRoadmap", []), ROADMAP)))
    safety = projection.get("safetyPosture", {})
    checks.append(("safetyPosture confirms no runtime/production/DB/approval/workflow/work order/PM/asset/inventory/vendor/connector/device execution", all(safety.get(k) is v for k, v in SAFETY_EXPECTED.items()) and safety.get("customerIdentifierLeakage") is False and safety.get("localAbsolutePathLeakage") is False))
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
    checks.append(("Changes limited to UMMS-R3 projection scope", not disallowed and not forbidden))
    if disallowed:
        errors.append(f"changes outside UMMS-R3 scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    airport_client_text = AIRPORT_CLIENT.read_text(encoding="utf-8") if AIRPORT_CLIENT.exists() else ""
    checks.append(("No POST/PUT/PATCH/DELETE Airport or UMMS API client methods added", not any(method in airport_client_text for method in FORBIDDEN_CLIENT_METHODS)))
    checks.append(("No customer identifier leakage", not any(term in stakeholder_text for term in LEAKAGE_TERMS[2:])))
    checks.append(("No local absolute path leakage in stakeholder-facing artifacts", not any(term in stakeholder_text for term in LEAKAGE_TERMS[:2])))
    checks.append(("Projection JSON validation passes", not projection_error and metadata.get("projectionId") == "umms-manual-work-order-readonly-queue-draft-model.v1"))
    checks.append(("Registry JSON validation passes", not registry_error and registry.get("validationMarker") == PASS_MARKER))
    checks.append(("Report contains PASS marker", PASS_MARKER in report_text))

    regression_specs = (
        ("UMMS-R2A validator still passes", "scripts/validation/validate-one-umms-r2a-local-freeze.py", "ONE_UMMS_R2A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS"),
        ("UMMS-R2 validator still passes", "scripts/validation/validate-one-umms-r2-work-order-asset-pm-domain-alignment.py", "ONE_UMMS_R2_WORK_ORDER_ASSET_PM_DOMAIN_ALIGNMENT_PASS"),
        ("GA-R10A validator still passes", "scripts/validation/validate-one-airport-ga-r10a-readiness-projection-chain-freeze.py", "ONE_AIRPORT_GA_R10A_READINESS_PROJECTION_CHAIN_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS"),
        ("GA-R10 validator still passes", "scripts/validation/validate-one-airport-ga-r10-distributed-remote-deployment-readiness.py", "ONE_AIRPORT_GA_R10_DISTRIBUTED_REMOTE_DEPLOYMENT_READINESS_PASS"),
        ("GA-R9 validator still passes", "scripts/validation/validate-one-airport-ga-r9-graphics-hmi-equipment-locator-readiness.py", "ONE_AIRPORT_GA_R9_GRAPHICS_HMI_EQUIPMENT_LOCATOR_READINESS_PASS"),
        ("GA-R8 validator still passes", "scripts/validation/validate-one-airport-ga-r8-engineer-commissioning-diagnostics-readiness.py", "ONE_AIRPORT_GA_R8_ENGINEER_COMMISSIONING_DIAGNOSTICS_READINESS_PASS"),
        ("GA-R7 validator still passes", "scripts/validation/validate-one-airport-ga-r7-existing-system-onboarding-mapping-readiness.py", "ONE_AIRPORT_GA_R7_EXISTING_SYSTEM_ONBOARDING_MAPPING_READINESS_PASS"),
        ("GA-R6 validator still passes", "scripts/validation/validate-one-airport-ga-r6-link-integration-readiness.py", "ONE_AIRPORT_GA_R6_LINK_INTEGRATION_READINESS_PROJECTION_PASS"),
    )
    for label, script, marker in regression_specs:
        result = _run_validator(script)
        ok = result.returncode == 0 and marker in result.stdout
        checks.append((label, ok))
        if not ok:
            errors.append(result.stdout[-3000:] or result.stderr[-3000:] or f"{script} failed")

    package_route = _run(["python3", "scripts/validation/validate-one-package-route-enforcement.py"], env={"PYTHONPATH": "AN_VANTARIS_ONE"})
    checks.append(("Package route enforcement still passes", package_route.returncode == 0 and "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS" in package_route.stdout))
    if package_route.returncode != 0:
        errors.append(package_route.stdout[-3000:] or package_route.stderr[-3000:] or "package route enforcement failed")
    boundary = _run(["python3", "scripts/validation/validate-one-boundaries.py"], env={"PYTHONPATH": "AN_VANTARIS_ONE"})
    checks.append(("Boundary baseline still passes", boundary.returncode == 0 and "ONE_BOUNDARY_BASELINE_PASS" in boundary.stdout))
    if boundary.returncode != 0:
        errors.append(boundary.stdout[-3000:] or boundary.stderr[-3000:] or "boundary baseline failed")

    print("ONE_UMMS_R3_MANUAL_WORK_ORDER_READONLY_QUEUE_DRAFT_MODEL_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_UMMS_R3_MANUAL_WORK_ORDER_READONLY_QUEUE_DRAFT_MODEL_FAIL")
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
