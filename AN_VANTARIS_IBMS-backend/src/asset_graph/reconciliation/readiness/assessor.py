"""Policy-driven read migration readiness assessment."""
from __future__ import annotations

from typing import Any, Mapping

from ..models import sha256_digest
from .evidence import extract_evidence_snapshot, validate_evidence_structure
from .gates import evaluate_gates
from .models import GateResult, ReadinessAssessment

ASSESSMENT_NAME = "VANTARIS ONE Asset Graph Read Migration Readiness Assessment"
ASSESSMENT_VERSION = "1.0.0"
AUTHORITY = "ONE-A5-P1-16I"


def _determine_decision(
    gate_results: tuple[GateResult, ...],
    classification: str,
    policy: Mapping[str, Any],
) -> str:
    ceilings = policy.get("classificationDecisionCeiling", {})
    ceiling = ceilings.get(classification, "NOT_READY")
    if any(gate.gate_code == "EVIDENCE_FORMAT_GATE" and gate.status == "FAIL" for gate in gate_results):
        return "INPUT_REJECTED"
    if any(gate.gate_code == "PRIVACY_GATE" and gate.status == "FAIL" for gate in gate_results):
        return "INPUT_REJECTED"
    hard_blocker_codes = set(policy.get("hardBlockerGateCodes", ()))
    if any(gate.gate_code in hard_blocker_codes and gate.status == "FAIL" and gate.blocking for gate in gate_results):
        return "NOT_READY"
    if classification == "SYNTHETIC_NEGATIVE_TEST":
        return "NOT_READY"
    if classification == "UNKNOWN":
        return "NOT_READY"
    review_or_fail = [gate for gate in gate_results if gate.status in {"FAIL", "REVIEW"} and not gate.blocking]
    blocking_fail = [gate for gate in gate_results if gate.status == "FAIL" and gate.blocking]
    if blocking_fail:
        return "NOT_READY"
    if review_or_fail:
        candidate = "READY_WITH_REMEDIATION"
    else:
        candidate = ceiling
    decision_order = (
        "NOT_READY",
        "READY_WITH_REMEDIATION",
        "READY_FOR_LIMITED_READ_VALIDATION",
        "READY_FOR_READ_MIGRATION_CANDIDATE",
    )
    candidate_index = decision_order.index(candidate) if candidate in decision_order else 0
    ceiling_index = decision_order.index(ceiling) if ceiling in decision_order else 0
    return decision_order[min(candidate_index, ceiling_index)]


def _required_remediations(gate_results: tuple[GateResult, ...]) -> tuple[str, ...]:
    items = []
    for gate in gate_results:
        if gate.status in {"FAIL", "REVIEW"}:
            items.append(f"{gate.remediation_category}:{gate.gate_code}")
    return tuple(sorted(set(items)))


def assess_readiness(
    evidence: Mapping[str, Any],
    policy: Mapping[str, Any],
    *,
    determinism_confirmed: bool = False,
) -> ReadinessAssessment:
    structure_ok, _ = validate_evidence_structure(evidence, policy)
    snapshot = extract_evidence_snapshot(evidence, policy)
    gate_results = evaluate_gates(
        evidence,
        snapshot,
        policy,
        determinism_confirmed=determinism_confirmed and structure_ok,
    )
    decision = _determine_decision(gate_results, snapshot.classification, policy)
    if decision in policy.get("forbiddenDecisions", ()):
        decision = "NOT_READY"
    hard_blocker_count = sum(
        1 for gate in gate_results if gate.blocking and gate.status == "FAIL"
    )
    passed_gate_count = sum(1 for gate in gate_results if gate.status == "PASS")
    failed_gate_count = sum(1 for gate in gate_results if gate.status == "FAIL")
    payload = {
        "assessmentName": ASSESSMENT_NAME,
        "assessmentVersion": ASSESSMENT_VERSION,
        "authority": AUTHORITY,
        "policyVersion": str(policy.get("policyVersion", "")),
        "evidenceDigest": snapshot.evidence_digest,
        "evidenceClassification": snapshot.classification,
        "decision": decision,
        "hardBlockerCount": hard_blocker_count,
        "reviewCount": snapshot.review_count,
        "warningCount": snapshot.warning_count,
        "passedGateCount": passed_gate_count,
        "failedGateCount": failed_gate_count,
        "gateResults": [item.serialize() for item in gate_results],
        "coverageSummary": {
            "requiredFieldCoverageMinimumPercent": snapshot.required_coverage_min_percent,
            "safeSourceFieldCoverageMinimumPercent": snapshot.safe_coverage_min_percent,
            "optionalFieldCoverageMinimumPercent": snapshot.optional_coverage_min_percent,
        },
        "identitySummary": {
            "globalIdCollision": snapshot.global_id_collision,
            "sourceIdentityCollision": snapshot.source_identity_collision,
            "missingStableSourceId": snapshot.missing_stable_source_id,
        },
        "scopeSummary": {
            "tenantScopeBlocker": snapshot.tenant_scope_blocker,
            "siteScopeBlocker": snapshot.site_scope_blocker,
        },
        "relationshipSummary": {
            "projectedPointCount": snapshot.projected_point_count,
            "canonicalRelationshipCount": snapshot.canonical_relationship_count,
            "relationshipResultCount": snapshot.relationship_result_count,
            "unresolvedRelationshipCount": snapshot.unresolved_relationship_count,
            "duplicateCanonicalRelationshipCount": snapshot.duplicate_canonical_relationship_count,
            "duplicateHasPointPairCount": snapshot.duplicate_has_point_pair_count,
            "hasPointParityValid": snapshot.has_point_parity_valid,
            "orphanRelationshipCount": snapshot.orphan_relationship_count,
        },
        "requiredRemediations": list(_required_remediations(gate_results)),
        "writeCutoverStatus": str(policy.get("writeCutoverStatus", "NOT_READY_FOR_WRITE_CUTOVER")),
    }
    return ReadinessAssessment(
        assessment_name=ASSESSMENT_NAME,
        assessment_version=ASSESSMENT_VERSION,
        authority=AUTHORITY,
        policy_version=str(policy.get("policyVersion", "")),
        evidence_digest=snapshot.evidence_digest,
        evidence_classification=snapshot.classification,
        decision=decision,
        hard_blocker_count=hard_blocker_count,
        review_count=snapshot.review_count,
        warning_count=snapshot.warning_count,
        passed_gate_count=passed_gate_count,
        failed_gate_count=failed_gate_count,
        gate_results=gate_results,
        coverage_summary=payload["coverageSummary"],
        identity_summary=payload["identitySummary"],
        scope_summary=payload["scopeSummary"],
        relationship_summary=payload["relationshipSummary"],
        required_remediations=tuple(payload["requiredRemediations"]),
        write_cutover_status=payload["writeCutoverStatus"],
        result_digest=sha256_digest(payload),
    )
