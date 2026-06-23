#!/usr/bin/env python3
"""Validate SERVER-PRECHECK-R2 read-only access window plan."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_PRECHECK_R2_READONLY_ACCESS_WINDOW_PLAN_PASS"

BACKEND = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/server_access_plan/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/server_access_plan/server_access_plan_provider.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/server_access_plan/server_access_plan_service.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/server_access_plan/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/server_access_plan/server_access_plan_api.py",
]
FRONTEND = [
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/serverAccessPlan.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/server/ServerAccessWindowPlan.vue",
]
REFS = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts",
]
DOCS = [
    ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R2.md",
    ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r2/server-precheck-r2.registry.json",
    ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r2/server-precheck-r2.evidence.json",
    ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r2/server-precheck-r2.validation.json",
]
ROUTES = [
    "/v1/one/server-access-plan/health",
    "/v1/one/server-access-plan/summary",
    "/v1/one/server-access-plan/access-window",
    "/v1/one/server-access-plan/approval-boundary",
    "/v1/one/server-access-plan/allowed-readonly-commands",
    "/v1/one/server-access-plan/evidence-capture",
    "/v1/one/server-access-plan/stop-conditions",
    "/v1/one/server-access-plan/r3-readiness",
    "/v1/one/server-access-plan/guardrails",
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
FORBIDDEN = [
    "import sub" + "process",
    "os." + "system",
    "import so" + "cket",
    "import req" + "uests",
    "para" + "miko",
    "psy" + "copg",
    "py" + "mysql",
    "sqlalchemy." + "create_engine",
    "db.session.add",
    "db.session.commit",
    "op.create_table",
    "op.add_column",
    "ssh executed",
    "deploy executed",
    "install executed",
    "run_systemctl_restart",
    "run_pm2_restart",
    "run_nginx_reload",
    "send_edge_command",
    "send_link_command",
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
    for path in BACKEND + FRONTEND + REFS + DOCS + [ROOT / "scripts/validation/validate-server-precheck-r2-readonly-access-window-plan.py"]:
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")
    ok("required backend, frontend, docs, registry, evidence, and validation files exist")

    registry = json.loads(read(DOCS[1]))
    evidence = json.loads(read(DOCS[2]))
    validation = json.loads(read(DOCS[3]))
    for name, payload in (("registry", registry), ("evidence", evidence), ("validation", validation)):
        if PASS not in json.dumps(payload):
            fail(f"PASS marker missing in {name}")
    for key, expected in FLAGS.items():
        if registry.get(key) is not expected:
            fail(f"registry {key} must be {expected}")
    ok("registry/evidence/validation JSON parse and read-only flags are correct")

    api = read(BACKEND[4])
    for route in ROUTES:
        if route not in api:
            fail(f"missing API route: {route}")
    for method in ('methods=["POST"]', 'methods=["PUT"]', 'methods=["PATCH"]', 'methods=["DELETE"]'):
        if method in api:
            fail(f"forbidden method in server_access_plan API: {method}")
    ok("server_access_plan API routes are present and GET-only")

    backend_text = "\n".join(read(path) for path in BACKEND)
    for token in ("SERVER_PRECHECK_R2", "server-access-window-plan", "access window", "approval boundary", "allowed read-only commands", "evidence capture", "stop conditions", "R3 readiness", "planning-only", "not executed in R2"):
        if token not in backend_text:
            fail(f"backend token missing: {token}")
    lowered = backend_text.lower()
    for token in FORBIDDEN:
        if token in lowered:
            fail(f"forbidden executable token present: {token}")
    ok("backend R2 planning tokens are present and executable tokens are absent")

    ref_text = "\n".join(read(path) for path in REFS)
    for phrase in ("from .server_access_plan import server_access_plan_api", "/one/server/access-window-plan", "server-access-window-plan", "Server Access Window Plan"):
        if phrase not in ref_text:
            fail(f"route/menu phrase missing: {phrase}")
    frontend_text = "\n".join(read(path) for path in FRONTEND)
    for phrase in ("Summary cards", "APP/DB target server cards", "Access window plan", "Approval boundary table", "Allowed read-only command catalog", "Evidence capture plan", "Stop / abort conditions", "R3 readiness panel", "Read-only guardrails panel", "Not Production GA note"):
        if phrase not in frontend_text:
            fail(f"frontend phrase missing: {phrase}")
    for forbidden_label in ("Mock", "MVP", "Pilot", "Coming soon"):
        if forbidden_label in read(FRONTEND[1]):
            fail(f"forbidden frontend label present: {forbidden_label}")
    ok("frontend route/menu/page strings are present and forbidden labels are absent")

    docs = "\n".join(read(path) for path in DOCS)
    for phrase in ("access window", "approval boundary", "allowed read-only commands", "evidence capture", "stop conditions", "R3 readiness", "planning-only", "not executed in R2", PASS):
        if phrase not in docs:
            fail(f"docs phrase missing: {phrase}")
    ok("docs and evidence contain required R2 phrases")

    print(PASS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
