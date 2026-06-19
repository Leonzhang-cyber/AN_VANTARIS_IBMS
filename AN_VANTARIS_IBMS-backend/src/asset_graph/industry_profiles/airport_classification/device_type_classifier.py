"""Device type classification for airport profile."""
from __future__ import annotations

from typing import Any

from ...reconciliation.models import sha256_digest
from .constants import DEVICE_TYPE_ALIASES, DEVICE_TYPE_DEFINITIONS, PROFILE_ID


def classify_device_type(
    *,
    device_type_code: str,
    source_device_type_label: str,
    source_evidence_digest: str,
) -> dict[str, Any]:
    code = str(device_type_code or "").strip().upper()
    column_label = str(source_device_type_label or "").strip()
    review_reasons: list[str] = []

    definition = DEVICE_TYPE_DEFINITIONS.get(code)
    alias_target = DEVICE_TYPE_ALIASES.get(code)

    if definition:
        airport_label = definition["label"]
        generic_class = definition["genericDeviceClass"]
        if column_label and column_label.lower() != airport_label.lower():
            mapping_status = "DEVICE_TYPE_COLUMN_CONFLICT"
            review_reasons.append("DEVICE_TYPE_LABEL_MISMATCH")
        else:
            mapping_status = "EXACT_TYPE_MATCH"
    elif alias_target and alias_target in DEVICE_TYPE_DEFINITIONS:
        airport_label = DEVICE_TYPE_DEFINITIONS[alias_target]["label"]
        generic_class = DEVICE_TYPE_DEFINITIONS[alias_target]["genericDeviceClass"]
        mapping_status = "TYPE_ALIAS_CANDIDATE"
        review_reasons.append(f"TYPE_ALIAS_CANDIDATE_{code}_TO_{alias_target}")
    elif code:
        airport_label = column_label or ""
        generic_class = "OTHER_CONTROLLED"
        mapping_status = "UNKNOWN_DEVICE_TYPE_CODE"
        review_reasons.append("UNKNOWN_DEVICE_TYPE_CODE")
    else:
        airport_label = column_label
        generic_class = "OTHER_CONTROLLED"
        mapping_status = "TYPE_REVIEW_REQUIRED"
        review_reasons.append("MISSING_DEVICE_TYPE_CODE")

    review_reasons = sorted(set(review_reasons))
    candidate = {
        "classificationCandidateId": sha256_digest({"profileId": PROFILE_ID, "deviceTypeCode": code}),
        "profileId": PROFILE_ID,
        "sourceDeviceType": code,
        "deviceTypeCode": code,
        "airportDeviceTypeLabel": airport_label,
        "genericDeviceClass": generic_class,
        "deviceTypeMappingStatus": mapping_status,
        "reviewReasons": review_reasons,
        "sourceEvidenceDigest": source_evidence_digest,
    }
    candidate["resultDigest"] = sha256_digest({k: v for k, v in candidate.items() if k != "resultDigest"})
    return candidate
