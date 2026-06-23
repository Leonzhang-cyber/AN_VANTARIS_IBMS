#!/usr/bin/env python3
"""Validate SERVER-PRECHECK-R1 dual-server read-only environment audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "ONE_SERVER_PRECHECK_R1_DUAL_SERVER_READONLY_AUDIT_PASS"

BACKEND_FILES = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/server_precheck/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/server_precheck/server_precheck_provider.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/server_precheck/server_precheck_service.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/server_precheck/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/server_precheck/server_precheck_api.py",
]
FRONTEND_FILES = [
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/serverPrecheck.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/server/ServerPrecheckAudit.vue",
]
MODIFIED_REFS = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts",
]
DOCS = [
    ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R1.md",
    ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r1/server-precheck-r1.registry.json",
    ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r1/server-precheck-r1.evidence.json",
    ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r1/server-precheck-r1.validation.json",
]
ROUTES = [
    "/v1/one/server-precheck/health",
    "/v1/one/server-precheck/summary",
    "/v1/one/server-precheck/server-plan",
    "/v1/one/server-precheck/app-server",
    "/v1/one/server-precheck/db-server",
    "/v1/one/server-precheck/checklist",
    "/v1/one/server-precheck/blockers",
    "/v1/one/server-precheck/handoff-readiness",
    "/v1/one/server-precheck/guardrails",
]
FLAGS = {
    "readOnly": True,
    "sshExecuted": False,
    "deploymentExecuted": False,
    "installExecuted": False,
    "dbConnectionExecuted": False,
    "dbMigrationExecuted": False,
    "dbWriteEnabled": False,
    "healthcheckRuntimeExecuted": False,
    "nginxSetupExecuted": False,
    "pm2SetupExecuted": False,
    "systemdSetupExecuted": False,
    "edgeCommandExecution": False,
    "linkCommandExecution": False,
    "deviceControlEnabled": False,
    "productionActivation": False,
}
FORBIDDEN_EXECUTABLE_TOKENS = [
    "import subprocess",
    "from subprocess",
    "os.system",
    "import socket",
    "from socket",
    "import requests",
    "from requests",
    "paramiko",
    "psycopg",
    "pymysql",
    "sqlalchemy.create_engine",
    "db.session.add",
    "db.session.commit",
    "op.create_table",
    "op.add_column",
    "ssh_client",
    "deploy(",
    "install(",
    "systemctl",
    "pm2 ",
    "nginx -s",
    "execute_healthcheck",
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
    for name, payload in (("registry", registry), ("evidence", evidence), ("validation", validation)):
        if PASS_MARKER not in json.dumps(payload):
            fail(f"PASS marker missing in {name}")
    if registry.get("scope") != "SERVER_PRECHECK_R1" or registry.get("moduleId") != "server-precheck":
        fail("registry scope/moduleId invalid")
    for key, expected in FLAGS.items():
        if registry.get(key) is not expected:
            fail(f"registry {key} must be {expected}")
    ok("registry/evidence/validation JSON parse and read-only flags are correct")

    api_text = read(ROOT / "AN_VANTARIS_IBMS-backend/src/api/server_precheck/server_precheck_api.py")
    for route in ROUTES:
        if route not in api_text:
            fail(f"missing API route string: {route}")
    for method in ('methods=["POST"]', 'methods=["PUT"]', 'methods=["PATCH"]', 'methods=["DELETE"]'):
        if method in api_text:
            fail(f"forbidden write method in server_precheck API: {method}")
    ok("server_precheck API routes are present and GET-only")

    backend_text = "\n".join(read(path) for path in BACKEND_FILES)
    for token in ("SERVER_PRECHECK_R1", "server-precheck", "VANTARIS_LIGHT_OPERATIONS_CONSOLE", "sshExecuted", "deploymentExecuted", "installExecuted", "dbConnectionExecuted", "dbMigrationExecuted", "dbWriteEnabled", "healthcheckRuntimeExecuted", "nginxSetupExecuted", "pm2SetupExecuted", "systemdSetupExecuted", "edgeCommandExecution", "linkCommandExecution", "deviceControlEnabled", "productionActivation"):
        if token not in backend_text:
            fail(f"backend read-only token missing: {token}")
    lowered = backend_text.lower()
    for token in FORBIDDEN_EXECUTABLE_TOKENS:
        if token in lowered:
            fail(f"forbidden executable token present in server_precheck code: {token}")
    ok("backend read-only guardrails exist and forbidden executable tokens are absent")

    route_menu_text = "\n".join(read(path) for path in MODIFIED_REFS)
    for phrase in ("from .server_precheck import server_precheck_api", "/one/server/precheck", "server-precheck-audit", "Server Precheck"):
        if phrase not in route_menu_text:
            fail(f"route/menu phrase missing: {phrase}")
    frontend_text = "\n".join(read(path) for path in FRONTEND_FILES)
    for phrase in ("Server Precheck", "APP/DB dual-server plan", "APP server readiness panel", "DB server readiness panel", "Precheck checklist table", "Blockers table", "Handoff readiness panel", "Read-only guardrails panel", "Not Production GA note"):
        if phrase not in frontend_text:
            fail(f"frontend phrase missing: {phrase}")
    for phrase in ("Mock", "MVP", "Pilot", "Coming soon"):
        if phrase in read(ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/server/ServerPrecheckAudit.vue"):
            fail(f"forbidden frontend label present: {phrase}")
    ok("frontend route/menu/page strings are present and forbidden labels are absent")

    docs_text = "\n".join(read(path) for path in DOCS)
    for phrase in ("192.168.60.21", "192.168.60.22", "No SSH/server access performed", "No deployment performed", "No DB connection tested", "No DB migration executed", "No runtime healthcheck executed", "No backup/restore drill executed", "No UAT executed", "No production monitoring enabled", "Remote branch not aligned with local latest commits", "No Nginx/PM2/systemd setup", PASS_MARKER):
        if phrase not in docs_text:
            fail(f"docs/evidence phrase missing: {phrase}")
    ok("docs and evidence contain required server precheck, blocker, and boundary phrases")

    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    sys.exit(main())

