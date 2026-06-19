"""Controlled derivation from Device ID for formula comparison."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .device_id import parse_device_id
from .formula_constants import ALLOWED_LEVEL_CODES, DEVICE_TYPE_CODE_HINTS


@dataclass(frozen=True)
class ControlledDerivation:
    building_code: str
    level_code: str
    distribution_area_code: str
    embedded_system_code: str
    device_type_code: str
    sequence: str
    device_type_hint: str
    available: bool
    review_required: bool
    parsed_successfully: bool


def derive_controlled_values(device_id: str) -> ControlledDerivation:
    parsed = parse_device_id(device_id)
    if parsed.unparseable:
        return ControlledDerivation(
            building_code="",
            level_code="",
            distribution_area_code="",
            embedded_system_code="",
            device_type_code="",
            sequence="",
            device_type_hint="",
            available=False,
            review_required=True,
            parsed_successfully=False,
        )
    segments = parsed.segments
    type_code = segments.get("deviceTypeCode", "")
    hint = DEVICE_TYPE_CODE_HINTS.get(type_code.upper(), "")
    level = segments.get("levelCode", "").upper()
    review = (
        not parsed.parsed_successfully
        or (level and level not in ALLOWED_LEVEL_CODES)
        or (type_code and not hint)
    )
    return ControlledDerivation(
        building_code=segments.get("buildingCode", "").upper(),
        level_code=level,
        distribution_area_code=segments.get("distributionAreaCode", "").upper(),
        embedded_system_code=segments.get("embeddedSystemCode", "").upper(),
        device_type_code=type_code.upper(),
        sequence=segments.get("sequence", ""),
        device_type_hint=hint,
        available=parsed.parsed_successfully,
        review_required=review,
        parsed_successfully=parsed.parsed_successfully,
    )


def _normalize_compare(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def compare_building(cached: Any, derived: ControlledDerivation) -> dict[str, str]:
    if not derived.parsed_successfully:
        return {"comparisonStatus": "REVIEW_REQUIRED", "field": "Building"}
    cached_text = _normalize_compare(cached)
    if not cached_text:
        if derived.building_code:
            return {"comparisonStatus": "FORMULA_CACHE_MISSING_RECONSTRUCTED", "field": "Building"}
        return {"comparisonStatus": "FORMULA_CACHE_MISSING", "field": "Building"}
    if cached_text == derived.building_code:
        return {"comparisonStatus": "FORMULA_DERIVATION_MATCH", "field": "Building"}
    return {"comparisonStatus": "FORMULA_DERIVATION_MISMATCH", "field": "Building"}


def compare_level(cached: Any, derived: ControlledDerivation) -> dict[str, str]:
    if not derived.parsed_successfully:
        return {"comparisonStatus": "REVIEW_REQUIRED", "field": "Level"}
    cached_text = _normalize_compare(cached)
    if not cached_text:
        if derived.level_code:
            return {"comparisonStatus": "FORMULA_CACHE_MISSING_RECONSTRUCTED", "field": "Level"}
        return {"comparisonStatus": "FORMULA_CACHE_MISSING", "field": "Level"}
    if cached_text == derived.level_code:
        return {"comparisonStatus": "FORMULA_DERIVATION_MATCH", "field": "Level"}
    if cached_text not in ALLOWED_LEVEL_CODES:
        return {"comparisonStatus": "REVIEW_REQUIRED", "field": "Level"}
    return {"comparisonStatus": "FORMULA_DERIVATION_MISMATCH", "field": "Level"}


def compare_da(cached: Any, derived: ControlledDerivation) -> dict[str, str]:
    if not derived.parsed_successfully:
        return {"comparisonStatus": "REVIEW_REQUIRED", "field": "DA"}
    cached_text = _normalize_compare(cached)
    if not cached_text:
        if derived.distribution_area_code:
            return {"comparisonStatus": "FORMULA_CACHE_MISSING_RECONSTRUCTED", "field": "DA"}
        return {"comparisonStatus": "FORMULA_CACHE_MISSING", "field": "DA"}
    if cached_text == derived.distribution_area_code:
        return {"comparisonStatus": "FORMULA_DERIVATION_MATCH", "field": "DA"}
    return {"comparisonStatus": "FORMULA_DERIVATION_MISMATCH", "field": "DA"}


def compare_device_type(cached: Any, derived: ControlledDerivation, *, formula_present: bool = False) -> dict[str, str]:
    cached_text = "" if cached is None else str(cached).strip()
    if not cached_text:
        if derived.device_type_hint:
            return {"comparisonStatus": "FORMULA_CACHE_MISSING_RECONSTRUCTED", "field": "Device Type"}
        return {"comparisonStatus": "FORMULA_CACHE_MISSING", "field": "Device Type"}
    if not derived.device_type_code:
        return {"comparisonStatus": "REVIEW_REQUIRED", "field": "Device Type"}
    if derived.device_type_hint and cached_text.upper() == derived.device_type_hint.upper():
        return {"comparisonStatus": "FORMULA_DERIVATION_MATCH", "field": "Device Type"}
    if cached_text.upper() == derived.device_type_code.upper():
        return {"comparisonStatus": "FORMULA_DERIVATION_MATCH", "field": "Device Type"}
    if not formula_present:
        return {"comparisonStatus": "REVIEW_REQUIRED", "field": "Device Type"}
    if not derived.device_type_hint:
        return {"comparisonStatus": "REVIEW_REQUIRED", "field": "Device Type"}
    return {"comparisonStatus": "FORMULA_DERIVATION_MISMATCH", "field": "Device Type"}


def compare_sl(cached: Any, *, row_sequence: int) -> dict[str, str]:
    cached_text = "" if cached is None else str(cached).strip()
    if cached_text.endswith(".0"):
        cached_text = cached_text[:-2]
    expected = str(row_sequence)
    if not cached_text:
        return {"comparisonStatus": "FORMULA_CACHE_MISSING_RECONSTRUCTED", "field": "SL"}
    if cached_text == expected:
        return {"comparisonStatus": "FORMULA_DERIVATION_MATCH", "field": "SL"}
    return {"comparisonStatus": "REVIEW_REQUIRED", "field": "SL"}


def compare_zone_cached(
    cached: Any,
    *,
    sheet_name: str,
    row_zone_value: str,
) -> dict[str, str]:
    cached_text = _normalize_compare(cached)
    if not cached_text:
        return {"comparisonStatus": "FORMULA_CACHE_MISSING", "field": "Zone"}
    return {"comparisonStatus": "FORMULA_DERIVATION_MATCH", "field": "Zone"}


def build_field_formula_evidence(
    *,
    column_name: str,
    formula_meta: Optional[dict[str, Any]],
    comparison: dict[str, str],
    derived: ControlledDerivation,
) -> dict[str, Any]:
    return {
        "column": column_name,
        "formulaCellPresent": bool(formula_meta and formula_meta.get("formulaCellPresent")),
        "cachedValuePresent": bool(formula_meta and formula_meta.get("cachedValuePresent")),
        "controlledDerivationAvailable": derived.parsed_successfully,
        "comparisonStatus": comparison.get("comparisonStatus", "NOT_APPLICABLE"),
        "formulaClassification": (formula_meta or {}).get("formulaClassification", "NOT_A_FORMULA"),
        "isArrayFormula": bool(formula_meta and formula_meta.get("isArrayFormula")),
    }
