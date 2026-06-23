#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "UHMI_GA_R4_CUSTOMER_PREVIEW_EXPORT_PACKAGE_PASS"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r4/uhmi-ga-r4-customer-preview-export-package.v1.json"
DOCS = [
    ROOT / "UHMI_GA_R4_CUSTOMER_PREVIEW_EXPORT_PACKAGE_INDEX.md",
    ROOT / "UHMI_GA_R4_OFFLINE_DEMO_HANDOFF_GUIDE.md",
    ROOT / "UHMI_GA_R4_ENGINEER_DEMO_RUNBOOK.md",
    ROOT / "UHMI_GA_R4_CUSTOMER_DEMO_ACCEPTANCE_HANDOVER.md",
    ROOT / "UHMI_GA_R4_EXPORT_SCOPE_AND_EXCLUSION_MATRIX.md",
    ROOT / "UHMI_GA_R4_REPORT.md",
]
EVIDENCE = [
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r4/uhmi-r4-export-manifest.txt",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r4/uhmi-r4-release-chain.txt",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r4/uhmi-r4-handoff-files.txt",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r4/uhmi-r4-validator-results.txt",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r4/uhmi-r4-exclusion-evidence.txt",
]

EXPECTED_CHAIN = {
    "UHMI-GA-R1": {
        "commit": "003f4f710cfd76130ff79275c8190ec6bbe7edc9",
        "tag": "uhmi-ga-r1-uconsole-readonly-workspace-freeze-20260622",
        "marker": "UHMI_GA_R1_UCONSOLE_UHMI_WORKSPACE_READONLY_FOUNDATION_FREEZE_PASS",
    },
    "UHMI-GA-R2A": {
        "commit": "6d682fdd351e3ad51b27ce91f2dbf92c74da3323",
        "tag": "uhmi-ga-r2a-full-uconsole-menu-ui-api-skeleton-freeze-20260622",
        "marker": "UHMI_GA_R2A_FULL_UCONSOLE_MENU_IA_UI_API_SKELETON_PASS",
        "registry": "AN_VANTARIS_ONE/registries/uhmi-ga-r2a/uhmi-ga-r2a-uconsole-menu-ia-ui-api-skeleton.v1.json",
    },
    "UHMI-GA-R2B": {
        "commit": "3678150d55f2459def6fc7b423496acb62143ac4",
        "tag": "uhmi-ga-r2b-workspace-panels-system-context-freeze-20260622",
        "marker": "UHMI_GA_R2B_WORKSPACE_PANELS_SYSTEM_CONTEXT_PASS",
        "registry": "AN_VANTARIS_ONE/registries/uhmi-ga-r2b/uhmi-ga-r2b-workspace-panels-system-context.v1.json",
    },
    "UHMI-GA-R2C": {
        "commit": "0262d90efffbb4993215d44c35f7c4d26f6d762f",
        "tag": "uhmi-ga-r2c-role-based-workspace-views-freeze-20260622",
        "marker": "UHMI_GA_R2C_ROLE_BASED_WORKSPACE_VIEWS_PASS",
        "registry": "AN_VANTARIS_ONE/registries/uhmi-ga-r2c/uhmi-ga-r2c-role-based-workspace-views.v1.json",
    },
    "UHMI-GA-R2D": {
        "commit": "e6c94cefcc7aee336d4702bc377a554a549454eb",
        "tag": "uhmi-ga-r2d-light-console-style-freeze-20260622",
        "marker": "UHMI_GA_R2D_WORKSPACE_VISUAL_POLISH_LIGHT_CONSOLE_STYLE_PASS",
        "registry": "AN_VANTARIS_ONE/registries/uhmi-ga-r2d/uhmi-ga-r2d-workspace-visual-polish-light-console-style.v1.json",
    },
    "UHMI-GA-R2E": {
        "commit": "6bd6bbaa0e23eee6676e170d2493d093084216a5",
        "tag": "uhmi-ga-r2e-api-frontend-integration-audit-freeze-20260622",
        "marker": "UHMI_GA_R2E_WORKSPACE_API_CONSOLIDATION_FRONTEND_INTEGRATION_AUDIT_PASS",
        "registry": "AN_VANTARIS_ONE/registries/uhmi-ga-r2e/uhmi-ga-r2e-workspace-api-consolidation-frontend-integration-audit.v1.json",
    },
    "UHMI-GA-R2F": {
        "commit": "b9e74f09394dee25d3a3b09da729f034431d3cf2",
        "tag": "uhmi-ga-r2f-final-readonly-workspace-release-index-freeze-20260622",
        "marker": "UHMI_GA_R2F_FINAL_READONLY_WORKSPACE_RELEASE_INDEX_PASS",
        "registry": "AN_VANTARIS_ONE/registries/uhmi-ga-r2f/uhmi-ga-r2f-final-readonly-workspace-release-index.v1.json",
    },
    "UHMI-GA-R3": {
        "commit": "1181339555067af75cc492cc12cf83fb433bc1a7",
        "tag": "uhmi-ga-r3-customer-preview-package-freeze-20260622",
        "marker": "UHMI_GA_R3_CUSTOMER_PREVIEW_PACKAGE_PASS",
        "registry": "AN_VANTARIS_ONE/registries/uhmi-ga-r3/uhmi-ga-r3-customer-preview-package.v1.json",
    },
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
            fail(f"missing required R4 file: {path.relative_to(ROOT)}")
    ok("required R4 documents, evidence files, and registry exist")

    registry = load_json(REGISTRY)
    ok("R4 registry JSON parses")

    expected_registry = {
        "scope": "UHMI_GA_R4",
        "mode": "read_only",
        "visualStyle": "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "baseline": "UHMI-GA-R3",
        "exportPackageType": "MANIFEST_EVIDENCE_RUNBOOK_ONLY",
        "productionActivation": "NOT_EXECUTED",
        "validationPassMarker": PASS_MARKER,
    }
    for key, value in expected_registry.items():
        if registry.get(key) != value:
            fail(f"registry.{key} must equal {value}")
    for key in ["customerPreviewExportPackage", "offlineDemoHandoff"]:
        if registry.get(key) is not True:
            fail(f"registry.{key} must be true")
    if registry.get("runnablePackageGenerated") is not False:
        fail("registry.runnablePackageGenerated must be false")
    ok("R4 registry core fields are correct")

    chain = registry.get("releaseChain")
    if not isinstance(chain, list):
        fail("registry.releaseChain must be a list")
    chain_by_stage = {item.get("stage"): item for item in chain if isinstance(item, dict)}
    for stage, expected in EXPECTED_CHAIN.items():
        item = chain_by_stage.get(stage)
        if not item:
            fail(f"releaseChain missing stage: {stage}")
        if item.get("commit") != expected["commit"]:
            fail(f"{stage} commit mismatch")
        if item.get("tag") != expected["tag"]:
            fail(f"{stage} tag mismatch")
        if item.get("passMarker") != expected["marker"]:
            fail(f"{stage} PASS marker mismatch")
        if item.get("status") != "PASS":
            fail(f"{stage} status must be PASS")
    ok("releaseChain includes R1-R3 with correct commits, tags, scopes, status, and PASS markers")

    for stage, expected in EXPECTED_CHAIN.items():
        registry_path = expected.get("registry")
        if registry_path:
            path = ROOT / registry_path
            if not path.exists():
                fail(f"missing required prior registry for {stage}: {registry_path}")
            if expected["marker"] not in read(path):
                fail(f"prior registry missing PASS marker for {stage}: {expected['marker']}")
    ok("required prior registries and PASS markers exist")

    combined_docs = "\n".join(read(path) for path in DOCS)
    for doc in DOCS:
        if PASS_MARKER not in read(doc):
            fail(f"R4 PASS marker missing from {doc.relative_to(ROOT)}")
    required_doc_phrases = [
        "Customer Preview Export Package",
        "Offline Demo Hand-off",
        "MANIFEST_EVIDENCE_RUNBOOK_ONLY",
        "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "NOT EXECUTED",
        "No Direct Device Control",
        "No Runtime Activation",
        "No DB Write",
        "No EDGE Command Execution",
        "No LINK Command Execution",
        "No auth / login / JWT / RBAC mutation",
        "No runnable production package generated",
        "No dist/build committed",
        "No .env/secrets committed",
        "UHMI is not HMI Server",
        "UHMI is not SCADA replacement",
    ]
    for phrase in required_doc_phrases:
        if phrase not in combined_docs:
            fail(f"required R4 doc phrase missing: {phrase}")
    ok("R4 docs contain required export, handoff, exclusion, style, and boundary phrases")

    forbidden_actions = registry.get("forbiddenActions")
    if not isinstance(forbidden_actions, dict):
        fail("registry.forbiddenActions must be an object")
    for key in [
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
    ]:
        if forbidden_actions.get(key) not in (False, "NOT_EXECUTED"):
            fail(f"forbiddenActions.{key} must be false or NOT_EXECUTED")
    ok("forbiddenActions are false or NOT_EXECUTED")

    if registry.get("futureControlPath") != "UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device":
        fail("futureControlPath mismatch")
    ok("future control path is recorded")

    active_text = "\n".join(read(path) for path in [*DOCS, *EVIDENCE, REGISTRY]).lower()
    forbidden_positive = [
        "ufms deep blue theme",
        "深蓝色主题",
        "dark scada dashboard",
        "industrial dark control room",
        "high-saturation dark console",
        "direct control enabled",
        "runtime activation enabled",
        "db write enabled",
        "edge command enabled",
        "link command enabled",
        "rbac mutation enabled",
        "permission write enabled",
        "package state mutation enabled",
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

    for path in [*DOCS, *EVIDENCE, REGISTRY, ROOT / "scripts/validation/validate-uhmi-ga-r4-customer-preview-export-package.py"]:
        relative = path.relative_to(ROOT).as_posix()
        for token in [".env", "node_modules", "dist", "build", ".runtime", "secrets", "tar.gz", "zip"]:
            if token in relative:
                fail(f"forbidden artifact path in R4 files: {relative}")
    ok("no forbidden artifact roots, archives, or files were added by R4")

    print(PASS_MARKER)


if __name__ == "__main__":
    main()
