"""Server access window plan read-only API."""

from __future__ import annotations

from src.api import api_bp
from src.common.models.response import Result
from src.server_access_plan.server_access_plan_service import ServerAccessPlanService


_service = ServerAccessPlanService()


@api_bp.route("/v1/one/server-access-plan/health", methods=["GET"])
def server_access_plan_health():
    return Result.success(data=_service.health())


@api_bp.route("/v1/one/server-access-plan/summary", methods=["GET"])
def server_access_plan_summary():
    return Result.success(data=_service.summary())


@api_bp.route("/v1/one/server-access-plan/access-window", methods=["GET"])
def server_access_plan_access_window():
    return Result.success(data=_service.access_window())


@api_bp.route("/v1/one/server-access-plan/approval-boundary", methods=["GET"])
def server_access_plan_approval_boundary():
    return Result.success(data=_service.approval_boundary())


@api_bp.route("/v1/one/server-access-plan/allowed-readonly-commands", methods=["GET"])
def server_access_plan_allowed_readonly_commands():
    return Result.success(data=_service.allowed_readonly_commands())


@api_bp.route("/v1/one/server-access-plan/evidence-capture", methods=["GET"])
def server_access_plan_evidence_capture():
    return Result.success(data=_service.evidence_capture())


@api_bp.route("/v1/one/server-access-plan/stop-conditions", methods=["GET"])
def server_access_plan_stop_conditions():
    return Result.success(data=_service.stop_conditions())


@api_bp.route("/v1/one/server-access-plan/r3-readiness", methods=["GET"])
def server_access_plan_r3_readiness():
    return Result.success(data=_service.r3_readiness())


@api_bp.route("/v1/one/server-access-plan/guardrails", methods=["GET"])
def server_access_plan_guardrails():
    return Result.success(data=_service.guardrails())

