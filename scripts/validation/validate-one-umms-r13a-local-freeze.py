#!/usr/bin/env python3
"""Validate UMMS-R13A local freeze + optional tag plan."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FREEZE_DOC = ROOT / "ONE_UMMS_R13A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-r13a-local-freeze.v1.json"
REPORT = ROOT / "ONE_UMMS_R13A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md"
R13_DOC = ROOT / "ONE_UMMS_R13_OBSERVABILITY_READONLY_METRICS_LAYER.md"
R13_REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-r13-observability-readonly-metrics.v1.json"
R13_REPORT = ROOT / "ONE_UMMS_R13_OBSERVABILITY_READONLY_METRICS_LAYER_REPORT.md"
BASE_COMMIT = "4fbee5838065c24bbe9e5b380ae878fe6fac977f"
PASS_MARKER = "ONE_UMMS_R13A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS"

CHAIN_MARKERS = (
    "ONE_UMMS_R2_WORK_ORDER_ASSET_PM_DOMAIN_ALIGNMENT_PASS",
    "ONE_UMMS_R2A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R3_MANUAL_WORK_ORDER_READONLY_QUEUE_DRAFT_MODEL_PASS",
    "ONE_UMMS_R3A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R4_WORK_ORDER_LIFECYCLE_STATE_VALIDATION_GATE_PASS",
    "ONE_UMMS_R4A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R5_PREVENTIVE_MAINTENANCE_SCHEDULE_READINESS_PASS",
    "ONE_UMMS_R5A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R6_SPARE_PARTS_INVENTORY_READINESS_PASS",
    "ONE_UMMS_R6A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R7_VENDOR_CONTRACT_SLA_READINESS_PASS",
    "ONE_UMMS_R7A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R8_UCDE_EVIDENCE_CLOSURE_ALIGNMENT_PASS",
    "ONE_UMMS_R8A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R9_AIRPORT_HMI_LOCATOR_BINDING_READINESS_PASS",
    "ONE_UMMS_R9A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE_PASS",
    "ONE_UMMS_R10A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_READINESS_PASS",
    "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R11_READONLY_API_ENTRY_SKELETON_PASS",
    "ONE_UMMS_R11A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R12_READONLY_FRONTEND_UCONSOLE_CARD_ENTRY_PASS",
    "ONE_UMMS_R12A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS",
    "ONE_UMMS_R13_OBSERVABILITY_READONLY_METRICS_LAYER_PASS",
)
SAFETY_FALSE_FLAGS = (
    "runtimeActivation",
    "productionActivation",
    "dbWrite",
    "workflowExecution",
    "backendMutation",
    "frontendUiMutation",
    "approvalExecution",
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
    "contractsChange",
    "ufmsChange",
    "oneAdapterIntroduced",
    "tagCreated",
    "pushPerformed",
)
ALLOWED_CHANGED_PREFIXES = (
    "ONE_UMMS_R13A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN.md",
    "AN_VANTARIS_ONE/registries/umms-r13a-local-freeze.v1.json",
    "ONE_UMMS_R13A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md",
    "scripts/validation/validate-one-umms-r13a-local-freeze.py",
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
REGRESSION_COMMANDS = (
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
    if _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip() == "docs(one): freeze umms observability readonly metrics layer":
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _marker_exists(marker: str) -> bool:
    return _run(["git", "grep", "-q", marker]).returncode == 0


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []

    freeze_text = FREEZE_DOC.read_text(encoding="utf-8") if FREEZE_DOC.exists() else ""
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    r13_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (R13_DOC, R13_REGISTRY, R13_REPORT)
        if path.exists()
    )
    combined = "\n".join([freeze_text, registry_text, report_text, r13_text])
    lower_combined = combined.lower()

    checks.append(("R13A freeze document exists", FREEZE_DOC.is_file()))
    checks.append(("R13A freeze registry exists", REGISTRY.is_file()))
    checks.append(("R13A freeze report exists", REPORT.is_file()))
    checks.append(("R13 source artifacts exist", R13_DOC.is_file() and R13_REGISTRY.is_file() and R13_REPORT.is_file()))
    checks.append(("Baseline commit reference is present", all(BASE_COMMIT in text for text in (freeze_text, registry_text, report_text))))

    try:
        registry = json.loads(registry_text)
    except Exception as exc:
        registry = {}
        errors.append(f"registry json invalid: {exc}")

    chain = registry.get("chainCompletenessR2ToR13", [])
    missing_chain = [marker for marker in CHAIN_MARKERS if marker not in chain or not _marker_exists(marker)]
    checks.append(("R2 to R13 chain intact", len(chain) == len(CHAIN_MARKERS) and not missing_chain))
    if missing_chain:
        errors.append(f"missing R2-R13 chain markers: {', '.join(missing_chain)}")

    metrics = registry.get("metricsModel", {})
    checks.append(("Metrics model frozen", metrics.get("totalChainLayers") == 25 and metrics.get("completedChainLayers") == 25 and metrics.get("readinessPercentage") == 100))
    checks.append(("Metrics have no runtime/mutation enabled", metrics.get("runtimeFlagsEnabled") == 0 and metrics.get("mutationFlagsEnabled") == 0))

    safety = registry.get("safetyFlags", {})
    checks.append(("Read-only/local-freeze flags are true", safety.get("readOnly") is True and safety.get("localFreezeOnly") is True and safety.get("metricsAggregationOnly") is True))
    checks.append(("No runtime flags enabled", all(safety.get(flag) is False for flag in SAFETY_FALSE_FLAGS)))
    checks.append(("No DB write", safety.get("dbWrite") is False and "This is not DB write enablement." in freeze_text))
    checks.append(("No workflow execution", safety.get("workflowExecution") is False and "This is not workflow execution." in freeze_text))
    checks.append(("No UI mutation", safety.get("frontendUiMutation") is False and "This is not frontend UI mutation." in freeze_text))
    checks.append(("No backend mutation", safety.get("backendMutation") is False and "This is not backend mutation." in freeze_text))
    checks.append(("No ONE Adapter", safety.get("oneAdapterIntroduced") is False and "one adapter introduced: yes" not in lower_combined))
    checks.append(("No tag/push claims", registry.get("tagCreated") is False and registry.get("pushPerformed") is False and "tag created: yes" not in lower_combined and "push performed: yes" not in lower_combined))

    dependency_map = registry.get("dependencyMap", {})
    checks.append(("Dependency map includes EDGE/LINK/UCDE", set(dependency_map) == {"EDGE", "LINK", "UCDE"}))
    checks.append(("Dependency runtime disabled", dependency_map.get("EDGE", {}).get("runtimeCallEnabled") is False and dependency_map.get("LINK", {}).get("runtimeCallEnabled") is False and dependency_map.get("UCDE", {}).get("runtimeExecutionEnabled") is False))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to UMMS-R13A freeze scope", not disallowed))
    checks.append(("No EDGE/LINK/Contracts/UFMS/backend/frontend/DB files modified", not forbidden and not any("VANTARIS_UFMS_FULL" in path for path in changed)))
    if disallowed:
        errors.append(f"changes outside UMMS-R13A freeze scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    forbidden_claims = (
        "runtime activation enabled",
        "production activation enabled",
        "db write enabled",
        "workflow execution enabled",
        "backend mutation enabled",
        "frontend ui mutation enabled",
        "one adapter introduced: yes",
    )
    checks.append(("No forbidden runtime/mutation claims", not any(term in lower_combined for term in forbidden_claims)))
    checks.append(("Registry JSON correctness", bool(registry.get("releaseFreezeId") == "umms-r13a-local-freeze.v1")))
    checks.append(("No local absolute path leakage", "/Users/" not in combined and "/Volumes/Work/VANTARIS_UFMS_FULL" not in combined))
    checks.append(("No customer identifier leakage", "customerAssetIdentifier" not in combined and "customer identifier" not in lower_combined))

    for label, command, marker, env in REGRESSION_COMMANDS:
        print(f"[RUN] {label}", flush=True)
        result = _run(command, env=env)
        passed = result.returncode == 0 and marker in result.stdout
        checks.append((label, passed))
        if not passed:
            errors.append(result.stdout[-3000:] or result.stderr[-3000:] or f"{label} failed")

    print("ONE_UMMS_R13A_LOCAL_FREEZE_VALIDATION")
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
