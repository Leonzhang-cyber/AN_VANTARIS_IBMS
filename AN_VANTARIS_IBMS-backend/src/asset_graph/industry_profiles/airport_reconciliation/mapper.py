"""Airport asset reconciliation orchestration."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from ...reconciliation.models import sha256_digest
from .constants import (
    AUTHORITY,
    FORBIDDEN_READINESS,
    IMPLEMENTATION_MODE,
    PROFILE_ID,
    PROFILE_NAME,
    PROFILE_VERSION,
    READINESS_OUTCOMES,
)
from .context import AirportReconciliationContext
from .decisions import (
    build_location_groups,
    canonical_proposal_decision,
    classification_decision,
    device_candidate_digest,
    duplicate_group_digest,
    evaluate_duplicate_group,
    identity_decision,
    location_group_status_for_device,
    source_identity_digest,
    source_row_digest,
    source_worksheet_digest,
    spatial_decision,
    classify_label,
)
from .errors import AirportReconciliationProfileError
from .evidence import load_json, verify_input_bundle
from .gates import evaluate_readiness_gates
from .packages import build_alias_approval_package


def compare_deterministic_outputs(first: Path, second: Path) -> tuple[bool, str]:
    if not first.is_file() or not second.is_file():
        return False, "MISSING_OUTPUT"
    if first.read_bytes() == second.read_bytes():
        return True, "MATCH"
    return False, "MISMATCH"


def _index_bindings(bindings: list[Mapping[str, Any]]) -> dict[tuple[str, int], dict[str, Any]]:
    indexed: dict[tuple[str, int], dict[str, Any]] = {}
    for binding in bindings:
        key = (str(binding.get("sourceWorksheet", "")), int(binding.get("sourceRowNumber", 0)))
        indexed[key] = dict(binding)
    return indexed


def _aggregate_reviews(
    *,
    duplicate_groups: list[dict[str, Any]],
    alias_proposals: list[dict[str, Any]],
    location_groups: list[dict[str, Any]],
    context_placeholders_present: bool,
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    findings: list[dict[str, Any]] = []
    causes: set[str] = set()

    for group in duplicate_groups:
        if group.get("requiresCanonicalWinnerDecision") or "CONFLICT" in str(group.get("duplicateGroupStatus", "")):
            cause = f"DUPLICATE_GROUP:{group['duplicateGroupDigest']}"
            causes.add(cause)
            findings.append(
                {
                    "classification": group["duplicateGroupStatus"],
                    "reviewScope": "GROUP",
                    "reviewCauseId": cause,
                    "affectedRecordCount": group["memberCount"],
                    "duplicateGroupDigest": group["duplicateGroupDigest"],
                    "reviewReasons": group.get("reviewReasons", []),
                }
            )

    for proposal in alias_proposals:
        cause = f"{proposal['proposalType']}:{proposal['proposalId']}"
        causes.add(cause)
        findings.append(
            {
                "classification": proposal["proposalType"],
                "reviewScope": "GROUP",
                "reviewCauseId": cause,
                "affectedRecordCount": proposal["affectedRecordCount"],
                "proposalId": proposal["proposalId"],
                "decisionStatus": proposal["decisionStatus"],
            }
        )

    for group in location_groups:
        if group.get("locationReconciliationStatus") == "NORMALIZED_LOCATION_TEXT_COLLISION":
            cause = f"LOCATION_GROUP:{group['locationGroupDigest']}"
            causes.add(cause)
            findings.append(
                {
                    "classification": "NORMALIZED_LOCATION_TEXT_COLLISION",
                    "reviewScope": "GROUP",
                    "reviewCauseId": cause,
                    "affectedRecordCount": group["memberCount"],
                    "locationGroupDigest": group["locationGroupDigest"],
                }
            )

    if context_placeholders_present:
        cause = "CONTEXT_PLACEHOLDER"
        causes.add(cause)
        findings.append(
            {
                "classification": "CONTEXT_PLACEHOLDER_REVIEW",
                "reviewScope": "GROUP",
                "reviewCauseId": cause,
                "affectedRecordCount": len(records),
            }
        )

    record_level = sum(1 for record in records if record.get("reviewReasons"))
    findings.sort(key=lambda item: json.dumps(item, sort_keys=True))
    metrics = {
        "recordLevelReviewCount": record_level,
        "groupLevelReviewCount": len(findings),
        "uniqueReviewCauseCount": len(causes),
        "affectedRecordCount": len(records),
    }
    return findings, metrics


def run_airport_asset_reconciliation(
    *,
    intake_evidence_path: Path,
    spatial_result_path: Path,
    spatial_bindings_path: Path,
    system_classification_path: Path,
    device_type_classification_path: Path,
    classification_bindings_path: Path,
    classification_reviews_path: Path,
    classification_summary_path: Path,
    coverage_analysis_path: Path,
    output_dir: Path,
    context: AirportReconciliationContext,
    run_id: str,
) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    intake = load_json(intake_evidence_path)
    spatial_result = load_json(spatial_result_path)
    spatial_bindings = load_json(spatial_bindings_path)
    system_classification = load_json(system_classification_path)
    device_type_classification = load_json(device_type_classification_path)
    classification_bindings = load_json(classification_bindings_path)
    classification_reviews = load_json(classification_reviews_path)
    classification_summary = load_json(classification_summary_path)
    coverage_analysis = load_json(coverage_analysis_path)

    if not isinstance(spatial_bindings, list) or not isinstance(classification_bindings, list):
        raise AirportReconciliationProfileError("BINDINGS_INVALID", "bindings payloads must be lists")

    verification = verify_input_bundle(
        intake=intake,
        spatial_result=spatial_result,
        spatial_bindings=spatial_bindings,
        system_classification=system_classification,
        device_type_classification=device_type_classification,
        classification_bindings=classification_bindings,
        classification_reviews=classification_reviews,
        classification_summary=classification_summary,
        coverage_analysis=coverage_analysis,
        context_workbook_digest=context.source_workbook_digest,
    )

    devices = list(intake.get("deviceCandidates", []))
    spatial_by_row = _index_bindings(spatial_bindings)
    class_by_row = _index_bindings(classification_bindings)
    workbook_digest = verification["sourceWorkbookDigest"]
    context_placeholders_present = bool(spatial_result.get("spatialContext", {}).get("contextPlaceholdersPresent"))

    location_summary = build_location_groups(devices, spatial_by_row)
    location_groups = location_summary["groups"]

    identity_groups: dict[str, list[dict[str, Any]]] = {}
    for device in devices:
        source_id = str(device.get("sourceId", ""))
        key = (str(device.get("sourceWorksheet", "")), int(device.get("sourceRowNumber", 0)))
        spatial = spatial_by_row.get(key, {})
        classification = class_by_row.get(key, {})
        identity_groups.setdefault(source_id, []).append(
            {
                **device,
                "deviceCandidateDigest": device_candidate_digest(device),
                "locationCandidateKey": str(spatial.get("locationCandidateKey", "")),
                "systemMappingStatus": str(classification.get("systemMappingStatus", "")),
                "deviceTypeMappingStatus": str(classification.get("deviceTypeMappingStatus", "")),
                "genericSystemCategory": str(classification.get("genericSystemCategory", "")),
                "genericDeviceClass": str(classification.get("genericDeviceClass", "")),
                "maintenanceExtensionFieldCount": int(device.get("maintenanceExtensionFieldCount", 0)),
            }
        )

    duplicate_groups: list[dict[str, Any]] = []
    duplicate_group_by_identity: dict[str, dict[str, Any]] = {}
    for source_id in sorted(identity_groups):
        members = identity_groups[source_id]
        if len(members) == 1:
            continue
        member_digests = sorted(item["deviceCandidateDigest"] for item in members)
        group_status, group_reasons = evaluate_duplicate_group(members)
        requires_winner = True
        if group_status == "DUPLICATE_GROUP_IDENTICAL":
            group_status = "DUPLICATE_GROUP_CANONICAL_WINNER_REQUIRED"
        group = {
            "duplicateGroupDigest": duplicate_group_digest(member_digests),
            "sourceIdentityDigest": source_identity_digest(source_id),
            "memberCount": len(members),
            "memberDeviceCandidateDigests": member_digests,
            "duplicateGroupStatus": group_status,
            "requiresCanonicalWinnerDecision": requires_winner,
            "reviewReasons": sorted(set(group_reasons)),
        }
        duplicate_groups.append(group)
        duplicate_group_by_identity[source_id] = group

    alias_proposals = build_alias_approval_package(devices=devices, classification_by_row=class_by_row)

    reconciliation_records: list[dict[str, Any]] = []
    canonical_proposals: list[dict[str, Any]] = []

    for device in devices:
        worksheet = str(device.get("sourceWorksheet", ""))
        row_number = int(device.get("sourceRowNumber", 0))
        row_key = (worksheet, row_number)
        source_id = str(device.get("sourceId", ""))
        spatial = spatial_by_row.get(row_key, {})
        classification = class_by_row.get(row_key, {})
        candidate_digest = device_candidate_digest(device)
        identity_digest = source_identity_digest(source_id)
        dup_group = duplicate_group_by_identity.get(source_id)
        dup_group_digest = dup_group["duplicateGroupDigest"] if dup_group else ""
        dup_group_status = dup_group["duplicateGroupStatus"] if dup_group else None
        group_size = len(identity_groups.get(source_id, []))

        label_status, _ = classify_label(str(device.get("sourceDeviceType", "")), str(classification.get("embeddedDeviceTypeCode", "")))
        loc_status = location_group_status_for_device(str(device.get("normalizedLocation", "")), location_groups)

        id_decision = identity_decision(source_id=source_id, group_size=group_size, group_status=dup_group_status or "UNIQUE")
        spat_decision = spatial_decision(
            spatial_binding=spatial,
            context_placeholders_present=context_placeholders_present,
            location_group_status=loc_status,
        )
        class_decision = classification_decision(classification_binding=classification, label_status=label_status)
        dup_decision = dup_group_status or "UNIQUE"
        proposal_decision = canonical_proposal_decision(
            identity_decision_value=id_decision,
            spatial_decision_value=spat_decision,
            classification_decision_value=class_decision,
            duplicate_group_status=dup_group_status,
            context_placeholders_present=context_placeholders_present,
        )

        review_reasons: list[str] = []
        blocker_reasons: list[str] = []
        warning_reasons: list[str] = []

        if dup_group:
            review_reasons.extend(dup_group.get("reviewReasons", []))
            review_reasons.append("CANONICAL_WINNER_REQUIRED")
        if class_decision == "CLASSIFICATION_ALIAS_APPROVAL_REQUIRED":
            review_reasons.append("SYSTEM_ALIAS_APPROVAL_REQUIRED")
        if class_decision == "CLASSIFICATION_NAMESPACE_REVIEW_REQUIRED":
            review_reasons.append("SCN_SEMANTIC_REVIEW_REQUIRED")
        if class_decision == "CLASSIFICATION_LABEL_CONFLICT_REVIEW":
            review_reasons.append("DEVICE_LABEL_NORMALIZATION_REQUIRED")
        if context_placeholders_present:
            review_reasons.append("CONTEXT_PLACEHOLDER_REVIEW")
        if proposal_decision == "CANONICAL_PROPOSAL_BLOCKED":
            blocker_reasons.append("CANONICAL_PROPOSAL_BLOCKED")
        if label_status != "LABEL_EXACT":
            warning_reasons.append(label_status)

        review_reasons = sorted(set(review_reasons))
        blocker_reasons = sorted(set(blocker_reasons))
        warning_reasons = sorted(set(warning_reasons))

        record = {
            "reconciliationRecordId": sha256_digest({"deviceCandidateDigest": candidate_digest, "profileId": PROFILE_ID}),
            "deviceCandidateDigest": candidate_digest,
            "sourceIdentityDigest": identity_digest,
            "sourceWorkbookDigest": workbook_digest,
            "sourceWorksheetDigest": source_worksheet_digest(worksheet),
            "sourceRowDigest": source_row_digest(worksheet, row_number),
            "spatialBindingDigest": str(classification.get("spatialBindingDigest", spatial.get("sourceDeviceDigest", ""))),
            "classificationBindingDigest": str(classification.get("bindingDigest", "")),
            "systemCategory": str(classification.get("genericSystemCategory", "")),
            "deviceClass": str(classification.get("genericDeviceClass", "")),
            "locationCandidateDigest": str(spatial.get("locationCandidateKey", "")),
            "duplicateGroupDigest": dup_group_digest,
            "identityDecision": id_decision,
            "spatialDecision": spat_decision,
            "classificationDecision": class_decision,
            "duplicateDecision": dup_decision,
            "canonicalProposalDecision": proposal_decision,
            "reviewReasons": review_reasons,
            "blockerReasons": blocker_reasons,
            "warningReasons": warning_reasons,
        }
        record["resultDigest"] = sha256_digest({k: v for k, v in record.items() if k != "resultDigest"})
        reconciliation_records.append(record)

        approval_dependencies: list[str] = []
        review_dependencies: list[str] = []
        blocker_dependencies: list[str] = []

        for proposal in alias_proposals:
            if proposal["proposalType"] == "SYSTEM_ALIAS" and class_decision == "CLASSIFICATION_ALIAS_APPROVAL_REQUIRED":
                review_dependencies.append(proposal["proposalId"])
            if proposal["proposalType"] == "SOURCE_NAMESPACE" and class_decision == "CLASSIFICATION_NAMESPACE_REVIEW_REQUIRED":
                review_dependencies.append(proposal["proposalId"])
            if proposal["proposalType"] == "DEVICE_LABEL_NORMALIZATION" and class_decision == "CLASSIFICATION_LABEL_CONFLICT_REVIEW":
                if str(proposal.get("deviceTypeCode", "")) == str(classification.get("embeddedDeviceTypeCode", "")):
                    review_dependencies.append(proposal["proposalId"])
        if dup_group:
            review_dependencies.append(dup_group["duplicateGroupDigest"])
        if context_placeholders_present:
            review_dependencies.append("CONTEXT_PLACEHOLDER")
        if blocker_reasons:
            blocker_dependencies.extend(blocker_reasons)

        proposal = {
            "proposalDigest": sha256_digest(
                {
                    "deviceCandidateDigest": candidate_digest,
                    "proposalStatus": proposal_decision,
                }
            ),
            "proposedObjectType": "Device",
            "sourceIdentityDigest": identity_digest,
            "deviceCandidateDigest": candidate_digest,
            "proposedSystemCategory": str(classification.get("genericSystemCategory", "")),
            "proposedDeviceClass": str(classification.get("genericDeviceClass", "")),
            "proposedSpatialBindingDigest": str(classification.get("spatialBindingDigest", "")),
            "proposedRelationshipDigests": sorted(
                digest
                for digest in (
                    str(spatial.get("locationCandidateKey", "")),
                    str(spatial.get("distributionAreaCandidateKey", "")),
                    str(spatial.get("levelCandidateKey", "")),
                )
                if digest
            ),
            "approvalDependencies": sorted(set(approval_dependencies)),
            "reviewDependencies": sorted(set(review_dependencies)),
            "blockerDependencies": sorted(set(blocker_dependencies)),
            "proposalStatus": proposal_decision,
        }
        canonical_proposals.append(proposal)

    reconciliation_records.sort(key=lambda item: item["reconciliationRecordId"])
    duplicate_groups.sort(key=lambda item: item["duplicateGroupDigest"])
    canonical_proposals.sort(key=lambda item: item["proposalDigest"])

    legacy_unclassified_used_as_blocker = int(classification_summary.get("unclassifiedDeviceCount", 0)) > 0 and int(
        coverage_analysis.get("coverage", {}).get("unmappedDeviceCount", 0)
    ) == 0

    gates = evaluate_readiness_gates(
        verification=verification,
        duplicate_groups=duplicate_groups,
        alias_proposals=alias_proposals,
        location_summary=location_summary,
        context_placeholders_present=context_placeholders_present,
        canonical_proposals=canonical_proposals,
        unmapped_device_count=int(verification["coverageMetrics"]["unmappedDeviceCount"]),
        legacy_unclassified_used_as_blocker=False,
    )

    review_findings, review_metrics = _aggregate_reviews(
        duplicate_groups=duplicate_groups,
        alias_proposals=alias_proposals,
        location_groups=location_groups,
        context_placeholders_present=context_placeholders_present,
        records=reconciliation_records,
    )

    unique_identities = len(identity_groups)
    duplicate_identities = sum(1 for members in identity_groups.values() if len(members) > 1)
    duplicate_identical = sum(1 for group in duplicate_groups if group["duplicateGroupStatus"] == "DUPLICATE_GROUP_CANONICAL_WINNER_REQUIRED")
    duplicate_conflict = sum(1 for group in duplicate_groups if "CONFLICT" in group["duplicateGroupStatus"])

    coverage_metrics = verification["coverageMetrics"]
    proposal_ready = sum(1 for item in canonical_proposals if item["proposalStatus"] == "CANONICAL_PROPOSAL_READY")
    proposal_review = sum(
        1
        for item in canonical_proposals
        if item["proposalStatus"]
        in {
            "CANONICAL_PROPOSAL_READY_WITH_REVIEW",
            "CANONICAL_PROPOSAL_DUPLICATE_REVIEW",
            "CANONICAL_PROPOSAL_CONTEXT_REQUIRED",
        }
    )
    proposal_deferred = sum(1 for item in canonical_proposals if item["proposalStatus"] == "CANONICAL_PROPOSAL_DEFERRED")
    proposal_blocked = sum(1 for item in canonical_proposals if item["proposalStatus"] == "CANONICAL_PROPOSAL_BLOCKED")
    spatial_review = sum(
        1
        for record in reconciliation_records
        if record["spatialDecision"] in {"SPATIAL_REVIEW_REQUIRED", "SPATIAL_MAPPING_VALID_WITH_LOCATION_REVIEW", "SPATIAL_CONTEXT_PLACEHOLDER"}
    )
    valid_spatial = sum(
        1
        for record in reconciliation_records
        if record["spatialDecision"] in {
            "SPATIAL_MAPPING_VALID",
            "SPATIAL_MAPPING_VALID_WITH_LOCATION_REVIEW",
            "SPATIAL_CONTEXT_PLACEHOLDER",
        }
    )

    blocker_count = sum(1 for gate in gates if gate["status"] == "BLOCKED") + sum(
        1 for record in reconciliation_records if record["blockerReasons"]
    )
    review_count = review_metrics["groupLevelReviewCount"] + review_metrics["recordLevelReviewCount"]
    warning_count = sum(1 for record in reconciliation_records if record["warningReasons"])

    if any(gate["status"] == "BLOCKED" for gate in gates):
        readiness = "RECONCILIATION_BLOCKED"
    elif review_findings or review_count or proposal_review or context_placeholders_present:
        readiness = "RECONCILIATION_COMPLETE_WITH_REVIEWS"
    else:
        readiness = "READY_FOR_CONTROLLED_CANONICAL_PROPOSAL_REVIEW"

    if readiness in FORBIDDEN_READINESS or readiness not in READINESS_OUTCOMES:
        raise AirportReconciliationProfileError("FORBIDDEN_READINESS", "forbidden readiness outcome generated")

    summary = {
        "authority": AUTHORITY,
        "containsCustomerAssetIdentifiers": False,
        "sourceRecordCount": len(devices),
        "reconciliationRecordCount": len(reconciliation_records),
        "uniqueSourceIdentityCount": unique_identities,
        "duplicateSourceIdentityCount": duplicate_identities,
        "duplicateGroupCount": len(duplicate_groups),
        "duplicateIdenticalGroupCount": duplicate_identical,
        "duplicateConflictGroupCount": duplicate_conflict,
        "evidenceClassifiedDeviceCount": coverage_metrics["evidenceClassifiedDeviceCount"],
        "reconciliationEligibleDeviceCount": coverage_metrics["reconciliationEligibleDeviceCount"],
        "fullyApprovedDeviceCount": coverage_metrics["fullyApprovedDeviceCount"],
        "reviewRequiredDeviceCount": coverage_metrics["reviewRequiredDeviceCount"],
        "unmappedDeviceCount": coverage_metrics["unmappedDeviceCount"],
        "validSpatialBindingCount": valid_spatial,
        "spatialReviewDeviceCount": spatial_review,
        "locationGroupCount": location_summary["locationGroupCount"],
        "expectedSharedLocationGroupCount": location_summary["expectedSharedLocationGroupCount"],
        "locationConflictGroupCount": location_summary["locationConflictGroupCount"],
        "systemAliasProposalCount": sum(1 for item in alias_proposals if item["proposalType"] == "SYSTEM_ALIAS"),
        "sourceNamespaceProposalCount": sum(1 for item in alias_proposals if item["proposalType"] == "SOURCE_NAMESPACE"),
        "labelNormalizationProposalCount": sum(1 for item in alias_proposals if item["proposalType"] == "DEVICE_LABEL_NORMALIZATION"),
        "canonicalProposalReadyCount": proposal_ready,
        "canonicalProposalReviewCount": proposal_review,
        "canonicalProposalDeferredCount": proposal_deferred,
        "canonicalProposalBlockedCount": proposal_blocked,
        "recordLevelReviewCount": review_metrics["recordLevelReviewCount"],
        "groupLevelReviewCount": review_metrics["groupLevelReviewCount"],
        "uniqueReviewCauseCount": review_metrics["uniqueReviewCauseCount"],
        "blockerCount": blocker_count,
        "reviewCount": review_count,
        "warningCount": warning_count,
        "readinessOutcome": readiness,
        "legacyUnclassifiedCountUsedAsBlocker": False,
    }
    summary["resultDigest"] = sha256_digest({k: v for k, v in summary.items() if k != "resultDigest"})

    result_doc = {
        "profileName": PROFILE_NAME,
        "profileId": PROFILE_ID,
        "profileVersion": PROFILE_VERSION,
        "authority": AUTHORITY,
        "implementationMode": IMPLEMENTATION_MODE,
        "platformCoreAirportized": False,
        "canonicalWriteEnabled": False,
        "databaseAccessEnabled": False,
        "runId": run_id,
        "verification": verification,
        "reconciliationContext": context.serialize(),
        "records": reconciliation_records,
        "readinessOutcome": readiness,
    }
    result_doc["resultDigest"] = sha256_digest({k: v for k, v in result_doc.items() if k != "resultDigest"})

    paths = {
        "airport-asset-reconciliation-result.json": result_doc,
        "airport-canonical-proposal-candidates.json": canonical_proposals,
        "airport-duplicate-reconciliation-groups.json": duplicate_groups,
        "airport-alias-approval-package.json": alias_proposals,
        "airport-location-reconciliation-groups.json": location_groups,
        "airport-asset-reconciliation-summary.json": summary,
        "airport-asset-reconciliation-review-findings.json": review_findings,
        "airport-asset-readiness-gates.json": gates,
    }

    for name, payload in paths.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    manifest = {"authority": AUTHORITY, "artifacts": [], "containsRawWorkbook": False}
    for relative in (*paths.keys(),):
        file_path = output_dir / relative
        manifest["artifacts"].append(
            {
                "artifactType": relative.replace(".json", "").upper().replace("-", "_"),
                "relativePath": relative,
                "sha256": hashlib.sha256(file_path.read_bytes()).hexdigest(),
                "containsCustomerAssetIdentifiers": relative
                in {"airport-asset-reconciliation-result.json", "airport-canonical-proposal-candidates.json"},
                "containsRawWorkbook": False,
                "retentionClass": "LOCAL_TMP_EVIDENCE",
            }
        )
    manifest_path = output_dir / "artifact-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "authority": AUTHORITY,
        "readinessOutcome": readiness,
        "summary": summary,
        "manifestPath": str(manifest_path),
        "resultDigest": summary["resultDigest"],
    }
