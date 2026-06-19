"""Build migration control inputs from aggregate readiness and evidence summaries."""
from __future__ import annotations

from typing import Any, Mapping

from .models import ApprovalRecord, ControlInput, ExecutionScope


def build_control_input(
    *,
    readiness_assessment: Mapping[str, Any],
    evidence: Mapping[str, Any],
    execution_scope: ExecutionScope,
    approvals: tuple[ApprovalRecord, ...] = (),
    requested_operations: tuple[str, ...] = (),
    migration_intent: str = "LIMITED_READ_VALIDATION",
    deterministic_verification_confirmed: bool = True,
    evaluation_instant: str = "2026-06-19T00:00:00Z",
) -> ControlInput:
    source_summary = evidence.get("sourceSummary", {})
    projection_summary = evidence.get("projectionSummary", {})
    reconciliation = evidence.get("reconciliationSummary", {})
    relationship = readiness_assessment.get("relationshipSummary", evidence.get("relationshipMetrics", {}))
    return ControlInput(
        readiness_result_digest=str(readiness_assessment.get("resultDigest", "")),
        readiness_policy_version=str(readiness_assessment.get("policyVersion", "")),
        readiness_decision=str(readiness_assessment.get("decision", "")),
        evidence_classification=str(readiness_assessment.get("evidenceClassification", "")),
        evidence_digest=str(readiness_assessment.get("evidenceDigest", evidence.get("resultDigest", ""))),
        mapping_version=str(evidence.get("mappingVersion", "")),
        source_count_summary={
            "deviceCount": int(source_summary.get("deviceCount", 0)),
            "recordCount": int(source_summary.get("recordCount", 0)),
        },
        projected_count_summary={
            "projectedDeviceCount": int(projection_summary.get("projectedDeviceCount", 0)),
            "projectedPointCount": int(projection_summary.get("projectedPointCount", 0)),
        },
        blocker_count=int(reconciliation.get("blockerCount", 0)),
        review_count=int(readiness_assessment.get("reviewCount", reconciliation.get("reviewCount", 0))),
        warning_count=int(readiness_assessment.get("warningCount", reconciliation.get("warningCount", 0))),
        hard_blocker_count=int(readiness_assessment.get("hardBlockerCount", 0)),
        relationship_invariant_summary={
            "hasPointParityValid": bool(relationship.get("hasPointParityValid", True)),
            "unresolvedRelationshipCount": int(relationship.get("unresolvedRelationshipCount", 0)),
            "duplicateCanonicalRelationshipCount": int(relationship.get("duplicateCanonicalRelationshipCount", 0)),
            "duplicateHasPointPairCount": int(relationship.get("duplicateHasPointPairCount", 0)),
            "relationshipResultCount": int(relationship.get("relationshipResultCount", 0)),
            "canonicalRelationshipCount": int(relationship.get("canonicalRelationshipCount", 0)),
        },
        deterministic_verification_confirmed=deterministic_verification_confirmed,
        write_cutover_status=str(readiness_assessment.get("writeCutoverStatus", "NOT_READY_FOR_WRITE_CUTOVER")),
        requested_operations=requested_operations,
        migration_intent=migration_intent,
        execution_scope=execution_scope,
        approvals=approvals,
        evaluation_instant=evaluation_instant,
    )
