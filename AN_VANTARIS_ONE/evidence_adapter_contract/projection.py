"""Deterministic Evidence Adapter Contract projection helpers."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION, RUNTIME_PRODUCER_TYPES, ValidationState


def sort_envelopes(envelopes: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [dict(item) for item in envelopes],
        key=lambda item: (
            str(item.get("sourceSystemKey", "")),
            str(item.get("evidenceKind", "")),
            str(item.get("envelopeId", "")),
        ),
    )


def is_runtime_observed(envelope: Mapping[str, Any]) -> bool:
    return str(envelope.get("producerType", "")) in RUNTIME_PRODUCER_TYPES


def build_contract_projection(
    *,
    envelopes: Sequence[Mapping[str, Any]],
    source_system_candidate_count: int,
    readiness_outcome: str,
    implementation_status: str,
) -> dict[str, Any]:
    sorted_envelopes = sort_envelopes(envelopes)
    accepted = [
        item
        for item in sorted_envelopes
        if str(item.get("validationState", ""))
        in {ValidationState.ACCEPTED_AS_EVIDENCE.value, ValidationState.NOT_RUNTIME_EVIDENCE.value}
    ]
    rejected = [item for item in sorted_envelopes if str(item.get("validationState", "")) == ValidationState.REJECTED.value]
    review_required = [
        item for item in sorted_envelopes if str(item.get("validationState", "")) == ValidationState.REVIEW_REQUIRED.value
    ]

    summary = {
        "contractVersion": CONTRACT_VERSION,
        "sourceSystemCandidateCount": source_system_candidate_count,
        "evidenceEnvelopeCount": len(sorted_envelopes),
        "acceptedAsEvidenceCount": len(accepted),
        "rejectedEnvelopeCount": len(rejected),
        "reviewRequiredEnvelopeCount": len(review_required),
        "runtimeObservedSystemCount": len({item["sourceSystemKey"] for item in sorted_envelopes if is_runtime_observed(item)}),
        "runtimeVerifiedSystemCount": 0,
        "runtimeConnectorExecutionEnabled": False,
        "databaseAccessEnabled": False,
        "productionActivationEnabled": False,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
        "readinessOutcome": readiness_outcome,
    }

    projection = {
        "contractVersion": CONTRACT_VERSION,
        "implementationStatus": implementation_status,
        "summary": summary,
        "envelopes": sorted_envelopes,
    }
    projection["resultDigest"] = sha256_digest({k: v for k, v in projection.items() if k != "resultDigest"})
    return projection
