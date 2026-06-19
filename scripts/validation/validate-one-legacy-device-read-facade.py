#!/usr/bin/env python3
"""Validate the bounded READ_ONLY legacy Device compatibility facade."""
from __future__ import annotations

import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/compatibility"
TESTS = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/compatibility"
VALIDATOR = "scripts/validation/validate-one-legacy-device-read-facade.py"
ALLOWED_PREFIXES = (
    "AN_VANTARIS_IBMS-backend/src/asset_graph/compatibility/",
    "AN_VANTARIS_IBMS-backend/tests/asset_graph/compatibility/",
)
LEGACY_PATHS = (
    "AN_VANTARIS_IBMS-backend/src/Iot/models.py",
    "AN_VANTARIS_IBMS-backend/src/Iot/dao.py",
)


def changed_paths() -> set[str]:
    tracked = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"], cwd=ROOT,
        capture_output=True, text=True, check=False,
    ).stdout.splitlines()
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT,
        capture_output=True, text=True, check=False,
    ).stdout.splitlines()
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT,
        capture_output=True, text=True, check=False,
    ).stdout.splitlines()
    paths = set(tracked + staged + untracked)
    if not paths:
        paths = set(subprocess.run(
            ["git", "diff", "--name-only", "HEAD^", "HEAD"], cwd=ROOT,
            capture_output=True, text=True, check=False,
        ).stdout.splitlines())
    return paths


def main() -> int:
    errors: list[str] = []
    files = sorted(PACKAGE.glob("*.py"))
    text = "\n".join(path.read_text(encoding="utf-8") for path in files)
    lowered = text.lower()
    if not files or not TESTS.is_dir():
        errors.append("compatibility package or tests missing")
    if "READ_ONLY_COMPATIBILITY_FACADE" not in text or "TEMPORARY_LEGACY_SOURCE" not in text:
        errors.append("read-only or temporary ownership marker missing")
    if "LegacyDeviceReadCompatibilityFacade" not in text or "Device(" not in text:
        errors.append("canonical Device projection missing")
    if "sha256" not in lowered or "MAPPING_VERSION" not in text:
        errors.append("versioned deterministic identity policy missing")
    if "SourceIdentity(" not in text or "missing stable source ID" not in text:
        errors.append("required SourceIdentity policy missing")
    if any(term in lowered for term in ("from src.iot", "import src.iot", "src.uedge", "src.link", "src.ufms")):
        errors.append("runtime ownership import found")
    if any(term in lowered for term in ("__tablename__", "sqlalchemy", "insert into", "update imbs_", "delete from")):
        errors.append("persistence declaration or SQL write found")
    if "blueprint" in lowered or "@api_bp.route" in lowered:
        errors.append("public route found")
    if "one_adapter" in lowered or "oneadapter" in lowered:
        errors.append("generic one-adapter found")
    if "current_value=" in lowered or "live_value=" in lowered or "telemetry_value=" in lowered:
        errors.append("telemetry value mapped")

    prohibited_calls = {
        "add_device", "add_point", "add_tag", "add_relationship",
        "create", "update", "delete", "save", "commit", "flush",
    }
    for path in files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            errors.append(f"syntax error: {path.name}:{exc.lineno}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = ""
                if isinstance(node.func, ast.Name):
                    name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    name = node.func.attr
                if name in prohibited_calls:
                    errors.append(f"write-like call found: {path.name}:{name}")
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in prohibited_calls:
                errors.append(f"write method found: {path.name}:{node.name}")

    changed = changed_paths()
    outside = sorted(
        path for path in changed
        if path != VALIDATOR and not path.startswith(ALLOWED_PREFIXES)
    )
    if outside:
        errors.append("changed files outside allowed scope: " + ", ".join(outside))
    if any(path in changed for path in LEGACY_PATHS):
        errors.append("legacy source changed")
    if any("migrations/" in path for path in changed):
        errors.append("migration changed")

    checks = [
        ("Read-only boundary", not any("read-only" in item or "write " in item or "write-like" in item for item in errors)),
        ("Legacy source unchanged", not any("legacy source changed" in item for item in errors)),
        ("Canonical projection", not any("canonical Device" in item for item in errors)),
        ("Deterministic identity", not any("deterministic identity" in item for item in errors)),
        ("Source identity", not any("SourceIdentity" in item for item in errors)),
        ("Credential exclusion", "sanitized_mapping" in text and "_PROHIBITED_KEY" in text),
        ("Telemetry exclusion", not any("telemetry value mapped" in item for item in errors)),
        ("No persistence writes", not any("persistence" in item or "SQL write" in item or "write-like" in item for item in errors)),
        ("No public API", not any("public route" in item for item in errors)),
        ("No EDGE runtime ownership", not any("runtime ownership" in item for item in errors)),
        ("Allowed path scope", not any("outside allowed" in item for item in errors)),
    ]
    print("[ONE LEGACY DEVICE READ FACADE VALIDATION]")
    for label, passed in checks:
        print(f"{label}: {'PASS' if passed else 'FAIL'}")
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        print("ONE_LEGACY_DEVICE_READ_FACADE_FAIL")
        return 1
    print("ONE_LEGACY_DEVICE_READ_FACADE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
