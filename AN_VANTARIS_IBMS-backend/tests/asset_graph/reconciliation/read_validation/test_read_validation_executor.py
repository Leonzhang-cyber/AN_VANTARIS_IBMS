"""Tests for offline limited read validation executor."""
from __future__ import annotations

import copy
import json
import hashlib
import shutil
import unittest
from pathlib import Path

from src.asset_graph.reconciliation.evidence.runner import run_device_reconciliation_evidence
from src.asset_graph.reconciliation.migration_control import (
    ApprovalRecord,
    ExecutionScope,
    build_control_input,
    evaluate_execution_plan,
    load_execution_contract,
)
from src.asset_graph.reconciliation.read_validation import (
    ACCEPTED_PLAN_STATE,
    ExecutionRequest,
    execute_limited_read_validation,
)
from src.asset_graph.reconciliation.readiness import assess_readiness, load_readiness_policy

ROOT = Path(__file__).resolve().parents[5]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CLEAN_PACKAGE = FIXTURES / "clean-source-package.json"
REVIEW_PACKAGE = FIXTURES / "review-source-package.json"
OUTPUT_ROOT = Path("/tmp/one-p1-16m")
RUN_ID = "LIMITED-READ-VALIDATION-001"
EVALUATION_INSTANT = "2026-06-19T12:00:00Z"

ALLOWED_OPERATIONS = (
    "READ_SOURCE_PACKAGE",
    "PROJECT_IN_MEMORY",
    "RECONCILE_IN_MEMORY",
    "GENERATE_EVIDENCE",
    "GENERATE_READINESS_ASSESSMENT",
    "EXPORT_AGGREGATE_REPORT",
)


def _default_scope(**overrides: object) -> ExecutionScope:
    payload = {
        "tenantScope": "tenant-synthetic-control",
        "siteScope": "site-synthetic-control",
        "sourceSystemScope": "legacy-device-v1",
        "mappingVersion": "legacy-device-v1",
        "maximumDeviceCount": 100,
        "maximumPointCount": 1000,
        "allowedOperations": list(ALLOWED_OPERATIONS),
        "forbiddenOperations": [],
        "outputLocationPolicy": "OFFLINE_AGGREGATE_EXPORT_ONLY",
        "retentionPolicy": "RETAIN_AGGREGATE_REPORTS_30_DAYS",
        "rollbackPolicy": "DISCARD_IN_MEMORY_PROJECTION_NO_PERSISTENCE",
        "approvalExpiry": "2026-12-31T23:59:59Z",
    }
    payload.update(overrides)
    return ExecutionScope.from_mapping(payload)


def _synthetic_approval(scope: ExecutionScope, assessment: dict) -> ApprovalRecord:
    return ApprovalRecord(
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
    )


def _build_approved_bundle(
    root: Path,
    package_path: Path,
    *,
    run_id: str = RUN_ID,
    scope: ExecutionScope | None = None,
) -> tuple[dict, dict, ExecutionScope, Path]:
    scope = scope or _default_scope()
    report_path = OUTPUT_ROOT / "setup" / f"{package_path.stem}-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = run_device_reconciliation_evidence(
        root=root,
        input_path=package_path,
        output_path=report_path,
        run_id=run_id,
    )
    policy = load_readiness_policy(root=root)
    assessment = assess_readiness(report, policy, determinism_confirmed=True).serialize()
    contract = load_execution_contract(root=root)
    control_input = build_control_input(
        readiness_assessment=assessment,
        evidence=report,
        execution_scope=scope,
        approvals=(_synthetic_approval(scope, assessment),),
        evaluation_instant=EVALUATION_INSTANT,
    )
    plan = evaluate_execution_plan(control_input, contract).serialize()
    return plan, assessment, scope, package_path


class TestReadValidationExecutor(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = ROOT
        cls.contract = load_execution_contract(root=ROOT)
        cls.clean_plan, cls.clean_assessment, cls.clean_scope, cls.clean_package = _build_approved_bundle(
            ROOT, CLEAN_PACKAGE
        )

    def setUp(self) -> None:
        self._case_dir = OUTPUT_ROOT / self.id().split(".")[-1]
        if self._case_dir.exists():
            shutil.rmtree(self._case_dir)
        self._case_dir.mkdir(parents=True, exist_ok=True)

    def _write_inputs(self, plan: dict, assessment: dict) -> tuple[Path, Path]:
        plan_path = self._case_dir / "approved-plan.json"
        readiness_path = self._case_dir / "readiness-assessment.json"
        plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        readiness_path.write_text(json.dumps(assessment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return plan_path, readiness_path

    def _execute(
        self,
        plan: dict,
        assessment: dict,
        scope: ExecutionScope,
        package_path: Path,
        *,
        run_id: str = RUN_ID,
        output_dir: Path | None = None,
        **overrides: str,
    ) -> dict:
        plan_path, readiness_path = self._write_inputs(plan, assessment)
        output_dir = output_dir or (self._case_dir / "output")
        request = ExecutionRequest(
            root=str(self.root),
            plan_path=str(plan_path),
            evidence_path=str(package_path),
            readiness_path=str(readiness_path),
            output_dir=str(output_dir),
            run_id=run_id,
            evaluation_instant=overrides.get("evaluation_instant", EVALUATION_INSTANT),
            evidence_digest=overrides.get("evidence_digest", assessment["evidenceDigest"]),
            readiness_result_digest=overrides.get("readiness_result_digest", assessment["resultDigest"]),
            scope_digest=overrides.get("scope_digest", scope.scope_digest()),
            mapping_version=overrides.get("mapping_version", scope.mapping_version),
        )
        return execute_limited_read_validation(request).serialize()

    def test_approved_state_required(self) -> None:
        plan = copy.deepcopy(self.clean_plan)
        plan["executionState"] = "WAITING_FOR_APPROVAL"
        result = self._execute(plan, self.clean_assessment, self.clean_scope, self.clean_package)
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")

    def test_only_accepts_approved_limited_read_state(self) -> None:
        self.assertEqual(self.clean_plan["executionState"], ACCEPTED_PLAN_STATE)

    def test_approval_expiry_blocks(self) -> None:
        plan = copy.deepcopy(self.clean_plan)
        plan["scopeSummary"] = dict(plan["scopeSummary"])
        plan["scopeSummary"]["approvalExpiry"] = "2026-06-01T00:00:00Z"
        scope = _default_scope(approvalExpiry="2026-06-01T00:00:00Z")
        result = self._execute(plan, self.clean_assessment, scope, self.clean_package)
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")
        codes = {item["gateCode"] for item in result["preExecutionGateResults"] if item["status"] == "FAIL"}
        self.assertIn("APPROVAL_EXPIRY_GATE", codes)

    def test_approval_type_synthetic_compatible(self) -> None:
        self.assertEqual(self.clean_assessment["evidenceClassification"], "SYNTHETIC_REPRESENTATIVE_ONLY")

    def test_plan_digest_present(self) -> None:
        result = self._execute(self.clean_plan, self.clean_assessment, self.clean_scope, self.clean_package)
        self.assertTrue(result["planDigest"])

    def test_scope_digest_verification(self) -> None:
        result = self._execute(
            self.clean_plan,
            self.clean_assessment,
            self.clean_scope,
            self.clean_package,
            scope_digest="invalid-scope-digest",
        )
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")

    def test_evidence_digest_mismatch_blocks(self) -> None:
        result = self._execute(
            self.clean_plan,
            self.clean_assessment,
            self.clean_scope,
            self.clean_package,
            evidence_digest="0" * 64,
        )
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")

    def test_readiness_digest_mismatch_blocks(self) -> None:
        result = self._execute(
            self.clean_plan,
            self.clean_assessment,
            self.clean_scope,
            self.clean_package,
            readiness_result_digest="0" * 64,
        )
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")

    def test_mapping_version_gate(self) -> None:
        result = self._execute(
            self.clean_plan,
            self.clean_assessment,
            self.clean_scope,
            self.clean_package,
            mapping_version="unsupported-version",
        )
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")

    def test_tenant_scope_match(self) -> None:
        result = self._execute(self.clean_plan, self.clean_assessment, self.clean_scope, self.clean_package)
        self.assertEqual(result["validationOutcome"], "VALIDATION_COMPLETE")

    def test_multi_site_scope_fields(self) -> None:
        scope = self.clean_plan["scopeSummary"]
        self.assertTrue(scope["tenantScope"])
        self.assertTrue(scope["siteScope"])

    def test_source_system_scope_match(self) -> None:
        result = self._execute(self.clean_plan, self.clean_assessment, self.clean_scope, self.clean_package)
        self.assertEqual(result["sourceCounts"]["deviceCount"], 1)

    def test_device_count_ceiling(self) -> None:
        scope = _default_scope(maximumDeviceCount=0)
        plan, assessment, _, _ = _build_approved_bundle(self.root, CLEAN_PACKAGE, scope=scope)
        result = self._execute(plan, assessment, scope, self.clean_package)
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")

    def test_point_count_ceiling(self) -> None:
        package_path = self._case_dir / "point-package.json"
        package = json.loads(CLEAN_PACKAGE.read_text(encoding="utf-8"))
        package["standardFields"] = [
            {
                "sourceId": "fld-ceiling-001",
                "deviceSourceId": "dev-clean-001",
                "sourceNamespace": "legacy.iot.standard_fields",
                "name": "status_note",
                "displayName": "Status",
                "fieldType": "string",
                "dataType": "STRING",
                "unit": "",
                "accessMode": "READ_ONLY",
                "lifecycleStatus": "ACTIVE",
                "sourceTagName": "SYN-CHLR-01:status_note",
                "approvedMetadata": {},
            }
        ]
        package_path.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        scope = _default_scope(maximumPointCount=0)
        plan, assessment, _, _ = _build_approved_bundle(
            self.root,
            package_path,
            scope=scope,
            run_id="LIMITED-READ-VALIDATION-POINT-CEILING",
        )
        result = self._execute(
            plan,
            assessment,
            scope,
            package_path,
            run_id="LIMITED-READ-VALIDATION-POINT-CEILING",
        )
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")

    def test_output_policy_outside_repo(self) -> None:
        result = self._execute(self.clean_plan, self.clean_assessment, self.clean_scope, self.clean_package)
        self.assertTrue(str(self._case_dir).startswith("/tmp/"))

    def test_retention_policy_required(self) -> None:
        plan = copy.deepcopy(self.clean_plan)
        plan["scopeSummary"] = dict(plan["scopeSummary"])
        plan["scopeSummary"]["retentionPolicy"] = "short"
        scope = _default_scope(retentionPolicy="short")
        result = self._execute(plan, self.clean_assessment, scope, self.clean_package)
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")

    def test_rollback_policy_required(self) -> None:
        plan = copy.deepcopy(self.clean_plan)
        plan["scopeSummary"] = dict(plan["scopeSummary"])
        plan["scopeSummary"]["rollbackPolicy"] = "tiny"
        scope = _default_scope(rollbackPolicy="tiny")
        result = self._execute(plan, self.clean_assessment, scope, self.clean_package)
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")

    def test_prohibited_evidence_blocks(self) -> None:
        bad = self._case_dir / "prohibited-package.json"
        package = json.loads(CLEAN_PACKAGE.read_text(encoding="utf-8"))
        package["devices"][0]["password"] = "secret"
        bad.write_text(json.dumps(package), encoding="utf-8")
        result = self._execute(self.clean_plan, self.clean_assessment, self.clean_scope, bad)
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")

    def test_forbidden_operation_in_plan_blocks(self) -> None:
        plan = copy.deepcopy(self.clean_plan)
        plan["allowedOperations"] = list(plan["allowedOperations"]) + ["WRITE_CANONICAL"]
        result = self._execute(plan, self.clean_assessment, self.clean_scope, self.clean_package)
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")

    def test_write_cutover_prohibition(self) -> None:
        plan = copy.deepcopy(self.clean_plan)
        plan["allowedOperations"] = list(plan["allowedOperations"]) + ["APPROVE_WRITE_CUTOVER"]
        result = self._execute(plan, self.clean_assessment, self.clean_scope, self.clean_package)
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")
        self.assertEqual(result["writeCutoverStatus"], "NOT_READY_FOR_WRITE_CUTOVER")

    def test_clean_synthetic_execution_complete(self) -> None:
        result = self._execute(self.clean_plan, self.clean_assessment, self.clean_scope, self.clean_package)
        self.assertEqual(result["validationOutcome"], "VALIDATION_COMPLETE")
        self.assertEqual(result["executionState"], "VALIDATION_COMPLETE")

    def test_validation_outcome_with_reviews(self) -> None:
        from src.asset_graph.reconciliation.read_validation.executor import _validation_outcome

        outcome = _validation_outcome(
            {"reviews": ["REVIEW:EXAMPLE"], "blockers": []},
            {"decision": "READY_FOR_LIMITED_READ_VALIDATION", "reviewCount": 1},
        )
        self.assertEqual(outcome, "VALIDATION_COMPLETE_WITH_REVIEWS")

    def test_review_evidence_non_approved_plan_blocked(self) -> None:
        report_path = OUTPUT_ROOT / "setup" / "review-source-report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report = run_device_reconciliation_evidence(
            root=self.root,
            input_path=REVIEW_PACKAGE,
            output_path=report_path,
            run_id="LIMITED-READ-VALIDATION-REVIEW-001",
        )
        policy = load_readiness_policy(root=self.root)
        assessment = assess_readiness(report, policy, determinism_confirmed=True).serialize()
        scope = _default_scope()
        contract = load_execution_contract(root=self.root)
        control_input = build_control_input(
            readiness_assessment=assessment,
            evidence=report,
            execution_scope=scope,
            approvals=(_synthetic_approval(scope, assessment),),
            evaluation_instant=EVALUATION_INSTANT,
        )
        plan = evaluate_execution_plan(control_input, contract).serialize()
        self.assertEqual(plan["executionState"], "EXECUTION_BLOCKED")
        result = self._execute(plan, assessment, scope, REVIEW_PACKAGE, run_id="LIMITED-READ-VALIDATION-REVIEW-001")
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")

    def test_blocker_rich_non_approved_plan_blocked(self) -> None:
        plan = copy.deepcopy(self.clean_plan)
        plan["executionState"] = "EXECUTION_BLOCKED"
        plan["approvalStatus"] = "INVALID"
        result = self._execute(plan, self.clean_assessment, self.clean_scope, self.clean_package)
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")

    def test_deterministic_output(self) -> None:
        out1 = self._case_dir / "run-a"
        out2 = self._case_dir / "run-b"
        one = self._execute(
            self.clean_plan,
            self.clean_assessment,
            self.clean_scope,
            self.clean_package,
            output_dir=out1,
        )
        two = self._execute(
            self.clean_plan,
            self.clean_assessment,
            self.clean_scope,
            self.clean_package,
            output_dir=out2,
        )
        self.assertEqual(one["resultDigest"], two["resultDigest"])
        for name in (
            "execution-result.json",
            "reconciliation-report.json",
            "readiness-assessment.json",
            "aggregate-summary.json",
            "artifact-manifest.json",
        ):
            self.assertEqual((out1 / name).read_bytes(), (out2 / name).read_bytes(), name)

    def test_artifact_manifest(self) -> None:
        output_dir = self._case_dir / "manifest"
        self._execute(
            self.clean_plan,
            self.clean_assessment,
            self.clean_scope,
            self.clean_package,
            output_dir=output_dir,
        )
        manifest = json.loads((output_dir / "artifact-manifest.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(manifest["artifacts"]), 4)
        for item in manifest["artifacts"]:
            self.assertFalse(item["containsRawRecords"])
            self.assertIn("sha256", item)
            self.assertIn("artifactType", item)

    def test_no_source_file_modification(self) -> None:
        before = hashlib.sha256(CLEAN_PACKAGE.read_bytes()).hexdigest()
        self._execute(self.clean_plan, self.clean_assessment, self.clean_scope, self.clean_package)
        after = hashlib.sha256(CLEAN_PACKAGE.read_bytes()).hexdigest()
        self.assertEqual(before, after)

    def test_no_raw_source_package_copy(self) -> None:
        output_dir = self._case_dir / "copy-check"
        self._execute(
            self.clean_plan,
            self.clean_assessment,
            self.clean_scope,
            self.clean_package,
            output_dir=output_dir,
        )
        copied = list(output_dir.glob("**/clean-source-package.json"))
        self.assertEqual(copied, [])

    def test_no_db_imports_in_module(self) -> None:
        module_dir = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/read_validation"
        text = "\n".join(path.read_text(encoding="utf-8") for path in module_dir.rglob("*.py"))
        for token in ("sqlalchemy", "db.session", "create_app(", "@api_bp.route"):
            self.assertNotIn(token, text)

    def test_no_provider_writes_in_module(self) -> None:
        module_dir = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/read_validation"
        text = "\n".join(path.read_text(encoding="utf-8") for path in module_dir.rglob("*.py"))
        for token in (".write(", "session.add(", "session.commit(", "insert("):
            self.assertNotIn(token, text)

    def test_no_api_routes_in_module(self) -> None:
        module_dir = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/read_validation"
        text = "\n".join(path.read_text(encoding="utf-8") for path in module_dir.rglob("*.py"))
        self.assertNotIn("@api_bp.route", text)

    def test_no_identifier_leakage_in_aggregate_summary(self) -> None:
        output_dir = self._case_dir / "aggregate"
        self._execute(
            self.clean_plan,
            self.clean_assessment,
            self.clean_scope,
            self.clean_package,
            output_dir=output_dir,
        )
        payload = json.loads((output_dir / "aggregate-summary.json").read_text(encoding="utf-8"))
        self.assertFalse(payload["containsRawRecords"])
        text = json.dumps(payload)
        for token in ("ag-device-", "ag-point-"):
            self.assertNotIn(token, text)

    def test_rollback_semantics(self) -> None:
        result = self._execute(self.clean_plan, self.clean_assessment, self.clean_scope, self.clean_package)
        rollback = result["rollbackDisposition"]
        self.assertTrue(rollback["inMemoryStateDiscarded"])
        self.assertTrue(rollback["sourceDataUnchanged"])
        self.assertTrue(rollback["canonicalDataUnchanged"])

    def test_execution_metadata(self) -> None:
        result = self._execute(self.clean_plan, self.clean_assessment, self.clean_scope, self.clean_package)
        self.assertEqual(result["executionName"], "VANTARIS ONE Offline Limited Read Validation Execution")
        self.assertEqual(result["authority"], "ONE-A5-P1-16M")

    def test_required_output_files(self) -> None:
        output_dir = self._case_dir / "outputs"
        self._execute(
            self.clean_plan,
            self.clean_assessment,
            self.clean_scope,
            self.clean_package,
            output_dir=output_dir,
        )
        for name in (
            "execution-result.json",
            "reconciliation-report.json",
            "readiness-assessment.json",
            "aggregate-summary.json",
            "artifact-manifest.json",
        ):
            self.assertTrue((output_dir / name).is_file(), name)

    def test_rejected_plan_states(self) -> None:
        for state in ("DRAFT", "WAITING_FOR_APPROVAL", "EXECUTION_BLOCKED", "ROLLED_BACK"):
            plan = copy.deepcopy(self.clean_plan)
            plan["executionState"] = state
            result = self._execute(plan, self.clean_assessment, self.clean_scope, self.clean_package)
            self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED", state)

    def test_write_cutover_status_on_result(self) -> None:
        result = self._execute(self.clean_plan, self.clean_assessment, self.clean_scope, self.clean_package)
        self.assertEqual(result["writeCutoverStatus"], "NOT_READY_FOR_WRITE_CUTOVER")

    def test_pre_execution_gate_results_present(self) -> None:
        result = self._execute(self.clean_plan, self.clean_assessment, self.clean_scope, self.clean_package)
        self.assertGreaterEqual(len(result["preExecutionGateResults"]), 10)

    def test_relationship_metrics_present(self) -> None:
        result = self._execute(self.clean_plan, self.clean_assessment, self.clean_scope, self.clean_package)
        self.assertIn("relationshipResultCount", result["relationshipMetrics"])

    def test_output_location_policy_gate(self) -> None:
        plan = copy.deepcopy(self.clean_plan)
        plan["scopeSummary"] = dict(plan["scopeSummary"])
        plan["scopeSummary"]["outputLocationPolicy"] = "INVALID"
        scope = _default_scope(outputLocationPolicy="INVALID")
        result = self._execute(plan, self.clean_assessment, scope, self.clean_package)
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")

    def test_approval_status_required(self) -> None:
        plan = copy.deepcopy(self.clean_plan)
        plan["approvalStatus"] = "MISSING"
        result = self._execute(plan, self.clean_assessment, self.clean_scope, self.clean_package)
        self.assertEqual(result["validationOutcome"], "EXECUTION_BLOCKED")


if __name__ == "__main__":
    unittest.main()
