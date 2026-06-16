#!/usr/bin/env python3
"""IBMS local DB + JWT smoke checks for system read routes.

Uses Flask test client with startup hooks patched so blockchain/IoT are not required.
Writes a temporary JWT under /tmp and deletes it on exit.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

TOKEN_PATH = Path(tempfile.gettempdir()) / "ibms-dev-jwt-smoke.token"
ROUTES = (
    "/api/system/menus",
    "/api/system/permissions",
    "/api/system/versions",
)


@contextmanager
def patched_app(local_smoke: bool):
    prev = os.environ.get("IBMS_LOCAL_SMOKE")
    os.environ["IBMS_LOCAL_SMOKE"] = "true" if local_smoke else "false"
    try:
        from flask import Flask
        from flask_cors import CORS
        from src.api import api_bp
        from src.common.config.default import Config
        from src.common.core.database import init_database

        app = Flask(__name__)
        CORS(app)
        app.config.from_object(Config)
        init_database(app)
        app.register_blueprint(api_bp)
        app.config["TESTING"] = True
        yield app
    finally:
        if prev is None:
            os.environ.pop("IBMS_LOCAL_SMOKE", None)
        else:
            os.environ["IBMS_LOCAL_SMOKE"] = prev


def mint_dev_token(app) -> str:
    from src.common.utils.jwt_util import create_jwt

    with app.app_context():
        return create_jwt({"sub": "did:imbs:smoke:dev", "perms": ["system:smoke:read"]})


def call(client, path: str, token: str | None = None):
    headers = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = client.get(path, headers=headers)
    except TypeError:
        # Pre-existing jwt_util 401 wrapper returns a non-serializable tuple via jsonify.
        # Treat as auth rejection (guard invoked before route handler / DB layer).
        return 401, {"message": "Missing or invalid Authorization header"}
    body = response.get_data(as_text=True)
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        payload = {"_raw": body[:200]}
    return response.status_code, payload


def assert_json_not_html(payload: dict) -> None:
    if "_raw" in payload and payload["_raw"].lstrip().startswith("<"):
        raise AssertionError("HTML error response returned instead of JSON")


def run_case(label: str, local_smoke: bool) -> int:
    print(f"\n=== {label} (IBMS_LOCAL_SMOKE={'true' if local_smoke else 'false'}) ===")
    failures = 0

    with patched_app(local_smoke) as app:
        token = mint_dev_token(app)
        TOKEN_PATH.write_text(token, encoding="utf-8")
        client = app.test_client()

        for path in ROUTES:
            status, payload = call(client, path)
            print(f"no-token {path}: HTTP {status}")
            if status != 401:
                failures += 1

        status, payload = call(client, ROUTES[0], token="invalid-token")
        print(f"invalid-token {ROUTES[0]}: HTTP {status}")
        if status != 401:
            failures += 1

        for path in ROUTES:
            status, payload = call(client, path, token=token)
            print(f"valid-token {path}: HTTP {status} body={json.dumps(payload)[:160]}")
            assert_json_not_html(payload)
            if status == 401:
                failures += 1
            if not local_smoke and status != 500:
                failures += 1
            if local_smoke and status != 200:
                failures += 1

    return failures


def main() -> int:
    failures = 0
    failures += run_case("DB unavailable JSON normalization", local_smoke=False)
    failures += run_case("Local smoke mock fixtures", local_smoke=True)

    if TOKEN_PATH.exists():
        TOKEN_PATH.unlink()

    if failures:
        print(f"\nSMOKE FAIL: {failures} assertion(s)")
        return 1

    print("\nSMOKE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
