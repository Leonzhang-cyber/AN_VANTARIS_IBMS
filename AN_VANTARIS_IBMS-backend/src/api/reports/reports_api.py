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
    verification_status = request.args.get("verificationStatus")
    result = _service.list_audit(
        limit=limit,
        event_type=event_type,
        report_id=report_id,
        verification_status=verification_status,
    )
    return Result.success(data=result)


@api_bp.route("/v1/reports/audit/verify", methods=["GET"])
def reports_audit_verify():
    limit = request.args.get("limit")
    try:
        parsed_limit = int(limit) if limit is not None else None
    except (TypeError, ValueError):
        parsed_limit = None
    result = _service.verify_audit(limit=parsed_limit)
    return Result.success(data=result)


@api_bp.route("/v1/reports/audit/retention-policy", methods=["GET"])
def reports_audit_retention_policy():
    result = _service.get_audit_retention_policy()
    return Result.success(data=result)


@api_bp.route("/v1/reports/audit/<string:audit_id>", methods=["GET"])
def reports_audit_detail(audit_id: str):
    result, error = _service.get_audit_detail(audit_id)
    if error:
        return Result.error(code=error[0], message=error[1])
    return Result.success(data=result)


def _reports_ga_r13_result(section: str):
    return Result.success(data=_service.get_ga_r13_section(section))


@api_bp.route("/one/reports/customer-demo-pack", methods=["GET"])
@api_bp.route("/v1/one/reports/customer-demo-pack", methods=["GET"])
def reports_ga_r13_customer_demo_pack():
    return Result.success(data=_service.get_ga_r13_workspace())


@api_bp.route("/one/reports/export-center", methods=["GET"])
@api_bp.route("/v1/one/reports/export-center", methods=["GET"])
def reports_ga_r13_export_center():
    return _reports_ga_r13_result("export-center")


@api_bp.route("/one/reports/report-library", methods=["GET"])
@api_bp.route("/v1/one/reports/report-library", methods=["GET"])
def reports_ga_r13_report_library():
    return _reports_ga_r13_result("report-library")


@api_bp.route("/one/reports/umms-maintenance", methods=["GET"])
@api_bp.route("/v1/one/reports/umms-maintenance", methods=["GET"])
def reports_ga_r13_umms_maintenance():
    return _reports_ga_r13_result("umms-maintenance")


@api_bp.route("/one/reports/uhmi-system-status", methods=["GET"])
@api_bp.route("/v1/one/reports/uhmi-system-status", methods=["GET"])
def reports_ga_r13_uhmi_system_status():
    return _reports_ga_r13_result("uhmi-system-status")


@api_bp.route("/one/reports/ucde-evidence", methods=["GET"])
@api_bp.route("/v1/one/reports/ucde-evidence", methods=["GET"])
def reports_ga_r13_ucde_evidence():
    return _reports_ga_r13_result("ucde-evidence")


@api_bp.route("/one/reports/customer-delivery-handoff", methods=["GET"])
@api_bp.route("/v1/one/reports/customer-delivery-handoff", methods=["GET"])
def reports_ga_r13_customer_delivery_handoff():
    return _reports_ga_r13_result("customer-delivery-handoff")


@api_bp.route("/one/reports/foundation-diagnostics", methods=["GET"])
@api_bp.route("/v1/one/reports/foundation-diagnostics", methods=["GET"])
def reports_ga_r13_foundation_diagnostics():
    return _reports_ga_r13_result("foundation-diagnostics")


@api_bp.route("/one/reports/package-readiness", methods=["GET"])
@api_bp.route("/v1/one/reports/package-readiness", methods=["GET"])
def reports_ga_r13_package_readiness():
    return _reports_ga_r13_result("package-readiness")


@api_bp.route("/one/reports/audit-compliance", methods=["GET"])
@api_bp.route("/v1/one/reports/audit-compliance", methods=["GET"])
def reports_ga_r13_audit_compliance():
    return _reports_ga_r13_result("audit-compliance")


@api_bp.route("/one/reports/export-queue-preview", methods=["GET"])
@api_bp.route("/v1/one/reports/export-queue-preview", methods=["GET"])
def reports_ga_r13_export_queue_preview():
    return _reports_ga_r13_result("export-queue-preview")


@api_bp.route("/one/reports/guardrails", methods=["GET"])
@api_bp.route("/v1/one/reports/guardrails", methods=["GET"])
def reports_ga_r13_guardrails():
    return _reports_ga_r13_result("guardrails")
