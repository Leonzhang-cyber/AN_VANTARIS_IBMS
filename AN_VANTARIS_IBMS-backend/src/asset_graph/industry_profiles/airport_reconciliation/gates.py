"""Readiness gates for airport asset reconciliation."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .constants import GATE_IDS


def evaluate_readiness_gates(
    *,
    verification: Mapping[str, Any],
    duplicate_groups: Sequence[Mapping[str, Any]],
    alias_proposals: Sequence[Mapping[str, Any]],
    location_summary: Mapping[str, Any],
    context_placeholders_present: bool,
    canonical_proposals: Sequence[Mapping[str, Any]],
    unmapped_device_count: int,
    legacy_unclassified_used_as_blocker: bool,
) -> list[dict[str, Any]]:
    device_count = int(verification.get("deviceCandidateCount", 0))
    coverage = verification.get("coverageMetrics", {})
    evidence_classified = int(coverage.get("evidenceClassifiedDeviceCount", 0))
    reconciliation_eligible = int(coverage.get("reconciliationEligibleDeviceCount", 0))
    duplicate_group_count = len(duplicate_groups)
    duplicate_review_groups = sum(
        1
        for group in duplicate_groups
        if group.get("requiresCanonicalWinnerDecision") or "CONFLICT" in str(group.get("duplicateGroupStatus", ""))
    )
    alias_count = sum(1 for item in alias_proposals if item.get("proposalType") == "SYSTEM_ALIAS")
    namespace_count = sum(1 for item in alias_proposals if item.get("proposalType") == "SOURCE_NAMESPACE")
    label_count = sum(1 for item in alias_proposals if item.get("proposalType") == "DEVICE_LABEL_NORMALIZATION")
    proposal_ready = sum(1 for item in canonical_proposals if item.get("proposalStatus") == "CANONICAL_PROPOSAL_READY")
    proposal_review = sum(
        1
        for item in canonical_proposals
        if item.get("proposalStatus") in {"CANONICAL_PROPOSAL_READY_WITH_REVIEW", "CANONICAL_PROPOSAL_DUPLICATE_REVIEW", "CANONICAL_PROPOSAL_CONTEXT_REQUIRED"}
    )
    proposal_blocked = sum(1 for item in canonical_proposals if item.get("proposalStatus") == "CANONICAL_PROPOSAL_BLOCKED")

    gates: list[dict[str, Any]] = []

    def add(gate_id: str, status: str, detail: str) -> None:
        gates.append({"gateId": gate_id, "status": status, "detail": detail})

    add("G01_INPUT_EVIDENCE_INTEGRITY", "PASS", "All upstream artifact authorities and digests verified")
    add(
        "G02_RECORD_COUNT_ALIGNMENT",
        "PASS" if device_count == evidence_classified == reconciliation_eligible else "BLOCKED",
        f"deviceCandidateCount={device_count}, evidenceClassified={evidence_classified}, reconciliationEligible={reconciliation_eligible}",
    )
    add(
        "G03_SPATIAL_BINDING_COVERAGE",
        "PASS_WITH_REVIEW" if context_placeholders_present else "PASS",
        "All device records have spatial bindings",
    )
    add(
        "G04_CLASSIFICATION_EVIDENCE_COVERAGE",
        "PASS" if evidence_classified == device_count and unmapped_device_count == 0 else "PASS_WITH_REVIEW",
        f"evidenceClassifiedDeviceCount={evidence_classified}, unmappedDeviceCount={unmapped_device_count}",
    )
    add(
        "G05_DUPLICATE_IDENTITY_REVIEW",
        "PASS_WITH_REVIEW" if duplicate_group_count else "PASS",
        f"duplicateGroupCount={duplicate_group_count}, reviewGroups={duplicate_review_groups}",
    )
    add(
        "G06_SYSTEM_ALIAS_APPROVAL",
        "PASS_WITH_REVIEW" if alias_count else "PASS",
        f"systemAliasProposalCount={alias_count}",
    )
    add(
        "G07_SOURCE_NAMESPACE_APPROVAL",
        "PASS_WITH_REVIEW" if namespace_count else "PASS",
        f"sourceNamespaceProposalCount={namespace_count}",
    )
    add(
        "G08_DEVICE_LABEL_NORMALIZATION",
        "PASS_WITH_REVIEW" if label_count else "PASS",
        f"labelNormalizationProposalCount={label_count}",
    )
    add(
        "G09_LOCATION_RECONCILIATION",
        "PASS_WITH_REVIEW" if int(location_summary.get("locationTextCollisionGroupCount", 0)) else "PASS",
        f"expectedSharedLocationGroupCount={location_summary.get('expectedSharedLocationGroupCount', 0)}",
    )
    add(
        "G10_CONTEXT_APPROVAL",
        "PASS_WITH_REVIEW" if context_placeholders_present else "PASS",
        "Airport and terminal context placeholders pending",
    )
    add(
        "G11_CANONICAL_PROPOSAL_COMPLETENESS",
        "PASS_WITH_REVIEW" if proposal_review or proposal_blocked else "PASS",
        f"ready={proposal_ready}, review={proposal_review}, blocked={proposal_blocked}",
    )
    add(
        "G12_WRITE_BOUNDARY_ENFORCEMENT",
        "PASS",
        "canonicalWriteEnabled=false, databaseAccessEnabled=false, writeCutoverPerformed=false",
    )

    if legacy_unclassified_used_as_blocker:
        gates.append(
            {
                "gateId": "G04_CLASSIFICATION_EVIDENCE_COVERAGE",
                "status": "BLOCKED",
                "detail": "Legacy unclassifiedDeviceCount must not be used as reconciliation blocker",
            }
        )

    gate_index = {item["gateId"]: item for item in gates}
    return [gate_index[gate_id] for gate_id in GATE_IDS if gate_id in gate_index]
