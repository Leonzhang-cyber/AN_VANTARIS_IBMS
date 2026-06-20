"""Read-only canonical alarm/event intake normalization."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .enums import EventCategory, EventSeverity, EventState, NormalizationState
from .models import build_intake_envelope
from .validation import validate_intake_envelope


def _safe_digest_ref(value: str) -> dict[str, Any]:
    return {"referencePolicy": "REDACTED_REFERENCE_DIGEST_ONLY", "referenceDigest": value}


def normalize_intake_envelope(
    raw: Mapping[str, Any],
    *,
    allowed_source_system_keys: Sequence[str],
    allow_unknown_source_system: bool = False,
    allow_missing_severity_unknown: bool = False,
) -> dict[str, Any]:
    """Normalize one static fixture input into a canonical intake envelope candidate."""
    result = validate_intake_envelope(
        raw,
        allowed_source_system_keys=allowed_source_system_keys,
        allow_unknown_source_system=allow_unknown_source_system,
        allow_missing_severity_unknown=allow_missing_severity_unknown,
    )
    event_severity = result["normalizedEventSeverity"] or EventSeverity.UNKNOWN.value
    event_category = str(raw.get("eventCategory") or EventCategory.UNKNOWN.value)
    event_state = str(raw.get("eventState") or EventState.UNKNOWN.value)
    review_reasons = sorted(set(result["reviewReasons"]) | set(raw.get("reviewReasons", [])))
    normalization_state = (
        NormalizationState.REJECTED.value
        if result["rejectionReasons"]
        else NormalizationState.REVIEW_REQUIRED.value
        if review_reasons
        else NormalizationState.NORMALIZED.value
    )
    payload = {
        "offlineFixture": True,
        "staticFixtureOnly": True,
        "runtimeAlarmObserved": False,
        "sourceSystemKey": raw.get("sourceSystemKey", ""),
        "eventTemplate": raw.get("eventTemplate", ""),
        "sourceReferenceDigest": raw.get("sourceEventReference", ""),
        "assetReferencePolicy": "REDACTED_REFERENCE_DIGEST_ONLY",
        "pointReferencePolicy": "REDACTED_REFERENCE_DIGEST_ONLY",
        "locationReferencePolicy": "REDACTED_REFERENCE_DIGEST_ONLY",
        "normalizationState": normalization_state,
    }
    return build_intake_envelope(
        source_system_key=str(raw.get("sourceSystemKey") or ""),
        registry_entry_id=str(raw.get("registryEntryId") or ""),
        event_kind=str(raw.get("eventKind") or ""),
        event_category=event_category,
        event_severity=event_severity,
        event_state=event_state,
        source_event_reference=str(raw.get("sourceEventReference") or ""),
        payload=payload,
        normalized_asset_reference=_safe_digest_ref(str(raw.get("assetReferenceDigest") or "")),
        normalized_point_reference=_safe_digest_ref(str(raw.get("pointReferenceDigest") or "")),
        normalized_location_reference=_safe_digest_ref(str(raw.get("locationReferenceDigest") or "")),
        evidence_references=list(raw.get("evidenceReferences", [])),
        validation_state=result["validationState"],
        rejection_reasons=result["rejectionReasons"],
        review_reasons=review_reasons,
    )
