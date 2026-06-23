#!/usr/bin/env python3
"""Validate Foundation Diagnostics GA R1 Engineer Diagnostics Workspace."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "FOUNDATION_DIAGNOSTICS_GA_R1_ENGINEER_DIAGNOSTICS_WORKSPACE_PASS"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/foundation-diagnostics-ga-r1/foundation-diagnostics-ga-r1-engineer-diagnostics-workspace.v1.json"
DOCS = [
    ROOT / "FOUNDATION_DIAGNOSTICS_GA_R1_ENGINEER_DIAGNOSTICS_WORKSPACE.md",
    ROOT / "FOUNDATION_DIAGNOSTICS_GA_R1_EDGE_LINK_DB_CONTRACTS_READINESS_SPEC.md",
    ROOT / "FOUNDATION_DIAGNOSTICS_GA_R1_DUAL_SERVER_PLAN_AND_OFFLINE_HEALTHCHECK_PREVIEW.md",
    ROOT / "FOUNDATION_DIAGNOSTICS_GA_R1_PACKAGE_INTEGRITY_AND_ROLLBACK_READINESS.md",
    ROOT / "FOUNDATION_DIAGNOSTICS_GA_R1_CUSTOMER_ENGINEER_ACCEPTANCE_CHECKLIST.md",
    ROOT / "FOUNDATION_DIAGNOSTICS_GA_R1_REPORT.md",
]
EVIDENCE = list((ROOT / "AN_VANTARIS_ONE/registries/foundation-diagnostics-ga-r1").glob("foundation-diagnostics-r1-*.txt"))
BACKEND = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/foundation_diagnostics/provider.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/foundation_diagnostics/service.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/foundation_diagnostics/foundation_diagnostics_api.py",
]
FRONTEND = [
    ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/foundation-diagnostics/FoundationDiagnosticsWorkspace.vue",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/foundationDiagnostics.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts",
]

ENDPOINTS = [
    "/one/foundation-diagnostics/workspace",
    "/one/foundation-diagnostics/overview",
    "/one/foundation-diagnostics/server-plan",
    "/one/foundation-diagnostics/package-readiness",
    "/one/foundation-diagnostics/edge-readiness",
    "/one/foundation-diagnostics/link-readiness",
    "/one/foundation-diagnostics/db-readiness",
    "/one/foundation-diagnostics/contracts-readiness",
    "/one/foundation-diagnostics/offline-checklist",
    "/one/foundation-diagnostics/healthcheck-preview",
    "/one/foundation-diagnostics/package-integrity",
    "/one/foundation-diagnostics/rollback-readiness",
    "/one/foundation-diagnostics/guardrails",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[PASS] {message}")


def active_phrase_present(text: str, phrase: str) -> bool:
    lower = text.lower()
    needle = phrase.lower()
    start = 0
    while True:
        idx = lower.find(needle, start)
        if idx == -1:
            return False
        prefix = lower[max(0, idx - 48):idx]
        if any(token in prefix for token in ("no ", "not ", "does not ", "false", "not_executed")):
            start = idx + len(needle)
            continue
        return True


def changed_paths() -> list[str]:
    proc = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return [line[3:].strip() for line in proc.stdout.splitlines() if line.strip()]


def main() -> int:
    required = DOCS + EVIDENCE + BACKEND + FRONTEND + [REGISTRY]
    for path in required:
        if not path.exists():
            fail(f"required file exists: {path.relative_to(ROOT)}")
    ok("required Foundation Diagnostics docs, evidence, registry, backend, and frontend files exist")

    registry = json.loads(read(REGISTRY))
    checks = {
        "scope": "FOUNDATION_DIAGNOSTICS_GA_R1",
        "mode": "read_only",
        "readinessLevel": "ENGINEER_DIAGNOSTICS_WORKSPACE",
        "visualStyle": "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "validationPassMarker": PASS_MARKER,
    }
    for key, value in checks.items():
        if registry.get(key) != value:
            fail(f"registry {key} must be {value}")
    if registry.get("engineerDiagnosticsWorkspace") is not True:
        fail("registry engineerDiagnosticsWorkspace must be true")
    ok("registry core fields are correct")

    plan = registry.get("serverPlan", {})
    for key, value in {
        "appNonDbTarget": "192.168.60.21",
        "dbOnlyTarget": "192.168.60.22",
        "sshExecuted": False,
        "deploymentExecuted": False,
        "installExecuted": False,
        "dbConnectionExecuted": False,
        "dbMigrationExecuted": False,
        "dbWrite": False,
    }.items():
        if plan.get(key) != value:
            fail(f"serverPlan.{key} must be {value}")
    ok("serverPlan records targets and non-execution flags")

    for key in ("packageReadiness", "edgeReadiness", "linkReadiness", "dbReadiness", "contractsReadiness", "healthcheckPreview", "packageIntegrityPreview", "rollbackReadiness"):
        if key not in registry:
            fail(f"registry missing {key}")
    for key, value in registry.get("forbiddenActions", {}).items():
        if value not in (False, "NOT_EXECUTED"):
            fail(f"forbiddenActions.{key} must be false or NOT_EXECUTED")
    ok("readiness sections and forbidden actions are present")

    related = json.dumps({k: registry.get(k, {}) for k in ("relatedCustomerDelivery", "relatedUHMI", "relatedUCDE", "relatedUMMS")})
    for token in ("CUSTOMER-DELIVERY-GA-R2", "a9bcaba94d0206ab8783878c29f696949f43d65e", "UHMI-GA-R6", "867b3d09a2cfc826dc2e1558b1dd3afb23dc77a8", "UCDE-GA-R6", "442657ac60a267d827fa02c8494e445529345e92", "UMMS-GA-R2", "9d9111ddfac1a8b1ed9a488a9f4f5f1a97b59e31"):
        if token not in related:
            fail(f"related release token missing: {token}")
    ok("related Customer Delivery, UHMI, UCDE, and UMMS references are present")

    docs = "\n".join(read(path) for path in DOCS + EVIDENCE)
    for phrase in ("Engineer Diagnostics Workspace", "shared foundation packages", "consumer and read-only diagnostics view", "does not do real SSH", "does not do real deployment", "does not do install/uninstall/rollback", "does not do DB connection / DB migration / DB write", "does not do EDGE/LINK command", "does not do device control", "does not do runtime activation", "does not do production activation", "192.168.60.21", "192.168.60.22", "CODE -> Policy Gate -> Approval -> Audit/UCDE -> LINK -> EDGE -> Device"):
        if phrase not in docs:
            fail(f"required doc phrase missing: {phrase}")
    if PASS_MARKER not in docs or PASS_MARKER not in json.dumps(registry):
        fail("PASS marker missing in docs/evidence or registry")
    ok("docs/evidence contain required phrases and PASS marker")

    backend = "\n".join(read(path) for path in BACKEND)
    for token in ("FOUNDATION_DIAGNOSTICS_GA_R1", "read_only", "ENGINEER_DIAGNOSTICS_WORKSPACE", "192.168.60.21", "192.168.60.22", '"sshExecuted": False', '"deploymentExecuted": False', '"installExecuted": False', '"dbConnectionExecuted": False', '"dbMigrationExecuted": False', '"dbWrite": False', '"edgeCommandExecution": False', '"linkCommandExecution": False'):
        if token not in backend:
            fail(f"backend token missing: {token}")
    for endpoint in ENDPOINTS:
        if endpoint not in backend:
            fail(f"endpoint missing: {endpoint}")
    for method in ('methods=["POST"]', 'methods=["PUT"]', 'methods=["PATCH"]', 'methods=["DELETE"]'):
        if method in backend:
            fail(f"backend must remain GET-only: {method}")
    ok("backend provider/API is GET-only and read-only")

    frontend = "\n".join(read(path) for path in FRONTEND)
    for phrase in ("Foundation Diagnostics Workspace", "Engineer Diagnostics", "Read-only Mode", "192.168.60.21", "192.168.60.22", "EDGE Readiness", "LINK Readiness", "DB Foundation Readiness", "Contracts Readiness", "Offline Package Readiness", "Healthcheck Preview", "Package Integrity Preview", "Rollback Readiness", "No SSH", "No Install", "No DB Migration", "No EDGE Command Execution", "No LINK Command Execution", "No Production Activation"):
        if phrase not in frontend:
            fail(f"frontend phrase missing: {phrase}")
    for phrase in ("Foundation Diagnostics", "Engineer Diagnostics", "/console/foundation-diagnostics/workspace"):
        if phrase not in frontend:
            fail(f"route/menu phrase missing: {phrase}")
    ok("frontend workspace and route/menu references are present")

    scan = "\n".join([docs, json.dumps(registry), backend, frontend])
    for phrase in ("ssh executed", "deployed to 192.168.60.21", "deployed to 192.168.60.22", "install enabled", "rollback enabled", "db connection enabled", "db migration enabled", "db write enabled", "runtime activation enabled", "edge command enabled", "link command enabled", "device control enabled", "production activation enabled"):
        if active_phrase_present(scan, phrase):
            fail(f"forbidden active phrase present: {phrase}")
    bad = []
    for path in changed_paths():
        parts = set(Path(path).parts)
        if parts & {"node_modules", "dist", "build", ".runtime", "secrets"}:
            bad.append(path)
        if path.endswith((".env", ".tar.gz", ".zip")):
            bad.append(path)
    if bad:
        fail(f"forbidden artifacts changed: {', '.join(bad)}")
    ok("forbidden active phrases and artifact changes are absent")

    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
