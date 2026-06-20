"""Airport Operator Review Decision Layer Projection."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from operator_review_decision.aggregation import build_decision_groups_and_queues
from operator_review_decision.enums import DecisionScope, DecisionState, DecisionType, QueueType, Severity
from operator_review_decision.models import (
    build_decision_item,
    build_operator_review_decision_projection,
    build_source_artifact_reference,
)
from operator_review_decision.projection import build_facets, build_filters, paginate_decision_items, sort_decision_items
from operator_review_decision.validation import validate_operator_review_decision_projection
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A4-01"
PROFILE_ID = "airport-operator-review-decision-profile-v1"
IMPLEMENTATION_STATUS = "OPERATOR_REVIEW_DECISION_LAYER_FOUNDATION_COMPLETE"
READINESS_OUTCOME = "OPERATOR_REVIEW_DECISION_QUEUE_COMPLETE_PENDING_OPERATOR_ACTION"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"

SOURCE_REVIEW = PROJECTIONS_DIR / "airport-source-system-review.v1.json"
A3_RELEASE_GATE = PROJECTIONS_DIR / "airport-a3-readiness-release-gate.v1.json"
RESOLUTION = PROJECTIONS_DIR / "airport-alarm-event-asset-resolution-review.v1.json"
INTAKE = PROJECTIONS_DIR / "airport-alarm-event-intake-candidates.v1.json"
FAULTCASE = PROJECTIONS_DIR / "airport-faultcase-candidates.v1.json"
WORKORDER = PROJECTIONS_DIR / "airport-workorder-intent-candidates.v1.json"
INVESTIGATION = PROJECTIONS_DIR / "airport-evidence-investigation.v1.json"
OPERATIONS = PROJECTIONS_DIR / "airport-uconsole-alarm-event-operations.v1.json"
INTEGRATION_HEALTH = PROJECTIONS_DIR / "airport-integration-health.v1.json"
EVIDENCE_ADAPTER = PROJECTIONS_DIR / "airport-evidence-adapter-contract.v1.json"
UCONSOLE_HEALTH = PROJECTIONS_DIR / "airport-uconsole-integration-health.v1.json"

SOURCE_REVIEW_DECISION = {
    "REGISTRY_APPROVAL_REQUIRED": DecisionType.REGISTRY_APPROVAL.value,
    "ALIAS_APPROVAL_REQUIRED": DecisionType.ALIAS_APPROVAL.value,
    "NAMESPACE_INTERPRETATION_REQUIRED": DecisionType.NAMESPACE_INTERPRETATION.value,
}

SOURCE_REVIEW_TITLE = {
    DecisionType.REGISTRY_APPROVAL.value: "Registry approval required",
    DecisionType.ALIAS_APPROVAL.value: "Alias approval required",
    DecisionType.NAMESPACE_INTERPRETATION.value: "Namespace interpretation required",
}

READ_ONLY_ALLOWED_DECISIONS = ("APPROVE", "REJECT", "DEFER", "REQUEST_MORE_CONTEXT", "KEEP_PENDING")
PROPOSAL_ALLOWED_DECISIONS = ("ACCEPT_PROPOSAL", "REJECT_PROPOSAL", "DEFER", "REQUEST_MORE_CONTEXT", "KEEP_PENDING")


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


def _references() -> list[dict[str, Any]]:
    paths = [
        (SOURCE_REVIEW, "SOURCE_SYSTEM_REVIEW"),
        (A3_RELEASE_GATE, "A3_READINESS_RELEASE_GATE"),
        (INTEGRATION_HEALTH, "INTEGRATION_HEALTH"),
        (EVIDENCE_ADAPTER, "EVIDENCE_ADAPTER_CONTRACT"),
        (UCONSOLE_HEALTH, "UCONSOLE_INTEGRATION_HEALTH"),
        (INTAKE, "ALARM_EVENT_INTAKE_CANDIDATES"),
        (RESOLUTION, "ALARM_EVENT_ASSET_RESOLUTION_REVIEW"),
        (FAULTCASE, "UFMS_FAULTCASE_CANDIDATES"),
        (WORKORDER, "WORKORDER_INTENT_CANDIDATES"),
        (INVESTIGATION, "EVIDENCE_INVESTIGATION"),
        (OPERATIONS, "UCONSOLE_ALARM_EVENT_OPERATIONS"),
    ]
    return sorted((_artifact_reference(path, kind) for path, kind in paths), key=lambda ref: ref["artifactType"])


def _add_queue(item: dict[str, Any], *queue_types: str) -> dict[str, Any]:
    item["queueTypes"] = sorted(queue_types)
    item["deterministicDigest"] = sha256_digest({k: v for k, v in item.items() if k != "deterministicDigest"})
    return item


def _source_system_decisions(source_review: Mapping[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for binding in sorted(source_review.get("evidenceBindings", []), key=lambda row: row["sourceSystemKey"]):
        reasons = list(binding.get("reviewReasons", []))
        decision_type = next(SOURCE_REVIEW_DECISION[reason] for reason in reasons if reason in SOURCE_REVIEW_DECISION)
        source_key = str(binding["sourceSystemKey"])
        item = build_decision_item(
            decision_type=decision_type,
            decision_scope=DecisionScope.SOURCE_SYSTEM_REVIEW.value,
            source_stage="A2",
            source_artifact_type="SOURCE_SYSTEM_REVIEW_BINDING",
            source_artifact_id=str(binding["bindingDigest"]),
            source_system_key=source_key,
            title=f"{source_key} {SOURCE_REVIEW_TITLE[decision_type]}",
            description=f"Operator review is required before {source_key} source-system evidence can be accepted as approved registry context.",
            severity=Severity.HIGH.value,
            priority=10,
            decision_state=DecisionState.PENDING.value,
            allowed_decisions=READ_ONLY_ALLOWED_DECISIONS,
            current_decision="KEEP_PENDING",
            decision_required=True,
            blocking=True,
            affected_record_count=int(binding.get("sourceRecordCount", 1)),
            affected_device_evidence_count=int(binding.get("deviceEvidenceCount", 0)),
            evidence_references=list(binding.get("evidenceReferences", [])),
            review_reasons=reasons,
            blocking_reasons=["SOURCE_SYSTEM_REVIEW_REQUIRED", decision_type],
        )
        items.append(_add_queue(item, QueueType.SOURCE_SYSTEM_QUEUE.value))
    return items


def _resolution_decisions(resolution: Mapping[str, Any]) -> list[dict[str, Any]]:
    specs = (
        (DecisionType.ASSET_RESOLUTION.value, "Asset resolution required", "ASSET_RESOLUTION_REQUIRED"),
        (DecisionType.POINT_RESOLUTION.value, "Point resolution required", "POINT_RESOLUTION_REQUIRED"),
        (DecisionType.LOCATION_RESOLUTION.value, "Location resolution required", "LOCATION_RESOLUTION_REQUIRED"),
    )
    items: list[dict[str, Any]] = []
    for row in sorted(resolution.get("resolutionRows", []), key=lambda item: item["sourceSystemKey"]):
        source_key = str(row["sourceSystemKey"])
        for decision_type, title, reason in specs:
            item = build_decision_item(
                decision_type=decision_type,
                decision_scope=DecisionScope.ASSET_REVIEW.value,
                source_stage="A3-02",
                source_artifact_type="ALARM_EVENT_ASSET_RESOLUTION_ROW",
                source_artifact_id=f"{row['rowId']}:{decision_type}",
                source_system_key=source_key,
                title=f"{source_key} {title}",
                description=f"Operator review is required for {source_key} before downstream alarm/event decisions can progress.",
                severity=str(row.get("eventSeverity", Severity.MEDIUM.value)),
                priority=20,
                decision_state=DecisionState.PENDING.value,
                allowed_decisions=PROPOSAL_ALLOWED_DECISIONS,
                current_decision="KEEP_PENDING",
                decision_required=True,
                blocking=True,
                affected_record_count=1,
                affected_device_evidence_count=int(row.get("deviceEvidenceCount", 0)),
                evidence_references=list(row.get("evidenceReferences", [])),
                review_reasons=[reason],
                blocking_reasons=[reason, "BLOCKS_DOWNSTREAM_CREATION"],
            )
            items.append(_add_queue(item, QueueType.ASSET_RESOLUTION_QUEUE.value))
    return items


def _per_source_decisions(
    *,
    rows: Sequence[Mapping[str, Any]],
    source_stage: str,
    source_artifact_type: str,
    source_id_field: str,
    decision_type: str,
    decision_scope: str,
    title_suffix: str,
    review_reason: str,
    queue_type: str,
    priority: int,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: item["sourceSystemKey"]):
        source_key = str(row["sourceSystemKey"])
        item = build_decision_item(
            decision_type=decision_type,
            decision_scope=decision_scope,
            source_stage=source_stage,
            source_artifact_type=source_artifact_type,
            source_artifact_id=str(row[source_id_field]),
            source_system_key=source_key,
            title=f"{source_key} {title_suffix}",
            description=f"Operator review is required for the {source_artifact_type} candidate associated with {source_key}.",
            severity=str(row.get("eventSeverity", row.get("operationalSeverity", Severity.HIGH.value))),
            priority=priority,
            decision_state=DecisionState.PENDING.value,
            allowed_decisions=PROPOSAL_ALLOWED_DECISIONS,
            current_decision="KEEP_PENDING",
            decision_required=True,
            blocking=True,
            affected_record_count=1,
            affected_device_evidence_count=int(row.get("deviceEvidenceCount", 0)),
            evidence_references=list(row.get("evidenceReferences", [])),
            review_reasons=[review_reason],
            blocking_reasons=list(row.get("blockingReasons", [])) or [review_reason],
        )
        items.append(_add_queue(item, queue_type))
    return items


def _downstream_authorization_decisions(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: item["sourceSystemKey"]):
        source_key = str(row["sourceSystemKey"])
        item = build_decision_item(
            decision_type=DecisionType.DOWNSTREAM_CREATION_AUTHORIZATION.value,
            decision_scope=DecisionScope.ALARM_EVENT_REVIEW.value,
            source_stage="A3-02",
            source_artifact_type="ALARM_EVENT_ASSET_RESOLUTION_ROW",
            source_artifact_id=f"{row['rowId']}:DOWNSTREAM_CREATION_AUTHORIZATION",
            source_system_key=source_key,
            title=f"{source_key} downstream creation authorization",
            description=f"Operator authorization is required before any downstream candidate creation is applied for {source_key}.",
            severity=str(row.get("eventSeverity", Severity.HIGH.value)),
            priority=70,
            decision_state=DecisionState.PENDING.value,
            allowed_decisions=READ_ONLY_ALLOWED_DECISIONS,
            current_decision="KEEP_PENDING",
            decision_required=True,
            blocking=True,
            affected_record_count=1,
            affected_device_evidence_count=int(row.get("deviceEvidenceCount", 0)),
            evidence_references=list(row.get("evidenceReferences", [])),
            review_reasons=["DOWNSTREAM_CREATION_NOT_AUTHORIZED"],
            blocking_reasons=["DOWNSTREAM_CREATION_NOT_AUTHORIZED"],
        )
        items.append(_add_queue(item, QueueType.ALARM_EVENT_QUEUE.value))
    return items


def _release_gate_decision(release_gate: Mapping[str, Any]) -> dict[str, Any]:
    decision = release_gate["releaseDecision"]
    item = build_decision_item(
        decision_type=DecisionType.RELEASE_GATE_REVIEW.value,
        decision_scope=DecisionScope.RELEASE_GATE.value,
        source_stage="A3-07",
        source_artifact_type="A3_READINESS_RELEASE_GATE",
        source_artifact_id=str(release_gate["releaseGateId"]),
        source_system_key=None,
        title="A3 read-only release gate review",
        description="A3 local read-only release gate passed; push remains disabled pending explicit operator/user instruction.",
        severity=Severity.INFO.value,
        priority=90,
        decision_state=DecisionState.READY_FOR_REVIEW.value,
        allowed_decisions=("DEFER", "REQUEST_MORE_CONTEXT", "KEEP_PENDING"),
        current_decision="KEEP_PENDING",
        decision_required=True,
        blocking=False,
        affected_record_count=1,
        affected_device_evidence_count=0,
        evidence_references=[str(decision.get("deterministicDigest"))],
        review_reasons=["RELEASE_GATE_PASS_PUSH_DISABLED"],
        blocking_reasons=[],
    )
    return _add_queue(item, QueueType.RELEASE_GATE_QUEUE.value)


def _build_items() -> list[dict[str, Any]]:
    source_review = _load(SOURCE_REVIEW)
    resolution = _load(RESOLUTION)
    intake = _load(INTAKE)
    faultcase = _load(FAULTCASE)
    workorder = _load(WORKORDER)
    investigation = _load(INVESTIGATION)
    release_gate = _load(A3_RELEASE_GATE)
    items: list[dict[str, Any]] = []
    items.extend(_source_system_decisions(source_review))
    items.extend(_resolution_decisions(resolution))
    items.extend(
        _per_source_decisions(
            rows=list(intake["candidates"]),
            source_stage="A3-01",
            source_artifact_type="ALARM_EVENT_CANDIDATE",
            source_id_field="candidateId",
            decision_type=DecisionType.ALARM_EVENT_REVIEW.value,
            decision_scope=DecisionScope.ALARM_EVENT_REVIEW.value,
            title_suffix="alarm/event review",
            review_reason="ALARM_EVENT_REVIEW_REQUIRED",
            queue_type=QueueType.ALARM_EVENT_QUEUE.value,
            priority=30,
        )
    )
    items.extend(
        _per_source_decisions(
            rows=list(faultcase["faultCaseCandidates"]),
            source_stage="A3-03",
            source_artifact_type="FAULTCASE_CANDIDATE",
            source_id_field="candidateId",
            decision_type=DecisionType.FAULTCASE_CANDIDATE_REVIEW.value,
            decision_scope=DecisionScope.FAULTCASE_REVIEW.value,
            title_suffix="FaultCase candidate review",
            review_reason="FAULTCASE_REVIEW_REQUIRED",
            queue_type=QueueType.FAULTCASE_QUEUE.value,
            priority=40,
        )
    )
    items.extend(
        _per_source_decisions(
            rows=list(workorder["workOrderIntentCandidates"]),
            source_stage="A3-04",
            source_artifact_type="WORKORDER_INTENT_CANDIDATE",
            source_id_field="candidateId",
            decision_type=DecisionType.WORKORDER_INTENT_REVIEW.value,
            decision_scope=DecisionScope.WORKORDER_REVIEW.value,
            title_suffix="WorkOrderIntent review",
            review_reason="WORKORDER_INTENT_REVIEW_REQUIRED",
            queue_type=QueueType.WORKORDER_INTENT_QUEUE.value,
            priority=50,
        )
    )
    items.extend(
        _per_source_decisions(
            rows=list(investigation["investigationCases"]),
            source_stage="A3-05",
            source_artifact_type="EVIDENCE_INVESTIGATION_CASE",
            source_id_field="investigationCaseId",
            decision_type=DecisionType.EVIDENCE_INVESTIGATION_REVIEW.value,
            decision_scope=DecisionScope.EVIDENCE_REVIEW.value,
            title_suffix="evidence investigation review",
            review_reason="EVIDENCE_INVESTIGATION_REVIEW_REQUIRED",
            queue_type=QueueType.EVIDENCE_INVESTIGATION_QUEUE.value,
            priority=60,
        )
    )
    items.extend(_downstream_authorization_decisions(list(resolution["resolutionRows"])))
    items.append(_release_gate_decision(release_gate))
    return sort_decision_items(items)


def _summary(items: Sequence[Mapping[str, Any]], groups: Sequence[Mapping[str, Any]], queues: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    source_keys = {item.get("sourceSystemKey") for item in items if item.get("sourceSystemKey")}
    count_type = lambda value: sum(1 for item in items if item["decisionType"] == value)
    return {
        "decisionItemCount": len(items),
        "decisionGroupCount": len(groups),
        "decisionQueueCount": len(queues),
        "pendingDecisionCount": sum(1 for item in items if item["decisionRequired"]),
        "blockingDecisionCount": sum(1 for item in items if item["blocking"]),
        "nonBlockingDecisionCount": sum(1 for item in items if not item["blocking"]),
        "sourceSystemRegistryDecisionCount": count_type(DecisionType.REGISTRY_APPROVAL.value)
        + count_type(DecisionType.ALIAS_APPROVAL.value)
        + count_type(DecisionType.NAMESPACE_INTERPRETATION.value),
        "assetResolutionDecisionCount": count_type(DecisionType.ASSET_RESOLUTION.value),
        "pointResolutionDecisionCount": count_type(DecisionType.POINT_RESOLUTION.value),
        "locationResolutionDecisionCount": count_type(DecisionType.LOCATION_RESOLUTION.value),
        "alarmEventReviewDecisionCount": count_type(DecisionType.ALARM_EVENT_REVIEW.value),
        "faultCaseReviewDecisionCount": count_type(DecisionType.FAULTCASE_CANDIDATE_REVIEW.value),
        "workOrderIntentReviewDecisionCount": count_type(DecisionType.WORKORDER_INTENT_REVIEW.value),
        "evidenceInvestigationDecisionCount": count_type(DecisionType.EVIDENCE_INVESTIGATION_REVIEW.value),
        "downstreamCreationAuthorizationDecisionCount": count_type(DecisionType.DOWNSTREAM_CREATION_AUTHORIZATION.value),
        "releaseGateDecisionCount": count_type(DecisionType.RELEASE_GATE_REVIEW.value),
        "affectedSourceSystemCount": len(source_keys),
        "totalDeviceEvidenceCount": 470,
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


def build_airport_operator_review_decision_projection() -> dict[str, Any]:
    items = _build_items()
    groups, queues = build_decision_groups_and_queues(items)
    projection = build_operator_review_decision_projection(
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=_summary(items, groups, queues),
        decision_items=items,
        decision_groups=groups,
        decision_queues=queues,
        filters=build_filters(items, queues),
        facets=build_facets(items, queues),
        default_page=paginate_decision_items(items, page_size=25),
        source_artifact_references=_references(),
    )
    validate_operator_review_decision_projection(projection)
    return projection
