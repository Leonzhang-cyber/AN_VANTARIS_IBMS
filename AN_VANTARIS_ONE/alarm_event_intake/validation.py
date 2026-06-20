"""Validation for canonical alarm/event intake envelopes."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .enums import EventKind, EventSeverity, ValidationState


def _enum_values(enum_type: type) -> set[str]:
    return {item.value for item in enum_type}


def validate_intake_envelope(
    envelope: Mapping[str, Any],
    *,
    allowed_source_system_keys: Sequence[str],
    allow_unknown_source_system: bool = False,
    allow_missing_severity_unknown: bool = False,
) -> dict[str, Any]:
    """Return deterministic validation state and reasons for one envelope-like input."""
    rejections: list[str] = []
    reviews: list[str] = []

    source_system_key = str(envelope.get("sourceSystemKey") or "")
    event_kind = str(envelope.get("eventKind") or "")
    event_severity = str(envelope.get("eventSeverity") or "")
    source_event_reference = str(envelope.get("sourceEventReference") or "")

    if not source_system_key:
        rejections.append("SOURCE_SYSTEM_KEY_REQUIRED")
    elif source_system_key not in set(allowed_source_system_keys) and not allow_unknown_source_system:
        rejections.append("SOURCE_SYSTEM_KEY_UNKNOWN")

    if not event_kind:
        rejections.append("EVENT_KIND_REQUIRED")
    elif event_kind not in _enum_values(EventKind):
        rejections.append("EVENT_KIND_UNSUPPORTED")

    if not source_event_reference:
        rejections.append("SOURCE_EVENT_REFERENCE_REQUIRED")

    normalized_severity = event_severity
    if not event_severity:
        if allow_missing_severity_unknown:
            normalized_severity = EventSeverity.UNKNOWN.value
            reviews.append("EVENT_SEVERITY_UNKNOWN")
        else:
            reviews.append("EVENT_SEVERITY_REQUIRED")
    elif event_severity not in _enum_values(EventSeverity):
        reviews.append("EVENT_SEVERITY_UNKNOWN")
        normalized_severity = EventSeverity.UNKNOWN.value

    state = ValidationState.REJECTED.value if rejections else ValidationState.ACCEPTED_AS_CANDIDATE.value
    if not rejections and reviews:
        state = ValidationState.REVIEW_REQUIRED.value

    return {
        "validationState": state,
        "rejectionReasons": sorted(rejections),
        "reviewReasons": sorted(reviews),
        "normalizedEventSeverity": normalized_severity,
    }
