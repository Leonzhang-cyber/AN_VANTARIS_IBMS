"""Deterministic read-only projection helpers for alarm/event intake candidates."""
from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

FACET_FIELDS = (
    "sourceSystemKey",
    "eventKind",
    "eventCategory",
    "eventSeverity",
    "eventState",
    "validationState",
    "normalizationState",
    "assetResolutionState",
    "pointResolutionState",
    "locationResolutionState",
    "decisionRequired",
)

FILTER_FIELDS = FACET_FIELDS


def sort_candidates(candidates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [dict(item) for item in sorted(candidates, key=lambda row: (str(row["sourceSystemKey"]), str(row["candidateId"])))]


def build_filters(candidates: Sequence[Mapping[str, Any]]) -> dict[str, list[Any]]:
    filters: dict[str, list[Any]] = {}
    for field in FILTER_FIELDS:
        filters[field] = sorted({item.get(field) for item in candidates}, key=lambda value: str(value))
    return filters


def build_facets(candidates: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    facets: dict[str, list[dict[str, Any]]] = {}
    for field in FACET_FIELDS:
        counts = Counter(str(item.get(field)) for item in candidates)
        facets[field] = [{"value": key, "count": counts[key]} for key in sorted(counts)]
    review_counts = Counter(reason for item in candidates for reason in item.get("reviewReasons", []))
    facets["reviewReason"] = [{"value": key, "count": review_counts[key]} for key in sorted(review_counts)]
    return facets


def paginate_candidates(
    candidates: Sequence[Mapping[str, Any]],
    *,
    page_size: int = 25,
    continuation_token: str | None = None,
) -> dict[str, Any]:
    sorted_rows = sort_candidates(candidates)
    offset = int(continuation_token or "0")
    page_rows = sorted_rows[offset : offset + page_size]
    next_offset = offset + len(page_rows)
    token = str(next_offset) if next_offset < len(sorted_rows) else None
    page = {
        "pageSize": page_size,
        "continuationToken": continuation_token,
        "nextContinuationToken": token,
        "items": page_rows,
    }
    page["deterministicDigest"] = sha256_digest(page)
    return page
