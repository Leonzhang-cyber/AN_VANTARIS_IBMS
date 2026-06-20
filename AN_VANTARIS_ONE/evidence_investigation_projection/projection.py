"""Projection helpers for Evidence Investigation cases."""
from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

CASE_FILTER_FIELDS = (
    "sourceSystemKey",
    "investigationState",
    "evidenceCompletenessState",
    "linkageState",
    "decisionRequired",
)


def sort_cases(cases: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [dict(case) for case in sorted(cases, key=lambda item: (str(item["sourceSystemKey"]), str(item["investigationCaseId"])))]


def build_filters(
    cases: Sequence[Mapping[str, Any]],
    evidence_links: Sequence[Mapping[str, Any]],
    timeline_items: Sequence[Mapping[str, Any]],
) -> dict[str, list[Any]]:
    filters = {field: sorted({case.get(field) for case in cases}, key=lambda value: str(value)) for field in CASE_FILTER_FIELDS}
    filters["reviewReason"] = sorted({reason for case in cases for reason in case.get("reviewReasons", [])})
    filters["blockingReason"] = sorted({reason for case in cases for reason in case.get("blockingReasons", [])})
    filters["evidenceRole"] = sorted({link.get("evidenceRole") for link in evidence_links})
    filters["linkType"] = sorted({link.get("linkType") for link in evidence_links})
    filters["timelineItemType"] = sorted({item.get("itemType") for item in timeline_items})
    return filters


def build_facets(
    cases: Sequence[Mapping[str, Any]],
    evidence_links: Sequence[Mapping[str, Any]],
    timeline_items: Sequence[Mapping[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    facets: dict[str, list[dict[str, Any]]] = {}
    for field in CASE_FILTER_FIELDS:
        counts = Counter(str(case.get(field)) for case in cases)
        facets[field] = [{"value": key, "count": counts[key]} for key in sorted(counts)]
    for field, source in (("reviewReason", "reviewReasons"), ("blockingReason", "blockingReasons")):
        counts = Counter(reason for case in cases for reason in case.get(source, []))
        facets[field] = [{"value": key, "count": counts[key]} for key in sorted(counts)]
    for field, rows, key_name in (
        ("evidenceRole", evidence_links, "evidenceRole"),
        ("linkType", evidence_links, "linkType"),
        ("timelineItemType", timeline_items, "itemType"),
    ):
        counts = Counter(str(row.get(key_name)) for row in rows)
        facets[field] = [{"value": key, "count": counts[key]} for key in sorted(counts)]
    return facets


def paginate_cases(
    cases: Sequence[Mapping[str, Any]],
    *,
    page_size: int = 25,
    continuation_token: str | None = None,
) -> dict[str, Any]:
    ordered = sort_cases(cases)
    offset = int(continuation_token or "0")
    items = ordered[offset : offset + page_size]
    next_offset = offset + len(items)
    page = {
        "pageSize": page_size,
        "continuationToken": continuation_token,
        "nextContinuationToken": str(next_offset) if next_offset < len(ordered) else None,
        "items": items,
    }
    page["deterministicDigest"] = sha256_digest(page)
    return page
