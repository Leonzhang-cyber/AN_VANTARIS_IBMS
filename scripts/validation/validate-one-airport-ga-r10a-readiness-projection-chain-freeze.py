#!/usr/bin/env python3
"""Validate GA-R10A Airport readiness projection chain freeze."""
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
FREEZE_DOC = ROOT / "ONE_AIRPORT_GA_R10A_READINESS_PROJECTION_CHAIN_FREEZE_AND_OPTIONAL_TAG_PLAN.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/airport-ga-r10a-readiness-projection-chain-freeze.v1.json"
REPORT = ROOT / "ONE_AIRPORT_GA_R10A_READINESS_PROJECTION_CHAIN_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md"
AIRPORT_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts"
PASS_MARKER = "ONE_AIRPORT_GA_R10A_READINESS_PROJECTION_CHAIN_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS"

COMMITS = (
    "dbf88514cb48b2994dd69276065d0b3316f08474",
    "7b7bd04ddfe27eeceecd572a78d532c77fc4a857",
    "30ba3536e45feb9c7030c1625f4338688f386308",
    "a18818644fa1fefa644753fd4cd31c10e3fcde0a",
    "51b23317441726151110ff544869c3e56fd3f91f",
)
PASS_MARKERS = (
    "ONE_AIRPORT_GA_R6_LINK_INTEGRATION_READINESS_PROJECTION_PASS",
    "ONE_AIRPORT_GA_R7_EXISTING_SYSTEM_ONBOARDING_MAPPING_READINESS_PASS",
    "ONE_AIRPORT_GA_R8_ENGINEER_COMMISSIONING_DIAGNOSTICS_READINESS_PASS",
    "ONE_AIRPORT_GA_R9_GRAPHICS_HMI_EQUIPMENT_LOCATOR_READINESS_PASS",
    "ONE_AIRPORT_GA_R10_DISTRIBUTED_REMOTE_DEPLOYMENT_READINESS_PASS",
)
PROJECTION_ARTIFACTS = (
    "AN_VANTARIS_ONE/projections/airport-link-integration-readiness.v1.json",
    "AN_VANTARIS_ONE/projections/airport-existing-system-onboarding-mapping-readiness.v1.json",
    "AN_VANTARIS_ONE/projections/airport-engineer-commissioning-diagnostics-readiness.v1.json",
    "AN_VANTARIS_ONE/projections/airport-graphics-hmi-equipment-locator-readiness.v1.json",
    "AN_VANTARIS_ONE/projections/airport-distributed-remote-deployment-readiness.v1.json",
)
REGISTRY_ARTIFACTS = (
    "AN_VANTARIS_ONE/registries/airport-link-integration-readiness-registry.v1.json",
    "AN_VANTARIS_ONE/registries/airport-existing-system-onboarding-mapping-readiness-registry.v1.json",
    "AN_VANTARIS_ONE/registries/airport-engineer-commissioning-diagnostics-readiness-registry.v1.json",
    "AN_VANTARIS_ONE/registries/airport-graphics-hmi-equipment-locator-readiness-registry.v1.json",
    "AN_VANTARIS_ONE/registries/airport-distributed-remote-deployment-readiness-registry.v1.json",
    "AN_VANTARIS_ONE/registries/airport-ga-r10a-readiness-projection-chain-freeze.v1.json",
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
EDGE_REQUIREMENTS = (
    "Airport ELV connector matrix",
    "Existing system onboarding profile",
    "Tag mapping and normalization",
    "Engineer commissioning diagnostics CLI",
    "Sample payload preview",
    "Normalization preview",
    "HMI locator data foundation",
    "Offline install package manifest",
    "Hardware-key/site-binding status",
    "Support bundle export",
    "Healthcheck / precheck / rollback readiness",
    "Remote deployment package readiness",
)
LINK_REQUIREMENTS = (
    "Airport ELV canonical envelope",
    "Source-system health contract",
    "Delivery readiness contract",
    "Audit/evidence chain Airport profile",
    "Work-order trigger contract",
    "Asset/location reference contract",
    "HMI drawing/symbol reference fields",
    "Mapping profile contract",
    "Distributed topology contract",
    "Deployment package status contract",
    "Remote support bundle contract",
    "Delivery / ACK / retry / DLQ diagnostics",
)
SAFETY_TERMS = (
    "readOnly | true",
    "productionActivation | false",
    "runtimeActivation | false",
    "dbWrite | false",
    "approvalExecution | false",
    "deploymentExecution | false",
    "installExecution | false",
    "upgradeExecution | false",
    "rollbackExecution | false",
    "remoteCommandExecution | false",
    "diagnosticsExecution | false",
    "hmiRuntimeExecution | false",
    "hmiControlExecution | false",
    "drawingUpload | false",
    "supportBundleExecution | false",
    "connectorExecution | false",
    "deviceConnection | false",
    "edgeRuntimeCall | false",
    "linkRuntimeCall | false",
    "oneAdapterIntroduced | false",
    "customerIdentifierLeakage | false",
    "localAbsolutePathLeakage | false",
)
ALLOWED_CHANGED_PREFIXES = (
    "ONE_AIRPORT_GA_R10A_READINESS_PROJECTION_CHAIN_FREEZE_AND_OPTIONAL_TAG_PLAN.md",
    "AN_VANTARIS_ONE/registries/airport-ga-r10a-readiness-projection-chain-freeze.v1.json",
    "ONE_AIRPORT_GA_R10A_READINESS_PROJECTION_CHAIN_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md",
    "AN_VANTARIS_ONE/tests/",
    "scripts/validation/validate-one-airport-ga-r10a-readiness-projection-chain-freeze.py",
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
    "deployment execution enabled",
    "install execution enabled",
    "upgrade execution enabled",
    "rollback execution enabled",
    "remote command execution enabled",
    "edge/link runtime integration enabled",
    "one adapter introduced: yes",
    "tag created: yes",
    "push performed: yes",
)
REGRESSION_MARKERS = {
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
    if "freeze airport readiness projection chain" in last_subject:
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _workspace_path_only_in_baseline(text: str) -> bool:
    allowed = "`/Users/leon/Desktop/AN_VANTARIS_IBMS`"
    return "/Users/" not in text.replace(allowed, "")


def _run_validator(script: str) -> subprocess.CompletedProcess[str]:
    path = ROOT / script
    if not path.exists():
        return subprocess.CompletedProcess([_python(), script], 1, "", f"{script} missing")
    spec = importlib.util.spec_from_file_location(f"ga_r10a_regression_{path.stem.replace('-', '_')}", path)
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


def _json_valid(path: str) -> bool:
    try:
        json.loads((ROOT / path).read_text(encoding="utf-8"))
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

    checks.append(("GA-R10A freeze document exists", FREEZE_DOC.is_file()))
    checks.append(("Optional registry exists", REGISTRY.is_file()))
    checks.append(("GA-R10A report exists", REPORT.is_file()))
    checks.append(("GA-R6 through GA-R10 commit references are present", all(commit in freeze_text for commit in COMMITS)))
    checks.append(("GA-R6 through GA-R10 PASS markers are referenced", all(marker in freeze_text for marker in PASS_MARKERS)))
    checks.append(("GA-R6 through GA-R10 projection artifact names are referenced", all(path in registry_text for path in PROJECTION_ARTIFACTS)))
    checks.append(("Customer core function coverage matrix includes all 10 customer functions", all(function in freeze_text for function in CUSTOMER_FUNCTIONS)))
    checks.append(("Shared foundation interface requirement summary includes EDGE requirements", all(req in freeze_text for req in EDGE_REQUIREMENTS)))
    checks.append(("Shared foundation interface requirement summary includes LINK requirements", all(req in freeze_text for req in LINK_REQUIREMENTS)))
    checks.append(("Safety freeze matrix contains all required flags", all(term in freeze_text for term in SAFETY_TERMS)))
    checks.append(("Optional tag plan is documented as not executed", "Suggested commands for future use only, not executed" in freeze_text and "Tag created: no" in freeze_text and "Push performed: no" in freeze_text))
    checks.append(("No claim that push was performed", "push performed: yes" not in lower_combined and "Push performed: no" in freeze_text and "Push performed: no" in report_text))
    checks.append(("No claim that tag was created", "tag created: yes" not in lower_combined and "Tag created: no" in freeze_text and "Tag created: no" in report_text))
    checks.append(("No production activation claim", "This is not production activation." in freeze_text and "production activation enabled" not in lower_combined))
    checks.append(("No runtime activation claim", "This is not runtime activation." in freeze_text and "runtime activation enabled" not in lower_combined))
    checks.append(("No DB write claim", "This is not DB write enablement." in freeze_text and "db write enabled" not in lower_combined))
    checks.append(("No approval execution claim", "This is not approval execution." in freeze_text and "approval execution enabled" not in lower_combined))
    checks.append(("No deployment/install/upgrade/rollback execution claim", "This is not deployment execution." in freeze_text and "This is not install / upgrade / rollback execution." in freeze_text and not any(claim in lower_combined for claim in FORBIDDEN_AFFIRMATIVE_CLAIMS[4:8])))
    checks.append(("No remote command execution claim", "This is not remote command execution." in freeze_text and "remote command execution enabled" not in lower_combined))
    checks.append(("No EDGE/LINK runtime integration claim", "This is not EDGE/LINK runtime integration." in freeze_text and "edge/link runtime integration enabled" not in lower_combined))
    checks.append(("No ONE Adapter introduction", "oneAdapterIntroduced | false" in freeze_text and "one adapter introduced: yes" not in lower_combined))
    checks.append(("No customer identifier leakage", not any(term in combined for term in LEAKAGE_TERMS)))
    checks.append(("No local absolute path leakage except baseline workspace", _workspace_path_only_in_baseline(freeze_text) and "/Users/" not in report_text and "/Users/" not in registry_text))
    checks.append(("GA-R10A PASS marker present", PASS_MARKER in combined))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to GA-R10A freeze scope", not disallowed))
    checks.append(("No EDGE/LINK/Contracts/UFMS files modified", not forbidden and not any("VANTARIS_UFMS_FULL" in path for path in changed)))
    if disallowed:
        errors.append(f"changes outside GA-R10A scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    try:
        registry_data = json.loads(registry_text)
    except Exception as exc:  # noqa: BLE001
        registry_data = {}
        errors.append(f"registry json invalid: {exc}")
    checks.append(("Registry freeze id present", registry_data.get("releaseFreezeId") == "airport-ga-r10a-readiness-projection-chain-freeze-20260621"))
    checks.append(("Registry tag and push false", registry_data.get("pushPerformed") is False and registry_data.get("tagCreated") is False and registry_data.get("optionalTagPlan", {}).get("commandsExecuted") is False))
    checks.append(("Registry safety matrix frozen", registry_data.get("safetyMatrix", {}).get("readOnly") is True and registry_data.get("safetyMatrix", {}).get("oneAdapterIntroduced") is False))
    checks.append(("Registry validation matrix includes required markers", all(marker in registry_data.get("validationMatrix", {}) for marker in PASS_MARKERS)))

    airport_client_text = AIRPORT_CLIENT.read_text(encoding="utf-8") if AIRPORT_CLIENT.exists() else ""
    checks.append(("No POST/PUT/PATCH/DELETE Airport API client methods added", not any(method in airport_client_text for method in FORBIDDEN_CLIENT_METHODS)))

    regression_specs = (
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

    checks.append(("Projection JSON validation passes", all(_json_valid(path) for path in PROJECTION_ARTIFACTS)))
    checks.append(("Registry JSON validation passes", all(_json_valid(path) for path in REGISTRY_ARTIFACTS)))

    print("ONE_AIRPORT_GA_R10A_READINESS_PROJECTION_CHAIN_FREEZE_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_AIRPORT_GA_R10A_READINESS_PROJECTION_CHAIN_FREEZE_AND_OPTIONAL_TAG_PLAN_FAIL")
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
