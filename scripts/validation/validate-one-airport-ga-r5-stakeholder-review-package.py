#!/usr/bin/env python3
"""Validate GA-R5 Airport stakeholder review package."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "ONE_AIRPORT_GA_R5_STAKEHOLDER_REVIEW_PACKAGE.md"
REPORT = ROOT / "ONE_AIRPORT_GA_R5_STAKEHOLDER_REVIEW_PACKAGE_REPORT.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/airport-ga-stakeholder-review-package.v1.json"
PASS_MARKER = "ONE_AIRPORT_GA_R5_STAKEHOLDER_REVIEW_PACKAGE_PASS"

REQUIRED_MARKERS = (
    "ONE_AIRPORT_GA_R1_READONLY_API_ROUTE_IMPLEMENTATION_PASS",
    "ONE_AIRPORT_GA_R2_READONLY_API_LOCAL_SMOKE_AND_CONTRACT_REGRESSION_PASS",
    "ONE_AIRPORT_GA_R3_READONLY_FRONTEND_ROUTE_PAGE_IMPLEMENTATION_PASS",
    "ONE_AIRPORT_GA_R4_UCONSOLE_AIRPORT_READONLY_PAGE_BINDING_PASS",
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
    "edgeLinkRuntimeCall | false",
    "customerIdentifierLeakage | false",
    "localAbsolutePathLeakage | false",
)
REQUIRED_SECTIONS = (
    "## F. Customer Core Function Readiness",
    "## G. Future EDGE/LINK Shared Foundation Interface Requirements",
    "## H. Known Limitations",
    "## I. Recommended Next Roadmap",
)
ALLOWED_CHANGED_PREFIXES = (
    "ONE_AIRPORT_GA_R5_STAKEHOLDER_REVIEW_PACKAGE.md",
    "ONE_AIRPORT_GA_R5_STAKEHOLDER_REVIEW_PACKAGE_REPORT.md",
    "AN_VANTARIS_ONE/registries/airport-ga-stakeholder-review-package.v1.json",
    "AN_VANTARIS_ONE/tests/",
    "scripts/validation/validate-one-airport-ga-r5-stakeholder-review-package.py",
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
LEAKAGE_TERMS = (
    "/Users/",
    "/Volumes/Work/VANTARIS_UFMS_FULL",
    "customerAssetIdentifier",
    '"assetId"',
    '"deviceId"',
)
FORBIDDEN_AFFIRMATIVE_CLAIMS = (
    "production activation enabled",
    "runtime activation enabled",
    "db write enabled",
    "approval execution enabled",
    "direct edge/link runtime integration enabled",
    "real edge/link runtime integration enabled",
    "real edge/link runtime call enabled",
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
    if "airport ga stakeholder review package" in last_subject:
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


def _contains_route(text: str, route: str) -> bool:
    method, path = route.split(" ", 1)
    return method in text and path in text


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []

    package_text = PACKAGE.read_text(encoding="utf-8") if PACKAGE.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    combined_text = "\n".join([package_text, report_text])
    lower_combined = combined_text.lower()

    checks.append(("GA-R5 stakeholder package exists", PACKAGE.is_file()))
    checks.append(("GA-R5 report exists", REPORT.is_file()))
    checks.append(("GA-R5 registry artifact exists", REGISTRY.is_file()))
    checks.append(("Required GA-R1/R2/R3/R4 markers are referenced", all(marker in combined_text for marker in REQUIRED_MARKERS)))
    checks.append(("Backend route matrix includes all 8 GET routes", all(_contains_route(package_text, route) for route in BACKEND_ROUTES)))
    checks.append(("Frontend route /one/airport/overview is referenced", "/one/airport/overview" in package_text))
    checks.append(("UConsole Airport GA Read-only entry is referenced", "Airport GA Read-only" in package_text))
    checks.append(("Read-only safety matrix includes all required flags", all(term in package_text for term in SAFETY_TERMS)))
    checks.append(("Customer core function readiness section exists", "## F. Customer Core Function Readiness" in package_text))
    checks.append(("Future EDGE/LINK shared foundation requirements section exists", "## G. Future EDGE/LINK Shared Foundation Interface Requirements" in package_text))
    checks.append(("Known limitations section exists", "## H. Known Limitations" in package_text))
    checks.append(("Roadmap section exists", "## I. Recommended Next Roadmap" in package_text))
    checks.append(("No claim of production activation", "This is not production activation." in package_text and not any(term in lower_combined for term in FORBIDDEN_AFFIRMATIVE_CLAIMS[:1])))
    checks.append(("No claim of runtime activation", "This is not runtime activation." in package_text and FORBIDDEN_AFFIRMATIVE_CLAIMS[1] not in lower_combined))
    checks.append(("No claim of DB write", "This is not DB write enablement." in package_text and FORBIDDEN_AFFIRMATIVE_CLAIMS[2] not in lower_combined))
    checks.append(("No claim of approval execution", "This is not approval execution." in package_text and FORBIDDEN_AFFIRMATIVE_CLAIMS[3] not in lower_combined))
    checks.append(("No claim of real EDGE/LINK runtime integration", "This is not direct EDGE/LINK runtime integration." in package_text and not any(term in lower_combined for term in FORBIDDEN_AFFIRMATIVE_CLAIMS[4:])))
    checks.append(("No local absolute path leakage in stakeholder-facing document", "/Users/" not in package_text))
    checks.append(("No customer identifier leakage", not any(term in package_text for term in LEAKAGE_TERMS[2:])))
    checks.append(("GA-R5 PASS marker present", PASS_MARKER in combined_text))
    checks.append(("Required sections exist", all(section in package_text for section in REQUIRED_SECTIONS)))

    changed = _changed_paths()
    disallowed = [path for path in changed if not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)]
    forbidden = [path for path in changed if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES)]
    checks.append(("Changes limited to GA-R5 stakeholder review scope", not disallowed))
    checks.append(("No EDGE/LINK/Contracts/UFMS/backend/frontend behavior files modified", not forbidden))
    if disallowed:
        errors.append(f"changes outside GA-R5 scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    try:
        registry_data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        registry_data = {}
        errors.append(f"registry json invalid: {exc}")
    checks.append(("Registry release candidate frozen", registry_data.get("releaseCandidate") == "airport-international-ga-ready-readonly-rc-20260620"))
    checks.append(("Registry safety matrix frozen", registry_data.get("safetyMatrix", {}).get("readOnly") is True and registry_data.get("safetyMatrix", {}).get("dbWrite") is False))
    checks.append(("Registry validation marker frozen", PASS_MARKER in registry_data.get("validationMarkers", [])))

    regression_specs = (
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

    print("ONE_AIRPORT_GA_R5_STAKEHOLDER_REVIEW_PACKAGE_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_AIRPORT_GA_R5_STAKEHOLDER_REVIEW_PACKAGE_FAIL")
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
