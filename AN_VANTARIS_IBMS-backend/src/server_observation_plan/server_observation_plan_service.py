"""Server observation plan read-only service facade."""

from __future__ import annotations

from typing import Any, Dict

from src.server_observation_plan.server_observation_plan_provider import (
    app_server_observation,
    approval_checklist,
    db_server_observation,
    evidence_package,
    execution_sequence,
    guardrails,
    health,
    stop_conditions,
    summary,
)


class ServerObservationPlanService:
    def health(self) -> Dict[str, Any]:
        return health()

    def summary(self) -> Dict[str, Any]:
        return summary()

    def execution_sequence(self) -> Dict[str, Any]:
        return execution_sequence()

    def app_server_observation(self) -> Dict[str, Any]:
        return app_server_observation()

    def db_server_observation(self) -> Dict[str, Any]:
        return db_server_observation()

    def evidence_package(self) -> Dict[str, Any]:
        return evidence_package()

    def stop_conditions(self) -> Dict[str, Any]:
        return stop_conditions()

    def approval_checklist(self) -> Dict[str, Any]:
        return approval_checklist()

    def guardrails(self) -> Dict[str, Any]:
        return guardrails()
