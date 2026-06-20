"""Aggregation helpers for operator review decisions."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .enums import QueueType, Severity
from .models import build_decision_group, build_decision_queue


QUEUE_GROUPS = (
    (QueueType.ALL_PENDING_QUEUE.value, "All pending decisions"),
    (QueueType.SOURCE_SYSTEM_QUEUE.value, "Source-system decisions"),
    (QueueType.ASSET_RESOLUTION_QUEUE.value, "Asset, point and location resolution decisions"),
    (QueueType.ALARM_EVENT_QUEUE.value, "Alarm/Event review decisions"),
    (QueueType.FAULTCASE_QUEUE.value, "FaultCase candidate decisions"),
    (QueueType.WORKORDER_INTENT_QUEUE.value, "WorkOrderIntent decisions"),
    (QueueType.EVIDENCE_INVESTIGATION_QUEUE.value, "Evidence investigation decisions"),
    (QueueType.RELEASE_GATE_QUEUE.value, "Release gate decisions"),
)


def items_for_queue(items: Sequence[Mapping[str, Any]], queue_type: str) -> list[Mapping[str, Any]]:
    if queue_type == QueueType.ALL_PENDING_QUEUE.value:
        return list(items)
    return [item for item in items if queue_type in item.get("queueTypes", [])]


def build_decision_groups_and_queues(items: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups: list[dict[str, Any]] = []
    queues: list[dict[str, Any]] = []
    for queue_type, title in QUEUE_GROUPS:
        queue_items = items_for_queue(items, queue_type)
        groups.append(build_decision_group(group_type=queue_type, title=title, decision_items=queue_items))
        severity = Severity.INFO.value if queue_type == QueueType.RELEASE_GATE_QUEUE.value else Severity.HIGH.value
        queues.append(build_decision_queue(queue_type=queue_type, title=title, decision_items=queue_items, severity=severity))
    return groups, queues
