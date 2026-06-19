"""Airport source-system review projection: cards, facets, filters, pagination."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest
from source_system_registry.enums import RegistryApprovalState, RegistryLifecycleState
from source_system_registry.errors import SourceSystemRegistryError

from .candidate_projection import (
    AUTHORITY as CANDIDATE_AUTHORITY,
    load_airport_profile,
    load_json,
    run_airport_source_system_projection,
)
from .source_system_evidence_binding import (
    AUTHORITY,
    build_source_system_evidence_bindings,
    validate_bindings_against_candidates,
)

READINESS_OUTCOME = "SOURCE_SYSTEM_REVIEW_PROJECTION_COMPLETE_WITH_PENDING_DECISIONS"
PROFILE_ID = "airport-source-system-profile-v1"
PAGE_SIZE_OPTIONS = (25, 50, 100)
MAX_PAGE_SIZE = 200

ALIAS_ALLOWED_DECISIONS = ("APPROVE_ALIAS", "REJECT_ALIAS", "DEFER")
NAMESPACE_ALLOWED_DECISIONS = ("APPROVE_NAMESPACE", "REJECT_NAMESPACE", "DEFER")
REGISTRY_ALLOWED_DECISIONS = ("APPROVE_REGISTRY", "REJECT_REGISTRY", "DEFER")


def compare_deterministic_outputs(first: Path, second: Path) -> tuple[bool, str]:
    if not first.is_file() or not second.is_file():
        return False, "MISSING_OUTPUT"
    if first.read_bytes() == second.read_bytes():
        return True, "MATCH"
    return False, "MISMATCH"


def build_review_card(
    *,
    review_type: str,
    title: str,
    affected_source_system_keys: Sequence[str],
    affected_record_count: int,
    evidence_references: Sequence[Mapping[str, Any]],
    allowed_decisions: Sequence[str],
    root_cause: str,
    blocking_effect: str,
    card_key: Mapping[str, Any],
) -> dict[str, Any]:
    card = {
        "reviewCardId": sha256_digest({"reviewType": review_type, "cardKey": card_key}),
        "reviewType": review_type,
        "title": title,
        "affectedSourceSystemKeys": sorted(affected_source_system_keys),
        "affectedRecordCount": affected_record_count,
        "evidenceReferences": list(evidence_references),
        "decisionRequired": True,
        "allowedDecisions": sorted(allowed_decisions),
        "currentDecision": "PENDING",
        "blockingEffect": blocking_effect,
        "rootCause": root_cause,
    }
    card["deterministicDigest"] = sha256_digest({k: v for k, v in card.items() if k != "deterministicDigest"})
    return card


def build_review_cards(
    *,
    candidates: Sequence[Mapping[str, Any]],
    bindings: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    binding_by_key = {str(item["sourceSystemKey"]): item for item in bindings}
    cards: list[dict[str, Any]] = []

    cctv = next(item for item in candidates if item["sourceSystemKey"] == "CCTV")
    pa = next(item for item in candidates if item["sourceSystemKey"] == "PA")
    tel = next(item for item in candidates if item["sourceSystemKey"] == "TEL")
    acs = next(item for item in candidates if item["sourceSystemKey"] == "ACS")
    ras = next(item for item in candidates if item["sourceSystemKey"] == "RAS")

    cards.append(
        build_review_card(
            review_type="ALIAS_APPROVAL",
            title="Approve CCT to CCTV source-system alias",
            affected_source_system_keys=["CCTV"],
            affected_record_count=int(binding_by_key["CCTV"]["sourceRecordCount"]),
            evidence_references=cctv.get("evidenceReferences", []),
            allowed_decisions=ALIAS_ALLOWED_DECISIONS,
            root_cause="SOURCE_ALIAS_CCT_TO_CCTV",
            blocking_effect="CANNOT_REGISTER_CCTV_WITHOUT_ALIAS_APPROVAL",
            card_key={"alias": "CCT", "target": "CCTV"},
        )
    )
    cards.append(
        build_review_card(
            review_type="ALIAS_APPROVAL",
            title="Approve PAS to PA source-system alias",
            affected_source_system_keys=["PA"],
            affected_record_count=int(binding_by_key["PA"]["sourceRecordCount"]),
            evidence_references=pa.get("evidenceReferences", []),
            allowed_decisions=ALIAS_ALLOWED_DECISIONS,
            root_cause="SOURCE_ALIAS_PAS_TO_PA",
            blocking_effect="CANNOT_REGISTER_PA_WITHOUT_ALIAS_APPROVAL",
            card_key={"alias": "PAS", "target": "PA"},
        )
    )
    cards.append(
        build_review_card(
            review_type="NAMESPACE_INTERPRETATION",
            title="Review SCN source namespace for TEL",
            affected_source_system_keys=["TEL"],
            affected_record_count=int(binding_by_key["TEL"]["sourceRecordCount"]),
            evidence_references=tel.get("evidenceReferences", []),
            allowed_decisions=NAMESPACE_ALLOWED_DECISIONS,
            root_cause="SOURCE_NAMESPACE_SCN_SEMANTIC_REVIEW",
            blocking_effect="CANNOT_REGISTER_TEL_WITHOUT_NAMESPACE_INTERPRETATION",
            card_key={"namespace": "SCN", "system": "TEL"},
        )
    )
    cards.append(
        build_review_card(
            review_type="REGISTRY_APPROVAL",
            title="Approve ACS source-system registry candidate",
            affected_source_system_keys=["ACS"],
            affected_record_count=int(binding_by_key["ACS"]["sourceRecordCount"]),
            evidence_references=acs.get("evidenceReferences", []),
            allowed_decisions=REGISTRY_ALLOWED_DECISIONS,
            root_cause="EXACT_EVIDENCE_REGISTRY_APPROVAL",
            blocking_effect="CANNOT_REGISTER_ACS_WITHOUT_REGISTRY_APPROVAL",
            card_key={"sourceSystemKey": "ACS", "evidenceMatch": "exact"},
        )
    )
    cards.append(
        build_review_card(
            review_type="REGISTRY_APPROVAL",
            title="Approve RAS source-system registry candidate",
            affected_source_system_keys=["RAS"],
            affected_record_count=int(binding_by_key["RAS"]["sourceRecordCount"]),
            evidence_references=ras.get("evidenceReferences", []),
            allowed_decisions=REGISTRY_ALLOWED_DECISIONS,
            root_cause="EXACT_EVIDENCE_REGISTRY_APPROVAL",
            blocking_effect="CANNOT_REGISTER_RAS_WITHOUT_REGISTRY_APPROVAL",
            card_key={"sourceSystemKey": "RAS", "evidenceMatch": "exact"},
        )
    )

    return sorted(cards, key=lambda item: (item["reviewType"], item["reviewCardId"]))


def build_facets(
    *,
    bindings: Sequence[Mapping[str, Any]],
    review_cards: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    facets: list[dict[str, Any]] = []

    def add_facet(facet_key: str, value: str, count: int) -> None:
        if not value:
            return
        facets.append(
            {
                "facetKey": facet_key,
                "optionDigest": sha256_digest({"facetKey": facet_key, "optionValue": value}),
                "count": count,
            }
        )

    evidence_type_counter = Counter(str(item.get("evidenceType", "")) for item in bindings)
    for value in sorted(evidence_type_counter):
        add_facet("evidenceType", value, evidence_type_counter[value])

    review_type_counter = Counter(str(item.get("reviewType", "")) for item in review_cards)
    for value in sorted(review_type_counter):
        add_facet("reviewType", value, review_type_counter[value])

    lifecycle_counter = Counter(str(item.get("lifecycleState", "")) for item in bindings)
    for value in sorted(lifecycle_counter):
        add_facet("lifecycleState", value, lifecycle_counter[value])

    approval_counter = Counter(str(item.get("approvalState", "")) for item in bindings)
    for value in sorted(approval_counter):
        add_facet("approvalState", value, approval_counter[value])

    add_facet("exactEvidence", "true", sum(1 for item in bindings if item.get("evidenceType") == "exact"))
    add_facet("aliasReview", "true", sum(1 for item in bindings if item.get("evidenceType") == "alias_review"))
    add_facet("namespaceReview", "true", sum(1 for item in bindings if item.get("evidenceType") == "namespace_review"))
    add_facet(
        "registryApprovalReview",
        "true",
        sum(1 for item in review_cards if item.get("reviewType") == "REGISTRY_APPROVAL"),
    )
    add_facet(
        "decisionRequired",
        "true",
        sum(1 for item in review_cards if item.get("decisionRequired") is True),
    )

    facets.sort(key=lambda item: (item["facetKey"], item["optionDigest"]))
    return facets


def build_filters() -> list[dict[str, Any]]:
    return [
        {"filterKey": "sourceSystemKey", "filterType": "ENUM", "options": ["ACS", "CCTV", "PA", "RAS", "TEL"]},
        {
            "filterKey": "evidenceType",
            "filterType": "ENUM",
            "options": ["exact", "alias_review", "namespace_review", "alias_candidate"],
        },
        {
            "filterKey": "reviewType",
            "filterType": "ENUM",
            "options": ["ALIAS_APPROVAL", "NAMESPACE_INTERPRETATION", "REGISTRY_APPROVAL"],
        },
        {
            "filterKey": "approvalState",
            "filterType": "ENUM",
            "options": ["DRAFT", "REVIEW_REQUIRED"],
        },
        {
            "filterKey": "lifecycleState",
            "filterType": "ENUM",
            "options": ["CANDIDATE"],
        },
        {"filterKey": "decisionRequired", "filterType": "BOOLEAN", "options": ["true"]},
    ]


def sort_bindings(bindings: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [dict(item) for item in bindings],
        key=lambda item: (
            str(item.get("sourceSystemKey", "")),
            str(item.get("registryEntryId", "")),
        ),
    )


def paginate_bindings(
    bindings: Sequence[Mapping[str, Any]],
    *,
    page_size: int,
    projection_state_digest: str,
    continuation_token: str | None = None,
) -> dict[str, Any]:
    page_size = min(max(page_size, 1), MAX_PAGE_SIZE)
    if page_size not in PAGE_SIZE_OPTIONS:
        page_size = min(PAGE_SIZE_OPTIONS, key=lambda option: abs(option - page_size))
    sorted_items = sort_bindings(bindings)
    offset = 0
    if continuation_token and continuation_token.startswith("v1:"):
        try:
            offset = int(continuation_token.split(":", 2)[1])
        except ValueError:
            offset = 0
    page = sorted_items[offset : offset + page_size]
    next_offset = offset + page_size
    next_token = None
    if next_offset < len(sorted_items):
        next_token = f"v1:{next_offset}:{sha256_digest({'projectionStateDigest': projection_state_digest, 'offset': next_offset})[:16]}"
    return {
        "pageSize": page_size,
        "offset": offset,
        "returnedCount": len(page),
        "totalCount": len(sorted_items),
        "continuationToken": next_token,
        "items": page,
    }


def build_projection_summary(
    *,
    bindings: Sequence[Mapping[str, Any]],
    review_cards: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    alias_cards = sum(1 for item in review_cards if item.get("reviewType") == "ALIAS_APPROVAL")
    namespace_cards = sum(1 for item in review_cards if item.get("reviewType") == "NAMESPACE_INTERPRETATION")
    registry_cards = sum(1 for item in review_cards if item.get("reviewType") == "REGISTRY_APPROVAL")
    pending = sum(1 for item in review_cards if item.get("decisionRequired") is True)

    return {
        "sourceSystemCandidateCount": 5,
        "sourceSystemEvidenceBindingCount": len(bindings),
        "totalBoundDeviceEvidenceCount": sum(int(item.get("deviceEvidenceCount", 0)) for item in bindings),
        "aliasReviewCardCount": alias_cards,
        "namespaceReviewCardCount": namespace_cards,
        "registryApprovalReviewCardCount": registry_cards,
        "pendingDecisionCount": pending,
        "activeSystemCount": sum(1 for item in bindings if str(item.get("lifecycleState", "")) == "ACTIVE"),
        "registeredSystemCount": sum(
            1 for item in bindings if str(item.get("lifecycleState", "")) == RegistryLifecycleState.REGISTERED.value
        ),
        "approvedSystemCount": sum(
            1 for item in bindings if str(item.get("approvalState", "")) == RegistryApprovalState.APPROVED.value
        ),
        "runtimeConnectorExecutionEnabled": False,
        "databaseAccessEnabled": False,
        "productionActivationEnabled": False,
        "crossIndustry": True,
        "airportSpecific": True,
        "containsCustomerAssetIdentifiers": False,
        "aggregateCustomerIdentifierCount": 0,
    }


def run_airport_source_system_review_projection(
    *,
    evidence_dir: Path,
    profile_path: Path,
    output_path: Path | None = None,
    page_size: int = 50,
) -> dict[str, Any]:
    airport_profile = load_airport_profile(profile_path)
    candidate_projection = run_airport_source_system_projection(
        evidence_dir=evidence_dir,
        profile_path=profile_path,
        output_path=None,
    )
    if str(candidate_projection.get("authority", "")) != CANDIDATE_AUTHORITY:
        raise SourceSystemRegistryError("CANDIDATE_AUTHORITY_MISMATCH", "unexpected candidate projection authority")

    candidates = list(candidate_projection.get("candidates", []))
    bindings = build_source_system_evidence_bindings(candidates)
    validate_bindings_against_candidates(bindings, candidates)
    review_cards = build_review_cards(candidates=candidates, bindings=bindings)
    facets = build_facets(bindings=bindings, review_cards=review_cards)
    filters = build_filters()

    projection_state_digest = sha256_digest(
        {
            "authority": AUTHORITY,
            "bindingCount": len(bindings),
            "reviewCardCount": len(review_cards),
            "candidateDigest": candidate_projection.get("resultDigest", ""),
        }
    )
    pagination = paginate_bindings(bindings, page_size=page_size, projection_state_digest=projection_state_digest)
    summary = build_projection_summary(bindings=bindings, review_cards=review_cards)

    projection = {
        "authority": AUTHORITY,
        "profileId": PROFILE_ID,
        "readinessOutcome": READINESS_OUTCOME,
        "summary": summary,
        "evidenceBindings": bindings,
        "reviewCards": review_cards,
        "facets": facets,
        "filters": filters,
        "pagination": pagination,
    }
    projection["resultDigest"] = sha256_digest({k: v for k, v in projection.items() if k != "resultDigest"})

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return projection
