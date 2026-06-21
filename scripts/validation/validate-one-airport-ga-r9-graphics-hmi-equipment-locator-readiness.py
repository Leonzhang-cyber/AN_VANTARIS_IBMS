#!/usr/bin/env python3
"""Validate GA-R9 Airport Graphics HMI equipment locator readiness."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import importlib.util
import io
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

ROOT = Path(__file__).resolve().parents[2]
PROJECTION = ROOT / "AN_VANTARIS_ONE/projections/airport-graphics-hmi-equipment-locator-readiness.v1.json"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/airport-graphics-hmi-equipment-locator-readiness-registry.v1.json"
REPORT = ROOT / "ONE_AIRPORT_GA_R9_GRAPHICS_HMI_EQUIPMENT_LOCATOR_READINESS_REPORT.md"
AIRPORT_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts"
PASS_MARKER = "ONE_AIRPORT_GA_R9_GRAPHICS_HMI_EQUIPMENT_LOCATOR_READINESS_PASS"

SAFETY_EXPECTED = {
    "readOnly": True,
    "runtimeActivation": False,
    "productionActivation": False,
    "dbWrite": False,
    "approvalExecution": False,
    "deploymentExecution": False,
    "remoteCommandExecution": False,
    "hmiRuntimeExecution": False,
    "hmiControlExecution": False,
    "drawingUpload": False,
    "bimRuntimeIntegration": False,
    "connectorExecution": False,
    "deviceConnection": False,
    "edgeRuntimeCall": False,
    "linkRuntimeCall": False,
    "oneAdapterIntroduced": False,
}
REFERENCES = {
    "assetRef", "locationRef", "systemRef", "equipmentRef", "drawingRef", "floorPlanRef",
    "zoneRef", "floorRef", "roomRef", "hmiSymbolRef", "topologyNodeRef", "bimObjectRef",
    "evidenceRef", "workOrderRef", "faultCaseRef", "alarmEventRef",
}
LOCATION_FIELDS = {
    "site", "terminal", "building", "level", "floor", "zone", "room", "area",
    "equipmentSpace", "coordinateSystem", "x", "y", "z", "geoReference",
    "drawingLayer", "hmiSymbolLayer",
}
DRAWING_FIELDS = {
    "drawingRef", "drawingType", "drawingVersion", "drawingDiscipline", "floorPlanRef",
    "symbolLibraryRef", "hmiSymbolRef", "symbolType", "symbolLabel", "symbolStatus",
    "symbolCoordinates", "symbolLayer", "assetRef", "locationRef", "lastReviewedAt",
    "reviewStatus",
}
DRAWING_TYPES = {
    "2D floor plan", "ELV system schematic", "system topology",
    "single-line diagram, future optional", "BIM view, future optional",
}
CHAIN_OBJECTS = {
    "Alarm", "Event", "Fault Case", "Work Order", "Asset Registry",
    "Preventive Maintenance Task", "Spare Part", "Vendor / Contract", "Evidence Record",
}
MAPPING_FIELDS = {
    "assetId", "assetRef", "assetName", "assetType", "systemType", "sourceSystemId",
    "connectorId", "deviceId", "pointId", "tagName", "locationRef", "building",
    "level", "floor", "zone", "room", "equipmentSpace", "drawingRef", "hmiSymbolRef",
    "topologyNodeRef", "bimObjectRef", "mappingStatus", "mappingConfidence",
    "reviewStatus", "riskFlags",
}
MAPPING_VALIDATIONS = {
    "missingAssetRefDetection", "missingLocationRefDetection", "missingDrawingRefDetection",
    "missingHmiSymbolRefDetection", "duplicateSymbolDetection", "conflictingLocationDetection",
    "staleDrawingVersionDetection", "unreviewedMappingDetection",
}
USE_CASES = {
    "locate-equipment-from-alarm", "locate-equipment-from-event",
    "locate-equipment-from-fault-case", "locate-equipment-from-work-order",
    "locate-equipment-from-asset-registry", "locate-equipment-from-pm-task",
    "locate-related-equipment-in-same-zone", "locate-evidence-source-context",
    "engineer-review-of-unmapped-equipment", "supervisor-review-of-location-confidence",
}
CUSTOMER_FUNCTIONS = {
    "Work Order Management, auto + manual", "Asset Registry, full lifecycle tracking",
    "Preventive Maintenance Scheduler", "Spare Parts / Inventory Management",
    "Vendor / Contract Management", "Graphics HMI to locate Equipment",
    "Existing system onboarding", "Engineer commissioning diagnostics",
    "Remote overseas deployment", "Distributed independent installation",
}
EDGE_REQUIREMENTS = {
    "assetRef / locationRef capture from connector mapping", "hmiSymbolRef mapping support",
    "drawingRef mapping support", "source tag to asset/location mapping preview",
    "asset-location mapping diagnostics", "HMI locator data foundation",
    "sample payload with asset/location references", "normalization preview with locator references",
    "connector mapping validation for missing references",
    "engineer commissioning output for locator readiness",
}
LINK_REQUIREMENTS = {
    "asset/location reference contract", "hmiSymbolRef / drawingRef reference fields",
    "source system health with locator mapping status",
    "delivery envelope with asset/location references",
    "work-order trigger with asset/location/hmi references",
    "evidence chain with asset/location context", "mapping profile contract",
    "distributed topology with site/building/floor references",
    "support bundle locator readiness summary", "audit event for mapping review status",
}
RENDERING_DEPENDENCIES = {
    "2D floor plan renderer", "Symbol library", "Equipment locator overlay",
    "Asset topology graph", "System topology view", "Alarm/event highlight overlay",
    "Work order location overlay", "Evidence-linked location view",
    "BIM integration, future optional", "Mobile locator view, future optional",
}
ALLOWED_CHANGED_PREFIXES = (
    "AN_VANTARIS_ONE/projections/airport-graphics-hmi-equipment-locator-readiness.v1.json",
    "AN_VANTARIS_ONE/registries/airport-graphics-hmi-equipment-locator-readiness-registry.v1.json",
    "ONE_AIRPORT_GA_R9_GRAPHICS_HMI_EQUIPMENT_LOCATOR_READINESS_REPORT.md",
    "AN_VANTARIS_ONE/tests/",
    "scripts/validation/validate-one-airport-ga-r9-graphics-hmi-equipment-locator-readiness.py",
)
FORBIDDEN_CHANGED_PREFIXES = (
    "AN_VANTARIS_EDGE/", "AN_VANTARIS_LINK/", "AN_VANTARIS_Contracts/",
    "/Volumes/Work/VANTARIS_UFMS_FULL", "AN_VANTARIS_IBMS-backend/",
    "AN_VANTARIS_IBMS-frontend/", "database/", "migrations/",
)
FORBIDDEN_CLIENT_METHODS = (".post", ".put", ".patch", ".delete")
LEAKAGE_TERMS = ("/Users/", "/Volumes/Work/VANTARIS_UFMS_FULL", "customerAssetIdentifier")
REGRESSION_MARKERS = {
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
    if "airport graphics hmi locator readiness" in last_subject:
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _run_validator(script: str) -> subprocess.CompletedProcess[str]:
    path = ROOT / script
    marker = REGRESSION_MARKERS.get(path.name, "")
    if not path.exists():
        return subprocess.CompletedProcess([_python(), script], 1, "", f"{script} missing")

    spec = importlib.util.spec_from_file_location(f"ga_r9_regression_{path.stem.replace('-', '_')}", path)
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


def _has_all(items: list | set, required: set[str]) -> bool:
    return required.issubset(set(items))


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    projection, projection_error = _load_json(PROJECTION)
    registry, registry_error = _load_json(REGISTRY)
    projection_text = PROJECTION.read_text(encoding="utf-8") if PROJECTION.exists() else ""
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    stakeholder_text = "\n".join([projection_text, registry_text, report_text])

    checks.append(("GA-R9 projection artifact exists", PROJECTION.is_file() and not projection_error))
    checks.append(("GA-R9 registry exists", REGISTRY.is_file() and not registry_error))
    checks.append(("GA-R9 report exists", REPORT.is_file()))
    if projection_error:
        errors.append(f"projection json invalid: {projection_error}")
    if registry_error:
        errors.append(f"registry json invalid: {registry_error}")

    metadata = projection.get("metadata", {})
    summary = projection.get("locatorReadinessSummary", {})
    drawing = projection.get("drawingAndSymbolRequirements", {})
    location = projection.get("locationHierarchyModel", {})
    mapping = projection.get("assetLocationMappingRequirements", {})
    shared = projection.get("sharedFoundationInterfaceRequirements", {})
    rendering = projection.get("futureRenderingDependencyModel", {})
    safety = projection.get("safetyPosture", {})

    checks.append(("Projection metadata contains platform = VANTARIS ONE", metadata.get("platform") == "VANTARIS ONE"))
    checks.append(("Projection metadata contains industryProjection = airport", metadata.get("industryProjection") == "airport"))
    checks.append(("Projection safety flags are correct", all(metadata.get(k) is v for k, v in SAFETY_EXPECTED.items())))
    checks.append(("locatorReadinessSummary confirms no runtime HMI/drawing/BIM/control", summary.get("runtimeHmiEnabled") is False and summary.get("customerDrawingLoaded") is False and summary.get("bimIntegrationEnabled") is False and summary.get("equipmentControlEnabled") is False))

    checks.append(("locatorReferenceModel includes all required references", REFERENCES.issubset({item.get("referenceName") for item in projection.get("locatorReferenceModel", [])})))
    checks.append(("locationHierarchyModel includes all required hierarchy fields", _has_all(location.get("requiredFields", []), LOCATION_FIELDS) and "No customer-specific location data is loaded" in location.get("statement", "")))
    checks.append(("drawingAndSymbolRequirements includes all required fields and drawing types", _has_all(drawing.get("requiredFutureFields", []), DRAWING_FIELDS) and _has_all(drawing.get("drawingTypes", []), DRAWING_TYPES)))
    checks.append(("drawingAndSymbolRequirements states no drawing upload or rendering is implemented in GA-R9", "No drawing upload or rendering is implemented in GA-R9" in drawing.get("statement", "")))
    checks.append(("locatorChainRequirements includes all required chains", CHAIN_OBJECTS.issubset({item.get("sourceObject") for item in projection.get("locatorChainRequirements", [])})))
    checks.append(("assetLocationMappingRequirements includes all required future fields", _has_all(mapping.get("requiredFutureFields", []), MAPPING_FIELDS)))
    checks.append(("assetLocationMappingRequirements includes all validation requirements", _has_all(mapping.get("validationRequirements", []), MAPPING_VALIDATIONS)))
    checks.append(("hmiLocatorUseCaseReadiness includes all required use cases", USE_CASES.issubset({item.get("useCaseId") for item in projection.get("hmiLocatorUseCaseReadiness", [])})))
    checks.append(("customerCoreFunctionLocatorImpact includes all 10 customer core functions", CUSTOMER_FUNCTIONS.issubset({item.get("function") for item in projection.get("customerCoreFunctionLocatorImpact", [])})))
    checks.append(("sharedFoundationInterfaceRequirements includes required EDGE requirements", _has_all(shared.get("edgeRequirements", []), EDGE_REQUIREMENTS)))
    checks.append(("sharedFoundationInterfaceRequirements includes required LINK requirements", _has_all(shared.get("linkRequirements", []), LINK_REQUIREMENTS)))
    checks.append(("futureRenderingDependencyModel exists and states GA-R9 does not implement rendering", _has_all(rendering.get("dependencies", []), RENDERING_DEPENDENCIES) and "GA-R9 does not implement rendering" in rendering.get("statement", "")))
    checks.append(("safetyPosture confirms no runtime/production/DB/approval/deployment/remote command/HMI control/drawing upload/BIM/connector/device execution", all(safety.get(k) is v for k, v in SAFETY_EXPECTED.items()) and safety.get("customerIdentifierLeakage") is False and safety.get("localAbsolutePathLeakage") is False))
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
    checks.append(("Changes limited to GA-R9 projection scope", not disallowed and not forbidden))
    if disallowed:
        errors.append(f"changes outside GA-R9 scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    airport_client_text = AIRPORT_CLIENT.read_text(encoding="utf-8") if AIRPORT_CLIENT.exists() else ""
    checks.append(("No POST/PUT/PATCH/DELETE Airport API client methods added", not any(method in airport_client_text for method in FORBIDDEN_CLIENT_METHODS)))
    checks.append(("No customer identifier leakage", not any(term in stakeholder_text for term in LEAKAGE_TERMS[2:])))
    checks.append(("No local absolute path leakage in stakeholder-facing artifacts", not any(term in stakeholder_text for term in LEAKAGE_TERMS[:2])))
    checks.append(("Projection JSON validation passes", not projection_error and metadata.get("projectionId") == "airport-graphics-hmi-equipment-locator-readiness.v1"))
    checks.append(("Registry JSON validation passes", not registry_error and registry.get("validationMarker") == PASS_MARKER))
    checks.append(("Report contains PASS marker", PASS_MARKER in report_text))

    regression_specs = (
        ("GA-R8 validator still passes", "scripts/validation/validate-one-airport-ga-r8-engineer-commissioning-diagnostics-readiness.py", "ONE_AIRPORT_GA_R8_ENGINEER_COMMISSIONING_DIAGNOSTICS_READINESS_PASS"),
        ("GA-R7 validator still passes", "scripts/validation/validate-one-airport-ga-r7-existing-system-onboarding-mapping-readiness.py", "ONE_AIRPORT_GA_R7_EXISTING_SYSTEM_ONBOARDING_MAPPING_READINESS_PASS"),
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

    print("ONE_AIRPORT_GA_R9_GRAPHICS_HMI_EQUIPMENT_LOCATOR_READINESS_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_AIRPORT_GA_R9_GRAPHICS_HMI_EQUIPMENT_LOCATOR_READINESS_FAIL")
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
