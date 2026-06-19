#!/usr/bin/env python3
"""Validate offline legacy device reconciliation evidence runner."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts/validation/run-one-device-reconciliation-evidence.py"
MODULE = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/evidence/runner.py"
TEST_FILE = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/evidence/test_device_reconciliation_evidence_runner.py"
SAMPLE_DIR = ROOT / "AN_VANTARIS_ONE/evidence/device-reconciliation/sample"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/evidence/",
    "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/evidence/",
    "AN_VANTARIS_ONE/evidence/device-reconciliation/sample/",
    "scripts/validation/run-one-device-reconciliation-evidence.py",
    "scripts/validation/validate-one-device-reconciliation-evidence.py",
)

REQUIRED_SAMPLES = (
    "minimal-valid-device.json",
    "valid-device-with-points.json",
    "identity-collision.json",
    "scope-mismatch.json",
    "missing-required-field.json",
    "ambiguous-standard-field.json",
    "unresolved-parent.json",
    "prohibited-field-rejected.json",
)


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)


def _changed_paths() -> set[str]:
    commands = (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    )
    paths: set[str] = set()
    for command in commands:
        paths.update(_run(command).stdout.splitlines())
    if not paths:
        paths.update(_run(["git", "diff", "--name-only", "HEAD^", "HEAD"]).stdout.splitlines())
    return {path for path in paths if path}


def _check_line(item: str, errors: list[str], text: str, *, invert: bool = False) -> bool:
    present = item in text
    if invert:
        if present:
            errors.append(f"forbidden pattern found: {item}")
        return not present
    if not present:
        errors.append(f"required pattern missing: {item}")
    return present


def _run_sample(sample_name: str, output_path: Path, run_id: str, extra: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(RUNNER),
        "--root",
        str(ROOT),
        "--input",
        f"AN_VANTARIS_ONE/evidence/device-reconciliation/sample/{sample_name}",
        "--output",
        str(output_path),
        "--run-id",
        run_id,
        "--format",
        "json",
    ]
    if extra:
        command.extend(extra)
    return _run(command)


def main() -> int:
    errors: list[str] = []
    checks: list[tuple[str, bool]] = []
    if not MODULE.is_file() or not RUNNER.is_file() or not TEST_FILE.is_file():
        errors.append("runner module, CLI runner, or tests missing")
    module_text = MODULE.read_text(encoding="utf-8")
    _check_line("LegacyDeviceReadCompatibilityFacade", errors, module_text)
    _check_line("DeviceProjectionReconciliationService", errors, module_text)
    _check_line("sqlalchemy", errors, module_text.lower(), invert=True)
    _check_line("__tablename__", errors, module_text, invert=True)
    _check_line("@api_bp.route", errors, module_text, invert=True)
    _check_line("DEFAULT_CUTOVER_DECISION", errors, module_text)

    for sample_name in REQUIRED_SAMPLES:
        sample_path = SAMPLE_DIR / sample_name
        if not sample_path.is_file():
            errors.append(f"missing sample: {sample_name}")
            continue
        sample_text = sample_path.read_text(encoding="utf-8")
        if any(token in sample_text.lower() for token in ("real_customer", "prod-", "10.", "172.16.", "192.168.")):
            errors.append(f"sample may not be synthetic: {sample_name}")
        _check_line("VANTARIS ONE Legacy Device Reconciliation Evidence Package", errors, sample_text)

    out1 = Path("/tmp/device-reconciliation-evidence-validator-1.json")
    out2 = Path("/tmp/device-reconciliation-evidence-validator-2.json")
    run1 = _run_sample("valid-device-with-points.json", out1, "VALIDATOR-RUN-001")
    run2 = _run_sample("valid-device-with-points.json", out2, "VALIDATOR-RUN-001")
    deterministic = run1.returncode == 0 and run2.returncode == 0 and out1.read_bytes() == out2.read_bytes()
    checks.append(("Deterministic evidence", deterministic))
    if not deterministic:
        errors.append("deterministic sample run mismatch")

    blocker_run = _run_sample("identity-collision.json", Path("/tmp/device-reconciliation-evidence-blocker.json"), "VALIDATOR-RUN-BLOCKER", ["--fail-on-blocker"])
    checks.append(("Blocker preservation", blocker_run.returncode != 0))
    if blocker_run.returncode == 0:
        errors.append("identity collision sample did not fail with --fail-on-blocker")

    review_run = _run_sample("ambiguous-standard-field.json", Path("/tmp/device-reconciliation-evidence-review.json"), "VALIDATOR-RUN-REVIEW", ["--fail-on-review"])
    checks.append(("Review preservation", review_run.returncode != 0))
    if review_run.returncode == 0:
        errors.append("review sample did not fail with --fail-on-review")

    check_match = _run(
        [
            sys.executable,
            str(RUNNER),
            "--root",
            str(ROOT),
            "--input",
            "AN_VANTARIS_ONE/evidence/device-reconciliation/sample/valid-device-with-points.json",
            "--output",
            str(out1),
            "--run-id",
            "VALIDATOR-RUN-001",
            "--format",
            "json",
            "--check",
            str(out2),
        ]
    )
    checks.append(("Semantic check mode", check_match.returncode == 0))
    if check_match.returncode != 0:
        errors.append("runner --check failed on identical evidence")

    changed = _changed_paths()
    outside = sorted(path for path in changed if not path.startswith(ALLOWED_PREFIXES))
    scope_ok = not outside
    checks.append(("Allowed path scope", scope_ok))
    if outside:
        errors.append("changed files outside allowed scope: " + ", ".join(outside))

    checks.extend(
        [
            ("Offline boundary", "create_app(" not in module_text and "db.session" not in module_text),
            ("Input sanitation", "PROHIBITED_KEY" in module_text and "PROHIBITED_VALUE" in module_text),
            ("Facade reuse", "LegacyDeviceReadCompatibilityFacade" in module_text),
            ("Reconciliation reuse", "DeviceProjectionReconciliationService" in module_text),
            ("Credential exclusion", "PROHIBITED_FIELD_PRESENT" in module_text),
            ("Telemetry exclusion", "telemetry" in module_text.lower()),
            ("No database access", "sqlalchemy" not in module_text.lower()),
            ("No persistence writes", "write_text(" in module_text),
            ("Write-cutover prohibition", True),
        ]
    )
    if out1.is_file():
        sample_payload = json.loads(out1.read_text(encoding="utf-8"))
        if sample_payload.get("cutoverDecision") == "READY_FOR_WRITE_CUTOVER":
            errors.append("output declared READY_FOR_WRITE_CUTOVER")
            checks = [
                (label, False) if label == "Write-cutover prohibition" else (label, status)
                for label, status in checks
            ]

    print("[ONE DEVICE RECONCILIATION EVIDENCE VALIDATION]")
    labels = [
        "Offline boundary",
        "Input sanitation",
        "Facade reuse",
        "Reconciliation reuse",
        "Credential exclusion",
        "Telemetry exclusion",
        "Deterministic evidence",
        "Blocker preservation",
        "Review preservation",
        "No database access",
        "No persistence writes",
        "Write-cutover prohibition",
        "Allowed path scope",
    ]
    check_map = {label: status for label, status in checks}
    for label in labels:
        print(f"{label}: {'PASS' if check_map.get(label) else 'FAIL'}")
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        print("ONE_DEVICE_RECONCILIATION_EVIDENCE_FAIL")
        return 1
    print("ONE_DEVICE_RECONCILIATION_EVIDENCE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
