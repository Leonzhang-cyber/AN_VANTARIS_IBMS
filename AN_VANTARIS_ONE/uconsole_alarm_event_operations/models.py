"""Model builders for deterministic UConsole operations projections."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def _sorted(values: Sequence[str] | None) -> list[str]:
    return sorted(str(value) for value in values or ())


def build_operations_row(
    *,
    source_system_key: str,
    alarm_event_candidate_id: str,
    resolution_row_id: str,
    faultcase_candidate_id: str,
    workorder_intent_candidate_id: str,
    investigation_case_id: str,
    event_kind: str,
    event_category: str,
    event_severity: str,
    alarm_event_state: str,
    faultcase_candidate_state: str,
    workorder_intent_candidate_state: str,
    investigation_state: str,
    asset_resolution_state: str,
    source_system_review_state: str,
    operational_status: str,
    operational_severity: str,
    decision_required: bool,
    pending_decision_count: int,
    device_evidence_count: int,
    review_reasons: Sequence[str],
    blocking_reasons: Sequence[str],
) -> dict[str, Any]:
    row_id = sha256_digest(
        {
            "contractVersion": CONTRACT_VERSION,
            "sourceSystemKey": source_system_key,
            "alarmEventCandidateId": alarm_event_candidate_id,
            "faultCaseCandidateId": faultcase_candidate_id,
            "workOrderIntentCandidateId": workorder_intent_candidate_id,
            "investigationCaseId": investigation_case_id,
        }
    )
    row = {
        "rowId": row_id,
        "sourceSystemKey": source_system_key,
        "alarmEventCandidateId": alarm_event_candidate_id,
        "resolutionRowId": resolution_row_id,
        "faultCaseCandidateId": faultcase_candidate_id,
        "workOrderIntentCandidateId": workorder_intent_candidate_id,
        "investigationCaseId": investigation_case_id,
        "eventKind": event_kind,
        "eventCategory": event_category,
        "eventSeverity": event_severity,
        "alarmEventState": alarm_event_state,
        "faultCaseCandidateState": faultcase_candidate_state,
        "workOrderIntentCandidateState": workorder_intent_candidate_state,
        "investigationState": investigation_state,
        "assetResolutionState": asset_resolution_state,
        "sourceSystemReviewState": source_system_review_state,
        "operationalStatus": operational_status,
        "operationalSeverity": operational_severity,
        "decisionRequired": bool(decision_required),
        "pendingDecisionCount": int(pending_decision_count),
        "deviceEvidenceCount": int(device_evidence_count),
        "reviewReasons": _sorted(review_reasons),
        "blockingReasons": _sorted(blocking_reasons),
    }
    row["deterministicDigest"] = sha256_digest({k: v for k, v in row.items() if k != "deterministicDigest"})
    return row


def build_operations_card(
    *,
    card_type: str,
    title: str,
    severity: str,
    status: str,
    value: int,
    unit: str,
    affected_source_system_keys: Sequence[str],
    affected_row_count: int,
    affected_device_evidence_count: int,
    decision_required: bool,
) -> dict[str, Any]:
    card = {
        "cardId": sha256_digest(
            {
                "contractVersion": CONTRACT_VERSION,
                "cardType": card_type,
                "affectedSourceSystemKeys": sorted(affected_source_system_keys),
            }
        ),
        "cardType": card_type,
        "title": title,
        "severity": severity,
        "status": status,
        "value": int(value),
        "unit": unit,
        "affectedSourceSystemKeys": sorted(affected_source_system_keys),
        "affectedRowCount": int(affected_row_count),
        "affectedDeviceEvidenceCount": int(affected_device_evidence_count),
        "decisionRequired": bool(decision_required),
    }
    card["deterministicDigest"] = sha256_digest({k: v for k, v in card.items() if k != "deterministicDigest"})
    return card


def build_source_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    ref = {"artifactType": artifact_type, "path": path, "digest": digest}
    ref["deterministicDigest"] = sha256_digest(ref)
    return ref


def build_operations_projection(
    *,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    operations_rows: Sequence[Mapping[str, Any]],
    operations_cards: Sequence[Mapping[str, Any]],
    queue_cards: Sequence[Mapping[str, Any]],
    investigation_cards: Sequence[Mapping[str, Any]],
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
                "rowDigests": [row.get("deterministicDigest") for row in operations_rows],
                "cardDigests": [card.get("deterministicDigest") for card in operations_cards],
            }
        ),
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "operationsRows": list(operations_rows),
        "operationsCards": list(operations_cards),
        "queueCards": list(queue_cards),
        "investigationCards": list(investigation_cards),
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
