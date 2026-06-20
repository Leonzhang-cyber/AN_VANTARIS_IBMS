"""Aggregation helpers for read-only Operations Console Packages."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest


def build_filter(*, field: str, values: Sequence[str]) -> dict[str, Any]:
    item = {"field": field, "values": sorted(str(value) for value in values)}
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_facet(*, field: str, counts: Mapping[str, int]) -> dict[str, Any]:
    item = {
        "field": field,
        "counts": {key: int(counts[key]) for key in sorted(counts)},
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_default_page(*, page_key: str, page_size: int, order_by: Sequence[str], continuation_token_seed: Mapping[str, Any]) -> dict[str, Any]:
    item = {
        "pageKey": page_key,
        "pageSize": int(page_size),
        "orderBy": list(order_by),
        "continuationToken": sha256_digest(continuation_token_seed),
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item
