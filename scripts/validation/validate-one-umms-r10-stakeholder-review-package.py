#!/usr/bin/env python3
"""Validate UMMS-R10 stakeholder review package."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE.md"
REPORT = ROOT / "ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE_REPORT.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-stakeholder-review-package.v1.json"
AIRPORT_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts"
PASS_MARKER = "ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE_PASS"

UMMS_MILESTONES = tuple(f"UMMS-R{i}" for i in range(2, 10))
PUBLISHED_UMMS_TAGS = (
    "umms-r2-work-asset-pm-domain-alignment-local-freeze-20260621",
    "umms-r3-manual-work-order-draft-model-local-freeze-20260621",
    "umms-r4-work-order-lifecycle-validation-gate-local-freeze-20260621",
    "umms-r5-preventive-maintenance-schedule-readiness-local-freeze-20260621",
    "umms-r6-spare-parts-inventory-readiness-local-freeze-20260621",
    "umms-r7-vendor-contract-sla-readiness-local-freeze-20260621",
    "umms-r8-ucde-evidence-closure-alignment-local-freeze-20260621",
    "umms-r9-airport-hmi-locator-binding-readiness-local-freeze-20260621",
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
DOMAINS = (
    "Work Order",
    "Work Order Draft",
    "Work Order Lifecycle",
    "Preventive Maintenance",
    "Asset Linkage",
    "Spare Parts",
    "Inventory",
    "Vendor",
    "Contract",
    "SLA",
    "UCDE Evidence",
    "HMI Locator",
    "Reports / Handoff",
)
EDGE_DEPENDENCIES = (
    "Connector matrix",
    "Existing system onboarding profile",
    "Tag mapping / normalization",
    "Asset/location mapping",
    "HMI locator data foundation",
    "Engineer diagnostics",
    "Runtime health / condition signals",
    "Offline deployment / support bundle",
)
LINK_DEPENDENCIES = (
    "Source-system health contract",
    "Delivery readiness contract",
    "Work-order trigger contract",
    "Asset/location reference contract",
    "HMI drawing/symbol reference fields",
    "Audit/evidence chain profile",
    "Delivery / ACK / retry / DLQ status",
    "Distributed topology contract",
    "Remote support bundle contract",
)
UCDE_DEPENDENCIES = (
    "EvidenceRecord",
    "WorkOrderEvidence",
    "PmEvidence",
    "InventoryEvidence",
    "VendorContractEvidence",
    "SlaEvidence",
    "ClosureEvidence",
    "VerificationEvidence",
    "AuditTrail",
    "HandoffPackage",
    "ReportEvidence",
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
LIMITATION_TERMS = (
    "No production activation",
    "No runtime activation",
    "No DB write",
    "No workflow execution",
    "No real work order creation/update/assignment/approval/closure",
    "No PM execution or automatic work order generation",
    "No inventory transaction or stock mutation",
    "No vendor transaction / contract execution / SLA enforcement",
    "No evidence upload / audit write / closure execution",
    "No HMI runtime / drawing upload / device connection",
    "No EDGE/LINK runtime integration",
    "No ONE Adapter",
)
ALLOWED_CHANGED_PREFIXES = (
    "ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE.md",
    "AN_VANTARIS_ONE/registries/umms-stakeholder-review-package.v1.json",
    "ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE_REPORT.md",
    "scripts/validation/validate-one-umms-r10-stakeholder-review-package.py",
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
LEAKAGE_TERMS = ("customerAssetIdentifier", "customer identifier", "/Users/", "/Volumes/Work/VANTARIS_UFMS_FULL")
REGRESSION_COMMANDS = (
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
    if _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip() == "docs(one): add umms stakeholder review package":
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
    package_text = PACKAGE.read_text(encoding="utf-8") if PACKAGE.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    combined = "\n".join([package_text, report_text, registry_text])
    lower_combined = combined.lower()

    checks.append(("UMMS-R10 stakeholder review package exists", PACKAGE.is_file()))
    checks.append(("UMMS-R10 report exists", REPORT.is_file()))
    checks.append(("Optional registry exists", REGISTRY.is_file()))
    checks.append(("Review package references UMMS-R2 through UMMS-R9", all(milestone in package_text for milestone in UMMS_MILESTONES)))
    checks.append(("Review package references all published UMMS tags from R2A through R9A", all(tag in package_text for tag in PUBLISHED_UMMS_TAGS)))
    checks.append(("Customer core function coverage includes all 10 customer functions", all(function in package_text for function in CUSTOMER_FUNCTIONS)))
    checks.append(("Domain coverage matrix includes required domains", all(domain in package_text for domain in DOMAINS)))
    checks.append(("Shared foundation dependency summary includes EDGE dependencies", all(dep in package_text for dep in EDGE_DEPENDENCIES)))
    checks.append(("Shared foundation dependency summary includes LINK dependencies", all(dep in package_text for dep in LINK_DEPENDENCIES)))
    checks.append(("Shared foundation dependency summary includes UCDE dependencies", all(dep in package_text for dep in UCDE_DEPENDENCIES)))
    checks.append(("Safety matrix includes all required flags", all(term in package_text for term in SAFETY_TERMS)))
    checks.append(("Known limitations include all no-runtime limitations", all(term in package_text for term in LIMITATION_TERMS)))
    checks.append(("Roadmap includes UMMS-R10A and future implementation phases", "UMMS-R10A Local Freeze + Optional Tag Plan" in package_text and "UMMS read-only API implementation, future" in package_text and "UMMS read-only frontend implementation, future" in package_text))
    checks.append(("No claim that production activation is enabled", "This is not production activation." in package_text and "production activation enabled" not in lower_combined))
    checks.append(("No claim that runtime activation is enabled", "This is not runtime activation." in package_text and "runtime activation enabled" not in lower_combined))
    checks.append(("No claim that DB write is enabled", "This is not DB write enablement." in package_text and "db write enabled" not in lower_combined))
    checks.append(("No claim that workflow execution is enabled", "This is not workflow execution." in package_text and "workflow execution enabled" not in lower_combined))
    checks.append(("No claim that EDGE/LINK runtime integration is implemented", "This is not EDGE/LINK runtime integration." in package_text and "edge/link runtime integration implemented" not in lower_combined and "edge/link runtime integration enabled" not in lower_combined))
    checks.append(("No ONE Adapter introduction", "oneAdapterIntroduced | false" in package_text and "one adapter introduced: yes" not in lower_combined))
    checks.append(("No customer identifier leakage", "customerAssetIdentifier" not in combined and "customer identifier" not in lower_combined))
    checks.append(("No local absolute path leakage in stakeholder-facing package", not any(term in package_text for term in LEAKAGE_TERMS)))
    checks.append(("PASS marker present", PASS_MARKER in combined))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to UMMS-R10 review package scope", not disallowed))
    checks.append(("No EDGE/LINK/Contracts/UFMS files modified", not forbidden and not any("VANTARIS_UFMS_FULL" in path for path in changed)))
    if disallowed:
        errors.append(f"changes outside UMMS-R10 scope: {', '.join(sorted(disallowed))}")
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
    checks.append(("Registry review package id present", registry_data.get("reviewPackageId") == "umms-stakeholder-review-package.v1"))
    checks.append(("Registry push false", registry_data.get("pushPerformed") is False))
    checks.append(("Registry safety matrix frozen", safety.get("readOnly") is True and safety.get("dbWrite") is False and safety.get("oneAdapterIntroduced") is False and safety.get("hmiRuntimeExecution") is False))
    checks.append(("Registry JSON validation passes if registry is created", _json_valid(REGISTRY)))

    for label, command, marker, env in REGRESSION_COMMANDS:
        result = _run(command, env=env)
        passed = result.returncode == 0 and marker in result.stdout
        checks.append((label, passed))
        if not passed:
            errors.append(result.stdout[-3000:] or result.stderr[-3000:] or f"{label} failed")

    print("ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE_VALIDATION")
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
