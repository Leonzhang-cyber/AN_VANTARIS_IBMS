#!/usr/bin/env python3
"""Validate Reports GA R13 customer demo report pack and export center."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "REPORTS_GA_R13_CUSTOMER_DEMO_REPORT_PACK_EXPORT_CENTER_PASS"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/reports-ga-r13/reports-ga-r13-customer-demo-report-pack-export-center.v1.json"
DOCS = [
    ROOT / "REPORTS_GA_R13_CUSTOMER_DEMO_REPORT_PACK.md",
    ROOT / "REPORTS_GA_R13_EXPORT_CENTER_PREVIEW_SPEC.md",
    ROOT / "REPORTS_GA_R13_MODULE_REPORT_LINKAGE_SPEC.md",
    ROOT / "REPORTS_GA_R13_CUSTOMER_ENGINEER_ADMIN_REPORT_PACKS.md",
    ROOT / "REPORTS_GA_R13_ACCEPTANCE_CHECKLIST.md",
    ROOT / "REPORTS_GA_R13_REPORT.md",
]
EVIDENCE = list((ROOT / "AN_VANTARIS_ONE/registries/reports-ga-r13").glob("reports-r13-*.txt"))
BACKEND = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/reports/reports_provider.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/reports/reports_service.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/reports/reports_api.py",
]
FRONTEND = [
    ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/reports/ReportsView.vue",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/reports.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts",
]
ENDPOINTS = [
    "/one/reports/customer-demo-pack",
    "/one/reports/export-center",
    "/one/reports/report-library",
    "/one/reports/umms-maintenance",
    "/one/reports/uhmi-system-status",
    "/one/reports/ucde-evidence",
    "/one/reports/customer-delivery-handoff",
    "/one/reports/foundation-diagnostics",
    "/one/reports/package-readiness",
    "/one/reports/audit-compliance",
    "/one/reports/export-queue-preview",
    "/one/reports/guardrails",
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
    for path in DOCS + EVIDENCE + BACKEND + FRONTEND + [REGISTRY]:
        if not path.exists():
            fail(f"required file exists: {path.relative_to(ROOT)}")
    ok("required Reports R13 docs, evidence, registry, backend, and frontend files exist")

    registry = json.loads(read(REGISTRY))
    expected = {
        "scope": "REPORTS_GA_R13",
        "mode": "read_only",
        "readinessLevel": "CUSTOMER_DEMO_REPORT_PACK",
        "visualStyle": "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "validationPassMarker": PASS_MARKER,
    }
    for key, value in expected.items():
        if registry.get(key) != value:
            fail(f"registry {key} must be {value}")
    for key in ("customerDemoReportPack", "exportCenterPreview"):
        if registry.get(key) is not True:
            fail(f"registry {key} must be true")
    for key in ("exportExecuted", "pdfGenerated", "excelGenerated", "zipGenerated"):
        if registry.get(key) is not False:
            fail(f"registry {key} must be false")
    ok("registry core fields are correct")

    plan = registry.get("serverPlanning", {})
    for key, value in {"appNonDbTarget": "192.168.60.21", "dbOnlyTarget": "192.168.60.22", "sshExecuted": False, "deploymentExecuted": False, "dbMigrationExecuted": False, "dbWrite": False}.items():
        if plan.get(key) != value:
            fail(f"serverPlanning.{key} must be {value}")
    ok("serverPlanning records targets and non-execution flags")

    for key in ("reportLibrary", "customerReportPack", "engineerReportPack", "adminReportPack", "ummsReportLinkage", "uhmiReportLinkage", "ucdeEvidenceReportLinkage", "customerDeliveryReportLinkage", "foundationDiagnosticsReportLinkage", "exportFormats", "exportQueuePreview"):
        if key not in registry:
            fail(f"registry missing {key}")
    for key, value in registry.get("forbiddenActions", {}).items():
        if value not in (False, "NOT_EXECUTED"):
            fail(f"forbiddenActions.{key} must be false or NOT_EXECUTED")
    ok("registry report sections and forbidden actions are present")

    related = json.dumps({k: registry.get(k, {}) for k in ("relatedUMMS", "relatedUHMI", "relatedUCDE", "relatedCustomerDelivery", "relatedFoundationDiagnostics")})
    for token in ("UMMS-GA-R2", "9d9111ddfac1a8b1ed9a488a9f4f5f1a97b59e31", "UHMI-GA-R6", "867b3d09a2cfc826dc2e1558b1dd3afb23dc77a8", "UCDE-GA-R6", "442657ac60a267d827fa02c8494e445529345e92", "CUSTOMER-DELIVERY-GA-R2", "a9bcaba94d0206ab8783878c29f696949f43d65e", "FOUNDATION-DIAGNOSTICS-GA-R1", "7818c7c8b4011455f10ab4ab319621963130403c"):
        if token not in related:
            fail(f"related release token missing: {token}")
    ok("related UMMS, UHMI, UCDE, Customer Delivery, and Foundation Diagnostics references are present")

    docs = "\n".join(read(path) for path in DOCS + EVIDENCE)
    for phrase in ("Reports & Analytics", "Customer Demo Report Pack + Export Center", "not POC", "not mock", "does not execute real export", "does not generate real PDF/Excel/ZIP", "does not do DB write", "does not do Evidence write", "does not do runtime activation", "does not do EDGE/LINK command", "does not do production activation", "192.168.60.21", "192.168.60.22", "UHMI / UCDE / UMMS / Customer Delivery / Foundation Diagnostics", "CODE -> Policy Gate -> Approval -> Audit/UCDE -> Export Artifact"):
        if phrase not in docs:
            fail(f"required doc phrase missing: {phrase}")
    if PASS_MARKER not in docs or PASS_MARKER not in json.dumps(registry):
        fail("PASS marker missing in docs/evidence or registry")
    ok("docs/evidence contain required phrases and PASS marker")

    backend = "\n".join(read(path) for path in BACKEND)
    for token in ("REPORTS_GA_R13", "read_only", "CUSTOMER_DEMO_REPORT_PACK", '"exportExecuted": False', '"pdfGenerated": False', '"excelGenerated": False', '"zipGenerated": False', '"dbWrite": False', '"evidenceWrite": False'):
        if token not in backend:
            fail(f"backend token missing: {token}")
    for endpoint in ENDPOINTS:
        if endpoint not in backend:
            fail(f"endpoint missing: {endpoint}")
    for method in ('methods=["PUT"]', 'methods=["PATCH"]', 'methods=["DELETE"]'):
        if method in backend:
            fail(f"Reports R13 backend must not add {method}")
    ok("backend Reports R13 API/provider is read-only and GET-only for R13 routes")

    frontend = "\n".join(read(path) for path in FRONTEND)
    for phrase in ("Reports & Analytics", "Customer Demo Report Pack", "Export Center Preview", "Read-only Mode", "Report Library", "UMMS Maintenance Report", "UHMI System Status Report", "UCDE Evidence Report", "Customer Delivery Handoff Report", "Foundation Diagnostics Readiness Report", "Export Formats Preview", "Export Queue Preview", "No Real Export Execution", "No PDF Generation", "No Excel Generation", "No ZIP Generation", "No DB Write", "No Production Activation", "Export Center"):
        if phrase not in frontend:
            fail(f"frontend phrase missing: {phrase}")
    ok("frontend Reports page and route/menu references are present")

    scan = "\n".join([docs, json.dumps(registry), backend, frontend])
    for phrase in ("export executed", "pdf generated", "excel generated", "zip generated", "report write enabled", "db write enabled", "evidence write enabled", "runtime activation enabled", "edge command enabled", "link command enabled", "production activation enabled", "deployed to 192.168.60.21", "deployed to 192.168.60.22", "ssh executed"):
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
