"""Airport read-only UConsole Integration Health projection aggregator."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from source_system_registry.digest import sha256_digest
from source_system_registry.errors import SourceSystemRegistryError
from uconsole_projection.enums import CardType, ProjectionStatus, Severity
from uconsole_projection.models import (
    build_dashboard_card,
    build_source_artifact_reference,
    build_source_system_row,
    build_uconsole_projection_shell,
)
from uconsole_projection.projection import (
    build_row_facets,
    build_row_filters,
    paginate_source_system_rows,
    sort_dashboard_cards,
    sort_source_system_rows,
)
from uconsole_projection.validation import validate_projection

from .evidence_adapter_profile import run_airport_evidence_adapter_projection
from .integration_health_projection import run_airport_integration_health_projection
from .source_system_review_projection import (
    compare_deterministic_outputs,
    run_airport_source_system_review_projection,
)

AUTHORITY = "ONE-AIRPORT-A2-05"
PROFILE_ID = "airport-source-system-profile-v1"
IMPLEMENTATION_STATUS = "READ_ONLY_UCONSOLE_INTEGRATION_HEALTH_PROJECTION_COMPLETE"
READINESS_OUTCOME = "UCONSOLE_INTEGRATION_HEALTH_READ_ONLY_PROJECTION_COMPLETE_RUNTIME_PENDING"

REVIEW_STATE_BY_REASON = {
    "ALIAS_APPROVAL_REQUIRED": "ALIAS_APPROVAL_PENDING",
    "NAMESPACE_INTERPRETATION_REQUIRED": "NAMESPACE_INTERPRETATION_PENDING",
    "REGISTRY_APPROVAL_REQUIRED": "REGISTRY_APPROVAL_PENDING",
}

SOURCE_SYSTEM_CARD_TITLES = {
    "ACS": "ACS source system",
    "RAS": "RAS source system",
    "CCTV": "CCTV source system",
    "PA": "PA source system",
    "TEL": "TEL source system",
}


def _review_state(binding: Mapping[str, Any]) -> str:
    reasons = list(binding.get("reviewReasons", []))
    for reason in reasons:
        mapped = REVIEW_STATE_BY_REASON.get(str(reason))
        if mapped:
            return mapped
    return "NO_REVIEW_PENDING"


def _card_status(readiness_state: str, review_state: str) -> str:
    if review_state != "NO_REVIEW_PENDING":
        return ProjectionStatus.REVIEW_REQUIRED.value
    if readiness_state == "RUNTIME_VERIFICATION_REQUIRED":
        return ProjectionStatus.RUNTIME_PENDING.value
    return ProjectionStatus.READY_FOR_READ_ONLY_CONSUMPTION.value


def _card_severity(review_state: str) -> str:
    if review_state in {"ALIAS_APPROVAL_PENDING", "NAMESPACE_INTERPRETATION_PENDING"}:
        return Severity.MEDIUM.value
    if review_state == "REGISTRY_APPROVAL_PENDING":
        return Severity.LOW.value
    return Severity.INFO.value


def _pending_decisions_for_key(review_cards: list[Mapping[str, Any]], source_key: str) -> int:
    return sum(
        1
        for card in review_cards
        if card.get("decisionRequired") is True and source_key in card.get("affectedSourceSystemKeys", [])
    )


def build_airport_uconsole_integration_health_projection(
    *,
    review_projection: Mapping[str, Any],
    health_projection: Mapping[str, Any],
    evidence_contract_projection: Mapping[str, Any],
) -> dict[str, Any]:
    bindings = list(review_projection.get("evidenceBindings", []))
    review_cards = list(review_projection.get("reviewCards", []))
    health_records = list(health_projection.get("healthRecords", []))
    envelopes = list(evidence_contract_projection.get("envelopes", []))

    if len(bindings) != 5 or len(health_records) != 5 or len(envelopes) != 5:
        raise SourceSystemRegistryError(
            "UCONSOLE_INPUT_COUNT_MISMATCH",
            "expected exactly five bindings, health records, and evidence envelopes",
        )

    binding_by_key = {str(item["sourceSystemKey"]): item for item in bindings}
    health_by_key = {str(item["sourceSystemKey"]): item for item in health_records}
    envelope_by_key = {str(item["sourceSystemKey"]): item for item in envelopes}

    expected_counts = {"ACS": 129, "RAS": 28, "CCTV": 52, "PA": 247, "TEL": 14}
    rows: list[dict[str, Any]] = []
    source_cards: list[dict[str, Any]] = []

    for source_key in sorted(expected_counts):
        binding = binding_by_key[source_key]
        health = health_by_key[source_key]
        envelope = envelope_by_key[source_key]
        device_count = int(binding["deviceEvidenceCount"])
        if device_count != expected_counts[source_key]:
            raise SourceSystemRegistryError(
                "UCONSOLE_DEVICE_COUNT_MISMATCH",
                f"unexpected device count for {source_key}: {device_count}",
            )

        review_state = _review_state(binding)
        readiness_state = str(health["readinessState"])
        pending = _pending_decisions_for_key(review_cards, source_key)
        finding_count = len(health.get("findings", []))

        row = build_source_system_row(
            source_system_key=source_key,
            registry_entry_id=str(binding["registryEntryId"]),
            lifecycle_state=str(binding["lifecycleState"]),
            approval_state=str(binding["approvalState"]),
            readiness_state=readiness_state,
            integration_health_state=readiness_state,
            review_state=review_state,
            evidence_contract_state=str(envelope["validationState"]),
            runtime_observed=bool(health["runtimeObservationHealth"]["runtimeObserved"]),
            runtime_verified=False,
            device_evidence_count=device_count,
            pending_decision_count=pending,
            finding_count=finding_count,
        )
        row["decisionRequired"] = pending > 0
        row["deterministicDigest"] = sha256_digest({k: v for k, v in row.items() if k != "deterministicDigest"})
        rows.append(row)

        source_cards.append(
            build_dashboard_card(
                card_type=CardType.SOURCE_SYSTEM_SUMMARY.value,
                title=SOURCE_SYSTEM_CARD_TITLES[source_key],
                severity=_card_severity(review_state),
                status=_card_status(readiness_state, review_state),
                value=device_count,
                unit="devices",
                affected_source_system_keys=[source_key],
                decision_required=pending > 0,
                evidence_references=list(binding.get("evidenceReferences", [])),
                card_key={"sourceSystemKey": source_key},
            )
        )

    rows = sort_source_system_rows(rows)
    source_cards = sort_dashboard_cards(source_cards)

    health_summary = health_projection.get("summary", {})
    review_summary = review_projection.get("summary", {})
    evidence_summary = evidence_contract_projection.get("summary", {})

    health_summary_card = build_dashboard_card(
        card_type=CardType.HEALTH_SUMMARY.value,
        title="Integration health summary",
        severity=Severity.INFO.value,
        status=ProjectionStatus.RUNTIME_PENDING.value,
        value=int(health_summary.get("runtimeObservedSystemCount", 0)),
        unit="runtimeObserved",
        affected_source_system_keys=sorted(expected_counts),
        decision_required=False,
        evidence_references=[],
        card_key={"cardType": "HEALTH_SUMMARY"},
    )

    review_queue_card = build_dashboard_card(
        card_type=CardType.REVIEW_QUEUE_SUMMARY.value,
        title="Review queue summary",
        severity=Severity.MEDIUM.value,
        status=ProjectionStatus.REVIEW_REQUIRED.value,
        value=int(review_summary.get("pendingDecisionCount", 0)),
        unit="pendingDecisions",
        affected_source_system_keys=sorted(expected_counts),
        decision_required=True,
        evidence_references=[],
        card_key={"cardType": "REVIEW_QUEUE_SUMMARY"},
    )

    evidence_contract_card = build_dashboard_card(
        card_type=CardType.EVIDENCE_CONTRACT_SUMMARY.value,
        title="Evidence adapter contract summary",
        severity=Severity.INFO.value,
        status=ProjectionStatus.RUNTIME_PENDING.value,
        value=int(evidence_summary.get("acceptedAsEvidenceCount", 0)),
        unit="acceptedEvidence",
        affected_source_system_keys=sorted(expected_counts),
        decision_required=False,
        evidence_references=[],
        card_key={"cardType": "EVIDENCE_CONTRACT_SUMMARY"},
    )

    total_evidence = sum(int(row["deviceEvidenceCount"]) for row in rows)
    if total_evidence != 470:
        raise SourceSystemRegistryError(
            "UCONSOLE_TOTAL_EVIDENCE_MISMATCH",
            f"expected 470 total evidence devices, got {total_evidence}",
        )

    summary = {
        "uConsoleIntegrationProjectionCount": 5,
        "sourceSystemRowCount": len(rows),
        "dashboardCardCount": len(source_cards),
        "healthSummaryCardCount": 1,
        "reviewQueueCardCount": 1,
        "evidenceContractCardCount": 1,
        "totalEvidenceDeviceCount": total_evidence,
        "pendingDecisionCount": int(review_summary.get("pendingDecisionCount", 0)),
        "runtimeObservedSystemCount": int(health_summary.get("runtimeObservedSystemCount", 0)),
        "runtimeVerifiedSystemCount": int(health_summary.get("runtimeVerifiedSystemCount", 0)),
        "healthySystemCount": int(health_summary.get("healthySystemCount", 0)),
        "activeSystemCount": int(health_summary.get("activeSystemCount", 0)),
        "registeredSystemCount": int(health_summary.get("registeredSystemCount", 0)),
        "approvedSystemCount": int(health_summary.get("approvedSystemCount", 0)),
        "aliasApprovalPendingCount": int(health_summary.get("aliasApprovalPendingCount", 0)),
        "namespaceReviewPendingCount": int(health_summary.get("namespaceReviewPendingCount", 0)),
        "registryApprovalPendingCount": int(health_summary.get("registryApprovalPendingCount", 0)),
        "evidenceEnvelopeCount": int(evidence_summary.get("evidenceEnvelopeCount", 0)),
        "acceptedAsEvidenceCount": int(evidence_summary.get("acceptedAsEvidenceCount", 0)),
        "rejectedEnvelopeCount": int(evidence_summary.get("rejectedEnvelopeCount", 0)),
        "runtimeConnectorExecutionEnabled": False,
        "databaseAccessEnabled": False,
        "productionActivationEnabled": False,
        "frontendEnabled": False,
        "apiEnabled": False,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
    }

    source_artifact_references = [
        build_source_artifact_reference(
            artifact_name="airport-source-system-review.v1.json",
            artifact_digest=str(review_projection.get("resultDigest", "")),
            authority=str(review_projection.get("authority", "")),
        ),
        build_source_artifact_reference(
            artifact_name="airport-integration-health.v1.json",
            artifact_digest=str(health_projection.get("resultDigest", "")),
            authority=str(health_projection.get("authority", "")),
        ),
        build_source_artifact_reference(
            artifact_name="airport-evidence-adapter-contract.v1.json",
            artifact_digest=str(evidence_contract_projection.get("resultDigest", "")),
            authority=str(evidence_contract_projection.get("authority", "")),
        ),
    ]

    projection_state_digest = sha256_digest(
        {
            "authority": AUTHORITY,
            "rowCount": len(rows),
            "reviewDigest": review_projection.get("resultDigest", ""),
            "healthDigest": health_projection.get("resultDigest", ""),
            "evidenceDigest": evidence_contract_projection.get("resultDigest", ""),
        }
    )
    default_page = paginate_source_system_rows(
        rows,
        page_size=25,
        projection_state_digest=projection_state_digest,
    )

    projection = build_uconsole_projection_shell(
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        dashboard_cards=source_cards,
        health_summary_cards=[health_summary_card],
        review_queue_cards=[review_queue_card],
        evidence_contract_cards=[evidence_contract_card],
        source_system_rows=rows,
        filters=build_row_filters(rows),
        facets=build_row_facets(rows),
        default_page=default_page,
        source_artifact_references=source_artifact_references,
    )
    validate_projection(projection)
    return projection


def build_airport_uconsole_from_committed_artifacts(projections_dir: Path) -> dict[str, Any]:
    review = json.loads((projections_dir / "airport-source-system-review.v1.json").read_text(encoding="utf-8"))
    health = json.loads((projections_dir / "airport-integration-health.v1.json").read_text(encoding="utf-8"))
    evidence = json.loads(
        (projections_dir / "airport-evidence-adapter-contract.v1.json").read_text(encoding="utf-8")
    )
    return build_airport_uconsole_integration_health_projection(
        review_projection=review,
        health_projection=health,
        evidence_contract_projection=evidence,
    )


def run_airport_uconsole_integration_health_projection(
    *,
    evidence_dir: Path | None = None,
    profile_path: Path | None = None,
    projections_dir: Path | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    if evidence_dir is not None and profile_path is not None:
        review = run_airport_source_system_review_projection(
            evidence_dir=evidence_dir,
            profile_path=profile_path,
            output_path=None,
        )
        health = run_airport_integration_health_projection(
            evidence_dir=evidence_dir,
            profile_path=profile_path,
            output_path=None,
        )
        evidence = run_airport_evidence_adapter_projection(
            evidence_dir=evidence_dir,
            profile_path=profile_path,
            output_path=None,
        )
        projection = build_airport_uconsole_integration_health_projection(
            review_projection=review,
            health_projection=health,
            evidence_contract_projection=evidence,
        )
    elif projections_dir is not None:
        projection = build_airport_uconsole_from_committed_artifacts(projections_dir)
    else:
        raise SourceSystemRegistryError(
            "UCONSOLE_INPUT_MISSING",
            "evidence_dir/profile_path or projections_dir is required",
        )

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return projection


__all__ = [
    "build_airport_uconsole_from_committed_artifacts",
    "build_airport_uconsole_integration_health_projection",
    "compare_deterministic_outputs",
    "run_airport_uconsole_integration_health_projection",
]
