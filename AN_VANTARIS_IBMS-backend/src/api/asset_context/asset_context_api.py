"""Asset Context read-only API."""

from __future__ import annotations

from src.api import api_bp
from src.asset_context.asset_context_service import AssetContextService
from src.common.models.response import Result


_service = AssetContextService()


@api_bp.route("/v1/one/asset-context/health", methods=["GET"])
def asset_context_health():
    return Result.success(data=_service.health())


@api_bp.route("/v1/one/asset-context/summary", methods=["GET"])
def asset_context_summary():
    return Result.success(data=_service.summary())


@api_bp.route("/v1/one/asset-context/assets", methods=["GET"])
def asset_context_assets():
    return Result.success(data=_service.assets())


@api_bp.route("/v1/one/asset-context/assets/<string:asset_id>", methods=["GET"])
def asset_context_asset_detail(asset_id: str):
    data = _service.asset_detail(asset_id)
    if not data:
        return Result.error(code=404, message="assetId not found")
    return Result.success(data=data)


@api_bp.route("/v1/one/asset-context/assets/<string:asset_id>/links", methods=["GET"])
def asset_context_asset_links(asset_id: str):
    data = _service.asset_links(asset_id)
    if not data:
        return Result.error(code=404, message="assetId not found")
    return Result.success(data=data)


@api_bp.route("/v1/one/asset-context/graph", methods=["GET"])
def asset_context_graph():
    return Result.success(data=_service.graph())


@api_bp.route("/v1/one/asset-context/guardrails", methods=["GET"])
def asset_context_guardrails():
    return Result.success(data=_service.guardrails())

