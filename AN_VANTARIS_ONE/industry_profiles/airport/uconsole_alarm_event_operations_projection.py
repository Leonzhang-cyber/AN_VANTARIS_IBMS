"""Airport read-only UConsole Alarm/Event Operations Projection."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest
from uconsole_alarm_event_operations.enums import CardType, OperationsStatus
from uconsole_alarm_event_operations.models import (
    build_operations_card,
    build_operations_projection,
    build_operations_row,
    build_source_artifact_reference,
)
from uconsole_alarm_event_operations.projection import build_facets, build_filters, paginate_rows, sort_rows
from uconsole_alarm_event_operations.validation import validate_operations_projection

AUTHORITY = "ONE-AIRPORT-A3-06"
PROFILE_ID = "airport-uconsole-alarm-event-operations-profile-v1"
IMPLEMENTATION_STATUS = "READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_COMPLETE"
READINESS_OUTCOME = "UCONSOLE_ALARM_EVENT_OPERATIONS_READ_ONLY_PROJECTION_COMPLETE_PENDING_REVIEWS"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
INTAKE_PROJECTION = PROJECTIONS_DIR / "airport-alarm-event-intake-candidates.v1.json"
RESOLUTION_PROJECTION = PROJECTIONS_DIR / "airport-alarm-event-asset-resolution-review.v1.json"
FAULTCASE_PROJECTION = PROJECTIONS_DIR / "airport-faultcase-candidates.v1.json"
WORKORDER_PROJECTION = PROJECTIONS_DIR / "airport-workorder-intent-candidates.v1.json"
INVESTIGATION_PROJECTION = PROJECTIONS_DIR / "airport-evidence-investigation.v1.json"
UCONSOLE_HEALTH_PROJECTION = PROJECTIONS_DIR / "airport-uconsole-integration-health.v1.json"

SOURCE_REVIEW_REASON = {
    "REGISTRY_APPROVAL_PENDING": "REGISTRY_APPROVAL_REQUIRED",
    "ALIAS_APPROVAL_PENDING": "ALIAS_APPROVAL_REQUIRED",
    "NAMESPACE_INTERPRETATION_PENDING": "NAMESPACE_INTERPRETATION_REQUIRED",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _by_key(rows: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    return {str(row["sourceSystemKey"]): row for row in rows}


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
            _artifact_reference(INVESTIGATION_PROJECTION, "EVIDENCE_INVESTIGATION"),
            _artifact_reference(UCONSOLE_HEALTH_PROJECTION, "UCONSOLE_INTEGRATION_HEALTH"),
        ],
        key=lambda item: item["artifactType"],
    )


def _unique(values: Sequence[str]) -> list[str]:
    return sorted({value for value in values if value})


def _row_review_reasons(
    *,
    alarm: Mapping[str, Any],
    resolution: Mapping[str, Any],
    faultcase: Mapping[str, Any],
    workorder: Mapping[str, Any],
    investigation: Mapping[str, Any],
    health: Mapping[str, Any],
) -> list[str]:
    reasons: list[str] = []
    for artifact in (alarm, resolution, faultcase, workorder, investigation):
        reasons.extend(str(reason) for reason in artifact.get("reviewReasons", []))
    reasons.extend(
        [
            "ALARM_EVENT_QUEUE_REVIEW_REQUIRED",
            "FAULTCASE_REVIEW_REQUIRED",
            "WORKORDER_INTENT_REVIEW_REQUIRED",
            "EVIDENCE_INVESTIGATION_REVIEW_REQUIRED",
        ]
    )
    if not bool(health.get("runtimeObserved")):
        reasons.append("RUNTIME_PENDING_REVIEW_REQUIRED")
    review_state = str(health.get("reviewState") or resolution.get("sourceSystemReviewState"))
    reasons.append(SOURCE_REVIEW_REASON[review_state])
    return _unique(reasons)


def _row_blocking_reasons(
    *,
    faultcase: Mapping[str, Any],
    workorder: Mapping[str, Any],
    investigation: Mapping[str, Any],
    health: Mapping[str, Any],
) -> list[str]:
    reasons: list[str] = []
    for artifact in (faultcase, workorder, investigation):
        reasons.extend(str(reason) for reason in artifact.get("blockingReasons", []))
    reasons.extend(
        [
            "ALARM_EVENT_OPERATIONS_READ_ONLY",
            "FAULTCASE_CREATION_NOT_AUTHORIZED",
            "WORKORDER_INTENT_CREATION_NOT_AUTHORIZED",
            "EVIDENCE_CENTER_WRITE_NOT_AUTHORIZED",
        ]
    )
    if not bool(health.get("runtimeObserved")):
        reasons.append("RUNTIME_PENDING")
    return _unique(reasons)


def _build_rows() -> list[dict[str, Any]]:
    intake = _load(INTAKE_PROJECTION)
    resolution = _load(RESOLUTION_PROJECTION)
    faultcase = _load(FAULTCASE_PROJECTION)
    workorder = _load(WORKORDER_PROJECTION)
    investigation = _load(INVESTIGATION_PROJECTION)
    health = _load(UCONSOLE_HEALTH_PROJECTION)

    alarms_by_key = _by_key(list(intake.get("candidates", [])))
    resolution_by_key = _by_key(list(resolution.get("resolutionRows", [])))
    faultcase_by_key = _by_key(list(faultcase.get("faultCaseCandidates", [])))
    workorder_by_key = _by_key(list(workorder.get("workOrderIntentCandidates", [])))
    investigation_by_key = _by_key(list(investigation.get("investigationCases", [])))
    health_by_key = _by_key(list(health.get("sourceSystemRows", [])))

    rows: list[dict[str, Any]] = []
    for source_key in sorted(alarms_by_key):
        alarm = alarms_by_key[source_key]
        resolution_row = resolution_by_key[source_key]
        faultcase_candidate = faultcase_by_key[source_key]
        workorder_candidate = workorder_by_key[source_key]
        investigation_case = investigation_by_key[source_key]
        health_row = health_by_key[source_key]
        review_reasons = _row_review_reasons(
            alarm=alarm,
            resolution=resolution_row,
            faultcase=faultcase_candidate,
            workorder=workorder_candidate,
            investigation=investigation_case,
            health=health_row,
        )
        blocking_reasons = _row_blocking_reasons(
            faultcase=faultcase_candidate,
            workorder=workorder_candidate,
            investigation=investigation_case,
            health=health_row,
        )
        rows.append(
            build_operations_row(
                source_system_key=source_key,
                alarm_event_candidate_id=str(alarm["candidateId"]),
                resolution_row_id=str(resolution_row["rowId"]),
                faultcase_candidate_id=str(faultcase_candidate["candidateId"]),
                workorder_intent_candidate_id=str(workorder_candidate["candidateId"]),
                investigation_case_id=str(investigation_case["investigationCaseId"]),
                event_kind=str(alarm["eventKind"]),
                event_category=str(alarm["eventCategory"]),
                event_severity=str(alarm["eventSeverity"]),
                alarm_event_state=str(alarm["eventState"]),
                faultcase_candidate_state=str(faultcase_candidate["proposedFaultState"]),
                workorder_intent_candidate_state=str(workorder_candidate["eligibilityState"]),
                investigation_state=str(investigation_case["investigationState"]),
                asset_resolution_state=str(resolution_row["assetResolutionState"]),
                source_system_review_state=str(resolution_row["sourceSystemReviewState"]),
                operational_status=OperationsStatus.BLOCKED.value,
                operational_severity=str(alarm["eventSeverity"]),
                decision_required=True,
                pending_decision_count=len(review_reasons),
                device_evidence_count=int(resolution_row["deviceEvidenceCount"]),
                review_reasons=review_reasons,
                blocking_reasons=blocking_reasons,
            )
        )
    return sort_rows(rows)


def _card(
    card_type: CardType,
    title: str,
    value: int,
    rows: Sequence[Mapping[str, Any]],
    *,
    severity: str = "HIGH",
    status: str = OperationsStatus.REVIEW_REQUIRED.value,
) -> dict[str, Any]:
    return build_operations_card(
        card_type=card_type.value,
        title=title,
        value=value,
        unit="ROWS",
        status=status,
        severity=severity,
        affected_source_system_keys=[str(row["sourceSystemKey"]) for row in rows],
        affected_row_count=len(rows),
        affected_device_evidence_count=sum(int(row["deviceEvidenceCount"]) for row in rows),
        decision_required=True,
    )


def _build_cards(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        _card(CardType.ALARM_EVENT_QUEUE, "Alarm/Event queue", len(rows), rows),
        _card(CardType.FAULTCASE_CANDIDATE_QUEUE, "FaultCase candidate queue", len(rows), rows),
        _card(CardType.WORKORDER_INTENT_QUEUE, "WorkOrderIntent queue", len(rows), rows),
        _card(CardType.EVIDENCE_INVESTIGATION_QUEUE, "Evidence investigation queue", len(rows), rows),
        _card(CardType.REVIEW_REQUIRED_SUMMARY, "Review-required summary", len(rows), rows),
        _card(
            CardType.RUNTIME_PENDING_SUMMARY,
            "Runtime pending summary",
            sum(1 for row in rows if "RUNTIME_PENDING" in row.get("blockingReasons", [])),
            rows,
            status=OperationsStatus.RUNTIME_PENDING.value,
        ),
        _card(CardType.SOURCE_SYSTEM_SUMMARY, "Source-system summary", len(rows), rows, severity="MEDIUM"),
    ]


def _summary(rows: Sequence[Mapping[str, Any]], cards: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "operationsRowCount": len(rows),
        "operationsCardCount": len(cards),
        "alarmEventCandidateCount": len(rows),
        "resolutionRowCount": len(rows),
        "faultCaseCandidateCount": len(rows),
        "workOrderIntentCandidateCount": len(rows),
        "investigationCaseCount": len(rows),
        "totalDeviceEvidenceCount": sum(int(row["deviceEvidenceCount"]) for row in rows),
        "decisionRequiredCount": sum(1 for row in rows if row["decisionRequired"]),
        "reviewRequiredRowCount": len(rows),
        "blockedRowCount": sum(1 for row in rows if row["operationalStatus"] == OperationsStatus.BLOCKED.value),
        "runtimePendingCount": sum(1 for row in rows if "RUNTIME_PENDING" in row.get("blockingReasons", [])),
        "registryApprovalPendingCount": sum(1 for row in rows if row["sourceSystemReviewState"] == "REGISTRY_APPROVAL_PENDING"),
        "aliasApprovalPendingCount": sum(1 for row in rows if row["sourceSystemReviewState"] == "ALIAS_APPROVAL_PENDING"),
        "namespaceReviewPendingCount": sum(1 for row in rows if row["sourceSystemReviewState"] == "NAMESPACE_INTERPRETATION_PENDING"),
        "assetResolutionRequiredCount": sum(1 for row in rows if row["assetResolutionState"] == "REVIEW_REQUIRED"),
        "faultCaseReviewRequiredCount": sum(1 for row in rows if "FAULTCASE_REVIEW_REQUIRED" in row["reviewReasons"]),
        "workOrderIntentReviewRequiredCount": sum(1 for row in rows if "WORKORDER_INTENT_REVIEW_REQUIRED" in row["reviewReasons"]),
        "evidenceInvestigationReviewRequiredCount": sum(1 for row in rows if "EVIDENCE_INVESTIGATION_REVIEW_REQUIRED" in row["reviewReasons"]),
        "runtimeAlarmObservedCount": 0,
        "ufmsFaultCaseCreatedCount": 0,
        "workOrderIntentCreatedCount": 0,
        "workOrderCreatedCount": 0,
        "evidenceCenterWriteCount": 0,
        "ummsWriteCount": 0,
        "oneWorkManagementWriteCount": 0,
        "canonicalWriteCount": 0,
        "databaseWriteCount": 0,
        "apiEnabled": False,
        "frontendEnabled": False,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
    }


def build_airport_uconsole_alarm_event_operations_projection() -> dict[str, Any]:
    rows = _build_rows()
    cards = _build_cards(rows)
    projection = build_operations_projection(
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        operations_rows=rows,
        operations_cards=cards,
        queue_cards=cards[:4],
        investigation_cards=[cards[3]],
        filters=build_filters(rows),
        facets=build_facets(rows),
        default_page=paginate_rows(rows, page_size=25),
        source_artifact_references=_source_artifact_references(),
        summary=_summary(rows, cards),
    )
    validate_operations_projection(projection)
    return projection
