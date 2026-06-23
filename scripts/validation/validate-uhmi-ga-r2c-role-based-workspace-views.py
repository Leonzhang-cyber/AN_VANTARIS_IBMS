#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "UHMI_GA_R2C_ROLE_BASED_WORKSPACE_VIEWS_PASS"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2c/uhmi-ga-r2c-role-based-workspace-views.v1.json"
DOCS = [
    ROOT / "UHMI_GA_R2C_ROLE_BASED_WORKSPACE_VIEWS.md",
    ROOT / "UHMI_GA_R2C_CUSTOMER_ENGINEER_ADMIN_OPERATOR_CONTEXT_SPEC.md",
    ROOT / "UHMI_GA_R2C_REPORT.md",
]
BACKEND_PROVIDER = ROOT / "AN_VANTARIS_IBMS-backend/src/uhmi/uhmi_provider.py"
BACKEND_API = ROOT / "AN_VANTARIS_IBMS-backend/src/api/uhmi/uhmi_api.py"
FRONTEND = ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/uhmi/UhmiWorkspace.vue"


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
            if "uhmi" not in route_path:
                continue
            for keyword in dec.keywords:
                if keyword.arg == "methods" and isinstance(keyword.value, ast.List):
                    for item in keyword.value.elts:
                        if isinstance(item, ast.Constant) and isinstance(item.value, str):
                            methods.add(item.value.upper())
    return methods


def main() -> None:
    required_files = [*DOCS, REGISTRY, BACKEND_PROVIDER, BACKEND_API, FRONTEND]
    for path in required_files:
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")
    ok("required R2C files exist")

    registry = load_json(REGISTRY)
    ok("registry JSON parses")

    expected = {
        "scope": "UHMI_GA_R2C",
        "mode": "read_only",
        "visualStyle": "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "validationPassMarker": PASS_MARKER,
    }
    for key, value in expected.items():
        if registry.get(key) != value:
            fail(f"registry.{key} must equal {value}")
    ok("registry scope, mode, visualStyle, and PASS marker are correct")

    expected_roles = ["Customer", "Engineer", "Admin", "Operator"]
    if registry.get("roles") != expected_roles:
        fail("registry roles do not match Customer, Engineer, Admin, Operator")
    for key in ["roleViews", "roleVisibilityMatrix", "disabledActions"]:
        if not registry.get(key):
            fail(f"registry missing non-empty {key}")
    expected_disabled = [
        "Device Control",
        "Runtime Activation",
        "DB Write",
        "EDGE Command",
        "LINK Command",
        "RBAC Mutation",
        "Package State Mutation",
        "Install/Rollback",
    ]
    for action in expected_disabled:
        if action not in registry.get("disabledActions", []):
            fail(f"disabled action missing: {action}")
    ok("registry roles, visibility matrix, and disabled actions are present")

    for doc in DOCS:
        if PASS_MARKER not in read(doc):
            fail(f"PASS marker missing from {doc.relative_to(ROOT)}")
    ok("PASS marker exists in R2C docs")

    backend_text = read(BACKEND_PROVIDER) + "\n" + read(BACKEND_API)
    backend_required = [
        "UHMI_GA_R2C",
        "read_only",
        "roleContextOnly",
        '"roleContextOnly": True',
        "realRbacMutation",
        '"realRbacMutation": False',
        "permissionWrite",
        '"permissionWrite": False',
        "packageStateMutation",
        '"packageStateMutation": False',
        "controlEnabled",
        '"controlEnabled": False',
        "runtimeActivation",
        '"runtimeActivation": False',
        "deviceWrite",
        '"deviceWrite": False',
        "dbWrite",
        '"dbWrite": False',
        "edgeCommandExecution",
        '"edgeCommandExecution": False',
        "linkCommandExecution",
        '"linkCommandExecution": False',
        "installExecution",
        '"installExecution": False',
        "rollbackExecution",
        '"rollbackExecution": False',
        "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
    ]
    for phrase in backend_required:
        if phrase not in backend_text:
            fail(f"backend required phrase missing: {phrase}")
    ok("backend R2C safety response fields exist")

    methods = discover_uhmi_methods(BACKEND_API)
    if methods != {"GET"}:
        fail(f"UHMI routes must be GET-only, found {sorted(methods)}")
    for method in ["POST", "PUT", "PATCH", "DELETE"]:
        if f'methods=["{method}"]' in backend_text or f"methods=['{method}']" in backend_text:
            fail(f"forbidden UHMI method found: {method}")
    ok("backend UHMI API is GET-only")

    frontend_text = read(FRONTEND)
    frontend_required = [
        "Role-based Workspace Views",
        "Customer",
        "Engineer",
        "Admin",
        "Operator",
        "Role Visibility Matrix",
        "Disabled Actions",
        "No Real RBAC Mutation",
        "No Permission Write",
        "No Direct Device Control",
        "No Runtime Activation",
        "No DB Write",
        "Future Control Path",
    ]
    for phrase in frontend_required:
        if phrase not in frontend_text:
            fail(f"frontend required phrase missing: {phrase}")
    ok("frontend R2C role workspace views exist")

    r2c_text = "\n".join(read(path) for path in [*DOCS, REGISTRY, BACKEND_PROVIDER, BACKEND_API, FRONTEND])
    forbidden_design_phrases = [
        "UFMS deep blue theme",
        "深蓝色主题",
        "dark SCADA dashboard",
        "SCADA replacement",
        "HMI Server",
        "direct control enabled",
        "runtime activation enabled",
        "db write enabled",
        "edge command enabled",
        "link command enabled",
        "rbac mutation enabled",
        "permission write enabled",
        "package state mutation enabled",
    ]
    for phrase in forbidden_design_phrases:
        if phrase in r2c_text:
            fail(f"forbidden design phrase found: {phrase}")
    ok("forbidden design phrases are absent from R2C files")

    forbidden_artifacts = [".env", "node_modules", "dist", "build", ".runtime", "secrets"]
    for path in [*DOCS, REGISTRY, BACKEND_PROVIDER, BACKEND_API, FRONTEND]:
        relative = path.relative_to(ROOT).as_posix()
        for token in forbidden_artifacts:
            if token in relative:
                fail(f"forbidden artifact path in task files: {relative}")
    ok("no forbidden artifact roots or files were added by R2C")

    print(PASS_MARKER)


if __name__ == "__main__":
    main()

