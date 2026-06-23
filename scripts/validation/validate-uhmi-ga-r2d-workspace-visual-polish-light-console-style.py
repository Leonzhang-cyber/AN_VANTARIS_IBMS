#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "UHMI_GA_R2D_WORKSPACE_VISUAL_POLISH_LIGHT_CONSOLE_STYLE_PASS"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2d/uhmi-ga-r2d-workspace-visual-polish-light-console-style.v1.json"
DOCS = [
    ROOT / "UHMI_GA_R2D_WORKSPACE_VISUAL_POLISH_LIGHT_CONSOLE_STYLE.md",
    ROOT / "UHMI_GA_R2D_LIGHT_CONSOLE_STYLE_TOKENS_AND_UI_GUIDE.md",
    ROOT / "UHMI_GA_R2D_REPORT.md",
]
FRONTEND = ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/uhmi/UhmiWorkspace.vue"
BACKEND_PROVIDER = ROOT / "AN_VANTARIS_IBMS-backend/src/uhmi/uhmi_provider.py"
BACKEND_API = ROOT / "AN_VANTARIS_IBMS-backend/src/api/uhmi/uhmi_api.py"


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
    for path in [*DOCS, REGISTRY, FRONTEND]:
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")
    ok("required R2D files exist")

    registry = load_json(REGISTRY)
    ok("registry JSON parses")

    expected = {
        "scope": "UHMI_GA_R2D",
        "mode": "read_only",
        "visualStyle": "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "validationPassMarker": PASS_MARKER,
    }
    for key, value in expected.items():
        if registry.get(key) != value:
            fail(f"registry.{key} must equal {value}")
    if registry.get("visualPolishFreeze") is not True:
        fail("registry.visualPolishFreeze must be true")
    if registry.get("lightConsoleStyleFreeze") is not True:
        fail("registry.lightConsoleStyleFreeze must be true")
    ok("registry core visual freeze fields are correct")

    required_tokens = [
        "light app shell",
        "white rounded cards",
        "soft shadow",
        "pale mint background",
        "teal primary accent",
        "pill tabs",
        "pastel icon blocks",
        "soft status badges",
        "clean table layout",
    ]
    for token in required_tokens:
        if token not in registry.get("styleTokens", []):
            fail(f"style token missing: {token}")
    required_components = [
        "UHMI Workspace Header",
        "Overview Metric Cards",
        "L3 Pill Tabs",
        "System Context Cards",
        "Device Context Table",
        "Mimic Panel Preview Cards",
        "Event Context Cards",
        "Evidence Context Cards",
        "Role Selector",
        "Role Visibility Matrix",
        "Disabled Actions Panel",
        "Guardrails Panel",
        "Future Control Path Panel",
    ]
    for component in required_components:
        if component not in registry.get("styledComponents", []):
            fail(f"styled component missing: {component}")
    ok("registry style tokens and styled components are present")

    for doc in DOCS:
        if PASS_MARKER not in read(doc):
            fail(f"PASS marker missing from {doc.relative_to(ROOT)}")
    ok("PASS marker exists in R2D docs")

    frontend_text = read(FRONTEND)
    frontend_required = [
        "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "Read-only Mode",
        "No Direct Device Control",
        "No Runtime Activation",
        "No DB Write",
        "Systems Monitored",
        "Devices Visible",
        "Active Events",
        "Panels Available",
        "Evidence Records",
        "Guardrails Active",
        "Role-based Workspace Views",
        "Role Visibility Matrix",
        "Future Control Path",
        "white-rounded-card",
        "soft-shadow",
        "teal-accent-card",
        "pale-mint-background",
        "pill-tabs",
        "soft-status-badges",
        "metric-card",
        "operations-table",
    ]
    for phrase in frontend_required:
        if phrase not in frontend_text:
            fail(f"frontend required visual token missing: {phrase}")
    ok("frontend R2D visual classes and text exist")

    backend_text = read(BACKEND_PROVIDER) + "\n" + read(BACKEND_API)
    if "UHMI_GA_R2D" in backend_text:
        backend_required = [
            "UHMI_GA_R2D",
            "read_only",
            "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
            "visualPolishFreeze",
            '"visualPolishFreeze": True',
            "lightConsoleStyleFreeze",
            '"lightConsoleStyleFreeze": True',
            '"controlEnabled": False',
            '"runtimeActivation": False',
            '"deviceWrite": False',
            '"dbWrite": False',
            '"edgeCommandExecution": False',
            '"linkCommandExecution": False',
        ]
        for phrase in backend_required:
            if phrase not in backend_text:
                fail(f"backend R2D required token missing: {phrase}")
    methods = discover_uhmi_methods(BACKEND_API)
    if methods != {"GET"}:
        fail(f"UHMI routes must be GET-only, found {sorted(methods)}")
    ok("backend remains GET-only and R2D metadata is safe")

    active_text = "\n".join(read(path) for path in [*DOCS, FRONTEND, BACKEND_PROVIDER, BACKEND_API])
    forbidden_positive = [
        "direct control enabled",
        "runtime activation enabled",
        "db write enabled",
        "edge command enabled",
        "link command enabled",
        "rbac mutation enabled",
        "permission write enabled",
        "package state mutation enabled",
    ]
    for phrase in forbidden_positive:
        if phrase in active_text:
            fail(f"forbidden positive capability phrase found: {phrase}")
    for phrase in registry.get("forbiddenVisualPatterns", []):
        if phrase not in registry.get("forbiddenVisualPatterns", []):
            fail(f"forbidden visual pattern not tracked: {phrase}")
    ok("forbidden visual patterns are tracked as forbidden, not active style")

    for path in [*DOCS, REGISTRY, FRONTEND, BACKEND_PROVIDER, BACKEND_API]:
        relative = path.relative_to(ROOT).as_posix()
        for token in [".env", "node_modules", "dist", "build", ".runtime", "secrets"]:
            if token in relative:
                fail(f"forbidden artifact path in task files: {relative}")
    ok("no forbidden artifact roots or files were added by R2D")

    print(PASS_MARKER)


if __name__ == "__main__":
    main()

