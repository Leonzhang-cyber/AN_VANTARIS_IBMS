"""Read-only registry projection helpers."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .digest import sha256_digest
from .enums import RegistryApprovalState, RegistryLifecycleState


def sort_registry_candidates(candidates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [dict(item) for item in candidates],
        key=lambda item: (
            str(item.get("sourceSystemKey", "")),
            str(item.get("registryEntryId", "")),
        ),
    )


def build_registry_projection(
    *,
    authority: str,
    candidates: Sequence[Mapping[str, Any]],
    readiness_outcome: str,
    implementation_status: str,
    profile_id: str,
) -> dict[str, Any]:
    sorted_candidates = sort_registry_candidates(candidates)
    active_count = sum(1 for item in sorted_candidates if str(item.get("lifecycleState", "")) == "ACTIVE")
    registered_count = sum(
        1 for item in sorted_candidates if str(item.get("lifecycleState", "")) == RegistryLifecycleState.REGISTERED.value
    )
    approved_count = sum(
        1 for item in sorted_candidates if str(item.get("approvalState", "")) == RegistryApprovalState.APPROVED.value
    )

    summary = {
        "sourceSystemCandidateCount": len(sorted_candidates),
        "activeSystemCount": active_count,
        "registeredSystemCount": registered_count,
        "approvedSystemCount": approved_count,
        "exactEvidenceCandidateCount": 0,
        "aliasReviewCandidateCount": 0,
        "namespaceReviewCandidateCount": 0,
        "totalEvidenceDeviceCount": 0,
        "runtimeConnectorExecutionEnabled": False,
        "databaseAccessEnabled": False,
        "productionActivationEnabled": False,
        "crossIndustry": True,
        "airportSpecific": False,
        "containsCustomerAssetIdentifiers": False,
    }

    projection = {
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": summary,
        "candidates": sorted_candidates,
    }
    projection["resultDigest"] = sha256_digest({k: v for k, v in projection.items() if k != "resultDigest"})
    return projection
