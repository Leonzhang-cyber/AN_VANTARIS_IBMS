"""Generic UConsole projection model builders."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import GENERATED_AT_POLICY, PROJECTION_VERSION, CardType, ProjectionType


def build_projection_id(*, authority: str, profile_id: str, projection_type: str) -> str:
    return sha256_digest(
        {
            "authority": authority,
            "profileId": profile_id,
            "projectionType": projection_type,
            "projectionVersion": PROJECTION_VERSION,
        }
    )


def build_row_id(*, source_system_key: str, registry_entry_id: str) -> str:
    return sha256_digest({"sourceSystemKey": source_system_key, "registryEntryId": registry_entry_id})


def build_card_id(*, card_type: str, card_key: Mapping[str, Any]) -> str:
    return sha256_digest({"cardType": card_type, "cardKey": dict(card_key)})


def build_dashboard_card(
    *,
    card_type: str,
    title: str,
    severity: str,
    status: str,
    value: int | str,
    unit: str,
    affected_source_system_keys: Sequence[str],
    decision_required: bool,
    evidence_references: Sequence[Mapping[str, Any]] = (),
    card_key: Mapping[str, Any],
) -> dict[str, Any]:
    card = {
        "cardId": build_card_id(card_type=card_type, card_key=card_key),
        "cardType": card_type,
        "title": title,
        "severity": severity,
        "status": status,
        "value": value,
        "unit": unit,
        "affectedSourceSystemKeys": sorted(set(affected_source_system_keys)),
        "decisionRequired": bool(decision_required),
        "evidenceReferences": list(evidence_references),
    }
    card["deterministicDigest"] = sha256_digest({k: v for k, v in card.items() if k != "deterministicDigest"})
    return card


def build_source_system_row(
    *,
    source_system_key: str,
    registry_entry_id: str,
    lifecycle_state: str,
    approval_state: str,
    readiness_state: str,
    integration_health_state: str,
    review_state: str,
    evidence_contract_state: str,
    runtime_observed: bool,
    runtime_verified: bool,
    device_evidence_count: int,
    pending_decision_count: int,
    finding_count: int,
) -> dict[str, Any]:
    row = {
        "rowId": build_row_id(source_system_key=source_system_key, registry_entry_id=registry_entry_id),
        "sourceSystemKey": source_system_key,
        "registryEntryId": registry_entry_id,
        "lifecycleState": lifecycle_state,
        "approvalState": approval_state,
        "readinessState": readiness_state,
        "integrationHealthState": integration_health_state,
        "reviewState": review_state,
        "evidenceContractState": evidence_contract_state,
        "runtimeObserved": bool(runtime_observed),
        "runtimeVerified": bool(runtime_verified),
        "deviceEvidenceCount": int(device_evidence_count),
        "pendingDecisionCount": int(pending_decision_count),
        "findingCount": int(finding_count),
    }
    row["deterministicDigest"] = sha256_digest({k: v for k, v in row.items() if k != "deterministicDigest"})
    return row


def build_source_artifact_reference(*, artifact_name: str, artifact_digest: str, authority: str) -> dict[str, str]:
    return {
        "artifactName": artifact_name,
        "artifactDigest": artifact_digest,
        "authority": authority,
    }


def build_uconsole_projection_shell(
    *,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    dashboard_cards: Sequence[Mapping[str, Any]],
    health_summary_cards: Sequence[Mapping[str, Any]],
    review_queue_cards: Sequence[Mapping[str, Any]],
    evidence_contract_cards: Sequence[Mapping[str, Any]],
    source_system_rows: Sequence[Mapping[str, Any]],
    filters: Sequence[Mapping[str, Any]],
    facets: Sequence[Mapping[str, Any]],
    default_page: Mapping[str, Any],
    source_artifact_references: Sequence[Mapping[str, Any]],
    projection_type: str = ProjectionType.UCONSOLE_INTEGRATION_HEALTH.value,
) -> dict[str, Any]:
    projection = {
        "projectionId": build_projection_id(
            authority=authority,
            profile_id=profile_id,
            projection_type=projection_type,
        ),
        "projectionType": projection_type,
        "authority": authority,
        "profileId": profile_id,
        "projectionVersion": PROJECTION_VERSION,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "generatedAtPolicy": GENERATED_AT_POLICY,
        "summary": dict(summary),
        "dashboardCards": list(dashboard_cards),
        "healthSummaryCards": list(health_summary_cards),
        "reviewQueueCards": list(review_queue_cards),
        "evidenceContractCards": list(evidence_contract_cards),
        "sourceSystemRows": list(source_system_rows),
        "filters": list(filters),
        "facets": list(facets),
        "defaultPage": dict(default_page),
        "sourceArtifactReferences": list(source_artifact_references),
    }
    projection["deterministicDigest"] = sha256_digest(
        {k: v for k, v in projection.items() if k != "deterministicDigest"}
    )
    return projection
