#!/usr/bin/env python3
"""Validate CODE-GA-R1 read-only policy gate preview."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "ONE_CODE_GA_R1_POLICY_GATE_PREVIEW_PASS"

BACKEND_FILES = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/code_policy/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/code_policy/code_policy_provider.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/code_policy/code_policy_service.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/code_policy/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/code_policy/code_policy_api.py",
]
FRONTEND_FILES = [
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/codePolicy.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/code/CodePolicyGate.vue",
]
MODIFIED_REFS = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts",
]
DOCS = [
    ROOT / "AN_VANTARIS_ONE/CODE_GA_R1.md",
    ROOT / "AN_VANTARIS_ONE/registries/code-ga-r1/code-ga-r1.registry.json",
    ROOT / "AN_VANTARIS_ONE/registries/code-ga-r1/code-ga-r1.evidence.json",
    ROOT / "AN_VANTARIS_ONE/registries/code-ga-r1/code-ga-r1.validation.json",
]
ROUTES = [
    "/v1/one/code-policy/health",
    "/v1/one/code-policy/summary",
    "/v1/one/code-policy/policy-gates",
    "/v1/one/code-policy/execution-boundary",
    "/v1/one/code-policy/approval-boundary",
    "/v1/one/code-policy/evidence-linkage",
    "/v1/one/code-policy/control-path",
    "/v1/one/code-policy/guardrails",
]
FLAGS = {
    "readOnly": True,
    "runtimeEnabled": False,
    "approvalExecutionEnabled": False,
    "policyMutationEnabled": False,
    "workflowExecutionEnabled": False,
    "commandExecutionEnabled": False,
    "dbWriteEnabled": False,
    "edgeCommandExecution": False,
    "linkCommandExecution": False,
    "deviceControlEnabled": False,
    "productionActivation": False,
}
FORBIDDEN_EXECUTABLE_TOKENS = [
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
    "run_approval(",
    "execute_approval(",
    "start_workflow(",
    "activate_runtime(",
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
    if registry.get("scope") != "CODE_GA_R1" or registry.get("moduleId") != "code-policy":
        fail("registry scope/moduleId invalid")
    for key, expected in FLAGS.items():
        if registry.get(key) is not expected:
            fail(f"registry {key} must be {expected}")
    ok("registry/evidence/validation JSON parse and read-only flags are correct")

    api_text = read(ROOT / "AN_VANTARIS_IBMS-backend/src/api/code_policy/code_policy_api.py")
    for route in ROUTES:
        if route not in api_text:
            fail(f"missing API route string: {route}")
    for method in ('methods=["POST"]', 'methods=["PUT"]', 'methods=["PATCH"]', 'methods=["DELETE"]'):
        if method in api_text:
            fail(f"forbidden write method in code_policy API: {method}")
    ok("code_policy API routes are present and GET-only")

    backend_text = "\n".join(read(path) for path in BACKEND_FILES)
    for token in ("CODE_GA_R1", "code-policy", "VANTARIS_LIGHT_OPERATIONS_CONSOLE", "approvalExecutionEnabled", "commandExecutionEnabled", "dbWriteEnabled", "edgeCommandExecution", "linkCommandExecution", "deviceControlEnabled", "productionActivation"):
        if token not in backend_text:
            fail(f"backend read-only token missing: {token}")
    lowered = backend_text.lower()
    for token in FORBIDDEN_EXECUTABLE_TOKENS:
        if token in lowered:
            fail(f"forbidden executable token present in code_policy code: {token}")
    ok("backend read-only guardrails exist and forbidden executable tokens are absent")

    route_menu_text = "\n".join(read(path) for path in MODIFIED_REFS)
    for phrase in ("from .code_policy import code_policy_api", "/one/code/policy-gate", "code-policy-gate", "CODE Policy Gate"):
        if phrase not in route_menu_text:
            fail(f"route/menu phrase missing: {phrase}")
    frontend_text = "\n".join(read(path) for path in FRONTEND_FILES)
    for phrase in ("CODE Policy Gate", "Required control path visualization", "Policy gate table", "Approval boundary timeline", "Evidence linkage matrix", "Blocked direct paths panel", "Read-only guardrails panel", "Not Production GA note"):
        if phrase not in frontend_text:
            fail(f"frontend phrase missing: {phrase}")
    for phrase in ("Mock", "MVP", "Pilot", "Coming soon"):
        if phrase in read(ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/code/CodePolicyGate.vue"):
            fail(f"forbidden frontend label present: {phrase}")
    ok("frontend route/menu/page strings are present and forbidden labels are absent")

    docs_text = "\n".join(read(path) for path in DOCS)
    for phrase in ("UHMI / UMMS / Asset Context -> CODE Policy Gate -> Approval Boundary -> Audit / UCDE Evidence -> LINK -> EDGE -> Device", "No direct device control", "No EDGE/LINK command", "No DB write", "No approval execution", "No runtime activation", "No production activation", "No bypass CODE", "No auth/RBAC mutation", PASS_MARKER):
        if phrase not in docs_text:
            fail(f"docs/evidence phrase missing: {phrase}")
    ok("docs and evidence contain required policy boundary phrases")

    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    sys.exit(main())

