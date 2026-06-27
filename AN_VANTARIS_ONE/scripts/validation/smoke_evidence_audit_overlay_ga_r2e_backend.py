#!/usr/bin/env python3
"""Smoke test for ONE-AIRPORT-DATA-ASSET-MAP-GA-R2E evidence/audit overlays."""

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
    spec = importlib.util.spec_from_file_location("evidence_audit_overlay_ga_r2e_assets_api", module_path)
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
    assert payload["formal_evidence_write"] is False, payload
    assert payload["formal_work_order_closure"] is False, payload
    assert payload["formal_asset_registry_write"] is False, payload
    assert payload["formal_event_registry_write"] is False, payload
    assert payload["formal_work_order_write"] is False, payload
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

    evidence = get_payload(client, f"/api/v1/assets/hmi-maps/{MAP_ID}/evidence-overlay")
    assert_readonly_blocked(evidence)
    assert evidence["summary"]["evidence_items_required"] > 0, evidence
    assert evidence["summary"]["closure_ready"] is False, evidence
    assert evidence["data"], evidence

    work_order_evidence = get_payload(client, f"/api/v1/assets/hmi-maps/{MAP_ID}/work-order-evidence")
    assert_readonly_blocked(work_order_evidence)
    assert work_order_evidence["summary"]["work_order_count"] == 5, work_order_evidence
    assert work_order_evidence["summary"]["closure_ready_count"] == 0, work_order_evidence
    assert work_order_evidence["data"][0]["confirm_close_enabled"] is False, work_order_evidence["data"][0]

    closure = get_payload(client, f"/api/v1/assets/hmi-maps/{MAP_ID}/closure-readiness")
    assert_readonly_blocked(closure)
    assert closure["closure_status"] == "not_ready_due_to_asset_quality_blockers", closure
    assert closure["summary"]["ready_to_close"] == 0, closure
    assert closure["gates"][0]["status"] == "blocked", closure["gates"]

    audit = get_payload(client, f"/api/v1/assets/hmi-maps/{MAP_ID}/import-audit-summary")
    assert_readonly_blocked(audit)
    assert audit["summary"]["total_records"] == 5187, audit
    assert audit["summary"]["readiness"] == "HOLD_BLOCKED", audit
    assert audit["audit"]["formal_import_committed"] is False, audit

    export_center = get_payload(client, f"/api/v1/assets/hmi-maps/{MAP_ID}/export-evidence-center")
    assert_readonly_blocked(export_center)
    assert export_center["export_ready"] is False, export_center
    assert export_center["export_status"] == "blocked_by_asset_quality", export_center
    assert export_center["available_packages"], export_center

    print("ONE_EVIDENCE_AUDIT_OVERLAY_GA_R2E_BACKEND_SMOKE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
