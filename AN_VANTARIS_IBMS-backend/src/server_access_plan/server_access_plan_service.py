"""Server access window plan read-only service facade."""

from __future__ import annotations

from typing import Any, Dict

from src.server_access_plan.server_access_plan_provider import (
    access_window,
    allowed_readonly_commands,
    approval_boundary,
    evidence_capture,
    guardrails,
    health,
    r3_readiness,
    stop_conditions,
    summary,
)


class ServerAccessPlanService:
    def health(self) -> Dict[str, Any]:
        return health()

    def summary(self) -> Dict[str, Any]:
        return summary()

    def access_window(self) -> Dict[str, Any]:
        return access_window()

    def approval_boundary(self) -> Dict[str, Any]:
        return approval_boundary()

    def allowed_readonly_commands(self) -> Dict[str, Any]:
        return allowed_readonly_commands()

    def evidence_capture(self) -> Dict[str, Any]:
        return evidence_capture()

    def stop_conditions(self) -> Dict[str, Any]:
        return stop_conditions()

    def r3_readiness(self) -> Dict[str, Any]:
        return r3_readiness()

    def guardrails(self) -> Dict[str, Any]:
        return guardrails()

