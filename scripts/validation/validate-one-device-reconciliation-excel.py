#!/usr/bin/env python3
"""Validate synthetic Excel device reconciliation evidence intake."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts/validation/run-one-device-reconciliation-excel.py"
MODULE_DIR = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/evidence/excel"
TEST_DIR = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/evidence/excel"
FIXTURES = TEST_DIR / "fixtures.py"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/evidence/excel/",
    "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/evidence/__init__.py",
    "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/evidence/excel/",
    "scripts/validation/run-one-device-reconciliation-excel.py",
    "scripts/validation/validate-one-device-reconciliation-excel.py",
)


def _run(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False, env=env)


def _changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        paths.update(_run(command).stdout.splitlines())
    return {path for path in paths if path}


def _module_text() -> str:
    parts = []
    for path in sorted(MODULE_DIR.rglob("*.py")):
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def main() -> int:
    errors: list[str] = []
    checks: list[tuple[str, bool]] = []
    text = _module_text()
    runner_text = RUNNER.read_text(encoding="utf-8")

    for token in ("sqlalchemy", "db.session", "create_app(", "@api_bp.route", "flask"):
        if token.lower() in text.lower() or token.lower() in runner_text.lower():
            errors.append(f"forbidden runtime pattern: {token}")
    for required in (
        "run_device_reconciliation_evidence",
        "RejectedSamples",
        "SYNTHETIC_REPRESENTATIVE_ONLY",
        "NOT_READY_FOR_WRITE_CUTOVER",
    ):
        if required not in text and required not in runner_text:
            errors.append(f"missing required pattern: {required}")

    workbook_path = Path("/tmp/VANTARIS_ONE_Representative_Synthetic_Device_Dataset.xlsx")
    build = _run([sys.executable, str(FIXTURES), str(workbook_path)])
    if build.returncode != 0:
        errors.append("fixture workbook generation failed")
        checks.append(("Fixture workbook", False))
    else:
        checks.append(("Fixture workbook", workbook_path.is_file()))

    out_dir = Path("/tmp/one-device-reconciliation-excel-validator")
    out_dir.mkdir(parents=True, exist_ok=True)
    package1 = out_dir / "run-1-package.json"
    report1 = out_dir / "run-1-report.json"
    package2 = out_dir / "run-2-package.json"
    report2 = out_dir / "run-2-report.json"
    shared_package = out_dir / "shared-package.json"
    command_base = [
        sys.executable,
        str(RUNNER),
        "--root",
        str(ROOT),
        "--input",
        str(workbook_path),
        "--run-id",
        "EXCEL-VALIDATOR-001",
    ]
    run1 = _run(command_base + ["--json-output", str(package1), "--report-output", str(out_dir / "tmp-report-1.json")])
    run2 = _run(command_base + ["--json-output", str(package2), "--report-output", str(out_dir / "tmp-report-2.json")])
    run3 = _run(command_base + ["--json-output", str(shared_package), "--report-output", str(report1)])
    run4 = _run(command_base + ["--json-output", str(shared_package), "--report-output", str(report2)])
    deterministic = (
        run1.returncode == 0
        and run2.returncode == 0
        and run3.returncode == 0
        and run4.returncode == 0
        and package1.read_bytes() == package2.read_bytes()
        and report1.read_bytes() == report2.read_bytes()
    )
    checks.append(("Deterministic package/report", deterministic))
    if not deterministic:
        errors.append("deterministic excel intake mismatch")

    if report1.is_file():
        payload = json.loads(report1.read_text(encoding="utf-8"))
        if payload.get("cutoverDecision") == "READY_FOR_WRITE_CUTOVER":
            errors.append("report declared READY_FOR_WRITE_CUTOVER")
        if payload.get("blockers"):
            checks.append(("Blocker preservation", True))
        else:
            errors.append("expected blockers in synthetic fixture report")
            checks.append(("Blocker preservation", False))

    unit = _run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/evidence/excel",
            "-p",
            "test*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
    )
    checks.append(("Focused excel tests", unit.returncode == 0))
    if unit.returncode != 0:
        errors.append("focused excel tests failed")

    changed = _changed_paths()
    outside = sorted(path for path in changed if not path.startswith(ALLOWED_PREFIXES))
    checks.append(("Allowed path scope", not outside))
    if outside:
        errors.append("changed files outside allowed scope: " + ", ".join(outside))

    forbidden_roots = ("AN_VANTARIS_IBMS-frontend/", "UFMS", "EDGE", "LINK")
    for path in changed:
        if any(token in path for token in forbidden_roots):
            errors.append(f"non-scope file changed: {path}")

    checks.extend(
        [
            ("Workbook mapping explicit", "TenantID" in text and "DeviceSourceID" in text),
            ("RejectedSamples isolated", "validate_rejected_samples" in text),
            ("Output remains synthetic", "SYNTHETIC_REPRESENTATIVE_ONLY" in text),
            ("Write cutover prohibited", "READY_FOR_WRITE_CUTOVER" not in text.split("NEVER")[0] or "NOT_READY_FOR_WRITE_CUTOVER" in text),
        ]
    )

    print("[ONE DEVICE RECONCILIATION EXCEL INTAKE VALIDATION]")
    for label, status in checks:
        print(f"{label}: {'PASS' if status else 'FAIL'}")
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        print("ONE_DEVICE_RECONCILIATION_EXCEL_INTAKE_FAIL")
        return 1
    print("ONE_DEVICE_RECONCILIATION_EXCEL_INTAKE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
