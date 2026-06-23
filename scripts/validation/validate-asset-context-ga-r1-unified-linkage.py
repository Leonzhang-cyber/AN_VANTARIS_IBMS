#!/usr/bin/env python3
"""Validate ASSET-CONTEXT-GA-R1 unified read-only linkage."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "ONE_ASSET_CONTEXT_GA_R1_UNIFIED_LINKAGE_PASS"

BACKEND_FILES = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/asset_context/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/asset_context/asset_context_provider.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/asset_context/asset_context_service.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/asset_context/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/asset_context/asset_context_api.py",
]
FRONTEND_FILES = [
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/assetContext.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/assets/AssetContext.vue",
]
MODIFIED_REFS = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts",
]
DOCS = [
    ROOT / "AN_VANTARIS_ONE/ASSET_CONTEXT_GA_R1.md",
    ROOT / "AN_VANTARIS_ONE/registries/asset-context-ga-r1/asset-context-ga-r1.registry.json",
    ROOT / "AN_VANTARIS_ONE/registries/asset-context-ga-r1/asset-context-ga-r1.evidence.json",
    ROOT / "AN_VANTARIS_ONE/registries/asset-context-ga-r1/asset-context-ga-r1.validation.json",
]

ROUTES = [
    "/v1/one/asset-context/health",
    "/v1/one/asset-context/summary",
    "/v1/one/asset-context/assets",
    "/v1/one/asset-context/assets/<string:asset_id>",
    "/v1/one/asset-context/assets/<string:asset_id>/links",
    "/v1/one/asset-context/graph",
    "/v1/one/asset-context/guardrails",
]
GUARDRAILS = [
    "readOnly",
    "runtimeEnabled",
    "dbWriteEnabled",
    "assetGraphWriteEnabled",
    "edgeCommandExecution",
    "linkCommandExecution",
    "deviceControlEnabled",
    "productionActivation",
    "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
    "ASSET_CONTEXT_GA_R1",
]
FORBIDDEN_CODE_TOKENS = [
    "db.session.add",
    "db.session.commit",
    ".execute(",
    "op.create_table",
    "op.add_column",
    "send_edge_command",
    "send_link_command",
    "execute_edge_command",
    "execute_link_command",
    "enable_device_control",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[PASS] {message}")


def main() -> int:
    for path in BACKEND_FILES + FRONTEND_FILES + MODIFIED_REFS + DOCS:
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")
    ok("required backend, frontend, docs, registry, evidence, and validation files exist")

    registry = json.loads(read(DOCS[1]))
    evidence = json.loads(read(DOCS[2]))
    validation = json.loads(read(DOCS[3]))
    for payload_name, payload in (("registry", registry), ("evidence", evidence), ("validation", validation)):
        if PASS_MARKER not in json.dumps(payload):
            fail(f"PASS marker missing in {payload_name}")
    if registry.get("scope") != "ASSET_CONTEXT_GA_R1" or registry.get("readOnly") is not True:
        fail("registry scope/readOnly invalid")
    for key in ("runtimeEnabled", "dbWriteEnabled", "assetGraphWriteEnabled", "edgeCommandExecution", "linkCommandExecution", "deviceControlEnabled", "productionActivation"):
        if registry.get(key) is not False:
            fail(f"registry {key} must be false")
    ok("registry/evidence/validation JSON parse and read-only flags are correct")

    api_text = read(ROOT / "AN_VANTARIS_IBMS-backend/src/api/asset_context/asset_context_api.py")
    for route in ROUTES:
        if route not in api_text:
            fail(f"missing API route string: {route}")
    for method in ('methods=["POST"]', 'methods=["PUT"]', 'methods=["PATCH"]', 'methods=["DELETE"]'):
        if method in api_text:
            fail(f"forbidden write method in asset_context API: {method}")
    ok("asset_context API routes are present and GET-only")

    backend_text = "\n".join(read(path) for path in BACKEND_FILES)
    for token in GUARDRAILS:
        if token not in backend_text:
            fail(f"read-only guardrail missing from backend: {token}")
    lowered = backend_text.lower()
    for token in FORBIDDEN_CODE_TOKENS:
        if token in lowered:
            fail(f"forbidden code token present in asset_context code: {token}")
    ok("backend read-only guardrails exist and forbidden write/runtime/control tokens are absent")

    frontend_text = "\n".join(read(path) for path in FRONTEND_FILES + MODIFIED_REFS[1:])
    for phrase in ("Asset Context", "/one/assets/context", "Read-only Mode", "Customer Preview", "Skeleton Runtime", "Asset context table", "Linkage matrix", "Read-only guardrails panel", "Not Production GA note"):
        if phrase not in frontend_text:
            fail(f"frontend phrase missing: {phrase}")
    for phrase in ("Mock", "Demo", "MVP", "Pilot", "Coming soon"):
        if phrase in read(ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/assets/AssetContext.vue"):
            fail(f"forbidden frontend label present: {phrase}")
    ok("frontend route, service, page strings, and label guardrails are correct")

    docs_text = "\n".join(read(path) for path in DOCS)
    for phrase in ("Asset / System / Device / Event / Work Order / Maintenance Task / UHMI Panel / UCDE Evidence / Reports / Customer Delivery / Foundation Diagnostics", "No DB write", "No Asset Graph canonical write", "No ONE Adapter introduction", PASS_MARKER):
        if phrase not in docs_text:
            fail(f"docs/evidence phrase missing: {phrase}")
    ok("docs and evidence contain required linkage and boundary phrases")

    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
