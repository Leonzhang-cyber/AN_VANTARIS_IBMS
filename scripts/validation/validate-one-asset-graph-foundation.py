#!/usr/bin/env python3
"""Statically validate the bounded Asset Graph Device/Point foundation."""
from __future__ import annotations

import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph"
TESTS = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph"
VALIDATOR = "scripts/validation/validate-one-asset-graph-foundation.py"
ALLOWED = (
    "AN_VANTARIS_IBMS-backend/src/asset_graph/",
    "AN_VANTARIS_IBMS-backend/tests/asset_graph/",
    VALIDATOR,
)


def changed_paths() -> set[str]:
    tracked = subprocess.run(["git", "diff", "--name-only", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    paths = set(tracked + untracked)
    if not paths:
        paths = set(subprocess.run(["git", "diff", "--name-only", "HEAD^", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines())
    return paths


def main() -> int:
    errors = []
    expected = {"__init__.py", "constants.py", "errors.py", "models.py", "provider.py", "validation.py", "in_memory.py"}
    files = sorted(PACKAGE.glob("*.py"))
    if {path.name for path in files} != expected:
        errors.append("Asset Graph package is incomplete")
    if not TESTS.is_dir():
        errors.append("focused Asset Graph tests are missing")
    forbidden_imports = ("src.Iot", "src.assets", "src.uedge", "src.link", "src.ufms", "sqlalchemy", "flask")
    for path in files:
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            errors.append(f"{path.name}: syntax error line {exc.lineno}")
            continue
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import): names = [alias.name for alias in node.names]
            if isinstance(node, ast.ImportFrom): names = [node.module or ""]
            for name in names:
                if name.startswith(forbidden_imports):
                    errors.append(f"{path.name}: forbidden import {name}")
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                if any(isinstance(target, ast.Name) and target.id == "__tablename__" for target in targets):
                    errors.append(f"{path.name}: ORM table declaration found")
            if isinstance(node, ast.Call):
                function = node.func
                if isinstance(function, ast.Name) and function.id == "open":
                    errors.append(f"{path.name}: filesystem call found")
                if isinstance(function, ast.Attribute) and function.attr in {"open", "write_text", "write_bytes", "mkdir", "touch"}:
                    errors.append(f"{path.name}: filesystem call found")
        lowered = text.lower()
        if ".jsonl" in lowered or "one-adapter" in lowered or "one_adapter" in lowered:
            errors.append(f"{path.name}: prohibited persistence or generic adapter reference")
        if "blueprint" in lowered or "@api_bp.route" in lowered:
            errors.append(f"{path.name}: public route added")
    models = (PACKAGE / "models.py").read_text(encoding="utf-8") if PACKAGE.is_dir() else ""
    if "class Device" not in models or "class Point" not in models or "class Tag" not in models:
        errors.append("canonical Device, Point or Tag model missing")
    if "class AssetRelationship" not in models:
        errors.append("relationship model missing")
    prohibited_fields = (
        "private_key:", "password:", "credential:", "connect_config:",
        "protocol_config:", "live_value:", "telemetry_value:", "telemetry_history:",
    )
    if any(field in models.lower() for field in prohibited_fields):
        errors.append("credential or telemetry field declared in canonical models")
    device_block = models[models.find("class Device"):models.find("class Point")]
    if "lifecycle_status" not in device_block or "operational_status" not in device_block:
        errors.append("Device lifecycle and operational status are not separate")
    point_block = models[models.find("class Point"):models.find("class Tag")]
    if "live_value" in point_block or "telemetry" in point_block:
        errors.append("Point stores live telemetry")
    constants = (PACKAGE / "constants.py").read_text(encoding="utf-8") if PACKAGE.is_dir() else ""
    memory = (PACKAGE / "in_memory.py").read_text(encoding="utf-8") if PACKAGE.is_dir() else ""
    if 'ASSET_GRAPH_OWNER = "ONE Asset Graph"' not in constants:
        errors.append("Device/Point ownership is not explicitly Asset Graph")
    if "NON_PRODUCTION_IN_MEMORY_PROVIDER" not in memory:
        errors.append("in-memory provider is not marked non-production")
    changed = changed_paths()
    outside = sorted(path for path in changed if not any(path == prefix or path.startswith(prefix) for prefix in ALLOWED))
    if outside:
        errors.append("changed files outside allowed scope: " + ", ".join(outside))
    if any(path.startswith("AN_VANTARIS_IBMS-backend/migrations/") for path in changed):
        errors.append("migration added")

    checks = [
        ("Canonical ownership", not any("ownership" in item for item in errors)),
        ("Device model", not any("Device" in item for item in errors)),
        ("Point model", not any("Point" in item for item in errors)),
        ("Tag model", not any("Tag" in item for item in errors)),
        ("Relationship model", not any("relationship model" in item for item in errors)),
        ("No ORM persistence", not any("ORM" in item for item in errors)),
        ("No migration", not any("migration" in item for item in errors)),
        ("No credential fields", not any("credential" in item for item in errors)),
        ("No EDGE runtime ownership", not any("uedge" in item.lower() or "EDGE" in item for item in errors)),
        ("No telemetry storage", not any("telemetry" in item for item in errors)),
        ("Lifecycle/status separation", not any("lifecycle" in item for item in errors)),
        ("Provider boundary", not any("forbidden import" in item or "filesystem" in item or "public route" in item for item in errors)),
        ("Allowed path scope", not any("outside allowed" in item for item in errors)),
    ]
    print("[ONE ASSET GRAPH FOUNDATION VALIDATION]")
    for label, passed in checks:
        print(f"{label}: {'PASS' if passed else 'FAIL'}")
    if errors:
        for error in errors: print(f"FAIL: {error}")
        print("ONE_ASSET_GRAPH_FOUNDATION_FAIL")
        return 1
    print("ONE_ASSET_GRAPH_FOUNDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
