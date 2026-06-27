"""Assets & Topology API skeleton."""

from __future__ import annotations

from pathlib import Path

from flask import request

from src.api import api_bp
from src.api.asset_import_ga.asset_overlay_service import AssetOverlayService
from src.api.asset_import_ga.asset_import_service import AssetImportService, UploadFile
from src.api.asset_import_ga.evidence_audit_overlay_service import EvidenceAuditOverlayService
from src.api.asset_import_ga.fault_work_order_overlay_service import FaultWorkOrderOverlayService
from src.assets.assets_service import AssetsTopologyService
from src.common.models.response import Result


_service = AssetsTopologyService()
_asset_import_service = AssetImportService()
_asset_overlay_service = AssetOverlayService()
_fault_work_order_overlay_service = FaultWorkOrderOverlayService()
_evidence_audit_overlay_service = EvidenceAuditOverlayService(_fault_work_order_overlay_service)


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


@api_bp.route("/v1/assets/import/preview", methods=["POST"])
def asset_import_preview():
    files = request.files.getlist("file")
    uploads = []
    for file in files:
        filename = Path(file.filename or "").name
        if filename:
            uploads.append(UploadFile(source_file_name=filename, payload=file.read()))
    try:
        return Result.success(data=_asset_import_service.preview_upload(uploads))
    except ValueError as exc:
        return Result.error(code=400, message=str(exc))


@api_bp.route("/v1/assets/import/batches", methods=["GET"])
def asset_import_batches():
    return Result.success(data=_asset_import_service.list_batches())


@api_bp.route("/v1/assets/import/batches/<string:batch_id>/report", methods=["GET"])
def asset_import_batch_report(batch_id: str):
    report = _asset_import_service.get_report(batch_id)
    if report is None:
        return Result.error(code=404, message="batch not found")
    return Result.success(data=report)


@api_bp.route("/v1/assets/import/batches/<string:batch_id>/confirm", methods=["POST"])
def asset_import_batch_confirm(batch_id: str):
    data, status_code, message = _asset_import_service.confirm(batch_id, request.get_json(silent=True) or {})
    if data is None:
        return Result.error(code=status_code, message=message)
    return Result.success(data=data)


@api_bp.route("/v1/assets/import/batches/<string:batch_id>/audit", methods=["GET"])
def asset_import_batch_audit(batch_id: str):
    audit = _asset_import_service.audit(batch_id)
    if audit is None:
        return Result.error(code=404, message="batch not found")
    return Result.success(data=audit)


@api_bp.route("/v1/assets/hmi-maps/<string:map_id>/zone-summary", methods=["GET"])
def asset_overlay_zone_summary(map_id: str):
    return Result.success(data=_asset_overlay_service.zone_summary(map_id))


@api_bp.route("/v1/assets/hmi-maps/<string:map_id>/location-summary", methods=["GET"])
def asset_overlay_location_summary(map_id: str):
    return Result.success(data=_asset_overlay_service.location_summary(map_id))


@api_bp.route("/v1/assets/hmi-maps/<string:map_id>/asset-overlay", methods=["GET"])
def asset_overlay_assets(map_id: str):
    return Result.success(data=_asset_overlay_service.asset_overlay(map_id))


@api_bp.route("/v1/assets/hmi-maps/<string:map_id>/system-overlay", methods=["GET"])
def asset_overlay_systems(map_id: str):
    return Result.success(data=_asset_overlay_service.system_overlay(map_id))


@api_bp.route("/v1/assets/hmi-maps/<string:map_id>/fault-overlay", methods=["GET"])
def fault_overlay_assets(map_id: str):
    return Result.success(data=_fault_work_order_overlay_service.fault_overlay(map_id))


@api_bp.route("/v1/assets/hmi-maps/<string:map_id>/work-order-overlay", methods=["GET"])
def work_order_overlay_assets(map_id: str):
    return Result.success(data=_fault_work_order_overlay_service.work_order_overlay(map_id))


@api_bp.route("/v1/assets/hmi-maps/<string:map_id>/technician-navigation", methods=["GET"])
def technician_navigation_overlay(map_id: str):
    return Result.success(data=_fault_work_order_overlay_service.technician_navigation(map_id))


@api_bp.route("/v1/assets/hmi-maps/<string:map_id>/decision-lens", methods=["GET"])
def decision_lens_overlay(map_id: str):
    return Result.success(
        data=_fault_work_order_overlay_service.decision_lens(
            map_id,
            event_id=request.args.get("event_id", ""),
            work_order_id=request.args.get("work_order_id", ""),
        )
    )


@api_bp.route("/v1/assets/hmi-maps/<string:map_id>/evidence-overlay", methods=["GET"])
def evidence_overlay_assets(map_id: str):
    return Result.success(data=_evidence_audit_overlay_service.evidence_overlay(map_id))


@api_bp.route("/v1/assets/hmi-maps/<string:map_id>/work-order-evidence", methods=["GET"])
def work_order_evidence_overlay(map_id: str):
    return Result.success(data=_evidence_audit_overlay_service.work_order_evidence(map_id))


@api_bp.route("/v1/assets/hmi-maps/<string:map_id>/closure-readiness", methods=["GET"])
def closure_readiness_overlay(map_id: str):
    return Result.success(data=_evidence_audit_overlay_service.closure_readiness(map_id))


@api_bp.route("/v1/assets/hmi-maps/<string:map_id>/import-audit-summary", methods=["GET"])
def import_audit_summary_overlay(map_id: str):
    return Result.success(data=_evidence_audit_overlay_service.import_audit_summary(map_id))


@api_bp.route("/v1/assets/hmi-maps/<string:map_id>/export-evidence-center", methods=["GET"])
def export_evidence_center_overlay(map_id: str):
    return Result.success(data=_evidence_audit_overlay_service.export_evidence_center(map_id))
