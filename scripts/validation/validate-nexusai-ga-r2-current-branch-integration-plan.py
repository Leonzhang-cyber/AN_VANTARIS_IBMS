#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "NEXUSAI_GA_R2_CURRENT_BRANCH_INTEGRATION_PLAN_PASS"
PLAN = ROOT / "NEXUSAI_GA_R2_CURRENT_BRANCH_INTEGRATION_PLAN.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/nexusai-ga-r2/nexusai-ga-r2-current-branch-integration-plan.v1.json"
REPORT = ROOT / "NEXUSAI_GA_R2_CURRENT_BRANCH_INTEGRATION_PLAN_REPORT.md"
DISCOVERY_FILES = [
    ROOT / "AN_VANTARIS_ONE/registries/nexusai-ga-r2/nexusai-current-branch-files.txt",
    ROOT / "AN_VANTARIS_ONE/registries/nexusai-ga-r2/nexusai-current-branch-references.txt",
    ROOT / "AN_VANTARIS_ONE/registries/nexusai-ga-r2/nexusai-branch-inventory.txt",
    ROOT / "AN_VANTARIS_ONE/registries/nexusai-ga-r2/nexusai-risk-scan.txt",
]
NEW_FILES = [
    PLAN,
    REGISTRY,
    REPORT,
    *DISCOVERY_FILES,
    ROOT / "scripts/validation/validate-nexusai-ga-r2-current-branch-integration-plan.py",
]


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
        fail(f"Registry JSON parse failed: {exc}")


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
    project_pythonpath = str(ROOT / "AN_VANTARIS_ONE")
    env["PYTHONPATH"] = project_pythonpath if not env.get("PYTHONPATH") else f"{project_pythonpath}{os.pathsep}{env['PYTHONPATH']}"
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


def main() -> None:
    if not PLAN.exists():
        fail("Plan markdown missing")
    if not REGISTRY.exists():
        fail("Registry JSON missing")
    registry = load_json(REGISTRY)
    if not REPORT.exists():
        fail("Report missing")
    ok("Plan, registry, and report exist")

    for path in DISCOVERY_FILES:
        if not path.exists():
            fail(f"Discovery file missing: {path.relative_to(ROOT)}")
    ok("Discovery files exist")

    for path in [PLAN, REGISTRY, REPORT]:
        if PASS_MARKER not in read_text(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("PASS marker exists in plan, registry, and report")

    if registry.get("platform") != "VANTARIS_ONE":
        fail("Registry platform must equal VANTARIS_ONE")
    if registry.get("capability") != "NEXUS_AI":
        fail("Registry capability must equal NEXUS_AI")
    if registry.get("releaseScope") != "CURRENT_BRANCH_INTEGRATION_PLAN":
        fail("Registry releaseScope must equal CURRENT_BRANCH_INTEGRATION_PLAN")
    ok("Registry platform, capability, and releaseScope are correct")

    status = registry.get("currentBranchStatus", {})
    if status.get("codeIntegration") != "NOT_EXECUTED":
        fail("currentBranchStatus.codeIntegration must equal NOT_EXECUTED")
    if status.get("productionActivation") != "NOT_EXECUTED":
        fail("currentBranchStatus.productionActivation must equal NOT_EXECUTED")
    ok("Registry currentBranchStatus values are correct")

    plan_text = read_text(PLAN)
    for phrase in [
        "NEXUS AI is advisory/decision/context layer.",
        "NEXUS AI is not autonomous executor.",
        "NEXUS AI must not directly control devices.",
        "NEXUS AI must not write DB by default.",
        "NEXUS AI must not bypass CODE layer.",
    ]:
        if phrase not in plan_text:
            fail(f"Plan missing required statement: {phrase}")
    ok("Plan includes required NEXUS AI boundary statements")

    for task_id in [
        "NEXUSAI-GA-R3",
        "NEXUSAI-GA-R4",
        "NEXUSAI-GA-R5",
        "NEXUSAI-GA-R6",
        "NEXUSAI-GA-R7",
        "NEXUSAI-GA-R8",
        "NEXUSAI-GA-R9",
    ]:
        if task_id not in plan_text:
            fail(f"Plan missing future task ID: {task_id}")
    ok("Plan includes all required future task IDs")

    scan_files = [PLAN, REGISTRY, REPORT, *DISCOVERY_FILES]
    combined = "\n".join(read_text(path) for path in scan_files if path.exists())
    forbidden_terms = [
        ".env",
        ".pem",
        ".key",
        ".p12",
        ".crt",
        "node_modules",
        "dist/",
        "build/",
        ".runtime",
        "__pycache__",
        "._",
    ]
    for term in forbidden_terms:
        if term in combined:
            fail(f"Forbidden term found across NEXUSAI-GA-R2 files: {term}")
    ok("Forbidden scan empty across newly created NEXUSAI-GA-R2 files")

    claim_text = "\n".join(read_text(path) for path in [PLAN, REGISTRY, REPORT] if path.exists()).lower()
    for phrase in [
        "merge executed: true",
        "cherry-pick executed: true",
        "code copy executed: true",
        "install executed: true",
        "rollback executed: true",
        "db migration executed: true",
        "runtime activation executed: true",
        "push executed: true",
        "tag executed: true",
        "production activation executed: true",
    ]:
        if phrase in claim_text:
            fail(f"Forbidden positive execution claim found: {phrase}")
    ok("No claim of merge/cherry-pick/code copy, install/rollback/DB/runtime, push/tag, or production activation")

    for marker in [
        "ONE_MODULE_GA_WAVE_R1_CONSOLIDATED_FREEZE_PASS",
        "ONE_PROD_GA_R10_FINAL_INTERNATIONAL_GA_READINESS_MATRIX_PASS",
        "ONE_DESIGN_R1_FULL_PRODUCT_DESIGN_BLUEPRINT_PASS",
    ]:
        if not marker_exists(marker):
            fail(f"Required prior PASS marker missing: {marker}")
    ok("Module wave, R10, and ONE-DESIGN-R1 PASS markers exist")

    safety = registry.get("safety", {})
    for key in ["noDbWrite", "noDeviceControl", "noRuntimeActivation", "noSecrets", "noExternalApiCalls"]:
        if safety.get(key) is not True:
            fail(f"Registry safety.{key} must be true")
    ok("Registry safety flags are correct")

    run_validator(ROOT / "scripts/validation/validate-one-package-route-enforcement.py", "Package route enforcement", "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS")
    run_validator(ROOT / "scripts/validation/validate-one-boundaries.py", "Boundary baseline", "ONE_BOUNDARY_BASELINE_PASS")

    print(PASS_MARKER)


if __name__ == "__main__":
    main()
