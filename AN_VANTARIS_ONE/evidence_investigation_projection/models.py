"""Model builders for deterministic Evidence Investigation projections."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def _sorted(values: Sequence[str] | None) -> list[str]:
    return sorted(str(value) for value in values or ())


def build_evidence_link(
    *,
    link_type: str,
    source_artifact_type: str,
    source_artifact_id: str,
    target_artifact_type: str,
    target_artifact_id: str,
    source_system_key: str,
    evidence_role: str,
    linkage_state: str,
    provenance: str,
    evidence_references: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    link_id = sha256_digest(
        {
            "contractVersion": CONTRACT_VERSION,
            "linkType": link_type,
            "sourceArtifactType": source_artifact_type,
            "sourceArtifactId": source_artifact_id,
            "targetArtifactType": target_artifact_type,
            "targetArtifactId": target_artifact_id,
        }
    )
    link = {
        "evidenceLinkId": link_id,
        "linkType": link_type,
        "sourceArtifactType": source_artifact_type,
        "sourceArtifactId": source_artifact_id,
        "targetArtifactType": target_artifact_type,
        "targetArtifactId": target_artifact_id,
        "sourceSystemKey": source_system_key,
        "evidenceRole": evidence_role,
        "linkageState": linkage_state,
        "provenance": provenance,
        "evidenceReferences": list(evidence_references or ()),
    }
    link["deterministicDigest"] = sha256_digest({k: v for k, v in link.items() if k != "deterministicDigest"})
    return link


def build_timeline_item(
    *,
    source_system_key: str,
    sequence: int,
    item_type: str,
    title: str,
    source_artifact_type: str,
    source_artifact_id: str,
    state: str,
    decision_required: bool,
) -> dict[str, Any]:
    item_id = sha256_digest(
        {
            "contractVersion": CONTRACT_VERSION,
            "sourceSystemKey": source_system_key,
            "sequence": sequence,
            "itemType": item_type,
            "sourceArtifactType": source_artifact_type,
            "sourceArtifactId": source_artifact_id,
        }
    )
    item = {
        "timelineItemId": item_id,
        "sourceSystemKey": source_system_key,
        "sequence": int(sequence),
        "itemType": item_type,
        "title": title,
        "sourceArtifactType": source_artifact_type,
        "sourceArtifactId": source_artifact_id,
        "state": state,
        "decisionRequired": bool(decision_required),
    }
    item["deterministicDigest"] = sha256_digest({k: v for k, v in item.items() if k != "deterministicDigest"})
    return item


def build_investigation_case(
    *,
    source_alarm_event_candidate_id: str,
    source_resolution_row_id: str,
    source_faultcase_candidate_id: str,
    source_workorder_intent_candidate_id: str,
    source_system_key: str,
    investigation_state: str,
    evidence_completeness_state: str,
    linkage_state: str,
    decision_required: bool,
    review_reasons: Sequence[str],
    blocking_reasons: Sequence[str],
    evidence_link_ids: Sequence[str],
    timeline_item_ids: Sequence[str],
    device_evidence_count: int,
) -> dict[str, Any]:
    case_id = sha256_digest(
        {
            "contractVersion": CONTRACT_VERSION,
            "sourceAlarmEventCandidateId": source_alarm_event_candidate_id,
            "sourceResolutionRowId": source_resolution_row_id,
            "sourceFaultCaseCandidateId": source_faultcase_candidate_id,
            "sourceWorkOrderIntentCandidateId": source_workorder_intent_candidate_id,
        }
    )
    case = {
        "investigationCaseId": case_id,
        "sourceAlarmEventCandidateId": source_alarm_event_candidate_id,
        "sourceResolutionRowId": source_resolution_row_id,
        "sourceFaultCaseCandidateId": source_faultcase_candidate_id,
        "sourceWorkOrderIntentCandidateId": source_workorder_intent_candidate_id,
        "sourceSystemKey": source_system_key,
        "investigationState": investigation_state,
        "evidenceCompletenessState": evidence_completeness_state,
        "linkageState": linkage_state,
        "decisionRequired": bool(decision_required),
        "reviewReasons": _sorted(review_reasons),
        "blockingReasons": _sorted(blocking_reasons),
        "evidenceLinkIds": _sorted(evidence_link_ids),
        "timelineItemIds": _sorted(timeline_item_ids),
        "deviceEvidenceCount": int(device_evidence_count),
    }
    case["deterministicDigest"] = sha256_digest({k: v for k, v in case.items() if k != "deterministicDigest"})
    return case


def build_review_card(
    *,
    review_type: str,
    title: str,
    affected_source_system_keys: Sequence[str],
    affected_case_count: int,
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
        "affectedCaseCount": int(affected_case_count),
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


def build_evidence_investigation_projection(
    *,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    investigation_cases: Sequence[Mapping[str, Any]],
    evidence_links: Sequence[Mapping[str, Any]],
    investigation_timeline: Sequence[Mapping[str, Any]],
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
                "caseDigests": [item.get("deterministicDigest") for item in investigation_cases],
                "linkDigests": [item.get("deterministicDigest") for item in evidence_links],
                "timelineDigests": [item.get("deterministicDigest") for item in investigation_timeline],
            }
        ),
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "investigationCases": list(investigation_cases),
        "evidenceLinks": list(evidence_links),
        "investigationTimeline": list(investigation_timeline),
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
