"""Airport read-only UFMS FaultCase candidate projection."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from faultcase_candidate.enums import (
    DownstreamCreationState,
    FaultCaseEligibilityState,
    ProposedFaultCaseType,
    ProposedFaultPriority,
    ProposedFaultState,
)
from faultcase_candidate.models import (
    build_faultcase_candidate,
    build_faultcase_projection,
    build_review_card,
    build_source_artifact_reference,
)
from faultcase_candidate.projection import build_facets, build_filters, paginate_candidates, sort_candidates
from faultcase_candidate.validation import validate_faultcase_projection
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A3-03"
PROFILE_ID = "airport-ufms-faultcase-candidate-profile-v1"
IMPLEMENTATION_STATUS = "UFMS_FAULTCASE_CANDIDATE_PROJECTION_COMPLETE"
READINESS_OUTCOME = "FAULTCASE_CANDIDATES_COMPLETE_WITH_PENDING_REVIEWS"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
INTAKE_PROJECTION = PROJECTIONS_DIR / "airport-alarm-event-intake-candidates.v1.json"
RESOLUTION_PROJECTION = PROJECTIONS_DIR / "airport-alarm-event-asset-resolution-review.v1.json"
SOURCE_SYSTEM_REVIEW = PROJECTIONS_DIR / "airport-source-system-review.v1.json"

FAULT_TYPE_BY_SOURCE = {
    "ACS": ProposedFaultCaseType.SECURITY_FAULT.value,
    "RAS": ProposedFaultCaseType.COMMUNICATION_FAULT.value,
    "CCTV": ProposedFaultCaseType.SECURITY_FAULT.value,
    "PA": ProposedFaultCaseType.EQUIPMENT_FAULT.value,
    "TEL": ProposedFaultCaseType.COMMUNICATION_FAULT.value,
}
FAULT_PRIORITY_BY_SOURCE = {
    "ACS": ProposedFaultPriority.P2_HIGH.value,
    "RAS": ProposedFaultPriority.P3_MEDIUM.value,
    "CCTV": ProposedFaultPriority.P4_LOW.value,
    "PA": ProposedFaultPriority.P4_LOW.value,
    "TEL": ProposedFaultPriority.P3_MEDIUM.value,
}
REVIEW_REASON_BY_SOURCE_REVIEW = {
    "REGISTRY_APPROVAL_PENDING": "REGISTRY_APPROVAL_REQUIRED",
    "ALIAS_APPROVAL_PENDING": "ALIAS_APPROVAL_REQUIRED",
    "NAMESPACE_INTERPRETATION_PENDING": "NAMESPACE_INTERPRETATION_REQUIRED",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_reference(path: Path, artifact_type: str) -> dict[str, Any]:
    return build_source_artifact_reference(
        artifact_type=artifact_type,
        path=str(path.relative_to(ROOT)),
        digest=sha256_digest(_load(path)),
    )


def _source_artifact_references() -> list[dict[str, Any]]:
    refs = [
        _artifact_reference(INTAKE_PROJECTION, "ALARM_EVENT_INTAKE_CANDIDATES"),
        _artifact_reference(RESOLUTION_PROJECTION, "ALARM_EVENT_ASSET_RESOLUTION_REVIEW"),
        _artifact_reference(SOURCE_SYSTEM_REVIEW, "SOURCE_SYSTEM_REVIEW"),
    ]
    return sorted(refs, key=lambda item: item["artifactType"])


def _candidate_for_resolution_row(row: Mapping[str, Any]) -> dict[str, Any]:
    source_system_key = str(row["sourceSystemKey"])
    source_review_reason = REVIEW_REASON_BY_SOURCE_REVIEW[str(row["sourceSystemReviewState"])]
    blocking_reasons = sorted(
        {
            "FAULTCASE_CREATION_NOT_AUTHORIZED",
            "BLOCKED_BY_SOURCE_SYSTEM_REVIEW",
            "BLOCKED_BY_RESOLUTION",
            source_review_reason,
            "ASSET_RESOLUTION_REQUIRED",
            "POINT_RESOLUTION_REQUIRED",
            "LOCATION_RESOLUTION_REQUIRED",
        }
    )
    review_reasons = sorted(
        {
            "FAULTCASE_CREATION_NOT_AUTHORIZED",
            "SOURCE_SYSTEM_REVIEW_REQUIRED",
            source_review_reason,
            "ASSET_RESOLUTION_REQUIRED",
            "POINT_RESOLUTION_REQUIRED",
            "LOCATION_RESOLUTION_REQUIRED",
        }
    )
    return build_faultcase_candidate(
        source_alarm_event_candidate_id=str(row["candidateId"]),
        source_system_key=source_system_key,
        event_kind=str(row["eventKind"]),
        event_category=str(row["eventCategory"]),
        event_severity=str(row["eventSeverity"]),
        proposed_fault_case_type=FAULT_TYPE_BY_SOURCE[source_system_key],
        proposed_fault_priority=FAULT_PRIORITY_BY_SOURCE[source_system_key],
        proposed_fault_state=ProposedFaultState.BLOCKED.value,
        eligibility_state=FaultCaseEligibilityState.BLOCKED_BY_RESOLUTION.value,
        blocking_reasons=blocking_reasons,
        asset_resolution_state=str(row["assetResolutionState"]),
        point_resolution_state=str(row["pointResolutionState"]),
        location_resolution_state=str(row["locationResolutionState"]),
        source_system_review_state=str(row["sourceSystemReviewState"]),
        downstream_creation_state=DownstreamCreationState.NOT_AUTHORIZED.value,
        evidence_references=list(row.get("evidenceReferences", [])),
        decision_required=True,
        review_reasons=review_reasons,
    )


def _review_cards(candidates: list[Mapping[str, Any]], evidence_counts: Mapping[str, int]) -> list[dict[str, Any]]:
    card_specs = {
        "FAULTCASE_CREATION_NOT_AUTHORIZED": (
            "FaultCase creation is not authorized",
            "BLOCKS_UFMS_FAULTCASE_CREATION",
            "A3-03 is a read-only candidate projection.",
        ),
        "SOURCE_SYSTEM_REVIEW_REQUIRED": (
            "Source-system review required",
            "BLOCKS_UFMS_FAULTCASE_CREATION",
            "Source-system registry, alias, or namespace review is pending.",
        ),
        "ASSET_RESOLUTION_REQUIRED": (
            "Asset resolution required",
            "BLOCKS_UFMS_FAULTCASE_CREATION",
            "FaultCase candidates cannot bind canonical assets yet.",
        ),
        "POINT_RESOLUTION_REQUIRED": (
            "Point resolution required",
            "BLOCKS_UFMS_FAULTCASE_CREATION",
            "FaultCase candidates cannot bind canonical points yet.",
        ),
        "LOCATION_RESOLUTION_REQUIRED": (
            "Location resolution required",
            "BLOCKS_UFMS_FAULTCASE_CREATION",
            "FaultCase candidates cannot bind canonical locations yet.",
        ),
        "REGISTRY_APPROVAL_REQUIRED": (
            "Registry approval required",
            "BLOCKS_UFMS_FAULTCASE_CREATION",
            "ACS/RAS source systems remain registry candidates.",
        ),
        "ALIAS_APPROVAL_REQUIRED": (
            "Alias approval required",
            "BLOCKS_UFMS_FAULTCASE_CREATION",
            "CCTV/PA aliases remain pending.",
        ),
        "NAMESPACE_INTERPRETATION_REQUIRED": (
            "Namespace interpretation required",
            "BLOCKS_UFMS_FAULTCASE_CREATION",
            "TEL namespace interpretation remains pending.",
        ),
    }
    cards: list[dict[str, Any]] = []
    for reason, (title, blocking_effect, root_cause) in card_specs.items():
        affected = [candidate for candidate in candidates if reason in candidate.get("reviewReasons", [])]
        cards.append(
            build_review_card(
                review_type=reason,
                title=title,
                affected_source_system_keys=[str(candidate["sourceSystemKey"]) for candidate in affected],
                affected_candidate_count=len(affected),
                affected_device_evidence_count=sum(int(evidence_counts[str(candidate["sourceSystemKey"])]) for candidate in affected),
                allowed_decisions=["APPROVE_FOR_NEXT_REVIEW", "KEEP_PENDING", "REJECT_CANDIDATE"],
                current_decision="KEEP_PENDING",
                blocking_effect=blocking_effect,
                root_cause=root_cause,
            )
        )
    return sorted(cards, key=lambda card: (card["reviewType"], card["reviewCardId"]))


def build_airport_faultcase_candidate_projection() -> dict[str, Any]:
    intake = _load(INTAKE_PROJECTION)
    resolution = _load(RESOLUTION_PROJECTION)
    source_review = _load(SOURCE_SYSTEM_REVIEW)
    intake_candidates = list(intake.get("candidates", []))
    resolution_rows = list(resolution.get("resolutionRows", []))
    if len(intake_candidates) != 5 or len(resolution_rows) != 5:
        raise ValueError("expected exactly five alarm/event candidates and resolution rows")
    if source_review.get("summary", {}).get("totalBoundDeviceEvidenceCount") != 470:
        raise ValueError("expected 470 source-system review evidence records")

    evidence_counts = {str(row["sourceSystemKey"]): int(row["deviceEvidenceCount"]) for row in resolution_rows}
    candidates = sort_candidates([_candidate_for_resolution_row(row) for row in resolution_rows])
    cards = _review_cards(candidates, evidence_counts)
    summary = {
        "alarmEventCandidateCount": len(intake_candidates),
        "resolutionRowCount": len(resolution_rows),
        "faultCaseCandidateCount": len(candidates),
        "reviewCardCount": len(cards),
        "totalDeviceEvidenceCount": sum(evidence_counts.values()),
        "securityFaultCandidateCount": sum(1 for item in candidates if item["proposedFaultCaseType"] == "SECURITY_FAULT"),
        "communicationFaultCandidateCount": sum(
            1 for item in candidates if item["proposedFaultCaseType"] == "COMMUNICATION_FAULT"
        ),
        "equipmentFaultCandidateCount": sum(1 for item in candidates if item["proposedFaultCaseType"] == "EQUIPMENT_FAULT"),
        "blockedByResolutionCount": sum(1 for item in candidates if "BLOCKED_BY_RESOLUTION" in item["blockingReasons"]),
        "blockedBySourceSystemReviewCount": sum(
            1 for item in candidates if "BLOCKED_BY_SOURCE_SYSTEM_REVIEW" in item["blockingReasons"]
        ),
        "decisionRequiredCount": sum(1 for item in candidates if item["decisionRequired"] is True),
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
    projection = build_faultcase_projection(
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        faultcase_candidates=candidates,
        review_cards=cards,
        filters=build_filters(candidates),
        facets=build_facets(candidates),
        default_page=paginate_candidates(candidates, page_size=25),
        source_artifact_references=_source_artifact_references(),
    )
    validate_faultcase_projection(projection)
    return projection


def write_airport_faultcase_candidate_projection(path: Path) -> dict[str, Any]:
    projection = build_airport_faultcase_candidate_projection()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return projection
