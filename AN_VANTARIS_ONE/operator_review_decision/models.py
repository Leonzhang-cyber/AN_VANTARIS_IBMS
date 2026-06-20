"""Deterministic model builders for operator review decisions."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def _sorted(values: Sequence[str] | None) -> list[str]:
    return sorted(str(value) for value in values or ())


def build_decision_item(
    *,
    decision_type: str,
    decision_scope: str,
    source_stage: str,
    source_artifact_type: str,
    source_artifact_id: str,
    source_system_key: str | None,
    title: str,
    description: str,
    severity: str,
    priority: int,
    decision_state: str,
    allowed_decisions: Sequence[str],
    current_decision: str,
    decision_required: bool,
    blocking: bool,
    affected_record_count: int,
    affected_device_evidence_count: int,
    evidence_references: Sequence[str],
    review_reasons: Sequence[str],
    blocking_reasons: Sequence[str],
) -> dict[str, Any]:
    item = {
        "decisionItemId": sha256_digest(
            {
                "contractVersion": CONTRACT_VERSION,
                "decisionType": decision_type,
                "sourceStage": source_stage,
                "sourceArtifactType": source_artifact_type,
                "sourceArtifactId": source_artifact_id,
                "sourceSystemKey": source_system_key or "GLOBAL",
            }
        ),
        "decisionType": decision_type,
        "decisionScope": decision_scope,
        "sourceStage": source_stage,
        "sourceArtifactType": source_artifact_type,
        "sourceArtifactId": source_artifact_id,
        "sourceSystemKey": source_system_key,
        "title": title,
        "description": description,
        "severity": severity,
        "priority": int(priority),
        "decisionState": decision_state,
        "allowedDecisions": _sorted(allowed_decisions),
        "currentDecision": current_decision,
        "decisionRequired": bool(decision_required),
        "blocking": bool(blocking),
        "affectedRecordCount": int(affected_record_count),
        "affectedDeviceEvidenceCount": int(affected_device_evidence_count),
        "evidenceReferences": _sorted(evidence_references),
        "reviewReasons": _sorted(review_reasons),
        "blockingReasons": _sorted(blocking_reasons),
    }
    item["deterministicDigest"] = sha256_digest({k: v for k, v in item.items() if k != "deterministicDigest"})
    return item


def build_decision_group(
    *,
    group_type: str,
    title: str,
    decision_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    group = {
        "decisionGroupId": sha256_digest(
            {
                "contractVersion": CONTRACT_VERSION,
                "groupType": group_type,
                "decisionItemIds": sorted(str(item["decisionItemId"]) for item in decision_items),
            }
        ),
        "groupType": group_type,
        "title": title,
        "decisionItemIds": sorted(str(item["decisionItemId"]) for item in decision_items),
        "affectedSourceSystemKeys": sorted(
            {str(item["sourceSystemKey"]) for item in decision_items if item.get("sourceSystemKey")}
        ),
        "decisionRequiredCount": sum(1 for item in decision_items if item.get("decisionRequired")),
        "blockingDecisionCount": sum(1 for item in decision_items if item.get("blocking")),
        "affectedDeviceEvidenceCount": sum(int(item.get("affectedDeviceEvidenceCount", 0)) for item in decision_items),
    }
    group["deterministicDigest"] = sha256_digest({k: v for k, v in group.items() if k != "deterministicDigest"})
    return group


def build_decision_queue(
    *,
    queue_type: str,
    title: str,
    decision_items: Sequence[Mapping[str, Any]],
    severity: str,
) -> dict[str, Any]:
    queue = {
        "queueId": sha256_digest(
            {
                "contractVersion": CONTRACT_VERSION,
                "queueType": queue_type,
                "decisionItemIds": sorted(str(item["decisionItemId"]) for item in decision_items),
            }
        ),
        "queueType": queue_type,
        "title": title,
        "decisionItemIds": sorted(str(item["decisionItemId"]) for item in decision_items),
        "openDecisionCount": sum(1 for item in decision_items if item.get("decisionRequired")),
        "blockingDecisionCount": sum(1 for item in decision_items if item.get("blocking")),
        "severity": severity,
    }
    queue["deterministicDigest"] = sha256_digest({k: v for k, v in queue.items() if k != "deterministicDigest"})
    return queue


def build_source_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    ref = {"artifactType": artifact_type, "path": path, "digest": digest}
    ref["deterministicDigest"] = sha256_digest(ref)
    return ref


def build_operator_review_decision_projection(
    *,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    decision_items: Sequence[Mapping[str, Any]],
    decision_groups: Sequence[Mapping[str, Any]],
    decision_queues: Sequence[Mapping[str, Any]],
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
                "itemDigests": [item.get("deterministicDigest") for item in decision_items],
                "queueDigests": [queue.get("deterministicDigest") for queue in decision_queues],
            }
        ),
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "decisionItems": list(decision_items),
        "decisionGroups": list(decision_groups),
        "decisionQueues": list(decision_queues),
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
