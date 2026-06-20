"""Airport read-only WorkOrderIntent candidate projection."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from source_system_registry.digest import sha256_digest
from workorder_intent_candidate.enums import (
    DownstreamCreationState,
    ProposedExecutionOwner,
    ProposedMaintenanceType,
    ProposedPriority,
    ProposedSlaClass,
    ProposedTradeDiscipline,
    ProposedWorkOrderIntentType,
    WorkOrderIntentEligibilityState,
)
from workorder_intent_candidate.models import (
    build_review_card,
    build_source_artifact_reference,
    build_workorder_intent_candidate,
    build_workorder_intent_projection,
)
from workorder_intent_candidate.projection import build_facets, build_filters, paginate_candidates, sort_candidates
from workorder_intent_candidate.validation import validate_workorder_intent_projection

AUTHORITY = "ONE-AIRPORT-A3-04"
PROFILE_ID = "airport-workorder-intent-candidate-profile-v1"
IMPLEMENTATION_STATUS = "WORKORDER_INTENT_CANDIDATE_PROJECTION_COMPLETE"
READINESS_OUTCOME = "WORKORDER_INTENT_CANDIDATES_COMPLETE_WITH_PENDING_REVIEWS"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
FAULTCASE_PROJECTION = PROJECTIONS_DIR / "airport-faultcase-candidates.v1.json"
RESOLUTION_PROJECTION = PROJECTIONS_DIR / "airport-alarm-event-asset-resolution-review.v1.json"
INTAKE_PROJECTION = PROJECTIONS_DIR / "airport-alarm-event-intake-candidates.v1.json"
SOURCE_SYSTEM_REVIEW = PROJECTIONS_DIR / "airport-source-system-review.v1.json"

INTENT_TYPE_BY_SOURCE = {
    "ACS": ProposedWorkOrderIntentType.CORRECTIVE_MAINTENANCE.value,
    "RAS": ProposedWorkOrderIntentType.INVESTIGATION_REQUEST.value,
    "CCTV": ProposedWorkOrderIntentType.INVESTIGATION_REQUEST.value,
    "PA": ProposedWorkOrderIntentType.CORRECTIVE_MAINTENANCE.value,
    "TEL": ProposedWorkOrderIntentType.INVESTIGATION_REQUEST.value,
}
MAINTENANCE_TYPE_BY_INTENT = {
    ProposedWorkOrderIntentType.CORRECTIVE_MAINTENANCE.value: ProposedMaintenanceType.CORRECTIVE.value,
    ProposedWorkOrderIntentType.INVESTIGATION_REQUEST.value: ProposedMaintenanceType.INVESTIGATION.value,
}
TRADE_BY_SOURCE = {
    "ACS": ProposedTradeDiscipline.SECURITY.value,
    "RAS": ProposedTradeDiscipline.COMMUNICATION.value,
    "CCTV": ProposedTradeDiscipline.SECURITY.value,
    "PA": ProposedTradeDiscipline.ELV.value,
    "TEL": ProposedTradeDiscipline.COMMUNICATION.value,
}
PRIORITY_BY_SOURCE = {
    "ACS": ProposedPriority.P2_HIGH.value,
    "RAS": ProposedPriority.P3_MEDIUM.value,
    "CCTV": ProposedPriority.P4_LOW.value,
    "PA": ProposedPriority.P4_LOW.value,
    "TEL": ProposedPriority.P3_MEDIUM.value,
}
SLA_BY_PRIORITY = {
    ProposedPriority.P1_CRITICAL.value: ProposedSlaClass.EMERGENCY.value,
    ProposedPriority.P2_HIGH.value: ProposedSlaClass.URGENT.value,
    ProposedPriority.P3_MEDIUM.value: ProposedSlaClass.STANDARD.value,
    ProposedPriority.P4_LOW.value: ProposedSlaClass.LOW.value,
}
SOURCE_REVIEW_REASON = {
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
    return sorted(
        [
            _artifact_reference(FAULTCASE_PROJECTION, "UFMS_FAULTCASE_CANDIDATES"),
            _artifact_reference(RESOLUTION_PROJECTION, "ALARM_EVENT_ASSET_RESOLUTION_REVIEW"),
            _artifact_reference(INTAKE_PROJECTION, "ALARM_EVENT_INTAKE_CANDIDATES"),
            _artifact_reference(SOURCE_SYSTEM_REVIEW, "SOURCE_SYSTEM_REVIEW"),
        ],
        key=lambda item: item["artifactType"],
    )


def _candidate_for_faultcase(faultcase: Mapping[str, Any], evidence_count: int) -> dict[str, Any]:
    source_system_key = str(faultcase["sourceSystemKey"])
    intent_type = INTENT_TYPE_BY_SOURCE[source_system_key]
    source_review_reason = SOURCE_REVIEW_REASON[str(faultcase["sourceSystemReviewState"])]
    blocking_reasons = sorted(
        {
            "WORKORDER_INTENT_CREATION_NOT_AUTHORIZED",
            "BLOCKED_BY_FAULTCASE_REVIEW",
            "BLOCKED_BY_RESOLUTION",
            "BLOCKED_BY_SOURCE_SYSTEM_REVIEW",
            "WORK_MANAGEMENT_POLICY_REVIEW_REQUIRED",
            source_review_reason,
            "ASSET_RESOLUTION_REQUIRED",
            "POINT_RESOLUTION_REQUIRED",
            "LOCATION_RESOLUTION_REQUIRED",
        }
    )
    review_reasons = sorted(
        {
            "WORKORDER_INTENT_CREATION_NOT_AUTHORIZED",
            "FAULTCASE_REVIEW_REQUIRED",
            "SOURCE_SYSTEM_REVIEW_REQUIRED",
            "WORK_MANAGEMENT_POLICY_REVIEW_REQUIRED",
            source_review_reason,
            "ASSET_RESOLUTION_REQUIRED",
            "POINT_RESOLUTION_REQUIRED",
            "LOCATION_RESOLUTION_REQUIRED",
        }
    )
    priority = PRIORITY_BY_SOURCE[source_system_key]
    return build_workorder_intent_candidate(
        source_faultcase_candidate_id=str(faultcase["candidateId"]),
        source_alarm_event_candidate_id=str(faultcase["sourceAlarmEventCandidateId"]),
        source_system_key=source_system_key,
        proposed_workorder_intent_type=intent_type,
        proposed_maintenance_type=MAINTENANCE_TYPE_BY_INTENT[intent_type],
        proposed_priority=priority,
        proposed_trade_discipline=TRADE_BY_SOURCE[source_system_key],
        proposed_execution_owner=ProposedExecutionOwner.ONE_WORK_MANAGEMENT.value,
        proposed_sla_class=SLA_BY_PRIORITY[priority],
        eligibility_state=WorkOrderIntentEligibilityState.BLOCKED_BY_FAULTCASE_REVIEW.value,
        blocking_reasons=blocking_reasons,
        source_system_review_state=str(faultcase["sourceSystemReviewState"]),
        asset_resolution_state=str(faultcase["assetResolutionState"]),
        point_resolution_state=str(faultcase["pointResolutionState"]),
        location_resolution_state=str(faultcase["locationResolutionState"]),
        faultcase_candidate_state=str(faultcase["proposedFaultState"]),
        downstream_creation_state=DownstreamCreationState.NOT_AUTHORIZED.value,
        device_evidence_count=evidence_count,
        evidence_references=list(faultcase.get("evidenceReferences", [])),
        decision_required=True,
        review_reasons=review_reasons,
    )


def _review_cards(candidates: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    card_specs = {
        "WORKORDER_INTENT_CREATION_NOT_AUTHORIZED": ("WorkOrderIntent creation is not authorized", "BLOCKS_WORKORDER_INTENT_CREATION", "A3-04 is read-only."),
        "FAULTCASE_REVIEW_REQUIRED": ("FaultCase review required", "BLOCKS_WORKORDER_INTENT_CREATION", "FaultCase candidates are not approved."),
        "SOURCE_SYSTEM_REVIEW_REQUIRED": ("Source-system review required", "BLOCKS_WORKORDER_INTENT_CREATION", "Source-system review is pending."),
        "ASSET_RESOLUTION_REQUIRED": ("Asset resolution required", "BLOCKS_WORKORDER_INTENT_CREATION", "Canonical asset resolution is pending."),
        "POINT_RESOLUTION_REQUIRED": ("Point resolution required", "BLOCKS_WORKORDER_INTENT_CREATION", "Canonical point resolution is pending."),
        "LOCATION_RESOLUTION_REQUIRED": ("Location resolution required", "BLOCKS_WORKORDER_INTENT_CREATION", "Canonical location resolution is pending."),
        "REGISTRY_APPROVAL_REQUIRED": ("Registry approval required", "BLOCKS_WORKORDER_INTENT_CREATION", "ACS/RAS registry approval is pending."),
        "ALIAS_APPROVAL_REQUIRED": ("Alias approval required", "BLOCKS_WORKORDER_INTENT_CREATION", "CCTV/PA alias approval is pending."),
        "NAMESPACE_INTERPRETATION_REQUIRED": ("Namespace interpretation required", "BLOCKS_WORKORDER_INTENT_CREATION", "TEL namespace review is pending."),
        "WORK_MANAGEMENT_POLICY_REVIEW_REQUIRED": ("Work Management policy review required", "BLOCKS_WORKORDER_INTENT_CREATION", "Intent routing policy requires review."),
    }
    cards = []
    for reason, (title, blocking_effect, root_cause) in card_specs.items():
        affected = [candidate for candidate in candidates if reason in candidate.get("reviewReasons", [])]
        cards.append(
            build_review_card(
                review_type=reason,
                title=title,
                affected_source_system_keys=[str(candidate["sourceSystemKey"]) for candidate in affected],
                affected_candidate_count=len(affected),
                affected_device_evidence_count=sum(int(candidate["deviceEvidenceCount"]) for candidate in affected),
                allowed_decisions=["APPROVE_FOR_NEXT_REVIEW", "KEEP_PENDING", "REJECT_CANDIDATE"],
                current_decision="KEEP_PENDING",
                blocking_effect=blocking_effect,
                root_cause=root_cause,
            )
        )
    return sorted(cards, key=lambda card: (card["reviewType"], card["reviewCardId"]))


def build_airport_workorder_intent_candidate_projection() -> dict[str, Any]:
    faultcase_projection = _load(FAULTCASE_PROJECTION)
    resolution_projection = _load(RESOLUTION_PROJECTION)
    intake_projection = _load(INTAKE_PROJECTION)
    source_review = _load(SOURCE_SYSTEM_REVIEW)
    faultcases = list(faultcase_projection.get("faultCaseCandidates", []))
    resolution_rows = list(resolution_projection.get("resolutionRows", []))
    if len(faultcases) != 5 or len(resolution_rows) != 5 or len(intake_projection.get("candidates", [])) != 5:
        raise ValueError("expected exactly five upstream candidates")
    if source_review.get("summary", {}).get("totalBoundDeviceEvidenceCount") != 470:
        raise ValueError("expected 470 source-system evidence records")

    evidence_counts = {str(row["sourceSystemKey"]): int(row["deviceEvidenceCount"]) for row in resolution_rows}
    candidates = sort_candidates(
        [_candidate_for_faultcase(faultcase, evidence_counts[str(faultcase["sourceSystemKey"])]) for faultcase in faultcases]
    )
    cards = _review_cards(candidates)
    summary = {
        "faultCaseCandidateCount": len(faultcases),
        "workOrderIntentCandidateCount": len(candidates),
        "reviewCardCount": len(cards),
        "totalDeviceEvidenceCount": sum(evidence_counts.values()),
        "correctiveMaintenanceCandidateCount": sum(
            1 for item in candidates if item["proposedWorkOrderIntentType"] == "CORRECTIVE_MAINTENANCE"
        ),
        "investigationRequestCandidateCount": sum(
            1 for item in candidates if item["proposedWorkOrderIntentType"] == "INVESTIGATION_REQUEST"
        ),
        "blockedByFaultCaseReviewCount": sum(1 for item in candidates if "BLOCKED_BY_FAULTCASE_REVIEW" in item["blockingReasons"]),
        "blockedByResolutionCount": sum(1 for item in candidates if "BLOCKED_BY_RESOLUTION" in item["blockingReasons"]),
        "blockedBySourceSystemReviewCount": sum(
            1 for item in candidates if "BLOCKED_BY_SOURCE_SYSTEM_REVIEW" in item["blockingReasons"]
        ),
        "workManagementPolicyReviewRequiredCount": sum(
            1 for item in candidates if "WORK_MANAGEMENT_POLICY_REVIEW_REQUIRED" in item["reviewReasons"]
        ),
        "decisionRequiredCount": sum(1 for item in candidates if item["decisionRequired"] is True),
        "workOrderIntentCreatedCount": 0,
        "workOrderCreatedCount": 0,
        "ummsWriteCount": 0,
        "oneWorkManagementWriteCount": 0,
        "canonicalWriteCount": 0,
        "databaseWriteCount": 0,
        "runtimeAlarmObservedCount": 0,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
    }
    projection = build_workorder_intent_projection(
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        workorder_intent_candidates=candidates,
        review_cards=cards,
        filters=build_filters(candidates),
        facets=build_facets(candidates),
        default_page=paginate_candidates(candidates, page_size=25),
        source_artifact_references=_source_artifact_references(),
    )
    validate_workorder_intent_projection(projection)
    return projection


def write_airport_workorder_intent_candidate_projection(path: Path) -> dict[str, Any]:
    projection = build_airport_workorder_intent_candidate_projection()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return projection
