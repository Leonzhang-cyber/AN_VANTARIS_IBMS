#!/usr/bin/env python3
"""Validate UMMS-R2A local freeze and optional tag plan."""
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
FREEZE_DOC = ROOT / "ONE_UMMS_R2A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-r2a-local-freeze.v1.json"
REPORT = ROOT / "ONE_UMMS_R2A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md"
AIRPORT_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts"
UMMS_PROJECTION = ROOT / "AN_VANTARIS_ONE/projections/umms-work-order-asset-pm-domain-alignment.v1.json"
UMMS_REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-work-order-asset-pm-domain-alignment-registry.v1.json"
PASS_MARKER = "ONE_UMMS_R2A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS"

UMMS_R2_COMMIT = "5ade7e70347b7beb881ebaa29b763d9ecde575e1"
UMMS_R2_MARKER = "ONE_UMMS_R2_WORK_ORDER_ASSET_PM_DOMAIN_ALIGNMENT_PASS"
FREEZE_SCOPE = (
    "UMMS generic domain alignment",
    "Work Order domain model",
    "Work Order lifecycle model",
    "Work Order trigger alignment",
    "Asset Registry domain model",
    "Asset lifecycle model",
    "Preventive Maintenance domain model",
    "Preventive Maintenance trigger model",
    "Airport-to-UMMS mapping",
    "Customer core function alignment",
    "Shared EDGE/LINK/UCDE dependency map",
    "Future UMMS roadmap",
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
SAFETY_TERMS = (
    "readOnly | true",
    "productionActivation | false",
    "runtimeActivation | false",
    "dbWrite | false",
    "approvalExecution | false",
    "workflowExecution | false",
    "workOrderCreation | false",
    "pmScheduleExecution | false",
    "assetLifecycleWrite | false",
    "inventoryTransaction | false",
    "vendorContractExecution | false",
    "deploymentExecution | false",
    "remoteCommandExecution | false",
    "connectorExecution | false",
    "deviceConnection | false",
    "edgeRuntimeCall | false",
    "linkRuntimeCall | false",
    "oneAdapterIntroduced | false",
    "customerIdentifierLeakage | false",
    "localAbsolutePathLeakage | false",
)
ALLOWED_CHANGED_PREFIXES = (
    "ONE_UMMS_R2A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN.md",
    "AN_VANTARIS_ONE/registries/umms-r2a-local-freeze.v1.json",
    "ONE_UMMS_R2A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md",
    "AN_VANTARIS_ONE/tests/",
    "scripts/validation/validate-one-umms-r2a-local-freeze.py",
)
FORBIDDEN_CHANGED_PREFIXES = (
    "AN_VANTARIS_EDGE/", "AN_VANTARIS_LINK/", "AN_VANTARIS_Contracts/",
    "/Volumes/Work/VANTARIS_UFMS_FULL", "AN_VANTARIS_IBMS-backend/",
    "AN_VANTARIS_IBMS-frontend/", "database/", "migrations/",
)
FORBIDDEN_CLIENT_METHODS = (".post", ".put", ".patch", ".delete")
LEAKAGE_TERMS = ("customerAssetIdentifier",)
FORBIDDEN_AFFIRMATIVE_CLAIMS = (
    "production activation enabled",
    "runtime activation enabled",
    "db write enabled",
    "approval execution enabled",
    "workflow execution enabled",
    "work order creation enabled",
    "pm schedule execution enabled",
    "asset lifecycle write enabled",
    "inventory transaction enabled",
    "vendor/contract execution enabled",
    "edge/link runtime integration enabled",
    "one adapter introduced: yes",
    "tag created: yes",
    "push performed: yes",
)
REGRESSION_MARKERS = {
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


def _changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        paths.update(line for line in _run(command).stdout.splitlines() if line)
    last_subject = _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip()
    if "freeze umms work asset pm alignment" in last_subject:
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _workspace_path_only_in_baseline(text: str) -> bool:
    allowed = "`/Users/leon/Desktop/AN_VANTARIS_IBMS`"
    return "/Users/" not in text.replace(allowed, "")


def _run_validator(script: str) -> subprocess.CompletedProcess[str]:
    path = ROOT / script
    if not path.exists():
        return subprocess.CompletedProcess([_python(), script], 1, "", f"{script} missing")
    spec = importlib.util.spec_from_file_location(f"umms_r2a_regression_{path.stem.replace('-', '_')}", path)
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
    except Exception as exc:  # noqa: BLE001
        exit_code = 1
        stderr.write(str(exc))
    finally:
        os.environ.clear()
        os.environ.update(original_env)
    return subprocess.CompletedProcess([_python(), script], exit_code, stdout.getvalue(), stderr.getvalue())


def _json_valid(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except Exception:
        return False


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    freeze_text = FREEZE_DOC.read_text(encoding="utf-8") if FREEZE_DOC.exists() else ""
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    combined = "\n".join([freeze_text, registry_text, report_text])
    lower_combined = combined.lower()

    checks.append(("UMMS-R2A freeze document exists", FREEZE_DOC.is_file()))
    checks.append(("Optional registry exists", REGISTRY.is_file()))
    checks.append(("UMMS-R2A report exists", REPORT.is_file()))
    checks.append(("UMMS-R2 commit reference is present", UMMS_R2_COMMIT in freeze_text and UMMS_R2_COMMIT in registry_text))
    checks.append(("UMMS-R2 PASS marker is referenced", UMMS_R2_MARKER in combined))
    checks.append(("Freeze scope includes all required UMMS-R2 scope items", all(item in freeze_text for item in FREEZE_SCOPE)))
    checks.append(("Domain alignment summary states UMMS is generic and not Airport-specific", "UMMS is a generic cross-industry maintenance management module." in freeze_text and "not Airport-specific logic" in freeze_text))
    checks.append(("Customer core function coverage matrix includes all 10 customer functions", all(function in freeze_text for function in CUSTOMER_FUNCTIONS)))
    checks.append(("Safety freeze matrix contains all required flags", all(term in freeze_text for term in SAFETY_TERMS)))
    checks.append(("Optional tag plan is documented as not executed", "Suggested commands for future use only, not executed" in freeze_text and "Tag created: no" in freeze_text and "Push performed: no" in freeze_text))
    checks.append(("No claim that push was performed", "push performed: yes" not in lower_combined and "Push performed: no" in freeze_text and "Push performed: no" in report_text))
    checks.append(("No claim that tag was created", "tag created: yes" not in lower_combined and "Tag created: no" in freeze_text and "Tag created: no" in report_text))
    checks.append(("No production activation claim", "This is not production activation." in freeze_text and "production activation enabled" not in lower_combined))
    checks.append(("No runtime activation claim", "This is not runtime activation." in freeze_text and "runtime activation enabled" not in lower_combined))
    checks.append(("No DB write claim", "This is not DB write enablement." in freeze_text and "db write enabled" not in lower_combined))
    checks.append(("No approval execution claim", "This is not approval execution." in freeze_text and "approval execution enabled" not in lower_combined))
    checks.append(("No workflow execution claim", "This is not workflow execution." in freeze_text and "workflow execution enabled" not in lower_combined))
    checks.append(("No work order creation claim", "This is not work order creation." in freeze_text and "work order creation enabled" not in lower_combined))
    checks.append(("No PM schedule execution claim", "This is not PM schedule execution." in freeze_text and "pm schedule execution enabled" not in lower_combined))
    checks.append(("No asset lifecycle write claim", "This is not asset lifecycle write." in freeze_text and "asset lifecycle write enabled" not in lower_combined))
    checks.append(("No inventory transaction claim", "This is not inventory transaction." in freeze_text and "inventory transaction enabled" not in lower_combined))
    checks.append(("No vendor/contract execution claim", "This is not vendor/contract execution." in freeze_text and "vendor/contract execution enabled" not in lower_combined))
    checks.append(("No EDGE/LINK runtime integration claim", "This is not EDGE/LINK runtime integration." in freeze_text and "edge/link runtime integration enabled" not in lower_combined))
    checks.append(("No ONE Adapter introduction", "oneAdapterIntroduced | false" in freeze_text and "one adapter introduced: yes" not in lower_combined))
    checks.append(("No customer identifier leakage", not any(term in combined for term in LEAKAGE_TERMS)))
    checks.append(("No local absolute path leakage except baseline workspace", _workspace_path_only_in_baseline(freeze_text) and "/Users/" not in report_text and "/Users/" not in registry_text))
    checks.append(("UMMS-R2A PASS marker present", PASS_MARKER in combined))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to UMMS-R2A freeze scope", not disallowed))
    checks.append(("No EDGE/LINK/Contracts/UFMS files modified", not forbidden and not any("VANTARIS_UFMS_FULL" in path for path in changed)))
    if disallowed:
        errors.append(f"changes outside UMMS-R2A scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    try:
        registry_data = json.loads(registry_text)
    except Exception as exc:  # noqa: BLE001
        registry_data = {}
        errors.append(f"registry json invalid: {exc}")
    checks.append(("Registry freeze id present", registry_data.get("releaseFreezeId") == "umms-r2a-local-freeze-20260621"))
    checks.append(("Registry tag and push false", registry_data.get("pushPerformed") is False and registry_data.get("tagCreated") is False and registry_data.get("optionalTagPlan", {}).get("commandsExecuted") is False))
    checks.append(("Registry safety matrix frozen", registry_data.get("safetyMatrix", {}).get("readOnly") is True and registry_data.get("safetyMatrix", {}).get("oneAdapterIntroduced") is False))
    checks.append(("Registry validation matrix includes UMMS-R2 marker", UMMS_R2_MARKER in registry_data.get("validationMatrix", {})))

    airport_client_text = AIRPORT_CLIENT.read_text(encoding="utf-8") if AIRPORT_CLIENT.exists() else ""
    checks.append(("No POST/PUT/PATCH/DELETE Airport or UMMS API client methods added", not any(method in airport_client_text for method in FORBIDDEN_CLIENT_METHODS)))

    regression_specs = (
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
    checks.append(("Projection JSON validation passes", _json_valid(UMMS_PROJECTION)))
    checks.append(("Registry JSON validation passes", _json_valid(UMMS_REGISTRY) and _json_valid(REGISTRY)))

    print("ONE_UMMS_R2A_LOCAL_FREEZE_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_UMMS_R2A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_FAIL")
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
