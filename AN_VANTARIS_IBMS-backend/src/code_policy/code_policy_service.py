"""CODE Policy Gate read-only service facade."""

from __future__ import annotations

from typing import Any, Dict

from src.code_policy.code_policy_provider import (
    approval_boundary,
    control_path,
    evidence_linkage,
    execution_boundary,
    guardrails,
    health,
    policy_gates,
    summary,
)


class CodePolicyService:
    def health(self) -> Dict[str, Any]:
        return health()

    def summary(self) -> Dict[str, Any]:
        return summary()

    def policy_gates(self) -> Dict[str, Any]:
        return policy_gates()

    def execution_boundary(self) -> Dict[str, Any]:
        return execution_boundary()

    def approval_boundary(self) -> Dict[str, Any]:
        return approval_boundary()

    def evidence_linkage(self) -> Dict[str, Any]:
        return evidence_linkage()

    def control_path(self) -> Dict[str, Any]:
        return control_path()

    def guardrails(self) -> Dict[str, Any]:
        return guardrails()

