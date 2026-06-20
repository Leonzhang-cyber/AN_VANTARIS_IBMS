"""Airport read-only UConsole Operator Review Queue Projection."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest
from uconsole_operator_review_queue.enums import QueueCardType, QueueStatus, Severity
from uconsole_operator_review_queue.models import (
    build_queue_card,
    build_queue_group,
    build_queue_row,
    build_source_artifact_reference,
    build_uconsole_operator_review_queue_projection,
)
from uconsole_operator_review_queue.projection import build_facets, build_filters, paginate_queue_rows, sort_queue_rows
from uconsole_operator_review_queue.validation import validate_uconsole_operator_review_queue_projection

AUTHORITY = "ONE-AIRPORT-A4-02"
PROFILE_ID = "airport-uconsole-operator-review-queue-profile-v1"
IMPLEMENTATION_STATUS = "OPERATOR_REVIEW_UCONSOLE_QUEUE_PROJECTION_COMPLETE"
READINESS_OUTCOME = "UCONSOLE_OPERATOR_REVIEW_QUEUE_READY_FOR_READ_ONLY_CONSUMPTION"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
DECISIONS = PROJECTIONS_DIR / "airport-operator-review-decisions.v1.json"

QUEUE_TITLES = {
    "ALL_PENDING_QUEUE": "All pending operator decisions",
    "SOURCE_SYSTEM_QUEUE": "Source-system review decisions",
    "ASSET_RESOLUTION_QUEUE": "Asset, point and location resolution decisions",
    "ALARM_EVENT_QUEUE": "Alarm/Event review decisions",
    "FAULTCASE_QUEUE": "FaultCase candidate decisions",
    "WORKORDER_INTENT_QUEUE": "WorkOrderIntent decisions",
    "EVIDENCE_INVESTIGATION_QUEUE": "Evidence investigation decisions",
    "RELEASE_GATE_QUEUE": "Release gate decisions",
}

QUEUE_CARD_TYPES = {
    "ALL_PENDING_QUEUE": QueueCardType.ALL_PENDING_SUMMARY.value,
    "SOURCE_SYSTEM_QUEUE": QueueCardType.SOURCE_SYSTEM_REVIEW_SUMMARY.value,
    "ASSET_RESOLUTION_QUEUE": QueueCardType.ASSET_RESOLUTION_SUMMARY.value,
    "ALARM_EVENT_QUEUE": QueueCardType.ALARM_EVENT_REVIEW_SUMMARY.value,
    "FAULTCASE_QUEUE": QueueCardType.FAULTCASE_REVIEW_SUMMARY.value,
    "WORKORDER_INTENT_QUEUE": QueueCardType.WORKORDER_INTENT_REVIEW_SUMMARY.value,
    "EVIDENCE_INVESTIGATION_QUEUE": QueueCardType.EVIDENCE_INVESTIGATION_REVIEW_SUMMARY.value,
    "RELEASE_GATE_QUEUE": QueueCardType.RELEASE_GATE_SUMMARY.value,
}

QUEUE_ORDER = (
    "ALL_PENDING_QUEUE",
    "SOURCE_SYSTEM_QUEUE",
    "ASSET_RESOLUTION_QUEUE",
    "ALARM_EVENT_QUEUE",
    "FAULTCASE_QUEUE",
    "WORKORDER_INTENT_QUEUE",
    "EVIDENCE_INVESTIGATION_QUEUE",
    "RELEASE_GATE_QUEUE",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_reference(path: Path, artifact_type: str) -> dict[str, Any]:
    return build_source_artifact_reference(
        artifact_type=artifact_type,
        path=str(path.relative_to(ROOT)),
        digest=sha256_digest(_load(path)),
    )


def _primary_queue(item: Mapping[str, Any]) -> str:
    queues = [queue for queue in item.get("queueTypes", []) if queue != "ALL_PENDING_QUEUE"]
    if not queues:
        return "ALL_PENDING_QUEUE"
    return sorted(queues)[0]


def _build_rows(decisions: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in decisions.get("decisionItems", []):
        rows.append(
            build_queue_row(
                decision_item_id=str(item["decisionItemId"]),
                decision_type=str(item["decisionType"]),
                decision_scope=str(item["decisionScope"]),
                queue_type=_primary_queue(item),
                source_stage=str(item["sourceStage"]),
                source_system_key=item.get("sourceSystemKey"),
                title=str(item["title"]),
                severity=str(item["severity"]),
                priority=int(item["priority"]),
                decision_state=str(item["decisionState"]),
                decision_required=bool(item["decisionRequired"]),
                blocking=bool(item["blocking"]),
                affected_record_count=int(item["affectedRecordCount"]),
                affected_device_evidence_count=int(item["affectedDeviceEvidenceCount"]),
                allowed_decisions=list(item.get("allowedDecisions", [])),
                current_decision=str(item["currentDecision"]),
                review_reasons=list(item.get("reviewReasons", [])),
                blocking_reasons=list(item.get("blockingReasons", [])),
            )
        )
    return sort_queue_rows(rows)


def _rows_for_queue(rows: Sequence[Mapping[str, Any]], queue_type: str) -> list[Mapping[str, Any]]:
    if queue_type == "ALL_PENDING_QUEUE":
        return list(rows)
    return [row for row in rows if row["queueType"] == queue_type]


def _status(rows: Sequence[Mapping[str, Any]]) -> str:
    if not rows:
        return QueueStatus.EMPTY.value
    if any(row.get("blocking") for row in rows):
        return QueueStatus.BLOCKED.value
    if any(row.get("decisionState") == "READY_FOR_REVIEW" for row in rows):
        return QueueStatus.READY_FOR_REVIEW.value
    return QueueStatus.PENDING.value


def _severity(rows: Sequence[Mapping[str, Any]], queue_type: str) -> str:
    if queue_type == "RELEASE_GATE_QUEUE":
        return Severity.INFO.value
    order = {Severity.INFO.value: 0, Severity.LOW.value: 1, Severity.MEDIUM.value: 2, Severity.HIGH.value: 3, Severity.CRITICAL.value: 4}
    if not rows:
        return Severity.INFO.value
    return max((str(row["severity"]) for row in rows), key=lambda value: order.get(value, 0))


def _build_groups(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        build_queue_group(queue_type=queue_type, title=QUEUE_TITLES[queue_type], rows=_rows_for_queue(rows, queue_type))
        for queue_type in QUEUE_ORDER
    ]


def _build_cards(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for queue_type in QUEUE_ORDER:
        queue_rows = _rows_for_queue(rows, queue_type)
        cards.append(
            build_queue_card(
                card_type=QUEUE_CARD_TYPES[queue_type],
                title=QUEUE_TITLES[queue_type],
                severity=_severity(queue_rows, queue_type),
                status=_status(queue_rows),
                value=len(queue_rows),
                unit="DECISIONS",
                queue_type=queue_type,
                rows=queue_rows,
                decision_required=bool(queue_rows),
            )
        )
    return cards


def _summary(decisions: Mapping[str, Any], rows: Sequence[Mapping[str, Any]], groups: Sequence[Mapping[str, Any]], cards: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    source_summary = decisions["summary"]
    return {
        "decisionItemCount": source_summary["decisionItemCount"],
        "queueRowCount": len(rows),
        "queueGroupCount": len(groups),
        "queueCardCount": len(cards),
        "pendingDecisionCount": source_summary["pendingDecisionCount"],
        "blockingDecisionCount": source_summary["blockingDecisionCount"],
        "nonBlockingDecisionCount": source_summary["nonBlockingDecisionCount"],
        "sourceSystemRegistryDecisionCount": source_summary["sourceSystemRegistryDecisionCount"],
        "assetResolutionDecisionCount": source_summary["assetResolutionDecisionCount"],
        "pointResolutionDecisionCount": source_summary["pointResolutionDecisionCount"],
        "locationResolutionDecisionCount": source_summary["locationResolutionDecisionCount"],
        "alarmEventReviewDecisionCount": source_summary["alarmEventReviewDecisionCount"],
        "faultCaseReviewDecisionCount": source_summary["faultCaseReviewDecisionCount"],
        "workOrderIntentReviewDecisionCount": source_summary["workOrderIntentReviewDecisionCount"],
        "evidenceInvestigationDecisionCount": source_summary["evidenceInvestigationDecisionCount"],
        "downstreamCreationAuthorizationDecisionCount": source_summary["downstreamCreationAuthorizationDecisionCount"],
        "releaseGateDecisionCount": source_summary["releaseGateDecisionCount"],
        "affectedSourceSystemCount": source_summary["affectedSourceSystemCount"],
        "totalDeviceEvidenceCount": source_summary["totalDeviceEvidenceCount"],
        "decisionWriteCount": 0,
        "approvalWriteCount": 0,
        "canonicalWriteCount": 0,
        "databaseWriteCount": 0,
        "apiEnabled": False,
        "frontendEnabled": False,
        "runtimeActivationAllowed": False,
        "productionActivationAllowed": False,
        "pushAllowed": False,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
    }


def build_airport_uconsole_operator_review_queue_projection() -> dict[str, Any]:
    decisions = _load(DECISIONS)
    rows = _build_rows(decisions)
    groups = _build_groups(rows)
    cards = _build_cards(rows)
    projection = build_uconsole_operator_review_queue_projection(
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=_summary(decisions, rows, groups, cards),
        queue_rows=rows,
        queue_cards=cards,
        queue_groups=groups,
        filters=build_filters(rows),
        facets=build_facets(rows),
        default_page=paginate_queue_rows(rows, page_size=25),
        source_artifact_references=[_artifact_reference(DECISIONS, "OPERATOR_REVIEW_DECISIONS")],
    )
    validate_uconsole_operator_review_queue_projection(projection)
    return projection
