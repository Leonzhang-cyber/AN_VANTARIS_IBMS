"""NexusAI read-only branch audit service facade."""

from __future__ import annotations

from typing import Any, Dict

from src.nexus_ai.nexus_branch_audit_provider import (
    commits,
    customer_demo_impact,
    evidence_linkage,
    guardrails,
    health,
    modules,
    risks,
    summary,
)


class NexusBranchAuditService:
    def health(self) -> Dict[str, Any]:
        return health()

    def summary(self) -> Dict[str, Any]:
        return summary()

    def commits(self) -> Dict[str, Any]:
        return commits()

    def modules(self) -> Dict[str, Any]:
        return modules()

    def risks(self) -> Dict[str, Any]:
        return risks()

    def evidence_linkage(self) -> Dict[str, Any]:
        return evidence_linkage()

    def customer_demo_impact(self) -> Dict[str, Any]:
        return customer_demo_impact()

    def guardrails(self) -> Dict[str, Any]:
        return guardrails()

