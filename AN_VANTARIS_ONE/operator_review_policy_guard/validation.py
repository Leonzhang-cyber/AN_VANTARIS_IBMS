"""Validation helpers for Operator Review Policy Guard projections."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import OperatorReviewPolicyGuardError


def validate_policy_guard_projection(projection: Mapping[str, Any]) -> None:
    summary = projection.get("summary", {})
    if len(projection.get("policyGuardResults", [])) != 46:
        raise OperatorReviewPolicyGuardError("GUARD_COUNT_INVALID", "expected 46 policy guard results")
    if len(projection.get("auditPreviews", [])) != 46:
        raise OperatorReviewPolicyGuardError("AUDIT_PREVIEW_COUNT_INVALID", "expected 46 audit previews")
    if len(projection.get("guardGroups", [])) != 8:
        raise OperatorReviewPolicyGuardError("GUARD_GROUP_COUNT_INVALID", "expected 8 guard groups")
    for key in ("writeAllowedCount", "approvalAllowedCount", "runtimeActivationAllowedCount", "productionActivationAllowedCount", "decisionWriteCount", "approvalWriteCount", "canonicalWriteCount", "databaseWriteCount"):
        if summary.get(key) != 0:
            raise OperatorReviewPolicyGuardError("FORBIDDEN_WRITE_OR_ACTIVATION_COUNT", f"{key} must be zero")
    for key in ("apiEnabled", "frontendEnabled", "pushAllowed", "containsCustomerAssetIdentifiers"):
        if summary.get(key) is not False:
            raise OperatorReviewPolicyGuardError("FORBIDDEN_RUNTIME_CAPABILITY", f"{key} must be false")
    if any(result.get("writeAllowed") or result.get("approvalAllowed") for result in projection.get("policyGuardResults", [])):
        raise OperatorReviewPolicyGuardError("GUARD_ALLOWED_WRITE", "guard results must not allow writes or approvals")


def validate_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = (
        "sql" + "alchemy",
        "fla" + "sk",
        "req" + "uests.",
        "url" + "lib",
        "soc" + "ket",
        "blue" + "print",
        "rea" + "ct",
        "src." + "ufms",
        "src." + "umms",
    )
    found = [token for token in forbidden if token in lowered]
    if found:
        raise OperatorReviewPolicyGuardError("BOUNDARY_VIOLATION", ", ".join(found))
