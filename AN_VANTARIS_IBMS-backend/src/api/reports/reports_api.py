"""IBMS-neutral Reports API runtime skeleton."""

from __future__ import annotations

from flask import request

from src.api import api_bp
from src.common.models.response import Result
from src.reports.reports_service import ReportsService


_service = ReportsService()


@api_bp.route("/v1/reports/health", methods=["GET"])
def reports_health():
    return Result.success(
        data={
            "module": "reports",
            "status": "ok",
            "runtimeMode": "skeleton",
            "provider": "local-mock-provider",
            "sourceSemantics": "ibms-neutral",
        }
    )


@api_bp.route("/v1/reports/catalog", methods=["GET"])
def reports_catalog_list():
    return Result.success(data={"items": _service.list_catalog(), "total": len(_service.list_catalog())})


@api_bp.route("/v1/reports/catalog/<string:report_id>", methods=["GET"])
def reports_catalog_detail(report_id: str):
    catalog = _service.get_catalog(report_id)
    if not catalog:
        return Result.error(code=404, message="reportId not found")
    return Result.success(data=catalog)


@api_bp.route("/v1/reports/query", methods=["POST"])
def reports_query():
    payload = request.get_json(silent=True) or {}
    result, error = _service.query_report(payload)
    if error:
        return Result.error(code=error[0], message=error[1])
    return Result.success(data=result)

