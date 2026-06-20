"""Airport Operator Review Decision Audit and Policy Guard Projection."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from operator_review_policy_guard.audit_preview import build_read_only_audit_preview
from operator_review_policy_guard.enums import AuditPreviewState
from operator_review_policy_guard.models import (
    build_guard_group,
    build_policy_guard_projection,
    build_policy_guard_result,
    build_source_artifact_reference,
)
from operator_review_policy_guard.policy import evaluate_decision_policy
from operator_review_policy_guard.projection import build_facets, build_filters, paginate_guard_results, sort_guard_results
from operator_review_policy_guard.validation import validate_policy_guard_projection
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A4-03"
PROFILE_ID = "airport-operator-review-policy-guard-profile-v1"
IMPLEMENTATION_STATUS = "OPERATOR_REVIEW_DECISION_AUDIT_AND_POLICY_GUARD_COMPLETE"
READINESS_OUTCOME = "OPERATOR_REVIEW_POLICY_GUARD_READY_FOR_READ_ONLY_PREVIEW"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
DECISIONS = PROJECTIONS_DIR / "airport-operator-review-decisions.v1.json"
QUEUE = PROJECTIONS_DIR / "airport-uconsole-operator-review-queue.v1.json"
A3_RELEASE = PROJECTIONS_DIR / "airport-a3-readiness-release-gate.v1.json"

GROUPS = (
    ("ALL_DECISION_GUARDS", "All decision policy guards", None),
    ("SOURCE_SYSTEM_GUARDS", "Source-system policy guards", "SOURCE_SYSTEM_QUEUE"),
    ("ASSET_RESOLUTION_GUARDS", "Asset-resolution policy guards", "ASSET_RESOLUTION_QUEUE"),
    ("ALARM_EVENT_GUARDS", "Alarm/Event policy guards", "ALARM_EVENT_QUEUE"),
    ("FAULTCASE_GUARDS", "FaultCase policy guards", "FAULTCASE_QUEUE"),
    ("WORKORDER_INTENT_GUARDS", "WorkOrderIntent policy guards", "WORKORDER_INTENT_QUEUE"),
    ("EVIDENCE_INVESTIGATION_GUARDS", "Evidence investigation policy guards", "EVIDENCE_INVESTIGATION_QUEUE"),
    ("RELEASE_GATE_GUARDS", "Release gate policy guards", "RELEASE_GATE_QUEUE"),
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_reference(path: Path, artifact_type: str) -> dict[str, Any]:
    return build_source_artifact_reference(
        artifact_type=artifact_type,
        path=str(path.relative_to(ROOT)),
        digest=sha256_digest(_load(path)),
    )


def _queue_by_decision_id(queue_projection: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {str(row["decisionItemId"]): row for row in queue_projection.get("queueRows", [])}


def _build_guard(decision: Mapping[str, Any], queue_row: Mapping[str, Any]) -> dict[str, Any]:
    policy = evaluate_decision_policy(decision)
    return build_policy_guard_result(
        decision_item_id=str(decision["decisionItemId"]),
        decision_type=str(decision["decisionType"]),
        decision_scope=str(decision["decisionScope"]),
        queue_type=str(queue_row["queueType"]),
        source_stage=str(decision["sourceStage"]),
        source_system_key=decision.get("sourceSystemKey"),
        requested_decision="PREVIEW_ONLY",
        current_decision=str(decision.get("currentDecision", "KEEP_PENDING")),
        decision_state=str(decision.get("decisionState", "PENDING")),
        guard_state=str(policy["guardState"]),
        eligibility_state=str(policy["eligibilityState"]),
        policy_result=str(policy["policyResult"]),
        blocking=True,
        reason_codes=list(policy["reasonCodes"]),
        required_preconditions=list(policy["requiredPreconditions"]),
        missing_preconditions=list(policy["missingPreconditions"]),
        write_allowed=False,
        approval_allowed=False,
        runtime_activation_allowed=False,
        production_activation_allowed=False,
        api_required=False,
        frontend_required=False,
        evidence_references=list(decision.get("evidenceReferences", [])),
    )


def _build_results_and_previews() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    decisions = _load(DECISIONS)
    queue_projection = _load(QUEUE)
    queue_rows = _queue_by_decision_id(queue_projection)
    results: list[dict[str, Any]] = []
    previews: list[dict[str, Any]] = []
    for decision in sorted(decisions.get("decisionItems", []), key=lambda item: (item["decisionType"], item.get("sourceSystemKey") or "", item["decisionItemId"])):
        guard = _build_guard(decision, queue_rows[str(decision["decisionItemId"])])
        results.append(guard)
        previews.append(build_read_only_audit_preview(decision, str(guard["deterministicDigest"])))
    return sort_guard_results(results), sorted(previews, key=lambda preview: (preview["decisionItemId"], preview["auditPreviewId"]))


def _build_groups(results: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for group_type, title, queue_type in GROUPS:
        group_results = list(results) if queue_type is None else [result for result in results if result["queueType"] == queue_type]
        groups.append(build_guard_group(group_type=group_type, title=title, results=group_results))
    return groups


def _summary(results: Sequence[Mapping[str, Any]], previews: Sequence[Mapping[str, Any]], groups: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "decisionItemCount": len(results),
        "policyGuardResultCount": len(results),
        "auditPreviewCount": len(previews),
        "guardGroupCount": len(groups),
        "eligibleForPreviewCount": sum(1 for result in results if result["eligibilityState"] == "ELIGIBLE_FOR_PREVIEW"),
        "eligibleForExecutionCount": 0,
        "blockedByPolicyCount": sum(1 for result in results if result["guardState"] == "BLOCKED_BY_POLICY"),
        "writeAllowedCount": sum(1 for result in results if result["writeAllowed"]),
        "approvalAllowedCount": sum(1 for result in results if result["approvalAllowed"]),
        "runtimeActivationAllowedCount": sum(1 for result in results if result["runtimeActivationAllowed"]),
        "productionActivationAllowedCount": sum(1 for result in results if result["productionActivationAllowed"]),
        "auditPreviewGeneratedCount": sum(1 for preview in previews if preview["auditPreviewState"] == AuditPreviewState.GENERATED_READ_ONLY.value),
        "decisionWriteCount": 0,
        "approvalWriteCount": 0,
        "canonicalWriteCount": 0,
        "databaseWriteCount": 0,
        "apiEnabled": False,
        "frontendEnabled": False,
        "pushAllowed": False,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
    }


def build_airport_operator_review_policy_guard_projection() -> dict[str, Any]:
    results, previews = _build_results_and_previews()
    groups = _build_groups(results)
    projection = build_policy_guard_projection(
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=_summary(results, previews, groups),
        policy_guard_results=results,
        audit_previews=previews,
        guard_groups=groups,
        filters=build_filters(results, previews),
        facets=build_facets(results, previews),
        default_page=paginate_guard_results(results, page_size=25),
        source_artifact_references=[
            _artifact_reference(DECISIONS, "OPERATOR_REVIEW_DECISIONS"),
            _artifact_reference(QUEUE, "UCONSOLE_OPERATOR_REVIEW_QUEUE"),
            _artifact_reference(A3_RELEASE, "A3_READINESS_RELEASE_GATE"),
        ],
    )
    validate_policy_guard_projection(projection)
    return projection
