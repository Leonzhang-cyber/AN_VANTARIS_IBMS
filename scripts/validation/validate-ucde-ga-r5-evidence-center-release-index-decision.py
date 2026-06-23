#!/usr/bin/env python3
"""Validate UCDE-GA-R5 Evidence Center release index and decision freeze."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "UCDE_GA_R5_EVIDENCE_CENTER_RELEASE_INDEX_DECISION_PASS"

DOCS = [
    ROOT / "UCDE_GA_R5_EVIDENCE_CENTER_RELEASE_INDEX.md",
    ROOT / "UCDE_GA_R5_CUSTOMER_PREVIEW_READINESS_MATRIX.md",
    ROOT / "UCDE_GA_R5_RELEASE_DECISION.md",
    ROOT / "UCDE_GA_R5_RISK_LIMITATION_EXCLUSION_MATRIX.md",
    ROOT / "UCDE_GA_R5_CUSTOMER_PREVIEW_SIGNOFF_PACK.md",
    ROOT / "UCDE_GA_R5_DEPLOYMENT_PLANNING_NOTE.md",
    ROOT / "UCDE_GA_R5_REPORT.md",
]

REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/ucde-ga-r5/ucde-ga-r5-evidence-center-release-index-decision.v1.json"

EVIDENCE_FILES = [
    ROOT / "AN_VANTARIS_ONE/registries/ucde-ga-r5/ucde-r5-release-index.txt",
    ROOT / "AN_VANTARIS_ONE/registries/ucde-ga-r5/ucde-r5-readiness-matrix.txt",
    ROOT / "AN_VANTARIS_ONE/registries/ucde-ga-r5/ucde-r5-release-decision.txt",
    ROOT / "AN_VANTARIS_ONE/registries/ucde-ga-r5/ucde-r5-risk-exclusion-evidence.txt",
    ROOT / "AN_VANTARIS_ONE/registries/ucde-ga-r5/ucde-r5-deployment-planning.txt",
    ROOT / "AN_VANTARIS_ONE/registries/ucde-ga-r5/ucde-r5-validator-results.txt",
]

PRIOR_REGISTRIES = [
    ROOT / "AN_VANTARIS_ONE/registries/ucde-ga-r4/ucde-ga-r4-evidence-center-customer-preview.v1.json",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2a/uhmi-ga-r2a-uconsole-menu-ia-ui-api-skeleton.v1.json",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2b/uhmi-ga-r2b-workspace-panels-system-context.v1.json",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2c/uhmi-ga-r2c-role-based-workspace-views.v1.json",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2d/uhmi-ga-r2d-workspace-visual-polish-light-console-style.v1.json",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2e/uhmi-ga-r2e-workspace-api-consolidation-frontend-integration-audit.v1.json",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2f/uhmi-ga-r2f-final-readonly-workspace-release-index.v1.json",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r3/uhmi-ga-r3-customer-preview-package.v1.json",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r4/uhmi-ga-r4-customer-preview-export-package.v1.json",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r5/uhmi-ga-r5-final-customer-preview-readiness-decision.v1.json",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r6/uhmi-ga-r6-customer-preview-final-archive.v1.json",
]

PRIOR_MARKERS = [
    "UCDE_GA_R4_EVIDENCE_CENTER_CUSTOMER_PREVIEW_PASS",
    "UHMI_GA_R1_UCONSOLE_UHMI_WORKSPACE_READONLY_FOUNDATION_FREEZE_PASS",
    "UHMI_GA_R2A_FULL_UCONSOLE_MENU_IA_UI_API_SKELETON_PASS",
    "UHMI_GA_R2B_WORKSPACE_PANELS_SYSTEM_CONTEXT_PASS",
    "UHMI_GA_R2C_ROLE_BASED_WORKSPACE_VIEWS_PASS",
    "UHMI_GA_R2D_WORKSPACE_VISUAL_POLISH_LIGHT_CONSOLE_STYLE_PASS",
    "UHMI_GA_R2E_WORKSPACE_API_CONSOLIDATION_FRONTEND_INTEGRATION_AUDIT_PASS",
    "UHMI_GA_R2F_FINAL_READONLY_WORKSPACE_RELEASE_INDEX_PASS",
    "UHMI_GA_R3_CUSTOMER_PREVIEW_PACKAGE_PASS",
    "UHMI_GA_R4_CUSTOMER_PREVIEW_EXPORT_PACKAGE_PASS",
    "UHMI_GA_R5_FINAL_CUSTOMER_PREVIEW_READINESS_DECISION_PASS",
    "UHMI_GA_R6_CUSTOMER_PREVIEW_FINAL_ARCHIVE_PASS",
]

UHMI_STAGES = [
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

DOC_PHRASES = [
    "Evidence Center Release Index",
    "Customer Preview Readiness Matrix",
    "Release Decision",
    "GO",
    "READ_ONLY_EVIDENCE_CENTER_CUSTOMER_PREVIEW",
    "Production GA: NOT_YET",
    "Evidence DB: NOT_CREATED",
    "Evidence Write: NOT_EXECUTED",
    "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
    "192.168.60.21",
    "192.168.60.22",
    "No deployment executed",
    "No SSH executed",
    "No DB migration executed",
    "No DB Write",
    "No Evidence Write",
    "No Runtime Activation",
    "No Direct Device Control",
    "No EDGE Command Execution",
    "No LINK Command Execution",
    "No auth / login / JWT / RBAC mutation",
    "No runnable production package",
    "No dist/build committed",
]

FORBIDDEN_ACTIVE_PHRASES = [
    "evidence db created",
    "evidence write enabled",
    "db write enabled",
    "runtime activation enabled",
    "direct control enabled",
    "edge command enabled",
    "link command enabled",
    "rbac mutation enabled",
    "permission write enabled",
    "production activation enabled",
    "runnable package generated",
    "ssh executed",
    "deployed to 192.168.60.21",
    "deployed to 192.168.60.22",
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


def git_grep(marker: str) -> bool:
    proc = subprocess.run(
        ["git", "grep", "-n", marker, "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return proc.returncode == 0 and marker in proc.stdout


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
        prefix = lower_text[max(0, index - 24):index]
        if any(token in prefix for token in ("no ", "not ", "not_", "non-", "without ")):
            start = index + len(lower_phrase)
            continue
        return True


def main() -> int:
    for path in DOCS + EVIDENCE_FILES + [REGISTRY]:
        if not path.exists():
            fail(f"required R5 file exists: {path.relative_to(ROOT)}")
    ok("all required R5 documents, evidence files, and registry exist")

    registry = load_json(REGISTRY)
    ok("R5 registry JSON parses")

    expected_values = {
        "scope": "UCDE_GA_R5",
        "taskId": "UCDE-GA-R5",
        "mode": "read_only",
        "visualStyle": "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "baseline": "UCDE-GA-R4",
        "releaseDecision": "GO",
        "releaseDecisionScope": "READ_ONLY_EVIDENCE_CENTER_CUSTOMER_PREVIEW",
        "productionGaDecision": "NOT_YET",
        "productionActivation": "NOT_EXECUTED",
        "evidenceDb": "NOT_CREATED",
        "evidenceWrite": "NOT_EXECUTED",
        "validationPassMarker": PASS_MARKER,
    }
    for key, value in expected_values.items():
        if registry.get(key) != value:
            fail(f"registry {key} must be {value}")
    if registry.get("evidenceCenterReleaseIndex") is not True:
        fail("registry evidenceCenterReleaseIndex must be true")
    if registry.get("customerPreviewReadinessMatrix") is not True:
        fail("registry customerPreviewReadinessMatrix must be true")
    ok("registry core fields, GO decision, and production exclusions are correct")

    deployment = registry.get("deploymentPlanning", {})
    deployment_expected = {
        "appNonDbTarget": "192.168.60.21",
        "dbOnlyTarget": "192.168.60.22",
        "deploymentExecuted": False,
        "sshExecuted": False,
        "dbMigrationExecuted": False,
        "productionActivationExecuted": False,
    }
    for key, value in deployment_expected.items():
        if deployment.get(key) != value:
            fail(f"deploymentPlanning.{key} must be {value}")
    ok("deployment planning targets are recorded and non-executed")

    ucde_chain_text = json.dumps(registry.get("relatedUcdeReleaseChain", []), sort_keys=True)
    for token in (
        "UCDE-GA-R4",
        "a8e71123f33c22da6e94c658c625f34db50625d4",
        "ucde-ga-r4-evidence-center-customer-preview-freeze-20260622",
    ):
        if token not in ucde_chain_text:
            fail(f"relatedUcdeReleaseChain missing {token}")
    ok("related UCDE release chain includes UCDE-GA-R4 commit and tag")

    uhmi_chain_text = json.dumps(registry.get("relatedUhmiReleaseChain", []), sort_keys=True)
    for stage in UHMI_STAGES:
        if stage not in uhmi_chain_text:
            fail(f"relatedUhmiReleaseChain missing {stage}")
    ok("related UHMI release chain includes R1-R6")

    for path in PRIOR_REGISTRIES:
        if not path.exists():
            fail(f"required prior registry missing: {path.relative_to(ROOT)}")
    ok("required prior registries exist")

    for marker in PRIOR_MARKERS:
        if not git_grep(marker):
            fail(f"required prior PASS marker missing from HEAD: {marker}")
    ok("required prior PASS markers exist")

    combined_text = "\n".join(read(path) for path in DOCS + EVIDENCE_FILES + [REGISTRY])
    for path in DOCS + [REGISTRY]:
        if PASS_MARKER not in read(path):
            fail(f"R5 PASS marker missing from {path.relative_to(ROOT)}")
    for phrase in DOC_PHRASES:
        if phrase not in combined_text:
            fail(f"required R5 phrase missing: {phrase}")
    ok("R5 docs contain required decision, planning, and exclusion phrases")

    forbidden = registry.get("forbiddenActions", {})
    for key in (
        "evidenceDbCreation",
        "evidenceWrite",
        "install",
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
        "sshExecution",
    ):
        value = forbidden.get(key)
        if value not in (False, "NOT_EXECUTED"):
            fail(f"forbiddenActions.{key} must be false or NOT_EXECUTED")
    ok("forbiddenActions are false or NOT_EXECUTED")

    for phrase in FORBIDDEN_ACTIVE_PHRASES:
        if active_phrase_present(combined_text, phrase):
            fail(f"forbidden active phrase found: {phrase}")
    ok("forbidden active production/runtime/control phrases are absent")

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
