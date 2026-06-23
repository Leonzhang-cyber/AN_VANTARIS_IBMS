"""Foundation Diagnostics GA R1 read-only API."""

from __future__ import annotations

from src.api import api_bp
from src.common.models.response import Result
from src.foundation_diagnostics.service import FoundationDiagnosticsService

_service = FoundationDiagnosticsService()


def _result(name: str):
    return Result.success(data=_service.section(name))


@api_bp.route("/one/foundation-diagnostics/workspace", methods=["GET"])
@api_bp.route("/v1/one/foundation-diagnostics/workspace", methods=["GET"])
def foundation_diagnostics_workspace_route():
    return Result.success(data=_service.workspace())


@api_bp.route("/one/foundation-diagnostics/overview", methods=["GET"])
@api_bp.route("/v1/one/foundation-diagnostics/overview", methods=["GET"])
def foundation_diagnostics_overview_route():
    return _result("overview")


@api_bp.route("/one/foundation-diagnostics/server-plan", methods=["GET"])
@api_bp.route("/v1/one/foundation-diagnostics/server-plan", methods=["GET"])
def foundation_diagnostics_server_plan_route():
    return _result("server-plan")


@api_bp.route("/one/foundation-diagnostics/package-readiness", methods=["GET"])
@api_bp.route("/v1/one/foundation-diagnostics/package-readiness", methods=["GET"])
def foundation_diagnostics_package_readiness_route():
    return _result("package-readiness")


@api_bp.route("/one/foundation-diagnostics/edge-readiness", methods=["GET"])
@api_bp.route("/v1/one/foundation-diagnostics/edge-readiness", methods=["GET"])
def foundation_diagnostics_edge_readiness_route():
    return _result("edge-readiness")


@api_bp.route("/one/foundation-diagnostics/link-readiness", methods=["GET"])
@api_bp.route("/v1/one/foundation-diagnostics/link-readiness", methods=["GET"])
def foundation_diagnostics_link_readiness_route():
    return _result("link-readiness")


@api_bp.route("/one/foundation-diagnostics/db-readiness", methods=["GET"])
@api_bp.route("/v1/one/foundation-diagnostics/db-readiness", methods=["GET"])
def foundation_diagnostics_db_readiness_route():
    return _result("db-readiness")


@api_bp.route("/one/foundation-diagnostics/contracts-readiness", methods=["GET"])
@api_bp.route("/v1/one/foundation-diagnostics/contracts-readiness", methods=["GET"])
def foundation_diagnostics_contracts_readiness_route():
    return _result("contracts-readiness")


@api_bp.route("/one/foundation-diagnostics/offline-checklist", methods=["GET"])
@api_bp.route("/v1/one/foundation-diagnostics/offline-checklist", methods=["GET"])
def foundation_diagnostics_offline_checklist_route():
    return _result("offline-checklist")


@api_bp.route("/one/foundation-diagnostics/healthcheck-preview", methods=["GET"])
@api_bp.route("/v1/one/foundation-diagnostics/healthcheck-preview", methods=["GET"])
def foundation_diagnostics_healthcheck_preview_route():
    return _result("healthcheck-preview")


@api_bp.route("/one/foundation-diagnostics/package-integrity", methods=["GET"])
@api_bp.route("/v1/one/foundation-diagnostics/package-integrity", methods=["GET"])
def foundation_diagnostics_package_integrity_route():
    return _result("package-integrity")


@api_bp.route("/one/foundation-diagnostics/rollback-readiness", methods=["GET"])
@api_bp.route("/v1/one/foundation-diagnostics/rollback-readiness", methods=["GET"])
def foundation_diagnostics_rollback_readiness_route():
    return _result("rollback-readiness")


@api_bp.route("/one/foundation-diagnostics/guardrails", methods=["GET"])
@api_bp.route("/v1/one/foundation-diagnostics/guardrails", methods=["GET"])
def foundation_diagnostics_guardrails_route():
    return _result("guardrails")
