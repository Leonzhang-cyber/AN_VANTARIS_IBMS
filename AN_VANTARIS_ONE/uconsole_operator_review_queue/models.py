"""Deterministic model builders for UConsole operator review queues."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def _sorted(values: Sequence[str] | None) -> list[str]:
    return sorted(str(value) for value in values or ())


def build_queue_row(
    *,
    decision_item_id: str,
    decision_type: str,
    decision_scope: str,
    queue_type: str,
    source_stage: str,
    source_system_key: str | None,
    title: str,
    severity: str,
    priority: int,
    decision_state: str,
    decision_required: bool,
    blocking: bool,
    affected_record_count: int,
    affected_device_evidence_count: int,
    allowed_decisions: Sequence[str],
    current_decision: str,
    review_reasons: Sequence[str],
    blocking_reasons: Sequence[str],
) -> dict[str, Any]:
    row = {
        "rowId": sha256_digest(
            {
                "contractVersion": CONTRACT_VERSION,
                "decisionItemId": decision_item_id,
                "queueType": queue_type,
            }
        ),
        "decisionItemId": decision_item_id,
        "decisionType": decision_type,
        "decisionScope": decision_scope,
        "queueType": queue_type,
        "sourceStage": source_stage,
        "sourceSystemKey": source_system_key,
        "title": title,
        "severity": severity,
        "priority": int(priority),
        "decisionState": decision_state,
        "decisionRequired": bool(decision_required),
        "blocking": bool(blocking),
        "affectedRecordCount": int(affected_record_count),
        "affectedDeviceEvidenceCount": int(affected_device_evidence_count),
        "allowedDecisions": _sorted(allowed_decisions),
        "currentDecision": current_decision,
        "reviewReasons": _sorted(review_reasons),
        "blockingReasons": _sorted(blocking_reasons),
    }
    row["deterministicDigest"] = sha256_digest({k: v for k, v in row.items() if k != "deterministicDigest"})
    return row


def build_queue_group(*, queue_type: str, title: str, rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    group = {
        "queueGroupId": sha256_digest(
            {
                "contractVersion": CONTRACT_VERSION,
                "queueType": queue_type,
                "rowIds": sorted(str(row["rowId"]) for row in rows),
            }
        ),
        "queueType": queue_type,
        "title": title,
        "rowIds": sorted(str(row["rowId"]) for row in rows),
        "openDecisionCount": sum(1 for row in rows if row.get("decisionRequired")),
        "blockingDecisionCount": sum(1 for row in rows if row.get("blocking")),
        "affectedSourceSystemKeys": sorted({str(row["sourceSystemKey"]) for row in rows if row.get("sourceSystemKey")}),
        "affectedDeviceEvidenceCount": sum(int(row.get("affectedDeviceEvidenceCount", 0)) for row in rows),
    }
    group["deterministicDigest"] = sha256_digest({k: v for k, v in group.items() if k != "deterministicDigest"})
    return group


def build_queue_card(
    *,
    card_type: str,
    title: str,
    severity: str,
    status: str,
    value: int,
    unit: str,
    queue_type: str,
    rows: Sequence[Mapping[str, Any]],
    decision_required: bool,
) -> dict[str, Any]:
    card = {
        "cardId": sha256_digest(
            {
                "contractVersion": CONTRACT_VERSION,
                "cardType": card_type,
                "queueType": queue_type,
                "rowIds": sorted(str(row["rowId"]) for row in rows),
            }
        ),
        "cardType": card_type,
        "title": title,
        "severity": severity,
        "status": status,
        "value": int(value),
        "unit": unit,
        "queueType": queue_type,
        "affectedSourceSystemKeys": sorted({str(row["sourceSystemKey"]) for row in rows if row.get("sourceSystemKey")}),
        "affectedDecisionCount": len(rows),
        "blockingDecisionCount": sum(1 for row in rows if row.get("blocking")),
        "decisionRequired": bool(decision_required),
    }
    card["deterministicDigest"] = sha256_digest({k: v for k, v in card.items() if k != "deterministicDigest"})
    return card


def build_source_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    ref = {"artifactType": artifact_type, "path": path, "digest": digest}
    ref["deterministicDigest"] = sha256_digest(ref)
    return ref


def build_uconsole_operator_review_queue_projection(
    *,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    queue_rows: Sequence[Mapping[str, Any]],
    queue_cards: Sequence[Mapping[str, Any]],
    queue_groups: Sequence[Mapping[str, Any]],
    filters: Mapping[str, Any],
    facets: Mapping[str, Any],
    default_page: Mapping[str, Any],
    source_artifact_references: Sequence[Mapping[str, Any]],
    generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
) -> dict[str, Any]:
    projection = {
        "projectionId": sha256_digest(
            {
                "contractVersion": CONTRACT_VERSION,
                "authority": authority,
                "profileId": profile_id,
                "rowDigests": [row.get("deterministicDigest") for row in queue_rows],
                "cardDigests": [card.get("deterministicDigest") for card in queue_cards],
            }
        ),
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "queueRows": list(queue_rows),
        "queueCards": list(queue_cards),
        "queueGroups": list(queue_groups),
        "filters": dict(filters),
        "facets": dict(facets),
        "defaultPage": dict(default_page),
        "sourceArtifactReferences": list(source_artifact_references),
        "generatedAtPolicy": generated_at_policy,
    }
    projection["deterministicDigest"] = sha256_digest(
        {k: v for k, v in projection.items() if k != "deterministicDigest"}
    )
    return projection
