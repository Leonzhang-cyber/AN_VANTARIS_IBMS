#!/usr/bin/env python3
"""Validate UMMS-R13 observability / monitoring / read-only metrics layer."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "ONE_UMMS_R13_OBSERVABILITY_READONLY_METRICS_LAYER.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-r13-observability-readonly-metrics.v1.json"
REPORT = ROOT / "ONE_UMMS_R13_OBSERVABILITY_READONLY_METRICS_LAYER_REPORT.md"
BASE_COMMIT = "49e0e2da209a77b6d491deaabf1f031886a7fbad"
PASS_MARKER = "ONE_UMMS_R13_OBSERVABILITY_READONLY_METRICS_LAYER_PASS"

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
NO_EXECUTION_FALSE_FLAGS = (
    "liveMetricsIngestion",
    "runtimeObservabilityAgent",
    "databaseReadImplementation",
    "databaseWriteImplementation",
    "backendRouteAdded",
    "frontendRouteAdded",
    "workflowHookAdded",
    "edgeLinkRuntimeHookAdded",
)
ALLOWED_CHANGED_PREFIXES = (
    "ONE_UMMS_R13_OBSERVABILITY_READONLY_METRICS_LAYER.md",
    "AN_VANTARIS_ONE/registries/umms-r13-observability-readonly-metrics.v1.json",
    "ONE_UMMS_R13_OBSERVABILITY_READONLY_METRICS_LAYER_REPORT.md",
    "scripts/validation/validate-one-umms-r13-observability-readonly-metrics.py",
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
    if _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip() == "docs(one): add umms observability readonly metrics layer":
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _marker_exists(marker: str) -> bool:
    return _run(["git", "grep", "-q", marker]).returncode == 0


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []

    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    combined = "\n".join([doc_text, registry_text, report_text])
    lower_combined = combined.lower()

    checks.append(("R13 document exists", DOC.is_file()))
    checks.append(("R13 registry exists", REGISTRY.is_file()))
    checks.append(("R13 report exists", REPORT.is_file()))
    checks.append(("Baseline commit is referenced", all(BASE_COMMIT in text for text in (doc_text, registry_text, report_text))))

    try:
        registry = json.loads(registry_text)
    except Exception as exc:
        registry = {}
        errors.append(f"registry json invalid: {exc}")

    chain = registry.get("chainStatusR2ToR12A", [])
    chain_markers = {row.get("marker") for row in chain}
    missing = [marker for marker in CHAIN_MARKERS if marker not in chain_markers or not _marker_exists(marker)]
    checks.append(("Chain completeness R2 through R12A", len(chain) == len(CHAIN_MARKERS) and not missing))
    if missing:
        errors.append(f"missing chain markers: {', '.join(missing)}")

    metrics = registry.get("aggregatedMetrics", {})
    checks.append(("Aggregated metrics are complete", metrics.get("totalChainLayers") == 24 and metrics.get("completedChainLayers") == 24 and metrics.get("readinessPercentage") == 100))
    checks.append(("Read-only endpoint and route counts are frozen", metrics.get("getOnlyEndpointCount") == 5 and metrics.get("readOnlyFrontendRoutes") == 1))
    checks.append(("No runtime or mutation flags are enabled in metrics", metrics.get("runtimeFlagsEnabled") == 0 and metrics.get("mutationFlagsEnabled") == 0))

    safety = registry.get("safetyFlags", {})
    checks.append(("Read-only metrics flags are true", safety.get("readOnly") is True and safety.get("metricsAggregationOnly") is True))
    checks.append(("Runtime and mutation safety flags are false", all(safety.get(flag) is False for flag in SAFETY_FALSE_FLAGS)))
    no_execution = registry.get("noExecutionFlags", {})
    checks.append(("No execution hooks declared", all(no_execution.get(flag) is False for flag in NO_EXECUTION_FALSE_FLAGS)))

    dependencies = registry.get("dependencyMap", {})
    checks.append(("Dependency map includes EDGE/LINK/UCDE", set(dependencies) == {"EDGE", "LINK", "UCDE"}))
    checks.append(("Dependency runtime calls are disabled", dependencies.get("EDGE", {}).get("runtimeCallEnabled") is False and dependencies.get("LINK", {}).get("runtimeCallEnabled") is False and dependencies.get("UCDE", {}).get("runtimeExecutionEnabled") is False))

    required_doc_phrases = (
        "No runtime observability agent.",
        "No live metrics ingestion.",
        "No database read or write implementation.",
        "No backend API route.",
        "No frontend UI modification.",
        "No EDGE or LINK runtime call.",
        "UMMS-R13A freeze plan.",
    )
    checks.append(("Limitations and next step are documented", all(phrase in doc_text for phrase in required_doc_phrases)))
    forbidden_claims = (
        "runtime activation enabled",
        "production activation enabled",
        "db write enabled",
        "workflow execution enabled",
        "backend mutation enabled",
        "frontend ui mutation enabled",
        "one adapter introduced: yes",
        "push performed: yes",
        "tag created: yes",
    )
    checks.append(("No mutation/runtime claims", not any(term in lower_combined for term in forbidden_claims)))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to UMMS-R13 observability scope", not disallowed))
    checks.append(("No EDGE/LINK/Contracts/UFMS/backend/frontend/DB files modified", not forbidden and not any("VANTARIS_UFMS_FULL" in path for path in changed)))
    if disallowed:
        errors.append(f"changes outside UMMS-R13 scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    checks.append(("No local absolute path leakage", "/Users/" not in combined and "/Volumes/Work/VANTARIS_UFMS_FULL" not in combined))
    checks.append(("No customer identifier leakage", "customerAssetIdentifier" not in combined and "customer identifier" not in lower_combined))

    for label, command, marker, env in REGRESSION_COMMANDS:
        print(f"[RUN] {label}", flush=True)
        result = _run(command, env=env)
        passed = result.returncode == 0 and marker in result.stdout
        checks.append((label, passed))
        if not passed:
            errors.append(result.stdout[-3000:] or result.stderr[-3000:] or f"{label} failed")

    print("ONE_UMMS_R13_OBSERVABILITY_READONLY_METRICS_VALIDATION")
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
