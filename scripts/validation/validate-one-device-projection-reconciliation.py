#!/usr/bin/env python3
"""Validate the bounded Device projection reconciliation baseline."""
from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation"
TESTS = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation"
POLICY = ROOT / "AN_VANTARIS_ONE/registries/device-projection-reconciliation-policy.v1.json"
VALIDATOR = "scripts/validation/validate-one-device-projection-reconciliation.py"
ALLOWED = (
    "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/",
    "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/",
)


def changed_paths() -> set[str]:
    commands = (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    )
    paths: set[str] = set()
    for command in commands:
        paths.update(subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True, check=False,
        ).stdout.splitlines())
    if not paths:
        paths.update(subprocess.run(
            ["git", "diff", "--name-only", "HEAD^", "HEAD"], cwd=ROOT,
            capture_output=True, text=True, check=False,
        ).stdout.splitlines())
    return paths


def main() -> int:
    errors: list[str] = []
    files = sorted(PACKAGE.glob("*.py"))
    text = "\n".join(path.read_text(encoding="utf-8") for path in files)
    lowered = text.lower()
    policy = json.loads(POLICY.read_text(encoding="utf-8")) if POLICY.is_file() else {}
    if not files or not TESTS.is_dir():
        errors.append("reconciliation package or tests missing")
    if "LegacyDeviceReadCompatibilityFacade" not in text or "project_device(" not in text:
        errors.append("existing compatibility facade is not reused")
    if "operational_map =" in text or "field_type_map =" in text:
        errors.append("legacy projection mapping logic duplicated")
    if "sha256" not in lowered or "canonical_json" not in text:
        errors.append("deterministic SHA-256 policy missing")
    if "NOT_READY_FOR_WRITE_CUTOVER" not in text:
        errors.append("safe cutover default missing")
    if "GLOBAL_ID_COLLISION" not in text or "SOURCE_IDENTITY_COLLISION" not in text:
        errors.append("identity collision blockers missing")
    if "TENANT_SCOPE" not in text or "SITE_SCOPE" not in text:
        errors.append("scope mismatch blockers missing")
    if "unresolved_relationships" not in text or "REVIEW_REQUIRED" not in text:
        errors.append("unresolved review visibility missing")
    if any(term in lowered for term in ("src.uedge", "src.iot", "src.link", "src.ufms")):
        errors.append("runtime ownership import found")
    if any(term in lowered for term in ("sqlalchemy", "__tablename__", "insert into", "update imbs_", "delete from", ".jsonl")):
        errors.append("persistence or SQL write found")
    if "blueprint" in lowered or "@api_bp.route" in lowered:
        errors.append("public API found")
    if "one_adapter" in lowered or "oneadapter" in lowered:
        errors.append("generic one-adapter found")
    if policy.get("defaultCutoverDecision") != "NOT_READY_FOR_WRITE_CUTOVER":
        errors.append("policy cutover default unsafe")
    required_dimensions = {
        "GLOBAL_ID_COLLISION", "SOURCE_IDENTITY_COLLISION", "FIELD_MAPPING_COMPLETENESS",
        "RELATIONSHIP_REFERENCE", "PROHIBITED_FIELD_EXCLUSION", "PROJECTION_DIGEST",
        "REPEAT_RUN_DETERMINISM", "BATCH_ORDER_DETERMINISM",
    }
    actual_dimensions = {
        item.get("dimensionId") for item in policy.get("reconciliationDimensions", [])
    }
    if not required_dimensions <= actual_dimensions:
        errors.append("policy reconciliation dimensions incomplete")

    write_names = {
        "add_device", "add_point", "add_tag", "add_relationship",
        "create", "delete", "save", "commit", "flush",
    }
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
                if name in write_names:
                    errors.append(f"write operation found: {path.name}:{name}")
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in write_names:
                errors.append(f"write method found: {path.name}:{node.name}")

    changed = changed_paths()
    allowed_files = {
        "AN_VANTARIS_ONE/registries/device-projection-reconciliation-policy.v1.json",
        VALIDATOR,
    }
    outside = sorted(path for path in changed if path not in allowed_files and not path.startswith(ALLOWED))
    if outside:
        errors.append("changed files outside allowed scope: " + ", ".join(outside))
    if any("migrations/" in path for path in changed):
        errors.append("migration changed")

    checks = [
        ("Read-only reconciliation", not any("write operation" in item or "write method" in item for item in errors)),
        ("Facade reuse", not any("facade" in item or "duplicated" in item for item in errors)),
        ("Identity reconciliation", not any("identity collision" in item for item in errors)),
        ("Field coverage", "FieldCoverage" in text and "required_field_coverage" in text),
        ("Relationship coverage", "RelationshipReconciliationResult" in text),
        ("Credential exclusion", "_PROHIBITED" in text and "prohibited_fields_detected" in text),
        ("Telemetry exclusion", "_PROHIBITED" in text),
        ("Deterministic digests", not any("SHA-256" in item for item in errors)),
        ("No persistence writes", not any("persistence" in item or "SQL write" in item for item in errors)),
        ("No public API", not any("public API" in item for item in errors)),
        ("Cutover safety", not any("cutover default" in item for item in errors)),
        ("Allowed path scope", not any("outside allowed" in item for item in errors)),
    ]
    print("[ONE DEVICE PROJECTION RECONCILIATION VALIDATION]")
    for label, passed in checks:
        print(f"{label}: {'PASS' if passed else 'FAIL'}")
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        print("ONE_DEVICE_PROJECTION_RECONCILIATION_FAIL")
        return 1
    print("ONE_DEVICE_PROJECTION_RECONCILIATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
