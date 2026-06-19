"""Airport spatial hierarchy mapping orchestration."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from ...reconciliation.models import sha256_digest
from .candidates import (
    build_airport_candidate,
    build_code_candidate,
    build_location_candidate,
    build_terminal_candidate,
    location_semantic_status,
    sheet_zone_finding,
)
from .constants import (
    AUTHORITY,
    FORBIDDEN_READINESS,
    GENERIC_RELATIONSHIP_SEMANTICS,
    GENERIC_TO_AIRPORT,
    IMPLEMENTATION_MODE,
    PROFILE_ID,
    PROFILE_NAME,
    READINESS_OUTCOMES,
)
from .context import AirportSpatialContext
from .errors import AirportSpatialProfileError
from .evidence import load_intake_evidence, verify_intake_evidence
from .validation import (
    build_parent_map,
    detect_hierarchy_cycles,
    detect_multiple_parent_conflicts,
    index_location_collisions,
    validate_device_spatial_fields,
)


def compare_deterministic_outputs(first: Path, second: Path) -> tuple[bool, str]:
    if not first.is_file() or not second.is_file():
        return False, "MISSING_OUTPUT"
    if first.read_bytes() == second.read_bytes():
        return True, "MATCH"
    return False, "MISMATCH"


def _relationship_candidate(
    *,
    profile_semantic: str,
    generic_semantic: str,
    from_type: str,
    from_key: str,
    to_type: str,
    to_key: str,
) -> dict[str, str]:
    if generic_semantic not in GENERIC_RELATIONSHIP_SEMANTICS:
        generic_semantic = "CONTAINS"
    return {
        "profileRelationshipLabel": profile_semantic,
        "genericRelationshipSemantic": generic_semantic,
        "fromProfileType": from_type,
        "fromCandidateKey": from_key,
        "toProfileType": to_type,
        "toCandidateKey": to_key,
    }


def run_airport_spatial_mapping(
    *,
    intake_evidence_path: Path,
    output_dir: Path,
    context: AirportSpatialContext,
    run_id: str,
    expected_workbook_digest: str | None = None,
    expected_intake_result_digest: str | None = None,
) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    evidence = load_intake_evidence(intake_evidence_path)
    intake_meta = verify_intake_evidence(
        evidence,
        expected_workbook_digest=expected_workbook_digest or context.source_workbook_digest,
        expected_result_digest=expected_intake_result_digest,
    )

    if context.source_workbook_digest and intake_meta["sourceWorkbookDigest"] != context.source_workbook_digest:
        raise AirportSpatialProfileError("CONTEXT_WORKBOOK_DIGEST_MISMATCH", "context workbook digest mismatch")

    spatial = evidence.get("spatialCandidates", {})
    devices = list(evidence.get("deviceCandidates", []))

    airport = build_airport_candidate(context)
    terminal = build_terminal_candidate(context, airport.candidate_key)

    candidate_map: dict[str, Any] = {
        airport.candidate_key: airport.serialize(),
        terminal.candidate_key: terminal.serialize(),
    }

    building_keys: dict[str, str] = {}
    for code in sorted(spatial.get("building", [])):
        normalized = str(code).strip().upper()
        candidate = build_code_candidate(
            context=context,
            candidate_type="BuildingCandidate",
            profile_label="Building",
            generic_target=GENERIC_TO_AIRPORT["Building"]["genericTarget"],
            normalized_code=normalized,
            parent_key=terminal.candidate_key,
            allowed_codes=context.allowed_building_codes,
        )
        candidate_map[candidate.candidate_key] = candidate.serialize()
        building_keys[normalized] = candidate.candidate_key

    level_keys: dict[str, str] = {}
    for code in sorted(spatial.get("level", [])):
        normalized = str(code).strip().upper()
        parent = building_keys.get(next(iter(building_keys), ""), terminal.candidate_key)
        if len(building_keys) == 1:
            parent = next(iter(building_keys.values()))
        candidate = build_code_candidate(
            context=context,
            candidate_type="LevelCandidate",
            profile_label="Level",
            generic_target=GENERIC_TO_AIRPORT["Level"]["genericTarget"],
            normalized_code=normalized,
            parent_key=parent,
            allowed_codes=context.allowed_level_codes,
        )
        candidate_map[candidate.candidate_key] = candidate.serialize()
        level_keys[normalized] = candidate.candidate_key

    zone_keys: dict[str, str] = {}
    for code in sorted(spatial.get("zone", [])):
        normalized = str(code).strip().upper()
        parent = next(iter(level_keys.values()), terminal.candidate_key)
        candidate = build_code_candidate(
            context=context,
            candidate_type="ZoneCandidate",
            profile_label="AirportZone",
            generic_target=GENERIC_TO_AIRPORT["AirportZone"]["genericTarget"],
            normalized_code=normalized,
            parent_key=parent,
            allowed_codes=context.allowed_zone_codes,
        )
        candidate_map[candidate.candidate_key] = candidate.serialize()
        zone_keys[normalized] = candidate.candidate_key

    da_keys: dict[str, str] = {}
    for code in sorted(spatial.get("distributionArea", [])):
        normalized = str(code).strip().upper()
        parent = next(iter(zone_keys.values()), terminal.candidate_key)
        candidate = build_code_candidate(
            context=context,
            candidate_type="DistributionAreaCandidate",
            profile_label="DistributionArea",
            generic_target=GENERIC_TO_AIRPORT["DistributionArea"]["genericTarget"],
            normalized_code=normalized,
            parent_key=parent,
            allowed_codes=context.allowed_distribution_area_codes,
        )
        candidate_map[candidate.candidate_key] = candidate.serialize()
        da_keys[normalized] = candidate.candidate_key

    location_collisions = index_location_collisions(devices)
    location_keys: dict[str, str] = {}
    for normalized_key in sorted(location_collisions):
        collision_group = sha256_digest({"normalizedLocationKey": normalized_key})
        semantic = location_semantic_status(normalized_key, len(location_collisions[normalized_key]))
        parent_da = next(iter(da_keys.values()), terminal.candidate_key)
        candidate = build_location_candidate(
            context=context,
            normalized_location_key=normalized_key,
            parent_da_key=parent_da,
            collision_group=collision_group,
            semantic_status=semantic,
        )
        candidate_map[candidate.candidate_key] = candidate.serialize()
        location_keys[normalized_key] = candidate.candidate_key

    review_findings: list[dict[str, Any]] = []
    device_bindings: list[dict[str, Any]] = []
    unbound_count = 0
    missing_building = missing_level = missing_zone = missing_da = missing_location = 0
    sheet_zone_mismatch_count = 0

    for device in devices:
        field_findings = validate_device_spatial_fields(device)
        review_findings.extend(field_findings)
        for finding in field_findings:
            cls = finding.get("classification", "")
            if cls == "MISSING_BUILDING":
                missing_building += 1
            elif cls == "MISSING_LEVEL":
                missing_level += 1
            elif cls == "MISSING_ZONE":
                missing_zone += 1
            elif cls == "MISSING_DISTRIBUTION_AREA":
                missing_da += 1
            elif cls == "LOCATION_MISSING":
                missing_location += 1

        worksheet = str(device.get("sourceWorksheet", ""))
        zone_code = str(device.get("zoneCode", "")).strip().upper()
        zone_finding = sheet_zone_finding(worksheet=worksheet, zone_code=zone_code)
        if zone_finding["classification"] == "SHEET_ZONE_MISMATCH":
            sheet_zone_mismatch_count += 1
        review_findings.append({**zone_finding, "rowNumber": device.get("sourceRowNumber")})

        building_key = building_keys.get(str(device.get("buildingCode", "")).strip().upper(), "")
        level_key = level_keys.get(str(device.get("levelCode", "")).strip().upper(), "")
        zone_key = zone_keys.get(zone_code, "")
        da_key = da_keys.get(str(device.get("distributionAreaCode", "")).strip().upper(), "")
        location_key = location_keys.get(str(device.get("normalizedLocation", "")).strip().upper(), "")

        binding = {
            "siteId": context.site_id,
            "airportContextId": context.airport_context_id,
            "terminalContextId": context.terminal_context_id,
            "buildingCandidateKey": building_key,
            "levelCandidateKey": level_key,
            "zoneCandidateKey": zone_key,
            "distributionAreaCandidateKey": da_key,
            "locationCandidateKey": location_key,
            "systemCandidateKey": sha256_digest(
                {"systemCode": str(device.get("sourceSystemCode", "")).strip().upper()}
            ),
            "sourceRowNumber": device.get("sourceRowNumber"),
            "sourceWorksheet": worksheet,
            "sourceDeviceDigest": sha256_digest({"sourceId": str(device.get("sourceId", ""))}),
            "bindingStatus": "BOUND" if all((building_key, level_key, zone_key, da_key)) else "PARTIAL",
        }
        if binding["bindingStatus"] != "BOUND":
            unbound_count += 1
            review_findings.append(
                {
                    "classification": "DEVICE_BINDING_INCOMPLETE",
                    "sourceDeviceDigest": binding["sourceDeviceDigest"],
                    "worksheet": worksheet,
                    "rowNumber": device.get("sourceRowNumber"),
                }
            )
        device_bindings.append(binding)

    relationships: list[dict[str, str]] = []
    relationships.append(
        _relationship_candidate(
            profile_semantic="Site REPRESENTS AirportContext",
            generic_semantic="CONTAINS",
            from_type="SiteCandidate",
            from_key=sha256_digest({"siteId": context.site_id}),
            to_type="AirportCandidate",
            to_key=airport.candidate_key,
        )
    )
    relationships.append(
        _relationship_candidate(
            profile_semantic="AirportContext CONTAINS Terminal",
            generic_semantic="CONTAINS",
            from_type="AirportCandidate",
            from_key=airport.candidate_key,
            to_type="TerminalCandidate",
            to_key=terminal.candidate_key,
        )
    )
    for candidate in candidate_map.values():
        ctype = candidate.get("candidateType", "")
        parent = candidate.get("parentCandidateKey", "")
        if parent and ctype.endswith("Candidate") and ctype not in {"AirportCandidate"}:
            relationships.append(
                _relationship_candidate(
                    profile_semantic=f"{ctype.replace('Candidate', '')} hierarchy",
                    generic_semantic="CONTAINS",
                    from_type="Parent",
                    from_key=parent,
                    to_type=str(ctype),
                    to_key=str(candidate.get("candidateKey", "")),
                )
            )

    for binding in device_bindings:
        if binding.get("locationCandidateKey"):
            relationships.append(
                _relationship_candidate(
                    profile_semantic="Device LOCATED_IN Location",
                    generic_semantic="LOCATED_IN",
                    from_type="Device",
                    from_key=str(binding["sourceDeviceDigest"]),
                    to_type="LocationCandidate",
                    to_key=str(binding["locationCandidateKey"]),
                )
            )
        if binding.get("distributionAreaCandidateKey"):
            relationships.append(
                _relationship_candidate(
                    profile_semantic="Device ASSIGNED_TO DistributionArea",
                    generic_semantic="ASSIGNED_TO",
                    from_type="Device",
                    from_key=str(binding["sourceDeviceDigest"]),
                    to_type="DistributionAreaCandidate",
                    to_key=str(binding["distributionAreaCandidateKey"]),
                )
            )

    parent_map = build_parent_map(list(candidate_map.values()))
    child_parents: dict[str, set[str]] = {}
    for child, parent in parent_map.items():
        child_parents.setdefault(child, set()).add(parent)
    multi_parent = detect_multiple_parent_conflicts(child_parents)
    review_findings.extend(multi_parent)
    cycles = detect_hierarchy_cycles(parent_map)

    if context.context_placeholders_present:
        review_findings.append(
            {
                "classification": "CONTEXT_PLACEHOLDER_REVIEW",
                "airportContextId": context.airport_context_id,
                "terminalContextId": context.terminal_context_id,
            }
        )

    review_findings.sort(key=lambda item: json.dumps(item, sort_keys=True))
    device_bindings.sort(key=lambda item: (str(item.get("sourceWorksheet", "")), int(item.get("sourceRowNumber", 0))))
    relationships.sort(key=lambda item: json.dumps(item, sort_keys=True))

    semantic_merge_pending = sum(
        1 for item in candidate_map.values()
        if item.get("candidateType") == "LocationCandidate"
        and "SEMANTIC_MERGE_NOT_APPROVED" in item.get("reviewReasons", [])
    )
    normalized_collision_count = sum(1 for _, ids in location_collisions.items() if len(ids) > 1)

    blocker_count = len(cycles) + len(multi_parent)
    review_count = len(review_findings)
    warning_count = sheet_zone_mismatch_count

    if cycles or multi_parent:
        readiness = "SPATIAL_MAPPING_BLOCKED"
    elif (
        context.context_placeholders_present
        or normalized_collision_count
        or sheet_zone_mismatch_count
        or unbound_count
        or review_findings
    ):
        readiness = "SPATIAL_MAPPING_COMPLETE_WITH_REVIEWS"
    else:
        readiness = "READY_FOR_AIRPORT_ASSET_RECONCILIATION"

    if readiness in FORBIDDEN_READINESS:
        raise AirportSpatialProfileError("FORBIDDEN_READINESS", "forbidden readiness outcome generated")

    summary = {
        "authority": AUTHORITY,
        "containsCustomerAssetIdentifiers": False,
        "airportContextCount": 1,
        "terminalCandidateCount": 1,
        "buildingCandidateCount": len(building_keys),
        "levelCandidateCount": len(level_keys),
        "zoneCandidateCount": len(zone_keys),
        "distributionAreaCandidateCount": len(da_keys),
        "locationCandidateCount": len(location_keys),
        "deviceBindingCount": len(device_bindings),
        "unboundDeviceCount": unbound_count,
        "missingBuildingCount": missing_building,
        "missingLevelCount": missing_level,
        "missingZoneCount": missing_zone,
        "missingDistributionAreaCount": missing_da,
        "missingLocationCount": missing_location,
        "sheetZoneMismatchCount": sheet_zone_mismatch_count,
        "multipleParentConflictCount": len(multi_parent),
        "hierarchyCycleCount": len(cycles),
        "normalizedLocationCollisionCount": normalized_collision_count,
        "semanticMergePendingCount": semantic_merge_pending,
        "blockerCount": blocker_count,
        "reviewCount": review_count,
        "warningCount": warning_count,
    }

    profile_result = {
        "profileName": PROFILE_NAME,
        "profileId": PROFILE_ID,
        "authority": AUTHORITY,
        "implementationMode": IMPLEMENTATION_MODE,
        "platformCoreAirportized": False,
        "runId": run_id,
        "intakeEvidence": intake_meta,
        "spatialContext": context.serialize(),
        "genericToAirportMapping": GENERIC_TO_AIRPORT,
        "candidates": sorted(candidate_map.values(), key=lambda item: item.get("candidateKey", "")),
        "relationshipCandidates": relationships,
        "readinessOutcome": readiness,
        "hierarchySummary": summary,
        "reviewFindingCount": review_count,
    }
    digest_material = {k: v for k, v in profile_result.items() if k != "resultDigest"}
    profile_result["resultDigest"] = sha256_digest(digest_material)

    result_path = output_dir / "airport-spatial-profile-result.json"
    summary_path = output_dir / "airport-spatial-hierarchy-summary.json"
    bindings_path = output_dir / "airport-device-spatial-bindings.json"
    reviews_path = output_dir / "airport-spatial-review-findings.json"

    result_path.write_text(json.dumps(profile_result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    bindings_path.write_text(json.dumps(device_bindings, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    reviews_path.write_text(json.dumps(review_findings, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    manifest = {
        "authority": AUTHORITY,
        "artifacts": [],
        "containsRawWorkbook": False,
    }
    for relative, contains_ids in (
        ("airport-spatial-profile-result.json", False),
        ("airport-spatial-hierarchy-summary.json", False),
        ("airport-device-spatial-bindings.json", True),
        ("airport-spatial-review-findings.json", False),
    ):
        file_path = output_dir / relative
        manifest["artifacts"].append(
            {
                "artifactType": relative.replace(".json", "").upper().replace("-", "_"),
                "relativePath": relative,
                "sha256": hashlib.sha256(file_path.read_bytes()).hexdigest(),
                "containsCustomerAssetIdentifiers": contains_ids,
                "containsRawWorkbook": False,
                "retentionClass": "LOCAL_TMP_EVIDENCE",
            }
        )
    manifest_path = output_dir / "artifact-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "authority": AUTHORITY,
        "readinessOutcome": readiness,
        "resultPath": str(result_path),
        "summaryPath": str(summary_path),
        "bindingsPath": str(bindings_path),
        "reviewsPath": str(reviews_path),
        "manifestPath": str(manifest_path),
        "resultDigest": profile_result["resultDigest"],
        "summary": summary,
    }
