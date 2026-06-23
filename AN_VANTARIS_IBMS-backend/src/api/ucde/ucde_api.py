"""UCDE evidence center API (read-only skeleton)."""

from __future__ import annotations

from flask import request

from src.api import api_bp
from src.common.models.response import Result
from src.ucde.evidence_service import UcdeEvidenceService


_service = UcdeEvidenceService()


@api_bp.route("/v1/ucde/health", methods=["GET"])
def ucde_health():
    return Result.success(data=_service.get_ucde_health())


@api_bp.route("/v1/ucde/evidence/summary", methods=["GET"])
def ucde_evidence_summary():
    return Result.success(data=_service.get_evidence_summary())


@api_bp.route("/v1/ucde/evidence/<string:evidence_id>/verify", methods=["GET"])
def ucde_evidence_verify(evidence_id: str):
    result, error = _service.verify_evidence_record(evidence_id)
    if error:
        return Result.error(code=error[0], message=error[1])
    return Result.success(data=result)


@api_bp.route("/v1/ucde/evidence/<string:evidence_id>/relationships", methods=["GET"])
def ucde_evidence_relationships(evidence_id: str):
    result, error = _service.get_evidence_relationships(evidence_id)
    if error:
        return Result.error(code=error[0], message=error[1])
    return Result.success(data=result)


@api_bp.route("/v1/ucde/evidence/<string:evidence_id>", methods=["GET"])
def ucde_evidence_detail(evidence_id: str):
    item = _service.get_evidence_detail(evidence_id)
    if not item:
        return Result.error(code=404, message="evidenceId not found")
    return Result.success(data=item)


@api_bp.route("/v1/ucde/evidence", methods=["GET"])
def ucde_evidence_list():
    filters = {
        "evidenceType": request.args.get("evidenceType"),
        "sourceModuleId": request.args.get("sourceModuleId"),
        "evidenceStatus": request.args.get("evidenceStatus"),
        "evidenceCategory": request.args.get("evidenceCategory"),
    }
    return Result.success(data=_service.list_evidence(filters=filters))


@api_bp.route("/one/ucde/evidence-center", methods=["GET"])
def ucde_r4_evidence_center():
    return Result.success(data=_service.get_r4_evidence_center())


@api_bp.route("/one/ucde/evidence-catalog", methods=["GET"])
def ucde_r4_evidence_catalog():
    return Result.success(data=_service.get_r4_evidence_catalog())


@api_bp.route("/one/ucde/evidence-records", methods=["GET"])
def ucde_r4_evidence_records():
    return Result.success(data=_service.get_r4_evidence_records())


@api_bp.route("/one/ucde/evidence-links", methods=["GET"])
def ucde_r4_evidence_links():
    return Result.success(data=_service.get_r4_evidence_links())


@api_bp.route("/one/ucde/uhmi-linkage", methods=["GET"])
def ucde_r4_uhmi_linkage():
    return Result.success(data=_service.get_r4_uhmi_linkage())


@api_bp.route("/one/ucde/customer-preview", methods=["GET"])
def ucde_r4_customer_preview():
    return Result.success(data=_service.get_r4_customer_preview())


@api_bp.route("/one/ucde/guardrails", methods=["GET"])
def ucde_r4_guardrails():
    return Result.success(data=_service.get_r4_guardrails())
