#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "UHMI_GA_R3_CUSTOMER_PREVIEW_PACKAGE_PASS"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r3/uhmi-ga-r3-customer-preview-package.v1.json"
DOCS = [
    ROOT / "UHMI_GA_R3_CUSTOMER_PREVIEW_PACKAGE_GUIDE.md",
    ROOT / "UHMI_GA_R3_DEMO_READY_WORKSPACE_FLOW.md",
    ROOT / "UHMI_GA_R3_CUSTOMER_PREVIEW_ACCEPTANCE_CHECKLIST.md",
    ROOT / "UHMI_GA_R3_ENGINEER_DEMO_CHECKLIST.md",
    ROOT / "UHMI_GA_R3_REPORT.md",
]
EVIDENCE = [
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r3/uhmi-r3-release-chain.txt",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r3/uhmi-r3-demo-flow.txt",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r3/uhmi-r3-preview-checklist.txt",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r3/uhmi-r3-validator-results.txt",
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
            fail(f"missing required R3 file: {path.relative_to(ROOT)}")
    ok("required R3 documents, evidence files, and registry exist")

    registry = load_json(REGISTRY)
    ok("R3 registry JSON parses")

    expected_registry = {
        "scope": "UHMI_GA_R3",
        "mode": "read_only",
        "visualStyle": "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "baseline": "UHMI-GA-R2F",
        "productionActivation": "NOT_EXECUTED",
        "validationPassMarker": PASS_MARKER,
    }
    for key, value in expected_registry.items():
        if registry.get(key) != value:
            fail(f"registry.{key} must equal {value}")
    for key in ["customerPreviewPackage", "demoReadyReadOnlyWorkspace"]:
        if registry.get(key) is not True:
            fail(f"registry.{key} must be true")
    ok("R3 registry core fields are correct")

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
    ok("releaseChain includes R1-R2F with correct commits, tags, scopes, status, and PASS markers")

    for stage, expected in EXPECTED_CHAIN.items():
        registry_path = expected.get("registry")
        if registry_path:
            path = ROOT / registry_path
            if not path.exists():
                fail(f"missing required prior registry for {stage}: {registry_path}")
            if expected["marker"] not in read(path):
                fail(f"prior registry missing PASS marker for {stage}: {expected['marker']}")
    ok("required prior registries and PASS markers exist")

    required_demo_steps = [
        "Open UConsole",
        "Open UHMI Workspace",
        "Show VANTARIS_LIGHT_OPERATIONS_CONSOLE visual style",
        "Show Overview metric cards",
        "Show System Context Panels",
        "Show Device Context Table",
        "Show Mimic Panel Preview",
        "Show Event Context",
        "Show Evidence Context",
        "Show Role-based views",
        "Show Customer view",
        "Show Engineer view",
        "Show Admin view",
        "Show Operator view",
        "Show Disabled Actions",
        "Show Guardrails",
        "Show Future Control Path",
        "Show R2F Evidence Pack / Release Index",
    ]
    for step in required_demo_steps:
        if step not in registry.get("demoFlow", []):
            fail(f"registry.demoFlow missing step: {step}")
    for role in ["Customer", "Engineer", "Admin", "Operator"]:
        if role not in registry.get("roleDemoViews", []):
            fail(f"registry.roleDemoViews missing role: {role}")
    ok("R3 demo flow and role demo views are registered")

    combined_docs = "\n".join(read(path) for path in DOCS)
    for doc in DOCS:
        if PASS_MARKER not in read(doc):
            fail(f"R3 PASS marker missing from {doc.relative_to(ROOT)}")
    required_doc_phrases = [
        "Customer Preview Package",
        "Demo-ready Read-only Workspace",
        "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "NOT EXECUTED",
        "No Direct Device Control",
        "No Runtime Activation",
        "No DB Write",
        "No EDGE Command Execution",
        "No LINK Command Execution",
        "No auth / login / JWT / RBAC mutation",
        "Production Activation Not Executed",
        "UHMI is not HMI Server",
        "UHMI is not SCADA replacement",
    ]
    for phrase in required_doc_phrases:
        if phrase not in combined_docs:
            fail(f"required R3 doc phrase missing: {phrase}")
    ok("R3 docs contain required customer preview, demo, style, and boundary phrases")

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
    for phrase in ["scada replacement", "hmi server"]:
        if phrase in active_text:
            allowed_not_phrase = f"not {phrase}"
            if allowed_not_phrase not in active_text:
                fail(f"forbidden active design phrase found without negation: {phrase}")
    ok("forbidden active design/capability phrases are absent")

    for path in [*DOCS, *EVIDENCE, REGISTRY, ROOT / "scripts/validation/validate-uhmi-ga-r3-customer-preview-package.py"]:
        relative = path.relative_to(ROOT).as_posix()
        for token in [".env", "node_modules", "dist", "build", ".runtime", "secrets"]:
            if token in relative:
                fail(f"forbidden artifact path in R3 files: {relative}")
    ok("no forbidden artifact roots or files were added by R3")

    print(PASS_MARKER)


if __name__ == "__main__":
    main()
