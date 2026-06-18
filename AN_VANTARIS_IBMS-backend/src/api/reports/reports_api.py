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


@api_bp.route("/v1/reports/export/manifest", methods=["POST"])
def reports_export_manifest():
    payload = request.get_json(silent=True) or {}
    result, error = _service.build_export_manifest_preview(payload)
    if error:
        return Result.error(code=error[0], message=error[1])
    return Result.success(data=result)


@api_bp.route("/v1/reports/audit", methods=["GET"])
def reports_audit_list():
    limit = request.args.get("limit", 50)
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 50
    event_type = request.args.get("eventType")
    report_id = request.args.get("reportId")
    result = _service.list_audit(limit=limit, event_type=event_type, report_id=report_id)
    return Result.success(data=result)


@api_bp.route("/v1/reports/audit/<string:audit_id>", methods=["GET"])
def reports_audit_detail(audit_id: str):
    result, error = _service.get_audit_detail(audit_id)
    if error:
        return Result.error(code=error[0], message=error[1])
    return Result.success(data=result)

