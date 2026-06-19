"""Header normalization for airport asset Excel intake."""
from __future__ import annotations

import re

from .constants import CANONICAL_HEADER_MAP

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_header(raw: str) -> str:
    collapsed = _WHITESPACE_RE.sub(" ", raw.replace("\n", " ").replace("\r", " ")).strip()
    if not collapsed:
        return ""
    lookup = collapsed.casefold()
    return CANONICAL_HEADER_MAP.get(lookup, collapsed)


def normalize_headers(raw_headers: list[str]) -> list[str]:
    return [normalize_header(header) for header in raw_headers]
