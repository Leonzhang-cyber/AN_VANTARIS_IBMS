#!/usr/bin/env python3
"""Validate UCDE-GA-R4 Evidence Center Customer Preview freeze."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "UCDE_GA_R4_EVIDENCE_CENTER_CUSTOMER_PREVIEW_PASS"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/ucde-ga-r4/ucde-ga-r4-evidence-center-customer-preview.v1.json"

DOCS = [
    ROOT / "UCDE_GA_R4_EVIDENCE_CENTER_CUSTOMER_PREVIEW.md",
    ROOT / "UCDE_GA_R4_UHMI_EVIDENCE_LINKAGE_SPEC.md",
    ROOT / "UCDE_GA_R4_EVIDENCE_OBJECT_MODEL_AND_CATALOG.md",
    ROOT / "UCDE_GA_R4_CUSTOMER_PREVIEW_ACCEPTANCE_CHECKLIST.md",
    ROOT / "UCDE_GA_R4_REPORT.md",
]

EVIDENCE_FILES = [
    ROOT / "AN_VANTARIS_ONE/registries/ucde-ga-r4/ucde-r4-evidence-catalog.txt",
    ROOT / "AN_VANTARIS_ONE/registries/ucde-ga-r4/ucde-r4-uhmi-linkage.txt",
    ROOT / "AN_VANTARIS_ONE/registries/ucde-ga-r4/ucde-r4-customer-preview-checklist.txt",
    ROOT / "AN_VANTARIS_ONE/registries/ucde-ga-r4/ucde-r4-validator-results.txt",
    ROOT / "AN_VANTARIS_ONE/registries/ucde-ga-r4/ucde-r4-risk-guardrails.txt",
]

BACKEND_FILES = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/ucde/evidence_provider.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/ucde/evidence_service.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/ucde/ucde_api.py",
]

FRONTEND_FILES = [
    ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/ucde/EvidenceCenter.vue",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/ucde.ts",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/uhmi/UhmiWorkspace.vue",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/uhmi.ts",
]

REQUIRED_COMMITS = [
    "003f4f710cfd76130ff79275c8190ec6bbe7edc9",
    "6d682fdd351e3ad51b27ce91f2dbf92c74da3323",
    "3678150d55f2459def6fc7b423496acb62143ac4",
    "0262d90efffbb4993215d44c35f7c4d26f6d762f",
    "e6c94cefcc7aee336d4702bc377a554a549454eb",
    "6bd6bbaa0e23eee6676e170d2493d093084216a5",
    "b9e74f09394dee25d3a3b09da729f034431d3cf2",
    "1181339555067af75cc492cc12cf83fb433bc1a7",
    "138cb73906ef1026e34461bf1eb0583bb3878d9e",
    "561106f2c91a4fd6a706843c4f5b34f27671f285",
    "867b3d09a2cfc826dc2e1558b1dd3afb23dc77a8",
]

REQUIRED_STAGES = [
    "UHMI-GA-R1",
    "UHMI-GA-R2A",
    "UHMI-GA-R2B",
    "UHMI-GA-R2C",
    "UHMI-GA-R2D",
    "UHMI-GA-R2E",
    "UHMI-GA-R2F",
    "UHMI-GA-R3",
    "UHMI-GA-R4",
    "UHMI-GA-R5",
    "UHMI-GA-R6",
]

EVIDENCE_TYPES = [
    "UHMI_WORKSPACE_EVIDENCE",
    "SYSTEM_CONTEXT_EVIDENCE",
    "DEVICE_CONTEXT_EVIDENCE",
    "EVENT_CONTEXT_EVIDENCE",
    "CUSTOMER_PREVIEW_EVIDENCE",
    "RELEASE_INDEX_EVIDENCE",
    "VALIDATOR_RESULT_EVIDENCE",
    "ACCEPTANCE_CHECKLIST_EVIDENCE",
    "OFFLINE_DEMO_HANDOFF_EVIDENCE",
    "RELEASE_DECISION_EVIDENCE",
]

UHMI_AREAS = [
    "UHMI Overview",
    "System Context Panels",
    "Device Context Table",
    "Mimic Panel Preview",
    "Event Context",
    "Evidence Context",
    "Role-based Views",
    "Guardrails",
    "Future Control Path",
    "Customer Preview Package",
    "Offline Demo Hand-off",
    "Final Release Decision",
]

DOC_PHRASES = [
    "Evidence Center Customer Preview",
    "UHMI Evidence Linkage",
    "Customer-readable Evidence Catalog",
    "Engineer Trace Context",
    "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
    "NOT EXECUTED",
    "No Evidence Write",
    "No DB Write",
    "No Runtime Activation",
    "No Direct Device Control",
    "No EDGE Command Execution",
    "No LINK Command Execution",
    "No auth / login / JWT / RBAC mutation",
    "UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device",
]

FORBIDDEN_ACTIVE_PHRASES = [
    "evidence write enabled",
    "db write enabled",
    "runtime activation enabled",
    "direct control enabled",
    "edge command enabled",
    "link command enabled",
    "rbac mutation enabled",
    "permission write enabled",
    "production activation enabled",
    "SCADA replacement",
    "HMI Server",
    "dark SCADA dashboard",
    "深蓝色主题",
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


def load_registry() -> dict[str, Any]:
    try:
        return json.loads(read(REGISTRY))
    except Exception as exc:  # pragma: no cover
        fail(f"registry JSON parses: {exc}")


def run_validator(script: str, marker: str) -> None:
    path = ROOT / script
    if not path.exists():
        ok(f"{Path(script).name} absent; optional dependency not executed")
        return
    proc = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if proc.returncode != 0 or marker not in proc.stdout:
        print(proc.stdout)
        fail(f"{Path(script).name} did not return {marker}")
    ok(f"{Path(script).name} returned {marker}")


def main() -> int:
    for path in DOCS + EVIDENCE_FILES + [REGISTRY]:
        if not path.exists():
            fail(f"required file exists: {path.relative_to(ROOT)}")
    ok("all UCDE-GA-R4 docs, evidence files, and registry exist")

    registry = load_registry()
    ok("registry JSON parses")

    if registry.get("scope") != "UCDE_GA_R4":
        fail("registry scope must be UCDE_GA_R4")
    if registry.get("taskId") != "UCDE-GA-R4":
        fail("registry taskId must be UCDE-GA-R4")
    if registry.get("mode") != "read_only":
        fail("registry mode must be read_only")
    if registry.get("visualStyle") != "VANTARIS_LIGHT_OPERATIONS_CONSOLE":
        fail("registry visualStyle mismatch")
    if registry.get("validationPassMarker") != PASS_MARKER:
        fail("registry PASS marker mismatch")
    ok("registry scope, taskId, mode, visualStyle, and PASS marker are correct")

    for key in (
        "evidenceCenterCustomerPreview",
        "uhmiEvidenceLinkage",
        "customerReadableEvidence",
        "engineerTraceContext",
    ):
        if registry.get(key) is not True:
            fail(f"registry {key} must be true")
    ok("registry preview flags are true")

    forbidden = registry.get("forbiddenActions", {})
    for key in (
        "evidenceWrite",
        "dbWrite",
        "dbMigration",
        "runtimeActivation",
        "deviceControl",
        "edgeCommandExecution",
        "linkCommandExecution",
        "authMutation",
        "loginMutation",
        "jwtMutation",
        "rbacMutation",
        "packageStateMutation",
        "productionActivation",
        "runnablePackageGeneration",
        "distBuildCommit",
        "secretsExport",
    ):
        if forbidden.get(key) is not False:
            fail(f"forbiddenActions.{key} must be false")
    ok("all forbiddenActions are false")

    chain = registry.get("relatedUhmiReleaseChain", [])
    chain_text = json.dumps(chain, sort_keys=True)
    for stage in REQUIRED_STAGES:
        if stage not in chain_text:
            fail(f"related UHMI chain missing {stage}")
    for commit in REQUIRED_COMMITS:
        if commit not in chain_text:
            fail(f"related UHMI chain missing commit {commit}")
    ok("UHMI R1-R6 chain includes required stages and commits")

    if set(EVIDENCE_TYPES) - set(registry.get("evidenceTypes", [])):
        fail("registry evidenceTypes missing required values")
    if set(UHMI_AREAS) - set(registry.get("uhmiLinkedAreas", [])):
        fail("registry uhmiLinkedAreas missing required values")
    ok("registry evidence types and UHMI linked areas are complete")

    fields = set(registry.get("evidenceObjectModel", {}).get("fields", []))
    required_fields = {
        "evidenceId",
        "evidenceType",
        "title",
        "sourceModule",
        "linkedWorkspace",
        "linkedObjectType",
        "linkedObjectId",
        "customerVisible",
        "engineerVisible",
        "integrityStatus",
        "timestamp",
        "readOnly",
        "linkedUhmiPanel",
        "linkedReport",
        "linkedDeliveryItem",
        "guardrailStatus",
    }
    if required_fields - fields:
        fail("evidenceObjectModel fields incomplete")
    for record in registry.get("evidenceRecords", []):
        if required_fields - set(record):
            fail(f"evidence record fields incomplete: {record.get('evidenceId')}")
        if record.get("readOnly") is not True:
            fail(f"evidence record must be readOnly: {record.get('evidenceId')}")
    ok("evidence object model and records are complete and read-only")

    combined_docs = "\n".join(read(path) for path in DOCS + EVIDENCE_FILES)
    for path in (DOCS[0], DOCS[-1], REGISTRY):
        if PASS_MARKER not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    for phrase in DOC_PHRASES:
        if phrase not in combined_docs:
            fail(f"required phrase missing: {phrase}")
    ok("PASS marker and required phrases exist in docs/evidence")

    scan_text = "\n".join(read(path) for path in DOCS + EVIDENCE_FILES + [REGISTRY] + BACKEND_FILES if path.exists())
    lower_scan = scan_text.lower()
    for phrase in FORBIDDEN_ACTIVE_PHRASES:
        if phrase.lower() in lower_scan:
            fail(f"forbidden active phrase found: {phrase}")
    ok("forbidden active design/action phrases are absent")

    backend_text = "\n".join(read(path) for path in BACKEND_FILES)
    for token in (
        "UCDE_GA_R4",
        "read_only",
        "evidenceWrite",
        "dbWrite",
        "runtimeActivation",
        "deviceControl",
        "edgeCommandExecution",
        "linkCommandExecution",
    ):
        if token not in backend_text:
            fail(f"backend token missing: {token}")
    for method in ('methods=["POST"]', 'methods=["PUT"]', 'methods=["PATCH"]', 'methods=["DELETE"]'):
        if method in backend_text:
            fail(f"backend UCDE R4 must stay GET-only: {method}")
    for route in (
        "/one/ucde/evidence-center",
        "/one/ucde/evidence-catalog",
        "/one/ucde/evidence-records",
        "/one/ucde/evidence-links",
        "/one/ucde/uhmi-linkage",
        "/one/ucde/customer-preview",
        "/one/ucde/guardrails",
    ):
        if route not in backend_text:
            fail(f"backend R4 route missing: {route}")
    ok("backend R4 API/provider is GET-only and read-only")

    frontend_text = "\n".join(read(path) for path in FRONTEND_FILES if path.exists())
    if "UCDE Evidence Center" not in frontend_text:
        fail("frontend UCDE Evidence Center reference missing")
    ok("frontend UCDE/UHMI references remain present")

    proc = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stdout)
        fail("git status --short failed")
    for line in proc.stdout.splitlines():
        path = line[3:] if len(line) > 3 else line
        if any(marker in path for marker in FORBIDDEN_ARTIFACT_MARKERS):
            fail(f"forbidden artifact in git status: {path}")
    ok("forbidden artifact scan is empty for git status")

    run_validator(
        "scripts/validation/validate-one-package-route-enforcement.py",
        "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS",
    )
    run_validator("scripts/validation/validate-one-boundaries.py", "ONE_BOUNDARY_BASELINE_PASS")

    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
