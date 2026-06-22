"""Production GA foundation package GET-only API routes."""

from __future__ import annotations

from flask import jsonify

from src.api import api_bp
from src.api.prod_ga.foundation_packages_provider import (
    foundation_package_health,
    get_foundation_package,
    list_foundation_packages_response,
)


@api_bp.route("/v1/one/prod-ga/foundation-packages", methods=["GET"])
def prod_ga_foundation_packages():
    return jsonify(list_foundation_packages_response())


@api_bp.route("/v1/one/prod-ga/foundation-packages/health", methods=["GET"])
def prod_ga_foundation_packages_health():
    return jsonify(foundation_package_health())


@api_bp.route("/v1/one/prod-ga/foundation-packages/<string:package_id>", methods=["GET"])
def prod_ga_foundation_package_detail(package_id: str):
    package = get_foundation_package(package_id)
    if package is None:
        return jsonify(
            {
                "error": "unknown_foundation_package",
                "allowedPackageIds": ["edge", "link", "db", "contracts"],
                "readOnly": True,
                "runtimeActivation": False,
                "productionActivation": False,
                "dbWrite": False,
                "deploymentExecution": False,
            }
        ), 404
    return jsonify(package)
