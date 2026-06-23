"""Server precheck read-only API."""

from __future__ import annotations

from src.api import api_bp
from src.common.models.response import Result
from src.server_precheck.server_precheck_service import ServerPrecheckService


_service = ServerPrecheckService()


@api_bp.route("/v1/one/server-precheck/health", methods=["GET"])
def server_precheck_health():
    return Result.success(data=_service.health())


@api_bp.route("/v1/one/server-precheck/summary", methods=["GET"])
def server_precheck_summary():
    return Result.success(data=_service.summary())


@api_bp.route("/v1/one/server-precheck/server-plan", methods=["GET"])
def server_precheck_server_plan():
    return Result.success(data=_service.server_plan())


@api_bp.route("/v1/one/server-precheck/app-server", methods=["GET"])
def server_precheck_app_server():
    return Result.success(data=_service.app_server())


@api_bp.route("/v1/one/server-precheck/db-server", methods=["GET"])
def server_precheck_db_server():
    return Result.success(data=_service.db_server())


@api_bp.route("/v1/one/server-precheck/checklist", methods=["GET"])
def server_precheck_checklist():
    return Result.success(data=_service.checklist())


@api_bp.route("/v1/one/server-precheck/blockers", methods=["GET"])
def server_precheck_blockers():
    return Result.success(data=_service.blockers())


@api_bp.route("/v1/one/server-precheck/handoff-readiness", methods=["GET"])
def server_precheck_handoff_readiness():
    return Result.success(data=_service.handoff_readiness())


@api_bp.route("/v1/one/server-precheck/guardrails", methods=["GET"])
def server_precheck_guardrails():
    return Result.success(data=_service.guardrails())

