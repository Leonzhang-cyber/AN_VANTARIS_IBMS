"""UHMI UConsole workspace GET-only API skeleton."""

from __future__ import annotations

from flask import jsonify

from src.api import api_bp
from src.uhmi.uhmi_provider import get_health, get_menu_ia, get_section, list_sections


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

