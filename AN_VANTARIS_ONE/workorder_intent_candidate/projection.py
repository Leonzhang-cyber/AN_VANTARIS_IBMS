"""Projection helpers for deterministic WorkOrderIntent candidates."""
from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

FILTER_FIELDS = (
    "sourceSystemKey",
    "proposedWorkOrderIntentType",
    "proposedMaintenanceType",
    "proposedPriority",
    "proposedTradeDiscipline",
    "proposedExecutionOwner",
    "proposedSlaClass",
    "eligibilityState",
    "downstreamCreationState",
    "decisionRequired",
)


def sort_candidates(candidates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        dict(candidate)
        for candidate in sorted(candidates, key=lambda item: (str(item["sourceSystemKey"]), str(item["candidateId"])))
    ]


def build_filters(candidates: Sequence[Mapping[str, Any]]) -> dict[str, list[Any]]:
    filters = {
        field: sorted({candidate.get(field) for candidate in candidates}, key=lambda value: str(value))
        for field in FILTER_FIELDS
    }
    filters["reviewReason"] = sorted({reason for candidate in candidates for reason in candidate.get("reviewReasons", [])})
    filters["blockingReason"] = sorted(
        {reason for candidate in candidates for reason in candidate.get("blockingReasons", [])}
    )
    return filters


def build_facets(candidates: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    facets: dict[str, list[dict[str, Any]]] = {}
    for field in FILTER_FIELDS:
        counts = Counter(str(candidate.get(field)) for candidate in candidates)
        facets[field] = [{"value": key, "count": counts[key]} for key in sorted(counts)]
    for field, source in (("reviewReason", "reviewReasons"), ("blockingReason", "blockingReasons")):
        counts = Counter(reason for candidate in candidates for reason in candidate.get(source, []))
        facets[field] = [{"value": key, "count": counts[key]} for key in sorted(counts)]
    return facets


def paginate_candidates(
    candidates: Sequence[Mapping[str, Any]],
    *,
    page_size: int = 25,
    continuation_token: str | None = None,
) -> dict[str, Any]:
    ordered = sort_candidates(candidates)
    offset = int(continuation_token or "0")
    page_items = ordered[offset : offset + page_size]
    next_offset = offset + len(page_items)
    page = {
        "pageSize": page_size,
        "continuationToken": continuation_token,
        "nextContinuationToken": str(next_offset) if next_offset < len(ordered) else None,
        "items": page_items,
    }
    page["deterministicDigest"] = sha256_digest(page)
    return page
