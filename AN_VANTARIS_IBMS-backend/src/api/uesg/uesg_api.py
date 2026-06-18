"""UESG sustainability API skeleton."""

from __future__ import annotations

from flask import request

from src.api import api_bp
from src.common.models.response import Result
from src.uesg.uesg_service import UesgSustainabilityService


_service = UesgSustainabilityService()


@api_bp.route("/v1/uesg/health", methods=["GET"])
def uesg_health():
    return Result.success(data=_service.get_uesg_health())


@api_bp.route("/v1/uesg/metrics/summary", methods=["GET"])
def uesg_metrics_summary():
    return Result.success(data=_service.get_metrics_summary())


@api_bp.route("/v1/uesg/metrics/breakdown", methods=["GET"])
def uesg_metrics_breakdown():
    return Result.success(data=_service.get_metrics_breakdown())


@api_bp.route("/v1/uesg/associations", methods=["GET"])
def uesg_associations():
    return Result.success(data=_service.get_associations())


@api_bp.route("/v1/uesg/metrics/<string:metric_id>", methods=["GET"])
def uesg_metric_detail(metric_id: str):
    data = _service.get_metric_detail(metric_id)
    if not data:
        return Result.error(code=404, message="metricId not found")
    return Result.success(data=data)


@api_bp.route("/v1/uesg/metrics", methods=["GET"])
def uesg_metrics():
    filters = {
        "metricCategory": request.args.get("metricCategory"),
        "metricScope": request.args.get("metricScope"),
        "metricPeriod": request.args.get("metricPeriod"),
        "siteId": request.args.get("siteId"),
        "systemId": request.args.get("systemId"),
        "dataQuality": request.args.get("dataQuality"),
    }
    return Result.success(data=_service.list_metrics(filters=filters))

