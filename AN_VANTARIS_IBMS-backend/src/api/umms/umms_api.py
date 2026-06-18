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

