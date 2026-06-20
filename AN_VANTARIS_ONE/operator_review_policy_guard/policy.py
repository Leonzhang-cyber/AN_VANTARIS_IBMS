"""Read-only policy guard rules for operator review decisions."""
from __future__ import annotations

from typing import Any, Mapping

from .enums import EligibilityState, GuardState, PolicyResult


def evaluate_decision_policy(decision: Mapping[str, Any]) -> dict[str, Any]:
    missing = [key for key in ("decisionItemId", "decisionType") if not decision.get(key)]
    approved_or_rejected = decision.get("decisionState") in {"APPROVED", "REJECTED"}
    unknown_state = decision.get("decisionState") not in {"PENDING", "READY_FOR_REVIEW", "BLOCKED", "DEFERRED", "APPROVED", "REJECTED"}
    reason_codes = ["READ_ONLY_PREVIEW_ALLOWED", "EXECUTION_NOT_AUTHORIZED", "WRITE_NOT_AUTHORIZED", "APPROVAL_NOT_AUTHORIZED"]
    if missing:
        reason_codes.append("PRECONDITION_MISSING")
    if approved_or_rejected:
        reason_codes.append("INPUT_DECISION_ALREADY_APPLIED")
    if unknown_state:
        reason_codes.append("UNKNOWN_DECISION_STATE")
    return {
        "guardState": GuardState.BLOCKED_BY_PRECONDITION.value if missing else GuardState.BLOCKED_BY_POLICY.value,
        "eligibilityState": EligibilityState.ELIGIBLE_FOR_PREVIEW.value if not missing else EligibilityState.BLOCKED.value,
        "policyResult": PolicyResult.FAIL_PRECONDITION_MISSING.value if missing else PolicyResult.FAIL_WRITE_NOT_AUTHORIZED.value,
        "reasonCodes": sorted(reason_codes),
        "requiredPreconditions": ["decisionItemId", "decisionType", "decisionState"],
        "missingPreconditions": sorted(missing),
        "writeAllowed": False,
        "approvalAllowed": False,
        "runtimeActivationAllowed": False,
        "productionActivationAllowed": False,
        "apiRequired": False,
        "frontendRequired": False,
    }
