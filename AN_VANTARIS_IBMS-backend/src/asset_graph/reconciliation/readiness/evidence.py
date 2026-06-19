"""Aggregate evidence snapshot extraction for readiness assessment."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping


def _parse_percent(value: Any) -> float:
    text = str(value or "").strip().replace("%", "")
    if not text:
        return 0.0
    return float(text)


def _contains_any(text: str, tokens: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(token.lower() in lowered for token in tokens)


@dataclass(frozen=True)
class EvidenceSnapshot:
    evidence_digest: str
    classification: str
    mapping_version: str
    projected_device_count: int
    projected_point_count: int
    source_device_count: int
    total_records: int
    required_coverage_min_percent: float
    safe_coverage_min_percent: float
    optional_coverage_min_percent: float
    review_count: int
    warning_count: int
    blocker_count: int
    prohibited_field_count: int
    privacy_status: str
    global_id_collision: bool
    source_identity_collision: bool
    missing_stable_source_id: bool
    tenant_scope_blocker: bool
    site_scope_blocker: bool
    point_parent_blocker: bool
    unresolved_relationship_count: int
    duplicate_canonical_relationship_count: int
    duplicate_has_point_pair_count: int
    orphan_relationship_count: int
    has_point_parity_valid: bool
    canonical_relationship_count: int
    relationship_result_count: int
    cutover_decision: str


def classify_evidence(evidence: Mapping[str, Any], policy: Mapping[str, Any]) -> str:
    rules = policy.get("classificationRules", {})
    source_summary = evidence.get("sourceSummary", {})
    notes = str(source_summary.get("notes", ""))
    export_policy = str(evidence.get("inputPackage", {}).get("exportPolicy", ""))
    assessment_type = str(evidence.get("assessmentType", ""))
    combined = " ".join((notes, export_policy, assessment_type, json.dumps(source_summary, sort_keys=True)))
    if _contains_any(combined, tuple(rules.get("realSanitizedSignals", ()))):
        return "REAL_SANITIZED_EVIDENCE"
    if _contains_any(combined, tuple(rules.get("syntheticNegativeSignals", ()))):
        return "SYNTHETIC_NEGATIVE_TEST"
    if _contains_any(combined, tuple(rules.get("syntheticRepresentativeSignals", ()))):
        return "SYNTHETIC_REPRESENTATIVE_ONLY"
    return "UNKNOWN"


def extract_evidence_snapshot(evidence: Mapping[str, Any], policy: Mapping[str, Any]) -> EvidenceSnapshot:
    projection = evidence.get("projectionSummary", {})
    reconciliation = evidence.get("reconciliationSummary", {})
    source_summary = evidence.get("sourceSummary", {})
    relationship = evidence.get("relationshipMetrics", {})
    prohibited = evidence.get("prohibitedFieldResults", {})
    blockers = tuple(str(item) for item in evidence.get("blockers", ()))
    field_rows = evidence.get("fieldCoverage", ())
    required_values = [_parse_percent(row.get("requiredFieldCoverage")) for row in field_rows if isinstance(row, Mapping)]
    safe_values = [_parse_percent(row.get("safeSourceFieldCoverage")) for row in field_rows if isinstance(row, Mapping)]
    optional_values = [_parse_percent(row.get("optionalFieldCoverage")) for row in field_rows if isinstance(row, Mapping)]
    has_point = relationship.get("relationshipTypeCounts", {}).get("HAS_POINT", {})
    orphan_count = 0
    if any("ORPHAN" in blocker for blocker in blockers):
        orphan_count = 1
    return EvidenceSnapshot(
        evidence_digest=str(evidence.get("resultDigest", "")),
        classification=classify_evidence(evidence, policy),
        mapping_version=str(evidence.get("mappingVersion", "")),
        projected_device_count=int(projection.get("projectedDeviceCount", 0)),
        projected_point_count=int(projection.get("projectedPointCount", 0)),
        source_device_count=int(source_summary.get("deviceCount", 0)),
        total_records=int(reconciliation.get("totalRecords", 0)),
        required_coverage_min_percent=min(required_values) if required_values else 0.0,
        safe_coverage_min_percent=min(safe_values) if safe_values else 0.0,
        optional_coverage_min_percent=min(optional_values) if optional_values else 0.0,
        review_count=int(reconciliation.get("reviewCount", 0)),
        warning_count=int(reconciliation.get("warningCount", 0)),
        blocker_count=int(reconciliation.get("blockerCount", 0)),
        prohibited_field_count=int(prohibited.get("detectedCount", 0)),
        privacy_status=str(prohibited.get("status", "UNKNOWN")),
        global_id_collision=any("GLOBAL_ID_COLLISION" in item for item in blockers),
        source_identity_collision=any(
            token in item for item in blockers for token in ("SOURCE_IDENTITY_COLLISION", "DUPLICATE_SOURCE_IDENTITY")
        ),
        missing_stable_source_id=any("MISSING_STABLE_SOURCE_ID" in item for item in blockers),
        tenant_scope_blocker=any("TENANT" in item for item in blockers),
        site_scope_blocker=any("SITE" in item for item in blockers),
        point_parent_blocker=any("POINT_DEVICE_REFERENCE" in item for item in blockers),
        unresolved_relationship_count=int(relationship.get("unresolvedRelationshipCount", 0)),
        duplicate_canonical_relationship_count=int(relationship.get("duplicateCanonicalRelationshipCount", 0)),
        duplicate_has_point_pair_count=int(relationship.get("duplicateHasPointPairCount", 0)),
        orphan_relationship_count=orphan_count,
        has_point_parity_valid=int(has_point.get("passCount", 0)) == int(projection.get("projectedPointCount", 0)),
        canonical_relationship_count=int(relationship.get("canonicalRelationshipCount", 0)),
        relationship_result_count=int(relationship.get("relationshipResultCount", 0)),
        cutover_decision=str(evidence.get("cutoverDecision", "")),
    )


def validate_evidence_structure(evidence: Mapping[str, Any], policy: Mapping[str, Any]) -> tuple[bool, str]:
    required = tuple(policy.get("requiredEvidenceFields", ()))
    missing = [field for field in required if field not in evidence]
    if missing:
        return False, f"missing fields: {', '.join(missing)}"
    if not str(evidence.get("resultDigest", "")).strip():
        return False, "missing resultDigest"
    return True, "valid"
