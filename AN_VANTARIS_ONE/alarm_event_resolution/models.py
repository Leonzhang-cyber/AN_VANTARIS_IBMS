"""Model builders for deterministic alarm/event resolution review projections."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def _value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _sorted(values: Sequence[str] | None) -> list[str]:
    return sorted(str(value) for value in values or ())


def build_resolution_row(
    *,
    candidate_id: str,
    source_system_key: str,
    event_kind: str,
    event_category: str,
    event_severity: str,
    asset_resolution_state: str,
    point_resolution_state: str,
    location_resolution_state: str,
    source_system_review_state: str,
    downstream_creation_state: str,
    resolution_confidence: str,
    device_evidence_count: int,
    decision_required: bool,
    review_reasons: Sequence[str],
    evidence_references: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    row_id = sha256_digest(
        {
            "contractVersion": CONTRACT_VERSION,
            "candidateId": candidate_id,
            "sourceSystemKey": source_system_key,
            "reviewReasons": sorted(review_reasons),
        }
    )
    row = {
        "rowId": row_id,
        "candidateId": candidate_id,
        "sourceSystemKey": source_system_key,
        "eventKind": event_kind,
        "eventCategory": event_category,
        "eventSeverity": event_severity,
        "assetResolutionState": _value(asset_resolution_state),
        "pointResolutionState": _value(point_resolution_state),
        "locationResolutionState": _value(location_resolution_state),
        "sourceSystemReviewState": _value(source_system_review_state),
        "downstreamCreationState": _value(downstream_creation_state),
        "resolutionConfidence": _value(resolution_confidence),
        "deviceEvidenceCount": int(device_evidence_count),
        "decisionRequired": bool(decision_required),
        "reviewReasons": _sorted(review_reasons),
        "evidenceReferences": list(evidence_references or ()),
    }
    row["deterministicDigest"] = sha256_digest({k: v for k, v in row.items() if k != "deterministicDigest"})
    return row


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


def build_resolution_projection(
    *,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    resolution_rows: Sequence[Mapping[str, Any]],
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
                "rowDigests": [row.get("deterministicDigest") for row in resolution_rows],
                "cardDigests": [card.get("deterministicDigest") for card in review_cards],
            }
        ),
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "resolutionRows": list(resolution_rows),
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
