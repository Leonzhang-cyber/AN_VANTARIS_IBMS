#!/usr/bin/env python3
"""Smoke test for ONE-AIRPORT-DATA-ASSET-MAP-GA-R2D fault/work-order overlays."""

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


def load_overlay_blueprint() -> Blueprint:
    api_bp = Blueprint("api", __name__, url_prefix="/api")
    fake_api = types.ModuleType("src.api")
    fake_api.api_bp = api_bp
    fake_api.__path__ = [str(BACKEND / "src" / "api")]
    original_api = sys.modules.get("src.api")
    sys.modules["src.api"] = fake_api
    module_path = BACKEND / "src" / "api" / "assets" / "assets_api.py"
    spec = importlib.util.spec_from_file_location("fault_work_order_overlay_ga_r2d_assets_api", module_path)
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


def get_payload(client, path: str) -> dict:
    response = client.get(path)
    if response.status_code != 200:
        raise AssertionError(f"{path} failed: {response.status_code} {response.get_data(as_text=True)}")
    body = response.get_json()
    assert_no_path_leak(body)
    return body["data"]


def assert_readonly_blocked(payload: dict) -> None:
    assert payload["asset_import_readiness"] == "HOLD_BLOCKED", payload
    assert payload["asset_overlay_status"] == "blocked_by_data_quality", payload
    assert payload["formal_event_registry_write"] is False, payload
    assert payload["formal_work_order_write"] is False, payload
    assert payload["formal_asset_registry_write"] is False, payload
    assert payload["readOnly"] is True, payload
    assert payload["productionActivation"] is False, payload
    assert payload["runtimeActivation"] is False, payload
    assert payload["databaseAccess"] is False, payload
    assert payload["dbWrite"] is False, payload
    assert payload["approvalExecution"] is False, payload


def main() -> int:
    app = Flask(__name__)
    app.register_blueprint(load_overlay_blueprint())
    client = app.test_client()

    fault = get_payload(client, f"/api/v1/assets/hmi-maps/{MAP_ID}/fault-overlay")
    assert_readonly_blocked(fault)
    assert fault["summary"]["fault_count"] == 5, fault
    assert fault["data"], fault
    first_event = fault["data"][0]["event_id"]

    work_order = get_payload(client, f"/api/v1/assets/hmi-maps/{MAP_ID}/work-order-overlay")
    assert_readonly_blocked(work_order)
    assert work_order["summary"]["work_order_count"] == 5, work_order
    assert work_order["data"], work_order
    first_work_order = work_order["data"][0]["work_order_id"]

    navigation = get_payload(client, f"/api/v1/assets/hmi-maps/{MAP_ID}/technician-navigation")
    assert_readonly_blocked(navigation)
    assert navigation["summary"]["route_count"] == 5, navigation
    assert navigation["data"], navigation
    assert navigation["data"][0]["navigation_status"] == "route_hint_only", navigation["data"][0]

    event_lens = get_payload(client, f"/api/v1/assets/hmi-maps/{MAP_ID}/decision-lens?event_id={first_event}")
    assert_readonly_blocked(event_lens)
    assert event_lens["context_type"] == "fault", event_lens
    assert event_lens["operational_context"], event_lens
    assert event_lens["evidence_context"]["status"] == "pending_closure_evidence", event_lens

    work_order_lens = get_payload(
        client, f"/api/v1/assets/hmi-maps/{MAP_ID}/decision-lens?work_order_id={first_work_order}"
    )
    assert_readonly_blocked(work_order_lens)
    assert work_order_lens["context_type"] == "work_order", work_order_lens
    assert work_order_lens["operational_context"], work_order_lens
    assert work_order_lens["evidence_context"]["required"] is True, work_order_lens

    print("ONE_FAULT_WORK_ORDER_OVERLAY_GA_R2D_BACKEND_SMOKE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
