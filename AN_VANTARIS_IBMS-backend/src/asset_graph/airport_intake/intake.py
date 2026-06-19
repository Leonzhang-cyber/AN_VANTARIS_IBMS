"""Airport asset Excel intake orchestration."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Optional

from ..reconciliation.models import sha256_digest
from .constants import (
    ASSET_MASTER_COLUMNS,
    AUTHORITY,
    EVIDENCE_CLASSIFICATION,
    EVIDENCE_NAME,
    EVIDENCE_VERSION,
    EXECUTION_MODE,
    EXPECTED_SOURCE_PROFILE,
    FORBIDDEN_READINESS_OUTCOMES,
    MAINTENANCE_EXTENSION_COLUMNS,
    PLACEHOLDER_AIRPORT,
    PLACEHOLDER_TERMINAL,
    REQUIRED_ASSET_COLUMNS,
    REQUIRED_WORKSHEETS,
    WEEKDAY_TOKENS,
)
from .device_id import compare_parsed_to_columns, parse_device_id
from .errors import AirportIntakeError
from .location import candidate_display_name, normalize_location
from .privacy import scan_row
from .system_aliases import evaluate_system_alias, normalize_system_code
from .workbook import AirportExcelWorkbook


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _non_empty_fields(record: Mapping[str, Any], columns: tuple[str, ...]) -> dict[str, Any]:
    return {
        column: record[column]
        for column in columns
        if column in record and record[column] not in (None, "")
    }


def _classify_day_value(day_value: str, location_value: str) -> Optional[str]:
    token = day_value.strip().upper()
    if not token:
        return None
    if token in WEEKDAY_TOKENS:
        return None
    location_key = normalize_location(location_value)[1]
    day_key = normalize_location(day_value)[1]
    if day_key and location_key and day_key == location_key:
        return "MAINTENANCE_DAY_SEMANTIC_AMBIGUITY"
    if len(token.split()) >= 2 and not any(part in WEEKDAY_TOKENS for part in token.split()):
        return "MAINTENANCE_DAY_SEMANTIC_AMBIGUITY"
    return None


def _sheet_zone_hint(sheet_name: str) -> str:
    if sheet_name == "Zone-1":
        return "Z1"
    if sheet_name == "Zone-2":
        return "Z2"
    return ""


def _validate_required_columns(headers: set[str]) -> None:
    missing = [column for column in REQUIRED_ASSET_COLUMNS if column not in headers]
    if missing:
        raise AirportIntakeError("MISSING_REQUIRED_COLUMNS", f"missing required asset columns: {', '.join(missing)}")


def _workbook_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifact_manifest(
    *,
    output_dir: Path,
    evidence_path: Path,
    aggregate_path: Path,
) -> dict[str, Any]:
    artifacts = []
    for relative, contains_ids, contains_raw in (
        ("airport-asset-intake-evidence.json", True, False),
        ("airport-asset-data-quality-summary.json", False, False),
    ):
        file_path = output_dir / relative
        artifacts.append(
            {
                "artifactType": relative.replace(".json", "").upper().replace("-", "_"),
                "relativePath": relative,
                "sha256": hashlib.sha256(file_path.read_bytes()).hexdigest(),
                "containsCustomerAssetIdentifiers": contains_ids,
                "containsRawWorkbook": contains_raw,
                "retentionClass": "LOCAL_TMP_EVIDENCE",
            }
        )
    manifest = {
        "authority": AUTHORITY,
        "artifacts": artifacts,
        "containsRawWorkbook": False,
    }
    manifest_path = output_dir / "artifact-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest["manifestPath"] = str(manifest_path)
    return manifest


def run_airport_asset_excel_intake(
    *,
    input_path: Path,
    output_dir: Path,
    airport_context_id: str,
    terminal_context_id: str,
    run_id: str,
    fail_on_blocker: bool = False,
    fail_on_review: bool = False,
) -> dict[str, Any]:
    input_path = input_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.is_file():
        raise AirportIntakeError("WORKBOOK_NOT_FOUND", "source workbook was not found at operator path")

    with AirportExcelWorkbook.open(input_path) as book:
        worksheet_rows: dict[str, list[tuple[int, dict[str, Any]]]] = {}
        for sheet in REQUIRED_WORKSHEETS:
            worksheet_rows[sheet] = book.rows_with_row_numbers(sheet)

    all_headers: set[str] = set()
    for rows in worksheet_rows.values():
        if rows:
            all_headers.update(rows[0][1].keys())
    _validate_required_columns(all_headers)

    privacy_findings: list[dict[str, str | int]] = []
    rejected_rows: list[dict[str, Any]] = []
    accepted_rows: list[dict[str, Any]] = []
    device_candidates: list[dict[str, Any]] = []
    maintenance_candidates: list[dict[str, Any]] = []
    duplicate_findings: list[dict[str, Any]] = []
    mapping_findings: list[dict[str, Any]] = []
    system_alias_candidates: list[dict[str, Any]] = []
    system_code_mismatch_findings: list[dict[str, Any]] = []
    sheet_zone_inconsistencies: list[dict[str, Any]] = []
    maintenance_ambiguities: list[dict[str, Any]] = []
    legacy_field_reviews: list[dict[str, Any]] = []

    device_id_index: dict[str, list[dict[str, Any]]] = {}
    sl_index: dict[str, list[dict[str, Any]]] = {}
    location_index: dict[str, list[str]] = {}

    spatial_sets = {
        "airport": set(),
        "terminal": set(),
        "building": set(),
        "level": set(),
        "zone": set(),
        "distributionArea": set(),
        "location": set(),
    }
    system_codes: set[str] = set()
    device_types: set[str] = set()

    source_row_count = 0
    accepted_row_count = 0
    rejected_row_count = 0
    missing_counts = {key: 0 for key in (
        "deviceId", "building", "level", "zone", "system", "location", "deviceType",
    )}

    for sheet_name, rows in worksheet_rows.items():
        sheet_hint = _sheet_zone_hint(sheet_name)
        for row_number, record in rows:
            source_row_count += 1
            privacy = scan_row(worksheet=sheet_name, row_number=row_number, record=record)
            if privacy:
                privacy_findings.extend(privacy)
                raise AirportIntakeError(
                    "PRIVACY_BLOCKED",
                    "credential or private material detected in source workbook",
                )

            unknown_headers = [
                header for header in record
                if header not in ASSET_MASTER_COLUMNS + MAINTENANCE_EXTENSION_COLUMNS
            ]
            for header in unknown_headers:
                legacy_field_reviews.append(
                    {
                        "classification": "LEGACY_FIELD_REVIEW_REQUIRED",
                        "worksheet": sheet_name,
                        "rowNumber": row_number,
                        "fieldName": header,
                    }
                )

            device_id = _stringify(record.get("Device ID"))
            building = _stringify(record.get("Building"))
            level = _stringify(record.get("Level"))
            zone = _stringify(record.get("Zone"))
            da = _stringify(record.get("DA"))
            system = _stringify(record.get("System"))
            area = _stringify(record.get("Area"))
            location = _stringify(record.get("Location"))
            device_type = _stringify(record.get("Device Type"))
            sl = _stringify(record.get("SL"))

            if not device_id:
                missing_counts["deviceId"] += 1
            if not building:
                missing_counts["building"] += 1
            if not level:
                missing_counts["level"] += 1
            if not zone:
                missing_counts["zone"] += 1
            if not system:
                missing_counts["system"] += 1
            if not location:
                missing_counts["location"] += 1
            if not device_type:
                missing_counts["deviceType"] += 1

            if sheet_hint and zone and zone.upper() != sheet_hint:
                sheet_zone_inconsistencies.append(
                    {
                        "worksheet": sheet_name,
                        "rowNumber": row_number,
                        "sheetZoneHint": sheet_hint,
                        "rowZoneValue": zone,
                        "classification": "SHEET_ZONE_INCONSISTENCY",
                    }
                )

            raw_location, normalized_location = normalize_location(location)
            if normalized_location:
                location_index.setdefault(normalized_location, []).append(device_id or f"ROW-{row_number}")

            parse_result = parse_device_id(device_id)
            column_agreement = compare_parsed_to_columns(
                parse_result,
                building=building,
                level=level,
                distribution_area=da,
                system=system,
            )
            mapping_findings.append(
                {
                    "worksheet": sheet_name,
                    "rowNumber": row_number,
                    "deviceIdParse": {
                        "parsedSuccessfully": parse_result.parsed_successfully,
                        "partiallyParsed": parse_result.partially_parsed,
                        "unparseable": parse_result.unparseable,
                        "parsePattern": parse_result.parse_pattern,
                    },
                    "columnComparison": column_agreement,
                }
            )

            alias_eval = evaluate_system_alias(
                column_system=system,
                embedded_system=parse_result.segments.get("embeddedSystemCode"),
            )
            alias_entry = {
                "worksheet": sheet_name,
                "rowNumber": row_number,
                **alias_eval,
            }
            if alias_eval["status"] == "KNOWN_ALIAS_CANDIDATE":
                system_alias_candidates.append(alias_entry)
            elif alias_eval["status"] in {"COLUMN_ID_CONFLICT", "UNMAPPED_CODE"}:
                system_code_mismatch_findings.append(alias_entry)

            maintenance_fields = _non_empty_fields(record, MAINTENANCE_EXTENSION_COLUMNS)
            if maintenance_fields:
                maintenance_candidates.append(
                    {
                        "worksheet": sheet_name,
                        "rowNumber": row_number,
                        "sourceDeviceId": device_id,
                        "fields": maintenance_fields,
                    }
                )
                day_ambiguity = _classify_day_value(
                    _stringify(record.get("Day")),
                    location,
                )
                if day_ambiguity:
                    maintenance_ambiguities.append(
                        {
                            "worksheet": sheet_name,
                            "rowNumber": row_number,
                            "classification": day_ambiguity,
                        }
                    )

            display_name = candidate_display_name(device_type, location)
            candidate = {
                "sourceId": device_id,
                "deviceCode": device_id,
                "buildingCode": building,
                "levelCode": level,
                "zoneCode": zone,
                "distributionAreaCode": da,
                "sourceSystemCode": system,
                "areaName": area,
                "locationName": location,
                "rawLocation": raw_location,
                "normalizedLocation": normalized_location,
                "sourceDeviceType": device_type,
                "sourceWorksheet": sheet_name,
                "sourceRowNumber": row_number,
                "sourceSequence": sl,
                "candidateDisplayName": display_name,
                "assetMasterFields": _non_empty_fields(record, ASSET_MASTER_COLUMNS),
                "maintenanceExtensionFieldCount": len(maintenance_fields),
            }
            device_candidates.append(candidate)
            accepted_rows.append({"worksheet": sheet_name, "rowNumber": row_number})
            accepted_row_count += 1

            if device_id:
                device_id_index.setdefault(device_id, []).append(
                    {"worksheet": sheet_name, "rowNumber": row_number, "candidate": candidate}
                )
            if sl:
                sl_index.setdefault(sl, []).append({"worksheet": sheet_name, "rowNumber": row_number, "deviceId": device_id})

            spatial_sets["airport"].add(airport_context_id)
            spatial_sets["terminal"].add(terminal_context_id)
            if building:
                spatial_sets["building"].add(building.upper())
            if level:
                spatial_sets["level"].add(level.upper())
            if zone:
                spatial_sets["zone"].add(zone.upper())
            if da:
                spatial_sets["distributionArea"].add(da.upper())
            if normalized_location:
                spatial_sets["location"].add(normalized_location)
            if system:
                system_codes.add(normalize_system_code(system))
            if device_type:
                device_types.add(device_type.upper())

    if privacy_findings:
        readiness = "INTAKE_BLOCKED"
    else:
        readiness = "INTAKE_COMPLETE_WITH_REVIEWS"
        if (
            not duplicate_findings
            and not system_alias_candidates
            and not maintenance_ambiguities
            and airport_context_id != PLACEHOLDER_AIRPORT
            and terminal_context_id != PLACEHOLDER_TERMINAL
            and not sheet_zone_inconsistencies
        ):
            readiness = "READY_FOR_AIRPORT_ASSET_RECONCILIATION"

    for device_id, occurrences in device_id_index.items():
        if len(occurrences) <= 1:
            continue
        worksheets = {item["worksheet"] for item in occurrences}
        signatures = [
            json.dumps(
                {key: value for key, value in item["candidate"]["assetMasterFields"].items() if key != "SL"},
                sort_keys=True,
            )
            for item in occurrences
        ]
        if len(set(signatures)) == 1:
            classification = "DUPLICATE_SOURCE_IDENTITY_IDENTICAL"
        else:
            classification = "DUPLICATE_SOURCE_IDENTITY_CONFLICT"
        duplicate_findings.append(
            {
                "classification": classification,
                "deviceId": device_id,
                "occurrenceCount": len(occurrences),
                "worksheets": sorted(worksheets),
                "crossWorksheet": len(worksheets) > 1,
            }
        )

    for sl_value, occurrences in sl_index.items():
        device_ids = {item["deviceId"] for item in occurrences}
        if len(occurrences) > 1:
            duplicate_findings.append(
                {
                    "classification": "DUPLICATE_ROW_REVIEW",
                    "field": "SL",
                    "value": sl_value,
                    "occurrenceCount": len(occurrences),
                    "distinctDeviceIds": len(device_ids),
                }
            )

    for normalized_location, device_ids in location_index.items():
        unique_ids = {item for item in device_ids if item}
        if len(unique_ids) > 1:
            duplicate_findings.append(
                {
                    "classification": "NORMALIZED_LOCATION_COLLISION",
                    "normalizedLocation": normalized_location,
                    "deviceIdCount": len(unique_ids),
                }
            )

    relationship_candidates = _build_relationship_candidates(
        airport_context_id=airport_context_id,
        terminal_context_id=terminal_context_id,
        device_candidates=device_candidates,
        spatial_sets=spatial_sets,
    )

    source_profile = _build_source_profile(
        worksheet_rows=worksheet_rows,
        system_codes=system_codes,
        spatial_sets=spatial_sets,
    )

    blocker_count = len(privacy_findings) + sum(
        1 for item in duplicate_findings if item["classification"] == "DUPLICATE_SOURCE_IDENTITY_CONFLICT"
    )
    review_count = (
        len(system_alias_candidates)
        + len(maintenance_ambiguities)
        + len(sheet_zone_inconsistencies)
        + len(legacy_field_reviews)
        + sum(1 for item in duplicate_findings if item["classification"] != "DUPLICATE_SOURCE_IDENTITY_CONFLICT")
    )
    warning_count = len(system_code_mismatch_findings)

    if duplicate_findings or system_alias_candidates or maintenance_ambiguities:
        readiness = "INTAKE_COMPLETE_WITH_REVIEWS"
    if airport_context_id == PLACEHOLDER_AIRPORT or terminal_context_id == PLACEHOLDER_TERMINAL:
        readiness = "INTAKE_COMPLETE_WITH_REVIEWS"

    aggregate = _build_aggregate_summary(
        worksheet_count=len(REQUIRED_WORKSHEETS),
        source_row_count=source_row_count,
        accepted_row_count=accepted_row_count,
        rejected_row_count=rejected_row_count,
        device_candidates=device_candidates,
        duplicate_findings=duplicate_findings,
        spatial_sets=spatial_sets,
        system_codes=system_codes,
        device_types=device_types,
        system_alias_candidates=system_alias_candidates,
        system_code_mismatch_findings=system_code_mismatch_findings,
        missing_counts=missing_counts,
        maintenance_candidates=maintenance_candidates,
        maintenance_ambiguities=maintenance_ambiguities,
        blocker_count=blocker_count,
        review_count=review_count,
        warning_count=warning_count,
    )

    evidence_core = {
        "evidenceName": EVIDENCE_NAME,
        "evidenceVersion": EVIDENCE_VERSION,
        "authority": AUTHORITY,
        "evidenceClassification": EVIDENCE_CLASSIFICATION,
        "executionMode": EXECUTION_MODE,
        "runId": run_id,
        "sourceWorkbook": {
            "fileName": input_path.name,
            "sha256": _workbook_digest(input_path),
            "worksheetNames": list(REQUIRED_WORKSHEETS),
            "containsRawWorkbook": False,
        },
        "sourceProfile": source_profile,
        "worksheetSummary": {
            sheet: {"sourceRowCount": len(rows), "acceptedRowCount": len(rows)}
            for sheet, rows in worksheet_rows.items()
        },
        "spatialCandidates": _spatial_candidates(spatial_sets),
        "systemCandidates": sorted(system_codes),
        "deviceCandidates": device_candidates,
        "maintenanceExtensionCandidates": maintenance_candidates,
        "relationshipCandidates": relationship_candidates,
        "duplicateFindings": duplicate_findings,
        "mappingFindings": mapping_findings,
        "systemAliasCandidates": system_alias_candidates,
        "systemCodeMismatchFindings": system_code_mismatch_findings,
        "sheetZoneInconsistencies": sheet_zone_inconsistencies,
        "maintenanceAmbiguities": maintenance_ambiguities,
        "legacyFieldReviews": legacy_field_reviews,
        "dataQualitySummary": aggregate,
        "privacySummary": {
            "findingCount": len(privacy_findings),
            "findings": privacy_findings,
            "blockedIntake": bool(privacy_findings),
        },
        "readinessSummary": {
            "outcome": readiness,
            "forbiddenOutcomesExcluded": sorted(FORBIDDEN_READINESS_OUTCOMES),
            "blockerCount": blocker_count,
            "reviewCount": review_count,
            "warningCount": warning_count,
            "airportContextId": airport_context_id,
            "terminalContextId": terminal_context_id,
            "contextPlaceholdersPresent": (
                airport_context_id == PLACEHOLDER_AIRPORT or terminal_context_id == PLACEHOLDER_TERMINAL
            ),
        },
        "pointTelemetryAlarmRule": {
            "deviceCandidateCount": len(device_candidates),
            "pointCandidateCount": 0,
            "telemetryRecordCount": 0,
            "alarmRecordCount": 0,
            "syntheticPointsGenerated": False,
        },
    }
    digest_material = {k: v for k, v in evidence_core.items()}
    evidence_core["resultDigest"] = sha256_digest(digest_material)

    evidence_path = output_dir / "airport-asset-intake-evidence.json"
    aggregate_path = output_dir / "airport-asset-data-quality-summary.json"
    evidence_path.write_text(json.dumps(evidence_core, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    aggregate_path.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = build_artifact_manifest(
        output_dir=output_dir,
        evidence_path=evidence_path,
        aggregate_path=aggregate_path,
    )

    if fail_on_blocker and blocker_count > 0:
        raise AirportIntakeError("BLOCKERS_PRESENT", f"{blocker_count} blocker(s) present")
    if fail_on_review and review_count > 0:
        raise AirportIntakeError("REVIEWS_PRESENT", f"{review_count} review item(s) present")

    return {
        "authority": AUTHORITY,
        "readinessOutcome": readiness,
        "evidencePath": str(evidence_path),
        "aggregatePath": str(aggregate_path),
        "manifestPath": str(output_dir / "artifact-manifest.json"),
        "resultDigest": evidence_core["resultDigest"],
        "blockerCount": blocker_count,
        "reviewCount": review_count,
        "sourceProfile": source_profile,
        "aggregateSummary": aggregate,
        "privacyBlocked": bool(privacy_findings),
    }


def _spatial_candidates(spatial_sets: dict[str, set[str]]) -> dict[str, list[str]]:
    return {key: sorted(values) for key, values in spatial_sets.items()}


def _build_relationship_candidates(
    *,
    airport_context_id: str,
    terminal_context_id: str,
    device_candidates: list[dict[str, Any]],
    spatial_sets: dict[str, set[str]],
) -> list[dict[str, str]]:
    relationships: list[dict[str, str]] = []
    for building in spatial_sets["building"]:
        relationships.append(
            {"relationshipType": "CONTAINS", "fromType": "Terminal", "fromId": terminal_context_id, "toType": "Building", "toId": building}
        )
    for level in spatial_sets["level"]:
        for building in spatial_sets["building"]:
            relationships.append(
                {"relationshipType": "CONTAINS", "fromType": "Building", "fromId": building, "toType": "Level", "toId": level}
            )
    for zone in spatial_sets["zone"]:
        for level in spatial_sets["level"]:
            relationships.append(
                {"relationshipType": "CONTAINS", "fromType": "Level", "fromId": level, "toType": "Zone", "toId": zone}
            )
    for da in spatial_sets["distributionArea"]:
        for zone in spatial_sets["zone"]:
            relationships.append(
                {"relationshipType": "CONTAINS", "fromType": "Zone", "fromId": zone, "toType": "DistributionArea", "toId": da}
            )
    for location in spatial_sets["location"]:
        for da in spatial_sets["distributionArea"]:
            relationships.append(
                {"relationshipType": "CONTAINS", "fromType": "DistributionArea", "fromId": da, "toType": "Location", "toId": location}
            )
    relationships.append(
        {"relationshipType": "CONTAINS", "fromType": "Airport", "fromId": airport_context_id, "toType": "Terminal", "toId": terminal_context_id}
    )
    seen: set[tuple[str, ...]] = set()
    for candidate in device_candidates:
        for rel_type, to_type, to_id in (
            ("LOCATED_IN", "Location", candidate.get("normalizedLocation", "")),
            ("BELONGS_TO", "System", normalize_system_code(candidate.get("sourceSystemCode", ""))),
            ("ASSIGNED_TO", "DistributionArea", candidate.get("distributionAreaCode", "").upper()),
        ):
            if not to_id:
                continue
            key = (rel_type, candidate.get("sourceId", ""), to_type, to_id)
            if key in seen:
                relationships.append(
                    {
                        "relationshipType": rel_type,
                        "fromType": "Device",
                        "fromId": candidate.get("sourceId", ""),
                        "toType": to_type,
                        "toId": to_id,
                        "classification": "RELATIONSHIP_DUPLICATE_CANDIDATE",
                    }
                )
                continue
            seen.add(key)
            relationships.append(
                {
                    "relationshipType": rel_type,
                    "fromType": "Device",
                    "fromId": candidate.get("sourceId", ""),
                    "toType": to_type,
                    "toId": to_id,
                }
            )
    return relationships


def _build_source_profile(
    *,
    worksheet_rows: dict[str, list[tuple[int, dict[str, Any]]]],
    system_codes: set[str],
    spatial_sets: dict[str, set[str]],
) -> dict[str, Any]:
    actual_rows = sum(len(rows) for rows in worksheet_rows.values())
    distribution = {sheet: len(rows) for sheet, rows in worksheet_rows.items()}
    profile_checks: list[dict[str, Any]] = []

    def _check(name: str, actual: Any, expected: Any) -> None:
        status = "MATCH" if actual == expected else "SOURCE_PROFILE_CHANGED_REVIEW_REQUIRED"
        profile_checks.append({"check": name, "expected": expected, "actual": actual, "status": status})

    _check("assetRowsApprox", actual_rows, EXPECTED_SOURCE_PROFILE["assetRowsApprox"])
    for sheet, expected_count in EXPECTED_SOURCE_PROFILE["worksheetDistribution"].items():
        _check(f"worksheetRows:{sheet}", distribution.get(sheet, 0), expected_count)
    _check("systems", sorted(system_codes), sorted(EXPECTED_SOURCE_PROFILE["expectedSystems"]))
    _check("buildings", sorted(spatial_sets["building"]), sorted(EXPECTED_SOURCE_PROFILE["expectedBuildings"]))
    _check("levels", sorted(spatial_sets["level"]), sorted(EXPECTED_SOURCE_PROFILE["expectedLevels"]))
    _check("zones", sorted(spatial_sets["zone"]), sorted(EXPECTED_SOURCE_PROFILE["expectedZones"]))
    _check(
        "distributionAreas",
        sorted(spatial_sets["distributionArea"]),
        sorted(EXPECTED_SOURCE_PROFILE["expectedDistributionAreas"]),
    )

    return {
        "actualAssetRowCount": actual_rows,
        "worksheetDistribution": distribution,
        "observedSystems": sorted(system_codes),
        "observedBuildings": sorted(spatial_sets["building"]),
        "observedLevels": sorted(spatial_sets["level"]),
        "observedZones": sorted(spatial_sets["zone"]),
        "observedDistributionAreas": sorted(spatial_sets["distributionArea"]),
        "profileChecks": profile_checks,
    }


def _build_aggregate_summary(
    *,
    worksheet_count: int,
    source_row_count: int,
    accepted_row_count: int,
    rejected_row_count: int,
    device_candidates: list[dict[str, Any]],
    duplicate_findings: list[dict[str, Any]],
    spatial_sets: dict[str, set[str]],
    system_codes: set[str],
    device_types: set[str],
    system_alias_candidates: list[dict[str, Any]],
    system_code_mismatch_findings: list[dict[str, Any]],
    missing_counts: dict[str, int],
    maintenance_candidates: list[dict[str, Any]],
    maintenance_ambiguities: list[dict[str, Any]],
    blocker_count: int,
    review_count: int,
    warning_count: int,
) -> dict[str, Any]:
    unique_device_ids = {c.get("sourceId") for c in device_candidates if c.get("sourceId")}
    duplicate_device_id_count = sum(
        1 for item in duplicate_findings if "deviceId" in item
    )
    conflicting_duplicate_count = sum(
        1 for item in duplicate_findings if item.get("classification") == "DUPLICATE_SOURCE_IDENTITY_CONFLICT"
    )
    return {
        "authority": AUTHORITY,
        "containsCustomerAssetIdentifiers": False,
        "worksheetCount": worksheet_count,
        "sourceRowCount": source_row_count,
        "acceptedRowCount": accepted_row_count,
        "rejectedRowCount": rejected_row_count,
        "deviceCandidateCount": len(device_candidates),
        "uniqueDeviceIdCount": len(unique_device_ids),
        "duplicateDeviceIdCount": duplicate_device_id_count,
        "conflictingDuplicateCount": conflicting_duplicate_count,
        "buildingCount": len(spatial_sets["building"]),
        "levelCount": len(spatial_sets["level"]),
        "zoneCount": len(spatial_sets["zone"]),
        "distributionAreaCount": len(spatial_sets["distributionArea"]),
        "locationCandidateCount": len(spatial_sets["location"]),
        "systemCodeCount": len(system_codes),
        "deviceTypeCount": len(device_types),
        "systemAliasCandidateCount": len(system_alias_candidates),
        "systemCodeConflictCount": len(system_code_mismatch_findings),
        "missingDeviceIdCount": missing_counts["deviceId"],
        "missingBuildingCount": missing_counts["building"],
        "missingLevelCount": missing_counts["level"],
        "missingZoneCount": missing_counts["zone"],
        "missingSystemCount": missing_counts["system"],
        "missingLocationCount": missing_counts["location"],
        "missingDeviceTypeCount": missing_counts["deviceType"],
        "maintenanceCandidateCount": len(maintenance_candidates),
        "ambiguousMaintenanceFieldCount": len(maintenance_ambiguities),
        "pointCandidateCount": 0,
        "telemetryRecordCount": 0,
        "alarmRecordCount": 0,
        "blockerCount": blocker_count,
        "reviewCount": review_count,
        "warningCount": warning_count,
    }


def compare_deterministic_outputs(first: Path, second: Path) -> tuple[bool, str]:
    if not first.is_file() or not second.is_file():
        return False, "MISSING_OUTPUT"
    if first.read_bytes() == second.read_bytes():
        return True, "MATCH"
    return False, "MISMATCH"
