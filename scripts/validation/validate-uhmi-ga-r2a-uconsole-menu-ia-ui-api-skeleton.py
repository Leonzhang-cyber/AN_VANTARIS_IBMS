#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "UHMI_GA_R2A_FULL_UCONSOLE_MENU_IA_UI_API_SKELETON_PASS"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2a/uhmi-ga-r2a-uconsole-menu-ia-ui-api-skeleton.v1.json"
FREEZE_DOC = ROOT / "UHMI_GA_R2A_FULL_UCONSOLE_MENU_IA_UI_API_SKELETON.md"
REPORT = ROOT / "UHMI_GA_R2A_REPORT.md"

UHMI_FILES = [
    FREEZE_DOC,
    ROOT / "UHMI_GA_R2A_UCONSOLE_MENU_INFORMATION_ARCHITECTURE.md",
    ROOT / "UHMI_GA_R2A_UI_API_SKELETON_BOUNDARY_SPEC.md",
    REPORT,
    REGISTRY,
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2a/uhmi-r2a-route-menu-references.txt",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2a/uhmi-r2a-api-ui-files.txt",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2a/uhmi-r2a-risk-scan.txt",
    ROOT / "AN_VANTARIS_IBMS-backend/src/uhmi/uhmi_provider.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/uhmi/uhmi_api.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/uhmi/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-backend/src/uhmi/__init__.py",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/uhmi/UhmiWorkspace.vue",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/uhmi.ts",
    ROOT / "scripts/validation/validate-uhmi-ga-r2a-uconsole-menu-ia-ui-api-skeleton.py",
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def ok(message: str) -> None:
    print(f"[PASS] {message}")


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict:
    try:
        data = json.loads(text(path))
    except json.JSONDecodeError as exc:
        fail(f"Registry JSON parse failed: {exc}")
    if not isinstance(data, dict):
        fail("Registry JSON must be an object")
    return data


def marker_exists(marker: str) -> bool:
    result = subprocess.run(
        [
            "/usr/bin/grep",
            "-R",
            marker,
            str(ROOT),
            "--exclude-dir=.git",
            "--exclude-dir=node_modules",
            "--exclude-dir=.venv",
            "--exclude-dir=venv",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.returncode == 0


def run_validator(path: Path, label: str, required_marker: str | None = None) -> None:
    if not path.exists():
        ok(f"{label} validator not present; skipped")
        return
    env = os.environ.copy()
    pythonpath = str(ROOT / "AN_VANTARIS_ONE")
    env["PYTHONPATH"] = pythonpath if not env.get("PYTHONPATH") else f"{pythonpath}{os.pathsep}{env['PYTHONPATH']}"
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(result.stdout)
    if result.returncode != 0:
        fail(f"{label} validator failed")
    if required_marker and required_marker not in result.stdout:
        fail(f"{label} marker missing from validator output: {required_marker}")
    ok(f"{label} validator passed")


def discover_backend_methods(path: Path) -> set[str]:
    tree = ast.parse(text(path))
    methods: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            if not isinstance(dec.func, ast.Attribute) or dec.func.attr != "route":
                continue
            for keyword in dec.keywords:
                if keyword.arg == "methods" and isinstance(keyword.value, ast.List):
                    for item in keyword.value.elts:
                        if isinstance(item, ast.Constant) and isinstance(item.value, str):
                            methods.add(item.value.upper())
    return methods


def main() -> None:
    for path in UHMI_FILES:
        if not path.exists():
            fail(f"Missing UHMI R2A file: {path.relative_to(ROOT)}")
    ok("All UHMI R2A files exist")

    registry = load_json(REGISTRY)
    ok("Registry JSON parses")

    for path in [FREEZE_DOC, REPORT, REGISTRY]:
        if PASS_MARKER not in text(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("PASS marker exists in freeze doc, report, and registry")

    expected = {
        "platform": "VANTARIS_ONE",
        "capability": "UHMI",
        "placement": "UConsole / UHMI Workspace",
        "releaseScope": "READ_ONLY_UI_API_SKELETON",
    }
    for field, value in expected.items():
        if registry.get(field) != value:
            fail(f"Registry {field} must equal {value}")
    for field in ["crossIndustry", "readOnly"]:
        if registry.get(field) is not True:
            fail(f"Registry {field} must be true")
    for field in ["airportOnly", "standaloneHmiServer", "scadaReplacement", "runtimeActivation", "productionActivation", "directDeviceControl", "directDatabaseWrite", "bypassCode", "dbMigration", "installOrRollback"]:
        if registry.get(field) is not False:
            fail(f"Registry {field} must be false")
    ok("Registry core fields and safety flags are correct")

    combined = "\n".join(text(path) for path in UHMI_FILES if path.suffix in {".md", ".json", ".txt", ".py", ".ts", ".vue"})
    required_phrases = [
        "UHMI = Unified Human-Machine Interface",
        "UConsole / UHMI Workspace",
        "not a SCADA replacement",
        "not an independent HMI server",
        "read-only",
        "No direct device control",
        "No direct DB write",
        "No bypass CODE",
        "Device/System -> EDGE -> LINK -> CODE -> UConsole/UHMI",
        "UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device",
        "NOT EXECUTED in R2A",
        "Sidebar only L1/L2; L3 inside page.",
    ]
    for phrase in required_phrases:
        if phrase not in combined:
            fail(f"Required phrase missing: {phrase}")
    ok("Required UHMI R2A phrases exist")

    menu_labels = [item.get("label") for item in registry.get("menuIa", {}).get("items", [])]
    expected_labels = [
        "HMI Overview",
        "System HMI",
        "Device HMI",
        "Alarm & Event HMI",
        "EDGE / LINK Diagnostics",
        "Evidence & Reports",
    ]
    if menu_labels != expected_labels:
        fail("UHMI menu labels do not match expected IA")
    ok("UHMI L3 menu IA is correct")

    route_file = text(ROOT / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts")
    static_menu = text(ROOT / "AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts")
    for route in [item["route"] for item in registry["menuIa"]["items"]]:
        if route not in route_file:
            fail(f"Frontend route missing: {route}")
    if "id: 'uconsole-uhmi-workspace'" not in static_menu:
        fail("UConsole UHMI Workspace L2 menu entry missing")
    ok("Frontend route and menu wiring exists")

    methods = discover_backend_methods(ROOT / "AN_VANTARIS_IBMS-backend/src/api/uhmi/uhmi_api.py")
    if methods != {"GET"}:
        fail(f"UHMI API must be GET-only, found: {sorted(methods)}")
    ok("UHMI backend API is GET-only")

    forbidden_source_tokens = [
        "db.session",
        ".commit(",
        "@api_bp.route(\"/v1/one/uhmi",
        "methods=[\"POST\"]",
        "methods=[\"PUT\"]",
        "methods=[\"PATCH\"]",
        "methods=[\"DELETE\"]",
        "send_command",
        "execute_command",
        "runtimeActivation\": True",
        "directDeviceControl\": True",
        "bypassCode\": True",
    ]
    source_paths = [
        ROOT / "AN_VANTARIS_IBMS-backend/src/uhmi/uhmi_provider.py",
        ROOT / "AN_VANTARIS_IBMS-backend/src/api/uhmi/uhmi_api.py",
        ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/uhmi/UhmiWorkspace.vue",
        ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/uhmi.ts",
    ]
    source_text = "\n".join(text(path) for path in source_paths)
    for token in forbidden_source_tokens:
        if token != "@api_bp.route(\"/v1/one/uhmi" and token in source_text:
            fail(f"Forbidden UHMI source token found: {token}")
    ok("UHMI source scan contains no write/control/runtime tokens")

    route_scan = text(ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r2a/uhmi-r2a-risk-scan.txt")
    forbidden_artifacts = [".env", "secrets", "node_modules", "dist/", "build/", ".runtime", "__pycache__", "._"]
    for token in forbidden_artifacts:
        if token in route_scan:
            fail(f"Forbidden artifact token found in R2A risk scan: {token}")
    ok("Forbidden artifact scan is empty for excluded roots and names")

    for marker in [
        "UHMI_GA_R1_UCONSOLE_UHMI_WORKSPACE_READONLY_FOUNDATION_FREEZE_PASS",
        "ONE_DESIGN_R1_FULL_PRODUCT_DESIGN_BLUEPRINT_PASS",
        "ONE_MODULE_GA_WAVE_R1_CONSOLIDATED_FREEZE_PASS",
    ]:
        if not marker_exists(marker):
            fail(f"Required prior PASS marker missing: {marker}")
    ok("Prior PASS markers exist")

    run_validator(ROOT / "scripts/validation/validate-one-package-route-enforcement.py", "Package route enforcement", "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS")
    run_validator(ROOT / "scripts/validation/validate-one-boundaries.py", "Boundary baseline", "ONE_BOUNDARY_BASELINE_PASS")

    print(PASS_MARKER)


if __name__ == "__main__":
    main()

