"""Formula safety inspection without execution."""
from __future__ import annotations

import re
from typing import Any

from openpyxl.worksheet.formula import ArrayFormula

from .formula_constants import (
    APPROVED_FORMULA_COLUMNS,
    CONDITIONAL_FORMULA_COLUMNS,
    EXTERNAL_FORMULA_MARKERS,
    FORBIDDEN_FORMULA_TOKENS,
    SAFE_FORMULA_FUNCTIONS,
)

_FORMULA_PREFIX_RE = re.compile(r"^=")
_SAFE_FUNCTION_RE = re.compile(r"\b([A-Z][A-Z0-9_]*)\(", re.IGNORECASE)


def _formula_text(value: Any) -> str:
    if isinstance(value, ArrayFormula):
        return str(value.text or "")
    if isinstance(value, str):
        return value
    return ""


def is_formula_cell(value: Any) -> bool:
    if isinstance(value, ArrayFormula):
        return True
    if isinstance(value, str):
        return _FORMULA_PREFIX_RE.match(value.strip()) is not None
    return False


def is_array_formula(value: Any) -> bool:
    return isinstance(value, ArrayFormula)


def extract_safe_function_set(formula_text: str) -> list[str]:
    if not formula_text:
        return []
    found = {match.group(1).upper() for match in _SAFE_FUNCTION_RE.finditer(formula_text)}
    return sorted(found)


def inspect_formula_text(formula_text: str) -> str:
    upper = formula_text.upper()
    if not formula_text.strip():
        return "UNSUPPORTED_FORMULA"
    for marker in EXTERNAL_FORMULA_MARKERS:
        if marker in upper:
            return "EXTERNAL_REFERENCE_FORMULA"
    if "[" in formula_text and "]" in formula_text:
        bracket = formula_text[formula_text.find("[") : formula_text.find("]") + 1]
        if ".xls" in bracket.lower():
            return "EXTERNAL_REFERENCE_FORMULA"
    for token in FORBIDDEN_FORMULA_TOKENS:
        if token in upper:
            return "UNSUPPORTED_FORMULA"
    if "HYPERLINK(" in upper and ("HTTP://" in upper or "HTTPS://" in upper or "FILE://" in upper):
        return "EXTERNAL_REFERENCE_FORMULA"
    return "APPROVED_DERIVED_FORMULA"


def classify_column_formula(
    *,
    column_name: str,
    formula_text: str,
    cached_value: Any,
    location_value: str,
) -> str:
    safety = inspect_formula_text(formula_text)
    if safety != "APPROVED_DERIVED_FORMULA":
        return safety
    if column_name in APPROVED_FORMULA_COLUMNS:
        return "APPROVED_DERIVED_FORMULA"
    if column_name in CONDITIONAL_FORMULA_COLUMNS:
        cached_text = "" if cached_value is None else str(cached_value).strip()
        location_key = location_value.strip().upper()
        if cached_text and location_key and cached_text.upper() == location_key:
            return "LEGACY_FIELD_SEMANTIC_CONFLICT"
        return "LEGACY_AMBIGUOUS_FORMULA"
    return "UNAPPROVED_FORMULA"


def summarize_formula_cell(
    *,
    worksheet: str,
    column_name: str,
    row_number: int,
    formula_value: Any,
    cached_value: Any,
    location_value: str = "",
) -> dict[str, Any]:
    formula_text = _formula_text(formula_value)
    classification = classify_column_formula(
        column_name=column_name,
        formula_text=formula_text,
        cached_value=cached_value,
        location_value=location_value,
    )
    safe_functions = extract_safe_function_set(formula_text)
    return {
        "worksheet": worksheet,
        "column": column_name,
        "row": row_number,
        "formulaClassification": classification,
        "safeFunctionSet": safe_functions,
        "status": classification,
        "formulaCellPresent": True,
        "cachedValuePresent": cached_value not in (None, ""),
        "isArrayFormula": is_array_formula(formula_value),
    }
