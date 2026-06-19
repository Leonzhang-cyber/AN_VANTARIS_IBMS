"""System alias evaluation for airport asset Excel intake."""
from __future__ import annotations

from typing import Optional

from .constants import KNOWN_SYSTEM_ALIASES


def normalize_system_code(value: str) -> str:
    return value.strip().upper()


def evaluate_system_alias(
    *,
    column_system: str,
    embedded_system: Optional[str],
) -> dict[str, str]:
    column_code = normalize_system_code(column_system)
    embedded_code = normalize_system_code(embedded_system or "")
    column_canonical = KNOWN_SYSTEM_ALIASES.get(column_code, column_code)
    embedded_canonical = KNOWN_SYSTEM_ALIASES.get(embedded_code, embedded_code) if embedded_code else ""

    if not column_code:
        return {"status": "UNMAPPED_CODE", "columnSystem": "", "embeddedSystem": embedded_code}

    if embedded_code and column_code == embedded_code:
        return {
            "status": "EXACT_MATCH",
            "columnSystem": column_code,
            "embeddedSystem": embedded_code,
        }

    if embedded_code and column_canonical == embedded_canonical and column_code != embedded_code:
        return {
            "status": "KNOWN_ALIAS_CANDIDATE",
            "columnSystem": column_code,
            "embeddedSystem": embedded_code,
            "aliasTarget": column_canonical,
        }

    if embedded_code and column_canonical != embedded_canonical:
        return {
            "status": "COLUMN_ID_CONFLICT",
            "columnSystem": column_code,
            "embeddedSystem": embedded_code,
        }

    if column_code in KNOWN_SYSTEM_ALIASES:
        return {
            "status": "KNOWN_ALIAS_CANDIDATE" if column_code != column_canonical else "EXACT_MATCH",
            "columnSystem": column_code,
            "embeddedSystem": embedded_code,
            "aliasTarget": column_canonical,
        }

    if column_code not in KNOWN_SYSTEM_ALIASES.values():
        return {
            "status": "UNMAPPED_CODE",
            "columnSystem": column_code,
            "embeddedSystem": embedded_code,
        }

    return {
        "status": "REVIEW_REQUIRED",
        "columnSystem": column_code,
        "embeddedSystem": embedded_code,
    }
