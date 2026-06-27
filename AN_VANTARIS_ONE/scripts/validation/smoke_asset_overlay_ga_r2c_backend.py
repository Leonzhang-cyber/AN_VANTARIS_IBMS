#!/usr/bin/env python3
"""Smoke test for ONE-AIRPORT-DATA-ASSET-MAP-GA-R2C overlay APIs."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import types

from flask import Blueprint, Flask


ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "AN_VANTARIS_IBMS-backend"
ONE = ROOT / "AN_VANTARIS_ONE"
MAP_ID = "T3-GF-HMI-001"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
if str(ONE) not in sys.path:
    sys.path.insert(0, str(ONE))


def load_asset_overlay_blueprint() -> Blueprint:
    api_bp = Blueprint("api", __name__, url_prefix="/api")
    fake_api = types.ModuleType("src.api")
    fake_api.api_bp = api_bp
    fake_api.__path__ = [str(BACKEND / "src" / "api")]
    original_api = sys.modules.get("src.api")
    sys.modules["src.api"] = fake_api
    module_path = BACKEND / "src" / "api" / "assets" / "assets_api.py"
    spec = importlib.util.spec_from_file_location("asset_overlay_ga_r2c_assets_api", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        if original_api is None:
            sys.modules.pop("src.api", None)
        else:
            sys.modules["src.api"] = original_api
    return api_bp


def assert_no_path_leak(payload: object) -> None:
    serialized = json.dumps(payload, sort_keys=True)
    forbidden = ["/Users/leon", str(ROOT), str(BACKEND), str(ONE)]
    leaked = [token for token in forbidden if token in serialized]
    if leaked:
        raise AssertionError(f"absolute path leaked: {leaked[0]}")


def assert_blocked_overlay(payload: dict) -> None:
    assert payload["asset_import_readiness"] == "HOLD_BLOCKED", payload
    assert payload["asset_overlay_status"] == "blocked_by_data_quality", payload
    assert payload["formal_asset_registry_write"] is False, payload
    assert payload["readOnly"] is True, payload
    assert payload["productionActivation"] is False, payload
    assert payload["runtimeActivation"] is False, payload
    assert payload["databaseAccess"] is False, payload
    assert payload["dbWrite"] is False, payload
    assert payload["approvalExecution"] is False, payload


def get_payload(client, path: str) -> dict:
    response = client.get(path)
    if response.status_code != 200:
        raise AssertionError(f"{path} failed: {response.status_code} {response.get_data(as_text=True)}")
    body = response.get_json()
    assert_no_path_leak(body)
    return body["data"]


def main() -> int:
    app = Flask(__name__)
    app.register_blueprint(load_asset_overlay_blueprint())
    client = app.test_client()

    zone = get_payload(client, f"/api/v1/assets/hmi-maps/{MAP_ID}/zone-summary")
    assert_blocked_overlay(zone)
    assert zone["map_id"] == MAP_ID, zone
    assert zone["summary"]["asset_records_seen"] == 5187, zone
    assert zone["data"], zone

    location = get_payload(client, f"/api/v1/assets/hmi-maps/{MAP_ID}/location-summary")
    assert_blocked_overlay(location)
    assert location["data"], location
    assert location["data"][0]["map_binding_status"] == "zone_location_grouped", location["data"][0]

    overlay = get_payload(client, f"/api/v1/assets/hmi-maps/{MAP_ID}/asset-overlay")
    assert_blocked_overlay(overlay)
    assert overlay["overlay_mode"] == "zone_location_grouped", overlay
    assert overlay["summary"]["records_seen"] == 5187, overlay
    assert overlay["summary"]["blocked_by_quality"] is True, overlay
    assert overlay["summary"]["confirm_enabled"] is False, overlay
    assert overlay["data"], overlay

    system = get_payload(client, f"/api/v1/assets/hmi-maps/{MAP_ID}/system-overlay")
    assert_blocked_overlay(system)
    assert system["data"], system
    assert any(row["system"] == "PA" for row in system["data"]), system["data"]

    print("ONE_ASSET_OVERLAY_GA_R2C_BACKEND_SMOKE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
