"""Airport read-only Evidence Linkage and Investigation Projection."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from evidence_investigation_projection.enums import (
    EvidenceCompletenessState,
    EvidenceRole,
    InvestigationState,
    LinkageState,
    TimelineItemType,
)
from evidence_investigation_projection.models import (
    build_evidence_investigation_projection,
    build_evidence_link,
    build_investigation_case,
    build_review_card,
    build_source_artifact_reference,
    build_timeline_item,
)
from evidence_investigation_projection.projection import build_facets, build_filters, paginate_cases, sort_cases
from evidence_investigation_projection.validation import validate_evidence_investigation_projection
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A3-05"
PROFILE_ID = "airport-evidence-investigation-profile-v1"
IMPLEMENTATION_STATUS = "EVIDENCE_INVESTIGATION_PROJECTION_COMPLETE"
READINESS_OUTCOME = "EVIDENCE_INVESTIGATION_LINKAGE_COMPLETE_WITH_PENDING_REVIEWS"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
INTAKE_PROJECTION = PROJECTIONS_DIR / "airport-alarm-event-intake-candidates.v1.json"
RESOLUTION_PROJECTION = PROJECTIONS_DIR / "airport-alarm-event-asset-resolution-review.v1.json"
FAULTCASE_PROJECTION = PROJECTIONS_DIR / "airport-faultcase-candidates.v1.json"
WORKORDER_PROJECTION = PROJECTIONS_DIR / "airport-workorder-intent-candidates.v1.json"
SOURCE_REVIEW_PROJECTION = PROJECTIONS_DIR / "airport-source-system-review.v1.json"
UCONSOLE_PROJECTION = PROJECTIONS_DIR / "airport-uconsole-integration-health.v1.json"

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
            _artifact_reference(INTAKE_PROJECTION, "ALARM_EVENT_INTAKE_CANDIDATES"),
            _artifact_reference(RESOLUTION_PROJECTION, "ALARM_EVENT_ASSET_RESOLUTION_REVIEW"),
            _artifact_reference(FAULTCASE_PROJECTION, "UFMS_FAULTCASE_CANDIDATES"),
            _artifact_reference(WORKORDER_PROJECTION, "WORKORDER_INTENT_CANDIDATES"),
            _artifact_reference(SOURCE_REVIEW_PROJECTION, "SOURCE_SYSTEM_REVIEW"),
            _artifact_reference(UCONSOLE_PROJECTION, "UCONSOLE_INTEGRATION_HEALTH"),
        ],
        key=lambda item: item["artifactType"],
    )


def _by_key(rows: list[Mapping[str, Any]], key: str = "sourceSystemKey") -> dict[str, Mapping[str, Any]]:
    return {str(row[key]): row for row in rows}


def _source_review_reason(review_state: str) -> str:
    return SOURCE_REVIEW_REASON[review_state]


def _case_review_reasons(review_state: str) -> list[str]:
    return sorted(
        {
            "INVESTIGATION_REVIEW_REQUIRED",
            "EVIDENCE_CENTER_WRITE_NOT_AUTHORIZED",
            "FAULTCASE_REVIEW_REQUIRED",
            "WORKORDER_INTENT_REVIEW_REQUIRED",
            "ASSET_RESOLUTION_REQUIRED",
            "SOURCE_SYSTEM_REVIEW_REQUIRED",
            _source_review_reason(review_state),
        }
    )


def _case_blocking_reasons(review_state: str) -> list[str]:
    return sorted(
        {
            "EVIDENCE_CENTER_WRITE_NOT_AUTHORIZED",
            "FAULTCASE_REVIEW_REQUIRED",
            "WORKORDER_INTENT_REVIEW_REQUIRED",
            "ASSET_RESOLUTION_REQUIRED",
            "SOURCE_SYSTEM_REVIEW_REQUIRED",
            _source_review_reason(review_state),
        }
    )


def _build_links(
    *,
    source_key: str,
    alarm: Mapping[str, Any],
    resolution: Mapping[str, Any],
    faultcase: Mapping[str, Any],
    workorder: Mapping[str, Any],
    case_seed: str,
) -> list[dict[str, Any]]:
    source_review_id = sha256_digest({"sourceSystemKey": source_key, "artifact": "source-system-review"})
    return [
        build_evidence_link(
            link_type="ALARM_EVENT_TO_RESOLUTION",
            source_artifact_type="ALARM_EVENT_CANDIDATE",
            source_artifact_id=str(alarm["candidateId"]),
            target_artifact_type="RESOLUTION_REVIEW",
            target_artifact_id=str(resolution["rowId"]),
            source_system_key=source_key,
            evidence_role=EvidenceRole.SOURCE_EVENT.value,
            linkage_state=LinkageState.LINKED.value,
            provenance="READ_ONLY_A3_05_LINKAGE",
            evidence_references=list(alarm.get("evidenceReferences", [])),
        ),
        build_evidence_link(
            link_type="RESOLUTION_TO_FAULTCASE_CANDIDATE",
            source_artifact_type="RESOLUTION_REVIEW",
            source_artifact_id=str(resolution["rowId"]),
            target_artifact_type="FAULTCASE_CANDIDATE",
            target_artifact_id=str(faultcase["candidateId"]),
            source_system_key=source_key,
            evidence_role=EvidenceRole.RESOLUTION_EVIDENCE.value,
            linkage_state=LinkageState.LINKED.value,
            provenance="READ_ONLY_A3_05_LINKAGE",
            evidence_references=list(resolution.get("evidenceReferences", [])),
        ),
        build_evidence_link(
            link_type="FAULTCASE_TO_WORKORDER_INTENT_CANDIDATE",
            source_artifact_type="FAULTCASE_CANDIDATE",
            source_artifact_id=str(faultcase["candidateId"]),
            target_artifact_type="WORKORDER_INTENT_CANDIDATE",
            target_artifact_id=str(workorder["candidateId"]),
            source_system_key=source_key,
            evidence_role=EvidenceRole.FAULTCASE_CANDIDATE_EVIDENCE.value,
            linkage_state=LinkageState.LINKED.value,
            provenance="READ_ONLY_A3_05_LINKAGE",
            evidence_references=list(faultcase.get("evidenceReferences", [])),
        ),
        build_evidence_link(
            link_type="SOURCE_SYSTEM_REVIEW_TO_INVESTIGATION",
            source_artifact_type="SOURCE_SYSTEM_REVIEW",
            source_artifact_id=source_review_id,
            target_artifact_type="INVESTIGATION_CASE",
            target_artifact_id=case_seed,
            source_system_key=source_key,
            evidence_role=EvidenceRole.SOURCE_SYSTEM_REVIEW_EVIDENCE.value,
            linkage_state=LinkageState.LINKED.value,
            provenance="READ_ONLY_A3_05_LINKAGE",
            evidence_references=list(workorder.get("evidenceReferences", [])),
        ),
    ]


def _build_timeline(
    *,
    source_key: str,
    alarm: Mapping[str, Any],
    resolution: Mapping[str, Any],
    faultcase: Mapping[str, Any],
    workorder: Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [
        build_timeline_item(
            source_system_key=source_key,
            sequence=1,
            item_type=TimelineItemType.ALARM_EVENT_CANDIDATE.value,
            title=f"{source_key} alarm/event candidate",
            source_artifact_type="ALARM_EVENT_CANDIDATE",
            source_artifact_id=str(alarm["candidateId"]),
            state=str(alarm.get("approvalState", "REVIEW_REQUIRED")),
            decision_required=True,
        ),
        build_timeline_item(
            source_system_key=source_key,
            sequence=2,
            item_type=TimelineItemType.RESOLUTION_REVIEW.value,
            title=f"{source_key} asset/point/location resolution review",
            source_artifact_type="RESOLUTION_REVIEW",
            source_artifact_id=str(resolution["rowId"]),
            state=str(resolution["assetResolutionState"]),
            decision_required=True,
        ),
        build_timeline_item(
            source_system_key=source_key,
            sequence=3,
            item_type=TimelineItemType.FAULTCASE_CANDIDATE.value,
            title=f"{source_key} UFMS FaultCase candidate",
            source_artifact_type="FAULTCASE_CANDIDATE",
            source_artifact_id=str(faultcase["candidateId"]),
            state=str(faultcase["proposedFaultState"]),
            decision_required=True,
        ),
        build_timeline_item(
            source_system_key=source_key,
            sequence=4,
            item_type=TimelineItemType.WORKORDER_INTENT_CANDIDATE.value,
            title=f"{source_key} WorkOrderIntent candidate",
            source_artifact_type="WORKORDER_INTENT_CANDIDATE",
            source_artifact_id=str(workorder["candidateId"]),
            state=str(workorder["eligibilityState"]),
            decision_required=True,
        ),
    ]


def _review_cards(cases: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    specs = {
        "INVESTIGATION_REVIEW_REQUIRED": ("Investigation review required", "BLOCKS_INVESTIGATION_APPROVAL", "All investigation chains require review."),
        "EVIDENCE_CENTER_WRITE_NOT_AUTHORIZED": ("Evidence Center write not authorized", "BLOCKS_EVIDENCE_RECORD_CREATION", "A3-05 is read-only."),
        "FAULTCASE_REVIEW_REQUIRED": ("FaultCase review required", "BLOCKS_INVESTIGATION_APPROVAL", "FaultCase candidates remain pending."),
        "WORKORDER_INTENT_REVIEW_REQUIRED": ("WorkOrderIntent review required", "BLOCKS_INVESTIGATION_APPROVAL", "WorkOrderIntent candidates remain pending."),
        "ASSET_RESOLUTION_REQUIRED": ("Asset resolution required", "BLOCKS_INVESTIGATION_APPROVAL", "Asset resolution remains pending."),
        "SOURCE_SYSTEM_REVIEW_REQUIRED": ("Source-system review required", "BLOCKS_INVESTIGATION_APPROVAL", "Source-system review remains pending."),
        "REGISTRY_APPROVAL_REQUIRED": ("Registry approval required", "BLOCKS_INVESTIGATION_APPROVAL", "ACS/RAS registry approval is pending."),
        "ALIAS_APPROVAL_REQUIRED": ("Alias approval required", "BLOCKS_INVESTIGATION_APPROVAL", "CCTV/PA alias approval is pending."),
        "NAMESPACE_INTERPRETATION_REQUIRED": ("Namespace interpretation required", "BLOCKS_INVESTIGATION_APPROVAL", "TEL namespace review is pending."),
    }
    cards = []
    for reason, (title, blocking_effect, root_cause) in specs.items():
        affected = [case for case in cases if reason in case.get("reviewReasons", [])]
        cards.append(
            build_review_card(
                review_type=reason,
                title=title,
                affected_source_system_keys=[str(case["sourceSystemKey"]) for case in affected],
                affected_case_count=len(affected),
                affected_device_evidence_count=sum(int(case["deviceEvidenceCount"]) for case in affected),
                allowed_decisions=["APPROVE_FOR_NEXT_REVIEW", "KEEP_PENDING", "REJECT_INVESTIGATION_CHAIN"],
                current_decision="KEEP_PENDING",
                blocking_effect=blocking_effect,
                root_cause=root_cause,
            )
        )
    return sorted(cards, key=lambda card: (card["reviewType"], card["reviewCardId"]))


def build_airport_evidence_investigation_projection() -> dict[str, Any]:
    intake = _load(INTAKE_PROJECTION)
    resolution = _load(RESOLUTION_PROJECTION)
    faultcase = _load(FAULTCASE_PROJECTION)
    workorder = _load(WORKORDER_PROJECTION)
    source_review = _load(SOURCE_REVIEW_PROJECTION)
    alarms = _by_key(list(intake.get("candidates", [])))
    resolutions = _by_key(list(resolution.get("resolutionRows", [])))
    faultcases = _by_key(list(faultcase.get("faultCaseCandidates", [])))
    workorders = _by_key(list(workorder.get("workOrderIntentCandidates", [])))
    source_keys = sorted(alarms)
    if source_keys != ["ACS", "CCTV", "PA", "RAS", "TEL"] or set(resolutions) != set(source_keys) or set(faultcases) != set(source_keys) or set(workorders) != set(source_keys):
        raise ValueError("expected exactly five matching source-system chains")
    if source_review.get("summary", {}).get("totalBoundDeviceEvidenceCount") != 470:
        raise ValueError("expected 470 source-system evidence records")

    all_links: list[dict[str, Any]] = []
    all_timeline: list[dict[str, Any]] = []
    cases: list[dict[str, Any]] = []
    for source_key in source_keys:
        alarm = alarms[source_key]
        row = resolutions[source_key]
        fault = faultcases[source_key]
        wo = workorders[source_key]
        case_seed = sha256_digest({"sourceSystemKey": source_key, "caseSeed": "A3-05"})
        links = _build_links(source_key=source_key, alarm=alarm, resolution=row, faultcase=fault, workorder=wo, case_seed=case_seed)
        timeline = _build_timeline(source_key=source_key, alarm=alarm, resolution=row, faultcase=fault, workorder=wo)
        all_links.extend(links)
        all_timeline.extend(timeline)
        cases.append(
            build_investigation_case(
                source_alarm_event_candidate_id=str(alarm["candidateId"]),
                source_resolution_row_id=str(row["rowId"]),
                source_faultcase_candidate_id=str(fault["candidateId"]),
                source_workorder_intent_candidate_id=str(wo["candidateId"]),
                source_system_key=source_key,
                investigation_state=InvestigationState.REVIEW_REQUIRED.value,
                evidence_completeness_state=EvidenceCompletenessState.PARTIAL.value,
                linkage_state=LinkageState.LINKED.value,
                decision_required=True,
                review_reasons=_case_review_reasons(str(row["sourceSystemReviewState"])),
                blocking_reasons=_case_blocking_reasons(str(row["sourceSystemReviewState"])),
                evidence_link_ids=[link["evidenceLinkId"] for link in links],
                timeline_item_ids=[item["timelineItemId"] for item in timeline],
                device_evidence_count=int(row["deviceEvidenceCount"]),
            )
        )

    cases = sort_cases(cases)
    all_links = sorted(all_links, key=lambda link: (link["sourceSystemKey"], link["linkType"], link["evidenceLinkId"]))
    all_timeline = sorted(all_timeline, key=lambda item: (item["sourceSystemKey"], item["sequence"], item["timelineItemId"]))
    cards = _review_cards(cases)
    summary = {
        "investigationCaseCount": len(cases),
        "evidenceLinkCount": len(all_links),
        "timelineItemCount": len(all_timeline),
        "reviewCardCount": len(cards),
        "totalDeviceEvidenceCount": sum(int(case["deviceEvidenceCount"]) for case in cases),
        "decisionRequiredCount": sum(1 for case in cases if case["decisionRequired"] is True),
        "partialEvidenceCaseCount": sum(1 for case in cases if case["evidenceCompletenessState"] == "PARTIAL"),
        "linkedCaseCount": sum(1 for case in cases if case["linkageState"] == "LINKED"),
        "registryApprovalPendingCount": sum(1 for case in cases if "REGISTRY_APPROVAL_REQUIRED" in case["reviewReasons"]),
        "aliasApprovalPendingCount": sum(1 for case in cases if "ALIAS_APPROVAL_REQUIRED" in case["reviewReasons"]),
        "namespaceReviewPendingCount": sum(1 for case in cases if "NAMESPACE_INTERPRETATION_REQUIRED" in case["reviewReasons"]),
        "evidenceCenterWriteCount": 0,
        "ufmsFaultCaseCreatedCount": 0,
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
    projection = build_evidence_investigation_projection(
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        investigation_cases=cases,
        evidence_links=all_links,
        investigation_timeline=all_timeline,
        review_cards=cards,
        filters=build_filters(cases, all_links, all_timeline),
        facets=build_facets(cases, all_links, all_timeline),
        default_page=paginate_cases(cases, page_size=25),
        source_artifact_references=_source_artifact_references(),
    )
    validate_evidence_investigation_projection(projection)
    return projection


def write_airport_evidence_investigation_projection(path: Path) -> dict[str, Any]:
    projection = build_airport_evidence_investigation_projection()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return projection
