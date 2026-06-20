"""Projection helpers for deterministic alarm/event resolution rows."""
from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

FILTER_FIELDS = (
    "sourceSystemKey",
    "eventKind",
    "eventCategory",
    "eventSeverity",
    "assetResolutionState",
    "pointResolutionState",
    "locationResolutionState",
    "sourceSystemReviewState",
    "downstreamCreationState",
    "decisionRequired",
)


def sort_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [dict(row) for row in sorted(rows, key=lambda row: (str(row["sourceSystemKey"]), str(row["rowId"])))]


def build_filters(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[Any]]:
    filters = {field: sorted({row.get(field) for row in rows}, key=lambda value: str(value)) for field in FILTER_FIELDS}
    filters["reviewReason"] = sorted({reason for row in rows for reason in row.get("reviewReasons", [])})
    return filters


def build_facets(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    facets: dict[str, list[dict[str, Any]]] = {}
    for field in FILTER_FIELDS:
        counts = Counter(str(row.get(field)) for row in rows)
        facets[field] = [{"value": key, "count": counts[key]} for key in sorted(counts)]
    review_counts = Counter(reason for row in rows for reason in row.get("reviewReasons", []))
    facets["reviewReason"] = [{"value": key, "count": review_counts[key]} for key in sorted(review_counts)]
    return facets


def paginate_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    page_size: int = 25,
    continuation_token: str | None = None,
) -> dict[str, Any]:
    ordered = sort_rows(rows)
    offset = int(continuation_token or "0")
    page_rows = ordered[offset : offset + page_size]
    next_offset = offset + len(page_rows)
    page = {
        "pageSize": page_size,
        "continuationToken": continuation_token,
        "nextContinuationToken": str(next_offset) if next_offset < len(ordered) else None,
        "items": page_rows,
    }
    page["deterministicDigest"] = sha256_digest(page)
    return page
