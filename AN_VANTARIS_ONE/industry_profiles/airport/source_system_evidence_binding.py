"""Airport source-system evidence binding over A2-01 candidates."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest
from source_system_registry.errors import SourceSystemRegistryError

from .candidate_projection import load_json

AUTHORITY = "ONE-AIRPORT-A2-02"
BINDING_SORT_KEYS = ("sourceSystemKey", "registryEntryId")


def _review_reasons_for_candidate(candidate: Mapping[str, Any]) -> list[str]:
    meta = candidate.get("airportConsumerMetadata", {})
    reasons: list[str] = []
    if meta.get("aliasReviewRequired"):
        reasons.append("ALIAS_APPROVAL_REQUIRED")
    if meta.get("namespaceReviewRequired"):
        reasons.append("NAMESPACE_INTERPRETATION_REQUIRED")
    if str(candidate.get("approvalState", "")) == "DRAFT" and str(meta.get("evidenceMatch", "")) == "exact":
        reasons.append("REGISTRY_APPROVAL_REQUIRED")
    if str(candidate.get("approvalState", "")) == "REVIEW_REQUIRED" and not reasons:
        reasons.append("REGISTRY_REVIEW_REQUIRED")
    return sorted(set(reasons))


def _observed_source_values(candidate: Mapping[str, Any]) -> list[str]:
    meta = candidate.get("airportConsumerMetadata", {})
    observed = meta.get("observedSourceValue")
    if observed:
        return [str(observed)]
    return [str(candidate.get("sourceSystemKey", ""))]


def _normalized_proposal(candidate: Mapping[str, Any]) -> str:
    meta = candidate.get("airportConsumerMetadata", {})
    return str(meta.get("proposedNormalizedValue") or candidate.get("sourceSystemKey", ""))


def _evidence_type(candidate: Mapping[str, Any]) -> str:
    meta = candidate.get("airportConsumerMetadata", {})
    match = str(meta.get("evidenceMatch", "exact"))
    if meta.get("namespaceReviewRequired"):
        return "namespace_review"
    if meta.get("aliasReviewRequired"):
        return "alias_review"
    return match


def build_source_system_evidence_binding(candidate: Mapping[str, Any]) -> dict[str, Any]:
    meta = candidate.get("airportConsumerMetadata", {})
    record_count = int(meta.get("sourceRecordCount", 0))
    if record_count <= 0:
        raise SourceSystemRegistryError("INVALID_BINDING_COUNT", "source record count must be positive")

    binding = {
        "registryEntryId": str(candidate.get("registryEntryId", "")),
        "sourceSystemKey": str(candidate.get("sourceSystemKey", "")),
        "observedSourceValues": _observed_source_values(candidate),
        "normalizedProposal": _normalized_proposal(candidate),
        "sourceRecordCount": record_count,
        "deviceEvidenceCount": record_count,
        "evidenceType": _evidence_type(candidate),
        "evidenceReferences": list(candidate.get("evidenceReferences", [])),
        "provenance": "ONE-AIRPORT-A1-03 classification bindings via ONE-AIRPORT-A2-01 candidates",
        "reviewReasons": _review_reasons_for_candidate(candidate),
        "lifecycleState": str(candidate.get("lifecycleState", "CANDIDATE")),
        "approvalState": str(candidate.get("approvalState", "DRAFT")),
    }
    binding["bindingDigest"] = sha256_digest({k: v for k, v in binding.items() if k != "bindingDigest"})
    return binding


def build_source_system_evidence_bindings(candidates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if len(candidates) != 5:
        raise SourceSystemRegistryError("CANDIDATE_COUNT_MISMATCH", "expected exactly five source-system candidates")

    bindings = [build_source_system_evidence_binding(candidate) for candidate in candidates]
    total = sum(item["deviceEvidenceCount"] for item in bindings)
    if total != 470:
        raise SourceSystemRegistryError("EVIDENCE_COUNT_MISMATCH", f"expected 470 bound devices, got {total}")

    return sorted(bindings, key=lambda item: (item["sourceSystemKey"], item["registryEntryId"]))


def validate_bindings_against_candidates(
    bindings: Sequence[Mapping[str, Any]],
    candidates: Sequence[Mapping[str, Any]],
) -> None:
    if len(bindings) != len(candidates):
        raise SourceSystemRegistryError("BINDING_COUNT_MISMATCH", "binding count must match candidate count")
    candidate_by_key = {str(item["sourceSystemKey"]): item for item in candidates}
    for binding in bindings:
        key = str(binding.get("sourceSystemKey", ""))
        candidate = candidate_by_key.get(key)
        if candidate is None:
            raise SourceSystemRegistryError("UNKNOWN_BINDING_KEY", f"unknown binding key: {key}")
        if str(binding.get("registryEntryId", "")) != str(candidate.get("registryEntryId", "")):
            raise SourceSystemRegistryError("REGISTRY_ENTRY_MISMATCH", f"registry entry mismatch for {key}")
