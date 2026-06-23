#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "UHMI_GA_R2E_WORKSPACE_API_CONSOLIDATION_FRONTEND_INTEGRATION_AUDIT_PASS"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2e/uhmi-ga-r2e-workspace-api-consolidation-frontend-integration-audit.v1.json"
DOCS = [
    ROOT / "UHMI_GA_R2E_WORKSPACE_API_CONSOLIDATION_FRONTEND_INTEGRATION_AUDIT.md",
    ROOT / "UHMI_GA_R2E_API_CONTRACT_AND_FRONTEND_MAPPING_SPEC.md",
    ROOT / "UHMI_GA_R2E_REPORT.md",
]
BACKEND_API = ROOT / "AN_VANTARIS_IBMS-backend/src/api/uhmi/uhmi_api.py"
BACKEND_PROVIDER = ROOT / "AN_VANTARIS_IBMS-backend/src/uhmi/uhmi_provider.py"
FRONTEND_SERVICE = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/uhmi.ts"
FRONTEND_WORKSPACE = ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/uhmi/UhmiWorkspace.vue"
ROUTE_FILE = ROOT / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts"
MENU_FILE = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts"
PACKAGE_REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/package-registry.v1.json"
ROUTE_INVENTORY = ROOT / "AN_VANTARIS_ONE/registries/frontend-route-inventory.v1.json"
ROUTE_ENFORCEMENT = ROOT / "AN_VANTARIS_ONE/registries/package-route-enforcement.v1.json"
API_NAMESPACE = ROOT / "AN_VANTARIS_ONE/registries/api-namespace-registry.v1.json"

PREVIOUS_STAGE_REGISTRIES = {
    "UHMI-GA-R2A": (
        ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2a/uhmi-ga-r2a-uconsole-menu-ia-ui-api-skeleton.v1.json",
        "UHMI_GA_R2A_FULL_UCONSOLE_MENU_IA_UI_API_SKELETON_PASS",
    ),
    "UHMI-GA-R2B": (
        ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2b/uhmi-ga-r2b-workspace-panels-system-context.v1.json",
        "UHMI_GA_R2B_WORKSPACE_PANELS_SYSTEM_CONTEXT_PASS",
    ),
    "UHMI-GA-R2C": (
        ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2c/uhmi-ga-r2c-role-based-workspace-views.v1.json",
        "UHMI_GA_R2C_ROLE_BASED_WORKSPACE_VIEWS_PASS",
    ),
    "UHMI-GA-R2D": (
        ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2d/uhmi-ga-r2d-workspace-visual-polish-light-console-style.v1.json",
        "UHMI_GA_R2D_WORKSPACE_VISUAL_POLISH_LIGHT_CONSOLE_STYLE_PASS",
    ),
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
        fail(f"registry JSON parse failed for {path.relative_to(ROOT)}: {exc}")
    if not isinstance(data, dict):
        fail(f"registry must be a JSON object: {path.relative_to(ROOT)}")
    return data


def discover_uhmi_methods(path: Path) -> set[str]:
    tree = ast.parse(read(path))
    methods: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            if not isinstance(dec.func, ast.Attribute) or dec.func.attr != "route":
                continue
            route_path = ""
            if dec.args and isinstance(dec.args[0], ast.Constant) and isinstance(dec.args[0].value, str):
                route_path = dec.args[0].value
            if "uhmi" not in route_path.lower():
                continue
            for keyword in dec.keywords:
                if keyword.arg == "methods" and isinstance(keyword.value, ast.List):
                    for item in keyword.value.elts:
                        if isinstance(item, ast.Constant) and isinstance(item.value, str):
                            methods.add(item.value.upper())
    return methods


def main() -> None:
    required_files = [
        *DOCS,
        REGISTRY,
        BACKEND_API,
        BACKEND_PROVIDER,
        FRONTEND_SERVICE,
        FRONTEND_WORKSPACE,
        ROUTE_FILE,
        MENU_FILE,
        PACKAGE_REGISTRY,
        ROUTE_INVENTORY,
        ROUTE_ENFORCEMENT,
        API_NAMESPACE,
    ]
    for path in required_files:
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")
    ok("required R2E docs, registry, backend, frontend, route, menu, and package files exist")

    registry = load_json(REGISTRY)
    ok("R2E registry JSON parses")

    expected_fields = {
        "scope": "UHMI_GA_R2E",
        "taskId": "UHMI-GA-R2E",
        "mode": "read_only",
        "platform": "VANTARIS_ONE",
        "capability": "UHMI",
        "placement": "UConsole / UHMI Workspace",
        "workspace": "UConsole / UHMI Workspace",
        "releaseScope": "API_CONSOLIDATION_FRONTEND_INTEGRATION_AUDIT",
        "visualStyle": "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "apiVersion": "uhmi-workspace-readonly.v1",
        "validationPassMarker": PASS_MARKER,
    }
    for key, value in expected_fields.items():
        if registry.get(key) != value:
            fail(f"registry.{key} must equal {value}")
    for key in [
        "apiConsolidation",
        "frontendIntegrationAudit",
        "routeMenuPackageAlignment",
        "staticDataConsistency",
        "readOnlySafetyVerified",
    ]:
        if registry.get(key) is not True:
            fail(f"registry.{key} must be true")
    ok("R2E registry core fields are correct")

    previous = registry.get("previousStages")
    expected_previous = ["UHMI-GA-R2A", "UHMI-GA-R2B", "UHMI-GA-R2C", "UHMI-GA-R2D"]
    if previous != expected_previous:
        fail(f"registry.previousStages must equal {expected_previous}")
    ok("previousStages includes R2A through R2D")

    required_common = [
        "scope",
        "mode",
        "visualStyle",
        "workspace",
        "apiVersion",
        "readOnly",
        "safety",
        "guardrails",
        "futureControlPath",
        "generatedAt",
        "staticSnapshotAt",
    ]
    for field in required_common:
        if field not in registry.get("commonResponseFields", []):
            fail(f"common response field missing: {field}")
    ok("common response fields are registered")

    safety_fields = [
        "controlEnabled",
        "runtimeActivation",
        "deviceWrite",
        "dbWrite",
        "edgeCommandExecution",
        "linkCommandExecution",
        "realRbacMutation",
        "permissionWrite",
        "packageStateMutation",
        "installExecution",
        "rollbackExecution",
    ]
    safety = registry.get("safetyFields")
    if not isinstance(safety, dict):
        fail("registry.safetyFields must be an object")
    for field in safety_fields:
        if safety.get(field) is not False:
            fail(f"registry.safetyFields.{field} must be false")
    ok("registry safety fields are false")

    required_endpoint = "GET /api/one/uconsole/uhmi/integration-audit"
    if required_endpoint not in registry.get("apiEndpoints", []):
        fail("R2E integration audit endpoint missing from registry")
    ok("R2E endpoint is registered")

    combined_docs = "\n".join(read(path) for path in DOCS)
    for doc in DOCS:
        if PASS_MARKER not in read(doc):
            fail(f"PASS marker missing from {doc.relative_to(ROOT)}")
    for phrase in [
        "Unified Human-Machine Interface",
        "UConsole / UHMI Workspace",
        "not SCADA",
        "not independent HMI server",
        "read-only",
        "No Direct Device Control",
        "No Runtime Activation",
        "No DB Write",
        "UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device",
        "UHMI -> bypass CODE",
    ]:
        if phrase not in combined_docs:
            fail(f"required R2E doc phrase missing: {phrase}")
    ok("R2E docs contain required read-only boundary phrases and PASS marker")

    backend_text = read(BACKEND_PROVIDER) + "\n" + read(BACKEND_API)
    for phrase in [
        "UHMI_GA_R2E",
        "get_integration_audit",
        "integration-audit",
        "apiConsolidation",
        "frontendIntegrationAudit",
        "readOnlySafetyVerified",
        '"controlEnabled": False',
        '"runtimeActivation": False',
        '"deviceWrite": False',
        '"dbWrite": False',
        '"edgeCommandExecution": False',
        '"linkCommandExecution": False',
        '"realRbacMutation": False',
        '"permissionWrite": False',
        '"packageStateMutation": False',
        '"installExecution": False',
        '"rollbackExecution": False',
    ]:
        if phrase not in backend_text:
            fail(f"backend R2E required token missing: {phrase}")
    methods = discover_uhmi_methods(BACKEND_API)
    if methods != {"GET"}:
        fail(f"UHMI routes must be GET-only, found {sorted(methods)}")
    ok("backend R2E endpoint exists and all UHMI routes remain GET-only")

    frontend_service = read(FRONTEND_SERVICE)
    for phrase in [
        "UhmiIntegrationAuditPayload",
        "getUhmiIntegrationAudit",
        "UHMI_GA_R2E",
        "integration-audit",
        "readOnly",
        "safety",
        "futureControlPath",
        "visualStyle",
        "previousStages",
    ]:
        if phrase not in frontend_service:
            fail(f"frontend service R2E required token missing: {phrase}")
    ok("frontend service contains R2E audit typing and GET mapping")

    workspace_text = read(FRONTEND_WORKSPACE)
    for phrase in [
        "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "Read-only Mode",
        "No Direct Device Control",
        "No Runtime Activation",
        "No DB Write",
        "No Real RBAC Mutation",
        "Future Control Path",
    ]:
        if phrase not in workspace_text:
            fail(f"UHMI Workspace visual/guardrail phrase missing: {phrase}")
    ok("UHMI Workspace keeps R2D visual and guardrail phrases")

    route_text = read(ROUTE_FILE)
    menu_text = read(MENU_FILE)
    package_text = read(PACKAGE_REGISTRY)
    inventory_text = read(ROUTE_INVENTORY)
    enforcement_text = read(ROUTE_ENFORCEMENT)
    namespace_text = read(API_NAMESPACE)
    for phrase in ["/one/uhmi/overview", "/one/uhmi/system", "/one/uhmi/device"]:
        if phrase not in route_text:
            fail(f"frontend route missing UHMI route: {phrase}")
    for phrase in ["uconsole-uhmi-workspace", "UHMI Workspace"]:
        if phrase not in menu_text:
            fail(f"static menu missing UHMI reference: {phrase}")
    for text, name, phrase in [
        (package_text, "package registry", "/one/uhmi/overview"),
        (inventory_text, "frontend route inventory", "/one/uhmi/overview"),
        (enforcement_text, "package route enforcement", "/one/uhmi/overview"),
        (namespace_text, "api namespace registry", "/api/v1/one/uhmi"),
    ]:
        if phrase not in text:
            fail(f"{name} missing UHMI reference: {phrase}")
    ok("route, menu, package, and namespace references contain UHMI alignment")

    for stage, (path, marker) in PREVIOUS_STAGE_REGISTRIES.items():
        if not path.exists():
            fail(f"missing previous stage registry: {stage}")
        stage_text = read(path)
        if marker not in stage_text:
            fail(f"missing previous stage PASS marker in {stage}: {marker}")
    ok("R2A through R2D registries and PASS markers exist")

    active_text = "\n".join(
        read(path)
        for path in [
            *DOCS,
            BACKEND_API,
            BACKEND_PROVIDER,
            FRONTEND_SERVICE,
            FRONTEND_WORKSPACE,
        ]
    ).lower()
    forbidden_positive = [
        "direct control enabled",
        "runtime activation enabled",
        "db write enabled",
        "edge command enabled",
        "link command enabled",
        "rbac mutation enabled",
        "permission write enabled",
        "package state mutation enabled",
        "install execution enabled",
        "rollback execution enabled",
        "execute device command",
        "trigger edge command",
        "trigger link command",
    ]
    for phrase in forbidden_positive:
        if phrase in active_text:
            fail(f"forbidden active capability phrase found: {phrase}")
    ok("no forbidden active capability phrases found")

    for path in [*DOCS, REGISTRY, BACKEND_API, BACKEND_PROVIDER, FRONTEND_SERVICE, FRONTEND_WORKSPACE]:
        relative = path.relative_to(ROOT).as_posix()
        for token in [".env", "secrets", "node_modules", "dist", "build", ".runtime", "__pycache__", "._"]:
            if token in relative:
                fail(f"forbidden artifact path in R2E files: {relative}")
    ok("no forbidden artifact roots or files were added by R2E")

    print(PASS_MARKER)


if __name__ == "__main__":
    main()
