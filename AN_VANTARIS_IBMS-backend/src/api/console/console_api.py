"""UConsole platform operations API skeleton."""

from __future__ import annotations

from flask import request

from src.api import api_bp
from src.common.models.response import Result
from src.console.console_service import ConsoleService
from src.console.module_package_service import ModulePackageService


_service = ConsoleService()
_package_service = ModulePackageService()


@api_bp.route("/v1/console/health", methods=["GET"])
def console_health():
    return Result.success(data=_service.get_console_health())


@api_bp.route("/v1/console/modules", methods=["GET"])
def console_modules():
    return Result.success(data={"items": _service.get_platform_modules_summary()})


@api_bp.route("/v1/console/operations/summary", methods=["GET"])
def console_operations_summary():
    return Result.success(data=_service.get_operations_dashboard_summary())


@api_bp.route("/v1/console/reports/readiness", methods=["GET"])
def console_reports_readiness():
    return Result.success(data=_service.get_reports_readiness_snapshot())


@api_bp.route("/v1/console/readiness/registry", methods=["GET"])
def console_readiness_registry():
    return Result.success(data={"items": _service.get_readiness_registry()})


@api_bp.route("/v1/console/modules/<string:module_id>/health", methods=["GET"])
def console_module_health(module_id: str):
    item = _service.get_module_health_detail(module_id)
    if not item:
        return Result.error(code=404, message="moduleId not found")
    return Result.success(data=item)


@api_bp.route("/v1/console/modules/health", methods=["GET"])
def console_modules_health():
    return Result.success(data={"items": _service.get_all_module_health_details()})


@api_bp.route("/v1/console/readiness/summary", methods=["GET"])
def console_readiness_summary():
    return Result.success(data=_service.get_readiness_summary())


@api_bp.route("/v1/console/readiness/score", methods=["GET"])
def console_readiness_score():
    return Result.success(data=_service.get_platform_readiness_score())


@api_bp.route("/v1/console/navigation/modules", methods=["GET"])
def console_navigation_modules():
    return Result.success(data=_service.get_platform_navigation_model())


@api_bp.route("/v1/console/packages/health", methods=["GET"])
def console_package_health():
    return Result.success(data=_package_service.get_package_center_health())


@api_bp.route("/v1/console/packages", methods=["GET"])
def console_packages():
    filters = {
        "moduleId": request.args.get("moduleId"),
        "packageCategory": request.args.get("packageCategory"),
        "installed": request.args.get("installed"),
        "entitled": request.args.get("entitled"),
        "enabled": request.args.get("enabled"),
        "visible": request.args.get("visible"),
        "patchStatus": request.args.get("patchStatus"),
        "role": request.args.get("role"),
    }
    return Result.success(data=_package_service.list_packages(filters))


@api_bp.route("/v1/console/packages/summary", methods=["GET"])
def console_packages_summary():
    return Result.success(data=_package_service.get_package_summary())


@api_bp.route("/v1/console/packages/entries", methods=["GET"])
def console_packages_entries():
    return Result.success(data=_package_service.get_entry_center())


@api_bp.route("/v1/console/packages/locked", methods=["GET"])
def console_packages_locked():
    return Result.success(data=_package_service.get_locked_packages())


@api_bp.route("/v1/console/packages/patch-readiness", methods=["GET"])
def console_packages_patch_readiness():
    return Result.success(data=_package_service.get_patch_readiness())


@api_bp.route("/v1/console/packages/roles", methods=["GET"])
def console_package_roles():
    return Result.success(data=_package_service.get_supported_roles())


@api_bp.route("/v1/console/packages/roles/summary", methods=["GET"])
def console_package_roles_summary():
    return Result.success(data=_package_service.get_role_visibility_summary())


@api_bp.route("/v1/console/packages/roles/<string:role>", methods=["GET"])
def console_package_role_visibility(role: str):
    data = _package_service.get_role_visibility(role)
    if not data:
        return Result.error(code=404, message="role not found")
    return Result.success(data=data)


@api_bp.route("/v1/console/packages/roles/<string:role>/entries", methods=["GET"])
def console_package_role_entries(role: str):
    data = _package_service.get_role_entries(role)
    if not data:
        return Result.error(code=404, message="role not found")
    return Result.success(data=data)


@api_bp.route("/v1/console/packages/roles/<string:role>/menu-preview", methods=["GET"])
def console_package_role_menu_preview(role: str):
    data = _package_service.get_role_menu_preview(role)
    if not data:
        return Result.error(code=404, message="role not found")
    return Result.success(data=data)


@api_bp.route("/v1/console/packages/<string:package_id_or_module_id>", methods=["GET"])
def console_package_detail(package_id_or_module_id: str):
    data = _package_service.get_package_detail(package_id_or_module_id)
    return Result.success(data={"item": data, "found": bool(data)})

