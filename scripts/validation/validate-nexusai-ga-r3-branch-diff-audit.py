#!/usr/bin/env python3
"""Validate NEXUSAI-GA-R3 read-only branch diff audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "ONE_NEXUSAI_GA_R3_BRANCH_DIFF_AUDIT_PASS"

BACKEND_FILES = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/nexus_ai/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/nexus_ai/nexus_branch_audit_provider.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/nexus_ai/nexus_branch_audit_service.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/nexus_ai/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/nexus_ai/nexus_ai_api.py",
]
FRONTEND_FILES = [
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/nexusAi.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/nexus/NexusBranchAudit.vue",
]
MODIFIED_REFS = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts",
]
DOCS = [
    ROOT / "AN_VANTARIS_ONE/NEXUSAI_GA_R3.md",
    ROOT / "AN_VANTARIS_ONE/registries/nexusai-ga-r3/nexusai-ga-r3.registry.json",
    ROOT / "AN_VANTARIS_ONE/registries/nexusai-ga-r3/nexusai-ga-r3.evidence.json",
    ROOT / "AN_VANTARIS_ONE/registries/nexusai-ga-r3/nexusai-ga-r3.validation.json",
]
ROUTES = [
    "/v1/one/nexus-ai/health",
    "/v1/one/nexus-ai/branch-audit/summary",
    "/v1/one/nexus-ai/branch-audit/commits",
    "/v1/one/nexus-ai/branch-audit/modules",
    "/v1/one/nexus-ai/branch-audit/risks",
    "/v1/one/nexus-ai/branch-audit/evidence-linkage",
    "/v1/one/nexus-ai/branch-audit/customer-demo-impact",
    "/v1/one/nexus-ai/branch-audit/guardrails",
]
FLAGS = {
    "readOnly": True,
    "aiRuntimeEnabled": False,
    "modelApiCallEnabled": False,
    "autoFixEnabled": False,
    "codeMutationEnabled": False,
    "workflowExecutionEnabled": False,
    "dbWriteEnabled": False,
    "edgeCommandExecution": False,
    "linkCommandExecution": False,
    "deviceControlEnabled": False,
    "productionActivation": False,
}
FORBIDDEN_EXECUTABLE_TOKENS = [
    "import subprocess",
    "from subprocess",
    "os.system",
    "requests.post",
    "import openai",
    "from openai",
    "import anthropic",
    "from anthropic",
    "db.session.add",
    "db.session.commit",
    "op.create_table",
    "op.add_column",
    "send_edge_command",
    "send_link_command",
    "execute_edge_command",
    "execute_link_command",
    "enable_device_control",
    "auto_fix(",
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
    if registry.get("scope") != "NEXUSAI_GA_R3" or registry.get("moduleId") != "nexus-ai-branch-audit":
        fail("registry scope/moduleId invalid")
    for key, expected in FLAGS.items():
        if registry.get(key) is not expected:
            fail(f"registry {key} must be {expected}")
    ok("registry/evidence/validation JSON parse and read-only flags are correct")

    api_text = read(ROOT / "AN_VANTARIS_IBMS-backend/src/api/nexus_ai/nexus_ai_api.py")
    for route in ROUTES:
        if route not in api_text:
            fail(f"missing API route string: {route}")
    for method in ('methods=["POST"]', 'methods=["PUT"]', 'methods=["PATCH"]', 'methods=["DELETE"]'):
        if method in api_text:
            fail(f"forbidden write method in nexus_ai API: {method}")
    ok("nexus_ai API routes are present and GET-only")

    backend_text = "\n".join(read(path) for path in BACKEND_FILES)
    for token in ("NEXUSAI_GA_R3", "nexus-ai-branch-audit", "VANTARIS_LIGHT_OPERATIONS_CONSOLE", "aiRuntimeEnabled", "modelApiCallEnabled", "autoFixEnabled", "codeMutationEnabled", "workflowExecutionEnabled", "dbWriteEnabled", "edgeCommandExecution", "linkCommandExecution", "deviceControlEnabled", "productionActivation"):
        if token not in backend_text:
            fail(f"backend read-only token missing: {token}")
    lowered = backend_text.lower()
    for token in FORBIDDEN_EXECUTABLE_TOKENS:
        if token in lowered:
            fail(f"forbidden executable token present in nexus_ai code: {token}")
    ok("backend read-only guardrails exist and forbidden executable tokens are absent")

    route_menu_text = "\n".join(read(path) for path in MODIFIED_REFS)
    for phrase in ("from .nexus_ai import nexus_ai_api", "/one/nexus-ai/branch-audit", "nexus-ai-branch-audit", "NexusAI Branch Audit"):
        if phrase not in route_menu_text:
            fail(f"route/menu phrase missing: {phrase}")
    frontend_text = "\n".join(read(path) for path in FRONTEND_FILES)
    for phrase in ("NexusAI Branch Audit", "Branch diff timeline", "Module readiness impact matrix", "Risk boundary table", "Evidence / Reports linkage panel", "Customer demo impact panel", "Read-only guardrails panel", "Not Production GA note"):
        if phrase not in frontend_text:
            fail(f"frontend phrase missing: {phrase}")
    for phrase in ("Mock", "MVP", "Pilot", "Coming soon"):
        if phrase in read(ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/nexus/NexusBranchAudit.vue"):
            fail(f"forbidden frontend label present: {phrase}")
    ok("frontend route/menu/page strings are present and forbidden labels are absent")

    docs_text = "\n".join(read(path) for path in DOCS)
    for phrase in ("Current Branch / Commit Diff -> NexusAI Read-only Branch Audit", "local commits not pushed", "production GA not yet", "no real export", "no DB persistence/evidence write", "no runtime activation", "no EDGE/LINK command", "no AI runtime", "no server precheck yet", "no UAT yet", "No model API call", "No auto-fix", PASS_MARKER):
        if phrase not in docs_text:
            fail(f"docs/evidence phrase missing: {phrase}")
    ok("docs and evidence contain required branch audit, risk, and boundary phrases")

    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
