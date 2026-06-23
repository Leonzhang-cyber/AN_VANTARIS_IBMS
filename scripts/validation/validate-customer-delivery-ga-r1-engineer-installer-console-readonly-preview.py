#!/usr/bin/env python3
"""Validate Customer Delivery GA R1 Engineer Installer Console read-only preview."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "CUSTOMER_DELIVERY_GA_R1_ENGINEER_INSTALLER_CONSOLE_READONLY_PREVIEW_PASS"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/customer-delivery-ga-r1/customer-delivery-ga-r1-engineer-installer-console-readonly-preview.v1.json"

DOCS = [
    ROOT / "CUSTOMER_DELIVERY_GA_R1_ENGINEER_INSTALLER_CONSOLE_READONLY_PREVIEW.md",
    ROOT / "CUSTOMER_DELIVERY_GA_R1_SERVER_PLAN_AND_OFFLINE_HANDOFF.md",
    ROOT / "CUSTOMER_DELIVERY_GA_R1_PACKAGE_READINESS_AND_DIAGNOSTICS_PREVIEW.md",
    ROOT / "CUSTOMER_DELIVERY_GA_R1_CUSTOMER_ACCEPTANCE_CHECKLIST.md",
    ROOT / "CUSTOMER_DELIVERY_GA_R1_REPORT.md",
]

EVIDENCE_FILES = [
    ROOT / "AN_VANTARIS_ONE/registries/customer-delivery-ga-r1/customer-delivery-r1-server-plan.txt",
    ROOT / "AN_VANTARIS_ONE/registries/customer-delivery-ga-r1/customer-delivery-r1-package-readiness.txt",
    ROOT / "AN_VANTARIS_ONE/registries/customer-delivery-ga-r1/customer-delivery-r1-offline-handoff.txt",
    ROOT / "AN_VANTARIS_ONE/registries/customer-delivery-ga-r1/customer-delivery-r1-acceptance-checklist.txt",
    ROOT / "AN_VANTARIS_ONE/registries/customer-delivery-ga-r1/customer-delivery-r1-validator-results.txt",
]

BACKEND_FILES = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/customer_delivery/readonly_preview_provider.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/customer_delivery/customer_delivery_api.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/engineer_installer/engineer_installer_api.py",
]

PACKAGE_NAMES = [
    "UConsole",
    "UHMI",
    "UCDE",
    "Customer Delivery",
    "EDGE Foundation",
    "VANTARIS Link",
    "DB Foundation",
    "Contracts",
    "Reports",
    "Governance & Security",
]

DOC_PHRASES = [
    "Engineer Installer Console",
    "Customer Delivery Preview",
    "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
    "192.168.60.21",
    "192.168.60.22",
    "No SSH",
    "No Install",
    "No Rollback",
    "No DB Migration",
    "No DB Write",
    "No Runtime Activation",
    "No Direct Device Control",
    "No EDGE Command Execution",
    "No LINK Command Execution",
    "No auth / login / JWT / RBAC mutation",
    "No Production Activation",
    "No runnable production package",
    "No dist/build committed",
]

FORBIDDEN_ACTIVE_PHRASES = [
    "ssh executed",
    "deployed to 192.168.60.21",
    "deployed to 192.168.60.22",
    "install enabled",
    "rollback enabled",
    "db migration enabled",
    "db write enabled",
    "runtime activation enabled",
    "direct control enabled",
    "edge command enabled",
    "link command enabled",
    "rbac mutation enabled",
    "permission write enabled",
    "production activation enabled",
    "runnable package generated",
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


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(read(path))
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


def active_phrase_present(text: str, phrase: str) -> bool:
    lower_text = text.lower()
    lower_phrase = phrase.lower()
    start = 0
    while True:
        index = lower_text.find(lower_phrase, start)
        if index == -1:
            return False
        prefix = lower_text[max(0, index - 32):index]
        if any(token in prefix for token in ("no ", "not ", "not_", "non-", "without ")):
            start = index + len(lower_phrase)
            continue
        return True


def main() -> int:
    for path in DOCS + EVIDENCE_FILES + [REGISTRY] + BACKEND_FILES:
        if not path.exists():
            fail(f"required file exists: {path.relative_to(ROOT)}")
    ok("required docs, evidence files, registry, and backend preview files exist")

    registry = load_json(REGISTRY)
    ok("registry JSON parses")

    expected = {
        "scope": "CUSTOMER_DELIVERY_GA_R1",
        "taskId": "CUSTOMER-DELIVERY-GA-R1",
        "mode": "read_only",
        "visualStyle": "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "validationPassMarker": PASS_MARKER,
    }
    for key, value in expected.items():
        if registry.get(key) != value:
            fail(f"registry {key} must be {value}")
    if registry.get("engineerInstallerConsolePreview") is not True:
        fail("registry engineerInstallerConsolePreview must be true")
    if registry.get("customerDeliveryPreview") is not True:
        fail("registry customerDeliveryPreview must be true")
    ok("registry core fields are correct")

    plan = registry.get("serverPlanning", {})
    plan_expected = {
        "appNonDbTarget": "192.168.60.21",
        "dbOnlyTarget": "192.168.60.22",
        "sshExecuted": False,
        "deploymentExecuted": False,
        "installExecuted": False,
        "rollbackExecuted": False,
        "dbMigrationExecuted": False,
        "dbWrite": False,
        "productionActivationExecuted": False,
    }
    for key, value in plan_expected.items():
        if plan.get(key) != value:
            fail(f"serverPlanning.{key} must be {value}")
    ok("serverPlanning records targets and non-execution flags")

    uhmi_text = json.dumps(registry.get("relatedUhmiArchive", {}), sort_keys=True)
    for token in (
        "UHMI-GA-R6",
        "867b3d09a2cfc826dc2e1558b1dd3afb23dc77a8",
        "uhmi-ga-r6-customer-preview-final-archive-freeze-20260622",
    ):
        if token not in uhmi_text:
            fail(f"relatedUhmiArchive missing {token}")
    ucde_text = json.dumps(registry.get("relatedUcdeArchive", {}), sort_keys=True)
    for token in (
        "UCDE-GA-R6",
        "442657ac60a267d827fa02c8494e445529345e92",
        "ucde-ga-r6-evidence-center-final-archive-freeze-20260622",
    ):
        if token not in ucde_text:
            fail(f"relatedUcdeArchive missing {token}")
    ok("related UHMI and UCDE archives are recorded")

    readiness = registry.get("packageReadiness", [])
    readiness_names = {item.get("packageName") for item in readiness if isinstance(item, dict)}
    for name in PACKAGE_NAMES:
        if name not in readiness_names:
            fail(f"packageReadiness missing {name}")
    for item in readiness:
        for field in (
            "packageId",
            "packageName",
            "packageRole",
            "targetServer",
            "readinessStatus",
            "customerVisible",
            "engineerVisible",
            "installActionState",
            "verificationState",
            "rollbackState",
            "guardrailStatus",
            "readOnly",
        ):
            if field not in item:
                fail(f"packageReadiness item missing {field}: {item}")
        if item.get("readOnly") is not True:
            fail(f"packageReadiness item must be readOnly: {item.get('packageName')}")
    ok("packageReadiness includes all required package entries and fields")

    combined_docs = "\n".join(read(path) for path in DOCS + EVIDENCE_FILES + [REGISTRY])
    for path in DOCS + [REGISTRY]:
        if PASS_MARKER not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    for phrase in DOC_PHRASES:
        if phrase not in combined_docs:
            fail(f"required doc phrase missing: {phrase}")
    ok("docs contain required preview, planning, and guardrail phrases")

    backend_text = "\n".join(read(path) for path in BACKEND_FILES)
    for token in (
        "CUSTOMER_DELIVERY_GA_R1",
        "read_only",
        "appNonDbTarget",
        "192.168.60.21",
        "dbOnlyTarget",
        "192.168.60.22",
        "sshExecuted",
        "deploymentExecuted",
        "installExecuted",
        "dbMigrationExecuted",
        "runtimeActivation",
    ):
        if token not in backend_text:
            fail(f"backend preview token missing: {token}")
    for method in ('methods=["POST"]', 'methods=["PUT"]', 'methods=["PATCH"]', 'methods=["DELETE"]'):
        if method in backend_text:
            fail(f"backend preview API must remain GET-only: {method}")
    ok("backend Customer Delivery / Engineer Installer preview files are GET-only and read-only")

    forbidden = registry.get("forbiddenActions", {})
    for key in (
        "sshExecution",
        "deploymentToAppServer",
        "deploymentToDbServer",
        "install",
        "uninstall",
        "rollback",
        "dbMigration",
        "dbWrite",
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
        value = forbidden.get(key)
        if value not in (False, "NOT_EXECUTED"):
            fail(f"forbiddenActions.{key} must be false or NOT_EXECUTED")
    ok("forbiddenActions are false or NOT_EXECUTED")

    scan_text = "\n".join([combined_docs, backend_text])
    for phrase in FORBIDDEN_ACTIVE_PHRASES:
        if active_phrase_present(scan_text, phrase):
            fail(f"forbidden active phrase found: {phrase}")
    ok("forbidden active production/runtime/install/control phrases are absent")

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
