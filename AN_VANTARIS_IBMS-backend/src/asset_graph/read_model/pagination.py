"""Deterministic bounded pagination."""
from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Sequence, Tuple, TypeVar

from ..reconciliation.models import canonical_json
from .errors import QueryBindingError

DEFAULT_LIMIT = 50
MAXIMUM_LIMIT = 500

T = TypeVar("T")


@dataclass(frozen=True)
class PageResult:
    items: Tuple[Any, ...]
    next_cursor: str | None
    limit: int
    query_binding: str


def validate_limit(limit: int | None) -> int:
    value = DEFAULT_LIMIT if limit is None else int(limit)
    if value < 0:
        raise QueryBindingError("limit must not be negative")
    if value > MAXIMUM_LIMIT:
        raise QueryBindingError("limit exceeds maximum")
    return value


def query_binding(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def encode_cursor(*, query_binding: str, last_key: str) -> str:
    material = json.dumps({"queryBinding": query_binding, "lastKey": last_key}, sort_keys=True, separators=(",", ":"))
    return base64.urlsafe_b64encode(material.encode("utf-8")).decode().rstrip("=")


def decode_cursor(cursor: str, *, expected_binding: str) -> str:
    try:
        padding = "=" * (-len(cursor) % 4)
        payload = json.loads(base64.urlsafe_b64decode(cursor + padding).decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        raise QueryBindingError("malformed cursor") from exc
    if payload.get("queryBinding") != expected_binding:
        raise QueryBindingError("cursor used with a different query")
    last_key = payload.get("lastKey")
    if not isinstance(last_key, str):
        raise QueryBindingError("malformed cursor")
    return last_key


def paginate(
    rows: Sequence[T],
    *,
    limit: int,
    cursor: str | None,
    query_binding_value: str,
    sort_key: Callable[[T], str],
) -> PageResult:
    ordered = sorted(rows, key=sort_key)
    if cursor:
        after = decode_cursor(cursor, expected_binding=query_binding_value)
        ordered = [row for row in ordered if sort_key(row) > after]
    page = tuple(ordered[:limit])
    next_cursor = None
    if len(ordered) > limit and page:
        next_cursor = encode_cursor(query_binding=query_binding_value, last_key=sort_key(page[-1]))
    return PageResult(items=page, next_cursor=next_cursor, limit=limit, query_binding=query_binding_value)
