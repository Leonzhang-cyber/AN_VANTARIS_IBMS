"""UHMI UConsole workspace GET-only API skeleton."""

from __future__ import annotations

from flask import jsonify

from src.api import api_bp
from src.uhmi.uhmi_provider import (
    get_devices,
    get_events,
    get_evidence,
    get_guardrails,
    get_health,
    get_integration_audit,
    get_menu_ia,
    get_panels,
    get_role_views,
    get_role_visibility,
    get_roles,
    get_section,
    get_status,
    get_systems,
    get_workspace,
    list_sections,
)


@api_bp.route("/v1/one/uhmi/health", methods=["GET"])
def uhmi_health():
    return jsonify(get_health())


@api_bp.route("/v1/one/uhmi/menu", methods=["GET"])
def uhmi_menu():
    return jsonify(get_menu_ia())


@api_bp.route("/v1/one/uhmi/sections", methods=["GET"])
def uhmi_sections():
    return jsonify({"items": list_sections(), "readOnly": True})


@api_bp.route("/v1/one/uhmi/sections/<string:section_key>", methods=["GET"])
def uhmi_section_detail(section_key: str):
    return jsonify(get_section(section_key))


@api_bp.route("/one/uconsole/uhmi/workspace", methods=["GET"])
def uhmi_r2b_workspace():
    return jsonify(get_workspace())


@api_bp.route("/one/uconsole/uhmi/status", methods=["GET"])
def uhmi_r2b_status():
    return jsonify(get_status())


@api_bp.route("/one/uconsole/uhmi/panels", methods=["GET"])
def uhmi_r2b_panels():
    return jsonify(get_panels())


@api_bp.route("/one/uconsole/uhmi/systems", methods=["GET"])
def uhmi_r2b_systems():
    return jsonify(get_systems())


@api_bp.route("/one/uconsole/uhmi/devices", methods=["GET"])
def uhmi_r2b_devices():
    return jsonify(get_devices())


@api_bp.route("/one/uconsole/uhmi/events", methods=["GET"])
def uhmi_r2b_events():
    return jsonify(get_events())


@api_bp.route("/one/uconsole/uhmi/evidence", methods=["GET"])
def uhmi_r2b_evidence():
    return jsonify(get_evidence())


@api_bp.route("/one/uconsole/uhmi/guardrails", methods=["GET"])
def uhmi_r2b_guardrails():
    return jsonify(get_guardrails())


@api_bp.route("/one/uconsole/uhmi/roles", methods=["GET"])
def uhmi_r2c_roles():
    return jsonify(get_roles())


@api_bp.route("/one/uconsole/uhmi/role-views", methods=["GET"])
def uhmi_r2c_role_views():
    return jsonify(get_role_views())


@api_bp.route("/one/uconsole/uhmi/role-visibility", methods=["GET"])
def uhmi_r2c_role_visibility():
    return jsonify(get_role_visibility())


@api_bp.route("/one/uconsole/uhmi/integration-audit", methods=["GET"])
def uhmi_r2e_integration_audit():
    return jsonify(get_integration_audit())
