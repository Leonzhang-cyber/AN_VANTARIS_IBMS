#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "ONE_MODULE_GA_WAVE_R1_CONSOLIDATED_FREEZE_PASS"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/module-ga-wave-r1/module-ga-wave-r1-consolidated-freeze.v1.json"
REPORT = ROOT / "ONE_MODULE_GA_WAVE_R1_CONSOLIDATED_FREEZE_REPORT.md"
PACKAGES_DIR = ROOT / "AN_VANTARIS_ONE/packages"

MODULE_DOCS = {
    "UCDE": (ROOT / "UCDE_GA_R1_FINAL_CAPABILITY_AUDIT_AND_CONSOLIDATED_FREEZE.md", "UCDE_GA_R1_FINAL_CAPABILITY_AUDIT_AND_CONSOLIDATED_FREEZE_PASS"),
    "UCONSOLE": (ROOT / "UCONSOLE_GA_R1_FULL_MODULE_ENTRY_AND_MENU_CONSISTENCY_FREEZE.md", "UCONSOLE_GA_R1_FULL_MODULE_ENTRY_AND_MENU_CONSISTENCY_FREEZE_PASS"),
    "UMMS": (ROOT / "UMMS_GA_R1_FINAL_MODULE_CONSOLIDATED_FREEZE.md", "UMMS_GA_R1_FINAL_MODULE_CONSOLIDATED_FREEZE_PASS"),
    "UESG": (ROOT / "UESG_GA_R1_FINAL_MODULE_CONSOLIDATED_FREEZE.md", "UESG_GA_R1_FINAL_MODULE_CONSOLIDATED_FREEZE_PASS"),
    "REPORTS_ANALYTICS": (ROOT / "REPORTS_GA_R1_FINAL_REPORTS_AND_ANALYTICS_FREEZE.md", "REPORTS_GA_R1_FINAL_REPORTS_AND_ANALYTICS_FREEZE_PASS"),
    "GOVERNANCE_SECURITY": (ROOT / "GOVERNANCE_SECURITY_GA_R1_FINAL_GOVERNANCE_AND_SECURITY_FREEZE.md", "GOVERNANCE_SECURITY_GA_R1_FINAL_GOVERNANCE_AND_SECURITY_FREEZE_PASS"),
    "NEXUS_AI": (ROOT / "NEXUSAI_GA_R1_CURRENT_BRANCH_INTEGRATION_FREEZE.md", "NEXUSAI_GA_R1_CURRENT_BRANCH_INTEGRATION_FREEZE_PASS"),
}

EVIDENCE_FILES = [
    ROOT / "AN_VANTARIS_ONE/registries/module-ga-wave-r1/module-ga-wave-r1-evidence-files.txt",
    ROOT / "AN_VANTARIS_ONE/registries/module-ga-wave-r1/module-ga-wave-r1-pass-markers.txt",
    ROOT / "AN_VANTARIS_ONE/registries/module-ga-wave-r1/module-ga-wave-r1-route-api-references.txt",
    ROOT / "AN_VANTARIS_ONE/registries/module-ga-wave-r1/module-ga-wave-r1-risk-scan.txt",
]

EXPECTED_COUNTS = {"EDGE": 248, "LINK": 153, "DB": 14, "Contracts": 174}
PACKAGE_DIRS = {
    "EDGE": "AN_VANTARIS_EDGE",
    "LINK": "AN_VANTARIS_LINK",
    "DB": "AN_VANTARIS_DB",
    "Contracts": "AN_VANTARIS_Contracts",
}

NEW_FILES = [path for path, _ in MODULE_DOCS.values()] + EVIDENCE_FILES + [REGISTRY, REPORT, ROOT / "scripts/validation/validate-one-module-ga-wave-r1-consolidated-freeze.py"]
FORBIDDEN_NAMES = {".env", "node_modules", "dist", "build", ".runtime", "__pycache__"}
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


def marker_exists(marker: str) -> bool:
    result = subprocess.run(
        ["/usr/bin/grep", "-R", marker, str(ROOT), "--exclude-dir=.git", "--exclude-dir=node_modules", "--exclude-dir=.venv", "--exclude-dir=venv"],
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
    project_pythonpath = str(ROOT / "AN_VANTARIS_ONE")
    env["PYTHONPATH"] = project_pythonpath if not env.get("PYTHONPATH") else f"{project_pythonpath}{os.pathsep}{env['PYTHONPATH']}"
    result = subprocess.run([sys.executable, str(path)], cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    print(result.stdout)
    if result.returncode != 0:
        fail(f"{label} validator failed")
    if required_marker and required_marker not in result.stdout:
        fail(f"{label} marker missing from validator output: {required_marker}")
    ok(f"{label} validator passed")


def assert_forbidden_file_scan() -> None:
    hits: list[str] = []
    for path in NEW_FILES:
        name = path.name
        if name in FORBIDDEN_NAMES or name.startswith(".env.") or name.startswith("._") or any(name.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES):
            hits.append(str(path.relative_to(ROOT)))
    if hits:
        fail("Forbidden file names found across newly created files:\n" + "\n".join(hits))
    ok("Forbidden filename scan empty across newly created files")


def main() -> None:
    for module_id, (path, marker) in MODULE_DOCS.items():
        if not path.exists():
            fail(f"Missing module freeze document for {module_id}: {path.relative_to(ROOT)}")
        if marker not in read_text(path):
            fail(f"Missing module pass marker for {module_id}: {marker}")
    ok("All seven module freeze documents and pass markers exist")

    if not REGISTRY.exists():
        fail("Consolidated registry missing")
    registry = load_json(REGISTRY)
    ok("Consolidated registry exists and parses")
    if not REPORT.exists():
        fail("Consolidated report missing")
    if PASS_MARKER not in read_text(REPORT) or registry.get("passMarker") != PASS_MARKER:
        fail("Consolidated PASS marker missing from report or registry")
    ok("Consolidated report and PASS marker exist")

    for path in EVIDENCE_FILES:
        if not path.exists():
            fail(f"Evidence discovery file missing: {path.relative_to(ROOT)}")
    ok("Evidence discovery files exist")

    if registry.get("platform") != "VANTARIS_ONE":
        fail("Registry platform must equal VANTARIS_ONE")
    if registry.get("releaseScope") != "MODULE_GA_WAVE_R1":
        fail("Registry releaseScope must equal MODULE_GA_WAVE_R1")
    ok("Registry platform and releaseScope are correct")

    module_ids = {entry.get("moduleId") for entry in registry.get("modules", [])}
    missing = set(MODULE_DOCS) - module_ids
    if missing:
        fail(f"Registry missing module IDs: {sorted(missing)}")
    ok("Registry includes all seven module IDs")

    final_decision = registry.get("finalDecision", {})
    expected_decision = {
        "moduleWaveFreeze": "PASS",
        "fullInternationalGAAcrossAllModules": "NOT_YET",
        "customerProductionActivation": "NOT_EXECUTED",
    }
    for key, expected in expected_decision.items():
        if final_decision.get(key) != expected:
            fail(f"finalDecision.{key} expected {expected}")
    ok("Registry finalDecision values are correct")

    counts = registry.get("packageCounts", {})
    for key, expected in EXPECTED_COUNTS.items():
        if counts.get(key) != expected:
            fail(f"packageCounts.{key} expected {expected}")
        actual = count_files(PACKAGES_DIR / PACKAGE_DIRS[key])
        if actual != expected:
            fail(f"{PACKAGE_DIRS[key]} file count {actual} != {expected}")
    ok("Package counts match EDGE 248, LINK 153, DB 14, Contracts 174")

    combined = "\n".join(read_text(path) for path in NEW_FILES if path.exists())
    claim_text = "\n".join(read_text(path) for path in [*EVIDENCE_FILES, *[doc for doc, _ in MODULE_DOCS.values()], REGISTRY, REPORT] if path.exists())
    for phrase in [
        "VANTARIS ONE is cross-industry",
        "not airport-only",
        "No install executed",
        "No rollback executed",
        "No DB migration executed",
        "No runtime activation executed",
    ]:
        if phrase not in combined:
            fail(f"Required safety/scope phrase missing: {phrase}")
    ok("Documents state cross-industry scope and no install/rollback/DB/runtime execution")

    nexus_text = read_text(MODULE_DOCS["NEXUS_AI"][0])
    for phrase in [
        "NEXUS AI is advisory/decision/context layer",
        "no autonomous execution",
        "current branch integration freeze pending",
    ]:
        if phrase not in nexus_text:
            fail(f"NEXUS AI document missing phrase: {phrase}")
    ok("NEXUS AI advisory and integration-pending statements are present")

    uconsole_text = read_text(MODULE_DOCS["UCONSOLE"][0])
    for phrase in ["UConsole must not bypass CODE layer", "UConsole must not directly control devices"]:
        if phrase not in uconsole_text:
            fail(f"UConsole document missing phrase: {phrase}")
    ok("UConsole CODE/device-control boundary statements are present")

    assert_forbidden_file_scan()

    if not marker_exists("ONE_PROD_GA_R10_FINAL_INTERNATIONAL_GA_READINESS_MATRIX_PASS"):
        fail("R10 PASS marker missing")
    if not marker_exists("ONE_DESIGN_R1_FULL_PRODUCT_DESIGN_BLUEPRINT_PASS"):
        fail("ONE-DESIGN-R1 PASS marker missing")
    ok("R10 and ONE-DESIGN-R1 PASS markers exist")

    forbidden_positive_claims = [
        "push executed: true", "tag executed: true", "merge executed: true", "rebase executed: true",
        "production activation executed: true", "Production activation executed: true",
    ]
    lower_claim_text = claim_text.lower()
    for claim in forbidden_positive_claims:
        if claim.lower() in lower_claim_text:
            fail(f"Forbidden positive claim found: {claim}")
    ok("No claim of push/tag/merge/rebase or production activation appears")

    safety = registry.get("safety", {})
    for key in ["noInstall", "noRollback", "noDbMigration", "noRuntimeActivation", "noPush", "noTag"]:
        if safety.get(key) is not True:
            fail(f"Registry safety.{key} must be true")
    ok("Registry safety flags are correct")

    run_validator(ROOT / "scripts/validation/validate-one-package-route-enforcement.py", "Package route enforcement", "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS")
    run_validator(ROOT / "scripts/validation/validate-one-boundaries.py", "Boundary baseline", "ONE_BOUNDARY_BASELINE_PASS")

    print(PASS_MARKER)


if __name__ == "__main__":
    main()
