"""UMMS maintenance API skeleton."""

from __future__ import annotations

from flask import request

from src.api import api_bp
from src.common.models.response import Result
from src.umms.umms_service import UmmsMaintenanceService


_service = UmmsMaintenanceService()


@api_bp.route("/v1/umms/health", methods=["GET"])
def umms_health():
    return Result.success(data=_service.get_umms_health())


@api_bp.route("/v1/umms/work-orders", methods=["GET"])
def umms_work_orders():
    filters = {
        "workOrderType": request.args.get("workOrderType"),
        "workOrderCategory": request.args.get("workOrderCategory"),
        "workOrderStatus": request.args.get("workOrderStatus"),
        "priority": request.args.get("priority"),
        "siteId": request.args.get("siteId"),
        "systemId": request.args.get("systemId"),
        "assetId": request.args.get("assetId"),
    }
    return Result.success(data=_service.list_work_orders(filters=filters))


@api_bp.route("/v1/umms/work-orders/summary", methods=["GET"])
def umms_work_orders_summary():
    return Result.success(data=_service.get_maintenance_summary())


@api_bp.route("/v1/umms/work-orders/breakdown", methods=["GET"])
def umms_work_orders_breakdown():
    return Result.success(data=_service.get_work_order_breakdown())


@api_bp.route("/v1/umms/associations", methods=["GET"])
def umms_associations():
    return Result.success(data=_service.get_maintenance_associations())


@api_bp.route("/v1/umms/work-orders/<string:work_order_id>", methods=["GET"])
def umms_work_order_detail(work_order_id: str):
    data = _service.get_work_order_detail(work_order_id)
    if not data:
        return Result.error(code=404, message="workOrderId not found")
    return Result.success(data=data)


@api_bp.route("/v1/one/umms/package-entry", methods=["GET"])
def umms_one_package_entry():
    return Result.success(data=_service.get_package_entry_projection())


@api_bp.route("/v1/one/umms/stakeholder-review", methods=["GET"])
def umms_one_stakeholder_review():
    return Result.success(data=_service.get_stakeholder_review_projection())


@api_bp.route("/v1/one/umms/readiness-summary", methods=["GET"])
def umms_one_readiness_summary():
    return Result.success(data=_service.get_readiness_summary_projection())


@api_bp.route("/v1/one/umms/customer-core-functions", methods=["GET"])
def umms_one_customer_core_functions():
    return Result.success(data=_service.get_customer_core_functions_projection())


@api_bp.route("/v1/one/umms/safety-posture", methods=["GET"])
def umms_one_safety_posture():
    return Result.success(data=_service.get_safety_posture_projection())


def _umms_ga_r2_response(section: str):
    return Result.success(data=_service.get_ga_r2_section(section))


@api_bp.route("/one/umms/workspace", methods=["GET"])
@api_bp.route("/v1/one/umms/workspace", methods=["GET"])
def umms_ga_r2_workspace():
    return Result.success(data=_service.get_ga_r2_workspace())


@api_bp.route("/one/umms/overview", methods=["GET"])
@api_bp.route("/v1/one/umms/overview", methods=["GET"])
def umms_ga_r2_overview():
    return _umms_ga_r2_response("overview")


@api_bp.route("/one/umms/work-orders", methods=["GET"])
@api_bp.route("/v1/one/umms/work-orders", methods=["GET"])
def umms_ga_r2_work_orders():
    return _umms_ga_r2_response("work-orders")


@api_bp.route("/one/umms/tasks", methods=["GET"])
@api_bp.route("/v1/one/umms/tasks", methods=["GET"])
def umms_ga_r2_tasks():
    return _umms_ga_r2_response("tasks")


@api_bp.route("/one/umms/maintenance-plans", methods=["GET"])
@api_bp.route("/v1/one/umms/maintenance-plans", methods=["GET"])
def umms_ga_r2_maintenance_plans():
    return _umms_ga_r2_response("maintenance-plans")


@api_bp.route("/one/umms/preventive-maintenance", methods=["GET"])
@api_bp.route("/v1/one/umms/preventive-maintenance", methods=["GET"])
def umms_ga_r2_preventive_maintenance():
    return _umms_ga_r2_response("preventive-maintenance")


@api_bp.route("/one/umms/corrective-maintenance", methods=["GET"])
@api_bp.route("/v1/one/umms/corrective-maintenance", methods=["GET"])
def umms_ga_r2_corrective_maintenance():
    return _umms_ga_r2_response("corrective-maintenance")


@api_bp.route("/one/umms/engineer-dispatch", methods=["GET"])
@api_bp.route("/v1/one/umms/engineer-dispatch", methods=["GET"])
def umms_ga_r2_engineer_dispatch():
    return _umms_ga_r2_response("engineer-dispatch")


@api_bp.route("/one/umms/asset-context", methods=["GET"])
@api_bp.route("/v1/one/umms/asset-context", methods=["GET"])
def umms_ga_r2_asset_context():
    return _umms_ga_r2_response("asset-context")


@api_bp.route("/one/umms/event-context", methods=["GET"])
@api_bp.route("/v1/one/umms/event-context", methods=["GET"])
def umms_ga_r2_event_context():
    return _umms_ga_r2_response("event-context")


@api_bp.route("/one/umms/evidence-linkage", methods=["GET"])
@api_bp.route("/v1/one/umms/evidence-linkage", methods=["GET"])
def umms_ga_r2_evidence_linkage():
    return _umms_ga_r2_response("evidence-linkage")


@api_bp.route("/one/umms/report-linkage", methods=["GET"])
@api_bp.route("/v1/one/umms/report-linkage", methods=["GET"])
def umms_ga_r2_report_linkage():
    return _umms_ga_r2_response("report-linkage")


@api_bp.route("/one/umms/customer-acceptance", methods=["GET"])
@api_bp.route("/v1/one/umms/customer-acceptance", methods=["GET"])
def umms_ga_r2_customer_acceptance():
    return _umms_ga_r2_response("customer-acceptance")


@api_bp.route("/one/umms/role-views", methods=["GET"])
@api_bp.route("/v1/one/umms/role-views", methods=["GET"])
def umms_ga_r2_role_views():
    return _umms_ga_r2_response("role-views")


@api_bp.route("/one/umms/guardrails", methods=["GET"])
@api_bp.route("/v1/one/umms/guardrails", methods=["GET"])
def umms_ga_r2_guardrails():
    return _umms_ga_r2_response("guardrails")
