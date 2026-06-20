"""Projection helpers for UConsole operator review queues."""
from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

FILTER_FIELDS = (
    "decisionType",
    "decisionScope",
    "queueType",
    "sourceStage",
    "sourceSystemKey",
    "severity",
    "priority",
    "decisionState",
    "blocking",
    "decisionRequired",
)


def sort_queue_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return sorted((dict(row) for row in rows), key=lambda row: (row["queueType"], row["decisionType"], row.get("sourceSystemKey") or "", row["rowId"]))


def build_filters(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    filters: dict[str, Any] = {}
    for field in FILTER_FIELDS:
        filters[field] = {"field": field, "options": sorted({row.get(field) for row in rows if row.get(field) is not None})}
    filters["reviewReason"] = {"field": "reviewReason", "options": sorted({reason for row in rows for reason in row.get("reviewReasons", [])})}
    filters["blockingReason"] = {"field": "blockingReason", "options": sorted({reason for row in rows for reason in row.get("blockingReasons", [])})}
    return filters


def build_facets(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    facets: dict[str, Any] = {}
    for field in FILTER_FIELDS:
        counts = Counter(row.get(field) for row in rows if row.get(field) is not None)
        facets[field] = {str(key): counts[key] for key in sorted(counts, key=lambda value: str(value))}
    review_counts = Counter(reason for row in rows for reason in row.get("reviewReasons", []))
    facets["reviewReason"] = {str(key): review_counts[key] for key in sorted(review_counts)}
    blocking_counts = Counter(reason for row in rows for reason in row.get("blockingReasons", []))
    facets["blockingReason"] = {str(key): blocking_counts[key] for key in sorted(blocking_counts)}
    return facets


def paginate_queue_rows(rows: Sequence[Mapping[str, Any]], *, page_size: int = 25) -> dict[str, Any]:
    ordered = sort_queue_rows(rows)
    page = ordered[:page_size]
    token = sha256_digest({"pageSize": page_size, "returnedIds": [row["rowId"] for row in page]})
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
