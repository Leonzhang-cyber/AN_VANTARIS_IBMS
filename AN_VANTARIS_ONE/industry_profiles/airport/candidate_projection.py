"""Airport source-system consumer profile adapter."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest
from source_system_registry.enums import DeclarationState, RegistryApprovalState, RegistryLifecycleState
from source_system_registry.errors import SourceSystemRegistryError
from source_system_registry.models import build_evidence_reference, build_integration_declaration
from source_system_registry.projection import build_registry_projection, sort_registry_candidates
from source_system_registry.registry import build_registry_candidate
from source_system_registry.validation import validate_evidence_bundle

AUTHORITY = "ONE-AIRPORT-A2-01"
PROFILE_ID = "airport-source-system-profile-v1"
MAPPING_VERSION = "airport-source-system-v1"
SCHEMA_VERSION = "1.0.0"
READINESS_OUTCOME = "SOURCE_SYSTEM_CANDIDATES_COMPLETE_WITH_PENDING_REVIEWS"
IMPLEMENTATION_STATUS = "GENERIC_SOURCE_SYSTEM_REGISTRY_FOUNDATION_COMPLETE"


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise SourceSystemRegistryError("EVIDENCE_NOT_FOUND", f"evidence artifact not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_airport_profile(profile_path: Path) -> dict[str, Any]:
    profile = load_json(profile_path)
    if str(profile.get("profileType", "")) != "INDUSTRY_CONSUMER_PROFILE":
        raise SourceSystemRegistryError("INVALID_AIRPORT_PROFILE", "airport profile type mismatch")
    return profile


def _count_bindings(bindings: Sequence[Mapping[str, Any]], *, generic_system_category: str) -> int:
    return sum(1 for item in bindings if str(item.get("genericSystemCategory", "")) == generic_system_category)


def _alias_proposal_by_target(alias_package: Sequence[Mapping[str, Any]], target: str) -> Mapping[str, Any] | None:
    for proposal in alias_package:
        if proposal.get("proposalType") == "SYSTEM_ALIAS" and str(proposal.get("targetValue", "")) == target:
            return proposal
    return None


def _namespace_proposal(alias_package: Sequence[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    for proposal in alias_package:
        if proposal.get("proposalType") == "SOURCE_NAMESPACE":
            return proposal
    return None


def build_airport_consumer_metadata(
    *,
    binding_rule: Mapping[str, Any],
    source_record_count: int,
    alias_proposal: Mapping[str, Any] | None = None,
    namespace_proposal: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = {
        "evidenceMatch": str(binding_rule.get("evidenceMatch", "exact")),
        "aliasReviewRequired": bool(binding_rule.get("aliasReviewRequired", False)),
        "namespaceReviewRequired": bool(binding_rule.get("namespaceReviewRequired", False)),
        "sourceRecordCount": source_record_count,
        "autoApproved": False,
    }
    if binding_rule.get("observedSourceValue"):
        metadata["observedSourceValue"] = str(binding_rule["observedSourceValue"])
    if binding_rule.get("proposedNormalizedValue"):
        metadata["proposedNormalizedValue"] = str(binding_rule["proposedNormalizedValue"])
    if binding_rule.get("sourceNamespaceCode"):
        metadata["sourceNamespaceCode"] = str(binding_rule["sourceNamespaceCode"])
    if alias_proposal:
        metadata["aliasProposalId"] = str(alias_proposal.get("proposalId", ""))
        metadata["aliasDecisionStatus"] = str(alias_proposal.get("decisionStatus", "APPROVAL_REQUIRED"))
        metadata["autoApproved"] = alias_proposal.get("decisionStatus") == "APPROVED"
    if namespace_proposal:
        metadata["namespaceProposalId"] = str(namespace_proposal.get("proposalId", ""))
        metadata["namespaceDecisionStatus"] = str(namespace_proposal.get("decisionStatus", "APPROVAL_REQUIRED"))
    metadata["resultDigest"] = sha256_digest({k: v for k, v in metadata.items() if k != "resultDigest"})
    return metadata


def build_airport_source_system_candidates(
    *,
    bindings: Sequence[Mapping[str, Any]],
    alias_package: Sequence[Mapping[str, Any]],
    airport_profile: Mapping[str, Any],
) -> list[dict[str, Any]]:
    validate_evidence_bundle(bindings=bindings, alias_package=alias_package)
    created_from_profile = str(airport_profile.get("profileId", PROFILE_ID))
    mapping_version = str(airport_profile.get("mappingVersion", MAPPING_VERSION))

    alias_cct = _alias_proposal_by_target(alias_package, "CCTV")
    alias_pa = _alias_proposal_by_target(alias_package, "PA")
    namespace_scn = _namespace_proposal(alias_package)

    candidates: list[dict[str, Any]] = []
    for rule in airport_profile.get("systemEvidenceBindings", []):
        category = str(rule.get("genericSystemCategory", ""))
        source_key = str(rule.get("sourceSystemKey", ""))
        record_count = _count_bindings(bindings, generic_system_category=category)
        if record_count <= 0:
            raise SourceSystemRegistryError("MISSING_EVIDENCE_FOR_BINDING", f"no evidence for {source_key}")

        evidence_ref = build_evidence_reference(
            evidence_type="CLASSIFICATION_BINDING_AGGREGATE",
            evidence_id=sha256_digest({"genericSystemCategory": category, "sourceSystemKey": source_key}),
            source_profile=created_from_profile,
            source_record_count=record_count,
            provenance="ONE-AIRPORT-A1-03 classification bindings",
            digest=sha256_digest({"recordCount": record_count, "category": category}),
        )

        approval_state = RegistryApprovalState.REVIEW_REQUIRED
        if rule.get("aliasReviewRequired") or rule.get("namespaceReviewRequired"):
            approval_state = RegistryApprovalState.REVIEW_REQUIRED
        elif str(rule.get("evidenceMatch", "")) == "exact":
            approval_state = RegistryApprovalState.DRAFT

        alias_proposal = None
        if source_key == "CCTV":
            alias_proposal = alias_cct
        elif source_key == "PA":
            alias_proposal = alias_pa

        candidate = build_registry_candidate(
            source_system_key=source_key,
            display_name=source_key,
            system_category=category,
            created_from_profile=created_from_profile,
            mapping_version=mapping_version,
            schema_version=SCHEMA_VERSION,
            evidence_references=[evidence_ref],
            integration_declarations=[
                build_integration_declaration(
                    integration_method="EVIDENCE_ONLY",
                    protocol_family="UNDECLARED",
                    declaration_state=DeclarationState.DECLARED,
                )
            ],
            approval_state=approval_state,
            lifecycle_state=RegistryLifecycleState.CANDIDATE,
        )
        candidate["airportConsumerMetadata"] = build_airport_consumer_metadata(
            binding_rule=rule,
            source_record_count=record_count,
            alias_proposal=alias_proposal if source_key in {"CCTV", "PA"} else None,
            namespace_proposal=namespace_scn if source_key == "TEL" else None,
        )
        candidates.append(candidate)

    return sort_registry_candidates(candidates)


def build_airport_projection_summary(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    total_devices = sum(int(item.get("airportConsumerMetadata", {}).get("sourceRecordCount", 0)) for item in candidates)
    exact_count = sum(
        1
        for item in candidates
        if str(item.get("airportConsumerMetadata", {}).get("evidenceMatch", "")) == "exact"
    )
    alias_count = sum(
        1 for item in candidates if item.get("airportConsumerMetadata", {}).get("aliasReviewRequired") is True
    )
    namespace_count = sum(
        1 for item in candidates if item.get("airportConsumerMetadata", {}).get("namespaceReviewRequired") is True
    )
    return {
        "sourceSystemCandidateCount": len(candidates),
        "activeSystemCount": sum(1 for item in candidates if str(item.get("lifecycleState", "")) == "ACTIVE"),
        "registeredSystemCount": sum(
            1 for item in candidates if str(item.get("lifecycleState", "")) == RegistryLifecycleState.REGISTERED.value
        ),
        "approvedSystemCount": sum(
            1 for item in candidates if str(item.get("approvalState", "")) == RegistryApprovalState.APPROVED.value
        ),
        "exactEvidenceCandidateCount": exact_count,
        "aliasReviewCandidateCount": alias_count,
        "namespaceReviewCandidateCount": namespace_count,
        "totalEvidenceDeviceCount": total_devices,
        "runtimeConnectorExecutionEnabled": False,
        "databaseAccessEnabled": False,
        "productionActivationEnabled": False,
        "crossIndustry": True,
        "airportSpecific": False,
        "containsCustomerAssetIdentifiers": False,
    }


def run_airport_source_system_projection(
    *,
    evidence_dir: Path,
    profile_path: Path,
    output_path: Path | None = None,
) -> dict[str, Any]:
    airport_profile = load_airport_profile(profile_path)
    bindings = load_json(evidence_dir / "airport-device-classification-bindings.json")
    alias_package = load_json(evidence_dir / "airport-alias-approval-package.json")
    if not isinstance(bindings, list) or not isinstance(alias_package, list):
        raise SourceSystemRegistryError("MALFORMED_EVIDENCE", "expected list evidence artifacts")

    candidates = build_airport_source_system_candidates(
        bindings=bindings,
        alias_package=alias_package,
        airport_profile=airport_profile,
    )
    projection = build_registry_projection(
        authority=AUTHORITY,
        candidates=candidates,
        readiness_outcome=READINESS_OUTCOME,
        implementation_status=IMPLEMENTATION_STATUS,
        profile_id=PROFILE_ID,
    )
    projection["summary"] = build_airport_projection_summary(candidates)
    projection["resultDigest"] = sha256_digest({k: v for k, v in projection.items() if k != "resultDigest"})

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return projection


def compare_deterministic_outputs(first: Path, second: Path) -> tuple[bool, str]:
    if not first.is_file() or not second.is_file():
        return False, "MISSING_OUTPUT"
    if first.read_bytes() == second.read_bytes():
        return True, "MATCH"
    return False, "MISMATCH"
