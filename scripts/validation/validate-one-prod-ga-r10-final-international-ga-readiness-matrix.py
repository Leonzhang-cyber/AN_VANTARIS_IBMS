#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "ONE_PROD_GA_R10_FINAL_INTERNATIONAL_GA_READINESS_MATRIX_PASS"
MATRIX = ROOT / "ONE_PROD_GA_R10_FINAL_INTERNATIONAL_GA_READINESS_MATRIX.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/prod-ga-final-international-ga-readiness-matrix.v1.json"
REPORT = ROOT / "ONE_PROD_GA_R10_FINAL_INTERNATIONAL_GA_READINESS_MATRIX_REPORT.md"
PACKAGES_DIR = ROOT / "AN_VANTARIS_ONE/packages"
R10_FILES = [
    MATRIX,
    REGISTRY,
    REPORT,
    ROOT / "scripts/validation/validate-one-prod-ga-r10-final-international-ga-readiness-matrix.py",
]

REQUIRED_MODULES = {
    "UCORE_UCODE",
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
    "CUSTOMER_DELIVERY",
    "OFFLINE_EXPORT",
}

EXPECTED_COUNTS = {
    "AN_VANTARIS_EDGE": 248,
    "AN_VANTARIS_LINK": 153,
    "AN_VANTARIS_DB": 14,
    "AN_VANTARIS_Contracts": 174,
}


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def ok(message: str) -> None:
    print(f"[PASS] {message}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def count_files(path: Path) -> int:
    return sum(1 for child in path.rglob("*") if child.is_file())


def load_json(path: Path) -> dict:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        fail(f"JSON parse failed for {path}: {exc}")


def run_validator(path: Path, label: str) -> None:
    if not path.exists():
        ok(f"{label} validator not present; skipped")
        return
    env = os.environ.copy()
    project_pythonpath = str(ROOT / "AN_VANTARIS_ONE")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        project_pythonpath
        if not existing_pythonpath
        else f"{project_pythonpath}{os.pathsep}{existing_pythonpath}"
    )
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
    forbidden_names = {
        ".env",
        "node_modules",
        "dist",
        "build",
        ".runtime",
        "__pycache__",
    }
    forbidden_suffixes = {".pem", ".key", ".p12", ".crt"}
    for path in paths:
        if not path.exists():
            continue
        candidates = [path] if path.is_file() else list(path.rglob("*"))
        for child in candidates:
            name = child.name
            if (
                name in forbidden_names
                or name.startswith(".env.")
                or name.startswith("._")
                or any(name.endswith(suffix) for suffix in forbidden_suffixes)
            ):
                hits.append(str(child.relative_to(ROOT)))
    return hits


def main() -> None:
    for path in [MATRIX, REGISTRY, REPORT]:
        if not path.exists():
            fail(f"Required R10 output missing: {path}")
    ok("Matrix, registry, and report exist")

    registry = load_json(REGISTRY)
    ok("Registry JSON parses")

    for path in [MATRIX, REGISTRY, REPORT]:
        if PASS_MARKER not in read_text(path):
            fail(f"PASS marker missing from {path}")
    ok("PASS marker exists in all R10 outputs")

    if registry.get("platform") != "VANTARIS_ONE":
        fail("Registry platform must equal VANTARIS_ONE")
    if registry.get("releaseScope") != "FINAL_INTERNATIONAL_GA_READINESS_MATRIX":
        fail("Registry releaseScope mismatch")
    ok("Registry platform and releaseScope are correct")

    modules = {entry.get("moduleId") for entry in registry.get("moduleMatrix", [])}
    missing = sorted(REQUIRED_MODULES - modules)
    if missing:
        fail(f"Missing module IDs in registry: {missing}")
    ok("All required modules are present in registry moduleMatrix")

    for package_name, expected_count in EXPECTED_COUNTS.items():
        actual_count = count_files(PACKAGES_DIR / package_name)
        if actual_count != expected_count:
            fail(f"{package_name} count {actual_count} != {expected_count}")
    foundation = registry.get("foundationPackageState", {})
    expected_foundation = {
        "edgeFileCount": 248,
        "linkFileCount": 153,
        "dbFileCount": 14,
        "contractsFileCount": 174,
        "status": "PASS",
    }
    for key, expected in expected_foundation.items():
        if foundation.get(key) != expected:
            fail(f"foundationPackageState.{key} expected {expected}")
    ok("Foundation package counts match EDGE 248, LINK 153, DB 14, Contracts 174")

    matrix_text = read_text(MATRIX)
    required_phrases = [
        "VANTARIS ONE is a cross-industry unified operations platform.",
        "It is not an airport-only system.",
        "Foundation package GA: PASS",
        "Offline export package: PASS",
        "Customer delivery scaffold: PASS",
        "Full customer production activation: NOT EXECUTED",
        "Full international GA across all modules: NOT YET",
    ]
    for phrase in required_phrases:
        if phrase not in matrix_text:
            fail(f"Matrix missing required phrase: {phrase}")
    ok("Matrix contains platform and final decision statements")

    forbidden = scan_forbidden_file_names(R10_FILES)
    if forbidden:
        fail("Forbidden file names found in R10 outputs:\n" + "\n".join(forbidden))
    ok("Forbidden scan empty across newly created R10 files")

    for marker in [
        "ONE_PROD_GA_R9_FINAL_CUSTOMER_DELIVERY_EDITION_PASS",
        "ONE_PROD_GA_R8_FINAL_EXPORT_PACKAGE_BUILDER_PASS",
        "ONE_PROD_GA_R7_FINAL_FOUNDATION_PACKAGE_CONSOLIDATED_RELEASE_INDEX_PASS",
        "ONE_PROD_GA_R6_FULL_EDGE_RUNTIME_RESYNC_GATE_PASS",
    ]:
        if not marker_exists(marker):
            fail(f"Required prior PASS marker missing: {marker}")
    ok("R9/R8/R7/R6 PASS markers exist")

    all_r10_text = "\n".join(read_text(path) for path in [MATRIX, REGISTRY, REPORT])
    forbidden_claims = [
        "Install executed: true",
        "Rollback executed: true",
        "DB migration executed: true",
        "Runtime action executed: true",
        "Production activation executed: true",
        "Push performed: true",
        "Tag created: true",
        "Merge performed: true",
        "Rebase performed: true",
    ]
    for claim in forbidden_claims:
        if claim in all_r10_text:
            fail(f"Forbidden execution claim found: {claim}")
    ok("No install/rollback/DB/runtime or push/tag/merge/rebase positive claim appears")

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
    ok("Registry safety flags are false")

    final_decision = registry.get("finalDecision", {})
    expected_decision = {
        "foundationPackageGA": "PASS",
        "offlineExportPackage": "PASS",
        "customerDeliveryScaffold": "PASS",
        "fullCustomerProductionActivation": "NOT_EXECUTED",
        "fullInternationalGAAcrossAllModules": "NOT_YET",
    }
    for key, expected in expected_decision.items():
        if final_decision.get(key) != expected:
            fail(f"finalDecision.{key} expected {expected}")
    ok("Registry final decisions are correct")

    run_validator(ROOT / "scripts/validation/validate-one-package-route-enforcement.py", "Package route enforcement")
    run_validator(ROOT / "scripts/validation/validate-one-boundaries.py", "Boundary baseline")

    print(PASS_MARKER)


if __name__ == "__main__":
    main()
