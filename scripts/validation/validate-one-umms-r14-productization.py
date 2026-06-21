#!/usr/bin/env python3
"""Validate UMMS-R14 productization consolidation architecture."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "ONE_UMMS_R14_PRODUCTIZATION_CONSOLIDATION.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-r14-productization-model.v1.json"
REPORT = ROOT / "ONE_UMMS_R14_PRODUCTIZATION_CONSOLIDATION_REPORT.md"
BASE_COMMIT = "599a7b3b510cc4d0b61fc450c4380ff5743995e9"
PASS_MARKER = "ONE_UMMS_R14_PRODUCTIZATION_CONSOLIDATION_PASS"
R13A_MARKER = "ONE_UMMS_R13A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS"

ALLOWED_CHANGED_PREFIXES = (
    "ONE_UMMS_R14_PRODUCTIZATION_CONSOLIDATION.md",
    "AN_VANTARIS_ONE/registries/umms-r14-productization-model.v1.json",
    "ONE_UMMS_R14_PRODUCTIZATION_CONSOLIDATION_REPORT.md",
    "scripts/validation/validate-one-umms-r14-productization.py",
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
FALSE_FLAGS = (
    "runtimeActivation",
    "productionActivation",
    "dbWrite",
    "workflowExecution",
    "apiChange",
    "uiChange",
    "backendMutation",
    "frontendMutation",
    "approvalExecution",
    "workOrderRuntimeExecution",
    "pmExecution",
    "inventoryTransaction",
    "vendorContractSlaRuntime",
    "evidenceClosureExecution",
    "hmiRuntimeExecution",
    "edgeRuntimeCall",
    "linkRuntimeCall",
    "ufmsModification",
    "oneAdapterIntroduced",
    "activationCapability",
)
CAPABILITIES = {
    "Maintenance Operations",
    "Asset Intelligence",
    "Vendor / SLA Awareness",
    "Inventory Readiness",
    "Evidence & Compliance View",
}
LAYERS = {
    "Core Read-only Domain Layer",
    "R11 API Layer",
    "R12 UI Layer",
    "R13 Observability Layer",
    "R13A Freeze Layer",
}
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
    if _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip() == "docs(one): add umms architecture consolidation r14":
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _marker_exists(marker: str) -> bool:
    return _run(["git", "grep", "-q", marker]).returncode == 0


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []

    doc = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    report = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    combined = "\n".join([doc, registry_text, report])
    lower = combined.lower()

    checks.append(("R14 document exists", DOC.is_file()))
    checks.append(("R14 registry exists", REGISTRY.is_file()))
    checks.append(("R14 report exists", REPORT.is_file()))
    checks.append(("Baseline HEAD is referenced", all(BASE_COMMIT in text for text in (doc, registry_text, report))))
    checks.append(("R13A dependency intact", R13A_MARKER in combined and _marker_exists(R13A_MARKER)))

    try:
        registry = json.loads(registry_text)
    except Exception as exc:
        registry = {}
        errors.append(f"registry json invalid: {exc}")

    boundary = registry.get("productBoundaryContract", {})
    checks.append(("Product boundaries are correct", boundary.get("UMMS", {}).get("role") == "read-only operations intelligence layer" and boundary.get("UFMS", {}).get("role") == "system-of-record core" and boundary.get("EDGE", {}).get("role") == "field execution layer" and boundary.get("LINK", {}).get("role") == "integration layer"))
    checks.append(("UMMS has no runtime authority", boundary.get("UMMS", {}).get("runtimeAuthority") is False and boundary.get("UMMS", {}).get("executionAuthority") is False))

    layers = {row.get("layer") for row in registry.get("moduleLayeringModel", [])}
    checks.append(("Module boundaries are correct", layers == LAYERS and all(row.get("runtimeAuthority") is False for row in registry.get("moduleLayeringModel", []))))
    caps = set(registry.get("capabilityMapping", {}))
    checks.append(("Capability mapping has five product domains", caps == CAPABILITIES and all(row.get("executionCapability") is False for row in registry.get("capabilityMapping", {}).values())))

    graph = registry.get("systemRelationshipGraph", {})
    checks.append(("System relationship graph is data-flow only", set(graph.get("nodes", [])) == {"UFMS", "UMMS", "EDGE", "LINK"} and all(edge.get("execution") is False for edge in graph.get("edges", []))))

    safety = registry.get("safetyPosture", {})
    checks.append(("Safety posture is architecture-only/read-only", safety.get("readOnly") is True and safety.get("architectureOnly") is True))
    checks.append(("All runtime flags are false", all(safety.get(flag) is False for flag in FALSE_FLAGS)))
    execution = registry.get("executionCapability", {})
    checks.append(("No execution capability", all(value is False for value in execution.values()) and len(execution) >= 6))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Architecture-only outputs", not disallowed))
    checks.append(("EDGE/LINK/UFMS/backend/frontend/DB untouched", not forbidden and not any("VANTARIS_UFMS_FULL" in path for path in changed)))
    if disallowed:
        errors.append(f"changes outside R14 architecture scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    forbidden_claims = (
        "runtime activation enabled",
        "db write enabled",
        "workflow execution enabled",
        "api change enabled",
        "ui change enabled",
        "one adapter introduced: yes",
    )
    checks.append(("No runtime/API/DB/UI mutation claims", not any(term in lower for term in forbidden_claims)))
    checks.append(("PASS marker present", PASS_MARKER in registry_text and PASS_MARKER in report))
    checks.append(("No local absolute path leakage", "/Users/" not in combined and "/Volumes/Work/VANTARIS_UFMS_FULL" not in combined))

    for label, command, marker, env in REGRESSION_COMMANDS:
        print(f"[RUN] {label}", flush=True)
        result = _run(command, env=env)
        passed = result.returncode == 0 and marker in result.stdout
        checks.append((label, passed))
        if not passed:
            errors.append(result.stdout[-3000:] or result.stderr[-3000:] or f"{label} failed")

    print("ONE_UMMS_R14_PRODUCTIZATION_VALIDATION")
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
