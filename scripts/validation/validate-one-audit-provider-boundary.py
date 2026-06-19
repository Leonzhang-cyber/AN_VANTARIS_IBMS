#!/usr/bin/env python3
"""Statically validate the bounded Governance Audit Provider foundation."""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "AN_VANTARIS_IBMS-backend/src/governance/audit"
GOVERNANCE_INIT = ROOT / "AN_VANTARIS_IBMS-backend/src/governance/__init__.py"
TEST_ROOT = ROOT / "AN_VANTARIS_IBMS-backend/src/tests/governance"
ALLOWED_PREFIXES = (
    "AN_VANTARIS_IBMS-backend/src/governance/",
    "AN_VANTARIS_IBMS-backend/src/tests/governance/",
    "AN_VANTARIS_IBMS-backend/src/api/system/menu_api.py",
    "scripts/validation/validate-one-audit-provider-boundary.py",
    "scripts/validation/validate-one-audit-integration-pilot.py",
)


def changed_paths() -> list[str]:
    tracked = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    ).stdout.splitlines()
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    ).stdout.splitlines()
    return sorted(set(tracked + untracked))


def main() -> int:
    errors: list[str] = []
    source_files = sorted(PACKAGE.glob("*.py"))
    expected = {
        "__init__.py", "constants.py", "errors.py", "models.py",
        "validation.py", "provider.py", "in_memory.py", "service.py", "pilot.py",
    }
    if {path.name for path in source_files} != expected:
        errors.append("audit provider source package is incomplete")
    if not GOVERNANCE_INIT.is_file() or not TEST_ROOT.is_dir():
        errors.append("governance package or focused test package is missing")

    forbidden_import_prefixes = (
        "src.reports", "src.ucde", "src.ufms", "src.uedge", "src.link",
        "src.Iot", "sqlalchemy", "redis", "kafka",
    )
    for path in source_files:
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            errors.append(f"{path.name}: syntax error at line {exc.lineno}")
            continue
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            for name in names:
                if name == "flask" and path.name != "pilot.py":
                    errors.append(f"{path.name}: forbidden cross-module import {name}")
                if name.startswith(forbidden_import_prefixes):
                    errors.append(f"{path.name}: forbidden cross-module import {name}")
            if isinstance(node, ast.ClassDef):
                if any(
                    isinstance(base, ast.Attribute) and base.attr == "Model"
                    for base in node.bases
                ):
                    errors.append(f"{path.name}: ORM model declaration found")
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                if any(isinstance(target, ast.Name) and target.id == "__tablename__" for target in targets):
                    errors.append(f"{path.name}: ORM table declaration found")
            if isinstance(node, ast.Call):
                function = node.func
                if isinstance(function, ast.Name) and function.id == "open":
                    errors.append(f"{path.name}: file persistence call found")
                if isinstance(function, ast.Attribute) and function.attr in {
                    "open", "write_text", "write_bytes", "mkdir", "touch",
                }:
                    errors.append(f"{path.name}: filesystem persistence call found")
        lowered = text.lower()
        if ".jsonl" in lowered or "reports_audit" in lowered:
            errors.append(f"{path.name}: Reports JSONL reference found")
        if "blueprint" in lowered or "@app.route" in lowered or "@api_bp.route" in lowered:
            errors.append(f"{path.name}: public route exposure found")
        if "one-adapter" in lowered or "one_adapter" in lowered:
            errors.append(f"{path.name}: generic one-adapter found")
        if "evidencerecord" in text.replace("AuditRecord", ""):
            errors.append(f"{path.name}: AuditRecord modeled as EvidenceRecord")

    models_text = (PACKAGE / "models.py").read_text(encoding="utf-8") if PACKAGE.is_dir() else ""
    prohibited_model_fields = {
        "password", "private_key", "seed_phrase", "bearer_token",
        "refresh_token", "authorization_header", "raw_jwt", "request_body",
    }
    try:
        model_tree = ast.parse(models_text)
        audit_class = next(
            node for node in model_tree.body
            if isinstance(node, ast.ClassDef) and node.name == "AuditRecord"
        )
        declared = {
            node.target.id for node in audit_class.body
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
        }
        forbidden = declared & prohibited_model_fields
        if forbidden:
            errors.append(f"AuditRecord contains prohibited fields: {sorted(forbidden)}")
        if "evidence_reference_ids" not in declared:
            errors.append("AuditRecord evidence-reference separation field missing")
    except (SyntaxError, StopIteration):
        errors.append("AuditRecord model could not be inspected")

    memory_text = (PACKAGE / "in_memory.py").read_text(encoding="utf-8") if PACKAGE.is_dir() else ""
    if "NON_PRODUCTION_IN_MEMORY_PROVIDER" not in memory_text:
        errors.append("in-memory provider is not marked non-production")

    changed = changed_paths()
    outside = [
        path for path in changed
        if not any(path == prefix or path.startswith(prefix) for prefix in ALLOWED_PREFIXES)
    ]
    if outside:
        errors.append("changed files outside allowed scope: " + ", ".join(outside))
    if any(path.startswith("AN_VANTARIS_IBMS-backend/migrations/") for path in changed):
        errors.append("migration file added")

    categories = [
        ("Provider ownership", not any("package is incomplete" in item or "package is missing" in item for item in errors)),
        ("No ORM persistence", not any("ORM" in item or "migration" in item for item in errors)),
        ("No JSONL persistence", not any("JSONL" in item or "filesystem persistence" in item or "file persistence" in item for item in errors)),
        ("Secret exclusion", not any("prohibited fields" in item for item in errors)),
        ("Evidence separation", not any("EvidenceRecord" in item or "evidence-reference" in item for item in errors)),
        ("Cross-module imports", not any("cross-module import" in item for item in errors)),
        ("Public API exposure", not any("public route" in item for item in errors)),
        ("Allowed path scope", not any("outside allowed scope" in item for item in errors)),
    ]
    print("[ONE AUDIT PROVIDER BOUNDARY VALIDATION]")
    for label, passed in categories:
        print(f"{label}: {'PASS' if passed else 'FAIL'}")
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        print("ONE_AUDIT_PROVIDER_BOUNDARY_FAIL")
        return 1
    print("ONE_AUDIT_PROVIDER_BOUNDARY_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
