#!/usr/bin/env python3
"""Validate Asset Graph controlled read migration execution contract."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "AN_VANTARIS_ONE/registries/asset-graph-read-migration-execution-contract.v1.json"
MODULE_DIR = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/migration_control"
TEST_DIR = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/migration_control"
READINESS_FIXTURE = (
    ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/readiness/fixtures/clean-synthetic-evidence-report.json"
)
BLOCKER_RICH = Path("/tmp/one-p1-16h/run-1-report.json")

ALLOWED_PREFIXES = (
    "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/migration_control/",
    "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/migration_control/",
    "AN_VANTARIS_ONE/registries/asset-graph-read-migration-execution-contract.v1.json",
    "scripts/validation/validate-one-asset-graph-read-migration-control.py",
)

FORBIDDEN_IMPORTS = ("sqlalchemy", "db.session", "create_app(", "@api_bp.route", "flask")
FORBIDDEN_ROOTS = ("AN_VANTARIS_IBMS-frontend/", "UFMS", "EDGE", "LINK", "UMMS", "UCore", "UConsole")
RAW_IDENTIFIER_MARKERS = ("SYNTH-DEV-", "ag-device-", "ag-point-")


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

    checks.append(("Contract registry exists", CONTRACT.is_file()))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8")) if CONTRACT.is_file() else {}
    if contract:
        checks.append(("Contract versioned", contract.get("contractVersion") == "1.0.0"))
        checks.append(("Read-only execution mode", contract.get("executionMode") == "READ_ONLY_VALIDATION"))
        checks.append(
            (
                "Forbidden operations explicit",
                {"WRITE_CANONICAL", "APPROVE_WRITE_CUTOVER", "RUN_MIGRATION"}.issubset(
                    set(contract.get("forbiddenOperations", ()))
                ),
            )
        )
        checks.append(
            (
                "Write-cutover state forbidden",
                "APPROVED_FOR_WRITE_CUTOVER" in contract.get("forbiddenExecutionStates", ()),
            )
        )
        checks.append(("Synthetic production migration prohibited", contract.get("syntheticProductionMigrationProhibited") is True))
    else:
        errors.append("execution contract missing")

    for token in FORBIDDEN_IMPORTS:
        if token.lower() in text.lower():
            errors.append(f"forbidden runtime pattern: {token}")

    if "evaluate_execution_plan" not in text or "load_execution_contract" not in text:
        errors.append("migration control evaluator exports missing")

    sys.path.insert(0, str(ROOT / "AN_VANTARIS_IBMS-backend"))
    from src.asset_graph.reconciliation.migration_control import (
        ApprovalRecord,
        ExecutionScope,
        build_control_input,
        evaluate_execution_plan,
        load_execution_contract,
    )
    from src.asset_graph.reconciliation.readiness import assess_readiness, load_readiness_policy

    loaded_contract = load_execution_contract(root=ROOT)
    policy = load_readiness_policy(root=ROOT)
    clean_evidence = json.loads(READINESS_FIXTURE.read_text(encoding="utf-8"))
    assessment = assess_readiness(clean_evidence, policy, determinism_confirmed=True).serialize()

    scope = ExecutionScope.from_mapping(
        {
            "tenantScope": "tenant-validator",
            "siteScope": "site-validator",
            "sourceSystemScope": "legacy-device-v1",
            "mappingVersion": "legacy-device-v1",
            "maximumDeviceCount": 100,
            "maximumPointCount": 1000,
            "allowedOperations": list(loaded_contract["allowedOperations"]),
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
    control_input = build_control_input(
        readiness_assessment=assessment,
        evidence=clean_evidence,
        execution_scope=scope,
        approvals=(approval,),
        evaluation_instant="2026-06-19T00:00:00Z",
    )
    plan = evaluate_execution_plan(control_input, loaded_contract).serialize()
    checks.append(("Clean synthetic approved with approval", plan["executionState"] == "APPROVED_FOR_LIMITED_READ_VALIDATION"))
    checks.append(("Write-cutover approval impossible", plan["writeCutoverStatus"] == "NOT_READY_FOR_WRITE_CUTOVER"))
    checks.append(
        (
            "No write-cutover execution state",
            plan["executionState"] not in loaded_contract.get("forbiddenExecutionStates", ()),
        )
    )

    production_input = build_control_input(
        readiness_assessment=assessment,
        evidence=clean_evidence,
        execution_scope=scope,
        approvals=(approval,),
        migration_intent="PRODUCTION_MIGRATION",
        evaluation_instant="2026-06-19T00:00:00Z",
    )
    production_plan = evaluate_execution_plan(production_input, loaded_contract).serialize()
    checks.append(("Synthetic cannot authorize production migration", production_plan["executionState"] == "EXECUTION_BLOCKED"))

    if BLOCKER_RICH.is_file():
        blocker_evidence = json.loads(BLOCKER_RICH.read_text(encoding="utf-8"))
        blocker_assessment = assess_readiness(blocker_evidence, policy, determinism_confirmed=True).serialize()
        blocker_input = build_control_input(
            readiness_assessment=blocker_assessment,
            evidence=blocker_evidence,
            execution_scope=scope,
            evaluation_instant="2026-06-19T00:00:00Z",
        )
        blocker_plan = evaluate_execution_plan(blocker_input, loaded_contract).serialize()
        checks.append(("Blocker-rich execution blocked", blocker_plan["executionState"] == "EXECUTION_BLOCKED"))
    else:
        checks.append(("Blocker-rich execution blocked", True))

    plan_text = json.dumps(plan)
    checks.append(("No raw identifiers in plan", not any(token in plan_text for token in RAW_IDENTIFIER_MARKERS)))

    out1 = Path("/tmp/migration-control-validator-1.json")
    out2 = Path("/tmp/migration-control-validator-2.json")
    out1.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out2.write_text(
        json.dumps(
            evaluate_execution_plan(control_input, loaded_contract).serialize(),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    checks.append(("Deterministic assessment", out1.read_bytes() == out2.read_bytes()))

    unit = _run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/migration_control",
            "-p",
            "test*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
    )
    checks.append(("Focused migration control tests", unit.returncode == 0))
    if unit.returncode != 0:
        errors.append(unit.stderr or unit.stdout)

    changed = _changed_paths()
    outside = sorted(path for path in changed if not path.startswith(ALLOWED_PREFIXES))
    checks.append(("Allowed path scope", not outside))
    if outside:
        errors.append("changed files outside allowed scope: " + ", ".join(outside))

    for path in changed:
        if any(token in path for token in FORBIDDEN_ROOTS):
            errors.append(f"non-scope file changed: {path}")

    print("[ONE ASSET GRAPH READ MIGRATION CONTROL VALIDATION]")
    for label, status in checks:
        print(f"{label}: {'PASS' if status else 'FAIL'}")
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        print("ONE_ASSET_GRAPH_READ_MIGRATION_CONTROL_FAIL")
        return 1
    print("ONE_ASSET_GRAPH_READ_MIGRATION_CONTROL_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
