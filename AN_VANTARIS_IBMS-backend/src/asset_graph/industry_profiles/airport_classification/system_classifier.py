"""System classification for airport profile."""
from __future__ import annotations

from typing import Any

from ...reconciliation.models import sha256_digest
from .constants import (
    APPROVED_EMBEDDED_ALIASES,
    DEVICE_TYPE_DEFINITIONS,
    EMBEDDED_SYSTEM_ALIAS_CANDIDATES,
    EXACT_INDUSTRY_CODES,
    INDUSTRY_TO_GENERIC,
    KNOWN_SOURCE_NAMESPACES,
    PROFILE_ID,
)

DEVICE_TYPE_CODES = frozenset(DEVICE_TYPE_DEFINITIONS)
from .device_id_segments import DeviceIdSegmentParse


def _confidence_for_status(status: str) -> str:
    mapping = {
        "EXACT_MATCH": "EXACT",
        "APPROVED_ALIAS": "HIGH",
        "ALIAS_CANDIDATE": "MEDIUM",
        "COLUMN_ID_CONFLICT": "LOW",
        "AMBIGUOUS_SOURCE_CODE": "LOW",
        "REVIEW_REQUIRED": "UNRESOLVED",
        "UNMAPPED_SOURCE_CODE": "UNRESOLVED",
        "UNSUPPORTED_SYSTEM": "UNRESOLVED",
    }
    return mapping.get(status, "UNRESOLVED")


def _authority_for_status(status: str) -> str:
    if status == "EXACT_MATCH":
        return "PLATFORM_GENERIC_CATEGORY"
    if status == "APPROVED_ALIAS":
        return "AIRPORT_PROFILE_APPROVED"
    if status == "ALIAS_CANDIDATE":
        return "EVIDENCE_ONLY"
    return "UNRESOLVED"


def classify_system(
    *,
    source_system_value: str,
    segment_parse: DeviceIdSegmentParse,
    source_evidence_digest: str,
) -> dict[str, Any]:
    column = str(source_system_value or "").strip().upper()
    embedded = segment_parse.embedded_system_code.upper()
    namespace = segment_parse.source_namespace_code.upper()
    review_reasons: list[str] = []

    industry_label = ""
    generic_category = ""
    mapping_status = "UNMAPPED_SOURCE_CODE"

    if column in INDUSTRY_TO_GENERIC:
        industry_label, generic_category = INDUSTRY_TO_GENERIC[column]
        if not embedded and not namespace:
            mapping_status = "EXACT_MATCH"
    elif column:
        mapping_status = "UNSUPPORTED_SYSTEM"
        review_reasons.append("UNSUPPORTED_COLUMN_SYSTEM")

    if namespace in KNOWN_SOURCE_NAMESPACES:
        review_reasons.append("SCN_SEMANTIC_REVIEW_REQUIRED")
        if column in INDUSTRY_TO_GENERIC:
            mapping_status = "REVIEW_REQUIRED"

    if embedded and column:
        if embedded in EMBEDDED_SYSTEM_ALIAS_CANDIDATES:
            alias_target = EMBEDDED_SYSTEM_ALIAS_CANDIDATES[embedded]
            if alias_target == column:
                if embedded in APPROVED_EMBEDDED_ALIASES:
                    mapping_status = "APPROVED_ALIAS"
                else:
                    mapping_status = "ALIAS_CANDIDATE"
                    review_reasons.append(f"EMBEDDED_ALIAS_CANDIDATE_{embedded}_TO_{alias_target}")
            else:
                mapping_status = "COLUMN_ID_CONFLICT"
                review_reasons.append("EMBEDDED_COLUMN_SYSTEM_MISMATCH")
        elif embedded in EXACT_INDUSTRY_CODES:
            if embedded == column or (column in INDUSTRY_TO_GENERIC and embedded == industry_label):
                mapping_status = "EXACT_MATCH"
            else:
                mapping_status = "COLUMN_ID_CONFLICT"
                review_reasons.append("EMBEDDED_EXACT_SYSTEM_COLUMN_MISMATCH")
        elif embedded in DEVICE_TYPE_CODES:
            if column in INDUSTRY_TO_GENERIC:
                if mapping_status == "UNMAPPED_SOURCE_CODE":
                    mapping_status = "REVIEW_REQUIRED"
                review_reasons.append("EMBEDDED_SEGMENT_IS_DEVICE_TYPE")
        elif embedded and embedded not in KNOWN_SOURCE_NAMESPACES:
            if column in INDUSTRY_TO_GENERIC and embedded != column:
                review_reasons.append("EMBEDDED_SYSTEM_SEGMENT_REVIEW")
                if mapping_status == "UNMAPPED_SOURCE_CODE":
                    mapping_status = "REVIEW_REQUIRED"

    if namespace in KNOWN_SOURCE_NAMESPACES and embedded:
        review_reasons.append("SOURCE_NAMESPACE_NOT_SYSTEM")

    if not column and embedded:
        mapping_status = "AMBIGUOUS_SOURCE_CODE"
        review_reasons.append("MISSING_COLUMN_SYSTEM")

    review_reasons = sorted(set(review_reasons))
    candidate = {
        "classificationCandidateId": sha256_digest(
            {
                "profileId": PROFILE_ID,
                "sourceSystemValue": column,
                "embeddedSystemCode": embedded,
                "sourceNamespace": namespace,
            }
        ),
        "profileId": PROFILE_ID,
        "sourceSystemValue": column,
        "embeddedSystemCode": embedded,
        "sourceNamespace": namespace,
        "genericSystemCategory": generic_category,
        "industrySystemLabel": industry_label,
        "mappingStatus": mapping_status,
        "confidenceClass": _confidence_for_status(mapping_status),
        "mappingAuthority": _authority_for_status(mapping_status),
        "reviewReasons": review_reasons,
        "sourceEvidenceDigest": source_evidence_digest,
    }
    candidate["resultDigest"] = sha256_digest({k: v for k, v in candidate.items() if k != "resultDigest"})
    return candidate
