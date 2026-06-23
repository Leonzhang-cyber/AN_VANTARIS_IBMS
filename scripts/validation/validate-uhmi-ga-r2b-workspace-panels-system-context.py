#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "UHMI_GA_R2B_WORKSPACE_PANELS_SYSTEM_CONTEXT_PASS"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2b/uhmi-ga-r2b-workspace-panels-system-context.v1.json"
DOCS = [
    ROOT / "UHMI_GA_R2B_WORKSPACE_PANELS_AND_SYSTEM_CONTEXT.md",
    ROOT / "UHMI_GA_R2B_SYSTEM_DEVICE_EVENT_EVIDENCE_CONTEXT_SPEC.md",
    ROOT / "UHMI_GA_R2B_REPORT.md",
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
    ok("required R2B files exist")

    registry = load_json(REGISTRY)
    ok("registry JSON parses")

    expected = {
        "scope": "UHMI_GA_R2B",
        "mode": "read_only",
        "visualStyle": "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
        "validationPassMarker": PASS_MARKER,
    }
    for key, value in expected.items():
        if registry.get(key) != value:
            fail(f"registry.{key} must equal {value}")
    ok("registry scope, mode, visualStyle, and PASS marker are correct")

    expected_panels = [
        "Overview",
        "System Panels",
        "Device Panels",
        "Mimic Panels",
        "Status View",
        "Event Context",
        "Evidence Context",
        "Guardrails",
        "Future Control Path",
    ]
    if registry.get("panels") != expected_panels:
        fail("registry panels do not match expected R2B panels")
    for key in ["systemContexts", "deviceContexts", "eventContexts", "evidenceContexts"]:
        if not registry.get(key):
            fail(f"registry missing non-empty {key}")
    ok("registry context sections are present")

    for doc in DOCS:
        if PASS_MARKER not in read(doc):
            fail(f"PASS marker missing from {doc.relative_to(ROOT)}")
    ok("PASS marker exists in R2B docs")

    backend_text = read(BACKEND_PROVIDER) + "\n" + read(BACKEND_API)
    backend_required = [
        "UHMI_GA_R2B",
        "read_only",
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
        "VANTARIS_LIGHT_OPERATIONS_CONSOLE",
    ]
    for phrase in backend_required:
        if phrase not in backend_text:
            fail(f"backend required phrase missing: {phrase}")
    ok("backend R2B safety response fields exist")

    methods = discover_uhmi_methods(BACKEND_API)
    if methods != {"GET"}:
        fail(f"UHMI routes must be GET-only, found {sorted(methods)}")
    forbidden_methods = ["POST", "PUT", "PATCH", "DELETE"]
    for method in forbidden_methods:
        if f'methods=["{method}"]' in backend_text or f"methods=['{method}']" in backend_text:
            fail(f"forbidden UHMI method found: {method}")
    ok("backend UHMI API is GET-only")

    frontend_required = [
        "Systems Monitored",
        "Devices Visible",
        "Active Events",
        "Panels Available",
        "Evidence Records",
        "Guardrails Active",
        "System Context",
        "Device Context",
        "Mimic Panel Preview",
        "Event Context",
        "Evidence Context",
        "Read-only Mode",
        "No Direct Device Control",
        "No Runtime Activation",
        "No DB Write",
        "Future Control Path",
    ]
    frontend_text = read(FRONTEND)
    for phrase in frontend_required:
        if phrase not in frontend_text:
            fail(f"frontend required phrase missing: {phrase}")
    ok("frontend R2B workspace panels exist")

    r2b_text = "\n".join(read(path) for path in [*DOCS, REGISTRY, BACKEND_PROVIDER, BACKEND_API, FRONTEND])
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
    ]
    for phrase in forbidden_design_phrases:
        if phrase in r2b_text:
            fail(f"forbidden design phrase found: {phrase}")
    ok("forbidden design phrases are absent from R2B files")

    forbidden_artifacts = [".env", "node_modules", "dist", "build", ".runtime", "secrets"]
    task_paths = [*DOCS, REGISTRY, BACKEND_PROVIDER, BACKEND_API, FRONTEND]
    for path in task_paths:
        relative = path.relative_to(ROOT).as_posix()
        for token in forbidden_artifacts:
            if token in relative:
                fail(f"forbidden artifact path in task files: {relative}")
    ok("no forbidden artifact roots or files were added by R2B")

    print(PASS_MARKER)


if __name__ == "__main__":
    main()
