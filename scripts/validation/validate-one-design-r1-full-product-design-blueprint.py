#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "ONE_DESIGN_R1_FULL_PRODUCT_DESIGN_BLUEPRINT_PASS"

CREATED_FILES = [
    ROOT / "VANTARIS_ONE_FULL_PRODUCT_DESIGN_BLUEPRINT_R1.md",
    ROOT / "VANTARIS_ONE_MODULE_ARCHITECTURE_AND_RESPONSIBILITY_MATRIX_R1.md",
    ROOT / "VANTARIS_ONE_GA_GAP_AND_ROADMAP_R1.md",
    ROOT / "VANTARIS_ONE_CUSTOMER_DELIVERY_AND_DEPLOYMENT_DESIGN_R1.md",
    ROOT / "VANTARIS_ONE_UI_UCONSOLE_INFORMATION_ARCHITECTURE_R1.md",
    ROOT / "VANTARIS_ONE_DATA_AND_EVENT_FLOW_DESIGN_R1.md",
    ROOT / "VANTARIS_ONE_SECURITY_GOVERNANCE_AND_POLICY_DESIGN_R1.md",
    ROOT / "AN_VANTARIS_ONE/registries/full-product-design-blueprint-r1.v1.json",
    ROOT / "ONE_DESIGN_R1_FULL_PRODUCT_DESIGN_BLUEPRINT_REPORT.md",
    ROOT / "scripts/validation/validate-one-design-r1-full-product-design-blueprint.py",
]

REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/full-product-design-blueprint-r1.v1.json"
BLUEPRINT = ROOT / "VANTARIS_ONE_FULL_PRODUCT_DESIGN_BLUEPRINT_R1.md"
REPORT = ROOT / "ONE_DESIGN_R1_FULL_PRODUCT_DESIGN_BLUEPRINT_REPORT.md"
PACKAGES_DIR = ROOT / "AN_VANTARIS_ONE/packages"

REQUIRED_MODULES = {
    "UCODE",
    "UMMS",
    "UFMS",
    "UESG",
    "UCDE",
    "UDOC",
    "AUTOMATED_RULES_POLICY",
    "ONE_ORCHESTRATOR",
    "UCONSOLE",
    "REPORTS_ANALYTICS",
    "GOVERNANCE_SECURITY",
    "NEXUS_AI",
    "EDGE",
    "LINK",
    "DB",
    "CONTRACTS",
    "CUSTOMER_DELIVERY_INSTALLER",
    "OFFLINE_EXPORT",
}

EXPECTED_COUNTS = {
    "EDGE": 248,
    "LINK": 153,
    "DB": 14,
    "Contracts": 174,
}

PACKAGE_DIRS = {
    "EDGE": "AN_VANTARIS_EDGE",
    "LINK": "AN_VANTARIS_LINK",
    "DB": "AN_VANTARIS_DB",
    "Contracts": "AN_VANTARIS_Contracts",
}

FORBIDDEN_NAMES = {
    ".env",
    "node_modules",
    "dist",
    "build",
    ".runtime",
    "__pycache__",
}
FORBIDDEN_SUFFIXES = {".pem", ".key", ".p12", ".crt"}


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def ok(message: str) -> None:
    print(f"[PASS] {message}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        fail(f"JSON parse failed for {path}: {exc}")


def count_files(path: Path) -> int:
    return sum(1 for child in path.rglob("*") if child.is_file())


def run_validator(path: Path, label: str, required_marker: str | None = None) -> None:
    if not path.exists():
        ok(f"{label} validator not present; skipped")
        return
    env = os.environ.copy()
    project_pythonpath = str(ROOT / "AN_VANTARIS_ONE")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = project_pythonpath if not existing_pythonpath else f"{project_pythonpath}{os.pathsep}{existing_pythonpath}"
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


def scan_forbidden_file_names(paths: list[Path]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        name = path.name
        if (
            name in FORBIDDEN_NAMES
            or name.startswith(".env.")
            or name.startswith("._")
            or any(name.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES)
        ):
            hits.append(str(path.relative_to(ROOT)))
    return hits


def main() -> None:
    for path in CREATED_FILES:
        if not path.exists():
            fail(f"Required created file missing: {path.relative_to(ROOT)}")
    ok("All 10 created files exist")

    registry = load_json(REGISTRY)
    ok("Registry JSON parses")

    for path in [BLUEPRINT, REGISTRY, REPORT]:
        if PASS_MARKER not in read_text(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("PASS marker exists in blueprint, registry, and report")

    if registry.get("platform") != "VANTARIS_ONE":
        fail("Registry platform must equal VANTARIS_ONE")
    if registry.get("designScope") != "FULL_PRODUCT_BLUEPRINT":
        fail("Registry designScope must equal FULL_PRODUCT_BLUEPRINT")
    ok("Registry platform and designScope are correct")

    module_ids = {entry.get("moduleId") for entry in registry.get("modules", [])}
    missing = sorted(REQUIRED_MODULES - module_ids)
    if missing:
        fail(f"Required modules missing from registry: {missing}")
    ok("Required modules exist in registry")

    package_counts = registry.get("packageCounts", {})
    for key, expected in EXPECTED_COUNTS.items():
        if package_counts.get(key) != expected:
            fail(f"Registry packageCounts.{key} expected {expected}")
        actual = count_files(PACKAGES_DIR / PACKAGE_DIRS[key])
        if actual != expected:
            fail(f"Package directory {PACKAGE_DIRS[key]} file count {actual} != {expected}")
    ok("Package counts match EDGE 248, LINK 153, DB 14, Contracts 174")

    combined_docs = "\n".join(read_text(path) for path in CREATED_FILES if path.suffix in {".md", ".json"})
    required_phrases = [
        "VANTARIS ONE is a cross-industry",
        "not an airport-only",
        "Full customer production activation: NOT EXECUTED",
        "Full international GA across all modules: NOT YET",
    ]
    for phrase in required_phrases:
        if phrase not in combined_docs:
            fail(f"Required platform/readiness phrase missing: {phrase}")
    ok("Documents state cross-industry scope and current activation/GA limits")

    required_document_topics = {
        "UI/UConsole architecture": "UConsole",
        "data/event flow": "Device -> EDGE -> LINK -> CODE -> Modules -> UConsole",
        "security/governance/policy design": "Security Governance And Policy",
        "GA gap roadmap": "GA Gap And Roadmap",
    }
    for label, phrase in required_document_topics.items():
        if phrase not in combined_docs:
            fail(f"Documents missing {label}")
    ok("Documents include UI/UConsole, data/event, security/governance, and GA roadmap content")

    forbidden = scan_forbidden_file_names(CREATED_FILES)
    if forbidden:
        fail("Forbidden file names found across new files:\n" + "\n".join(forbidden))
    ok("Forbidden filename scan empty across new files")

    forbidden_positive_claims = [
        "Install executed: true",
        "Rollback executed: true",
        "DB migration executed: true",
        "Runtime action executed: true",
        "Runtime activation executed: true",
        "Production activation executed: true",
        "Push performed: true",
        "Tag created: true",
        "Merge performed: true",
        "Rebase performed: true",
    ]
    for claim in forbidden_positive_claims:
        if claim in combined_docs:
            fail(f"Forbidden positive execution claim found: {claim}")
    ok("No install/rollback/DB migration/runtime execution positive claim appears")
    ok("No push/tag/merge/rebase positive claim appears")

    if not marker_exists("ONE_PROD_GA_R10_FINAL_INTERNATIONAL_GA_READINESS_MATRIX_PASS"):
        fail("R10 PASS marker missing")
    ok("R10 PASS marker exists")
    if not marker_exists("ONE_PROD_GA_R9_FINAL_CUSTOMER_DELIVERY_EDITION_PASS"):
        fail("R9 PASS marker missing")
    ok("R9 PASS marker exists")

    run_validator(
        ROOT / "scripts/validation/validate-one-package-route-enforcement.py",
        "Package route enforcement",
        "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS",
    )
    run_validator(
        ROOT / "scripts/validation/validate-one-boundaries.py",
        "Boundary baseline",
        "ONE_BOUNDARY_BASELINE_PASS",
    )

    safety = registry.get("safety", {})
    for key in [
        "installExecuted",
        "rollbackExecuted",
        "dbMigrationExecuted",
        "runtimeActionExecuted",
        "productionActivationExecuted",
        "pushPerformed",
        "tagCreated",
        "mergePerformed",
        "rebasePerformed",
    ]:
        if safety.get(key) is not False:
            fail(f"Registry safety.{key} must be false")
    ok("Registry safety flags confirm no forbidden runtime or git publication action")

    print(PASS_MARKER)


if __name__ == "__main__":
    main()
