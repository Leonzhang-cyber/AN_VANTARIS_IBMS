#!/usr/bin/env python3
"""Validate UMMS-GA-R2 production-grade maintenance workspace."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "UMMS_GA_R2_PRODUCTION_GRADE_MAINTENANCE_WORKSPACE_PASS"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/umms-ga-r2/umms-ga-r2-production-grade-maintenance-workspace.v1.json"

DOCS = [
    ROOT / "UMMS_GA_R2_PRODUCTION_GRADE_MAINTENANCE_WORKSPACE.md",
    ROOT / "UMMS_GA_R2_WORK_ORDER_TASK_DISPATCH_PLAN_CONTEXT_SPEC.md",
    ROOT / "UMMS_GA_R2_UHMI_UCDE_ASSET_EVENT_REPORT_LINKAGE_SPEC.md",
    ROOT / "UMMS_GA_R2_ROLE_BASED_CUSTOMER_ENGINEER_ADMIN_OPERATOR_VIEWS.md",
    ROOT / "UMMS_GA_R2_CUSTOMER_DEMO_ACCEPTANCE_CHECKLIST.md",
    ROOT / "UMMS_GA_R2_REPORT.md",
]

EVIDENCE_FILES = [
    ROOT / "AN_VANTARIS_ONE/registries/umms-ga-r2/umms-r2-workspace-data-catalog.txt",
    ROOT / "AN_VANTARIS_ONE/registries/umms-ga-r2/umms-r2-menu-route-references.txt",
    ROOT / "AN_VANTARIS_ONE/registries/umms-ga-r2/umms-r2-uhmi-ucde-asset-report-linkage.txt",
    ROOT / "AN_VANTARIS_ONE/registries/umms-ga-r2/umms-r2-role-view-matrix.txt",
    ROOT / "AN_VANTARIS_ONE/registries/umms-ga-r2/umms-r2-validator-results.txt",
    ROOT / "AN_VANTARIS_ONE/registries/umms-ga-r2/umms-r2-risk-guardrails.txt",
]

BACKEND_FILES = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/umms/umms_provider.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/umms/umms_service.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/umms/umms_api.py",
]

FRONTEND_FILES = [
    ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/umms/UmmsMaintenance.vue",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/umms.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts",
]

REQUIRED_REGISTRY_TRUE = [
    "productionDemoReady",
    "customerDemo",
    "readOnlyApi",
    "frontendWorkspace",
    "workOrderManagement",
    "taskBoard",
    "maintenancePlans",
    "preventiveMaintenance",
    "correctiveMaintenance",
    "engineerDispatch",
    "assetContext",
    "eventContext",
    "uhmiLinkage",
    "ucdeEvidenceLinkage",
    "reportsLinkage",
    "customerAcceptance",
]

REQUIRED_DOC_PHRASES = [
    "Work Management / Maintenance capability",
    "production-grade customer demo readiness",
    "not POC",
    "not mock",
    "not temporary demo",
    "does not do real work order write",
    "does not do DB write",
    "does not do runtime activation",
    "does not do device control",
    "does not do EDGE/LINK command",
    "does not do production activation",
    "192.168.60.21",
    "192.168.60.22",
    "UHMI / UCDE / Assets / Events / Reports",
    "CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device",
]

REQUIRED_FRONTEND_PHRASES = [
    "UMMS Production-grade Maintenance Workspace",
    "Production Demo Ready",
    "Read-only Mode",
    "Not POC",
    "Work Order Management",
    "Maintenance Task Board",
    "Preventive Maintenance Plan",
    "Corrective Maintenance Flow",
    "Engineer Dispatch",
    "Asset Maintenance Context",
    "Event / Fault Context",
    "UCDE Evidence Linkage",
    "UHMI Linkage",
    "Reports Linkage",
    "Customer Acceptance View",
    "Role-based Views",
    "No Work Order Write",
    "No DB Write",
    "No Runtime Activation",
    "No Direct Device Control",
]

ENDPOINTS = [
    "/one/umms/workspace",
    "/one/umms/overview",
    "/one/umms/work-orders",
    "/one/umms/tasks",
    "/one/umms/maintenance-plans",
    "/one/umms/preventive-maintenance",
    "/one/umms/corrective-maintenance",
    "/one/umms/engineer-dispatch",
    "/one/umms/asset-context",
    "/one/umms/event-context",
    "/one/umms/evidence-linkage",
    "/one/umms/report-linkage",
    "/one/umms/customer-acceptance",
    "/one/umms/role-views",
    "/one/umms/guardrails",
]

FORBIDDEN_ACTIVE_PHRASES = [
    "poc: true",
    "mock: true",
    "temporaryDemo: true",
    "work order write enabled",
    "task write enabled",
    "db write enabled",
    "runtime activation enabled",
    "direct control enabled",
    "edge command enabled",
    "link command enabled",
    "production activation enabled",
    "deployed to 192.168.60.21",
    "deployed to 192.168.60.22",
    "ssh executed",
]

FORBIDDEN_ARTIFACT_MARKERS = [
    ".env",
    "node_modules",
    "dist",
    "build",
    ".runtime",
    "secrets",
    ".tar.gz",
    ".zip",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def ok(message: str) -> None:
    print(f"[PASS] {message}")


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(read(path))
    except Exception as exc:
        fail(f"registry JSON parses: {exc}")
    if not isinstance(data, dict):
        fail("registry JSON must be an object")
    return data


def changed_paths() -> list[str]:
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    paths: list[str] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        paths.append(line[3:].strip())
    return paths


def active_phrase_present(text: str, phrase: str) -> bool:
    lower_text = text.lower()
    lower_phrase = phrase.lower()
    start = 0
    while True:
        index = lower_text.find(lower_phrase, start)
        if index == -1:
            return False
        prefix = lower_text[max(0, index - 40):index]
        if any(token in prefix for token in ("no ", "not ", "without ", "false", "not_executed")):
            start = index + len(lower_phrase)
            continue
        return True


def main() -> int:
    for path in DOCS + EVIDENCE_FILES + BACKEND_FILES + FRONTEND_FILES + [REGISTRY]:
        if not path.exists():
            fail(f"required file exists: {path.relative_to(ROOT)}")
    ok("required UMMS-GA-R2 docs, evidence, backend, frontend, and registry files exist")

    registry = load_json(REGISTRY)
    ok("registry JSON parses")

    expected = {
        "scope": "UMMS_GA_R2",
        "taskId": "UMMS-GA-R2",
        "mode": "read_only",
        "readinessLevel": "PRODUCTION_GRADE_CUSTOMER_DEMO",
        "visualStyle": "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "validationPassMarker": PASS_MARKER,
    }
    for key, value in expected.items():
        if registry.get(key) != value:
            fail(f"registry {key} must be {value}")
    for key in REQUIRED_REGISTRY_TRUE:
        if registry.get(key) is not True:
            fail(f"registry {key} must be true")
    for key in ("poc", "mock", "temporaryDemo"):
        if registry.get(key) is not False:
            fail(f"registry {key} must be false")
    ok("registry core fields and production-demo posture are correct")

    server = registry.get("serverPlanning", {})
    for key, value in {
        "appNonDbTarget": "192.168.60.21",
        "dbOnlyTarget": "192.168.60.22",
        "sshExecuted": False,
        "deploymentExecuted": False,
        "dbMigrationExecuted": False,
        "dbWrite": False,
    }.items():
        if server.get(key) != value:
            fail(f"serverPlanning.{key} must be {value}")
    ok("server planning records targets and non-execution flags")

    for key, value in registry.get("forbiddenActions", {}).items():
        if value not in (False, "NOT_EXECUTED"):
            fail(f"forbiddenActions.{key} must be false or NOT_EXECUTED")
    ok("forbiddenActions are false or NOT_EXECUTED")

    combined_docs = "\n".join(read(path) for path in DOCS + EVIDENCE_FILES)
    if PASS_MARKER not in combined_docs or PASS_MARKER not in json.dumps(registry):
        fail("PASS marker must exist in docs/evidence and registry")
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in combined_docs:
            fail(f"required doc phrase missing: {phrase}")
    ok("required documentation phrases and PASS marker are present")

    backend_text = "\n".join(read(path) for path in BACKEND_FILES)
    for token in [
        "UMMS_GA_R2",
        "read_only",
        "PRODUCTION_GRADE_CUSTOMER_DEMO",
        "productionDemoReady",
        '"poc": False',
        '"mock": False',
        '"temporaryDemo": False',
        '"workOrderWrite": False',
        '"taskWrite": False',
        '"dbWrite": False',
        '"runtimeActivation": False',
        '"deviceControl": False',
        '"edgeCommandExecution": False',
        '"linkCommandExecution": False',
    ]:
        if token not in backend_text:
            fail(f"backend token missing: {token}")
    for endpoint in ENDPOINTS:
        if endpoint not in backend_text:
            fail(f"backend endpoint missing: {endpoint}")
    for method in ('methods=["POST"]', 'methods=["PUT"]', 'methods=["PATCH"]', 'methods=["DELETE"]'):
        if method in backend_text and "umms_ga_r2" in backend_text:
            fail(f"UMMS R2 API must remain GET-only: {method}")
    ok("backend UMMS R2 API/provider is GET-only and read-only")

    frontend_text = "\n".join(read(path) for path in FRONTEND_FILES)
    for phrase in REQUIRED_FRONTEND_PHRASES:
        if phrase not in frontend_text:
            fail(f"frontend phrase missing: {phrase}")
    for phrase in ["Work Management", "UMMS Overview", "Maintenance Tasks", "/one/umms/workspace"]:
        if phrase not in frontend_text:
            fail(f"route/menu reference missing: {phrase}")
    ok("frontend workspace and route/menu references contain required UMMS production-grade entries")

    scan_text = "\n".join([combined_docs, json.dumps(registry), backend_text, frontend_text])
    for phrase in FORBIDDEN_ACTIVE_PHRASES:
        if active_phrase_present(scan_text, phrase):
            fail(f"forbidden active phrase present: {phrase}")
    ok("forbidden active design phrases are absent")

    bad_artifacts = [
        path
        for path in changed_paths()
        if any(marker in path for marker in FORBIDDEN_ARTIFACT_MARKERS)
    ]
    if bad_artifacts:
        fail(f"forbidden generated/artifact paths changed: {', '.join(sorted(bad_artifacts))}")
    ok("forbidden artifact scan is empty for current change set")

    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
