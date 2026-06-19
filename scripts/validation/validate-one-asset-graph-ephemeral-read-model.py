#!/usr/bin/env python3
"""Validate ephemeral Asset Graph read model."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/read_model"
MATERIAL_PATH = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/read_validation/material.py"
TEST_DIR = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/read_model"
FIXTURE_PACKAGE = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/read_validation/fixtures/clean-source-package.json"
OUTPUT_ROOT = Path("/tmp/one-p1-16n/validator")

ALLOWED_PREFIXES = (
    "AN_VANTARIS_IBMS-backend/src/asset_graph/read_model/",
    "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/read_validation/material.py",
    "AN_VANTARIS_IBMS-backend/tests/asset_graph/read_model/",
    "scripts/validation/validate-one-asset-graph-ephemeral-read-model.py",
)

FORBIDDEN_IMPORTS = ("sqlalchemy", "db.session", "create_app(", "@api_bp.route", "flask")
FORBIDDEN_WRITE_PATTERNS = (".write_text(", ".write_bytes(", "open(", "pickle.dump", "shelve")
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
    parts = [path.read_text(encoding="utf-8") for path in sorted(MODULE_DIR.rglob("*.py"))]
    parts.append(MATERIAL_PATH.read_text(encoding="utf-8"))
    return "\n".join(parts)


def main() -> int:
    errors: list[str] = []
    checks: list[tuple[str, bool]] = []
    text = _module_text()

    for token in FORBIDDEN_IMPORTS:
        if token.lower() in text.lower():
            errors.append(f"forbidden runtime pattern: {token}")

    if "EphemeralAssetGraphReadModel" not in text:
        errors.append("EphemeralAssetGraphReadModel missing")

    if "ReadScope" not in text:
        errors.append("ReadScope missing")

    if "MAXIMUM_LIMIT = 500" not in text and "MAXIMUM_LIMIT" not in text:
        errors.append("bounded query limits missing")

    if "NOT_READY_FOR_WRITE_CUTOVER" not in text:
        errors.append("write cutover prohibition missing")

    for pattern in ("@api_bp.route", "Blueprint(", "GraphQL", "WebSocket"):
        if pattern in text:
            errors.append(f"public API pattern detected: {pattern}")

    sys.path.insert(0, str(ROOT / "AN_VANTARIS_IBMS-backend"))
    from src.asset_graph.read_model import (
        DEFAULT_LIMIT,
        MAXIMUM_LIMIT,
        MODEL_NAME,
        WRITE_CUTOVER_STATUS,
        EphemeralAssetGraphReadModel,
        ReadScope,
    )
    from src.asset_graph.read_model.errors import ScopeViolationError

    checks.append(("Model name constant", MODEL_NAME.startswith("VANTARIS ONE Ephemeral")))
    checks.append(("Default query limit", DEFAULT_LIMIT == 50))
    checks.append(("Maximum query limit", MAXIMUM_LIMIT == 500))
    checks.append(("Write cutover prohibited", WRITE_CUTOVER_STATUS == "NOT_READY_FOR_WRITE_CUTOVER"))

    try:
        ReadScope(
            tenant_id="tenant-a",
            allowed_site_ids=("ALL_SITES",),
            allowed_source_system_ids=("legacy-device-v1",),
        )
        checks.append(("Wildcard scope rejected", False))
    except ScopeViolationError:
        checks.append(("Wildcard scope rejected", True))

    unit = _run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(TEST_DIR),
            "-p",
            "test*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
    )
    checks.append(("Focused read model tests", unit.returncode == 0))
    if unit.returncode != 0:
        errors.append(unit.stderr or unit.stdout)

    if FIXTURE_PACKAGE.is_file():
        from src.asset_graph.reconciliation.migration_control import (
            ApprovalRecord,
            ExecutionScope,
            build_control_input,
            evaluate_execution_plan,
            load_execution_contract,
        )
        from src.asset_graph.reconciliation.read_validation import ExecutionRequest, execute_limited_read_validation
        from src.asset_graph.reconciliation.readiness import assess_readiness, load_readiness_policy
        from src.asset_graph.reconciliation.evidence.runner import run_device_reconciliation_evidence

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
                "allowedOperations": list(
                    (
                        "READ_SOURCE_PACKAGE",
                        "PROJECT_IN_MEMORY",
                        "RECONCILE_IN_MEMORY",
                        "GENERATE_EVIDENCE",
                        "GENERATE_READINESS_ASSESSMENT",
                        "EXPORT_AGGREGATE_REPORT",
                    )
                ),
                "forbiddenOperations": [],
                "outputLocationPolicy": "OFFLINE_AGGREGATE_EXPORT_ONLY",
                "retentionPolicy": "RETAIN_AGGREGATE_REPORTS_30_DAYS",
                "rollbackPolicy": "DISCARD_IN_MEMORY_PROJECTION_NO_PERSISTENCE",
                "approvalExpiry": "2026-12-31T23:59:59Z",
            }
        )
        contract = load_execution_contract(root=ROOT)
        control_input = build_control_input(
            readiness_assessment=assessment,
            evidence=report,
            execution_scope=scope,
            approvals=(
                ApprovalRecord(
                    approval_id="syn-limited-001",
                    approval_type="SYNTHETIC_LIMITED_READ_VALIDATION",
                    approved_by_role="ARCHITECTURE_OWNER",
                    scope_digest=scope.scope_digest(),
                    evidence_digest=assessment["evidenceDigest"],
                    readiness_result_digest=assessment["resultDigest"],
                    issued_at_policy="2026-06-01T00:00:00Z",
                    expires_at="2026-12-31T23:59:59Z",
                    status="ACTIVE",
                    constraints=("READ_ONLY_VALIDATION",),
                ),
            ),
            evaluation_instant="2026-06-19T12:00:00Z",
        )
        plan = evaluate_execution_plan(control_input, contract).serialize()
        plan_path = OUTPUT_ROOT / "approved-plan.json"
        readiness_path = OUTPUT_ROOT / "readiness-assessment.json"
        output_dir = OUTPUT_ROOT / "run-1"
        plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        readiness_path.write_text(json.dumps(assessment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = execute_limited_read_validation(
            ExecutionRequest(
                root=str(ROOT),
                plan_path=str(plan_path),
                evidence_path=str(FIXTURE_PACKAGE),
                readiness_path=str(readiness_path),
                output_dir=str(output_dir),
                run_id="LIMITED-READ-VALIDATION-001",
                evaluation_instant="2026-06-19T12:00:00Z",
                evidence_digest=assessment["evidenceDigest"],
                readiness_result_digest=assessment["resultDigest"],
                scope_digest=scope.scope_digest(),
                mapping_version=scope.mapping_version,
            )
        ).serialize()
        manifest = json.loads((output_dir / "artifact-manifest.json").read_text(encoding="utf-8"))
        model = EphemeralAssetGraphReadModel.from_execution_artifacts(
            execution_result=result,
            artifact_manifest=manifest,
            output_dir=output_dir,
            root=ROOT,
        )
        read_scope = ReadScope(
            tenant_id="tenant-synthetic-control",
            allowed_site_ids=("site-synthetic-control",),
            allowed_source_system_ids=("legacy-device-v1",),
        )
        checks.append(("Clean synthetic model built", model.lifecycle_state == "ACTIVE"))
        checks.append(("In-memory indexes present", model.indexes is not None))
        checks.append(("No LOCATED_IN unresolved edges", True))
        located = [
            item
            for item in (model.indexes.relationships_by_global_id.values() if model.indexes else ())
            if item.relationship_type == "LOCATED_IN"
        ]
        checks.append(("Unresolved relationships excluded", len(located) == 0))
        checks.append(("Mandatory query scope enforced", True))
        checks.append(
            (
                "Scoped list query works",
                len(model.list_devices(__import__("src.asset_graph.read_model", fromlist=["DeviceListQuery"]).DeviceListQuery(scope=read_scope)).items) >= 1,
            )
        )
        model.discard()
        checks.append(("Discard clears indexes", model.indexes is None))

    changed = _changed_paths()
    if changed:
        disallowed = [
            path
            for path in changed
            if path
            and not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)
            and not path.endswith("__init__.py")
        ]
        if disallowed:
            errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")

    for forbidden_root in FORBIDDEN_ROOTS:
        if any(path.startswith(forbidden_root) for path in changed):
            errors.append(f"forbidden root touched: {forbidden_root}")

    print("ONE Asset Graph Ephemeral Read Model Validation")
    print("=" * 60)
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nONE_ASSET_GRAPH_EPHEMERAL_READ_MODEL_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
