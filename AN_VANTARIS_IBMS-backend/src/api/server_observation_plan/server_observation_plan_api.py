"""Server observation plan read-only API."""

from __future__ import annotations

from src.api import api_bp
from src.common.models.response import Result
from src.server_observation_plan.server_observation_plan_service import ServerObservationPlanService


_service = ServerObservationPlanService()


@api_bp.route("/v1/one/server-observation-plan/health", methods=["GET"])
def server_observation_plan_health():
    return Result.success(data=_service.health())


@api_bp.route("/v1/one/server-observation-plan/summary", methods=["GET"])
def server_observation_plan_summary():
    return Result.success(data=_service.summary())


@api_bp.route("/v1/one/server-observation-plan/execution-sequence", methods=["GET"])
def server_observation_plan_execution_sequence():
    return Result.success(data=_service.execution_sequence())


@api_bp.route("/v1/one/server-observation-plan/app-server-observation", methods=["GET"])
def server_observation_plan_app_server_observation():
    return Result.success(data=_service.app_server_observation())


@api_bp.route("/v1/one/server-observation-plan/db-server-observation", methods=["GET"])
def server_observation_plan_db_server_observation():
    return Result.success(data=_service.db_server_observation())


@api_bp.route("/v1/one/server-observation-plan/evidence-package", methods=["GET"])
def server_observation_plan_evidence_package():
    return Result.success(data=_service.evidence_package())


@api_bp.route("/v1/one/server-observation-plan/stop-conditions", methods=["GET"])
def server_observation_plan_stop_conditions():
    return Result.success(data=_service.stop_conditions())


@api_bp.route("/v1/one/server-observation-plan/approval-checklist", methods=["GET"])
def server_observation_plan_approval_checklist():
    return Result.success(data=_service.approval_checklist())


@api_bp.route("/v1/one/server-observation-plan/guardrails", methods=["GET"])
def server_observation_plan_guardrails():
    return Result.success(data=_service.guardrails())
