"""Canonical alarm/event intake model builders."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def _value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _sorted_list(values: Sequence[str] | None) -> list[str]:
    return sorted(str(value) for value in values or ())


def build_intake_envelope_id(
    *,
    source_system_key: str,
    source_event_reference: str,
    event_kind: str,
    payload_digest: str,
) -> str:
    return sha256_digest(
        {
            "contractVersion": CONTRACT_VERSION,
            "sourceSystemKey": source_system_key,
            "sourceEventReference": source_event_reference,
            "eventKind": event_kind,
            "payloadDigest": payload_digest,
        }
    )


def build_candidate_id(*, intake_envelope_id: str, canonical_event_key: str) -> str:
    return sha256_digest(
        {
            "contractVersion": CONTRACT_VERSION,
            "intakeEnvelopeId": intake_envelope_id,
            "canonicalEventKey": canonical_event_key,
        }
    )


def build_intake_envelope(
    *,
    source_system_key: str,
    registry_entry_id: str,
    event_kind: str,
    event_category: str,
    event_severity: str,
    event_state: str,
    source_event_reference: str,
    payload: Mapping[str, Any],
    normalized_asset_reference: Mapping[str, Any] | None = None,
    normalized_point_reference: Mapping[str, Any] | None = None,
    normalized_location_reference: Mapping[str, Any] | None = None,
    evidence_references: Sequence[Mapping[str, Any]] | None = None,
    validation_state: str = "ACCEPTED_AS_CANDIDATE",
    rejection_reasons: Sequence[str] | None = None,
    review_reasons: Sequence[str] | None = None,
    event_time_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
    source_asset_reference_policy: str = "REDACTED_REFERENCE_DIGEST_ONLY",
) -> dict[str, Any]:
    payload_digest = sha256_digest(payload)
    intake_envelope_id = build_intake_envelope_id(
        source_system_key=source_system_key,
        source_event_reference=source_event_reference,
        event_kind=_value(event_kind),
        payload_digest=payload_digest,
    )
    envelope = {
        "intakeEnvelopeId": intake_envelope_id,
        "contractVersion": CONTRACT_VERSION,
        "sourceSystemKey": source_system_key,
        "registryEntryId": registry_entry_id,
        "eventKind": _value(event_kind),
        "eventCategory": _value(event_category),
        "eventSeverity": _value(event_severity),
        "eventState": _value(event_state),
        "eventTimePolicy": event_time_policy,
        "sourceEventReference": source_event_reference,
        "sourceAssetReferencePolicy": source_asset_reference_policy,
        "normalizedAssetReference": dict(normalized_asset_reference or {}),
        "normalizedPointReference": dict(normalized_point_reference or {}),
        "normalizedLocationReference": dict(normalized_location_reference or {}),
        "evidenceReferences": list(evidence_references or ()),
        "payloadDigest": payload_digest,
        "payload": dict(payload),
        "validationState": _value(validation_state),
        "rejectionReasons": _sorted_list(rejection_reasons),
        "reviewReasons": _sorted_list(review_reasons),
    }
    envelope["deterministicDigest"] = sha256_digest(
        {k: v for k, v in envelope.items() if k != "deterministicDigest"}
    )
    return envelope


def build_canonical_alarm_event_candidate(
    *,
    envelope: Mapping[str, Any],
    canonical_event_key: str,
    lifecycle_state: str = "CANDIDATE",
    approval_state: str = "REVIEW_REQUIRED",
    normalization_state: str = "REVIEW_REQUIRED",
    asset_resolution_state: str = "REVIEW_REQUIRED",
    point_resolution_state: str = "REVIEW_REQUIRED",
    location_resolution_state: str = "REVIEW_REQUIRED",
    ufms_fault_case_candidate_state: str = "BLOCKED",
    work_order_intent_candidate_state: str = "BLOCKED",
    review_reasons: Sequence[str] | None = None,
) -> dict[str, Any]:
    intake_envelope_id = str(envelope["intakeEnvelopeId"])
    candidate = {
        "candidateId": build_candidate_id(
            intake_envelope_id=intake_envelope_id,
            canonical_event_key=canonical_event_key,
        ),
        "intakeEnvelopeId": intake_envelope_id,
        "canonicalEventKey": canonical_event_key,
        "sourceSystemKey": str(envelope["sourceSystemKey"]),
        "eventKind": str(envelope["eventKind"]),
        "eventCategory": str(envelope["eventCategory"]),
        "eventSeverity": str(envelope["eventSeverity"]),
        "eventState": str(envelope["eventState"]),
        "validationState": str(envelope["validationState"]),
        "lifecycleState": _value(lifecycle_state),
        "approvalState": _value(approval_state),
        "normalizationState": _value(normalization_state),
        "assetResolutionState": _value(asset_resolution_state),
        "pointResolutionState": _value(point_resolution_state),
        "locationResolutionState": _value(location_resolution_state),
        "ufmsFaultCaseCandidateState": _value(ufms_fault_case_candidate_state),
        "workOrderIntentCandidateState": _value(work_order_intent_candidate_state),
        "evidenceReferences": list(envelope.get("evidenceReferences", [])),
        "decisionRequired": True,
        "reviewReasons": _sorted_list(review_reasons or envelope.get("reviewReasons", [])),
    }
    candidate["deterministicDigest"] = sha256_digest(
        {k: v for k, v in candidate.items() if k != "deterministicDigest"}
    )
    return candidate


def build_review_card(
    *,
    reason: str,
    title: str,
    severity: str,
    affected_source_system_keys: Sequence[str],
    candidate_count: int,
) -> dict[str, Any]:
    card = {
        "reviewCardId": sha256_digest(
            {
                "contractVersion": CONTRACT_VERSION,
                "reason": reason,
                "affectedSourceSystemKeys": sorted(affected_source_system_keys),
            }
        ),
        "reason": reason,
        "title": title,
        "severity": severity,
        "affectedSourceSystemKeys": sorted(affected_source_system_keys),
        "candidateCount": candidate_count,
        "decisionRequired": True,
    }
    card["deterministicDigest"] = sha256_digest({k: v for k, v in card.items() if k != "deterministicDigest"})
    return card


def build_projection(
    *,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    candidates: Sequence[Mapping[str, Any]],
    review_cards: Sequence[Mapping[str, Any]],
    filters: Mapping[str, Any],
    facets: Mapping[str, Any],
    default_page: Mapping[str, Any],
    generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
) -> dict[str, Any]:
    projection = {
        "projectionId": sha256_digest(
            {
                "contractVersion": CONTRACT_VERSION,
                "authority": authority,
                "profileId": profile_id,
                "candidateDigests": [item.get("deterministicDigest") for item in candidates],
            }
        ),
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "candidates": list(candidates),
        "reviewCards": list(review_cards),
        "filters": dict(filters),
        "facets": dict(facets),
        "defaultPage": dict(default_page),
        "generatedAtPolicy": generated_at_policy,
    }
    projection["deterministicDigest"] = sha256_digest(
        {k: v for k, v in projection.items() if k != "deterministicDigest"}
    )
    return projection
