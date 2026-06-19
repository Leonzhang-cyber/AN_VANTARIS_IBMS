#!/usr/bin/env python3
"""Validate the VANTARIS ONE audit and idempotency declaration contracts."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "AN_VANTARIS_ONE/registries/audit-contract.v1.json"
IDEMPOTENCY = ROOT / "AN_VANTARIS_ONE/registries/idempotency-contract.v1.json"
DECLARATIONS = ROOT / "AN_VANTARIS_ONE/registries/backend-route-control-declarations.v1.json"
INVENTORY = ROOT / "AN_VANTARIS_ONE/registries/backend-route-inventory.v1.json"
POLICY = ROOT / "AN_VANTARIS_ONE/registries/backend-route-policy.v1.json"
PACKAGES = ROOT / "AN_VANTARIS_ONE/registries/package-registry.v1.json"
PERMISSIONS = ROOT / "AN_VANTARIS_ONE/registries/permission-registry.v1.json"

AUDIT_REQUIREMENTS = {"REQUIRED", "CONDITIONAL", "NOT_REQUIRED", "REVIEW_REQUIRED", "TEST_ONLY"}
RETRY_SAFETY = {"SAFE", "SAFE_WITH_IDEMPOTENCY", "UNSAFE", "NOT_APPLICABLE", "REVIEW_REQUIRED"}
CURRENT_AUDIT = {"DECLARED_AND_IMPLEMENTED", "PARTIAL", "LEGACY_LOCAL_ONLY", "NOT_DECLARED", "NOT_APPLICABLE", "UNKNOWN"}
CURRENT_IDEM = {"DECLARED_AND_IMPLEMENTED", "PARTIAL", "NOT_DECLARED", "NOT_REQUIRED", "UNKNOWN"}
IMPLEMENTATION = {
    "ALREADY_COMPLIANT", "AUDIT_IMPLEMENTATION_REQUIRED",
    "IDEMPOTENCY_IMPLEMENTATION_REQUIRED", "AUDIT_AND_IDEMPOTENCY_REQUIRED",
    "LEGACY_COMPATIBILITY_REQUIRED", "REVIEW_REQUIRED", "NON_PRODUCTION",
}
REVIEW_TYPES = {
    "SENSITIVE_READ_CLASSIFICATION", "AUDIT_EVENT_CLASS_AMBIGUITY",
    "AUDIT_FAILURE_POLICY", "IDEMPOTENCY_REQUIREMENT", "RETRY_OWNER",
    "EXPORT_CLASSIFICATION", "LEGACY_LOCAL_AUDIT", "AUTHENTICATION_AUDIT",
    "PERMISSION_DEPENDENCY", "DYNAMIC_BEHAVIOR",
}


def load(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.name}: {exc}")
        return {}


def expected_summary(rows: list[dict], reviews: list[dict]) -> dict:
    audit_counts = Counter(row.get("auditEventClass") for row in rows)
    idem_counts = Counter(row.get("idempotencyOperationClass") for row in rows)
    module_counts = Counter(row.get("owningModule") for row in rows)
    package_counts = Counter(row.get("packageId") or "UNRESOLVED" for row in rows)
    status_counts = Counter(row.get("implementationStatus") for row in rows)
    return {
        "totalRoutes": len(rows),
        "productionAndLegacyRoutes": sum(row.get("runtimeClass") in {"PRODUCTION", "LEGACY"} for row in rows),
        "testOnlyRoutes": sum(row.get("runtimeClass") == "TEST_ONLY" for row in rows),
        "routesRequiringAudit": sum(row.get("auditRequirement") == "REQUIRED" for row in rows),
        "routesWithConditionalAudit": sum(row.get("auditRequirement") == "CONDITIONAL" for row in rows),
        "routesNotRequiringAudit": sum(row.get("auditRequirement") == "NOT_REQUIRED" for row in rows),
        "sensitiveReadRoutes": sum(row.get("sensitiveRead") is True or row.get("sensitiveRead") == "review" for row in rows),
        "exportRoutes": sum(row.get("exportOperation") is True for row in rows),
        "controlRoutes": sum(row.get("operationPolicy") == "CONTROL" for row in rows),
        "intakeRoutes": sum(row.get("operationPolicy") == "INTAKE" for row in rows),
        "routesRequiringIdempotency": sum(row.get("idempotencyKeyRequired") is True for row in rows),
        "routesSafeWithoutIdempotency": sum(row.get("idempotencyOperationClass") == "NOT_REQUIRED_SAFE_READ" for row in rows),
        "routesUnsafeLegacyCompatibility": sum(row.get("idempotencyOperationClass") == "UNSAFE_LEGACY_COMPATIBILITY" for row in rows),
        "routesRequiringCorrelation": sum(row.get("correlationRequired") is True for row in rows),
        "routesRequiringTrace": sum(row.get("traceRequired") is True for row in rows),
        "routesAlreadyCompliant": status_counts["ALREADY_COMPLIANT"],
        "auditImplementationRequired": status_counts["AUDIT_IMPLEMENTATION_REQUIRED"],
        "idempotencyImplementationRequired": status_counts["IDEMPOTENCY_IMPLEMENTATION_REQUIRED"],
        "auditAndIdempotencyRequired": status_counts["AUDIT_AND_IDEMPOTENCY_REQUIRED"],
        "legacyLocalAuditRoutes": sum(row.get("currentAuditState") == "LEGACY_LOCAL_ONLY" for row in rows),
        "reviewQueueCount": len(reviews),
        "routesByAuditEventClass": dict(sorted(audit_counts.items())),
        "routesByIdempotencyClass": dict(sorted(idem_counts.items())),
        "routesByOwningModule": dict(sorted(module_counts.items())),
        "routesByPackage": dict(sorted(package_counts.items())),
    }


def deterministic(path: Path, value: dict) -> bool:
    return path.read_text(encoding="utf-8") == json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    errors: list[str] = []
    for path in (AUDIT, IDEMPOTENCY, DECLARATIONS):
        if not path.is_file():
            errors.append(f"missing registry: {path.name}")
    audit = load(AUDIT, errors) if AUDIT.is_file() else {}
    idem = load(IDEMPOTENCY, errors) if IDEMPOTENCY.is_file() else {}
    declarations = load(DECLARATIONS, errors) if DECLARATIONS.is_file() else {}
    inventory = load(INVENTORY, errors)
    route_policy = load(POLICY, errors)
    packages = load(PACKAGES, errors)
    permissions = load(PERMISSIONS, errors)

    audit_top = {
        "registryName", "registryVersion", "authority", "status", "generatedAtPolicy",
        "auditPrinciples", "auditEventClasses", "actorTypes", "targetTypes",
        "outcomeTypes", "severityLevels", "requiredFields", "sensitiveDataPolicy",
        "evidenceRelationshipPolicy", "retentionClasses", "deliveryPolicy",
        "failurePolicy", "compatibilityPolicy",
    }
    idem_top = {
        "registryName", "registryVersion", "authority", "status", "generatedAtPolicy",
        "principles", "operationClasses", "idempotencyKeyPolicy",
        "requestFingerprintPolicy", "replayPolicy", "retentionPolicy",
        "conflictPolicy", "retryPolicy", "serviceIdentityPolicy", "compatibilityPolicy",
    }
    declaration_top = {
        "registryName", "registryVersion", "authority", "status",
        "generatedAtPolicy", "sourceInventory", "sourcePolicyRegistry",
        "summary", "routeDeclarations", "reviewQueue",
    }
    if set(audit) != audit_top:
        errors.append("audit contract invalid top-level fields")
    if set(idem) != idem_top:
        errors.append("idempotency contract invalid top-level fields")
    if set(declarations) != declaration_top:
        errors.append("route declarations invalid top-level fields")
    fixed = [
        (audit, "registryName", "VANTARIS ONE Audit Contract"),
        (audit, "status", "FROZEN_FOR_AUDIT_IMPLEMENTATION"),
        (idem, "registryName", "VANTARIS ONE Idempotency Contract"),
        (idem, "status", "FROZEN_FOR_IDEMPOTENCY_IMPLEMENTATION"),
        (declarations, "registryName", "VANTARIS ONE Backend Route Control Declarations"),
        (declarations, "status", "FROZEN_CONTROL_DECLARATION_BASELINE"),
    ]
    for doc, field, value in fixed:
        if doc.get(field) != value:
            errors.append(f"invalid {field}: expected {value}")
    for doc in (audit, idem, declarations):
        if doc.get("registryVersion") != "1.0.0" or doc.get("authority") != "ONE-A5-P0-07":
            errors.append("invalid registry version or authority")
        if doc.get("generatedAtPolicy") != "STATIC_ARCHITECTURE_BASELINE":
            errors.append("invalid generatedAtPolicy")

    event_rows = audit.get("auditEventClasses", [])
    event_ids = {row.get("eventClass") for row in event_rows}
    required_events = {
        "AUTHENTICATION", "AUTHORIZATION_DECISION", "SECURITY_ADMINISTRATION",
        "PACKAGE_LIFECYCLE", "ENTITLEMENT_LIFECYCLE", "CONFIGURATION_CHANGE",
        "CANONICAL_OBJECT_CREATE", "CANONICAL_OBJECT_UPDATE", "CANONICAL_OBJECT_RETIRE",
        "BUSINESS_STATE_TRANSITION", "WORK_LIFECYCLE", "MAINTENANCE_LIFECYCLE",
        "FAULT_ACTION", "EVIDENCE_ACTION", "REPORT_EXECUTION", "EXPORT",
        "CONTROL_OPERATION", "INTEGRATION_OPERATION", "AI_REQUEST", "AI_REVIEW",
        "MODEL_LIFECYCLE", "SENSITIVE_READ", "SYSTEM_HEALTH_CONTROL",
    }
    if not required_events <= event_ids or len(event_ids) != len(event_rows):
        errors.append("audit event classes incomplete or duplicated")
    event_fields = {
        "eventClass", "owner", "defaultSeverity", "actorRequired", "targetRequired",
        "beforeStateRequired", "afterStateRequired", "reasonRequired",
        "permissionRequired", "tenantRequired", "siteRequired", "evidenceEligible",
        "retentionClass", "synchronousEmissionRequired", "failureBehavior",
    }
    if any(set(row) != event_fields for row in event_rows):
        errors.append("audit event class structure invalid")

    required_audit_fields = {
        "auditId", "eventClass", "action", "occurredAt", "actorType", "actorId",
        "serviceIdentityId", "tenantId", "siteId", "subjectType", "subjectId",
        "targetType", "targetId", "routeId", "requestId", "traceId",
        "correlationId", "permission", "packageId", "outcome", "denialCode",
        "reasonCode", "previousStateDigest", "resultingStateDigest",
        "sourceIpClass", "userAgentClass", "contractVersion",
        "metadataClassification", "evidenceReferenceIds",
    }
    if {row.get("field") for row in audit.get("requiredFields", [])} != required_audit_fields:
        errors.append("AuditRecord required fields incomplete")
    sensitive = audit.get("sensitiveDataPolicy", {})
    required_sensitive_classes = {
        "PROHIBITED", "REDACTED", "HASHED", "TOKENIZED_REFERENCE",
        "CLASSIFIED_METADATA", "ALLOWED_NON_SENSITIVE",
    }
    if set(sensitive.get("classificationClasses", [])) != required_sensitive_classes:
        errors.append("sensitive-data classifications incomplete")
    required_prohibited = {
        "PASSWORDS", "PRIVATE_KEYS", "SEED_PHRASES", "BEARER_TOKENS",
        "REFRESH_TOKENS", "COMPLETE_AUTHENTICATION_HEADERS",
        "DATABASE_CREDENTIALS", "RAW_LICENSE_TOKENS",
        "CONFIDENTIAL_FILE_CONTENTS", "UNRESTRICTED_TELEMETRY_PAYLOADS",
        "COMPLETE_PERSONAL_DATA_RECORDS",
    }
    if not required_prohibited <= set(sensitive.get("prohibitedContent", [])):
        errors.append("prohibited sensitive content list incomplete")
    evidence = audit.get("evidenceRelationshipPolicy", {})
    if evidence.get("auditRecordIsEvidenceRecord") is not False or evidence.get("relationshipMechanism") != "EvidenceReference":
        errors.append("AuditRecord is conflated with EvidenceRecord")
    if audit.get("compatibilityPolicy", {}).get("legacyReportsJsonl") != "LEGACY_COMPATIBILITY_ONLY_NOT_TARGET_SYSTEM_OF_RECORD":
        errors.append("Reports JSONL incorrectly represented as target audit system of record")

    failure_modes = set(audit.get("failurePolicy", {}).get("modes", []))
    required_failures = {
        "FAIL_CLOSED", "FAIL_OPERATION_WITH_AUDIT_ERROR",
        "QUEUE_DURABLY_THEN_CONTINUE", "BEST_EFFORT_NON_SENSITIVE_READ",
        "NOT_APPLICABLE",
    }
    if failure_modes != required_failures:
        errors.append("audit failure policies incomplete")

    idem_rows = idem.get("operationClasses", [])
    idem_ids = {row.get("operationClass") for row in idem_rows}
    required_idem = {
        "NOT_REQUIRED_SAFE_READ", "REQUIRED_CREATE", "REQUIRED_INTAKE",
        "REQUIRED_COMMAND", "REQUIRED_CONTROL", "REQUIRED_EXPORT_JOB",
        "OPTIONAL_UPDATE_WITH_VERSION", "STATE_TRANSITION_GUARDED",
        "UNSAFE_LEGACY_COMPATIBILITY", "TEST_ONLY", "REVIEW_REQUIRED",
    }
    if idem_ids != required_idem or len(idem_ids) != len(idem_rows):
        errors.append("idempotency operation classes incomplete or duplicated")
    idem_fields = {
        "operationClass", "keyRequired", "fingerprintRequired",
        "resultReplayAllowed", "inProgressBehavior", "conflictResponse",
        "retentionClass", "retryOwner", "auditRequired", "serviceIdentityAllowed",
    }
    if any(set(row) != idem_fields for row in idem_rows):
        errors.append("idempotency operation class structure invalid")
    if idem.get("idempotencyKeyPolicy", {}).get("acceptedHeaderNameRecommendation") != "Idempotency-Key":
        errors.append("idempotency header recommendation invalid")

    correlation = audit.get("compatibilityPolicy", {}).get("correlationAndTracePolicy", {})
    required_correlation = {
        "requestId", "traceId", "correlationId", "causationId", "sourceEnvelopeId",
        "sourceEventId", "WorkOrderIntentId", "EvidenceReferenceId", "auditId",
        "idempotencyKey", "interchangeability",
    }
    if set(correlation) != required_correlation or correlation.get("interchangeability") != "PROHIBITED":
        errors.append("correlation and trace policy incomplete")

    inventory_by_id = {row.get("routeId"): row for row in inventory.get("routes", [])}
    policy_by_id = {row.get("routeId"): row for row in route_policy.get("routePolicies", [])}
    package_ids = {row.get("packageId") for row in packages.get("packages", [])}
    permission_ids = {row.get("permission") for row in permissions.get("permissions", [])}
    permission_gap_ids = {
        row.get("routeId") for row in route_policy.get("reviewQueue", [])
        if row.get("reviewType") == "PERMISSION_GAP"
    }
    rows = declarations.get("routeDeclarations", [])
    row_ids = [row.get("routeId") for row in rows]
    if len(row_ids) != len(set(row_ids)) or set(row_ids) != set(inventory_by_id):
        errors.append("route declaration coverage mismatch")
    if len(rows) != 181:
        errors.append("route declarations must cover all 181 routes")
    if row_ids != sorted(row_ids):
        errors.append("route declarations are not deterministically sorted")
    route_fields = {
        "routeId", "fullPath", "methods", "runtimeClass", "owningModule",
        "packageId", "operationPolicy", "requiredPermissions", "auditRequirement",
        "auditEventClass", "auditFailurePolicy", "sensitiveRead", "exportOperation",
        "idempotencyRequirement", "idempotencyOperationClass",
        "idempotencyKeyRequired", "retrySafety", "retryOwner",
        "correlationRequired", "traceRequired", "requestIdRequired",
        "evidenceEligible", "currentAuditState", "currentIdempotencyState",
        "implementationStatus", "compatibilityStage", "remediationWorkstream",
        "proposedImplementationTask", "scannerConfidence", "reviewReason", "notes",
    }
    for row in rows:
        rid = row.get("routeId")
        source = inventory_by_id.get(rid, {})
        pol = policy_by_id.get(rid, {})
        if set(row) != route_fields:
            errors.append(f"{rid}: invalid declaration structure")
        if row.get("fullPath") != source.get("fullPath") or row.get("methods") != source.get("methods"):
            errors.append(f"{rid}: route path or methods differ from inventory")
        if row.get("packageId") and row.get("packageId") not in package_ids:
            errors.append(f"{rid}: unknown package ID")
        if set(row.get("requiredPermissions", [])) - permission_ids:
            errors.append(f"{rid}: unknown permission")
        if row.get("auditEventClass") not in event_ids:
            errors.append(f"{rid}: unknown audit event class")
        if row.get("auditFailurePolicy") not in failure_modes:
            errors.append(f"{rid}: unknown audit failure policy")
        if row.get("idempotencyOperationClass") not in idem_ids:
            errors.append(f"{rid}: unknown idempotency operation class")
        if row.get("auditRequirement") not in AUDIT_REQUIREMENTS:
            errors.append(f"{rid}: invalid audit requirement")
        if row.get("retrySafety") not in RETRY_SAFETY:
            errors.append(f"{rid}: invalid retry safety")
        if row.get("currentAuditState") not in CURRENT_AUDIT:
            errors.append(f"{rid}: invalid current audit state")
        if row.get("currentIdempotencyState") not in CURRENT_IDEM:
            errors.append(f"{rid}: invalid current idempotency state")
        if row.get("implementationStatus") not in IMPLEMENTATION:
            errors.append(f"{rid}: invalid implementation status")
        if row.get("runtimeClass") == "TEST_ONLY":
            if row.get("auditRequirement") != "TEST_ONLY" or row.get("idempotencyOperationClass") != "TEST_ONLY" or row.get("implementationStatus") != "NON_PRODUCTION":
                errors.append(f"{rid}: test route classification invalid")
            continue
        if pol.get("operationPolicy") in {"CREATE", "UPDATE", "DELETE", "CONTROL", "EXPORT", "INTAKE"}:
            if row.get("auditRequirement") != "REQUIRED":
                errors.append(f"{rid}: mutation/control/export lacks required audit")
        if pol.get("operationPolicy") in {"INTAKE", "CONTROL"}:
            if not row.get("idempotencyKeyRequired") or row.get("idempotencyOperationClass") not in {"REQUIRED_INTAKE", "REQUIRED_COMMAND", "REQUIRED_CONTROL"}:
                errors.append(f"{rid}: intake/control lacks idempotency classification")
        if pol.get("operationPolicy") == "EXPORT" and not row.get("exportOperation"):
            errors.append(f"{rid}: export classification missing")
        if pol.get("operationPolicy") == "AUTHENTICATION":
            if row.get("auditEventClass") != "AUTHENTICATION" or row.get("auditRequirement") != "REQUIRED":
                errors.append(f"{rid}: authentication audit policy invalid")
        if pol.get("authenticationClass") == "PUBLIC" and pol.get("operationPolicy") == "HEALTH_PUBLIC":
            if row.get("sensitiveRead") is True:
                errors.append(f"{rid}: public health classified as sensitive detailed audit")
        if row.get("implementationStatus") == "ALREADY_COMPLIANT":
            if row.get("auditRequirement") != "NOT_REQUIRED" or row.get("idempotencyKeyRequired"):
                errors.append(f"{rid}: compliant claim lacks static no-control evidence")
        if row.get("currentAuditState") == "LEGACY_LOCAL_ONLY":
            if "/reports/" not in row.get("fullPath", "") or rid not in {
                key for key, value in inventory_by_id.items()
                if value.get("fullPath") in {"/api/v1/reports/query", "/api/v1/reports/export/manifest"}
            }:
                errors.append(f"{rid}: legacy local audit classification unsupported")
        if rid in permission_gap_ids:
            if row.get("proposedImplementationTask") != "ONE-A5-P0-07-PERMISSION-DEPENDENCY":
                errors.append(f"{rid}: permission dependency task missing")
        if not any("no audit or idempotency runtime was implemented" in note for note in row.get("notes", [])):
            errors.append(f"{rid}: runtime honesty note missing")

    reviews = declarations.get("reviewQueue", [])
    review_ids = [row.get("reviewId") for row in reviews]
    if len(review_ids) != len(set(review_ids)):
        errors.append("duplicate review ID")
    review_route_ids = {row.get("routeId") for row in reviews}
    for review in reviews:
        if review.get("routeId") not in inventory_by_id:
            errors.append(f"{review.get('reviewId')}: unknown review route")
        if review.get("reviewType") not in REVIEW_TYPES:
            errors.append(f"{review.get('reviewId')}: invalid review type")
    for rid in permission_gap_ids:
        if not any(row.get("routeId") == rid and row.get("reviewType") == "PERMISSION_DEPENDENCY" for row in reviews):
            errors.append(f"{rid}: permission dependency review missing")
    if not review_route_ids <= set(inventory_by_id):
        errors.append("review queue contains unknown route IDs")
    if declarations.get("summary") != expected_summary(rows, reviews):
        errors.append("route declaration summary mismatch")

    serialized = json.dumps({"audit": audit, "idempotency": idem, "declarations": declarations}, sort_keys=True)
    if re.search(r"\b20\d{2}-\d{2}-\d{2}\b", serialized) or "/Users/" in serialized:
        errors.append("timestamp or absolute user path found")
    if re.search(r"https?://|localhost|127\.0\.0\.1", serialized, re.IGNORECASE):
        errors.append("live endpoint found")
    if re.search(r"UFMS.{0,40}(endpoint|payload|authentication|pagination|error response)", serialized, re.IGNORECASE):
        errors.append("live UFMS implementation detail found")
    if any(path.is_file() and doc and not deterministic(path, doc) for path, doc in (
        (AUDIT, audit), (IDEMPOTENCY, idem), (DECLARATIONS, declarations)
    )):
        errors.append("registry JSON serialization is not deterministic")

    checks = [
        ("Audit contract structure", not any("audit contract" in item.lower() or "audit event class" in item.lower() or "AuditRecord required" in item for item in errors)),
        ("Idempotency contract structure", not any("idempotency contract" in item.lower() or "idempotency operation class" in item.lower() or "header recommendation" in item.lower() for item in errors)),
        ("Route declaration coverage", not any("coverage" in item.lower() or "181 routes" in item or "path or methods" in item.lower() for item in errors)),
        ("Audit classifications", not any("audit requirement" in item.lower() or "audit failure" in item.lower() or "mutation/control/export" in item.lower() or "authentication audit" in item.lower() for item in errors)),
        ("Idempotency classifications", not any("idempotency classification" in item.lower() or "intake/control" in item.lower() for item in errors)),
        ("Sensitive-data policy", not any("sensitive" in item.lower() or "prohibited" in item.lower() for item in errors)),
        ("Correlation policy", not any("correlation" in item.lower() or "trace policy" in item.lower() for item in errors)),
        ("Permission dependencies", not any("permission dependency" in item.lower() for item in errors)),
        ("Review queue", not any("review" in item.lower() for item in errors)),
        ("Runtime honesty", not any("runtime honesty" in item.lower() or "compliant claim" in item.lower() or "system of record" in item.lower() for item in errors)),
    ]
    print("[ONE AUDIT IDEMPOTENCY CONTRACT VALIDATION]")
    for label, passed in checks:
        print(f"{label}: {'PASS' if passed else 'FAIL'}")
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        print("ONE_AUDIT_IDEMPOTENCY_CONTRACT_FAIL")
        return 1
    print("ONE_AUDIT_IDEMPOTENCY_CONTRACT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
