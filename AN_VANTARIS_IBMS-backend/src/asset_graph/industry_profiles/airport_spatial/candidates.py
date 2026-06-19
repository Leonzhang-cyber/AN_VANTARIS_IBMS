"""Spatial candidate construction for airport profile."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ...airport_intake.location import normalize_location
from ...reconciliation.models import sha256_digest
from .constants import PROFILE_ID, SHEET_ZONE_HINTS
from .context import AirportSpatialContext


@dataclass(frozen=True)
class SpatialCandidate:
    candidate_type: str
    candidate_key: str
    profile_id: str
    tenant_id: str
    site_id: str
    source_value_digest: str
    normalized_code: str
    display_label_policy: str
    parent_candidate_key: str
    source_worksheet_digest: str
    mapping_status: str
    review_reasons: tuple[str, ...]
    generic_target: str
    profile_label: str

    def serialize(self) -> dict[str, Any]:
        return {
            "candidateType": self.candidate_type,
            "candidateKey": self.candidate_key,
            "profileId": self.profile_id,
            "tenantId": self.tenant_id,
            "siteId": self.site_id,
            "sourceValueDigest": self.source_value_digest,
            "normalizedCode": self.normalized_code,
            "displayLabelPolicy": self.display_label_policy,
            "parentCandidateKey": self.parent_candidate_key,
            "sourceWorksheetDigest": self.source_worksheet_digest,
            "mappingStatus": self.mapping_status,
            "reviewReasons": list(self.review_reasons),
            "genericTarget": self.generic_target,
            "profileLabel": self.profile_label,
        }


def _candidate_key(
    *,
    context: AirportSpatialContext,
    candidate_type: str,
    normalized_code: str,
) -> str:
    material = {
        "tenantId": context.tenant_id,
        "siteId": context.site_id,
        "profileId": PROFILE_ID,
        "candidateType": candidate_type,
        "normalizedCode": normalized_code,
    }
    return sha256_digest(material)


def _value_digest(value: str) -> str:
    return sha256_digest({"value": value.strip().upper()})


def _worksheet_digest(worksheet: str) -> str:
    return sha256_digest({"worksheet": worksheet})


def _mapping_status_for_code(code: str, allowed: tuple[str, ...]) -> tuple[str, tuple[str, ...]]:
    if not code:
        return "REVIEW_REQUIRED", ("MISSING_CODE",)
    if code not in allowed:
        return "REVIEW_REQUIRED", ("UNSUPPORTED_CODE",)
    return "MAPPED", ()


def build_airport_candidate(context: AirportSpatialContext) -> SpatialCandidate:
    code = context.airport_context_id.upper()
    review: list[str] = []
    status = "MAPPED"
    if context.context_placeholders_present:
        status = "REVIEW_REQUIRED"
        review.append("AIRPORT_CONTEXT_PLACEHOLDER")
    return SpatialCandidate(
        candidate_type="AirportCandidate",
        candidate_key=_candidate_key(context=context, candidate_type="AirportCandidate", normalized_code=code),
        profile_id=PROFILE_ID,
        tenant_id=context.tenant_id,
        site_id=context.site_id,
        source_value_digest=_value_digest(code),
        normalized_code=code,
        display_label_policy="CONTEXT_SUPPLIED",
        parent_candidate_key=_candidate_key(
            context=context, candidate_type="SiteCandidate", normalized_code=context.site_id.upper()
        ),
        source_worksheet_digest=sha256_digest({"source": "context"}),
        mapping_status=status,
        review_reasons=tuple(review),
        generic_target="Site",
        profile_label="Airport",
    )


def build_terminal_candidate(context: AirportSpatialContext, airport_key: str) -> SpatialCandidate:
    code = context.terminal_context_id.upper()
    review: list[str] = []
    status = "MAPPED"
    if context.terminal_context_id.upper() == "TERMINAL-CONTEXT-REQUIRED":
        status = "REVIEW_REQUIRED"
        review.append("TERMINAL_CONTEXT_PLACEHOLDER")
    if code not in context.allowed_terminal_codes and code != "TERMINAL-CONTEXT-REQUIRED":
        status = "REVIEW_REQUIRED"
        review.append("UNSUPPORTED_TERMINAL_CODE")
    return SpatialCandidate(
        candidate_type="TerminalCandidate",
        candidate_key=_candidate_key(context=context, candidate_type="TerminalCandidate", normalized_code=code),
        profile_id=PROFILE_ID,
        tenant_id=context.tenant_id,
        site_id=context.site_id,
        source_value_digest=_value_digest(code),
        normalized_code=code,
        display_label_policy="CONTEXT_SUPPLIED",
        parent_candidate_key=airport_key,
        source_worksheet_digest=sha256_digest({"source": "context"}),
        mapping_status=status,
        review_reasons=tuple(review),
        generic_target="Facility",
        profile_label="Terminal",
    )


def build_code_candidate(
    *,
    context: AirportSpatialContext,
    candidate_type: str,
    profile_label: str,
    generic_target: str,
    normalized_code: str,
    parent_key: str,
    allowed_codes: tuple[str, ...],
    worksheet: str = "",
) -> SpatialCandidate:
    code = normalized_code.strip().upper()
    status, reviews = _mapping_status_for_code(code, allowed_codes)
    return SpatialCandidate(
        candidate_type=candidate_type,
        candidate_key=_candidate_key(context=context, candidate_type=candidate_type, normalized_code=code),
        profile_id=PROFILE_ID,
        tenant_id=context.tenant_id,
        site_id=context.site_id,
        source_value_digest=_value_digest(code),
        normalized_code=code,
        display_label_policy="NORMALIZED_CODE",
        parent_candidate_key=parent_key,
        source_worksheet_digest=_worksheet_digest(worksheet) if worksheet else sha256_digest({"source": "aggregate"}),
        mapping_status=status,
        review_reasons=reviews,
        generic_target=generic_target,
        profile_label=profile_label,
    )


def build_location_candidate(
    *,
    context: AirportSpatialContext,
    normalized_location_key: str,
    parent_da_key: str,
    collision_group: str,
    semantic_status: str,
) -> SpatialCandidate:
    code = normalized_location_key
    reviews: list[str] = []
    status = "MAPPED"
    if semantic_status == "SEMANTIC_MERGE_NOT_APPROVED":
        status = "REVIEW_REQUIRED"
        reviews.append("SEMANTIC_MERGE_NOT_APPROVED")
    if semantic_status == "NORMALIZED_TEXT_COLLISION":
        status = "REVIEW_REQUIRED"
        reviews.append("NORMALIZED_TEXT_COLLISION")
    if not code:
        status = "REVIEW_REQUIRED"
        reviews.append("LOCATION_MISSING")
    return SpatialCandidate(
        candidate_type="LocationCandidate",
        candidate_key=_candidate_key(context=context, candidate_type="LocationCandidate", normalized_code=code),
        profile_id=PROFILE_ID,
        tenant_id=context.tenant_id,
        site_id=context.site_id,
        source_value_digest=_value_digest(code),
        normalized_code=code,
        display_label_policy="NORMALIZED_LOCATION_KEY",
        parent_candidate_key=parent_da_key,
        source_worksheet_digest=sha256_digest({"collisionGroup": collision_group}),
        mapping_status=status,
        review_reasons=tuple(reviews),
        generic_target="Space",
        profile_label="Location",
    )


def sheet_zone_finding(*, worksheet: str, zone_code: str) -> dict[str, str]:
    hint = SHEET_ZONE_HINTS.get(worksheet, "")
    zone = zone_code.strip().upper()
    if not zone:
        return {"classification": "ZONE_VALUE_MISSING", "worksheet": worksheet}
    if hint and zone != hint:
        return {"classification": "SHEET_ZONE_MISMATCH", "worksheet": worksheet}
    if hint and zone == hint:
        return {"classification": "SHEET_ZONE_MATCH", "worksheet": worksheet}
    return {"classification": "ZONE_CONTEXT_REVIEW_REQUIRED", "worksheet": worksheet}


def location_semantic_status(normalized_key: str, collision_count: int) -> str:
    if not normalized_key:
        return "LOCATION_MISSING"
    if collision_count > 1:
        return "NORMALIZED_TEXT_COLLISION"
    return "EXACT_NORMALIZED_LOCATION"
