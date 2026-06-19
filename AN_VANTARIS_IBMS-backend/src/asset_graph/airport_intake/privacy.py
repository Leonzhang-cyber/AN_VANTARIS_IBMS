"""Privacy scanning for airport asset Excel intake."""
from __future__ import annotations

import re
from typing import Any, Mapping

from .constants import PRIVACY_PATTERNS

_COMPILED = [(category, re.compile(pattern)) for category, pattern in PRIVACY_PATTERNS]


def scan_cell(
    *,
    worksheet: str,
    row_number: int,
    column_name: str,
    value: Any,
) -> list[dict[str, str | int]]:
    if value in (None, ""):
        return []
    text = str(value)
    findings: list[dict[str, str | int]] = []
    for category, pattern in _COMPILED:
        if category == "PHONE" and len(re.sub(r"\D", "", text)) < 8:
            continue
        if pattern.search(text):
            findings.append(
                {
                    "category": category,
                    "worksheet": worksheet,
                    "rowNumber": row_number,
                    "columnName": column_name,
                    "status": "DETECTED",
                }
            )
    return findings


def scan_row(
    *,
    worksheet: str,
    row_number: int,
    record: Mapping[str, Any],
) -> list[dict[str, str | int]]:
    findings: list[dict[str, str | int]] = []
    for column_name, value in record.items():
        findings.extend(
            scan_cell(
                worksheet=worksheet,
                row_number=row_number,
                column_name=column_name,
                value=value,
            )
        )
    return findings
