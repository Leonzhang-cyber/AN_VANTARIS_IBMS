#!/usr/bin/env python3
"""Validate GA-R8 Airport engineer commissioning diagnostics readiness."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTION = ROOT / "AN_VANTARIS_ONE/projections/airport-engineer-commissioning-diagnostics-readiness.v1.json"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/airport-engineer-commissioning-diagnostics-readiness-registry.v1.json"
REPORT = ROOT / "ONE_AIRPORT_GA_R8_ENGINEER_COMMISSIONING_DIAGNOSTICS_READINESS_REPORT.md"
AIRPORT_CLIENT = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/airportGaReadonly.ts"
PASS_MARKER = "ONE_AIRPORT_GA_R8_ENGINEER_COMMISSIONING_DIAGNOSTICS_READINESS_PASS"

DIAGNOSTIC_DOMAINS = {
    "EDGE Node Readiness", "LINK Gateway Readiness", "Source System Connectivity",
    "Connector Health", "Protocol Handshake", "Tag Mapping", "Asset / Location Mapping",
    "Sample Payload Preview", "Normalization Preview", "Local Buffer Status",
    "Delivery / ACK Status", "Retry / DLQ Status", "Audit Chain Status",
    "Evidence Chain Status", "Hardware Key / Site Binding", "Package Integrity",
    "Config Version", "Clock / Timezone", "Network Reachability",
    "Support Bundle Readiness", "Remote Engineer Review Checklist",
}
EDGE_FIELDS = {"edgeNodeId", "siteId", "projectId", "edgeVersion", "packageIntegrityStatus", "hardwareKeyStatus", "siteBindingStatus", "connectorCount", "connectorHealthSummary", "sourceSystemCount", "localBufferStatus", "offlineModeStatus", "configVersion", "lastHealthSnapshotAt", "clockStatus", "timezoneStatus", "networkReachabilityStatus", "supportBundleAvailable"}
LINK_FIELDS = {"linkGatewayId", "siteId", "projectId", "linkVersion", "deliveryChannelStatus", "lastDeliveryAt", "lastAckAt", "queueDepth", "retryCount", "dlqCount", "deliveryLatencyMs", "auditChainStatus", "evidenceChainStatus", "syncBatchStatus", "distributedTopologyStatus", "supportBundleReference"}
SOURCE_FIELDS = {"sourceSystemId", "sourceSystemName", "sourceSystemType", "connectorId", "integrationMethod", "connectivityStatus", "credentialStatus", "lastSeenAt", "lastSampleReceivedAt", "dataFreshnessStatus", "mappingStatus", "normalizationStatus", "riskFlags", "requiredEngineerAction"}
MAPPING_CHECKS = {"tagMappingStatus", "duplicateTagCount", "tagConflictCount", "missingAssetRefCount", "missingLocationRefCount", "unitNormalizationStatus", "timezoneNormalizationStatus", "qualityFlagStatus", "severityMappingStatus", "alarmMappingStatus", "faultCandidateMappingStatus", "workOrderTriggerMappingStatus", "hmiLocatorMappingStatus"}
PAYLOAD_FIELDS = {"samplePayloadId", "sourceSystemId", "connectorId", "rawPayloadPreviewAllowed", "redactedPayloadPreviewRequired", "payloadHash", "normalizedEnvelopePreview", "normalizationStatus", "validationErrors", "qualityFlags", "timestampNormalizationStatus", "severityNormalizationStatus", "evidenceRef"}
DELIVERY_FIELDS = {"deliveryChannelId", "deliveryStatus", "lastDeliveryAt", "lastAckAt", "ackRequired", "retryPolicyStatus", "queueDepth", "retryCount", "dlqCount", "backpressureStatus", "payloadHashRequired", "auditChainRequired", "evidenceChainRequired"}
SUPPORT_FIELDS = {"supportBundleId", "siteId", "edgeNodeId", "linkGatewayId", "createdAt", "includedDiagnostics", "redactionStatus", "customerIdentifierRedacted", "localPathRedacted", "packageIntegrityStatus", "signatureStatus", "uploadAllowed", "remoteSupportAllowed", "retentionClass"}
CHECKLIST = {
    "Confirm deployment mode", "Confirm site / project binding", "Confirm hardware key status",
    "Confirm EDGE package integrity", "Confirm LINK package integrity",
    "Confirm connector matrix selected", "Confirm source system profiles",
    "Confirm mapping draft", "Confirm tag mapping risks",
    "Confirm asset/location mapping risks", "Confirm sample payload preview readiness",
    "Confirm normalization preview readiness", "Confirm delivery / ack readiness",
    "Confirm retry / DLQ readiness", "Confirm audit/evidence chain readiness",
    "Confirm support bundle readiness", "Confirm runtime activation remains disabled",
    "Confirm production activation remains disabled", "Confirm customer approval required before activation",
}
CUSTOMER_FUNCTIONS = {
    "Work Order Management, auto + manual", "Asset Registry, full lifecycle tracking",
    "Preventive Maintenance Scheduler", "Spare Parts / Inventory Management",
    "Vendor / Contract Management", "Graphics HMI to locate Equipment",
    "Existing system onboarding", "Engineer commissioning diagnostics",
    "Remote overseas deployment", "Distributed independent installation",
}
EDGE_REQUIREMENTS = {"Engineer commissioning CLI", "Connector health diagnostics", "Source system connectivity diagnostics", "Protocol handshake diagnostics", "Tag mapping diagnostics", "Asset/location mapping diagnostics", "Sample payload preview", "Normalization preview", "Local buffer diagnostics", "Hardware-key / site-binding diagnostics", "Offline package integrity diagnostics", "Support bundle export", "Timezone / clock check", "Network reachability check"}
LINK_REQUIREMENTS = {"LINK gateway diagnostics", "Delivery / ACK diagnostics", "Retry / DLQ diagnostics", "Audit/evidence chain diagnostics", "Sync batch diagnostics", "Distributed topology diagnostics", "Deployment package status", "Remote support bundle contract", "Support bundle ingestion / reference", "Delivery channel backpressure status"}
SAFETY_EXPECTED = {
    "readOnly": True, "runtimeActivation": False, "productionActivation": False, "dbWrite": False,
    "approvalExecution": False, "deploymentExecution": False, "remoteCommandExecution": False,
    "diagnosticsExecution": False, "connectorExecution": False, "deviceConnection": False,
    "edgeRuntimeCall": False, "linkRuntimeCall": False, "oneAdapterIntroduced": False,
    "customerIdentifierLeakage": False, "localAbsolutePathLeakage": False,
}
ALLOWED_CHANGED_PREFIXES = (
    "AN_VANTARIS_ONE/projections/airport-engineer-commissioning-diagnostics-readiness.v1.json",
    "AN_VANTARIS_ONE/registries/airport-engineer-commissioning-diagnostics-readiness-registry.v1.json",
    "ONE_AIRPORT_GA_R8_ENGINEER_COMMISSIONING_DIAGNOSTICS_READINESS_REPORT.md",
    "AN_VANTARIS_ONE/tests/",
    "scripts/validation/validate-one-airport-ga-r8-engineer-commissioning-diagnostics-readiness.py",
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
    if "airport engineer commissioning readiness" in last_subject:
        paths.update(line for line in _run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines() if line)
    return paths


def _run_validator(script: str) -> subprocess.CompletedProcess[str]:
    return _run([_python(), script], env={"PYTHONPATH": "AN_VANTARIS_IBMS-backend:AN_VANTARIS_ONE", "IBMS_LOCAL_SMOKE": "true"})


def main() -> int:
    checks: list[tuple[str, bool]] = []
    errors: list[str] = []
    projection, projection_error = _load_json(PROJECTION)
    registry, registry_error = _load_json(REGISTRY)
    projection_text = PROJECTION.read_text(encoding="utf-8") if PROJECTION.exists() else ""
    registry_text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    stakeholder_text = "\n".join([projection_text, registry_text, report_text])

    checks.append(("GA-R8 projection artifact exists", PROJECTION.is_file() and not projection_error))
    checks.append(("GA-R8 registry exists", REGISTRY.is_file() and not registry_error))
    checks.append(("GA-R8 report exists", REPORT.is_file()))
    if projection_error:
        errors.append(f"projection json invalid: {projection_error}")
    if registry_error:
        errors.append(f"registry json invalid: {registry_error}")

    metadata = projection.get("metadata", {})
    checks.append(("Projection metadata contains platform = VANTARIS ONE", metadata.get("platform") == "VANTARIS ONE"))
    checks.append(("Projection metadata contains industryProjection = airport", metadata.get("industryProjection") == "airport"))
    checks.append(("Projection safety flags are correct", all(metadata.get(k) is v for k, v in SAFETY_EXPECTED.items() if k in metadata)))

    domains = {item.get("domainName") for item in projection.get("diagnosticsDomainCatalog", [])}
    checklist = {item.get("checkName") for item in projection.get("remoteEngineerReviewChecklist", [])}
    functions = {item.get("function") for item in projection.get("customerCoreFunctionDiagnosticImpact", [])}
    shared = projection.get("sharedFoundationInterfaceRequirements", {})
    safety = projection.get("safetyPosture", {})

    checks.append(("diagnosticsDomainCatalog includes all required diagnostic domains", DIAGNOSTIC_DOMAINS.issubset(domains)))
    checks.append(("edgeDiagnosticRequirements includes all required future fields", EDGE_FIELDS.issubset(set(projection.get("edgeDiagnosticRequirements", {}).get("requiredFutureFields", [])))))
    checks.append(("linkDiagnosticRequirements includes all required future fields", LINK_FIELDS.issubset(set(projection.get("linkDiagnosticRequirements", {}).get("requiredFutureFields", [])))))
    checks.append(("sourceSystemDiagnosticRequirements exists", SOURCE_FIELDS.issubset(set(projection.get("sourceSystemDiagnosticRequirements", {}).get("requiredFutureFields", [])))))
    checks.append(("mappingDiagnosticRequirements includes all required mapping checks", MAPPING_CHECKS.issubset(set(projection.get("mappingDiagnosticRequirements", {}).get("requiredChecks", [])))))
    payload = projection.get("payloadAndNormalizationPreviewRequirements", {})
    checks.append(("payloadAndNormalizationPreviewRequirements exists and states no runtime payload collection is added", PAYLOAD_FIELDS.issubset(set(payload.get("requiredFutureFields", []))) and "No runtime payload collection is added" in payload.get("statement", "")))
    checks.append(("deliveryDiagnosticsRequirements exists", DELIVERY_FIELDS.issubset(set(projection.get("deliveryDiagnosticsRequirements", {}).get("requiredFutureFields", [])))))
    support = projection.get("supportBundleRequirements", {})
    checks.append(("supportBundleRequirements exists and states support bundle generation/execution is not implemented in GA-R8", SUPPORT_FIELDS.issubset(set(support.get("requiredFutureFields", []))) and "Support bundle generation/execution is not implemented in GA-R8" in support.get("statement", "")))
    checks.append(("remoteEngineerReviewChecklist includes all required checklist items", CHECKLIST.issubset(checklist)))
    checks.append(("customerCoreFunctionDiagnosticImpact includes all 10 customer core functions", CUSTOMER_FUNCTIONS.issubset(functions)))
    checks.append(("sharedFoundationInterfaceRequirements includes required EDGE requirements", EDGE_REQUIREMENTS.issubset(set(shared.get("edgeRequirements", [])))))
    checks.append(("sharedFoundationInterfaceRequirements includes required LINK requirements", LINK_REQUIREMENTS.issubset(set(shared.get("linkRequirements", [])))))
    checks.append(("safetyPosture confirms no runtime/production/DB/approval/deployment/remote command/diagnostics/connector/device execution", all(safety.get(k) is v for k, v in SAFETY_EXPECTED.items())))
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
    checks.append(("Changes limited to GA-R8 projection scope", not disallowed and not forbidden))
    if disallowed:
        errors.append(f"changes outside GA-R8 scope: {', '.join(sorted(disallowed))}")
    if forbidden:
        errors.append(f"forbidden paths touched: {', '.join(sorted(forbidden))}")

    airport_client_text = AIRPORT_CLIENT.read_text(encoding="utf-8") if AIRPORT_CLIENT.exists() else ""
    checks.append(("No POST/PUT/PATCH/DELETE Airport API client methods added", not any(method in airport_client_text for method in FORBIDDEN_CLIENT_METHODS)))
    checks.append(("No customer identifier leakage", not any(term in stakeholder_text for term in LEAKAGE_TERMS[2:])))
    checks.append(("No local absolute path leakage in stakeholder-facing artifacts", not any(term in stakeholder_text for term in LEAKAGE_TERMS[:2])))
    checks.append(("Projection JSON validation passes", not projection_error and metadata.get("projectionId") == "airport-engineer-commissioning-diagnostics-readiness.v1"))
    checks.append(("Registry JSON validation passes", not registry_error and registry.get("validationMarker") == PASS_MARKER))
    checks.append(("Report contains PASS marker", PASS_MARKER in report_text))

    regression_specs = (
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

    print("ONE_AIRPORT_GA_R8_ENGINEER_COMMISSIONING_DIAGNOSTICS_READINESS_VALIDATION")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors or not all(ok for _, ok in checks):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ONE_AIRPORT_GA_R8_ENGINEER_COMMISSIONING_DIAGNOSTICS_READINESS_FAIL")
        return 1
    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
