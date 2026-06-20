#!/usr/bin/env python3
"""Validate GA-R5A Airport local release freeze and optional tag plan."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FREEZE_DOC = ROOT / "ONE_AIRPORT_GA_R5A_LOCAL_RELEASE_FREEZE_AND_OPTIONAL_TAG_PLAN.md"
REPORT = ROOT / "ONE_AIRPORT_GA_R5A_LOCAL_RELEASE_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/airport-ga-r5a-local-release-freeze.v1.json"
PASS_MARKER = "ONE_AIRPORT_GA_R5A_LOCAL_RELEASE_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS"

COMMITS = (
    "c78fb35190c76027115b4bb92fc8322bf07b73c7",
    "d4218fe3711344369420ea30e57217998d968f2b",
    "f1056fe0b34019dc0660783bab687cae0332e5ee",
    "82667d1",
    "a581d5e242f1f3e6fb6890f31f2ad562a079d125",
)
PASS_MARKERS = (
    "ONE_AIRPORT_GA_R1_READONLY_API_ROUTE_IMPLEMENTATION_PASS",
    "ONE_AIRPORT_GA_R2_READONLY_API_LOCAL_SMOKE_AND_CONTRACT_REGRESSION_PASS",
    "ONE_AIRPORT_GA_R3_READONLY_FRONTEND_ROUTE_PAGE_IMPLEMENTATION_PASS",
    "ONE_AIRPORT_GA_R4_UCONSOLE_AIRPORT_READONLY_PAGE_BINDING_PASS",
    "ONE_AIRPORT_GA_R5_STAKEHOLDER_REVIEW_PACKAGE_PASS",
)
BACKEND_ROUTES = (
    "GET /api/v1/one/airport/console/overview",
    "GET /api/v1/one/airport/console/systems-integration-health",
    "GET /api/v1/one/airport/console/assets-topology",
    "GET /api/v1/one/airport/console/alarms-events",
    "GET /api/v1/one/airport/console/fault-cases",
    "GET /api/v1/one/airport/console/maintenance-work-orders",
    "GET /api/v1/one/airport/console/evidence-investigation",
    "GET /api/v1/one/airport/console/reports",
)
SAFETY_TERMS = (
    "readOnly | true",
    "productionActivation | false",
    "runtimeActivation | false",
    "dbWrite | false",
    "approvalExecution | false",
    "deploymentExecution | false",
    "remoteCommandExecution | false",
    "edgeLinkRuntimeCall | false",
    "customerIdentifierLeakage | false",
    "localAbsolutePathLeakage | false",
    "oneAdapterIntroduced | false",
)
ALLOWED_CHANGED_PREFIXES = (
    "ONE_AIRPORT_GA_R5A_LOCAL_RELEASE_FREEZE_AND_OPTIONAL_TAG_PLAN.md",
    "ONE_AIRPORT_GA_R5A_LOCAL_RELEASE_FREEZE_AND_OPTIONAL_TAG_PLAN_REPORT.md",
    "AN_VANTARIS_ONE/registries/airport-ga-r5a-local-release-freeze.v1.json",
    "AN_VANTARIS_ONE/tests/",
    "scripts/validation/validate-one-airport-ga-r5a-local-release-freeze.py",
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
FORBIDDEN_AFFIRMATIVE_CLAIMS = (
    "production activation enabled",
    "runtime activation enabled",
    "db write enabled",
    "approval execution enabled",
    "deployment execution enabled",
    "remote command execution enabled",
    "edge/link runtime integration enabled",
    "one adapter introduced",
    "tag created: yes",
    "push performed: yes",
)
CUSTOMER_LEAKAGE_TERMS = (
    "customerAssetIdentifier",
    '"assetId"',
    '"deviceId"',
)


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
    if "freeze airport ga readonly stakeholder review chain" in last_subject:
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _run_validator(script: str) -> subprocess.CompletedProcess[str]:
    return _run(
        [_python(), script],
        env={
            "PYTHONPATH": "AN_VANTARIS_IBMS-backend:AN_VANTARIS_ONE",
            "IBMS_LOCAL_SMOKE": "true",
        },
    )


def _route_present(text: str, route: str) -> bool:
    method, path = route.split(" ", 1)
    return method in text and path in text


def _workspace_path_only_in_baseline(text: str) -> bool:
    allowed = "`/Users/leon/Desktop/AN_VANTARIS_IBMS`"
    without_allowed = text.replace(allowed, "")
    return "/Users/" not in without_allowed


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []

    freeze_text = FREEZE_DOC.read_text(encoding="utf-8") if FREEZE_DOC.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    combined = "\n".join([freeze_text, report_text])
    lower_combined = combined.lower()

    checks.append(("GA-R5A freeze document exists", FREEZE_DOC.is_file()))
    checks.append(("GA-R5A report exists", REPORT.is_file()))
    checks.append(("Optional registry exists", REGISTRY.is_file()))
    checks.append(("GA-R1 through GA-R5 commit references are present", all(commit in freeze_text for commit in COMMITS)))
    checks.append(("GA-R1 through GA-R5 PASS markers are referenced", all(marker in freeze_text for marker in PASS_MARKERS)))
    checks.append(("All 8 backend routes are referenced", all(_route_present(freeze_text, route) for route in BACKEND_ROUTES)))
    checks.append(("Frontend route /one/airport/overview is referenced", "/one/airport/overview" in freeze_text))
    checks.append(("UConsole entry Airport GA Read-only is referenced", "Airport GA Read-only" in freeze_text))
    checks.append(("Safety freeze matrix contains all required flags", all(term in freeze_text for term in SAFETY_TERMS)))
    checks.append(("Optional tag plan is documented as not executed", "Suggested commands for future use only, not executed" in freeze_text and "Tag created: no" in freeze_text))
    checks.append(("No claim that push was performed", "Push performed: no" in freeze_text and "Push performed: no" in report_text and "push performed: yes" not in lower_combined))
    checks.append(("No claim that tag was created", "Tag created: no" in freeze_text and "Tag created: no" in report_text and "tag created: yes" not in lower_combined))
    checks.append(("No production activation claim", "This is not production activation." in freeze_text and FORBIDDEN_AFFIRMATIVE_CLAIMS[0] not in lower_combined))
    checks.append(("No runtime activation claim", "This is not runtime activation." in freeze_text and FORBIDDEN_AFFIRMATIVE_CLAIMS[1] not in lower_combined))
    checks.append(("No DB write claim", "This is not DB write enablement." in freeze_text and FORBIDDEN_AFFIRMATIVE_CLAIMS[2] not in lower_combined))
    checks.append(("No approval execution claim", "This is not approval execution." in freeze_text and FORBIDDEN_AFFIRMATIVE_CLAIMS[3] not in lower_combined))
    checks.append(("No EDGE/LINK runtime integration claim", "This is not EDGE/LINK runtime integration." in freeze_text and FORBIDDEN_AFFIRMATIVE_CLAIMS[6] not in lower_combined))
    checks.append(("No ONE Adapter introduction", "oneAdapterIntroduced | false" in freeze_text and "one adapter introduced" not in lower_combined))
    checks.append(("No customer identifier leakage", not any(term in freeze_text for term in CUSTOMER_LEAKAGE_TERMS)))
    checks.append(("No local absolute path leakage except baseline workspace", _workspace_path_only_in_baseline(freeze_text) and "/Users/" not in report_text))
    checks.append(("GA-R5A PASS marker present", PASS_MARKER in combined))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to GA-R5A freeze scope", not disallowed))
    checks.append(("No EDGE/LINK/Contracts/UFMS/backend/frontend/UConsole files modified", not forbidden))
    if disallowed:
        errors.append(f"changes outside GA-R5A scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    try:
        registry_data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        registry_data = {}
        errors.append(f"registry json invalid: {exc}")
    checks.append(("Registry freeze id present", registry_data.get("releaseFreezeId") == "airport-ga-r5a-local-release-freeze-20260621"))
    checks.append(("Registry tag and push frozen false", registry_data.get("pushPerformed") is False and registry_data.get("tagCreated") is False))
    checks.append(("Registry safety matrix frozen", registry_data.get("safetyMatrix", {}).get("readOnly") is True and registry_data.get("safetyMatrix", {}).get("oneAdapterIntroduced") is False))
    checks.append(("Registry PASS marker present", PASS_MARKER in registry_data.get("passMarkers", [])))

    regression_specs = (
        ("GA-R5 validator still passes", "scripts/validation/validate-one-airport-ga-r5-stakeholder-review-package.py", "ONE_AIRPORT_GA_R5_STAKEHOLDER_REVIEW_PACKAGE_PASS"),
        ("GA-R4 validator still passes", "scripts/validation/validate-one-airport-ga-r4-uconsole-binding.py", "ONE_AIRPORT_GA_R4_UCONSOLE_AIRPORT_READONLY_PAGE_BINDING_PASS"),
        ("GA-R3 validator still passes", "scripts/validation/validate-one-airport-ga-r3-readonly-frontend-page.py", "ONE_AIRPORT_GA_R3_READONLY_FRONTEND_ROUTE_PAGE_IMPLEMENTATION_PASS"),
        ("GA-R2 validator still passes", "scripts/validation/validate-one-airport-ga-r2-readonly-api-smoke-regression.py", "ONE_AIRPORT_GA_R2_READONLY_API_LOCAL_SMOKE_AND_CONTRACT_REGRESSION_PASS"),
        ("GA-R1 validator still passes", "scripts/validation/validate-one-airport-ga-readonly-api-routes.py", "ONE_AIRPORT_GA_R1_READONLY_API_ROUTE_IMPLEMENTATION_PASS"),
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

    print("ONE_AIRPORT_GA_R5A_LOCAL_RELEASE_FREEZE_AND_OPTIONAL_TAG_PLAN_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_AIRPORT_GA_R5A_LOCAL_RELEASE_FREEZE_AND_OPTIONAL_TAG_PLAN_FAIL")
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
