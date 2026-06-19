"""Airport spatial context validation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ...reconciliation.models import sha256_digest
from .constants import (
    AUTHORITY,
    MAPPING_VERSION,
    MAX_BUILDINGS,
    MAX_DISTRIBUTION_AREAS,
    MAX_LEVELS,
    MAX_TERMINALS,
    MAX_ZONES,
    PLACEHOLDER_AIRPORT,
    PLACEHOLDER_TERMINAL,
    PROFILE_ID,
    WILDCARD_TOKENS,
)
from .errors import AirportSpatialProfileError


def _normalize_codes(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({value.strip().upper() for value in values if value and value.strip()}))


def _reject_wildcards(label: str, values: Sequence[str]) -> None:
    for value in values:
        token = value.strip().upper()
        if token in WILDCARD_TOKENS or "*" in token:
            raise AirportSpatialProfileError("WILDCARD_CONTEXT", f"{label} contains wildcard value")


@dataclass(frozen=True)
class AirportSpatialContext:
    industry_profile_id: str
    tenant_id: str
    site_id: str
    airport_context_id: str
    terminal_context_id: str
    building_context_policy: str
    source_workbook_digest: str
    mapping_version: str
    allowed_terminal_codes: tuple[str, ...]
    allowed_building_codes: tuple[str, ...]
    allowed_level_codes: tuple[str, ...]
    allowed_zone_codes: tuple[str, ...]
    allowed_distribution_area_codes: tuple[str, ...]
    location_normalization_policy: str
    scope_digest: str

    @staticmethod
    def create(
        *,
        tenant_id: str,
        site_id: str,
        airport_context_id: str,
        terminal_context_id: str,
        source_workbook_digest: str,
        allowed_terminal_codes: Sequence[str],
        allowed_building_codes: Sequence[str],
        allowed_level_codes: Sequence[str],
        allowed_zone_codes: Sequence[str],
        allowed_distribution_area_codes: Sequence[str],
        building_context_policy: str = "ROW_LEVEL_AUTHORITATIVE",
        location_normalization_policy: str = "BOUNDED_TEXT_NORMALIZATION",
        mapping_version: str = MAPPING_VERSION,
        industry_profile_id: str = PROFILE_ID,
    ) -> "AirportSpatialContext":
        if not tenant_id or not tenant_id.strip():
            raise AirportSpatialProfileError("MISSING_TENANT", "tenantId is required")
        if not site_id or not site_id.strip():
            raise AirportSpatialProfileError("MISSING_SITE", "siteId is required")
        if not mapping_version or mapping_version != MAPPING_VERSION:
            raise AirportSpatialProfileError("UNSUPPORTED_MAPPING_VERSION", "mapping version is unsupported")
        if not industry_profile_id:
            raise AirportSpatialProfileError("MISSING_PROFILE", "industry profile id is required")

        terminal_codes = _normalize_codes(allowed_terminal_codes)
        building_codes = _normalize_codes(allowed_building_codes)
        level_codes = _normalize_codes(allowed_level_codes)
        zone_codes = _normalize_codes(allowed_zone_codes)
        da_codes = _normalize_codes(allowed_distribution_area_codes)

        for label, values in (
            ("tenantId", (tenant_id,)),
            ("siteId", (site_id,)),
            ("terminalCodes", terminal_codes),
            ("buildingCodes", building_codes),
            ("levelCodes", level_codes),
            ("zoneCodes", zone_codes),
            ("distributionAreaCodes", da_codes),
        ):
            _reject_wildcards(label, values)

        if len(terminal_codes) > MAX_TERMINALS:
            raise AirportSpatialProfileError("CONTEXT_LIMIT_EXCEEDED", "terminal code list exceeds limit")
        if len(building_codes) > MAX_BUILDINGS:
            raise AirportSpatialProfileError("CONTEXT_LIMIT_EXCEEDED", "building code list exceeds limit")
        if len(level_codes) > MAX_LEVELS:
            raise AirportSpatialProfileError("CONTEXT_LIMIT_EXCEEDED", "level code list exceeds limit")
        if len(zone_codes) > MAX_ZONES:
            raise AirportSpatialProfileError("CONTEXT_LIMIT_EXCEEDED", "zone code list exceeds limit")
        if len(da_codes) > MAX_DISTRIBUTION_AREAS:
            raise AirportSpatialProfileError("CONTEXT_LIMIT_EXCEEDED", "distribution area list exceeds limit")

        scope_material = {
            "authority": AUTHORITY,
            "industryProfileId": industry_profile_id,
            "tenantId": tenant_id.strip(),
            "siteId": site_id.strip(),
            "airportContextId": airport_context_id.strip(),
            "terminalContextId": terminal_context_id.strip(),
            "mappingVersion": mapping_version,
            "allowedTerminalCodes": terminal_codes,
            "allowedBuildingCodes": building_codes,
            "allowedLevelCodes": level_codes,
            "allowedZoneCodes": zone_codes,
            "allowedDistributionAreaCodes": da_codes,
            "sourceWorkbookDigest": source_workbook_digest.strip(),
        }
        scope_digest = sha256_digest(scope_material)

        return AirportSpatialContext(
            industry_profile_id=industry_profile_id,
            tenant_id=tenant_id.strip(),
            site_id=site_id.strip(),
            airport_context_id=airport_context_id.strip(),
            terminal_context_id=terminal_context_id.strip(),
            building_context_policy=building_context_policy,
            source_workbook_digest=source_workbook_digest.strip(),
            mapping_version=mapping_version,
            allowed_terminal_codes=terminal_codes,
            allowed_building_codes=building_codes,
            allowed_level_codes=level_codes,
            allowed_zone_codes=zone_codes,
            allowed_distribution_area_codes=da_codes,
            location_normalization_policy=location_normalization_policy,
            scope_digest=scope_digest,
        )

    @property
    def context_placeholders_present(self) -> bool:
        return (
            self.airport_context_id == PLACEHOLDER_AIRPORT
            or self.terminal_context_id == PLACEHOLDER_TERMINAL
        )

    def serialize(self) -> dict[str, object]:
        return {
            "industryProfileId": self.industry_profile_id,
            "tenantId": self.tenant_id,
            "siteId": self.site_id,
            "airportContextId": self.airport_context_id,
            "terminalContextId": self.terminal_context_id,
            "buildingContextPolicy": self.building_context_policy,
            "sourceWorkbookDigest": self.source_workbook_digest,
            "mappingVersion": self.mapping_version,
            "allowedTerminalCodes": list(self.allowed_terminal_codes),
            "allowedBuildingCodes": list(self.allowed_building_codes),
            "allowedLevelCodes": list(self.allowed_level_codes),
            "allowedZoneCodes": list(self.allowed_zone_codes),
            "allowedDistributionAreaCodes": list(self.allowed_distribution_area_codes),
            "locationNormalizationPolicy": self.location_normalization_policy,
            "scopeDigest": self.scope_digest,
            "contextPlaceholdersPresent": self.context_placeholders_present,
        }
