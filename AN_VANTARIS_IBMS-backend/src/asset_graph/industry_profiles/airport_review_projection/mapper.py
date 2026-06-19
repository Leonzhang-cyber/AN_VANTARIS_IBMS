"""Airport review projection orchestration."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from ...reconciliation.models import sha256_digest
from .constants import (
    AUTHORITY,
    FORBIDDEN_READINESS,
    IMPLEMENTATION_MODE,
    INFORMATIONAL_LOCATION_STATUSES,
    PROFILE_ID,
    PROFILE_NAME,
    PROFILE_VERSION,
    READINESS_OUTCOMES,
)
from .context import AirportReviewProjectionContext
from .errors import AirportReviewProjectionError
from .evidence import verify_reconciliation_bundle
from .projection import (
    build_alias_review_card,
    build_context_review_card,
    build_duplicate_review_card,
    build_facets,
    build_informational_location_card,
    build_label_review_card,
    build_location_review_card,
    build_namespace_review_card,
    build_readiness_gate_card,
    build_review_cause,
    display_status_for_record,
    paginate_rows,
    sort_review_rows,
)


def compare_deterministic_outputs(first: Path, second: Path) -> tuple[bool, str]:
    if not first.is_file() or not second.is_file():
        return False, "MISSING_OUTPUT"
    if first.read_bytes() == second.read_bytes():
        return True, "MATCH"
    return False, "MISMATCH"


def run_airport_review_projection(
    *,
    reconciliation_dir: Path,
    output_dir: Path,
    context: AirportReviewProjectionContext,
    run_id: str,
) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    bundle = verify_reconciliation_bundle(
        reconciliation_dir=reconciliation_dir,
        expected_workbook_digest=context.source_workbook_digest,
        expected_reconciliation_digest=context.reconciliation_result_digest,
    )
    loaded = bundle["loaded"]
    result = loaded["reconciliationResult"]
    records = list(result.get("records", []))
    proposals = list(loaded["canonicalProposals"])
    duplicate_groups = list(loaded["duplicateGroups"])
    alias_package = list(loaded["aliasPackage"])
    location_groups = list(loaded["locationGroups"])
    gates = list(loaded["readinessGates"])
    summary_in = loaded["summary"]

    proposal_by_device = {str(item["deviceCandidateDigest"]): item for item in proposals}
    records_by_dup_group: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        digest = str(record.get("duplicateGroupDigest", ""))
        if digest:
            records_by_dup_group.setdefault(digest, []).append(record)

    context_pending = any(
        str(record.get("spatialDecision", "")) == "SPATIAL_CONTEXT_PLACEHOLDER"
        or str(record.get("canonicalProposalDecision", "")) == "CANONICAL_PROPOSAL_CONTEXT_REQUIRED"
        for record in records
    )
    context_card = build_context_review_card(
        affected_record_count=len(records),
        affected_proposal_count=len(proposals),
    )
    context_cause_id = context_card["reviewCauseId"]

    alias_proposals = [item for item in alias_package if item.get("proposalType") == "SYSTEM_ALIAS"]
    namespace_proposals = [item for item in alias_package if item.get("proposalType") == "SOURCE_NAMESPACE"]
    label_proposals = [item for item in alias_package if item.get("proposalType") == "DEVICE_LABEL_NORMALIZATION"]

    alias_cause_by_target = {
        str(item["proposalId"]): build_review_cause(
            review_cause_id=sha256_digest({"type": "ALIAS", "proposalId": item["proposalId"]}),
            review_cause_type="SYSTEM_ALIAS",
            title_key=f"review.alias.{item.get('targetValue', '').lower()}",
            description_key="review.alias.description",
            affected_record_count=int(item.get("affectedRecordCount", 0)),
            affected_proposal_count=int(item.get("affectedRecordCount", 0)),
            risk_class=str(item.get("riskClass", "MEDIUM")),
            current_authority=str(item.get("currentAuthority", "EVIDENCE_ONLY")),
            required_authority=str(item.get("requiredAuthority", "CUSTOMER_MAPPING_APPROVED")),
            related_group_digests=[str(item.get("proposalId", ""))],
            blocking_write_readiness=True,
        )
        for item in alias_proposals
    }
    namespace_cause = None
    if namespace_proposals:
        ns = namespace_proposals[0]
        namespace_cause = build_review_cause(
            review_cause_id=sha256_digest({"type": "NAMESPACE", "proposalId": ns["proposalId"]}),
            review_cause_type="SOURCE_NAMESPACE",
            title_key="review.namespace.scn",
            description_key="review.namespace.scn.description",
            affected_record_count=int(ns.get("affectedRecordCount", 0)),
            affected_proposal_count=int(ns.get("affectedRecordCount", 0)),
            risk_class=str(ns.get("riskClass", "HIGH")),
            current_authority=str(ns.get("currentAuthority", "UNRESOLVED")),
            required_authority=str(ns.get("requiredAuthority", "CUSTOMER_MAPPING_APPROVED")),
            related_group_digests=[str(ns.get("proposalId", ""))],
            blocking_write_readiness=True,
        )

    label_cause_by_proposal = {
        str(item["proposalId"]): build_review_cause(
            review_cause_id=sha256_digest({"type": "LABEL", "proposalId": item["proposalId"]}),
            review_cause_type="DEVICE_LABEL_NORMALIZATION",
            title_key="review.label.normalization",
            description_key="review.label.normalization.description",
            affected_record_count=int(item.get("affectedRecordCount", 0)),
            affected_proposal_count=int(item.get("affectedRecordCount", 0)),
            risk_class="LOW",
            current_authority=str(item.get("currentAuthority", "EVIDENCE_ONLY")),
            required_authority=str(item.get("requiredAuthority", "CUSTOMER_MAPPING_APPROVED")),
            related_group_digests=[str(item.get("proposalId", ""))],
            blocking_write_readiness=False,
        )
        for item in label_proposals
    }

    duplicate_cards = [
        build_duplicate_review_card(group=group, members=records_by_dup_group.get(str(group.get("duplicateGroupDigest", "")), []))
        for group in duplicate_groups
    ]
    duplicate_cause_ids = {card["reviewCauseId"] for card in duplicate_cards}

    location_conflict_cards = [
        build_location_review_card(duplicate_group=group, card_type="LOCATION_CONFLICT_REVIEW")
        for group in duplicate_groups
    ]
    informational_location_cards = [
        build_informational_location_card(group)
        for group in location_groups
        if str(group.get("locationReconciliationStatus", "")) in INFORMATIONAL_LOCATION_STATUSES
    ]

    review_rows: list[dict[str, Any]] = []
    for record in records:
        device_digest = str(record.get("deviceCandidateDigest", ""))
        proposal = proposal_by_device.get(device_digest, {})
        has_duplicate = str(record.get("identityDecision", "")).startswith("SOURCE_IDENTITY_DUPLICATE")
        has_namespace = record.get("classificationDecision") == "CLASSIFICATION_NAMESPACE_REVIEW_REQUIRED"
        has_alias = record.get("classificationDecision") == "CLASSIFICATION_ALIAS_APPROVAL_REQUIRED"
        has_label = record.get("classificationDecision") == "CLASSIFICATION_LABEL_CONFLICT_REVIEW"
        has_location_conflict = has_duplicate and bool(record.get("duplicateGroupDigest"))

        review_cause_ids: list[str] = [context_cause_id]
        blocker_cause_ids = list(record.get("blockerReasons", []))
        warning_cause_ids = list(record.get("warningReasons", []))

        if has_duplicate:
            for card in duplicate_cards:
                if str(record.get("duplicateGroupDigest", "")) == card.get("duplicateGroupDigest"):
                    review_cause_ids.append(str(card["reviewCauseId"]))
        if has_namespace and namespace_cause:
            review_cause_ids.append(namespace_cause["reviewCauseId"])
        if has_alias:
            for cause in alias_cause_by_target.values():
                review_cause_ids.append(cause["reviewCauseId"])
        if has_label:
            for cause in label_cause_by_proposal.values():
                review_cause_ids.append(cause["reviewCauseId"])

        display_status = display_status_for_record(
            record=record,
            proposal=proposal,
            has_duplicate=has_duplicate,
            has_namespace=has_namespace,
            has_alias=has_alias,
            has_label=has_label,
            has_location_conflict=has_location_conflict,
            context_pending=context_pending,
        )

        row = {
            "reconciliationRecordId": str(record.get("reconciliationRecordId", "")),
            "sourceIdentityDigest": str(record.get("sourceIdentityDigest", "")),
            "deviceCandidateDigest": device_digest,
            "spatialBindingDigest": str(record.get("spatialBindingDigest", "")),
            "classificationBindingDigest": str(record.get("classificationBindingDigest", "")),
            "canonicalProposalDigest": str(proposal.get("proposalDigest", "")),
            "systemCategory": str(record.get("systemCategory", "")),
            "deviceClass": str(record.get("deviceClass", "")),
            "spatialStatus": str(record.get("spatialDecision", "")),
            "classificationStatus": str(record.get("classificationDecision", "")),
            "duplicateStatus": str(record.get("duplicateDecision", "")),
            "proposalStatus": str(proposal.get("proposalStatus", "")),
            "reviewCauseIds": sorted(set(review_cause_ids)),
            "blockerCauseIds": sorted(set(str(item) for item in blocker_cause_ids)),
            "warningCauseIds": sorted(set(str(item) for item in warning_cause_ids)),
            "displayStatus": display_status,
            "detailProjection": {
                "assetEvidenceSummary": {
                    "sourceWorkbookDigest": str(record.get("sourceWorkbookDigest", "")),
                    "sourceWorksheetDigest": str(record.get("sourceWorksheetDigest", "")),
                    "sourceRowDigest": str(record.get("sourceRowDigest", "")),
                },
                "spatialEvidenceSummary": {
                    "spatialBindingDigest": str(record.get("spatialBindingDigest", "")),
                    "locationCandidateDigest": str(record.get("locationCandidateDigest", "")),
                },
                "classificationEvidenceSummary": {
                    "classificationBindingDigest": str(record.get("classificationBindingDigest", "")),
                    "systemCategory": str(record.get("systemCategory", "")),
                    "deviceClass": str(record.get("deviceClass", "")),
                },
                "duplicateComparisonSummary": {
                    "duplicateGroupDigest": str(record.get("duplicateGroupDigest", "")),
                    "identityDecision": str(record.get("identityDecision", "")),
                },
                "canonicalProposalSummary": {
                    "proposalDigest": str(proposal.get("proposalDigest", "")),
                    "proposalStatus": str(proposal.get("proposalStatus", "")),
                    "reviewDependencies": sorted(proposal.get("reviewDependencies", [])),
                },
                "readinessImpact": {
                    "displayStatus": display_status,
                    "blockingWriteReadiness": display_status in {"BLOCKED"},
                },
                "provenanceDigests": sorted(
                    digest
                    for digest in (
                        str(record.get("sourceWorkbookDigest", "")),
                        str(record.get("sourceRowDigest", "")),
                        device_digest,
                        str(proposal.get("proposalDigest", "")),
                    )
                    if digest
                ),
            },
        }
        row["resultDigest"] = sha256_digest({k: v for k, v in row.items() if k != "resultDigest"})
        review_rows.append(row)

    review_rows = sort_review_rows(review_rows)
    facets = build_facets(review_rows)

    review_causes = [context_card]
    review_causes.extend(alias_cause_by_target.values())
    if namespace_cause:
        review_causes.append(namespace_cause)
    review_causes.extend(label_cause_by_proposal.values())

    review_groups: list[dict[str, Any]] = []
    review_groups.append(context_card)
    review_groups.extend(duplicate_cards)
    review_groups.extend(build_alias_review_card(item) for item in alias_proposals)
    if namespace_proposals:
        review_groups.append(build_namespace_review_card(namespace_proposals[0]))
    review_groups.extend(build_label_review_card(item) for item in label_proposals)
    review_groups.extend(location_conflict_cards)
    review_groups.extend(informational_location_cards)

    projection_state_digest = sha256_digest(
        {
            "profileId": PROFILE_ID,
            "recordCount": len(review_rows),
            "reconciliationResultDigest": bundle["reconciliationResultDigest"],
        }
    )
    pagination = paginate_rows(
        review_rows,
        page_size=context.page_size,
        projection_state_digest=projection_state_digest,
    )

    readiness_cards = [
        build_readiness_gate_card(gate, affected_record_count=len(records), affected_proposal_count=len(proposals))
        for gate in gates
    ]

    status_counter = Counter(row["displayStatus"] for row in review_rows)

    unique_causes = {cause["reviewCauseId"] for cause in review_causes}
    unique_causes.update(duplicate_cause_ids)
    unique_causes.update(card["reviewCauseId"] for card in location_conflict_cards if not card.get("informationalOnly"))

    pending_operator = sum(
        1
        for card in review_groups
        if card.get("decisionState") == "APPROVAL_REQUIRED" and not card.get("informationalOnly")
    )

    blocker_count = status_counter.get("BLOCKED", 0)
    review_count = sum(1 for row in review_rows if row["displayStatus"] != "EVIDENCE_COMPLETE")
    warning_count = sum(1 for row in review_rows if row.get("warningCauseIds"))

    if any(gate.get("status") == "BLOCKED" for gate in gates):
        readiness = "REVIEW_PROJECTION_BLOCKED"
    elif pending_operator or review_count:
        readiness = "REVIEW_PROJECTION_COMPLETE_WITH_PENDING_DECISIONS"
    else:
        readiness = "READY_FOR_READ_ONLY_UCONSOLE_INTEGRATION"

    if readiness in FORBIDDEN_READINESS or readiness not in READINESS_OUTCOMES:
        raise AirportReviewProjectionError("FORBIDDEN_READINESS", "forbidden readiness outcome generated")

    dashboard = {
        "authority": AUTHORITY,
        "containsCustomerAssetIdentifiers": False,
        "readinessOutcome": readiness,
        "readinessGateCards": readiness_cards,
        "reviewCauseCount": len(unique_causes),
        "pendingOperatorDecisionCount": pending_operator,
        "paginationPreview": {
            "pageSize": pagination["pageSize"],
            "totalCount": pagination["totalCount"],
            "continuationToken": pagination["continuationToken"],
        },
        "displayStatusBreakdown": dict(sorted(status_counter.items())),
    }
    dashboard["resultDigest"] = sha256_digest({k: v for k, v in dashboard.items() if k != "resultDigest"})

    summary = {
        "authority": AUTHORITY,
        "containsCustomerAssetIdentifiers": False,
        "aggregateCustomerIdentifierCount": 0,
        "assetReviewRowCount": len(review_rows),
        "evidenceCompleteCount": status_counter.get("EVIDENCE_COMPLETE", 0),
        "reviewRequiredRecordCount": review_count,
        "blockedRecordCount": blocker_count,
        "contextReviewCardCount": 1,
        "duplicateReviewCardCount": len(duplicate_cards),
        "aliasReviewCardCount": len(alias_proposals),
        "namespaceReviewCardCount": len(namespace_proposals),
        "labelReviewCardCount": len(label_proposals),
        "locationReviewCardCount": len(location_conflict_cards),
        "informationalLocationGroupCount": len(informational_location_cards),
        "pendingOperatorDecisionCount": pending_operator,
        "uniqueReviewCauseCount": len(unique_causes),
        "affectedRecordCount": len(records),
        "affectedProposalCount": len(proposals),
        "readinessGateCardCount": len(readiness_cards),
        "blockerCount": blocker_count,
        "reviewCount": review_count,
        "warningCount": warning_count,
        "readinessOutcome": readiness,
        "projectionStateDigest": projection_state_digest,
    }
    summary["resultDigest"] = sha256_digest({k: v for k, v in summary.items() if k != "resultDigest"})

    paths = {
        "airport-asset-review-rows.json": review_rows,
        "airport-review-groups.json": review_groups,
        "airport-review-dashboard.json": dashboard,
        "airport-review-facets.json": facets,
        "airport-review-readiness-cards.json": readiness_cards,
        "airport-review-summary.json": summary,
    }

    for name, payload in paths.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    manifest = {"authority": AUTHORITY, "artifacts": [], "containsRawWorkbook": False}
    for relative, contains_ids in (
        ("airport-asset-review-rows.json", True),
        ("airport-review-groups.json", False),
        ("airport-review-dashboard.json", False),
        ("airport-review-facets.json", False),
        ("airport-review-readiness-cards.json", False),
        ("airport-review-summary.json", False),
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
        "summary": summary,
        "manifestPath": str(manifest_path),
        "resultDigest": summary["resultDigest"],
    }
