"""Assets & Topology API skeleton."""

from __future__ import annotations

from flask import request

from src.api import api_bp
from src.assets.assets_service import AssetsTopologyService
from src.common.models.response import Result


_service = AssetsTopologyService()


@api_bp.route("/v1/assets/health", methods=["GET"])
def assets_health():
    return Result.success(data=_service.get_assets_health())


@api_bp.route("/v1/assets/summary", methods=["GET"])
def assets_summary():
    return Result.success(data=_service.get_assets_summary())


@api_bp.route("/v1/assets/topology", methods=["GET"])
def assets_topology():
    return Result.success(data=_service.get_topology())


@api_bp.route("/v1/assets/<string:asset_id>/relationships", methods=["GET"])
def asset_relationships(asset_id: str):
    data, error = _service.get_asset_relationships(asset_id)
    if error:
        return Result.error(code=error[0], message=error[1])
    return Result.success(data=data)


@api_bp.route("/v1/assets/<string:asset_id>/lineage", methods=["GET"])
def asset_lineage(asset_id: str):
    data, error = _service.get_asset_topology_lineage(asset_id)
    if error:
        return Result.error(code=error[0], message=error[1])
    return Result.success(data=data)


@api_bp.route("/v1/assets/<string:asset_id>/impact", methods=["GET"])
def asset_impact(asset_id: str):
    data, error = _service.get_asset_impact(asset_id)
    if error:
        return Result.error(code=error[0], message=error[1])
    return Result.success(data=data)


@api_bp.route("/v1/assets/<string:asset_id>", methods=["GET"])
def asset_detail(asset_id: str):
    data = _service.get_asset_detail(asset_id)
    if not data:
        return Result.error(code=404, message="assetId not found")
    return Result.success(data=data)


@api_bp.route("/v1/assets", methods=["GET"])
def assets_list():
    filters = {
        "assetType": request.args.get("assetType"),
        "assetCategory": request.args.get("assetCategory"),
        "lifecycleStatus": request.args.get("lifecycleStatus"),
        "operationalStatus": request.args.get("operationalStatus"),
        "siteId": request.args.get("siteId"),
        "systemId": request.args.get("systemId"),
    }
    return Result.success(data=_service.list_assets(filters=filters))

