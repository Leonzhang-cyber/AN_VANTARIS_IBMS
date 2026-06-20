#!/usr/bin/env python3
"""Validate GA-R7 Airport existing-system onboarding and mapping readiness."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTION = ROOT / "AN_VANTARIS_ONE/projections/airport-existing-system-onboarding-mapping-readiness.v1.json"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/airport-existing-system-onboarding-mapping-readiness-registry.v1.json"
REPORT = ROOT / "ONE_AIRPORT_GA_R7_EXISTING_SYSTEM_ONBOARDING_MAPPING_READINESS_REPORT.md"
AIRPORT_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts"
PASS_MARKER = "ONE_AIRPORT_GA_R7_EXISTING_SYSTEM_ONBOARDING_MAPPING_READINESS_PASS"

SYSTEMS = {
    "Bosch CCTV", "Bosch ACS-SMS", "PA System", "Radio System", "Tonna IPTV",
    "Mobatime Clock System", "NEC IPBX", "Armanno Toll", "BMS", "EMS", "MMS",
    "e-Inspection", "iFeedback", "Security System",
}
METHODS = {
    "OPC UA", "OPC TCP/IP", "SNMP", "Modbus TCP", "BACnet/IP", "REST API",
    "SDK", "CSV import", "Excel import", "File export", "Scheduled export",
    "Webhook / event push future",
}
MAPPING_GROUPS = {
    "Source System Mapping", "Connector Mapping", "Device Mapping", "Point Mapping",
    "Tag Mapping", "Asset Reference Mapping", "Location Reference Mapping",
    "Alarm Severity Mapping", "Fault Candidate Mapping", "Work Order Trigger Mapping",
    "Evidence Reference Mapping", "Graphics HMI Locator Mapping",
}
TAG_FIELDS = {
    "tagName", "rawTagName", "normalizedTagName", "sourceSystemId", "connectorId",
    "deviceId", "pointId", "assetRef", "locationRef", "systemType", "discipline",
    "signalType", "unit", "quality", "severityMapping", "alarmMapping",
    "faultCandidateMapping", "workOrderTriggerMapping", "hmiSymbolRef",
}
TAG_VALIDATIONS = {
    "duplicateTagDetection", "tagConflictDetection", "missingAssetRefDetection",
    "missingLocationRefDetection", "unitNormalization", "timezoneNormalization",
    "qualityFlagNormalization", "severityNormalization",
}
CUSTOMER_FUNCTIONS = {
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
}
EDGE_REQUIREMENTS = {
    "Airport ELV connector matrix", "Existing system onboarding profile",
    "Tag list import parser", "OPC browse snapshot import",
    "BACnet discovery snapshot import", "SNMP walk snapshot import",
    "CSV / Excel import connector", "Tag mapping validation",
    "Normalization preview", "Sample payload preview", "Engineer commissioning CLI",
    "Offline/remote deployment package", "Hardware-key / site-binding status",
    "HMI locator data foundation",
}
LINK_REQUIREMENTS = {
    "Source system health contract", "Delivery readiness contract",
    "Canonical delivery envelope", "Work-order trigger contract",
    "Asset/location reference contract", "Audit/evidence chain profile",
    "Mapping profile contract", "Deployment package status contract",
    "Remote support bundle contract", "Distributed topology contract",
}
SAFETY_EXPECTED = {
    "readOnly": True,
    "runtimeActivation": False,
    "productionActivation": False,
    "dbWrite": False,
    "approvalExecution": False,
    "deploymentExecution": False,
    "remoteCommandExecution": False,
    "connectorExecution": False,
    "deviceConnection": False,
    "edgeRuntimeCall": False,
    "linkRuntimeCall": False,
    "oneAdapterIntroduced": False,
    "customerIdentifierLeakage": False,
    "localAbsolutePathLeakage": False,
}
ALLOWED_CHANGED_PREFIXES = (
    "AN_VANTARIS_ONE/projections/airport-existing-system-onboarding-mapping-readiness.v1.json",
    "AN_VANTARIS_ONE/registries/airport-existing-system-onboarding-mapping-readiness-registry.v1.json",
    "ONE_AIRPORT_GA_R7_EXISTING_SYSTEM_ONBOARDING_MAPPING_READINESS_REPORT.md",
    "AN_VANTARIS_ONE/tests/",
    "scripts/validation/validate-one-airport-ga-r7-existing-system-onboarding-mapping-readiness.py",
)
FORBIDDEN_CHANGED_PREFIXES = (
    "AN_VANTARIS_EDGE/", "AN_VANTARIS_LINK/", "AN_VANTARIS_Contracts/",
    "/Volumes/Work/VANTARIS_UFMS_FULL", "AN_VANTARIS_IBMS-backend/",
    "AN_VANTARIS_IBMS-frontend/", "database/", "migrations/",
)
FORBIDDEN_CLIENT_METHODS = (".post", ".put", ".patch", ".delete")
LEAKAGE_TERMS = ("/Users/", "/Volumes/Work/VANTARIS_UFMS_FULL", "customerAssetIdentifier", '"assetId"')


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
    except Exception as exc:  # noqa: BLE001
        return {}, str(exc)


def _changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        paths.update(line for line in _run(command).stdout.splitlines() if line)
    last_subject = _run(["git", "log", "-1", "--pretty=%s"]).stdout.strip()
    if "airport existing system onboarding readiness" in last_subject:
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _run_validator(script: str) -> subprocess.CompletedProcess[str]:
    return _run(
        [_python(), script],
        env={"PYTHONPATH": "AN_VANTARIS_IBMS-backend:AN_VANTARIS_ONE", "IBMS_LOCAL_SMOKE": "true"},
    )


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    projection, projection_error = _load_json(PROJECTION)
    registry, registry_error = _load_json(REGISTRY)
    projection_text = PROJECTION.read_text(encoding="utf-8") if PROJECTION.exists() else ""
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    stakeholder_text = "\n".join([projection_text, registry_text, report_text])

    checks.append(("GA-R7 projection artifact exists", PROJECTION.is_file() and not projection_error))
    checks.append(("GA-R7 registry exists", REGISTRY.is_file() and not registry_error))
    checks.append(("GA-R7 report exists", REPORT.is_file()))
    if projection_error:
        errors.append(f"projection json invalid: {projection_error}")
    if registry_error:
        errors.append(f"registry json invalid: {registry_error}")

    metadata = projection.get("metadata", {})
    checks.append(("Projection metadata contains platform = VANTARIS ONE", metadata.get("platform") == "VANTARIS ONE"))
    checks.append(("Projection metadata contains industryProjection = airport", metadata.get("industryProjection") == "airport"))
    checks.append(("Projection safety flags are correct", all(metadata.get(k) is v for k, v in SAFETY_EXPECTED.items() if k in metadata)))

    systems = {item.get("systemName") for item in projection.get("existingSystemCatalog", [])}
    methods = {item.get("methodName") for item in projection.get("integrationMethodCatalog", [])}
    groups = {item.get("name") for item in projection.get("mappingReadinessModel", [])}
    tag_requirements = projection.get("tagMappingRequirements", {})
    packet = projection.get("onboardingReviewPacketRequirements", {})
    functions = {item.get("function") for item in projection.get("customerCoreFunctionMappingImpact", [])}
    shared = projection.get("sharedFoundationInterfaceRequirements", {})
    safety = projection.get("safetyPosture", {})

    checks.append(("existingSystemCatalog includes all required customer systems", SYSTEMS.issubset(systems)))
    checks.append(("integrationMethodCatalog includes all required integration methods", METHODS.issubset(methods)))
    checks.append(("mappingReadinessModel includes all required mapping groups", MAPPING_GROUPS.issubset(groups)))
    checks.append(("tagMappingRequirements includes all required future fields", TAG_FIELDS.issubset(set(tag_requirements.get("requiredFutureFields", [])))))
    checks.append(("tagMappingRequirements includes all required validation requirements", TAG_VALIDATIONS.issubset(set(tag_requirements.get("validationRequirements", [])))))
    checks.append(("onboardingReviewPacketRequirements exists and activationAllowed remains false", packet.get("activationAllowed") is False and "activationAllowed must remain false in GA-R7" in packet.get("activationStatement", "")))
    checks.append(("customerCoreFunctionMappingImpact includes all 10 customer core functions", CUSTOMER_FUNCTIONS.issubset(functions)))
    checks.append(("sharedFoundationInterfaceRequirements includes required EDGE requirements", EDGE_REQUIREMENTS.issubset(set(shared.get("edgeRequirements", [])))))
    checks.append(("sharedFoundationInterfaceRequirements includes required LINK requirements", LINK_REQUIREMENTS.issubset(set(shared.get("linkRequirements", [])))))
    checks.append(("safetyPosture confirms no runtime/production/DB/approval/deployment/remote command/connector/device execution", all(safety.get(k) is v for k, v in SAFETY_EXPECTED.items())))
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
    checks.append(("Changes limited to GA-R7 projection scope", not disallowed and not forbidden))
    if disallowed:
        errors.append(f"changes outside GA-R7 scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    airport_client_text = AIRPORT_CLIENT.read_text(encoding="utf-8") if AIRPORT_CLIENT.exists() else ""
    checks.append(("No POST/PUT/PATCH/DELETE Airport API client methods added", not any(method in airport_client_text for method in FORBIDDEN_CLIENT_METHODS)))
    checks.append(("No customer identifier leakage", not any(term in stakeholder_text for term in LEAKAGE_TERMS[2:])))
    checks.append(("No local absolute path leakage in stakeholder-facing artifacts", not any(term in stakeholder_text for term in LEAKAGE_TERMS[:2])))
    checks.append(("Projection JSON validation passes", not projection_error and metadata.get("projectionId") == "airport-existing-system-onboarding-mapping-readiness.v1"))
    checks.append(("Registry JSON validation passes", not registry_error and registry.get("validationMarker") == PASS_MARKER))
    checks.append(("Report contains PASS marker", PASS_MARKER in report_text))

    regression_specs = (
        ("GA-R6 validator still passes", "scripts/validation/validate-one-airport-ga-r6-link-integration-readiness.py", "ONE_AIRPORT_GA_R6_LINK_INTEGRATION_READINESS_PROJECTION_PASS"),
        ("GA-R5A validator still passes", "scripts/validation/validate-one-airport-ga-r5a-local-release-freeze.py", "ONE_AIRPORT_GA_R5A_LOCAL_RELEASE_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS"),
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

    print("ONE_AIRPORT_GA_R7_EXISTING_SYSTEM_ONBOARDING_MAPPING_READINESS_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_AIRPORT_GA_R7_EXISTING_SYSTEM_ONBOARDING_MAPPING_READINESS_FAIL")
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
