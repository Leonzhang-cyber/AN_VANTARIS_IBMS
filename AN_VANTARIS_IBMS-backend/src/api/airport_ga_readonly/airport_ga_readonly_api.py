"""Airport GA-R1 projection-backed read-only API routes.

These routes implement the A7 frozen Airport read-only API paths as GET-only
local projection readers. They do not activate production runtime behavior,
database access, approval execution, or external system connections.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from flask import jsonify

from src.api import api_bp
from src.common.models.response import Result


RELEASE_CANDIDATE = "airport-international-ga-ready-readonly-rc-20260620"
SKELETON_PATH = "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-api-skeleton.v1.json"
FORBIDDEN_IDENTIFIER_KEYS = {"customerAssetIdentifier", "assetId", "deviceId"}
ROOT_KEY_COMPATIBILITY_ALIASES = {
    "operationsRows": "candidates",
    "sourceSystemRows": "healthRecords",
}


@dataclass(frozen=True)
class AirportReadOnlyRoute:
    endpoint_key: str
    path: str
    root_key: str
    source_artifact_path: str


def _repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "AN_VANTARIS_ONE").is_dir() and (parent / "AN_VANTARIS_IBMS-backend").is_dir():
            return parent
    raise RuntimeError("VANTARIS ONE repository root not found")


def _load_json(relative_path: str) -> dict[str, Any]:
    path = _repo_root() / relative_path
    if not path.is_file():
        raise FileNotFoundError(relative_path)
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{relative_path} must contain a JSON object")
    return data


def _load_route_contracts() -> dict[str, AirportReadOnlyRoute]:
    skeleton = _load_json(SKELETON_PATH)
    endpoint_paths = {
        item["endpointKey"]: item["path"]
        for item in skeleton.get("endpointSkeletons", [])
        if item.get("method") == "GET" and isinstance(item.get("path"), str)
    }
    routes: dict[str, AirportReadOnlyRoute] = {}
    for contract in skeleton.get("responseContracts", []):
        endpoint_key = contract.get("endpointKey")
        if endpoint_key not in endpoint_paths:
            continue
        routes[endpoint_key] = AirportReadOnlyRoute(
            endpoint_key=endpoint_key,
            path=endpoint_paths[endpoint_key],
            root_key=contract["projectionRootKey"],
            source_artifact_path=contract["sourceArtifactPath"],
        )
    if len(routes) != 8:
        raise ValueError("A7 Airport read-only API skeleton must define exactly 8 GET routes")
    return routes


ROUTES = _load_route_contracts()


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _sanitize(item)
            for key, item in value.items()
            if key not in FORBIDDEN_IDENTIFIER_KEYS
        }
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    return value


def _default_page(data: Any) -> dict[str, Any]:
    total = len(data) if isinstance(data, list) else 1 if data is not None else 0
    return {
        "page": 1,
        "pageSize": total,
        "totalItems": total,
        "totalPages": 1,
    }


def _read_endpoint_payload(endpoint_key: str) -> dict[str, Any]:
    route = ROUTES[endpoint_key]
    artifact = _load_json(route.source_artifact_path)
    source_root_key = route.root_key
    if source_root_key not in artifact:
        source_root_key = ROOT_KEY_COMPATIBILITY_ALIASES.get(route.root_key, route.root_key)
    if source_root_key not in artifact:
        raise KeyError(f"{route.source_artifact_path} missing {route.root_key}")

    data = _sanitize(artifact[source_root_key])
    summary = _sanitize(artifact.get("summary", data if isinstance(data, dict) else {}))
    filters = _sanitize(artifact.get("filters", []))
    facets = _sanitize(artifact.get("facets", []))
    pagination = _sanitize(artifact.get("defaultPage", _default_page(data)))

    return {
        "platform": "VANTARIS ONE",
        "industryProjection": "airport",
        "releaseCandidate": RELEASE_CANDIDATE,
        "endpointKey": endpoint_key,
        "route": route.path,
        "method": "GET",
        "readOnly": True,
        "productionActivation": False,
        "runtimeActivation": False,
        "databaseAccess": False,
        "dbWrite": False,
        "approvalExecution": False,
        "customerIdentifierLeakage": False,
        "source": {
            "type": "local_projection_artifact",
            "path": route.source_artifact_path,
            "rootKey": route.root_key,
            "sourceRootKey": source_root_key,
            "authority": "A7_FROZEN_READ_ONLY_API_CONTRACT",
        },
        "summary": summary,
        "data": data,
        "filters": filters,
        "facets": facets,
        "pagination": pagination,
    }


def _success(endpoint_key: str):
    return Result.success(data=_read_endpoint_payload(endpoint_key))


def _error(endpoint_key: str, exc: Exception):
    route = ROUTES[endpoint_key]
    body = {
        "code": 500,
        "message": "airport read-only projection unavailable",
        "data": {
            "platform": "VANTARIS ONE",
            "industryProjection": "airport",
            "releaseCandidate": RELEASE_CANDIDATE,
            "endpointKey": endpoint_key,
            "route": route.path,
            "method": "GET",
            "readOnly": True,
            "productionActivation": False,
            "runtimeActivation": False,
            "databaseAccess": False,
            "dbWrite": False,
            "approvalExecution": False,
            "customerIdentifierLeakage": False,
            "source": {
                "type": "local_projection_artifact",
                "path": route.source_artifact_path,
                "rootKey": route.root_key,
                "authority": "A7_FROZEN_READ_ONLY_API_CONTRACT",
            },
            "error": {
                "type": exc.__class__.__name__,
                "message": str(exc),
            },
        },
    }
    return jsonify(body), 500


def _handle(endpoint_key: str):
    try:
        return _success(endpoint_key)
    except Exception as exc:  # pragma: no cover - defensive API envelope
        return _error(endpoint_key, exc)


@api_bp.route("/v1/one/airport/console/overview", methods=["GET"])
def airport_ga_readonly_overview():
    return _handle("AIRPORT_OVERVIEW")


@api_bp.route("/v1/one/airport/console/systems-integration-health", methods=["GET"])
def airport_ga_readonly_systems_integration_health():
    return _handle("SYSTEMS_INTEGRATION_HEALTH")


@api_bp.route("/v1/one/airport/console/assets-topology", methods=["GET"])
def airport_ga_readonly_assets_topology():
    return _handle("ASSETS_TOPOLOGY")


@api_bp.route("/v1/one/airport/console/alarms-events", methods=["GET"])
def airport_ga_readonly_alarms_events():
    return _handle("ALARMS_EVENTS")


@api_bp.route("/v1/one/airport/console/fault-cases", methods=["GET"])
def airport_ga_readonly_fault_cases():
    return _handle("FAULT_CASES")


@api_bp.route("/v1/one/airport/console/maintenance-work-orders", methods=["GET"])
def airport_ga_readonly_maintenance_work_orders():
    return _handle("MAINTENANCE_WORK_ORDERS")


@api_bp.route("/v1/one/airport/console/evidence-investigation", methods=["GET"])
def airport_ga_readonly_evidence_investigation():
    return _handle("EVIDENCE_INVESTIGATION")


@api_bp.route("/v1/one/airport/console/reports", methods=["GET"])
def airport_ga_readonly_reports():
    return _handle("REPORTS")
