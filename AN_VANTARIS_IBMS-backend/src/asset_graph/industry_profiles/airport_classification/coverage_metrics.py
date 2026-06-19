"""Coverage semantics and aggregate metrics for airport classification."""
from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from ...reconciliation.models import sha256_digest

AUTHORITY = "ONE-AIRPORT-A1-03A"

APPROVED_SYSTEM_STATUSES = frozenset({"EXACT_MATCH", "APPROVED_ALIAS"})
APPROVED_DEVICE_TYPE_STATUSES = frozenset({"EXACT_TYPE_MATCH", "APPROVED_TYPE_ALIAS"})
PROFILE_READY_SYSTEM_STATUSES = frozenset({"EXACT_MATCH", "APPROVED_ALIAS", "ALIAS_CANDIDATE"})
PROFILE_READY_DEVICE_TYPE_STATUSES = frozenset(
    {"EXACT_TYPE_MATCH", "APPROVED_TYPE_ALIAS", "TYPE_ALIAS_CANDIDATE"}
)
COMPATIBILITY_EVALUATED_STATUSES = frozenset(
    {
        "SYSTEM_DEVICE_COMPATIBLE",
        "SYSTEM_DEVICE_UNEXPECTED",
        "SYSTEM_DEVICE_AMBIGUOUS",
        "SYSTEM_DEVICE_CONFLICT",
        "COMPATIBILITY_REVIEW_REQUIRED",
    }
)

METRIC_DEFINITIONS: dict[str, str] = {
    "deviceCandidateCount": "Total device evidence rows represented by classification bindings.",
    "evidenceClassifiedDeviceCount": (
        "Device records with bounded system and device-type classification results, "
        "including review and alias-candidate statuses."
    ),
    "reconciliationEligibleDeviceCount": (
        "Device records with deterministic genericSystemCategory, genericDeviceClass, "
        "and embeddedDeviceTypeCode suitable for A1-04 reconciliation handoff."
    ),
    "fullyApprovedDeviceCount": (
        "Device records where system mapping is EXACT_MATCH or APPROVED_ALIAS and "
        "device-type mapping is EXACT_TYPE_MATCH or APPROVED_TYPE_ALIAS with no pending review."
    ),
    "reviewRequiredDeviceCount": (
        "Device records that are not fully approved, including alias candidates, "
        "semantic review, and column conflicts."
    ),
    "unmappedDeviceCount": (
        "Device records lacking a bounded system or device-type mapping "
        "(UNMAPPED_SOURCE_CODE, UNSUPPORTED_SYSTEM, UNKNOWN_DEVICE_TYPE_CODE, TYPE_REVIEW_REQUIRED)."
    ),
    "compatibilityEvaluatedDeviceCount": (
        "Device records with an explicit compatibilityStatus outcome. "
        "Compatibility evaluation does not imply mapping approval."
    ),
    "compatibilityNotEvaluatedDeviceCount": "Device records missing a compatibilityStatus outcome.",
    "compatibilityReviewDeviceCount": (
        "Device records with compatibilityStatus COMPATIBILITY_REVIEW_REQUIRED."
    ),
    "classifiedDeviceCount": (
        "Legacy metric: device records where system mapping is EXACT_MATCH, APPROVED_ALIAS, "
        "or ALIAS_CANDIDATE AND device-type mapping is EXACT_TYPE_MATCH, APPROVED_TYPE_ALIAS, "
        "or TYPE_ALIAS_CANDIDATE. Excludes REVIEW_REQUIRED and DEVICE_TYPE_COLUMN_CONFLICT."
    ),
    "unclassifiedDeviceCount": (
        "Legacy metric: deviceCandidateCount minus classifiedDeviceCount. "
        "Does not mean records are absent from bindings."
    ),
    "compatibleSystemDeviceCount": (
        "Device records with compatibilityStatus SYSTEM_DEVICE_COMPATIBLE. "
        "Includes records with DEVICE_TYPE_COLUMN_CONFLICT when the type code matches the system category."
    ),
    "exactSystemMatchCount": "Unique system classification candidates with EXACT_MATCH (not a device-record count).",
    "exactDeviceTypeMatchCount": "Unique device-type classification candidates with EXACT_TYPE_MATCH (not a device-record count).",
    "deviceTypeColumnConflictRecordCount": "Device records with deviceTypeMappingStatus DEVICE_TYPE_COLUMN_CONFLICT.",
}


def _has_bounded_system(binding: Mapping[str, Any]) -> bool:
    status = str(binding.get("systemMappingStatus", ""))
    return bool(str(binding.get("sourceSystemValue", "")).strip()) and status not in {
        "UNMAPPED_SOURCE_CODE",
        "UNSUPPORTED_SYSTEM",
    }


def _has_bounded_device_type(binding: Mapping[str, Any]) -> bool:
    status = str(binding.get("deviceTypeMappingStatus", ""))
    return bool(str(binding.get("embeddedDeviceTypeCode", "")).strip()) and status not in {
        "UNKNOWN_DEVICE_TYPE_CODE",
        "TYPE_REVIEW_REQUIRED",
    }


def classified_for_evidence(binding: Mapping[str, Any]) -> bool:
    return _has_bounded_system(binding) and _has_bounded_device_type(binding)


def classified_for_reconciliation(binding: Mapping[str, Any]) -> bool:
    return bool(str(binding.get("genericSystemCategory", "")).strip()) and bool(
        str(binding.get("genericDeviceClass", "")).strip()
    ) and bool(str(binding.get("embeddedDeviceTypeCode", "")).strip())


def fully_approved_classification(binding: Mapping[str, Any]) -> bool:
    return (
        str(binding.get("systemMappingStatus", "")) in APPROVED_SYSTEM_STATUSES
        and str(binding.get("deviceTypeMappingStatus", "")) in APPROVED_DEVICE_TYPE_STATUSES
    )


def legacy_profile_ready_classification(binding: Mapping[str, Any]) -> bool:
    return (
        str(binding.get("systemMappingStatus", "")) in PROFILE_READY_SYSTEM_STATUSES
        and str(binding.get("deviceTypeMappingStatus", "")) in PROFILE_READY_DEVICE_TYPE_STATUSES
    )


def review_required_device(binding: Mapping[str, Any]) -> bool:
    return not fully_approved_classification(binding)


def unmapped_device(binding: Mapping[str, Any]) -> bool:
    system_status = str(binding.get("systemMappingStatus", ""))
    type_status = str(binding.get("deviceTypeMappingStatus", ""))
    return system_status in {"UNMAPPED_SOURCE_CODE", "UNSUPPORTED_SYSTEM"} or type_status in {
        "UNKNOWN_DEVICE_TYPE_CODE",
        "TYPE_REVIEW_REQUIRED",
    }


def compatibility_evaluated(binding: Mapping[str, Any]) -> bool:
    return str(binding.get("compatibilityStatus", "")) in COMPATIBILITY_EVALUATED_STATUSES


def _status_counter(bindings: Sequence[Mapping[str, Any]], field: str) -> dict[str, int]:
    counter = Counter(str(item.get(field, "")) for item in bindings)
    return dict(sorted(counter.items()))


def _unclassified_reason(binding: Mapping[str, Any]) -> str:
    if legacy_profile_ready_classification(binding):
        return "LEGACY_CLASSIFIED"
    system_status = str(binding.get("systemMappingStatus", ""))
    type_status = str(binding.get("deviceTypeMappingStatus", ""))
    if system_status == "REVIEW_REQUIRED":
        return "SYSTEM_REVIEW_REQUIRED"
    if type_status == "DEVICE_TYPE_COLUMN_CONFLICT":
        return "DEVICE_TYPE_COLUMN_CONFLICT"
    if system_status in {"UNMAPPED_SOURCE_CODE", "UNSUPPORTED_SYSTEM", "AMBIGUOUS_SOURCE_CODE", "COLUMN_ID_CONFLICT"}:
        return f"SYSTEM_{system_status}"
    if type_status in {"UNKNOWN_DEVICE_TYPE_CODE", "TYPE_REVIEW_REQUIRED", "TYPE_ALIAS_CANDIDATE"}:
        return f"DEVICE_TYPE_{type_status}"
    return "OTHER_LEGACY_UNCLASSIFIED"


def compute_device_coverage(bindings: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    total = len(bindings)
    legacy_classified = sum(1 for item in bindings if legacy_profile_ready_classification(item))
    unclassified_reasons = Counter(_unclassified_reason(item) for item in bindings if not legacy_profile_ready_classification(item))

    return {
        "totalDeviceCandidates": total,
        "devicesWithSystemClassification": sum(1 for item in bindings if _has_bounded_system(item)),
        "devicesWithoutSystemClassification": sum(1 for item in bindings if not _has_bounded_system(item)),
        "devicesWithDeviceTypeClassification": sum(1 for item in bindings if _has_bounded_device_type(item)),
        "devicesWithoutDeviceTypeClassification": sum(1 for item in bindings if not _has_bounded_device_type(item)),
        "devicesWithBothClassifications": sum(1 for item in bindings if classified_for_evidence(item)),
        "devicesWithCompatibilityEvaluation": sum(1 for item in bindings if compatibility_evaluated(item)),
        "devicesWithoutCompatibilityEvaluation": sum(1 for item in bindings if not compatibility_evaluated(item)),
        "deviceCandidateCount": total,
        "evidenceClassifiedDeviceCount": sum(1 for item in bindings if classified_for_evidence(item)),
        "reconciliationEligibleDeviceCount": sum(1 for item in bindings if classified_for_reconciliation(item)),
        "fullyApprovedDeviceCount": sum(1 for item in bindings if fully_approved_classification(item)),
        "reviewRequiredDeviceCount": sum(1 for item in bindings if review_required_device(item)),
        "unmappedDeviceCount": sum(1 for item in bindings if unmapped_device(item)),
        "compatibilityEvaluatedDeviceCount": sum(1 for item in bindings if compatibility_evaluated(item)),
        "compatibilityNotEvaluatedDeviceCount": sum(1 for item in bindings if not compatibility_evaluated(item)),
        "compatibilityReviewDeviceCount": sum(
            1 for item in bindings if str(item.get("compatibilityStatus", "")) == "COMPATIBILITY_REVIEW_REQUIRED"
        ),
        "classifiedDeviceCount": legacy_classified,
        "unclassifiedDeviceCount": total - legacy_classified,
        "compatibleSystemDeviceCount": sum(
            1 for item in bindings if str(item.get("compatibilityStatus", "")) == "SYSTEM_DEVICE_COMPATIBLE"
        ),
        "systemMappingStatusRecordCounts": _status_counter(bindings, "systemMappingStatus"),
        "deviceTypeMappingStatusRecordCounts": _status_counter(bindings, "deviceTypeMappingStatus"),
        "compatibilityStatusRecordCounts": _status_counter(bindings, "compatibilityStatus"),
        "legacyUnclassifiedReasonCounts": dict(sorted(unclassified_reasons.items())),
        "deviceTypeColumnConflictRecordCount": sum(
            1 for item in bindings if str(item.get("deviceTypeMappingStatus", "")) == "DEVICE_TYPE_COLUMN_CONFLICT"
        ),
    }


def build_coverage_analysis(
    bindings: Sequence[Mapping[str, Any]],
    *,
    source_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    coverage = compute_device_coverage(bindings)
    payload: dict[str, Any] = {
        "authority": AUTHORITY,
        "containsCustomerAssetIdentifiers": False,
        "semanticDefinitions": {
            "classifiedForEvidence": (
                "Bounded system and device-type classification exists for the record, including review statuses."
            ),
            "classifiedForProfileUse": (
                "Same as classifiedForEvidence for this profile version; all records receive profile outputs."
            ),
            "classifiedForReconciliation": (
                "genericSystemCategory, genericDeviceClass, and embeddedDeviceTypeCode are populated."
            ),
            "fullyApprovedClassification": (
                "System mapping is EXACT_MATCH or APPROVED_ALIAS and device-type mapping is "
                "EXACT_TYPE_MATCH or APPROVED_TYPE_ALIAS."
            ),
            "compatibilityEvaluated": (
                "compatibilityStatus is present. Compatibility does not imply mapping approval."
            ),
            "legacyClassifiedDeviceCount": METRIC_DEFINITIONS["classifiedDeviceCount"],
        },
        "metricDefinitions": METRIC_DEFINITIONS,
        "coverage": coverage,
        "primaryDiagnosis": "DISPLAYED_METRIC_AMBIGUOUS",
        "diagnosisExplanation": (
            "All device records are present in bindings with bounded evidence classifications. "
            "The legacy classifiedDeviceCount metric applies a strict AND predicate requiring both "
            "system and device-type statuses in profile-ready sets, excluding REVIEW_REQUIRED (14 SCN records) "
            "and DEVICE_TYPE_COLUMN_CONFLICT (61 label-mismatch records). "
            "compatibleSystemDeviceCount evaluates type-code fit and does not require label approval."
        ),
    }
    if source_summary is not None:
        payload["sourceClassificationSummaryDigest"] = str(source_summary.get("resultDigest", ""))
    digest_material = {k: v for k, v in payload.items() if k != "resultDigest"}
    payload["resultDigest"] = sha256_digest(digest_material)
    return payload


def extend_summary(summary: dict[str, Any], bindings: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    coverage = compute_device_coverage(bindings)
    extended = dict(summary)
    for key in (
        "evidenceClassifiedDeviceCount",
        "reconciliationEligibleDeviceCount",
        "fullyApprovedDeviceCount",
        "reviewRequiredDeviceCount",
        "unmappedDeviceCount",
        "compatibilityEvaluatedDeviceCount",
        "compatibilityNotEvaluatedDeviceCount",
        "compatibilityReviewDeviceCount",
        "deviceTypeColumnConflictRecordCount",
    ):
        extended[key] = coverage[key]
    extended["metricDefinitions"] = METRIC_DEFINITIONS
    extended["legacyClassifiedDeviceCountSemantics"] = METRIC_DEFINITIONS["classifiedDeviceCount"]
    return extended
