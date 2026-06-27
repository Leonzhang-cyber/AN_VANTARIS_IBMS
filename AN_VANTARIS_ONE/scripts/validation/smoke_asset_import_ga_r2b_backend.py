#!/usr/bin/env python3
"""Smoke test for ONE-AIRPORT-DATA-ASSET-MAP-GA-R2B backend API skeleton."""

from __future__ import annotations

from io import BytesIO
import importlib.util
import json
from pathlib import Path
import sys
import types

from flask import Blueprint, Flask


ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "AN_VANTARIS_IBMS-backend"
ONE = ROOT / "AN_VANTARIS_ONE"
SOURCE_FILES = [
    ONE / "source-data" / "Asset Database Zonewise_Basement_SH_030626.xlsx",
    ONE / "source-data" / "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
]

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
if str(ONE) not in sys.path:
    sys.path.insert(0, str(ONE))

def load_asset_import_blueprint() -> Blueprint:
    api_bp = Blueprint("api", __name__, url_prefix="/api")
    fake_api = types.ModuleType("src.api")
    fake_api.api_bp = api_bp
    fake_api.__path__ = [str(BACKEND / "src" / "api")]
    original_api = sys.modules.get("src.api")
    sys.modules["src.api"] = fake_api
    module_path = BACKEND / "src" / "api" / "assets" / "assets_api.py"
    spec = importlib.util.spec_from_file_location("asset_import_ga_r2b_assets_api", module_path)
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


def main() -> int:
    for path in SOURCE_FILES:
        if not path.is_file():
            raise AssertionError(f"missing source workbook: {path.name}")

    app = Flask(__name__)
    app.register_blueprint(load_asset_import_blueprint())
    client = app.test_client()

    multipart_files = []
    for path in SOURCE_FILES:
        multipart_files.append((BytesIO(path.read_bytes()), path.name))

    preview_response = client.post(
        "/api/v1/assets/import/preview",
        data={"file": multipart_files},
        content_type="multipart/form-data",
    )
    if preview_response.status_code != 200:
        raise AssertionError(f"preview failed: {preview_response.status_code} {preview_response.get_data(as_text=True)}")
    preview_body = preview_response.get_json()
    assert_no_path_leak(preview_body)
    preview = preview_body["data"]
    summary = preview["summary"]
    alert = preview["alert"]
    batch_id = preview["batchId"]

    assert summary["total_records"] == 5187, summary
    assert summary["readiness"] == "HOLD_BLOCKED", summary
    assert summary["blocker_count"] == 2, summary
    assert summary["major_count"] == 1, summary
    assert summary["warning_count"] == 7, summary
    assert alert["confirm_enabled"] is False, alert

    batches_response = client.get("/api/v1/assets/import/batches")
    assert batches_response.status_code == 200, batches_response.get_data(as_text=True)
    assert_no_path_leak(batches_response.get_json())
    batches = batches_response.get_json()["data"]["batches"]
    assert any(row["import_batch_id"] == batch_id for row in batches), batches

    report_response = client.get(f"/api/v1/assets/import/batches/{batch_id}/report")
    assert report_response.status_code == 200, report_response.get_data(as_text=True)
    report_body = report_response.get_json()
    assert_no_path_leak(report_body)
    report = report_body["data"]["report"]
    assert report["summary"]["total_records"] == 5187, report["summary"]
    assert report["summary"]["readiness"] == "HOLD_BLOCKED", report["summary"]

    confirm_response = client.post(
        f"/api/v1/assets/import/batches/{batch_id}/confirm",
        json={"reviewed_quality_report": True, "accepted_unresolved_warnings": True},
    )
    assert confirm_response.status_code == 409, confirm_response.get_data(as_text=True)
    assert confirm_response.get_json()["message"] == "Import blocked until critical issues are resolved."
    print("CONFIRM_BLOCKED_PASS")

    audit_response = client.get(f"/api/v1/assets/import/batches/{batch_id}/audit")
    assert audit_response.status_code == 200, audit_response.get_data(as_text=True)
    audit_body = audit_response.get_json()
    assert_no_path_leak(audit_body)
    audit = audit_body["data"]["audit"]
    assert audit["import_batch_id"] == batch_id, audit
    assert audit["source_file_hash"], audit
    assert audit["readiness"] == "HOLD_BLOCKED", audit
    assert audit["import_status"] == "preview_ready", audit

    print("ONE_ASSET_IMPORT_GA_R2B_BACKEND_SMOKE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
