#!/usr/bin/env python3
"""Validate UMMS-R11A local freeze + optional tag plan."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FREEZE_DOC = ROOT / "ONE_UMMS_R11A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-r11a-readonly-api-entry-local-freeze.v1.json"
REPORT = ROOT / "ONE_UMMS_R11A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md"
BASE_COMMIT = "0b0587f071030158b200d2fec5e18a80ffc482aa"
R11_MARKER = "ONE_UMMS_R11_READONLY_API_ENTRY_SKELETON_PASS"
PASS_MARKER = "ONE_UMMS_R11A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS"

EXPECTED_ENDPOINTS = (
    "GET `/api/v1/one/umms/package-entry`",
    "GET `/api/v1/one/umms/stakeholder-review`",
    "GET `/api/v1/one/umms/readiness-summary`",
    "GET `/api/v1/one/umms/customer-core-functions`",
    "GET `/api/v1/one/umms/safety-posture`",
)
SAFETY_FLAGS = (
    "readOnly",
    "getOnly",
    "productionActivation",
    "runtimeActivation",
    "dbWrite",
    "approvalExecution",
    "workflowExecution",
    "writeActionsEnabled",
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
    "oneAdapterIntroduced",
    "customerIdentifierLeakage",
    "localAbsolutePathLeakage",
)
ALLOWED_CHANGED_PREFIXES = (
    "ONE_UMMS_R11A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN.md",
    "AN_VANTARIS_ONE/registries/umms-r11a-readonly-api-entry-local-freeze.v1.json",
    "ONE_UMMS_R11A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md",
    "scripts/validation/validate-one-umms-r11a-local-freeze.py",
)
FORBIDDEN_CHANGED_PREFIXES = (
    "AN_VANTARIS_EDGE/",
    "AN_VANTARIS_LINK/",
    "AN_VANTARIS_Contracts/",
    "/Volumes/Work/VANTARIS_UFMS_FULL",
    "AN_VANTARIS_IBMS-backend/src/api/umms/",
    "AN_VANTARIS_IBMS-backend/src/umms/",
    "AN_VANTARIS_IBMS-frontend/",
    "database/",
    "migrations/",
)
REGRESSION_COMMANDS = (
    ("UMMS-R11 validator still passes", ["python3", "scripts/validation/validate-one-umms-r11-readonly-api-entry-skeleton.py"], "ONE_UMMS_R11_READONLY_API_ENTRY_SKELETON_PASS", None),
    ("UMMS Package / UConsole stakeholder entry local freeze validator still passes", ["python3", "scripts/validation/validate-one-umms-package-uconsole-stakeholder-entry-local-freeze.py"], "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS", None),
    ("UMMS Package / UConsole stakeholder entry readiness validator still passes", ["python3", "scripts/validation/validate-one-umms-package-uconsole-stakeholder-entry-readiness.py"], "ONE_UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_READINESS_PASS", None),
    ("UMMS-R10A validator still passes", ["python3", "scripts/validation/validate-one-umms-r10a-local-freeze.py"], "ONE_UMMS_R10A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS", None),
    ("UMMS-R10 validator still passes", ["python3", "scripts/validation/validate-one-umms-r10-stakeholder-review-package.py"], "ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE_PASS", None),
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
    if _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip() == "docs(one): freeze umms readonly api entry skeleton":
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _json_valid(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except Exception:
        return False


def _strip_allowed_workspace_path(text: str) -> str:
    return text.replace("/Users/leon/Desktop/AN_VANTARIS_IBMS", "")


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    freeze_text = FREEZE_DOC.read_text(encoding="utf-8") if FREEZE_DOC.exists() else ""
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    combined = "\n".join([freeze_text, registry_text, report_text])
    lower_combined = combined.lower()

    checks.append(("Freeze document exists", FREEZE_DOC.is_file()))
    checks.append(("Freeze registry exists", REGISTRY.is_file()))
    checks.append(("Freeze report exists", REPORT.is_file()))
    checks.append(("Current commit reference is present", BASE_COMMIT in freeze_text and BASE_COMMIT in registry_text and BASE_COMMIT in report_text))
    checks.append(("UMMS-R11 PASS marker is referenced", R11_MARKER in combined))
    checks.append(("Frozen API scope includes all 5 GET-only endpoints", all(endpoint in freeze_text and endpoint in report_text for endpoint in EXPECTED_ENDPOINTS)))
    checks.append(("Freeze document states no POST / PUT / PATCH / DELETE endpoints", all(term in freeze_text for term in ("No POST endpoints.", "No PUT endpoints.", "No PATCH endpoints.", "No DELETE endpoints."))))

    try:
        registry = json.loads(registry_text)
    except Exception as exc:
        registry = {}
        errors.append(f"registry json invalid: {exc}")
    safety = registry.get("safetyMatrix", {})
    optional_tag_plan = registry.get("optionalTagPlan", {})

    checks.append(("Safety freeze matrix contains all required flags", all(flag in safety for flag in SAFETY_FLAGS) and safety.get("readOnly") is True and safety.get("getOnly") is True and all(safety.get(flag) is False for flag in SAFETY_FLAGS if flag not in {"readOnly", "getOnly"})))
    checks.append(("Optional tag plan is documented as not executed", "Suggested commands for future use only, not executed" in freeze_text and optional_tag_plan.get("commandsExecuted") is False and registry.get("pushPerformed") is False and registry.get("tagCreated") is False))
    checks.append(("No claim that push was performed", "push performed: yes" not in lower_combined and '"pushPerformed": false' in registry_text))
    checks.append(("No claim that tag was created", "tag created: yes" not in lower_combined and '"tagCreated": false' in registry_text))
    checks.append(("No production activation claim", "This is not production activation." in freeze_text and "production activation enabled" not in lower_combined))
    checks.append(("No runtime activation claim", "This is not runtime activation." in freeze_text and "runtime activation enabled" not in lower_combined))
    checks.append(("No DB write claim", "This is not DB write enablement." in freeze_text and "db write enabled" not in lower_combined))
    checks.append(("No approval execution claim", "This is not approval execution." in freeze_text and "approval execution enabled" not in lower_combined))
    checks.append(("No workflow execution claim", "This is not workflow execution." in freeze_text and "workflow execution enabled" not in lower_combined))
    runtime_phrases = (
        "This is not work order runtime execution.",
        "This is not PM execution.",
        "This is not inventory transaction.",
        "This is not vendor / contract / SLA runtime.",
        "This is not evidence upload or closure execution.",
        "This is not HMI runtime.",
    )
    checks.append(("No work order/PM/inventory/vendor/evidence/HMI runtime claim", all(phrase in freeze_text for phrase in runtime_phrases)))
    checks.append(("No EDGE/LINK runtime integration claim", "This is not EDGE/LINK runtime integration." in freeze_text and "edge/link runtime integration enabled" not in lower_combined))
    checks.append(("No ONE Adapter introduction", safety.get("oneAdapterIntroduced") is False and "one adapter introduced: yes" not in lower_combined))
    checks.append(("No customer identifier leakage", "customerAssetIdentifier" not in combined and "customer identifier" not in lower_combined))
    no_local_path_leak = "/Users/" not in _strip_allowed_workspace_path(freeze_text) and "/Users/" not in _strip_allowed_workspace_path(report_text) and "/Users/" not in registry_text
    checks.append(("No local absolute path leakage except internal workspace baseline", no_local_path_leak and "/Volumes/Work/VANTARIS_UFMS_FULL" not in combined))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to UMMS-R11A freeze scope", not disallowed))
    checks.append(("No EDGE/LINK/Contracts/UFMS files modified", not forbidden and not any("VANTARIS_UFMS_FULL" in path for path in changed)))
    if disallowed:
        errors.append(f"changes outside UMMS-R11A freeze scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    checks.append(("Registry JSON validation passes", _json_valid(REGISTRY)))

    for label, command, marker, env in REGRESSION_COMMANDS:
        print(f"[RUN] {label}", flush=True)
        result = _run(command, env=env)
        passed = result.returncode == 0 and marker in result.stdout
        checks.append((label, passed))
        if not passed:
            errors.append(result.stdout[-3000:] or result.stderr[-3000:] or f"{label} failed")

    print("ONE_UMMS_R11A_LOCAL_FREEZE_VALIDATION")
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

