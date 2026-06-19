"""Offline deterministic evidence runner for legacy Device reconciliation."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

from src.asset_graph.compatibility import (
    LegacyDeviceReadCompatibilityFacade,
    LegacyDeviceSnapshot,
    LegacyFieldSnapshot,
    ProjectionContext,
)
from src.asset_graph.reconciliation.constants import DEFAULT_CUTOVER_DECISION, MAX_RECONCILIATION_BATCH_SIZE
from src.asset_graph.reconciliation import (
    DeviceProjectionReconciliationService,
    ReconciliationInput,
    canonical_json,
    sha256_digest,
)
from src.asset_graph.reconciliation.relationship_reporting import collect_relationship_metrics
from src.asset_graph.reconciliation.site_context import (
    SiteContextError,
    collect_scope_metrics,
    merge_site_context,
    parse_site_context,
)

AUTHORITY = "ONE-A5-P1-16B"
FORMAT_NAME = "VANTARIS ONE Legacy Device Reconciliation Evidence Package"
FORMAT_VERSION = "1.0.0"
FORMAT_POLICY = "SANITIZED_OFFLINE_READ_ONLY"
EVIDENCE_NAME = "VANTARIS ONE Device Projection Reconciliation Evidence"
EVIDENCE_VERSION = "1.0.0"
EVIDENCE_STATUS = "OFFLINE_RECONCILIATION_EVIDENCE"
GENERATED_AT_POLICY = "CALLER_CONTROLLED_NO_HIDDEN_TIMESTAMP"

REQUIRED_TOP_LEVEL = {
    "formatName",
    "formatVersion",
    "exportPolicy",
    "tenantContext",
    "siteContext",
    "sourceSystemContext",
    "mappingVersion",
    "devices",
    "standardFields",
    "declaredRedactions",
    "sourceSummary",
}

ALLOWED_DEVICE_FIELDS = {
    "sourceId",
    "sourceNamespace",
    "tenantId",
    "siteId",
    "name",
    "code",
    "description",
    "deviceType",
    "manufacturer",
    "model",
    "serialNumber",
    "lifecycleStatus",
    "operationalStatus",
    "sourceTagName",
    "locationReference",
    "createdAt",
    "updatedAt",
    "approvedMetadata",
}

ALLOWED_STANDARD_FIELDS = {
    "sourceId",
    "deviceSourceId",
    "sourceNamespace",
    "name",
    "displayName",
    "fieldType",
    "dataType",
    "unit",
    "accessMode",
    "lifecycleStatus",
    "sourceTagName",
    "approvedMetadata",
}

PROHIBITED_KEY = re.compile(
    r"(password|secret|token|bearer|api[_-]?key|private[_-]?key|credential|mqtt|opc|"
    r"connection[_-]?string|database[_-]?url|telemetry|current[_-]?value|history|"
    r"command[_-]?payload|runtime[_-]?state|session)",
    re.IGNORECASE,
)
PROHIBITED_VALUE = re.compile(
    r"(bearer\s+[a-z0-9\-\._~\+\/]+=*|-----BEGIN .*PRIVATE KEY-----|"
    r"[a-z]+:\/\/[^\/\s:@]+:[^@\s]+@|password\s*[:=]|token\s*[:=]|api[_-]?key\s*[:=])",
    re.IGNORECASE,
)
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
ALLOWED_EXPORT_KEYS = {"recordCount", "deviceCount", "standardFieldCount", "notes"}


@dataclass(frozen=True)
class EvidencePackageError(Exception):
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def _safe_rel(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.name)


def _parse_timestamp(value: Any, *, fallback: datetime) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if not isinstance(value, str) or not value.strip():
        return fallback
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _ensure_safe_identifier(value: str, label: str) -> None:
    if not value or not SAFE_ID.match(value):
        raise EvidencePackageError("INVALID_IDENTIFIER", f"{label} is malformed")


def _scan_prohibited(value: Any, *, path: str = "") -> Optional[str]:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_str = str(key)
            key_path = f"{path}.{key_str}" if path else key_str
            if PROHIBITED_KEY.search(key_str):
                return f"prohibited field detected at {key_path}"
            result = _scan_prohibited(item, path=key_path)
            if result:
                return result
        return None
    if isinstance(value, (list, tuple)):
        for idx, item in enumerate(value):
            result = _scan_prohibited(item, path=f"{path}[{idx}]")
            if result:
                return result
        return None
    if isinstance(value, str) and PROHIBITED_VALUE.search(value):
        return f"prohibited value detected at {path or 'root'}"
    return None


def _validate_top_level(package: Mapping[str, Any]) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL - set(package))
    if missing:
        raise EvidencePackageError("MISSING_TOP_LEVEL_FIELDS", "required top-level fields are missing")
    if package.get("formatName") != FORMAT_NAME:
        raise EvidencePackageError("UNSUPPORTED_FORMAT", "formatName is unsupported")
    if package.get("formatVersion") != FORMAT_VERSION:
        raise EvidencePackageError("UNSUPPORTED_VERSION", "formatVersion is unsupported")
    if package.get("exportPolicy") != FORMAT_POLICY:
        raise EvidencePackageError("UNSUPPORTED_EXPORT_POLICY", "exportPolicy is unsupported")
    tenant_context = package.get("tenantContext")
    source_context = package.get("sourceSystemContext")
    if not isinstance(tenant_context, Mapping) or not tenant_context.get("tenantId"):
        raise EvidencePackageError("MISSING_TENANT_CONTEXT", "tenant context is required")
    if not isinstance(source_context, Mapping) or not source_context.get("sourceSystemId"):
        raise EvidencePackageError("MISSING_SOURCE_SYSTEM_CONTEXT", "source-system context is required")
    if not isinstance(package.get("devices"), list):
        raise EvidencePackageError("INVALID_DEVICES", "devices must be a list")
    if not isinstance(package.get("standardFields"), list):
        raise EvidencePackageError("INVALID_STANDARD_FIELDS", "standardFields must be a list")
    if not isinstance(package.get("declaredRedactions"), list):
        raise EvidencePackageError("INVALID_REDACTIONS", "declaredRedactions must be a list")
    summary = package.get("sourceSummary")
    if not isinstance(summary, Mapping):
        raise EvidencePackageError("INVALID_SOURCE_SUMMARY", "sourceSummary must be an object")
    forbidden_export_keys = sorted(set(summary) - ALLOWED_EXPORT_KEYS)
    if forbidden_export_keys:
        raise EvidencePackageError("INVALID_SOURCE_SUMMARY_KEYS", "sourceSummary contains unsupported keys")


def _status_to_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    text = str(value).strip().upper()
    mapping = {
        "UNAVAILABLE": 0,
        "AVAILABLE": 1,
        "DEGRADED": 2,
        "UNKNOWN": 99,
    }
    return mapping.get(text)


def _build_context(package: Mapping[str, Any]) -> ProjectionContext:
    tenant_context = package["tenantContext"]
    site_context = package["siteContext"]
    source_context = package["sourceSystemContext"]
    tenant_id = str(tenant_context.get("tenantId", "")).strip()
    source_system_id = str(source_context.get("sourceSystemId", "")).strip()
    source_namespace = str(source_context.get("sourceNamespace", "legacy.iot.devices")).strip()
    _ensure_safe_identifier(tenant_id, "tenantId")
    _ensure_safe_identifier(source_system_id, "sourceSystemId")
    _ensure_safe_identifier(source_namespace.replace("/", "_"), "sourceNamespace")
    try:
        site_base = parse_site_context(site_context, tenant_id=tenant_id)
    except SiteContextError as exc:
        raise EvidencePackageError("INVALID_SITE_CONTEXT", str(exc)) from exc
    for site_value in site_base.allowed_site_ids:
        _ensure_safe_identifier(site_value, "allowedSiteId")
    if site_base.primary_site_id:
        _ensure_safe_identifier(site_base.primary_site_id, "primarySiteId")
    return merge_site_context(
        site_base,
        tenant_id=tenant_id,
        source_system_id=source_system_id,
        source_namespace=source_namespace,
        default_device_type="CONTROLLER",
    )


def _record_prohibited_scan(
    devices: Iterable[Mapping[str, Any]],
    fields: Iterable[Mapping[str, Any]],
) -> None:
    for idx, row in enumerate(devices):
        result = _scan_prohibited(row, path=f"devices[{idx}]")
        if result:
            raise EvidencePackageError("PROHIBITED_FIELD_PRESENT", result)
    for idx, row in enumerate(fields):
        result = _scan_prohibited(row, path=f"standardFields[{idx}]")
        if result:
            raise EvidencePackageError("PROHIBITED_FIELD_PRESENT", result)


def _normalize_devices(
    package: Mapping[str, Any],
    context: ProjectionContext,
    now: datetime,
) -> tuple[list[LegacyDeviceSnapshot], list[dict[str, str]]]:
    devices: list[LegacyDeviceSnapshot] = []
    blockers: list[dict[str, str]] = []
    seen_identity: set[tuple[str, str, str]] = set()
    for index, raw in enumerate(package["devices"]):
        if not isinstance(raw, Mapping):
            blockers.append({"type": "BLOCKER", "code": "INVALID_DEVICE_RECORD", "message": f"device[{index}] must be object"})
            continue
        unknown = sorted(set(raw) - ALLOWED_DEVICE_FIELDS)
        if unknown:
            blockers.append({"type": "BLOCKER", "code": "UNAPPROVED_DEVICE_FIELDS", "message": f"device[{index}] contains unapproved fields"})
            continue
        source_id = str(raw.get("sourceId", "")).strip()
        if not source_id:
            blockers.append({"type": "BLOCKER", "code": "MISSING_STABLE_SOURCE_ID", "message": f"device[{index}] missing stable sourceId"})
            continue
        if not SAFE_ID.match(source_id):
            blockers.append({"type": "BLOCKER", "code": "MALFORMED_SOURCE_ID", "message": f"device[{index}] has malformed sourceId"})
            continue
        source_ns = str(raw.get("sourceNamespace", context.source_namespace)).strip() or context.source_namespace
        identity_key = (context.tenant_id, source_ns, source_id)
        if identity_key in seen_identity:
            blockers.append({"type": "BLOCKER", "code": "DUPLICATE_SOURCE_IDENTITY", "message": f"device[{index}] duplicates source identity"})
        seen_identity.add(identity_key)
        tenant_id = str(raw.get("tenantId", context.tenant_id)).strip() or context.tenant_id
        site_id_raw = raw.get("siteId", context.site_id)
        site_id = str(site_id_raw).strip() if site_id_raw else None
        if tenant_id != context.tenant_id:
            blockers.append({"type": "BLOCKER", "code": "TENANT_SCOPE_MISMATCH", "message": f"device[{index}] tenant mismatch"})
        if site_id and not context.allows_record_site(site_id):
            blockers.append({"type": "BLOCKER", "code": "SITE_SCOPE_MISMATCH", "message": f"device[{index}] site mismatch"})
        parent_reference = None
        if isinstance(raw.get("locationReference"), Mapping):
            parent_reference = str(raw["locationReference"].get("parentSourceId", "")).strip() or None
        elif raw.get("locationReference"):
            parent_reference = str(raw.get("locationReference")).strip() or None
        devices.append(
            LegacyDeviceSnapshot(
                source_id=source_id,
                device_name=str(raw.get("name", "")).strip() or f"Device-{source_id}",
                device_code=str(raw.get("code", "")).strip() or None,
                description=str(raw.get("description", "")).strip() or None,
                manufacturer=str(raw.get("manufacturer", "")).strip() or None,
                model=str(raw.get("model", "")).strip() or None,
                serial_number=str(raw.get("serialNumber", "")).strip() or None,
                device_type=str(raw.get("deviceType", "")).strip() or None,
                status=_status_to_int(raw.get("operationalStatus")),
                created_at=_parse_timestamp(raw.get("createdAt"), fallback=now),
                updated_at=_parse_timestamp(raw.get("updatedAt"), fallback=now),
                source_version=str(package.get("mappingVersion", "")).strip() or None,
                parent_reference=parent_reference,
                source_tenant_id=tenant_id,
                source_site_id=site_id,
            )
        )
    return devices, blockers


def _normalize_standard_fields(
    package: Mapping[str, Any],
    context: ProjectionContext,
) -> tuple[dict[str, tuple[LegacyFieldSnapshot, ...]], list[dict[str, str]]]:
    grouped: dict[str, list[LegacyFieldSnapshot]] = {}
    reviews: list[dict[str, str]] = []
    for index, raw in enumerate(package["standardFields"]):
        if not isinstance(raw, Mapping):
            reviews.append({"type": "REVIEW", "code": "INVALID_FIELD_RECORD", "message": f"standardFields[{index}] must be object"})
            continue
        unknown = sorted(set(raw) - ALLOWED_STANDARD_FIELDS)
        if unknown:
            reviews.append({"type": "REVIEW", "code": "UNAPPROVED_FIELD_KEYS", "message": f"standardFields[{index}] contains unapproved fields"})
            continue
        source_id = str(raw.get("sourceId", "")).strip()
        device_source_id = str(raw.get("deviceSourceId", "")).strip()
        if not source_id:
            reviews.append({"type": "REVIEW", "code": "MISSING_FIELD_SOURCE_ID", "message": f"standardFields[{index}] missing sourceId"})
            continue
        if not device_source_id:
            reviews.append({"type": "REVIEW", "code": "UNRESOLVED_PARENT", "message": f"standardFields[{index}] missing deviceSourceId"})
            continue
        field_type = str(raw.get("fieldType", raw.get("dataType", "string"))).strip().lower() or "string"
        access_mode = str(raw.get("accessMode", "READ_ONLY")).strip().upper() or "READ_ONLY"
        if field_type == "json":
            reviews.append({"type": "REVIEW", "code": "AMBIGUOUS_STANDARD_FIELD", "message": f"standardFields[{index}] ambiguous json field"})
        grouped.setdefault(device_source_id, []).append(
            LegacyFieldSnapshot(
                source_id=source_id,
                field_code=str(raw.get("name", source_id)).strip() or source_id,
                field_name=str(raw.get("displayName", raw.get("name", source_id))).strip() or source_id,
                field_type=field_type,
                unit=str(raw.get("unit", "")).strip() or None,
                description=str(raw.get("approvedMetadata", {}).get("description", "")).strip()
                if isinstance(raw.get("approvedMetadata"), Mapping)
                else None,
                access_mode=access_mode,
                is_configuration=bool(
                    isinstance(raw.get("approvedMetadata"), Mapping)
                    and raw.get("approvedMetadata", {}).get("classification") == "configuration"
                ),
                source_version=str(package.get("mappingVersion", "")).strip() or None,
            )
        )
    return {key: tuple(sorted(rows, key=lambda row: row.source_id)) for key, rows in grouped.items()}, reviews


def _collect_results(
    run: Any,
    validation_blockers: list[dict[str, str]],
    validation_reviews: list[dict[str, str]],
) -> dict[str, Any]:
    identity_results = []
    scope_results = []
    prohibited_detected = []
    point_class_counts: dict[str, int] = {}
    relationship_summary = {"pass": 0, "review": 0, "mismatch": 0}
    tag_total = 0
    for record in run.record_results:
        identity_results.append(
            {
                "sourceObjectId": record.source_object_id,
                "sourceIdentity": record.source_identity,
                "canonicalGlobalId": record.canonical_global_id,
                "projectionStatus": record.projection_status,
            }
        )
        tag_total += len(record.tag_keys)
        for point in record.point_results:
            point_class_counts[point.classification] = point_class_counts.get(point.classification, 0) + 1
        for rel in record.relationship_results:
            if rel.status == "PASS":
                relationship_summary["pass"] += 1
            elif rel.status == "REVIEW_REQUIRED":
                relationship_summary["review"] += 1
            else:
                relationship_summary["mismatch"] += 1
        if record.prohibited_fields_detected:
            prohibited_detected.append(
                {
                    "sourceObjectId": record.source_object_id,
                    "detectedCount": len(record.prohibited_fields_detected),
                    "detected": sorted(set(record.prohibited_fields_detected)),
                }
            )
        if record.cutover_blockers:
            for blocker in sorted(set(record.cutover_blockers)):
                if "TENANT" in blocker or "SITE" in blocker:
                    scope_results.append({"sourceObjectId": record.source_object_id, "result": blocker})
    blockers = []
    reviews = []
    warnings = []
    for item in validation_blockers:
        blockers.append(item["code"])
    for item in validation_reviews:
        reviews.append(item["code"])
    for record in run.record_results:
        warnings.extend(record.warnings)
        reviews.extend(record.reviews)
        reviews.extend(record.review_fields)
        blockers.extend(record.cutover_blockers)
    for dimension in run.dimension_results:
        if dimension.cutover_blocking and dimension.status != "PASS":
            blockers.append(dimension.dimension_id)
        elif dimension.status not in {"PASS", "NOT_APPLICABLE"}:
            reviews.append(dimension.dimension_id)
    return {
        "identityResults": sorted(identity_results, key=lambda row: row["sourceObjectId"] or ""),
        "scopeResults": sorted(scope_results, key=lambda row: row["sourceObjectId"]),
        "pointClassificationResults": {
            "totalPoints": sum(point_class_counts.values()),
            "counts": dict(sorted(point_class_counts.items())),
        },
        "tagResults": {
            "totalTags": tag_total,
            "tagNamespaceUniqueness": "PASS" if not any(item == "TAG_NAMESPACE_UNIQUENESS" for item in blockers) else "BLOCKED",
        },
        "relationshipResults": relationship_summary,
        "prohibitedFieldResults": {
            "status": "PASS" if not prohibited_detected else "REVIEW_REQUIRED",
            "records": prohibited_detected,
            "detectedCount": len(prohibited_detected),
        },
        "warnings": sorted(set(item for item in warnings if item)),
        "reviews": sorted(set(item for item in reviews if item)),
        "blockers": sorted(set(item for item in blockers if item)),
    }


def _cutover_decision(blockers: list[str], reviews: list[str], service_decision: str) -> str:
    if "REPEAT_RUN_NONDETERMINISM" in blockers:
        return "BLOCKED_BY_NONDETERMINISM"
    if any("IDENTITY" in item or "GLOBAL_ID" in item for item in blockers):
        return "BLOCKED_BY_IDENTITY"
    if any("TENANT" in item or "SITE" in item for item in blockers):
        return "BLOCKED_BY_SCOPE"
    if any("REQUIRED" in item for item in blockers):
        return "BLOCKED_BY_REQUIRED_FIELDS"
    if any("RELATIONSHIP" in item or "POINT_DEVICE_REFERENCE" in item for item in blockers):
        return "BLOCKED_BY_RELATIONSHIPS"
    if blockers:
        return DEFAULT_CUTOVER_DECISION
    if reviews:
        return "BLOCKED_BY_REVIEW"
    if service_decision == "READY_FOR_READ_MIGRATION":
        return "READY_FOR_READ_MIGRATION"
    return "READY_FOR_READ_MIGRATION"


def _report_digest_material(report: Mapping[str, Any]) -> Mapping[str, Any]:
    result = dict(report)
    result.pop("resultDigest", None)
    if isinstance(result.get("inputPackage"), Mapping):
        package_copy = dict(result["inputPackage"])
        package_copy.pop("path", None)
        result["inputPackage"] = package_copy
    return result


def run_device_reconciliation_evidence(
    *,
    root: Path,
    input_path: Path,
    output_path: Path,
    run_id: str,
    fail_on_blocker: bool = False,
    fail_on_review: bool = False,
) -> dict[str, Any]:
    if not run_id or not SAFE_ID.match(run_id):
        raise EvidencePackageError("INVALID_RUN_ID", "run-id is required and must be a safe identifier")
    package = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(package, Mapping):
        raise EvidencePackageError("INVALID_PACKAGE", "input package must be a JSON object")
    _validate_top_level(package)
    devices_raw = package["devices"]
    fields_raw = package["standardFields"]
    _record_prohibited_scan(devices_raw, fields_raw)
    context = _build_context(package)
    mapping_version = str(package.get("mappingVersion", "")).strip()
    _ensure_safe_identifier(mapping_version, "mappingVersion")
    if len(devices_raw) > MAX_RECONCILIATION_BATCH_SIZE:
        raise EvidencePackageError("BATCH_LIMIT_EXCEEDED", "device batch exceeds allowed maximum")
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    devices, validation_blockers = _normalize_devices(package, context, now)
    fields_by_device, validation_reviews = _normalize_standard_fields(package, context)
    reconciliation_input = ReconciliationInput(
        devices=tuple(devices),
        fields_by_device=fields_by_device,
        context=context,
        mapping_version=mapping_version,
        projection_configuration=tuple(),
    )
    facade = LegacyDeviceReadCompatibilityFacade()
    service = DeviceProjectionReconciliationService(facade=facade)
    run = service.reconcile_batch(run_id=run_id, reconciliation_input=reconciliation_input)
    collected = _collect_results(run, validation_blockers, validation_reviews)
    scope_metrics = collect_scope_metrics(
        context,
        package["devices"],
        validation_blockers,
        run.record_results,
    )
    blockers = list(collected["blockers"])
    reviews = list(collected["reviews"])
    relationship_metrics = collect_relationship_metrics(run, blockers=blockers)
    cutover_decision = _cutover_decision(blockers, reviews, run.cutover_decision)
    if cutover_decision == "READY_FOR_WRITE_CUTOVER":
        cutover_decision = DEFAULT_CUTOVER_DECISION
    input_digest = sha256_digest(
        {
            "formatName": package["formatName"],
            "formatVersion": package["formatVersion"],
            "exportPolicy": package["exportPolicy"],
            "tenantContext": package["tenantContext"],
            "siteContext": package["siteContext"],
            "sourceSystemContext": package["sourceSystemContext"],
            "mappingVersion": package["mappingVersion"],
            "devices": sorted(package["devices"], key=lambda item: str(item.get("sourceId", ""))),
            "standardFields": sorted(package["standardFields"], key=lambda item: str(item.get("sourceId", ""))),
            "declaredRedactions": sorted(str(item) for item in package["declaredRedactions"]),
            "sourceSummary": package["sourceSummary"],
        }
    )
    report = {
        "evidenceName": EVIDENCE_NAME,
        "evidenceVersion": EVIDENCE_VERSION,
        "authority": AUTHORITY,
        "status": EVIDENCE_STATUS,
        "generatedAtPolicy": GENERATED_AT_POLICY,
        "inputPackage": {
            "path": _safe_rel(input_path, root),
            "formatName": package["formatName"],
            "formatVersion": package["formatVersion"],
            "exportPolicy": package["exportPolicy"],
        },
        "inputDigest": input_digest,
        "mappingVersion": mapping_version,
        "tenantId": context.tenant_id,
        "siteId": context.site_id,
        "scopeMetrics": scope_metrics,
        "relationshipMetrics": relationship_metrics,
        "sourceSystemId": context.source_system_id,
        "runId": run_id,
        "sourceSummary": package["sourceSummary"],
        "projectionSummary": {
            "projectedDeviceCount": run.summary.projected_records,
            "projectedPointCount": run.projection_counts[1][1] if len(run.projection_counts) > 1 else 0,
            "projectedTagCount": run.projection_counts[2][1] if len(run.projection_counts) > 2 else 0,
            "projectedRelationshipCount": run.projection_counts[3][1] if len(run.projection_counts) > 3 else 0,
            "projectedRelationshipCountSemantics": relationship_metrics["relationshipResultCountSemantics"],
        },
        "reconciliationSummary": {
            "totalRecords": run.summary.total_records,
            "warningCount": run.summary.warning_count + len(collected["warnings"]),
            "reviewCount": run.summary.review_count + len(reviews),
            "blockerCount": run.summary.blocker_count + len(blockers),
        },
        "fieldCoverage": [
            {
                "sourceObjectId": record.source_object_id,
                "requiredFieldCoverage": record.field_coverage.required_field_coverage,
                "safeSourceFieldCoverage": record.field_coverage.safe_source_field_coverage,
                "optionalFieldCoverage": record.field_coverage.optional_field_coverage,
            }
            for record in sorted(run.record_results, key=lambda item: item.source_object_id)
        ],
        "identityResults": collected["identityResults"],
        "scopeResults": collected["scopeResults"],
        "pointClassificationResults": collected["pointClassificationResults"],
        "tagResults": collected["tagResults"],
        "relationshipResults": {
            **collected["relationshipResults"],
            "relationshipResultCount": relationship_metrics["relationshipResultCount"],
            "relationshipResultCountSemantics": relationship_metrics["relationshipResultCountSemantics"],
        },
        "prohibitedFieldResults": collected["prohibitedFieldResults"],
        "warnings": collected["warnings"],
        "reviews": reviews,
        "blockers": blockers,
        "cutoverDecision": cutover_decision,
        "validationStatement": (
            "Offline read-only evidence execution reused compatibility facade and reconciliation engine. "
            "No database access and no write cutover approval were performed."
        ),
    }
    report["resultDigest"] = sha256_digest(_report_digest_material(report))
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    if fail_on_blocker and report["blockers"]:
        raise EvidencePackageError("BLOCKERS_PRESENT", "blockers detected with --fail-on-blocker")
    if fail_on_review and report["reviews"]:
        raise EvidencePackageError("REVIEWS_PRESENT", "reviews detected with --fail-on-review")
    return report


def compare_evidence_reports(
    *,
    expected_path: Path,
    actual_path: Path,
    allow_run_id_only_diff: bool = False,
) -> tuple[bool, str]:
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    actual = json.loads(actual_path.read_text(encoding="utf-8"))
    if expected == actual:
        return True, "EVIDENCE_MATCH"
    expected_no_digest = dict(expected)
    actual_no_digest = dict(actual)
    expected_no_digest.pop("resultDigest", None)
    actual_no_digest.pop("resultDigest", None)
    if expected_no_digest == actual_no_digest:
        return False, "EVIDENCE_DIGEST_MISMATCH"
    if allow_run_id_only_diff:
        expected_no_run = dict(expected_no_digest)
        actual_no_run = dict(actual_no_digest)
        expected_no_run.pop("runId", None)
        actual_no_run.pop("runId", None)
        if expected_no_run == actual_no_run:
            return True, "EVIDENCE_MATCH_RUN_ID_IGNORED"
    return False, "EVIDENCE_MISMATCH"
