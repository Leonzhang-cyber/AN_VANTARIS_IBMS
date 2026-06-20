"""Deterministic model builders for Operator Review Policy Guards."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def _sorted(values: Sequence[str] | None) -> list[str]:
    return sorted(str(value) for value in values or ())


def build_policy_guard_result(
    *,
    decision_item_id: str,
    decision_type: str,
    decision_scope: str,
    queue_type: str,
    source_stage: str,
    source_system_key: str | None,
    requested_decision: str,
    current_decision: str,
    decision_state: str,
    guard_state: str,
    eligibility_state: str,
    policy_result: str,
    blocking: bool,
    reason_codes: Sequence[str],
    required_preconditions: Sequence[str],
    missing_preconditions: Sequence[str],
    write_allowed: bool,
    approval_allowed: bool,
    runtime_activation_allowed: bool,
    production_activation_allowed: bool,
    api_required: bool,
    frontend_required: bool,
    evidence_references: Sequence[str],
) -> dict[str, Any]:
    result = {
        "guardResultId": sha256_digest(
            {"contractVersion": CONTRACT_VERSION, "decisionItemId": decision_item_id, "requestedDecision": requested_decision}
        ),
        "decisionItemId": decision_item_id,
        "decisionType": decision_type,
        "decisionScope": decision_scope,
        "queueType": queue_type,
        "sourceStage": source_stage,
        "sourceSystemKey": source_system_key,
        "requestedDecision": requested_decision,
        "currentDecision": current_decision,
        "decisionState": decision_state,
        "guardState": guard_state,
        "eligibilityState": eligibility_state,
        "policyResult": policy_result,
        "blocking": bool(blocking),
        "reasonCodes": _sorted(reason_codes),
        "requiredPreconditions": _sorted(required_preconditions),
        "missingPreconditions": _sorted(missing_preconditions),
        "writeAllowed": bool(write_allowed),
        "approvalAllowed": bool(approval_allowed),
        "runtimeActivationAllowed": bool(runtime_activation_allowed),
        "productionActivationAllowed": bool(production_activation_allowed),
        "apiRequired": bool(api_required),
        "frontendRequired": bool(frontend_required),
        "evidenceReferences": _sorted(evidence_references),
    }
    result["deterministicDigest"] = sha256_digest({k: v for k, v in result.items() if k != "deterministicDigest"})
    return result


def build_audit_preview(
    *,
    decision_item_id: str,
    audit_event_type: str,
    audit_scope: str,
    actor_policy: str,
    before_state: str,
    proposed_after_state: str,
    write_target: str,
    write_allowed: bool,
    approval_write_allowed: bool,
    evidence_digest: str,
    policy_digest: str,
    audit_preview_state: str,
) -> dict[str, Any]:
    preview = {
        "auditPreviewId": sha256_digest(
            {"contractVersion": CONTRACT_VERSION, "decisionItemId": decision_item_id, "auditEventType": audit_event_type}
        ),
        "decisionItemId": decision_item_id,
        "auditEventType": audit_event_type,
        "auditScope": audit_scope,
        "actorPolicy": actor_policy,
        "beforeState": before_state,
        "proposedAfterState": proposed_after_state,
        "writeTarget": write_target,
        "writeAllowed": bool(write_allowed),
        "approvalWriteAllowed": bool(approval_write_allowed),
        "evidenceDigest": evidence_digest,
        "policyDigest": policy_digest,
        "auditPreviewState": audit_preview_state,
    }
    preview["deterministicDigest"] = sha256_digest({k: v for k, v in preview.items() if k != "deterministicDigest"})
    return preview


def build_guard_group(*, group_type: str, title: str, results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    group = {
        "guardGroupId": sha256_digest(
            {"contractVersion": CONTRACT_VERSION, "groupType": group_type, "ids": sorted(str(r["guardResultId"]) for r in results)}
        ),
        "groupType": group_type,
        "title": title,
        "guardResultIds": sorted(str(r["guardResultId"]) for r in results),
        "affectedSourceSystemKeys": sorted({str(r["sourceSystemKey"]) for r in results if r.get("sourceSystemKey")}),
        "eligibleCount": sum(1 for r in results if r.get("eligibilityState") == "ELIGIBLE_FOR_PREVIEW"),
        "blockedCount": sum(1 for r in results if r.get("guardState") in {"BLOCKED_BY_POLICY", "BLOCKED_BY_PRECONDITION"}),
        "writeAllowedCount": sum(1 for r in results if r.get("writeAllowed")),
        "approvalAllowedCount": sum(1 for r in results if r.get("approvalAllowed")),
    }
    group["deterministicDigest"] = sha256_digest({k: v for k, v in group.items() if k != "deterministicDigest"})
    return group


def build_source_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    ref = {"artifactType": artifact_type, "path": path, "digest": digest}
    ref["deterministicDigest"] = sha256_digest(ref)
    return ref


def build_policy_guard_projection(
    *,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    policy_guard_results: Sequence[Mapping[str, Any]],
    audit_previews: Sequence[Mapping[str, Any]],
    guard_groups: Sequence[Mapping[str, Any]],
    filters: Mapping[str, Any],
    facets: Mapping[str, Any],
    default_page: Mapping[str, Any],
    source_artifact_references: Sequence[Mapping[str, Any]],
    generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
) -> dict[str, Any]:
    projection = {
        "projectionId": sha256_digest(
            {
                "contractVersion": CONTRACT_VERSION,
                "authority": authority,
                "profileId": profile_id,
                "guardDigests": [r.get("deterministicDigest") for r in policy_guard_results],
                "auditDigests": [a.get("deterministicDigest") for a in audit_previews],
            }
        ),
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "policyGuardResults": list(policy_guard_results),
        "auditPreviews": list(audit_previews),
        "guardGroups": list(guard_groups),
        "filters": dict(filters),
        "facets": dict(facets),
        "defaultPage": dict(default_page),
        "sourceArtifactReferences": list(source_artifact_references),
        "generatedAtPolicy": generated_at_policy,
    }
    projection["deterministicDigest"] = sha256_digest(
        {k: v for k, v in projection.items() if k != "deterministicDigest"}
    )
    return projection
