"""Projection helpers for operator review decisions."""
from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

FILTER_FIELDS = (
    "decisionType",
    "decisionScope",
    "sourceStage",
    "sourceSystemKey",
    "severity",
    "priority",
    "decisionState",
    "blocking",
    "decisionRequired",
)


def sort_decision_items(items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return sorted((dict(item) for item in items), key=lambda item: (item["decisionType"], item.get("sourceSystemKey") or "", item["decisionItemId"]))


def build_filters(items: Sequence[Mapping[str, Any]], queues: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    filters: dict[str, Any] = {}
    for field in FILTER_FIELDS:
        values = sorted({item.get(field) for item in items if item.get(field) is not None})
        filters[field] = {"field": field, "options": values}
    filters["queueType"] = {"field": "queueType", "options": sorted({queue["queueType"] for queue in queues})}
    filters["reviewReason"] = {"field": "reviewReason", "options": sorted({reason for item in items for reason in item.get("reviewReasons", [])})}
    filters["blockingReason"] = {"field": "blockingReason", "options": sorted({reason for item in items for reason in item.get("blockingReasons", [])})}
    return filters


def build_facets(items: Sequence[Mapping[str, Any]], queues: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    facets: dict[str, Any] = {}
    for field in FILTER_FIELDS:
        counts = Counter(item.get(field) for item in items if item.get(field) is not None)
        facets[field] = {str(key): counts[key] for key in sorted(counts, key=lambda value: str(value))}
    queue_counts = Counter(queue["queueType"] for queue in queues)
    facets["queueType"] = {str(key): queue_counts[key] for key in sorted(queue_counts)}
    reason_counts = Counter(reason for item in items for reason in item.get("reviewReasons", []))
    facets["reviewReason"] = {str(key): reason_counts[key] for key in sorted(reason_counts)}
    blocking_counts = Counter(reason for item in items for reason in item.get("blockingReasons", []))
    facets["blockingReason"] = {str(key): blocking_counts[key] for key in sorted(blocking_counts)}
    return facets


def paginate_decision_items(items: Sequence[Mapping[str, Any]], *, page_size: int = 25) -> dict[str, Any]:
    ordered = sort_decision_items(items)
    page = ordered[:page_size]
    token = sha256_digest({"pageSize": page_size, "returnedIds": [item["decisionItemId"] for item in page]})
    next_token = None
    if len(ordered) > page_size:
        next_token = sha256_digest({"nextOffset": page_size, "totalCount": len(ordered)})
    return {
        "pageSize": page_size,
        "items": page,
        "continuationToken": token,
        "nextContinuationToken": next_token,
        "totalCount": len(ordered),
        "returnedCount": len(page),
        "deterministicDigest": sha256_digest({"token": token, "next": next_token, "count": len(page)}),
    }
