"""Airport offline consumer profile for canonical alarm/event intake candidates."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from alarm_event_intake.models import (
    build_canonical_alarm_event_candidate,
    build_projection,
    build_review_card,
)
from alarm_event_intake.normalization import normalize_intake_envelope
from alarm_event_intake.projection import build_facets, build_filters, paginate_candidates, sort_candidates
from source_system_registry.digest import sha256_digest
from source_system_registry.models import build_registry_entry_id

AUTHORITY = "ONE-AIRPORT-A3-01"
PROFILE_ID = "airport-alarm-event-intake-profile-v1"
IMPLEMENTATION_STATUS = "CANONICAL_ALARM_EVENT_INTAKE_FOUNDATION_COMPLETE"
READINESS_OUTCOME = "ALARM_EVENT_INTAKE_CANDIDATES_COMPLETE_WITH_PENDING_REVIEWS"
ALLOWED_SOURCE_SYSTEM_KEYS = ("ACS", "RAS", "CCTV", "PA", "TEL")


def _registry_entry_id(source_system_key: str) -> str:
    return build_registry_entry_id(
        source_system_key=source_system_key,
        created_from_profile="airport-source-system-profile-v1",
        mapping_version="airport-alarm-event-intake-profile.v1",
    )


def _safe_reference(*, source_system_key: str, concept: str) -> str:
    return sha256_digest(
        {
            "profileId": PROFILE_ID,
            "sourceSystemKey": source_system_key,
            "concept": concept,
            "redacted": True,
        }
    )


def airport_offline_fixture_inputs() -> list[dict[str, Any]]:
    """Exactly five static fixture candidate inputs; these are not live alarms."""
    base: list[dict[str, Any]] = []
    specs = (
        ("ACS", "ALARM", "SECURITY", "HIGH", "RAISED", ["REGISTRY_APPROVAL_REQUIRED"]),
        ("RAS", "EVENT", "COMMUNICATION", "MEDIUM", "UPDATED", ["REGISTRY_APPROVAL_REQUIRED"]),
        ("CCTV", "HEALTH_SIGNAL", "SECURITY", "LOW", "UPDATED", ["ALIAS_APPROVAL_REQUIRED"]),
        ("PA", "EVENT", "EQUIPMENT", "LOW", "UPDATED", ["ALIAS_APPROVAL_REQUIRED"]),
        ("TEL", "STATUS_CHANGE", "COMMUNICATION", "MEDIUM", "UPDATED", ["NAMESPACE_INTERPRETATION_REQUIRED"]),
    )
    for source_system_key, event_kind, category, severity, state, reasons in specs:
        common_reviews = [
            "ASSET_RESOLUTION_REQUIRED",
            "POINT_RESOLUTION_REQUIRED",
            "LOCATION_RESOLUTION_REQUIRED",
            "DOWNSTREAM_CREATION_NOT_AUTHORIZED",
        ]
        source_ref = _safe_reference(source_system_key=source_system_key, concept="source-event-reference")
        base.append(
            {
                "sourceSystemKey": source_system_key,
                "registryEntryId": _registry_entry_id(source_system_key),
                "eventKind": event_kind,
                "eventCategory": category,
                "eventSeverity": severity,
                "eventState": state,
                "sourceEventReference": source_ref,
                "eventTemplate": f"{source_system_key} offline candidate template",
                "assetReferenceDigest": _safe_reference(source_system_key=source_system_key, concept="asset"),
                "pointReferenceDigest": _safe_reference(source_system_key=source_system_key, concept="point"),
                "locationReferenceDigest": _safe_reference(source_system_key=source_system_key, concept="location"),
                "reviewReasons": sorted(reasons + common_reviews),
                "evidenceReferences": [
                    {
                        "evidenceType": "SOURCE_SYSTEM_REGISTRY_REFERENCE",
                        "sourceSystemKey": source_system_key,
                        "referenceDigest": _safe_reference(source_system_key=source_system_key, concept="evidence"),
                        "provenance": "OFFLINE_FIXTURE_CANDIDATE_ONLY",
                    }
                ],
            }
        )
    return base


def _candidate_for_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
    source_system_key = str(envelope["sourceSystemKey"])
    canonical_event_key = sha256_digest(
        {
            "profileId": PROFILE_ID,
            "sourceSystemKey": source_system_key,
            "sourceEventReference": envelope["sourceEventReference"],
        }
    )
    return build_canonical_alarm_event_candidate(
        envelope=envelope,
        canonical_event_key=canonical_event_key,
        lifecycle_state="CANDIDATE",
        approval_state="REVIEW_REQUIRED",
        normalization_state="REVIEW_REQUIRED",
        asset_resolution_state="REVIEW_REQUIRED",
        point_resolution_state="REVIEW_REQUIRED",
        location_resolution_state="REVIEW_REQUIRED",
        ufms_fault_case_candidate_state="BLOCKED",
        work_order_intent_candidate_state="BLOCKED",
        review_reasons=list(envelope.get("reviewReasons", [])),
    )


def _review_cards(candidates: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    reason_specs = {
        "REGISTRY_APPROVAL_REQUIRED": ("Registry approval required", "LOW"),
        "ALIAS_APPROVAL_REQUIRED": ("Alias approval required", "MEDIUM"),
        "NAMESPACE_INTERPRETATION_REQUIRED": ("Namespace interpretation required", "MEDIUM"),
        "ASSET_RESOLUTION_REQUIRED": ("Asset resolution required", "MEDIUM"),
        "POINT_RESOLUTION_REQUIRED": ("Point resolution required", "MEDIUM"),
        "LOCATION_RESOLUTION_REQUIRED": ("Location resolution required", "MEDIUM"),
        "DOWNSTREAM_CREATION_NOT_AUTHORIZED": ("Downstream creation blocked", "HIGH"),
    }
    for reason, (title, severity) in reason_specs.items():
        affected = [str(item["sourceSystemKey"]) for item in candidates if reason in item.get("reviewReasons", [])]
        if affected:
            cards.append(
                build_review_card(
                    reason=reason,
                    title=title,
                    severity=severity,
                    affected_source_system_keys=affected,
                    candidate_count=len(affected),
                )
            )
    return sorted(cards, key=lambda card: (card["reason"], card["reviewCardId"]))


def build_airport_alarm_event_intake_projection() -> dict[str, Any]:
    raw_inputs = airport_offline_fixture_inputs()
    envelopes = [
        normalize_intake_envelope(
            raw,
            allowed_source_system_keys=ALLOWED_SOURCE_SYSTEM_KEYS,
            allow_unknown_source_system=False,
            allow_missing_severity_unknown=False,
        )
        for raw in raw_inputs
    ]
    candidates = sort_candidates([_candidate_for_envelope(envelope) for envelope in envelopes])
    review_cards = _review_cards(candidates)
    summary = {
        "sourceSystemCandidateCount": 5,
        "intakeEnvelopeCount": len(envelopes),
        "canonicalAlarmEventCandidateCount": len(candidates),
        "acceptedAsCandidateCount": sum(1 for item in envelopes if item["validationState"] == "ACCEPTED_AS_CANDIDATE"),
        "rejectedEnvelopeCount": sum(1 for item in envelopes if item["validationState"] == "REJECTED"),
        "reviewRequiredCandidateCount": sum(1 for item in candidates if item["decisionRequired"] is True),
        "runtimeAlarmObservedCount": 0,
        "liveAlarmPollingEnabled": False,
        "connectorExecutionEnabled": False,
        "databaseAccessEnabled": False,
        "databaseWriteCount": 0,
        "canonicalWriteCount": 0,
        "ufmsFaultCaseCreatedCount": 0,
        "workOrderIntentCreatedCount": 0,
        "workOrderCreatedCount": 0,
        "evidenceCenterWriteCount": 0,
        "productionActivationEnabled": False,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
    }
    return build_projection(
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        candidates=candidates,
        review_cards=review_cards,
        filters=build_filters(candidates),
        facets=build_facets(candidates),
        default_page=paginate_candidates(candidates, page_size=25),
    )


def compare_deterministic_outputs(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return json.dumps(left, sort_keys=True, separators=(",", ":")) == json.dumps(
        right, sort_keys=True, separators=(",", ":")
    )


def write_airport_alarm_event_intake_projection(path: Path) -> dict[str, Any]:
    projection = build_airport_alarm_event_intake_projection()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return projection
