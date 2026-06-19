"""Review projection helpers: display status, causes, cards, facets, pagination."""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Mapping, Sequence

from ...reconciliation.models import sha256_digest
from .constants import (
    DISPLAY_STATUS_PRIORITY,
    INFORMATIONAL_LOCATION_STATUSES,
    MAX_PAGE_SIZE,
    PAGE_SIZE_OPTIONS,
    PENDING_LOCATION_STATUSES,
    PROFILE_ID,
)


def primary_display_status(candidates: Sequence[str]) -> str:
    priority = {status: index for index, status in enumerate(DISPLAY_STATUS_PRIORITY)}
    ranked = sorted(set(candidates), key=lambda item: priority.get(item, 999))
    return ranked[0] if ranked else "EVIDENCE_COMPLETE"


def display_status_for_record(
    *,
    record: Mapping[str, Any],
    proposal: Mapping[str, Any],
    has_duplicate: bool,
    has_namespace: bool,
    has_alias: bool,
    has_label: bool,
    has_location_conflict: bool,
    context_pending: bool,
) -> str:
    candidates: list[str] = []
    if record.get("blockerReasons") or proposal.get("proposalStatus") == "CANONICAL_PROPOSAL_BLOCKED":
        candidates.append("BLOCKED")
    if has_duplicate:
        candidates.append("DUPLICATE_DECISION_REQUIRED")
    if context_pending or proposal.get("proposalStatus") == "CANONICAL_PROPOSAL_CONTEXT_REQUIRED":
        candidates.append("CONTEXT_REQUIRED")
    if has_namespace:
        candidates.append("NAMESPACE_REVIEW_REQUIRED")
    if has_alias:
        candidates.append("ALIAS_APPROVAL_REQUIRED")
    if has_label:
        candidates.append("LABEL_REVIEW_REQUIRED")
    if has_location_conflict:
        candidates.append("LOCATION_REVIEW_REQUIRED")
    if record.get("reviewReasons"):
        candidates.append("REVIEW_REQUIRED")
    if proposal.get("proposalStatus") in {
        "CANONICAL_PROPOSAL_READY_WITH_REVIEW",
        "CANONICAL_PROPOSAL_DUPLICATE_REVIEW",
    }:
        candidates.append("READY_FOR_REVIEW")
    if record.get("classificationDecision") == "CLASSIFICATION_FULLY_APPROVED" and not candidates:
        candidates.append("EVIDENCE_COMPLETE")
    if not candidates:
        candidates.append("READY_FOR_REVIEW")
    return primary_display_status(candidates)


def build_review_cause(
    *,
    review_cause_id: str,
    review_cause_type: str,
    title_key: str,
    description_key: str,
    affected_record_count: int,
    affected_proposal_count: int,
    risk_class: str,
    current_authority: str,
    required_authority: str,
    related_group_digests: Sequence[str],
    blocking_write_readiness: bool,
) -> dict[str, Any]:
    cause = {
        "reviewCauseId": review_cause_id,
        "reviewCauseType": review_cause_type,
        "titleKey": title_key,
        "descriptionKey": description_key,
        "affectedRecordCount": affected_record_count,
        "affectedProposalCount": affected_proposal_count,
        "riskClass": risk_class,
        "currentAuthority": current_authority,
        "requiredAuthority": required_authority,
        "decisionState": "APPROVAL_REQUIRED",
        "relatedGroupDigests": sorted(related_group_digests),
        "blockingWriteReadiness": blocking_write_readiness,
    }
    cause["resultDigest"] = sha256_digest({k: v for k, v in cause.items() if k != "resultDigest"})
    return cause


def build_context_review_card(*, affected_record_count: int, affected_proposal_count: int) -> dict[str, Any]:
    card = {
        "cardType": "ContextReviewCard",
        "reviewCauseId": sha256_digest({"reviewCauseType": "CONTEXT", "scope": "AIRPORT_TERMINAL"}),
        "airportContextPending": True,
        "terminalContextPending": True,
        "affectedRecordCount": affected_record_count,
        "affectedProposalCount": affected_proposal_count,
        "decisionState": "APPROVAL_REQUIRED",
        "operatorActionRequired": True,
    }
    card["resultDigest"] = sha256_digest({k: v for k, v in card.items() if k != "resultDigest"})
    return card


def build_duplicate_review_card(
    *,
    group: Mapping[str, Any],
    members: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    locations = {str(item.get("locationCandidateDigest", "")) for item in members}
    classifications = {str(item.get("classificationDecision", "")) for item in members}
    spatial = {str(item.get("spatialDecision", "")) for item in members}
    maintenance = {str(item.get("maintenanceExtensionFieldCount", "")) for item in members if "maintenanceExtensionFieldCount" in item}
    spatial_agreement = "AGREE" if len(spatial) == 1 else "DIVERGE"
    location_agreement = "AGREE" if len(locations) == 1 else "DIVERGE"
    classification_agreement = "AGREE" if len(classifications) == 1 else "DIVERGE"
    maintenance_agreement = "AGREE" if len(maintenance) <= 1 else "DIVERGE"

    card = {
        "cardType": "DuplicateReviewCard",
        "duplicateGroupDigest": str(group.get("duplicateGroupDigest", "")),
        "reviewCauseId": sha256_digest({"reviewCauseType": "DUPLICATE", "group": group.get("duplicateGroupDigest", "")}),
        "memberCount": int(group.get("memberCount", 0)),
        "spatialAgreementStatus": spatial_agreement,
        "locationAgreementStatus": location_agreement,
        "classificationAgreementStatus": classification_agreement,
        "maintenanceAgreementStatus": maintenance_agreement,
        "sourceProvenanceCount": len({str(item.get("sourceRowDigest", "")) for item in members}),
        "winnerRequired": bool(group.get("requiresCanonicalWinnerDecision", True)),
        "recommendedNextAction": "DEFER_FOR_SITE_VERIFICATION" if location_agreement == "DIVERGE" else "CONFIRM_SAME_PHYSICAL_DEVICE",
        "decisionState": "APPROVAL_REQUIRED",
        "memberDeviceCandidateDigests": sorted(str(item.get("deviceCandidateDigest", "")) for item in members),
    }
    card["resultDigest"] = sha256_digest({k: v for k, v in card.items() if k != "resultDigest"})
    return card


def build_alias_review_card(proposal: Mapping[str, Any]) -> dict[str, Any]:
    card = {
        "cardType": "AliasReviewCard",
        "proposalId": str(proposal.get("proposalId", "")),
        "reviewCauseId": sha256_digest({"reviewCauseType": "SYSTEM_ALIAS", "proposalId": proposal.get("proposalId", "")}),
        "sourceValueDigest": str(proposal.get("sourceValueDigest", "")),
        "targetValue": str(proposal.get("targetValue", "")),
        "genericTargetCategory": str(proposal.get("genericCategory", "")),
        "affectedRecordCount": int(proposal.get("affectedRecordCount", 0)),
        "evidenceBasis": str(proposal.get("evidenceBasis", "")),
        "currentAuthority": str(proposal.get("currentAuthority", "")),
        "requiredAuthority": str(proposal.get("requiredAuthority", "")),
        "riskClass": str(proposal.get("riskClass", "")),
        "recommendedDecision": str(proposal.get("recommendedDecision", "APPROVAL_REQUIRED")),
        "decisionState": "APPROVAL_REQUIRED",
    }
    card["resultDigest"] = sha256_digest({k: v for k, v in card.items() if k != "resultDigest"})
    return card


def build_namespace_review_card(proposal: Mapping[str, Any]) -> dict[str, Any]:
    card = {
        "cardType": "NamespaceReviewCard",
        "proposalId": str(proposal.get("proposalId", "")),
        "reviewCauseId": sha256_digest({"reviewCauseType": "SOURCE_NAMESPACE", "proposalId": proposal.get("proposalId", "")}),
        "sourceValueDigest": str(proposal.get("sourceValueDigest", "")),
        "reviewTarget": str(proposal.get("targetValue", "")),
        "affectedRecordCount": int(proposal.get("affectedRecordCount", 0)),
        "evidenceBasis": str(proposal.get("evidenceBasis", "")),
        "currentAuthority": str(proposal.get("currentAuthority", "")),
        "requiredAuthority": str(proposal.get("requiredAuthority", "")),
        "riskClass": str(proposal.get("riskClass", "")),
        "decisionState": "APPROVAL_REQUIRED",
    }
    card["resultDigest"] = sha256_digest({k: v for k, v in card.items() if k != "resultDigest"})
    return card


def build_label_review_card(proposal: Mapping[str, Any]) -> dict[str, Any]:
    card = {
        "cardType": "LabelNormalizationReviewCard",
        "proposalId": str(proposal.get("proposalId", "")),
        "reviewCauseId": sha256_digest({"reviewCauseType": "LABEL_NORMALIZATION", "proposalId": proposal.get("proposalId", "")}),
        "sourceValueDigest": str(proposal.get("sourceValueDigest", "")),
        "proposedLabel": str(proposal.get("targetValue", "")),
        "deviceTypeCode": str(proposal.get("deviceTypeCode", "")),
        "labelClassification": str(proposal.get("labelClassification", "")),
        "affectedRecordCount": int(proposal.get("affectedRecordCount", 0)),
        "decisionState": "APPROVAL_REQUIRED",
    }
    card["resultDigest"] = sha256_digest({k: v for k, v in card.items() if k != "resultDigest"})
    return card


def build_location_review_card(
    *,
    location_group: Mapping[str, Any] | None = None,
    duplicate_group: Mapping[str, Any] | None = None,
    card_type: str = "LOCATION_CONFLICT_REVIEW",
) -> dict[str, Any]:
    if duplicate_group:
        digest = str(duplicate_group.get("duplicateGroupDigest", ""))
        member_count = int(duplicate_group.get("memberCount", 0))
        cause_id = sha256_digest({"reviewCauseType": "LOCATION_CONFLICT", "duplicateGroup": digest})
    else:
        digest = str(location_group.get("locationGroupDigest", "")) if location_group else ""
        member_count = int(location_group.get("memberCount", 0)) if location_group else 0
        cause_id = sha256_digest({"reviewCauseType": "LOCATION_CONFLICT", "locationGroup": digest})

    card = {
        "cardType": "LocationReviewCard",
        "locationReconciliationStatus": card_type,
        "reviewCauseId": cause_id,
        "relatedGroupDigest": digest,
        "memberCount": member_count,
        "decisionState": "APPROVAL_REQUIRED",
        "informationalOnly": False,
    }
    card["resultDigest"] = sha256_digest({k: v for k, v in card.items() if k != "resultDigest"})
    return card


def build_informational_location_card(location_group: Mapping[str, Any]) -> dict[str, Any]:
    card = {
        "cardType": "LocationReviewCard",
        "locationReconciliationStatus": str(location_group.get("locationReconciliationStatus", "")),
        "locationGroupDigest": str(location_group.get("locationGroupDigest", "")),
        "memberCount": int(location_group.get("memberCount", 0)),
        "decisionState": "RESOLVED_BY_EXISTING_AUTHORITY",
        "informationalOnly": True,
    }
    card["resultDigest"] = sha256_digest({k: v for k, v in card.items() if k != "resultDigest"})
    return card


def sort_review_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    priority = {status: index for index, status in enumerate(DISPLAY_STATUS_PRIORITY)}

    def sort_key(row: Mapping[str, Any]) -> tuple:
        return (
            priority.get(str(row.get("displayStatus", "")), 999),
            str(row.get("systemCategory", "")),
            str(row.get("deviceClass", "")),
            str(row.get("sourceIdentityDigest", "")),
            str(row.get("reconciliationRecordId", "")),
        )

    return sorted([dict(row) for row in rows], key=sort_key)


def build_facets(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    facet_fields = (
        "displayStatus",
        "systemCategory",
        "deviceClass",
        "spatialStatus",
        "classificationStatus",
        "duplicateStatus",
        "proposalStatus",
    )
    facets: list[dict[str, Any]] = []
    for field in facet_fields:
        counter: Counter[str] = Counter(str(row.get(field, "")) for row in rows)
        review_counter: Counter[str] = Counter(
            str(row.get(field, "")) for row in rows if row.get("displayStatus") not in {"EVIDENCE_COMPLETE"}
        )
        blocker_counter: Counter[str] = Counter(
            str(row.get(field, "")) for row in rows if row.get("displayStatus") == "BLOCKED"
        )
        for value in sorted(counter):
            if not value:
                continue
            facets.append(
                {
                    "facetKey": field,
                    "optionDigest": sha256_digest({"facetKey": field, "optionValue": value}),
                    "recordCount": counter[value],
                    "reviewCount": review_counter[value],
                    "blockerCount": blocker_counter[value],
                }
            )
    facets.sort(key=lambda item: (item["facetKey"], item["optionDigest"]))
    return facets


def paginate_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    page_size: int,
    continuation_token: str | None = None,
    projection_state_digest: str,
) -> dict[str, Any]:
    page_size = min(max(page_size, 1), MAX_PAGE_SIZE)
    if page_size not in PAGE_SIZE_OPTIONS:
        page_size = min(PAGE_SIZE_OPTIONS, key=lambda option: abs(option - page_size))
    sorted_rows = sort_review_rows(rows)
    offset = 0
    if continuation_token:
        expected = sha256_digest({"projectionStateDigest": projection_state_digest, "offset": offset})
        if continuation_token.startswith("v1:"):
            try:
                offset = int(continuation_token.split(":", 2)[1])
            except ValueError:
                offset = 0
        else:
            offset = 0
    page = sorted_rows[offset : offset + page_size]
    next_offset = offset + page_size
    next_token = None
    if next_offset < len(sorted_rows):
        next_token = f"v1:{next_offset}:{sha256_digest({'projectionStateDigest': projection_state_digest, 'offset': next_offset})[:16]}"
    return {
        "pageSize": page_size,
        "offset": offset,
        "returnedCount": len(page),
        "totalCount": len(sorted_rows),
        "continuationToken": next_token,
        "rows": page,
    }


def build_readiness_gate_card(gate: Mapping[str, Any], *, affected_record_count: int, affected_proposal_count: int) -> dict[str, Any]:
    gate_id = str(gate.get("gateId", ""))
    card = {
        "cardType": "ReadinessGateCard",
        "gateId": gate_id,
        "status": str(gate.get("status", "")),
        "titleKey": f"readiness.gate.{gate_id.lower()}",
        "affectedRecordCount": affected_record_count,
        "affectedProposalCount": affected_proposal_count,
        "reviewCauseCount": 1 if gate.get("status") == "PASS_WITH_REVIEW" else 0,
        "blockingConditionCount": 1 if gate.get("status") == "BLOCKED" else 0,
        "operatorActionRequired": gate.get("status") in {"PASS_WITH_REVIEW", "BLOCKED"},
        "writeReadinessImpact": gate_id == "G12_WRITE_BOUNDARY_ENFORCEMENT",
    }
    if gate_id == "G12_WRITE_BOUNDARY_ENFORCEMENT":
        card["canonicalWriteEnabled"] = False
        card["databaseAccessEnabled"] = False
        card["writeCutoverPerformed"] = False
    card["resultDigest"] = sha256_digest({k: v for k, v in card.items() if k != "resultDigest"})
    return card
