#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "UHMI_GA_R6_CUSTOMER_PREVIEW_FINAL_ARCHIVE_PASS"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r6/uhmi-ga-r6-customer-preview-final-archive.v1.json"
DOCS = [
    ROOT / "UHMI_GA_R6_CUSTOMER_PREVIEW_FINAL_ARCHIVE_SUMMARY.md",
    ROOT / "UHMI_GA_R6_BRANCH_CLOSURE_SUMMARY.md",
    ROOT / "UHMI_GA_R6_FINAL_RELEASE_CHAIN_INDEX.md",
    ROOT / "UHMI_GA_R6_FINAL_EVIDENCE_INDEX.md",
    ROOT / "UHMI_GA_R6_NEXT_PHASE_RECOMMENDATION.md",
    ROOT / "UHMI_GA_R6_REPORT.md",
]
EVIDENCE = [
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r6/uhmi-r6-final-release-chain.txt",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r6/uhmi-r6-final-evidence-index.txt",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r6/uhmi-r6-branch-closure.txt",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r6/uhmi-r6-next-phase-recommendation.txt",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r6/uhmi-r6-validator-results.txt",
]

EXPECTED_CHAIN = {
    "UHMI-GA-R1": ("003f4f710cfd76130ff79275c8190ec6bbe7edc9", "uhmi-ga-r1-uconsole-readonly-workspace-freeze-20260622", "UHMI_GA_R1_UCONSOLE_UHMI_WORKSPACE_READONLY_FOUNDATION_FREEZE_PASS", None),
    "UHMI-GA-R2A": ("6d682fdd351e3ad51b27ce91f2dbf92c74da3323", "uhmi-ga-r2a-full-uconsole-menu-ui-api-skeleton-freeze-20260622", "UHMI_GA_R2A_FULL_UCONSOLE_MENU_IA_UI_API_SKELETON_PASS", "AN_VANTARIS_ONE/registries/uhmi-ga-r2a/uhmi-ga-r2a-uconsole-menu-ia-ui-api-skeleton.v1.json"),
    "UHMI-GA-R2B": ("3678150d55f2459def6fc7b423496acb62143ac4", "uhmi-ga-r2b-workspace-panels-system-context-freeze-20260622", "UHMI_GA_R2B_WORKSPACE_PANELS_SYSTEM_CONTEXT_PASS", "AN_VANTARIS_ONE/registries/uhmi-ga-r2b/uhmi-ga-r2b-workspace-panels-system-context.v1.json"),
    "UHMI-GA-R2C": ("0262d90efffbb4993215d44c35f7c4d26f6d762f", "uhmi-ga-r2c-role-based-workspace-views-freeze-20260622", "UHMI_GA_R2C_ROLE_BASED_WORKSPACE_VIEWS_PASS", "AN_VANTARIS_ONE/registries/uhmi-ga-r2c/uhmi-ga-r2c-role-based-workspace-views.v1.json"),
    "UHMI-GA-R2D": ("e6c94cefcc7aee336d4702bc377a554a549454eb", "uhmi-ga-r2d-light-console-style-freeze-20260622", "UHMI_GA_R2D_WORKSPACE_VISUAL_POLISH_LIGHT_CONSOLE_STYLE_PASS", "AN_VANTARIS_ONE/registries/uhmi-ga-r2d/uhmi-ga-r2d-workspace-visual-polish-light-console-style.v1.json"),
    "UHMI-GA-R2E": ("6bd6bbaa0e23eee6676e170d2493d093084216a5", "uhmi-ga-r2e-api-frontend-integration-audit-freeze-20260622", "UHMI_GA_R2E_WORKSPACE_API_CONSOLIDATION_FRONTEND_INTEGRATION_AUDIT_PASS", "AN_VANTARIS_ONE/registries/uhmi-ga-r2e/uhmi-ga-r2e-workspace-api-consolidation-frontend-integration-audit.v1.json"),
    "UHMI-GA-R2F": ("b9e74f09394dee25d3a3b09da729f034431d3cf2", "uhmi-ga-r2f-final-readonly-workspace-release-index-freeze-20260622", "UHMI_GA_R2F_FINAL_READONLY_WORKSPACE_RELEASE_INDEX_PASS", "AN_VANTARIS_ONE/registries/uhmi-ga-r2f/uhmi-ga-r2f-final-readonly-workspace-release-index.v1.json"),
    "UHMI-GA-R3": ("1181339555067af75cc492cc12cf83fb433bc1a7", "uhmi-ga-r3-customer-preview-package-freeze-20260622", "UHMI_GA_R3_CUSTOMER_PREVIEW_PACKAGE_PASS", "AN_VANTARIS_ONE/registries/uhmi-ga-r3/uhmi-ga-r3-customer-preview-package.v1.json"),
    "UHMI-GA-R4": ("138cb73906ef1026e34461bf1eb0583bb3878d9e", "uhmi-ga-r4-customer-preview-export-handoff-freeze-20260622", "UHMI_GA_R4_CUSTOMER_PREVIEW_EXPORT_PACKAGE_PASS", "AN_VANTARIS_ONE/registries/uhmi-ga-r4/uhmi-ga-r4-customer-preview-export-package.v1.json"),
    "UHMI-GA-R5": ("561106f2c91a4fd6a706843c4f5b34f27671f285", "uhmi-ga-r5-customer-preview-readiness-decision-freeze-20260622", "UHMI_GA_R5_FINAL_CUSTOMER_PREVIEW_READINESS_DECISION_PASS", "AN_VANTARIS_ONE/registries/uhmi-ga-r5/uhmi-ga-r5-final-customer-preview-readiness-decision.v1.json"),
}


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def ok(message: str) -> None:
    print(f"[PASS] {message}")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict:
    try:
        data = json.loads(read(path))
    except json.JSONDecodeError as exc:
        fail(f"registry JSON parse failed: {exc}")
    if not isinstance(data, dict):
        fail("registry must be a JSON object")
    return data


def main() -> None:
    for path in [*DOCS, *EVIDENCE, REGISTRY]:
        if not path.exists():
            fail(f"missing required R6 file: {path.relative_to(ROOT)}")
    ok("required R6 documents, evidence files, and registry exist")

    registry = load_json(REGISTRY)
    ok("R6 registry JSON parses")

    expected = {
        "scope": "UHMI_GA_R6",
        "mode": "read_only",
        "visualStyle": "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "baseline": "UHMI-GA-R5",
        "releaseDecision": "GO",
        "releaseDecisionScope": "READ_ONLY_CUSTOMER_PREVIEW_OFFLINE_DEMO_HANDOFF",
        "productionGaDecision": "NOT_YET",
        "productionActivation": "NOT_EXECUTED",
        "branchClosureStatus": "READY_FOR_ARCHIVE",
        "validationPassMarker": PASS_MARKER,
    }
    for key, value in expected.items():
        if registry.get(key) != value:
            fail(f"registry.{key} must equal {value}")
    for key in ["customerPreviewFinalArchive", "branchClosureSummary"]:
        if registry.get(key) is not True:
            fail(f"registry.{key} must be true")
    ok("R6 registry core fields are correct")

    chain = registry.get("releaseChain")
    if not isinstance(chain, list):
        fail("registry.releaseChain must be a list")
    chain_by_stage = {item.get("stage"): item for item in chain if isinstance(item, dict)}
    for stage, (commit, tag, marker, registry_path) in EXPECTED_CHAIN.items():
        item = chain_by_stage.get(stage)
        if not item:
            fail(f"releaseChain missing stage: {stage}")
        if item.get("commit") != commit:
            fail(f"{stage} commit mismatch")
        if item.get("tag") != tag:
            fail(f"{stage} tag mismatch")
        if item.get("passMarker") != marker:
            fail(f"{stage} PASS marker mismatch")
        if item.get("status") != "PASS":
            fail(f"{stage} status must be PASS")
        if registry_path:
            path = ROOT / registry_path
            if not path.exists():
                fail(f"missing required prior registry for {stage}: {registry_path}")
            if marker not in read(path):
                fail(f"prior registry missing PASS marker for {stage}: {marker}")
    ok("releaseChain includes R1-R5 with correct commits, tags, status, and PASS markers")

    combined_docs = "\n".join(read(path) for path in DOCS)
    for doc in DOCS:
        if PASS_MARKER not in read(doc):
            fail(f"R6 PASS marker missing from {doc.relative_to(ROOT)}")
    required_phrases = [
        "Customer Preview Final Archive",
        "Branch Closure Summary",
        "Final Release Chain Index",
        "Final Evidence Index",
        "GO",
        "READY_FOR_ARCHIVE",
        "READ_ONLY_CUSTOMER_PREVIEW_OFFLINE_DEMO_HANDOFF",
        "Production GA: NOT_YET",
        "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "NOT EXECUTED",
        "No Direct Device Control",
        "No Runtime Activation",
        "No DB Write",
        "No EDGE Command Execution",
        "No LINK Command Execution",
        "No auth / login / JWT / RBAC mutation",
        "No runnable production package",
        "No dist/build committed",
        "UHMI is not HMI Server",
        "UHMI is not SCADA replacement",
    ]
    for phrase in required_phrases:
        if phrase not in combined_docs:
            fail(f"required R6 doc phrase missing: {phrase}")
    ok("R6 docs contain required archive, closure, decision, and boundary phrases")

    forbidden_actions = registry.get("forbiddenActions")
    if not isinstance(forbidden_actions, dict):
        fail("registry.forbiddenActions must be an object")
    for key in [
        "install", "rollback", "dbMigration", "dbWrite", "runtimeActivation",
        "deviceControl", "edgeCommandExecution", "linkCommandExecution",
        "authMutation", "loginMutation", "jwtMutation", "rbacMutation",
        "packageStateMutation", "productionActivation", "runnablePackageGeneration",
        "distBuildCommit", "secretsExport",
    ]:
        if forbidden_actions.get(key) not in (False, "NOT_EXECUTED"):
            fail(f"forbiddenActions.{key} must be false or NOT_EXECUTED")
    ok("forbiddenActions are false or NOT_EXECUTED")

    if registry.get("futureControlPath") != "UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device":
        fail("futureControlPath mismatch")
    ok("future control path is recorded")

    active_text = "\n".join(read(path) for path in [*DOCS, *EVIDENCE, REGISTRY]).lower()
    forbidden_positive = [
        "ufms deep blue theme", "深蓝色主题", "dark scada dashboard",
        "industrial dark control room", "high-saturation dark console",
        "direct control enabled", "runtime activation enabled", "db write enabled",
        "edge command enabled", "link command enabled", "rbac mutation enabled",
        "permission write enabled", "package state mutation enabled",
        "production activation enabled",
    ]
    for phrase in forbidden_positive:
        if phrase in active_text:
            fail(f"forbidden active design/capability phrase found: {phrase}")
    if "runnable package generated" in active_text:
        if "no runnable package generated" not in active_text and "not a runnable package" not in active_text:
            fail("forbidden active design/capability phrase found: runnable package generated")
    for phrase in ["scada replacement", "hmi server"]:
        if phrase in active_text and f"not {phrase}" not in active_text:
            fail(f"forbidden active design phrase found without negation: {phrase}")
    ok("forbidden active design/capability phrases are absent")

    for path in [*DOCS, *EVIDENCE, REGISTRY, ROOT / "scripts/validation/validate-uhmi-ga-r6-customer-preview-final-archive.py"]:
        relative = path.relative_to(ROOT).as_posix()
        for token in [".env", "node_modules", "dist", "build", ".runtime", "secrets", "tar.gz", "zip"]:
            if token in relative:
                fail(f"forbidden artifact path in R6 files: {relative}")
    ok("no forbidden artifact roots, archives, or files were added by R6")

    print(PASS_MARKER)


if __name__ == "__main__":
    main()
