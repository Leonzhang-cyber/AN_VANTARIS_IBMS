"""UConsole platform operations API skeleton."""

from __future__ import annotations

from src.api import api_bp
from src.common.models.response import Result
from src.console.console_service import ConsoleService


_service = ConsoleService()


@api_bp.route("/v1/console/health", methods=["GET"])
def console_health():
    return Result.success(data=_service.get_console_health())


@api_bp.route("/v1/console/modules", methods=["GET"])
def console_modules():
    return Result.success(data={"items": _service.get_platform_modules_summary()})


@api_bp.route("/v1/console/operations/summary", methods=["GET"])
def console_operations_summary():
    return Result.success(data=_service.get_operations_dashboard_summary())


@api_bp.route("/v1/console/reports/readiness", methods=["GET"])
def console_reports_readiness():
    return Result.success(data=_service.get_reports_readiness_snapshot())

