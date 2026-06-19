"""Read migration readiness gate evaluation."""
from __future__ import annotations

from typing import Any, Mapping

from .evidence import EvidenceSnapshot, validate_evidence_structure
from .models import GateResult


def _gate_meta(policy: Mapping[str, Any], gate_code: str) -> tuple[str, str]:
    for item in policy.get("gates", ()):
        if item.get("gateCode") == gate_code:
            return str(item.get("severity", "REVIEW")), str(item.get("remediationCategory", "GENERAL"))
    return "REVIEW", "GENERAL"


def _result(
    policy: Mapping[str, Any],
    gate_code: str,
    *,
    status: str,
    observed: str,
    required: str,
    blocking: bool,
) -> GateResult:
    severity, remediation = _gate_meta(policy, gate_code)
    return GateResult(
        gate_code=gate_code,
        status=status,
        severity=severity,
        observed_value=observed,
        required_value=required,
        blocking=blocking,
        remediation_category=remediation,
    )


def evaluate_gates(
    evidence: Mapping[str, Any],
    snapshot: EvidenceSnapshot,
    policy: Mapping[str, Any],
    *,
    determinism_confirmed: bool,
) -> tuple[GateResult, ...]:
    coverage = policy["coverageThresholds"]
    ratios = policy["ratioThresholds"]
    relationships = policy["relationshipThresholds"]
    supported_mapping = tuple(policy.get("supportedMappingVersions", ()))
    total_records = max(snapshot.total_records, 1)
    review_ratio = (snapshot.review_count / total_records) * 100
    warning_ratio = (snapshot.warning_count / total_records) * 100
    structure_ok, structure_reason = validate_evidence_structure(evidence, policy)

    gates = [
        _result(
            policy,
            "PRIVACY_GATE",
            status="PASS" if snapshot.prohibited_field_count == 0 and snapshot.privacy_status == "PASS" else "FAIL",
            observed=f"detectedCount={snapshot.prohibited_field_count};status={snapshot.privacy_status}",
            required="detectedCount=0;status=PASS",
            blocking=True,
        ),
        _result(
            policy,
            "EVIDENCE_FORMAT_GATE",
            status="PASS" if structure_ok else "FAIL",
            observed=structure_reason,
            required="required evidence structure present",
            blocking=True,
        ),
        _result(
            policy,
            "DETERMINISM_GATE",
            status="PASS" if determinism_confirmed and snapshot.evidence_digest else "FAIL",
            observed=f"determinismConfirmed={determinism_confirmed};digestPresent={bool(snapshot.evidence_digest)}",
            required="determinismConfirmed=true;digestPresent=true",
            blocking=True,
        ),
        _result(
            policy,
            "MAPPING_VERSION_GATE",
            status="PASS" if snapshot.mapping_version in supported_mapping else "FAIL",
            observed=snapshot.mapping_version,
            required=",".join(supported_mapping),
            blocking=True,
        ),
        _result(
            policy,
            "REQUIRED_FIELD_COVERAGE_GATE",
            status="PASS" if snapshot.required_coverage_min_percent >= coverage["requiredFieldCoverageMinimumPercent"] else "FAIL",
            observed=f"{snapshot.required_coverage_min_percent:.2f}%",
            required=f">={coverage['requiredFieldCoverageMinimumPercent']:.2f}%",
            blocking=True,
        ),
        _result(
            policy,
            "SAFE_SOURCE_COVERAGE_GATE",
            status="PASS" if snapshot.safe_coverage_min_percent >= coverage["safeSourceFieldCoverageMinimumPercent"] else "FAIL",
            observed=f"{snapshot.safe_coverage_min_percent:.2f}%",
            required=f">={coverage['safeSourceFieldCoverageMinimumPercent']:.2f}%",
            blocking=True,
        ),
        _result(
            policy,
            "SOURCE_IDENTITY_GATE",
            status="FAIL" if snapshot.source_identity_collision or snapshot.missing_stable_source_id else "PASS",
            observed=f"collision={snapshot.source_identity_collision};missingStableSourceId={snapshot.missing_stable_source_id}",
            required="collision=false;missingStableSourceId=false",
            blocking=True,
        ),
        _result(
            policy,
            "GLOBAL_ID_GATE",
            status="FAIL" if snapshot.global_id_collision else "PASS",
            observed=str(snapshot.global_id_collision),
            required="false",
            blocking=True,
        ),
        _result(
            policy,
            "TENANT_SCOPE_GATE",
            status="FAIL" if snapshot.tenant_scope_blocker else "PASS",
            observed=str(snapshot.tenant_scope_blocker),
            required="false",
            blocking=True,
        ),
        _result(
            policy,
            "SITE_SCOPE_GATE",
            status="FAIL" if snapshot.site_scope_blocker else "PASS",
            observed=str(snapshot.site_scope_blocker),
            required="false",
            blocking=True,
        ),
        _result(
            policy,
            "POINT_PARENT_GATE",
            status="FAIL" if snapshot.point_parent_blocker else "PASS",
            observed=str(snapshot.point_parent_blocker),
            required="false",
            blocking=True,
        ),
        _result(
            policy,
            "HAS_POINT_PARITY_GATE",
            status="PASS" if snapshot.has_point_parity_valid else "FAIL",
            observed=f"hasPointPassMatchesProjectedPoints={snapshot.has_point_parity_valid}",
            required="true",
            blocking=True,
        ),
        _result(
            policy,
            "ORPHAN_RELATIONSHIP_GATE",
            status="PASS" if snapshot.orphan_relationship_count <= relationships["orphanRelationshipCountMaximum"] else "FAIL",
            observed=str(snapshot.orphan_relationship_count),
            required=f"<={relationships['orphanRelationshipCountMaximum']}",
            blocking=True,
        ),
        _result(
            policy,
            "UNRESOLVED_RELATIONSHIP_GATE",
            status=(
                "PASS"
                if snapshot.unresolved_relationship_count <= relationships["unresolvedRelationshipCountMaximumForLimitedValidation"]
                else "FAIL"
            ),
            observed=str(snapshot.unresolved_relationship_count),
            required=(
                f"limited<={relationships['unresolvedRelationshipCountMaximumForLimitedValidation']};"
                f"candidate<={relationships['unresolvedRelationshipCountMaximumForReadMigrationCandidate']}"
            ),
            blocking=snapshot.unresolved_relationship_count > relationships["unresolvedRelationshipCountMaximumForReadMigrationCandidate"],
        ),
        _result(
            policy,
            "DUPLICATE_RELATIONSHIP_GATE",
            status=(
                "PASS"
                if snapshot.duplicate_canonical_relationship_count <= relationships["duplicateCanonicalRelationshipCountMaximum"]
                else "FAIL"
            ),
            observed=(
                f"duplicateCanonical={snapshot.duplicate_canonical_relationship_count};"
                f"duplicateHasPointPairs={snapshot.duplicate_has_point_pair_count}"
            ),
            required=f"duplicateCanonical<={relationships['duplicateCanonicalRelationshipCountMaximum']}",
            blocking=True,
        ),
        _result(
            policy,
            "REVIEW_RATIO_GATE",
            status="PASS" if review_ratio <= ratios["reviewRatioMaximumPercentForLimitedValidation"] else "REVIEW",
            observed=f"{review_ratio:.2f}%",
            required=f"<={ratios['reviewRatioMaximumPercentForLimitedValidation']:.2f}%",
            blocking=False,
        ),
        _result(
            policy,
            "WARNING_RATIO_GATE",
            status="PASS" if warning_ratio <= ratios["warningRatioMaximumPercentForLimitedValidation"] else "REVIEW",
            observed=f"{warning_ratio:.2f}%",
            required=f"<={ratios['warningRatioMaximumPercentForLimitedValidation']:.2f}%",
            blocking=False,
        ),
        _result(
            policy,
            "EVIDENCE_CLASSIFICATION_GATE",
            status="PASS" if snapshot.classification != "UNKNOWN" else "FAIL",
            observed=snapshot.classification,
            required="not UNKNOWN",
            blocking=True,
        ),
        _result(
            policy,
            "WRITE_CUTOVER_PROHIBITION_GATE",
            status="PASS" if snapshot.cutover_decision != "READY_FOR_WRITE_CUTOVER" else "FAIL",
            observed=snapshot.cutover_decision,
            required="not READY_FOR_WRITE_CUTOVER",
            blocking=True,
        ),
    ]
    return tuple(gates)
