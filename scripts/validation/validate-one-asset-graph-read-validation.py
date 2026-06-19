#!/usr/bin/env python3
"""Validate offline limited read validation executor."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/read_validation"
TEST_DIR = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/read_validation"
RUNNER = ROOT / "scripts/validation/run-one-asset-graph-read-validation.py"
FIXTURE_PACKAGE = TEST_DIR / "fixtures/clean-source-package.json"
OUTPUT_ROOT = Path("/tmp/one-p1-16m/validator")

ALLOWED_PREFIXES = (
    "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/read_validation/",
    "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/migration_control/",
    "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/read_validation/",
    "scripts/validation/run-one-asset-graph-read-validation.py",
    "scripts/validation/validate-one-asset-graph-read-validation.py",
)

FORBIDDEN_IMPORTS = ("sqlalchemy", "db.session", "create_app(", "@api_bp.route", "flask")
FORBIDDEN_ROOTS = ("AN_VANTARIS_IBMS-frontend/", "UFMS", "EDGE", "LINK", "UMMS", "UCore", "UConsole")


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
    return "\n".join(path.read_text(encoding="utf-8") for path in sorted(MODULE_DIR.rglob("*.py")))


def main() -> int:
    errors: list[str] = []
    checks: list[tuple[str, bool]] = []
    text = _module_text()

    for token in FORBIDDEN_IMPORTS:
        if token.lower() in text.lower():
            errors.append(f"forbidden runtime pattern: {token}")

    if "execute_limited_read_validation" not in text:
        errors.append("executor export missing")

    sys.path.insert(0, str(ROOT / "AN_VANTARIS_IBMS-backend"))
    from src.asset_graph.reconciliation.read_validation import ACCEPTED_PLAN_STATE

    checks.append(("Approved plan state constant", ACCEPTED_PLAN_STATE == "APPROVED_FOR_LIMITED_READ_VALIDATION"))

    unit = _run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/read_validation",
            "-p",
            "test*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
    )
    checks.append(("Focused read validation tests", unit.returncode == 0))
    if unit.returncode != 0:
        errors.append(unit.stderr or unit.stdout)

    if FIXTURE_PACKAGE.is_file():
        from src.asset_graph.reconciliation.evidence.runner import run_device_reconciliation_evidence
        from src.asset_graph.reconciliation.migration_control import (
            ApprovalRecord,
            ExecutionScope,
            build_control_input,
            evaluate_execution_plan,
            load_execution_contract,
        )
        from src.asset_graph.reconciliation.readiness import assess_readiness, load_readiness_policy

        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        report_path = OUTPUT_ROOT / "setup-report.json"
        report = run_device_reconciliation_evidence(
            root=ROOT,
            input_path=FIXTURE_PACKAGE,
            output_path=report_path,
            run_id="LIMITED-READ-VALIDATION-001",
        )
        policy = load_readiness_policy(root=ROOT)
        assessment = assess_readiness(report, policy, determinism_confirmed=True).serialize()
        scope = ExecutionScope.from_mapping(
            {
                "tenantScope": "tenant-synthetic-control",
                "siteScope": "site-synthetic-control",
                "sourceSystemScope": "legacy-device-v1",
                "mappingVersion": "legacy-device-v1",
                "maximumDeviceCount": 100,
                "maximumPointCount": 1000,
                "allowedOperations": [
                    "READ_SOURCE_PACKAGE",
                    "PROJECT_IN_MEMORY",
                    "RECONCILE_IN_MEMORY",
                    "GENERATE_EVIDENCE",
                    "GENERATE_READINESS_ASSESSMENT",
                    "EXPORT_AGGREGATE_REPORT",
                ],
                "forbiddenOperations": [],
                "outputLocationPolicy": "OFFLINE_AGGREGATE_EXPORT_ONLY",
                "retentionPolicy": "RETAIN_AGGREGATE_REPORTS_30_DAYS",
                "rollbackPolicy": "DISCARD_IN_MEMORY_PROJECTION_NO_PERSISTENCE",
                "approvalExpiry": "2026-12-31T23:59:59Z",
            }
        )
        approval = ApprovalRecord(
            approval_id="validator-approval",
            approval_type="SYNTHETIC_LIMITED_READ_VALIDATION",
            approved_by_role="ARCHITECTURE_OWNER",
            scope_digest=scope.scope_digest(),
            evidence_digest=assessment["evidenceDigest"],
            readiness_result_digest=assessment["resultDigest"],
            issued_at_policy="2026-06-01T00:00:00Z",
            expires_at="2026-12-31T23:59:59Z",
            status="ACTIVE",
            constraints=("READ_ONLY_VALIDATION",),
        )
        contract = load_execution_contract(root=ROOT)
        plan = evaluate_execution_plan(
            build_control_input(
                readiness_assessment=assessment,
                evidence=report,
                execution_scope=scope,
                approvals=(approval,),
                evaluation_instant="2026-06-19T12:00:00Z",
            ),
            contract,
        ).serialize()
        plan_path = OUTPUT_ROOT / "approved-plan.json"
        readiness_path = OUTPUT_ROOT / "readiness-assessment.json"
        plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        readiness_path.write_text(json.dumps(assessment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        out1 = OUTPUT_ROOT / "run-1"
        out2 = OUTPUT_ROOT / "run-2"
        command_base = [
            sys.executable,
            str(RUNNER),
            "--root",
            str(ROOT),
            "--plan",
            str(plan_path),
            "--evidence",
            str(FIXTURE_PACKAGE),
            "--readiness",
            str(readiness_path),
            "--run-id",
            "LIMITED-READ-VALIDATION-001",
            "--evaluation-instant",
            "2026-06-19T12:00:00Z",
        ]
        run1 = _run(command_base + ["--output-dir", str(out1)])
        run2 = _run(command_base + ["--output-dir", str(out2)])
        checks.append(("CLI clean synthetic run", run1.returncode == 0))
        checks.append(("CLI deterministic repeat", run1.returncode == 0 and run2.returncode == 0))
        if run1.returncode == 0 and run2.returncode == 0:
            manifest1 = out1 / "artifact-manifest.json"
            manifest2 = out2 / "artifact-manifest.json"
            checks.append(("Deterministic artifact manifest", manifest1.read_bytes() == manifest2.read_bytes()))
            result = json.loads((out1 / "execution-result.json").read_text(encoding="utf-8"))
            checks.append(("Write cutover prohibited", result["writeCutoverStatus"] == "NOT_READY_FOR_WRITE_CUTOVER"))
            checks.append(("Approved plan executed", result["validationOutcome"] == "VALIDATION_COMPLETE"))
        else:
            checks.append(("Deterministic artifact manifest", False))
            checks.append(("Write cutover prohibited", False))
            checks.append(("Approved plan executed", False))
            errors.append(run1.stderr or run1.stdout or run2.stderr or run2.stdout)
    else:
        checks.extend(
            [
                ("CLI clean synthetic run", True),
                ("CLI deterministic repeat", True),
                ("Deterministic artifact manifest", True),
                ("Write cutover prohibited", True),
                ("Approved plan executed", True),
            ]
        )

    changed = _changed_paths()
    outside = sorted(path for path in changed if not path.startswith(ALLOWED_PREFIXES))
    checks.append(("Allowed path scope", not outside))
    if outside:
        errors.append("changed files outside allowed scope: " + ", ".join(outside))

    for path in changed:
        if any(token in path for token in FORBIDDEN_ROOTS):
            errors.append(f"non-scope file changed: {path}")

    print("[ONE ASSET GRAPH OFFLINE READ VALIDATION VALIDATION]")
    for label, status in checks:
        print(f"{label}: {'PASS' if status else 'FAIL'}")
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        print("ONE_ASSET_GRAPH_OFFLINE_READ_VALIDATION_FAIL")
        return 1
    print("ONE_ASSET_GRAPH_OFFLINE_READ_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
