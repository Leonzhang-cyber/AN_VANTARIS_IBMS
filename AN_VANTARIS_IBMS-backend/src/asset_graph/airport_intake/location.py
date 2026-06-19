"""Location normalization for airport asset Excel intake."""
from __future__ import annotations

import re

_WHITESPACE_RE = re.compile(r"\s+")
_PUNCTUATION_RE = re.compile(r"[,;]+")


def normalize_location(raw: str) -> tuple[str, str]:
    """Return (rawLocation, normalizedLocation)."""
    raw_text = raw.replace("\n", " ").replace("\r", " ")
    trimmed = raw_text.strip()
    collapsed = _WHITESPACE_RE.sub(" ", trimmed)
    punct_normalized = _PUNCTUATION_RE.sub(" ", collapsed)
    normalized = _WHITESPACE_RE.sub(" ", punct_normalized).strip()
    comparison_key = normalized.upper()
    return trimmed, comparison_key


def candidate_display_name(device_type: str, location: str) -> str:
    _, normalized_location = normalize_location(location)
    device_type_clean = _WHITESPACE_RE.sub(" ", device_type.strip()).upper()
    location_clean = normalized_location
    if device_type_clean and location_clean:
        return f"{device_type_clean} @ {location_clean}"
    if device_type_clean:
        return device_type_clean
    return location_clean or "UNNAMED-DEVICE-CANDIDATE"
