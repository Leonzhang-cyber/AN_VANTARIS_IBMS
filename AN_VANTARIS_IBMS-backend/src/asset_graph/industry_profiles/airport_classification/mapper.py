"""Airport classification orchestration."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ...reconciliation.models import sha256_digest
from .compatibility import evaluate_compatibility
from .constants import (
    AUTHORITY,
    FORBIDDEN_READINESS,
    IMPLEMENTATION_MODE,
    PROFILE_ID,
    PROFILE_NAME,
    PROFILE_VERSION,
    READINESS_OUTCOMES,
)
from .context import AirportClassificationContext
from .device_id_segments import parse_device_id_segments
from .device_type_classifier import classify_device_type
from .duplicates import compare_duplicate_classifications
from .errors import AirportClassificationProfileError
from .evidence import load_json, load_spatial_bindings, verify_intake_evidence, verify_spatial_result
from .system_classifier import classify_system


def compare_deterministic_outputs(first: Path, second: Path) -> tuple[bool, str]:
    if not first.is_file() or not second.is_file():
        return False, "MISSING_OUTPUT"
    if first.read_bytes() == second.read_bytes():
        return True, "MATCH"
    return False, "MISMATCH"


def _device_candidate_digest(device: dict[str, Any]) -> str:
    return sha256_digest(
        {
            "sourceId": str(device.get("sourceId", "")),
            "sourceWorksheet": str(device.get("sourceWorksheet", "")),
            "sourceRowNumber": int(device.get("sourceRowNumber", 0)),
        }
    )


def _spatial_binding_digest(binding: dict[str, Any]) -> str:
    return sha256_digest(
        {
            "sourceDeviceDigest": str(binding.get("sourceDeviceDigest", "")),
            "bindingStatus": str(binding.get("bindingStatus", "")),
            "buildingCandidateKey": str(binding.get("buildingCandidateKey", "")),
            "levelCandidateKey": str(binding.get("levelCandidateKey", "")),
            "zoneCandidateKey": str(binding.get("zoneCandidateKey", "")),
            "distributionAreaCandidateKey": str(binding.get("distributionAreaCandidateKey", "")),
            "locationCandidateKey": str(binding.get("locationCandidateKey", "")),
        }
    )


def _index_spatial_bindings(bindings: list[dict[str, Any]]) -> dict[tuple[str, int], dict[str, Any]]:
    indexed: dict[tuple[str, int], dict[str, Any]] = {}
    for binding in bindings:
        key = (str(binding.get("sourceWorksheet", "")), int(binding.get("sourceRowNumber", 0)))
        indexed[key] = binding
    return indexed


def run_airport_classification(
    *,
    intake_evidence_path: Path,
    spatial_result_path: Path,
    spatial_bindings_path: Path,
    output_dir: Path,
    context: AirportClassificationContext,
    run_id: str,
) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    intake = load_json(intake_evidence_path)
    spatial = load_json(spatial_result_path)
    bindings_raw = load_spatial_bindings(spatial_bindings_path)

    intake_meta = verify_intake_evidence(
        intake,
        expected_workbook_digest=context.source_workbook_digest,
        expected_result_digest=context.expected_intake_result_digest,
    )
    spatial_meta = verify_spatial_result(
        spatial,
        expected_result_digest=context.expected_spatial_result_digest,
        expected_intake_result_digest=intake_meta["resultDigest"],
    )

    if len(bindings_raw) != len(intake.get("deviceCandidates", [])):
        raise AirportClassificationProfileError(
            "BINDING_COUNT_MISMATCH",
            "spatial binding count does not match device candidate count",
        )

    binding_index = _index_spatial_bindings(bindings_raw)
    devices = list(intake.get("deviceCandidates", []))
    intake_digest = intake_meta["resultDigest"]
    spatial_digest = spatial_meta["resultDigest"]

    system_candidates: dict[str, dict[str, Any]] = {}
    device_type_candidates: dict[str, dict[str, Any]] = {}
    device_bindings: list[dict[str, Any]] = []
    review_findings: list[dict[str, Any]] = []

    for device in devices:
        source_id = str(device.get("sourceId", ""))
        segment = parse_device_id_segments(source_id)
        worksheet = str(device.get("sourceWorksheet", ""))
        row_number = int(device.get("sourceRowNumber", 0))
        spatial_binding = binding_index.get((worksheet, row_number), {})
        device_digest = _device_candidate_digest(device)
        binding_digest_value = _spatial_binding_digest(spatial_binding) if spatial_binding else ""

        type_code = segment.device_type_code or str(device.get("sourceDeviceType", "")).split()[0].upper()
        if not type_code and segment.embedded_system_code in {"EML/DC1", "EML/DC2", "BG", "PB", "INCR", "OTCR"}:
            type_code = segment.embedded_system_code

        system_result = classify_system(
            source_system_value=str(device.get("sourceSystemCode", "")),
            segment_parse=segment,
            source_evidence_digest=intake_digest,
        )
        type_result = classify_device_type(
            device_type_code=type_code,
            source_device_type_label=str(device.get("sourceDeviceType", "")),
            source_evidence_digest=intake_digest,
        )

        system_key = system_result["classificationCandidateId"]
        type_key = type_result["classificationCandidateId"]
        system_candidates[system_key] = system_result
        device_type_candidates[type_key] = type_result

        compatibility_status, compatibility_reasons = evaluate_compatibility(
            generic_system_category=str(system_result.get("genericSystemCategory", "")),
            device_type_code=type_code,
            system_mapping_status=str(system_result.get("mappingStatus", "")),
            device_type_mapping_status=str(type_result.get("deviceTypeMappingStatus", "")),
        )

        binding_reasons = sorted(
            set(
                list(system_result.get("reviewReasons", []))
                + list(type_result.get("reviewReasons", []))
                + compatibility_reasons
            )
        )

        binding = {
            "deviceCandidateDigest": device_digest,
            "spatialBindingDigest": binding_digest_value,
            "sourceSystemValue": system_result["sourceSystemValue"],
            "sourceNamespaceCode": segment.source_namespace_code,
            "embeddedDeviceTypeCode": type_code,
            "embeddedSystemCode": segment.embedded_system_code,
            "industrySystemLabel": system_result["industrySystemLabel"],
            "genericSystemCategory": system_result["genericSystemCategory"],
            "airportDeviceTypeLabel": type_result["airportDeviceTypeLabel"],
            "genericDeviceClass": type_result["genericDeviceClass"],
            "systemMappingStatus": system_result["mappingStatus"],
            "deviceTypeMappingStatus": type_result["deviceTypeMappingStatus"],
            "compatibilityStatus": compatibility_status,
            "parseStatus": segment.parse_status,
            "parsePattern": segment.parse_pattern,
            "reviewReasons": binding_reasons,
            "sourceWorksheet": worksheet,
            "sourceRowNumber": row_number,
            "sourceId": source_id,
        }
        binding["bindingDigest"] = sha256_digest({k: v for k, v in binding.items() if k not in {"sourceId", "bindingDigest"}})
        device_bindings.append(binding)

        for reason in binding_reasons:
            if reason == "SCN_SEMANTIC_REVIEW_REQUIRED":
                review_findings.append(
                    {
                        "classification": "SCN_SEMANTIC_REVIEW_REQUIRED",
                        "deviceCandidateDigest": device_digest,
                        "sourceNamespaceCode": segment.source_namespace_code,
                        "embeddedDeviceTypeCode": type_code,
                        "reviewReasons": [reason],
                    }
                )

    device_bindings.sort(key=lambda item: (str(item.get("sourceWorksheet", "")), int(item.get("sourceRowNumber", 0))))

    duplicate_findings = compare_duplicate_classifications(device_bindings)
    review_findings.extend(duplicate_findings)

    for binding in device_bindings:
        if binding.get("compatibilityStatus") == "SYSTEM_DEVICE_UNEXPECTED":
            review_findings.append(
                {
                    "classification": "SYSTEM_DEVICE_UNEXPECTED",
                    "deviceCandidateDigest": binding["deviceCandidateDigest"],
                    "genericSystemCategory": binding["genericSystemCategory"],
                    "embeddedDeviceTypeCode": binding["embeddedDeviceTypeCode"],
                    "reviewReasons": ["UNEXPECTED_DEVICE_TYPE_FOR_SYSTEM"],
                }
            )

    review_findings.sort(key=lambda item: json.dumps(item, sort_keys=True))

    exact_system = sum(1 for item in system_candidates.values() if item["mappingStatus"] == "EXACT_MATCH")
    approved_system_alias = sum(1 for item in system_candidates.values() if item["mappingStatus"] == "APPROVED_ALIAS")
    system_alias_candidate = sum(1 for item in system_candidates.values() if item["mappingStatus"] == "ALIAS_CANDIDATE")
    ambiguous_source = sum(1 for item in system_candidates.values() if item["mappingStatus"] == "AMBIGUOUS_SOURCE_CODE")
    system_column_conflict = sum(1 for item in system_candidates.values() if item["mappingStatus"] == "COLUMN_ID_CONFLICT")

    exact_type = sum(1 for item in device_type_candidates.values() if item["deviceTypeMappingStatus"] == "EXACT_TYPE_MATCH")
    approved_type_alias = sum(
        1 for item in device_type_candidates.values() if item["deviceTypeMappingStatus"] == "APPROVED_TYPE_ALIAS"
    )
    type_alias_candidate = sum(
        1 for item in device_type_candidates.values() if item["deviceTypeMappingStatus"] == "TYPE_ALIAS_CANDIDATE"
    )
    unknown_type = sum(
        1 for item in device_type_candidates.values() if item["deviceTypeMappingStatus"] == "UNKNOWN_DEVICE_TYPE_CODE"
    )
    type_column_conflict = sum(
        1 for item in device_type_candidates.values() if item["deviceTypeMappingStatus"] == "DEVICE_TYPE_COLUMN_CONFLICT"
    )

    compatible_count = sum(1 for item in device_bindings if item["compatibilityStatus"] == "SYSTEM_DEVICE_COMPATIBLE")
    unexpected_count = sum(1 for item in device_bindings if item["compatibilityStatus"] == "SYSTEM_DEVICE_UNEXPECTED")
    ambiguous_compat = sum(1 for item in device_bindings if item["compatibilityStatus"] == "SYSTEM_DEVICE_AMBIGUOUS")
    duplicate_agreement = sum(1 for item in duplicate_findings if item["classification"] == "DUPLICATE_CLASSIFICATION_AGREEMENT")
    duplicate_conflict = sum(
        1
        for item in duplicate_findings
        if item["classification"]
        in {"DUPLICATE_SYSTEM_CONFLICT", "DUPLICATE_DEVICE_TYPE_CONFLICT", "DUPLICATE_CLASSIFICATION_REVIEW_REQUIRED"}
    )

    classified_count = sum(
        1
        for item in device_bindings
        if item["systemMappingStatus"] in {"EXACT_MATCH", "APPROVED_ALIAS", "ALIAS_CANDIDATE"}
        and item["deviceTypeMappingStatus"] in {"EXACT_TYPE_MATCH", "APPROVED_TYPE_ALIAS", "TYPE_ALIAS_CANDIDATE"}
    )
    unclassified_count = len(device_bindings) - classified_count

    blocker_count = sum(1 for item in device_bindings if item["systemMappingStatus"] == "UNSUPPORTED_SYSTEM")
    review_count = len(review_findings) + sum(1 for item in device_bindings if item.get("reviewReasons"))
    warning_count = unexpected_count + type_column_conflict + system_column_conflict

    if blocker_count:
        readiness = "CLASSIFICATION_BLOCKED"
    elif (
        system_alias_candidate
        or type_alias_candidate
        or unknown_type
        or duplicate_conflict
        or review_findings
        or any(item.get("reviewReasons") for item in device_bindings)
    ):
        readiness = "CLASSIFICATION_COMPLETE_WITH_REVIEWS"
    else:
        readiness = "READY_FOR_AIRPORT_ASSET_RECONCILIATION"

    if readiness in FORBIDDEN_READINESS or readiness not in READINESS_OUTCOMES:
        raise AirportClassificationProfileError("FORBIDDEN_READINESS", "forbidden readiness outcome generated")

    system_result_doc = {
        "profileName": PROFILE_NAME,
        "profileId": PROFILE_ID,
        "profileVersion": PROFILE_VERSION,
        "authority": AUTHORITY,
        "implementationMode": IMPLEMENTATION_MODE,
        "platformCoreAirportized": False,
        "runId": run_id,
        "intakeEvidence": intake_meta,
        "spatialEvidence": spatial_meta,
        "classificationContext": context.serialize(),
        "candidates": sorted(system_candidates.values(), key=lambda item: item["classificationCandidateId"]),
        "readinessOutcome": readiness,
    }
    system_result_doc["resultDigest"] = sha256_digest({k: v for k, v in system_result_doc.items() if k != "resultDigest"})

    device_type_result_doc = {
        "profileName": PROFILE_NAME,
        "profileId": PROFILE_ID,
        "profileVersion": PROFILE_VERSION,
        "authority": AUTHORITY,
        "implementationMode": IMPLEMENTATION_MODE,
        "platformCoreAirportized": False,
        "runId": run_id,
        "intakeEvidence": intake_meta,
        "spatialEvidence": spatial_meta,
        "candidates": sorted(device_type_candidates.values(), key=lambda item: item["classificationCandidateId"]),
        "readinessOutcome": readiness,
    }
    device_type_result_doc["resultDigest"] = sha256_digest(
        {k: v for k, v in device_type_result_doc.items() if k != "resultDigest"}
    )

    aggregate_bindings = [
        {k: v for k, v in binding.items() if k != "sourceId"}
        for binding in device_bindings
    ]

    summary = {
        "authority": AUTHORITY,
        "containsCustomerAssetIdentifiers": False,
        "deviceCandidateCount": len(devices),
        "classifiedDeviceCount": classified_count,
        "unclassifiedDeviceCount": unclassified_count,
        "exactSystemMatchCount": exact_system,
        "approvedSystemAliasCount": approved_system_alias,
        "systemAliasCandidateCount": system_alias_candidate,
        "ambiguousSourceCodeCount": ambiguous_source,
        "systemColumnConflictCount": system_column_conflict,
        "exactDeviceTypeMatchCount": exact_type,
        "approvedDeviceTypeAliasCount": approved_type_alias,
        "deviceTypeAliasCandidateCount": type_alias_candidate,
        "unknownDeviceTypeCodeCount": unknown_type,
        "deviceTypeColumnConflictCount": type_column_conflict,
        "compatibleSystemDeviceCount": compatible_count,
        "unexpectedSystemDeviceCount": unexpected_count,
        "ambiguousSystemDeviceCount": ambiguous_compat,
        "duplicateClassificationAgreementCount": duplicate_agreement,
        "duplicateClassificationConflictCount": duplicate_conflict,
        "blockerCount": blocker_count,
        "reviewCount": review_count,
        "warningCount": warning_count,
        "readinessOutcome": readiness,
    }
    summary["resultDigest"] = sha256_digest({k: v for k, v in summary.items() if k != "resultDigest"})

    paths = {
        "airport-system-classification-result.json": system_result_doc,
        "airport-device-type-classification-result.json": device_type_result_doc,
        "airport-device-classification-bindings.json": aggregate_bindings,
        "airport-classification-review-findings.json": review_findings,
        "airport-classification-summary.json": summary,
    }

    for name, payload in paths.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    manifest = {
        "authority": AUTHORITY,
        "artifacts": [],
        "containsRawWorkbook": False,
    }
    for relative in paths:
        file_path = output_dir / relative
        manifest["artifacts"].append(
            {
                "artifactType": relative.replace(".json", "").upper().replace("-", "_"),
                "relativePath": relative,
                "sha256": hashlib.sha256(file_path.read_bytes()).hexdigest(),
                "containsCustomerAssetIdentifiers": relative == "airport-device-classification-bindings.json",
                "containsRawWorkbook": False,
                "retentionClass": "LOCAL_TMP_EVIDENCE",
            }
        )
    manifest_path = output_dir / "artifact-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "authority": AUTHORITY,
        "readinessOutcome": readiness,
        "resultDigest": summary["resultDigest"],
        "summary": summary,
        "manifestPath": str(manifest_path),
    }
