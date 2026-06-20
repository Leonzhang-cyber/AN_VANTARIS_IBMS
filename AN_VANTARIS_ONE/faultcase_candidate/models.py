"""Model builders for deterministic UFMS FaultCase candidate projections."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def _sorted(values: Sequence[str] | None) -> list[str]:
    return sorted(str(value) for value in values or ())


def build_faultcase_candidate(
    *,
    source_alarm_event_candidate_id: str,
    source_system_key: str,
    event_kind: str,
    event_category: str,
    event_severity: str,
    proposed_fault_case_type: str,
    proposed_fault_priority: str,
    proposed_fault_state: str,
    eligibility_state: str,
    blocking_reasons: Sequence[str],
    asset_resolution_state: str,
    point_resolution_state: str,
    location_resolution_state: str,
    source_system_review_state: str,
    downstream_creation_state: str,
    evidence_references: Sequence[Mapping[str, Any]] | None,
    decision_required: bool,
    review_reasons: Sequence[str],
) -> dict[str, Any]:
    candidate_id = sha256_digest(
        {
            "contractVersion": CONTRACT_VERSION,
            "sourceAlarmEventCandidateId": source_alarm_event_candidate_id,
            "sourceSystemKey": source_system_key,
            "proposedFaultCaseType": proposed_fault_case_type,
            "blockingReasons": sorted(blocking_reasons),
        }
    )
    candidate = {
        "candidateId": candidate_id,
        "sourceAlarmEventCandidateId": source_alarm_event_candidate_id,
        "sourceSystemKey": source_system_key,
        "eventKind": event_kind,
        "eventCategory": event_category,
        "eventSeverity": event_severity,
        "proposedFaultCaseType": proposed_fault_case_type,
        "proposedFaultPriority": proposed_fault_priority,
        "proposedFaultState": proposed_fault_state,
        "eligibilityState": eligibility_state,
        "blockingReasons": _sorted(blocking_reasons),
        "assetResolutionState": asset_resolution_state,
        "pointResolutionState": point_resolution_state,
        "locationResolutionState": location_resolution_state,
        "sourceSystemReviewState": source_system_review_state,
        "downstreamCreationState": downstream_creation_state,
        "evidenceReferences": list(evidence_references or ()),
        "decisionRequired": bool(decision_required),
        "reviewReasons": _sorted(review_reasons),
    }
    candidate["deterministicDigest"] = sha256_digest(
        {k: v for k, v in candidate.items() if k != "deterministicDigest"}
    )
    return candidate


def build_review_card(
    *,
    review_type: str,
    title: str,
    affected_source_system_keys: Sequence[str],
    affected_candidate_count: int,
    affected_device_evidence_count: int,
    allowed_decisions: Sequence[str],
    current_decision: str,
    blocking_effect: str,
    root_cause: str,
) -> dict[str, Any]:
    card = {
        "reviewCardId": sha256_digest(
            {
                "contractVersion": CONTRACT_VERSION,
                "reviewType": review_type,
                "affectedSourceSystemKeys": sorted(affected_source_system_keys),
            }
        ),
        "reviewType": review_type,
        "title": title,
        "affectedSourceSystemKeys": sorted(affected_source_system_keys),
        "affectedCandidateCount": int(affected_candidate_count),
        "affectedDeviceEvidenceCount": int(affected_device_evidence_count),
        "decisionRequired": True,
        "allowedDecisions": _sorted(allowed_decisions),
        "currentDecision": current_decision,
        "blockingEffect": blocking_effect,
        "rootCause": root_cause,
    }
    card["deterministicDigest"] = sha256_digest({k: v for k, v in card.items() if k != "deterministicDigest"})
    return card


def build_source_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    ref = {"artifactType": artifact_type, "path": path, "digest": digest}
    ref["deterministicDigest"] = sha256_digest(ref)
    return ref


def build_faultcase_projection(
    *,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    faultcase_candidates: Sequence[Mapping[str, Any]],
    review_cards: Sequence[Mapping[str, Any]],
    filters: Mapping[str, Any],
    facets: Mapping[str, Any],
    default_page: Mapping[str, Any],
    source_artifact_references: Sequence[Mapping[str, Any]],
    generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
) -> dict[str, Any]:
    projection = {
        "projectionId": sha256_digest(
            {
                "contractVersion": CONTRACT_VERSION,
                "authority": authority,
                "profileId": profile_id,
                "candidateDigests": [candidate.get("deterministicDigest") for candidate in faultcase_candidates],
                "cardDigests": [card.get("deterministicDigest") for card in review_cards],
            }
        ),
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "faultCaseCandidates": list(faultcase_candidates),
        "reviewCards": list(review_cards),
        "filters": dict(filters),
        "facets": dict(facets),
        "defaultPage": dict(default_page),
        "sourceArtifactReferences": list(source_artifact_references),
        "generatedAtPolicy": generated_at_policy,
    }
    projection["deterministicDigest"] = sha256_digest(
        {k: v for k, v in projection.items() if k != "deterministicDigest"}
    )
    return projection
