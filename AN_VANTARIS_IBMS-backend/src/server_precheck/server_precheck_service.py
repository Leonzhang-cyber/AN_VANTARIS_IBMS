"""Server precheck read-only service facade."""

from __future__ import annotations

from typing import Any, Dict

from src.server_precheck.server_precheck_provider import (
    app_server,
    blockers,
    checklist,
    db_server,
    guardrails,
    handoff_readiness,
    health,
    server_plan,
    summary,
)


class ServerPrecheckService:
    def health(self) -> Dict[str, Any]:
        return health()

    def summary(self) -> Dict[str, Any]:
        return summary()

    def server_plan(self) -> Dict[str, Any]:
        return server_plan()

    def app_server(self) -> Dict[str, Any]:
        return app_server()

    def db_server(self) -> Dict[str, Any]:
        return db_server()

    def checklist(self) -> Dict[str, Any]:
        return checklist()

    def blockers(self) -> Dict[str, Any]:
        return blockers()

    def handoff_readiness(self) -> Dict[str, Any]:
        return handoff_readiness()

    def guardrails(self) -> Dict[str, Any]:
        return guardrails()

