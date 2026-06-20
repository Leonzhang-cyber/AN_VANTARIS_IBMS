"""Deterministic UConsole projection helpers."""
from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import FACET_KEYS, FILTER_KEYS

PAGE_SIZE_OPTIONS = (25, 50, 100)
MAX_PAGE_SIZE = 200
DEFAULT_PAGE_SIZE = 25


def sort_source_system_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [dict(item) for item in rows],
        key=lambda item: (str(item.get("sourceSystemKey", "")), str(item.get("rowId", ""))),
    )


def sort_dashboard_cards(cards: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [dict(item) for item in cards],
        key=lambda item: (str(item.get("cardType", "")), str(item.get("cardId", ""))),
    )


def paginate_source_system_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    page_size: int = DEFAULT_PAGE_SIZE,
    continuation_token: str | None = None,
    projection_state_digest: str | None = None,
) -> dict[str, Any]:
    size = min(max(int(page_size), 1), MAX_PAGE_SIZE)
    if size not in PAGE_SIZE_OPTIONS:
        size = min(PAGE_SIZE_OPTIONS, key=lambda value: abs(value - size))

    offset = 0
    if continuation_token and continuation_token.startswith("v1:"):
        try:
            offset = int(continuation_token.split(":", 2)[1])
        except ValueError:
            offset = 0

    ordered = sort_source_system_rows(rows)
    items = ordered[offset : offset + size]
    next_offset = offset + size
    next_token = None
    if next_offset < len(ordered):
        digest_input = projection_state_digest or sha256_digest({"rowCount": len(ordered)})
        next_token = f"v1:{next_offset}:{sha256_digest({'projectionStateDigest': digest_input, 'offset': next_offset})[:16]}"

    result = {
        "pageSize": size,
        "offset": offset,
        "totalCount": len(ordered),
        "returnedCount": len(items),
        "items": items,
        "continuationToken": next_token,
    }
    result["deterministicDigest"] = sha256_digest(result)
    return result


def build_row_facets(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    facets: list[dict[str, Any]] = []
    for facet_key in FILTER_KEYS:
        if facet_key not in FACET_KEYS:
            continue
        counter = Counter()
        for row in rows:
            value = row.get(facet_key)
            if isinstance(value, bool):
                counter[str(value).lower()] += 1
            else:
                counter[str(value)] += 1
        for value in sorted(counter):
            facets.append(
                {
                    "facetKey": facet_key,
                    "optionValue": value,
                    "count": counter[value],
                    "optionDigest": sha256_digest({"facetKey": facet_key, "optionValue": value}),
                }
            )
    facets.sort(key=lambda item: (item["facetKey"], item["optionDigest"]))
    return facets


def build_row_filters(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    options: dict[str, set[str]] = {key: set() for key in FILTER_KEYS}
    for row in rows:
        for key in FILTER_KEYS:
            value = row.get(key)
            if isinstance(value, bool):
                options[key].add(str(value).lower())
            else:
                options[key].add(str(value))

    filters: list[dict[str, Any]] = []
    for key in FILTER_KEYS:
        values = sorted(options[key])
        if not values:
            continue
        filter_type = "BOOLEAN" if key in {"runtimeObserved", "runtimeVerified", "decisionRequired"} else "ENUM"
        filters.append({"filterKey": key, "filterType": filter_type, "options": values})
    return filters
