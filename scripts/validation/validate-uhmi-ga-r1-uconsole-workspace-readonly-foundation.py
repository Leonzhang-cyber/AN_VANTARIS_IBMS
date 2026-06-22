#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "UHMI_GA_R1_UCONSOLE_UHMI_WORKSPACE_READONLY_FOUNDATION_FREEZE_PASS"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r1/uhmi-ga-r1-uconsole-workspace-readonly-foundation.v1.json"
FREEZE_DOC = ROOT / "UHMI_GA_R1_UCONSOLE_UHMI_WORKSPACE_READONLY_FOUNDATION_FREEZE.md"
REPORT = ROOT / "UHMI_GA_R1_REPORT.md"
UHMI_FILES = [
    FREEZE_DOC,
    ROOT / "UHMI_GA_R1_UCONSOLE_WORKSPACE_MENU_AND_INFORMATION_ARCHITECTURE.md",
    ROOT / "UHMI_GA_R1_DATA_FLOW_AND_BOUNDARY_SPEC.md",
    ROOT / "UHMI_GA_R1_ENGINEER_OPERATOR_CUSTOMER_WORKFLOWS.md",
    ROOT / "UHMI_GA_R1_CONTROL_CAPABILITY_FUTURE_GUARDRAILS.md",
    REPORT,
    REGISTRY,
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r1/uhmi-uconsole-evidence-files.txt",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r1/uhmi-uconsole-route-menu-references.txt",
    ROOT / "AN_VANTARIS_ONE/registries/uhmi-ga-r1/uhmi-risk-scan.txt",
    ROOT / "scripts/validation/validate-uhmi-ga-r1-uconsole-workspace-readonly-foundation.py",
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
    for path in UHMI_FILES:
        if not path.exists():
            fail(f"Missing UHMI file: {path.relative_to(ROOT)}")
    ok("All UHMI files exist")

    registry = load_json(REGISTRY)
    ok("Registry JSON parses")

    for path in [FREEZE_DOC, REPORT, REGISTRY]:
        if PASS_MARKER not in read_text(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("PASS marker exists in freeze doc, report, and registry")

    if registry.get("platform") != "VANTARIS_ONE":
        fail("Registry platform must equal VANTARIS_ONE")
    if registry.get("capability") != "UHMI":
        fail("Registry capability must equal UHMI")
    if registry.get("placement") != "UConsole / UHMI Workspace":
        fail("Registry placement must equal UConsole / UHMI Workspace")
    if registry.get("releaseScope") != "READ_ONLY_FOUNDATION_FREEZE":
        fail("Registry releaseScope must equal READ_ONLY_FOUNDATION_FREEZE")
    ok("Registry platform, capability, placement, and releaseScope are correct")

    combined = "\n".join(read_text(path) for path in UHMI_FILES if path.suffix in {".md", ".json", ".txt"})
    required_phrases = [
        "UHMI = Unified Human-Machine Interface",
        "UConsole / UHMI Workspace",
        "not a SCADA replacement",
        "not an independent HMI server",
        "read-only",
        "No direct device control",
        "No direct DB write",
        "No bypass CODE",
    ]
    for phrase in required_phrases:
        if phrase not in combined:
            fail(f"Required phrase missing: {phrase}")
    ok("Required UHMI phrases exist")

    for phrase in [
        "Device/System -> EDGE -> LINK -> CODE -> UConsole/UHMI",
        "UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device",
    ]:
        if phrase not in combined:
            fail(f"Required flow missing: {phrase}")
    ok("Data flow and future controlled action path exist")

    forbidden_terms = [".env", "secrets", "node_modules", "dist/", "build/", ".runtime", "__pycache__", "._"]
    scan_text = "\n".join(read_text(path) for path in UHMI_FILES if path != Path(__file__).resolve())
    for term in forbidden_terms:
        if term in scan_text:
            fail(f"Forbidden term found across UHMI files: {term}")
    ok("Forbidden scan empty across UHMI files")

    for marker in [
        "ONE_DESIGN_R1_FULL_PRODUCT_DESIGN_BLUEPRINT_PASS",
        "ONE_MODULE_GA_WAVE_R1_CONSOLIDATED_FREEZE_PASS",
    ]:
        if not marker_exists(marker):
            fail(f"Required prior PASS marker missing: {marker}")
    ok("ONE-DESIGN-R1 and ONE-MODULE-GA-WAVE-R1 PASS markers exist")

    run_validator(ROOT / "scripts/validation/validate-one-package-route-enforcement.py", "Package route enforcement", "ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS")
    run_validator(ROOT / "scripts/validation/validate-one-boundaries.py", "Boundary baseline", "ONE_BOUNDARY_BASELINE_PASS")

    print(PASS_MARKER)


if __name__ == "__main__":
    main()
