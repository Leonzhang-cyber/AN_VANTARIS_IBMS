"""Reconciliation decision logic for airport asset reconciliation."""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Mapping, Sequence

from ...reconciliation.models import sha256_digest


def device_candidate_digest(device: Mapping[str, Any]) -> str:
    return sha256_digest(
        {
            "sourceId": str(device.get("sourceId", "")),
            "sourceWorksheet": str(device.get("sourceWorksheet", "")),
            "sourceRowNumber": int(device.get("sourceRowNumber", 0)),
        }
    )


def source_identity_digest(source_id: str) -> str:
    return sha256_digest({"sourceId": source_id})


def source_worksheet_digest(worksheet: str) -> str:
    return sha256_digest({"sourceWorksheet": worksheet})


def source_row_digest(worksheet: str, row_number: int) -> str:
    return sha256_digest({"sourceWorksheet": worksheet, "sourceRowNumber": row_number})


def duplicate_group_digest(digests: Sequence[str]) -> str:
    return sha256_digest({"memberDigests": sorted(digests)})


def classify_label(source_label: str, device_type_code: str) -> tuple[str, str | None]:
    text = str(source_label or "").strip()
    upper_code = str(device_type_code or "").upper()
    from .constants import LABEL_NORMALIZATION_CANDIDATES, LABEL_PREFIX_NORMALIZATIONS

    if text in LABEL_NORMALIZATION_CANDIDATES:
        entry = LABEL_NORMALIZATION_CANDIDATES[text]
        if entry.get("deviceTypeCode", upper_code) == upper_code or not entry.get("deviceTypeCode"):
            return entry["classification"], entry["normalizedLabel"]
    for source_prefix, normalized, code in LABEL_PREFIX_NORMALIZATIONS:
        if text == source_prefix and upper_code == code:
            return "LABEL_NORMALIZATION_CANDIDATE", normalized
    if text.lower().replace(" ", "") == "electromagneticlock" and upper_code in {"EML/DC1", "EML/DC2", "DC1", "DC2"}:
        return "LABEL_SEMANTIC_EQUIVALENCE_CANDIDATE", "Electromagnetic Lock"
    return "LABEL_EXACT", None


def identity_decision(
    *,
    source_id: str,
    group_size: int,
    group_status: str,
) -> str:
    if not source_id:
        return "SOURCE_IDENTITY_INCOMPLETE"
    if group_size == 1:
        return "SOURCE_IDENTITY_UNIQUE"
    if group_status == "DUPLICATE_GROUP_IDENTICAL":
        return "SOURCE_IDENTITY_DUPLICATE_IDENTICAL"
    if group_status == "DUPLICATE_GROUP_BLOCKED":
        return "IDENTITY_BLOCKED"
    if "CONFLICT" in group_status:
        return "SOURCE_IDENTITY_DUPLICATE_CONFLICT"
    if group_status == "DUPLICATE_GROUP_COMPATIBLE_REVIEW":
        return "SOURCE_IDENTITY_DUPLICATE_COMPATIBLE"
    return "IDENTITY_REVIEW_REQUIRED"


def evaluate_duplicate_group(members: list[dict[str, Any]]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    locations = {str(item.get("normalizedLocation", "")).upper() for item in members}
    spatial_keys = {str(item.get("locationCandidateKey", "")) for item in members}
    system_statuses = {str(item.get("systemMappingStatus", "")) for item in members}
    type_statuses = {str(item.get("deviceTypeMappingStatus", "")) for item in members}
    categories = {str(item.get("genericSystemCategory", "")) for item in members}
    classes = {str(item.get("genericDeviceClass", "")) for item in members}
    maintenance = {int(item.get("maintenanceExtensionFieldCount", 0)) for item in members}

    if len(system_statuses) > 1 or len(categories) > 1:
        return "DUPLICATE_GROUP_SYSTEM_CONFLICT", ["DUPLICATE_SYSTEM_DIVERGENCE"]
    if len(type_statuses) > 1 or len(classes) > 1:
        return "DUPLICATE_GROUP_DEVICE_TYPE_CONFLICT", ["DUPLICATE_DEVICE_TYPE_DIVERGENCE"]
    if len(maintenance) > 1:
        return "DUPLICATE_GROUP_MAINTENANCE_CONFLICT", ["DUPLICATE_MAINTENANCE_DIVERGENCE"]
    if len(locations) > 1 or len(spatial_keys) > 1:
        reasons.append("DUPLICATE_LOCATION_DIVERGENCE")
        if len(categories) == 1 and len(classes) == 1:
            return "DUPLICATE_GROUP_SPATIAL_CONFLICT", reasons
        return "DUPLICATE_GROUP_SPATIAL_CONFLICT", reasons

    worksheets = {str(item.get("sourceWorksheet", "")) for item in members}
    if len(worksheets) > 1:
        reasons.append("CROSS_WORKSHEET_DUPLICATE")
    return "DUPLICATE_GROUP_IDENTICAL", reasons


def spatial_decision(
    *,
    spatial_binding: Mapping[str, Any],
    context_placeholders_present: bool,
    location_group_status: str,
) -> str:
    status = str(spatial_binding.get("bindingStatus", ""))
    if status != "BOUND":
        return "SPATIAL_UNBOUND"
    if location_group_status in {"SEMANTIC_LOCATION_CONFLICT", "LOCATION_MERGE_APPROVAL_REQUIRED"}:
        return "SPATIAL_REVIEW_REQUIRED"
    if location_group_status == "NORMALIZED_LOCATION_TEXT_COLLISION":
        return "SPATIAL_MAPPING_VALID_WITH_LOCATION_REVIEW"
    if context_placeholders_present:
        return "SPATIAL_CONTEXT_PLACEHOLDER"
    return "SPATIAL_MAPPING_VALID"


def classification_decision(
    *,
    classification_binding: Mapping[str, Any],
    label_status: str,
) -> str:
    system_status = str(classification_binding.get("systemMappingStatus", ""))
    type_status = str(classification_binding.get("deviceTypeMappingStatus", ""))
    namespace = str(classification_binding.get("sourceNamespaceCode", ""))
    embedded = str(classification_binding.get("embeddedSystemCode", ""))

    if system_status in {"UNMAPPED_SOURCE_CODE", "UNSUPPORTED_SYSTEM"} or type_status in {
        "UNKNOWN_DEVICE_TYPE_CODE",
        "TYPE_REVIEW_REQUIRED",
    }:
        return "CLASSIFICATION_UNMAPPED"
    if namespace == "SCN" or "SCN_SEMANTIC_REVIEW_REQUIRED" in classification_binding.get("reviewReasons", []):
        return "CLASSIFICATION_NAMESPACE_REVIEW_REQUIRED"
    if embedded in {"CCT", "PAS"} and system_status == "ALIAS_CANDIDATE":
        return "CLASSIFICATION_ALIAS_APPROVAL_REQUIRED"
    if label_status in {"LABEL_NORMALIZATION_CANDIDATE", "LABEL_SEMANTIC_EQUIVALENCE_CANDIDATE", "LABEL_APPROVAL_REQUIRED"}:
        return "CLASSIFICATION_LABEL_CONFLICT_REVIEW"
    if type_status == "DEVICE_TYPE_COLUMN_CONFLICT":
        return "CLASSIFICATION_LABEL_CONFLICT_REVIEW"
    if system_status in {"EXACT_MATCH", "APPROVED_ALIAS"} and type_status in {"EXACT_TYPE_MATCH", "APPROVED_TYPE_ALIAS"}:
        return "CLASSIFICATION_FULLY_APPROVED"
    if str(classification_binding.get("genericSystemCategory", "")) and str(classification_binding.get("genericDeviceClass", "")):
        return "CLASSIFICATION_RECONCILIATION_ELIGIBLE"
    return "CLASSIFICATION_EVIDENCE_COMPLETE"


def canonical_proposal_decision(
    *,
    identity_decision_value: str,
    spatial_decision_value: str,
    classification_decision_value: str,
    duplicate_group_status: str | None,
    context_placeholders_present: bool,
) -> str:
    if identity_decision_value == "IDENTITY_BLOCKED":
        return "CANONICAL_PROPOSAL_BLOCKED"
    if context_placeholders_present:
        return "CANONICAL_PROPOSAL_CONTEXT_REQUIRED"
    if identity_decision_value.startswith("SOURCE_IDENTITY_DUPLICATE"):
        return "CANONICAL_PROPOSAL_DUPLICATE_REVIEW"
    if duplicate_group_status == "DUPLICATE_GROUP_CANONICAL_WINNER_REQUIRED":
        return "CANONICAL_PROPOSAL_DUPLICATE_REVIEW"
    if classification_decision_value in {
        "CLASSIFICATION_ALIAS_APPROVAL_REQUIRED",
        "CLASSIFICATION_NAMESPACE_REVIEW_REQUIRED",
        "CLASSIFICATION_LABEL_CONFLICT_REVIEW",
    }:
        return "CANONICAL_PROPOSAL_READY_WITH_REVIEW"
    if classification_decision_value == "CLASSIFICATION_UNMAPPED":
        return "CANONICAL_PROPOSAL_BLOCKED"
    if spatial_decision_value in {"SPATIAL_UNBOUND", "SPATIAL_BLOCKED"}:
        return "CANONICAL_PROPOSAL_BLOCKED"
    if classification_decision_value == "CLASSIFICATION_FULLY_APPROVED" and spatial_decision_value == "SPATIAL_MAPPING_VALID":
        return "CANONICAL_PROPOSAL_READY"
    if classification_decision_value in {"CLASSIFICATION_RECONCILIATION_ELIGIBLE", "CLASSIFICATION_EVIDENCE_COMPLETE"}:
        return "CANONICAL_PROPOSAL_READY_WITH_REVIEW"
    return "CANONICAL_PROPOSAL_DEFERRED"


def build_location_groups(devices: Sequence[Mapping[str, Any]], spatial_by_row: Mapping[tuple[str, int], Mapping[str, Any]]) -> dict[str, Any]:
    by_normalized: dict[str, list[dict[str, Any]]] = defaultdict(list)
    raw_variants: dict[str, set[str]] = defaultdict(set)
    for device in devices:
        normalized = str(device.get("normalizedLocation", "")).strip().upper()
        key = (str(device.get("sourceWorksheet", "")), int(device.get("sourceRowNumber", 0)))
        spatial = spatial_by_row.get(key, {})
        entry = {
            "deviceCandidateDigest": device_candidate_digest(device),
            "normalizedLocation": normalized,
            "rawLocationVariantDigest": sha256_digest({"rawLocation": str(device.get("rawLocation", device.get("locationName", "")))}),
            "locationCandidateKey": str(spatial.get("locationCandidateKey", "")),
        }
        by_normalized[normalized].append(entry)
        raw_variants[normalized].add(str(device.get("rawLocation", device.get("locationName", ""))).strip().upper())

    groups: list[dict[str, Any]] = []
    expected_shared = 0
    text_collision = 0
    conflict = 0
    for normalized_key in sorted(by_normalized):
        members = by_normalized[normalized_key]
        location_keys = {item["locationCandidateKey"] for item in members if item["locationCandidateKey"]}
        raw_count = len(raw_variants[normalized_key])
        if len(members) == 1:
            status = "EXACT_NORMALIZED_LOCATION"
        elif raw_count == 1:
            status = "EXPECTED_SHARED_LOCATION"
            expected_shared += 1
        elif len(location_keys) <= 1:
            status = "NORMALIZED_LOCATION_REUSE"
            expected_shared += 1
        else:
            status = "NORMALIZED_LOCATION_TEXT_COLLISION"
            text_collision += 1
        group = {
            "locationGroupDigest": sha256_digest({"normalizedLocationKey": normalized_key, "memberCount": len(members)}),
            "normalizedLocationKeyDigest": sha256_digest({"normalizedLocationKey": normalized_key}),
            "memberCount": len(members),
            "locationReconciliationStatus": status,
            "memberDeviceCandidateDigests": sorted(item["deviceCandidateDigest"] for item in members),
        }
        groups.append(group)

    identity_location_variants: dict[str, set[str]] = defaultdict(set)
    for device in devices:
        identity_location_variants[str(device.get("sourceId", ""))].add(str(device.get("normalizedLocation", "")).strip().upper())
    for source_id, variants in identity_location_variants.items():
        if len(variants) > 1:
            conflict += 1

    return {
        "groups": groups,
        "locationGroupCount": len(groups),
        "expectedSharedLocationGroupCount": expected_shared,
        "locationConflictGroupCount": text_collision + conflict,
        "locationTextCollisionGroupCount": text_collision,
    }


def location_group_status_for_device(normalized: str, groups: Sequence[Mapping[str, Any]]) -> str:
    digest = sha256_digest({"normalizedLocationKey": normalized.strip().upper()})
    for group in groups:
        if group.get("normalizedLocationKeyDigest") == digest:
            status = str(group.get("locationReconciliationStatus", ""))
            mapping = {
                "EXPECTED_SHARED_LOCATION": "EXPECTED_SHARED_LOCATION",
                "NORMALIZED_LOCATION_REUSE": "NORMALIZED_LOCATION_REUSE",
                "NORMALIZED_LOCATION_TEXT_COLLISION": "NORMALIZED_LOCATION_TEXT_COLLISION",
                "EXACT_NORMALIZED_LOCATION": "EXACT_NORMALIZED_LOCATION",
            }
            return mapping.get(status, status)
    return "EXACT_NORMALIZED_LOCATION"
