#!/usr/bin/env python3
"""Validate SERVER-PRECHECK-R3 actual read-only observation plan."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_PRECHECK_R3_ACTUAL_READONLY_OBSERVATION_PLAN_PASS"

BACKEND = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/server_observation_plan/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/server_observation_plan/server_observation_plan_provider.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/server_observation_plan/server_observation_plan_service.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/server_observation_plan/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/server_observation_plan/server_observation_plan_api.py",
]
FRONTEND = [
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/serverObservationPlan.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/server/ServerObservationPlan.vue",
]
REFS = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts",
]
DOCS = [
    ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R3.md",
    ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r3/server-precheck-r3.registry.json",
    ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r3/server-precheck-r3.evidence.json",
    ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r3/server-precheck-r3.validation.json",
]
ROUTES = [
    "/v1/one/server-observation-plan/health",
    "/v1/one/server-observation-plan/summary",
    "/v1/one/server-observation-plan/execution-sequence",
    "/v1/one/server-observation-plan/app-server-observation",
    "/v1/one/server-observation-plan/db-server-observation",
    "/v1/one/server-observation-plan/evidence-package",
    "/v1/one/server-observation-plan/stop-conditions",
    "/v1/one/server-observation-plan/approval-checklist",
    "/v1/one/server-observation-plan/guardrails",
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
    "actualObservationExecuted": False,
}
FORBIDDEN_EXECUTABLE = [
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
    "methods=[\"POST\"]",
    "methods=[\"PUT\"]",
    "methods=[\"PATCH\"]",
    "methods=[\"DELETE\"]",
    "systemctl restart",
    "systemctl start",
    "systemctl stop",
    "pm2 restart",
    "pm2 start",
    "pm2 delete",
    "nginx -s reload",
    "psql -c",
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
    required = BACKEND + FRONTEND + REFS + DOCS + [
        ROOT / "scripts/validation/validate-server-precheck-r3-actual-readonly-observation-plan.py"
    ]
    for path in required:
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
            fail(f"forbidden method in server_observation_plan API: {method}")
    ok("server_observation_plan API routes are present and GET-only")

    backend_text = "\n".join(read(path) for path in BACKEND)
    for token in (
        "SERVER_PRECHECK_R3",
        "server-observation-plan",
        "actual approved read-only server observation plan",
        "execution sequence",
        "app server observation",
        "db server observation",
        "evidence package",
        "stop conditions",
        "approval checklist",
        "planned-only",
        "not executed in R3",
        "separate approval required",
    ):
        if token not in backend_text:
            fail(f"backend token missing: {token}")
    lowered = backend_text.lower()
    for token in FORBIDDEN_EXECUTABLE:
        if token in lowered:
            fail(f"forbidden executable token present: {token}")
    ok("backend R3 planning tokens are present and executable tokens are absent")

    ref_text = "\n".join(read(path) for path in REFS)
    for phrase in (
        "from .server_observation_plan import server_observation_plan_api",
        "/one/server/observation-plan",
        "server-observation-plan",
        "Server Observation Plan",
    ):
        if phrase not in ref_text:
            fail(f"route/menu phrase missing: {phrase}")
    frontend_text = "\n".join(read(path) for path in FRONTEND)
    for phrase in (
        "Summary cards",
        "APP/DB target server cards",
        "Execution sequence timeline",
        "APP server planned read-only command table",
        "DB server planned read-only command table",
        "Evidence package plan",
        "Stop / abort conditions",
        "Approval checklist",
        "Read-only guardrails panel",
        "Not Production GA note",
    ):
        if phrase not in frontend_text:
            fail(f"frontend phrase missing: {phrase}")
    for forbidden_label in ("Mock", "MVP", "Pilot", "Coming soon"):
        if forbidden_label in read(FRONTEND[1]):
            fail(f"forbidden frontend label present: {forbidden_label}")
    ok("frontend route/menu/page strings are present and forbidden labels are absent")

    docs = "\n".join(read(path) for path in DOCS)
    for phrase in (
        "actual approved read-only server observation plan",
        "execution sequence",
        "app server observation",
        "db server observation",
        "evidence package",
        "stop conditions",
        "approval checklist",
        "planned-only",
        "not executed in R3",
        "separate approval required",
        PASS,
    ):
        if phrase not in docs:
            fail(f"docs phrase missing: {phrase}")
    ok("docs and evidence contain required R3 phrases")

    print(PASS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
