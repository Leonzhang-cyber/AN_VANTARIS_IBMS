"""Engineer Installer Console read-only preview API."""

from __future__ import annotations

from src.api import api_bp
from src.common.models.response import Result
from src.customer_delivery.readonly_preview_provider import (
    APP_SERVER_PLAN,
    DB_SERVER_PLAN,
    diagnostics_preview,
    engineer_installer_console,
    guardrails,
    package_readiness,
    server_plan,
)


@api_bp.route("/one/engineer-installer/console", methods=["GET"])
def engineer_installer_console_route():
    return Result.success(data=engineer_installer_console())


@api_bp.route("/one/engineer-installer/package-readiness", methods=["GET"])
def engineer_installer_package_readiness_route():
    return Result.success(data=package_readiness())


@api_bp.route("/one/engineer-installer/app-server-plan", methods=["GET"])
def engineer_installer_app_server_plan_route():
    return Result.success(data={**server_plan(), "appServerPlan": APP_SERVER_PLAN})


@api_bp.route("/one/engineer-installer/db-server-plan", methods=["GET"])
def engineer_installer_db_server_plan_route():
    return Result.success(data={**server_plan(), "dbServerPlan": DB_SERVER_PLAN})


@api_bp.route("/one/engineer-installer/offline-demo-handoff", methods=["GET"])
def engineer_installer_offline_demo_handoff_route():
    return Result.success(data=engineer_installer_console())


@api_bp.route("/one/engineer-installer/diagnostics-preview", methods=["GET"])
def engineer_installer_diagnostics_preview_route():
    return Result.success(data=diagnostics_preview())


@api_bp.route("/one/engineer-installer/guardrails", methods=["GET"])
def engineer_installer_guardrails_route():
    return Result.success(data=guardrails())
