"""Airport read-only Alarm/Event to Asset/Point/Location resolution projection."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from alarm_event_resolution.enums import (
    DownstreamCreationState,
    ResolutionConfidence,
    ResolutionState,
    ReviewState,
)
from alarm_event_resolution.models import (
    build_resolution_projection,
    build_resolution_row,
    build_review_card,
    build_source_artifact_reference,
)
from alarm_event_resolution.projection import build_facets, build_filters, paginate_rows, sort_rows
from alarm_event_resolution.validation import validate_resolution_projection
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A3-02"
PROFILE_ID = "airport-alarm-event-asset-resolution-review-profile-v1"
IMPLEMENTATION_STATUS = "ALARM_EVENT_ASSET_RESOLUTION_REVIEW_PROJECTION_COMPLETE"
READINESS_OUTCOME = "ALARM_EVENT_RESOLUTION_REVIEW_COMPLETE_WITH_PENDING_DECISIONS"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
INTAKE_PROJECTION = PROJECTIONS_DIR / "airport-alarm-event-intake-candidates.v1.json"
SOURCE_SYSTEM_REVIEW = PROJECTIONS_DIR / "airport-source-system-review.v1.json"
SOURCE_SYSTEM_CANDIDATES = PROJECTIONS_DIR / "airport-source-system-candidates.v1.json"
INTEGRATION_HEALTH = PROJECTIONS_DIR / "airport-integration-health.v1.json"
UCONSOLE_HEALTH = PROJECTIONS_DIR / "airport-uconsole-integration-health.v1.json"

DEVICE_EVIDENCE_COUNTS = {"ACS": 129, "RAS": 28, "CCTV": 52, "PA": 247, "TEL": 14}
PRIMARY_REVIEW_BY_SOURCE = {
    "ACS": ReviewState.REGISTRY_APPROVAL_PENDING.value,
    "RAS": ReviewState.REGISTRY_APPROVAL_PENDING.value,
    "CCTV": ReviewState.ALIAS_APPROVAL_PENDING.value,
    "PA": ReviewState.ALIAS_APPROVAL_PENDING.value,
    "TEL": ReviewState.NAMESPACE_INTERPRETATION_PENDING.value,
}
PRIMARY_REASON_BY_REVIEW = {
    ReviewState.REGISTRY_APPROVAL_PENDING.value: "REGISTRY_APPROVAL_REQUIRED",
    ReviewState.ALIAS_APPROVAL_PENDING.value: "ALIAS_APPROVAL_REQUIRED",
    ReviewState.NAMESPACE_INTERPRETATION_PENDING.value: "NAMESPACE_INTERPRETATION_REQUIRED",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_reference(path: Path, artifact_type: str) -> dict[str, Any]:
    relative = str(path.relative_to(ROOT))
    return build_source_artifact_reference(
        artifact_type=artifact_type,
        path=relative,
        digest=sha256_digest(_load(path)),
    )


def _source_artifact_references() -> list[dict[str, Any]]:
    refs = [
        _artifact_reference(INTAKE_PROJECTION, "ALARM_EVENT_INTAKE_CANDIDATES"),
        _artifact_reference(SOURCE_SYSTEM_REVIEW, "SOURCE_SYSTEM_REVIEW"),
        _artifact_reference(SOURCE_SYSTEM_CANDIDATES, "SOURCE_SYSTEM_CANDIDATES"),
        _artifact_reference(INTEGRATION_HEALTH, "INTEGRATION_HEALTH"),
        _artifact_reference(UCONSOLE_HEALTH, "UCONSOLE_INTEGRATION_HEALTH"),
    ]
    return sorted(refs, key=lambda item: item["artifactType"])


def _review_reasons(source_system_key: str) -> list[str]:
    primary_review = PRIMARY_REVIEW_BY_SOURCE[source_system_key]
    primary_reason = PRIMARY_REASON_BY_REVIEW[primary_review]
    return sorted(
        {
            primary_reason,
            "RESOLUTION_REVIEW_REQUIRED",
            "ASSET_RESOLUTION_REQUIRED",
            "POINT_RESOLUTION_REQUIRED",
            "LOCATION_RESOLUTION_REQUIRED",
            "DOWNSTREAM_CREATION_NOT_AUTHORIZED",
        }
    )


def _row_for_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    source_system_key = str(candidate["sourceSystemKey"])
    return build_resolution_row(
        candidate_id=str(candidate["candidateId"]),
        source_system_key=source_system_key,
        event_kind=str(candidate["eventKind"]),
        event_category=str(candidate["eventCategory"]),
        event_severity=str(candidate["eventSeverity"]),
        asset_resolution_state=ResolutionState.REVIEW_REQUIRED.value,
        point_resolution_state=ResolutionState.REVIEW_REQUIRED.value,
        location_resolution_state=ResolutionState.REVIEW_REQUIRED.value,
        source_system_review_state=PRIMARY_REVIEW_BY_SOURCE[source_system_key],
        downstream_creation_state=DownstreamCreationState.NOT_AUTHORIZED.value,
        resolution_confidence=ResolutionConfidence.LOW.value,
        device_evidence_count=DEVICE_EVIDENCE_COUNTS[source_system_key],
        decision_required=True,
        review_reasons=_review_reasons(source_system_key),
        evidence_references=list(candidate.get("evidenceReferences", [])),
    )


def _review_cards(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    card_specs = {
        "REGISTRY_APPROVAL_REQUIRED": (
            "Registry approval required before resolution use",
            "BLOCKS_RESOLUTION_AND_DOWNSTREAM_CREATION",
            "Source systems remain registry candidates.",
        ),
        "ALIAS_APPROVAL_REQUIRED": (
            "Alias approval required before resolution use",
            "BLOCKS_RESOLUTION_AND_DOWNSTREAM_CREATION",
            "Airport source-system aliases require approval.",
        ),
        "NAMESPACE_INTERPRETATION_REQUIRED": (
            "Namespace interpretation required before resolution use",
            "BLOCKS_RESOLUTION_AND_DOWNSTREAM_CREATION",
            "Source namespace interpretation is pending review.",
        ),
        "ASSET_RESOLUTION_REQUIRED": (
            "Asset resolution review required",
            "BLOCKS_CANONICAL_ASSET_LINKING",
            "Alarm/event candidates have redacted asset reference digests only.",
        ),
        "POINT_RESOLUTION_REQUIRED": (
            "Point resolution review required",
            "BLOCKS_CANONICAL_POINT_LINKING",
            "Alarm/event candidates have redacted point reference digests only.",
        ),
        "LOCATION_RESOLUTION_REQUIRED": (
            "Location resolution review required",
            "BLOCKS_CANONICAL_LOCATION_LINKING",
            "Alarm/event candidates have redacted location reference digests only.",
        ),
        "DOWNSTREAM_CREATION_NOT_AUTHORIZED": (
            "Downstream creation is not authorized",
            "BLOCKS_FAULTCASE_AND_WORKORDER_CREATION",
            "A3-02 is a read-only review projection.",
        ),
    }
    cards: list[dict[str, Any]] = []
    for reason, (title, blocking_effect, root_cause) in card_specs.items():
        affected = [row for row in rows if reason in row.get("reviewReasons", [])]
        cards.append(
            build_review_card(
                review_type=reason,
                title=title,
                affected_source_system_keys=[str(row["sourceSystemKey"]) for row in affected],
                affected_candidate_count=len(affected),
                affected_device_evidence_count=sum(int(row["deviceEvidenceCount"]) for row in affected),
                allowed_decisions=["APPROVE_FOR_NEXT_REVIEW", "KEEP_PENDING", "REJECT_RESOLUTION_PATH"],
                current_decision="KEEP_PENDING",
                blocking_effect=blocking_effect,
                root_cause=root_cause,
            )
        )
    return sorted(cards, key=lambda card: (card["reviewType"], card["reviewCardId"]))


def build_airport_alarm_event_asset_resolution_projection() -> dict[str, Any]:
    intake = _load(INTAKE_PROJECTION)
    source_review = _load(SOURCE_SYSTEM_REVIEW)
    candidates = list(intake.get("candidates", []))
    if len(candidates) != 5:
        raise ValueError("expected exactly five A3-01 alarm/event candidates")
    if source_review.get("summary", {}).get("totalBoundDeviceEvidenceCount") != 470:
        raise ValueError("expected 470 bound device evidence records from A2 source-system review")

    rows = sort_rows([_row_for_candidate(candidate) for candidate in candidates])
    cards = _review_cards(rows)
    summary = {
        "alarmEventCandidateCount": len(candidates),
        "resolutionRowCount": len(rows),
        "reviewCardCount": len(cards),
        "totalDeviceEvidenceCount": sum(int(row["deviceEvidenceCount"]) for row in rows),
        "assetResolutionRequiredCount": sum(1 for row in rows if row["assetResolutionState"] == "REVIEW_REQUIRED"),
        "pointResolutionRequiredCount": sum(1 for row in rows if row["pointResolutionState"] == "REVIEW_REQUIRED"),
        "locationResolutionRequiredCount": sum(1 for row in rows if row["locationResolutionState"] == "REVIEW_REQUIRED"),
        "registryApprovalPendingCount": sum(
            1 for row in rows if row["sourceSystemReviewState"] == ReviewState.REGISTRY_APPROVAL_PENDING.value
        ),
        "aliasApprovalPendingCount": sum(
            1 for row in rows if row["sourceSystemReviewState"] == ReviewState.ALIAS_APPROVAL_PENDING.value
        ),
        "namespaceReviewPendingCount": sum(
            1 for row in rows if row["sourceSystemReviewState"] == ReviewState.NAMESPACE_INTERPRETATION_PENDING.value
        ),
        "downstreamCreationNotAuthorizedCount": sum(
            1 for row in rows if row["downstreamCreationState"] == DownstreamCreationState.NOT_AUTHORIZED.value
        ),
        "ufmsFaultCaseCreatedCount": 0,
        "workOrderIntentCreatedCount": 0,
        "workOrderCreatedCount": 0,
        "canonicalWriteCount": 0,
        "databaseWriteCount": 0,
        "runtimeAlarmObservedCount": 0,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
    }
    projection = build_resolution_projection(
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        resolution_rows=rows,
        review_cards=cards,
        filters=build_filters(rows),
        facets=build_facets(rows),
        default_page=paginate_rows(rows, page_size=25),
        source_artifact_references=_source_artifact_references(),
    )
    validate_resolution_projection(projection)
    return projection


def write_airport_alarm_event_asset_resolution_projection(path: Path) -> dict[str, Any]:
    projection = build_airport_alarm_event_asset_resolution_projection()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return projection
