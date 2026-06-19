"""UEDGE setup and diagnostics API (read-only skeleton)."""

from __future__ import annotations

from flask import jsonify

from src.api import api_bp
from src.uedge.uedge_service import UedgeService


_service = UedgeService()


def _ok(data):
    return jsonify({"success": True, "data": data}), 200


@api_bp.route("/v1/uedge/health", methods=["GET"])
def uedge_health():
    return _ok(_service.get_uedge_health())


@api_bp.route("/v1/uedge/setup", methods=["GET"])
def uedge_setup():
    return _ok(_service.get_customer_setup())


@api_bp.route("/v1/uedge/setup/steps", methods=["GET"])
def uedge_setup_steps():
    return _ok(_service.get_setup_steps())


@api_bp.route("/v1/uedge/diagnostics", methods=["GET"])
def uedge_diagnostics():
    return _ok(_service.get_engineer_diagnostics())


@api_bp.route("/v1/uedge/diagnostics/panels", methods=["GET"])
def uedge_diagnostics_panels():
    return _ok(_service.get_diagnostics_panels())


@api_bp.route("/v1/uedge/summary", methods=["GET"])
def uedge_summary():
    return _ok(_service.get_uedge_summary())

