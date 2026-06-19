"""Tests for controlled Asset Graph read migration execution contract."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from src.asset_graph.reconciliation.migration_control import (
    ApprovalRecord,
    ExecutionScope,
    build_control_input,
    evaluate_execution_plan,
    load_execution_contract,
)
from src.asset_graph.reconciliation.migration_control.contract import MigrationControlContractError
from src.asset_graph.reconciliation.readiness import assess_readiness, load_readiness_policy

ROOT = Path(__file__).resolve().parents[5]
READINESS_FIXTURES = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/readiness/fixtures"
CLEAN = READINESS_FIXTURES / "clean-synthetic-evidence-report.json"
REAL = READINESS_FIXTURES / "real-sanitized-evidence-report.json"
BLOCKER_RICH = Path("/tmp/one-p1-16h/run-1-report.json")

ALLOWED_OPERATIONS = (
    "READ_SOURCE_PACKAGE",
    "PROJECT_IN_MEMORY",
    "RECONCILE_IN_MEMORY",
    "GENERATE_EVIDENCE",
    "GENERATE_READINESS_ASSESSMENT",
    "EXPORT_AGGREGATE_REPORT",
)

EVALUATION_INSTANT = "2026-06-19T00:00:00Z"


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


def _real_approvals(scope: ExecutionScope, assessment: dict) -> tuple[ApprovalRecord, ...]:
    common = {
        "scope_digest": scope.scope_digest(),
        "evidence_digest": assessment["evidenceDigest"],
        "readiness_result_digest": assessment["resultDigest"],
        "issued_at_policy": "2026-06-01T00:00:00Z",
        "expires_at": "2026-12-31T23:59:59Z",
        "status": "ACTIVE",
        "constraints": ("READ_ONLY_VALIDATION",),
        "revocation_reason": "",
    }
    return (
        ApprovalRecord(
            approval_id="real-data-001",
            approval_type="REAL_READ_MIGRATION_CANDIDATE_REVIEW",
            approved_by_role="DATA_OWNER",
            **common,
        ),
        ApprovalRecord(
            approval_id="real-arch-001",
            approval_type="REAL_READ_MIGRATION_CANDIDATE_REVIEW",
            approved_by_role="ARCHITECTURE_OWNER",
            **common,
        ),
    )


class TestMigrationControl(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = load_execution_contract(root=ROOT)
        cls.policy = load_readiness_policy(root=ROOT)
        cls.clean_evidence = json.loads(CLEAN.read_text(encoding="utf-8"))
        cls.real_evidence = json.loads(REAL.read_text(encoding="utf-8"))
        cls.blocker_rich = (
            json.loads(BLOCKER_RICH.read_text(encoding="utf-8")) if BLOCKER_RICH.is_file() else None
        )
        cls.clean_assessment = assess_readiness(
            cls.clean_evidence, cls.policy, determinism_confirmed=True
        ).serialize()
        cls.real_assessment = assess_readiness(
            cls.real_evidence, cls.policy, determinism_confirmed=True
        ).serialize()
        cls.blocker_assessment = (
            assess_readiness(cls.blocker_rich, cls.policy, determinism_confirmed=True).serialize()
            if cls.blocker_rich is not None
            else None
        )

    def _plan(self, evidence: dict, assessment: dict, *, scope=None, approvals=(), **kwargs: object) -> dict:
        scope = scope or _default_scope()
        control_input = build_control_input(
            readiness_assessment=assessment,
            evidence=evidence,
            execution_scope=scope,
            approvals=approvals,
            evaluation_instant=EVALUATION_INSTANT,
            **kwargs,
        )
        return evaluate_execution_plan(control_input, self.contract).serialize()

    def test_contract_parses(self) -> None:
        self.assertEqual(self.contract["contractVersion"], "1.0.0")
        self.assertEqual(self.contract["authority"], "ONE-A5-P1-16L")

    def test_execution_mode_read_only(self) -> None:
        self.assertEqual(self.contract["executionMode"], "READ_ONLY_VALIDATION")

    def test_allowed_execution_states(self) -> None:
        self.assertIn("APPROVED_FOR_LIMITED_READ_VALIDATION", self.contract["allowedExecutionStates"])
        self.assertIn("WAITING_FOR_APPROVAL", self.contract["allowedExecutionStates"])

    def test_forbidden_execution_states(self) -> None:
        forbidden = set(self.contract["forbiddenExecutionStates"])
        self.assertTrue({"APPROVED_FOR_WRITE_MIGRATION", "APPROVED_FOR_WRITE_CUTOVER", "DUAL_WRITE_ACTIVE"}.issubset(forbidden))

    def test_allowed_operations_declared(self) -> None:
        self.assertIn("GENERATE_READINESS_ASSESSMENT", self.contract["allowedOperations"])

    def test_forbidden_operations_declared(self) -> None:
        forbidden = set(self.contract["forbiddenOperations"])
        self.assertTrue({"WRITE_CANONICAL", "RUN_MIGRATION", "APPROVE_WRITE_CUTOVER"}.issubset(forbidden))

    def test_approval_types_declared(self) -> None:
        self.assertIn("SYNTHETIC_LIMITED_READ_VALIDATION", self.contract["allowedApprovalTypes"])

    def test_scope_digest_deterministic(self) -> None:
        scope = _default_scope()
        self.assertEqual(scope.scope_digest(), scope.scope_digest())

    def test_scope_digest_changes_with_scope(self) -> None:
        one = _default_scope()
        two = _default_scope(maximumDeviceCount=99)
        self.assertNotEqual(one.scope_digest(), two.scope_digest())

    def test_evidence_digest_required(self) -> None:
        bad = copy.deepcopy(self.clean_assessment)
        bad["evidenceDigest"] = ""
        plan = self._plan(self.clean_evidence, bad, approvals=(_synthetic_approval(_default_scope(), self.clean_assessment),))
        self.assertEqual(plan["executionState"], "WAITING_FOR_EVIDENCE")

    def test_readiness_decision_compatibility_clean(self) -> None:
        self.assertEqual(self.clean_assessment["decision"], "READY_FOR_LIMITED_READ_VALIDATION")

    def test_synthetic_ceiling(self) -> None:
        self.assertEqual(self.clean_assessment["evidenceClassification"], "SYNTHETIC_REPRESENTATIVE_ONLY")

    def test_blocker_rich_scenario_execution_blocked(self) -> None:
        if self.blocker_assessment is None:
            self.skipTest("blocker-rich synthetic report unavailable")
        plan = self._plan(self.blocker_rich, self.blocker_assessment)
        self.assertEqual(plan["executionState"], "EXECUTION_BLOCKED")
        self.assertEqual(self.blocker_assessment["decision"], "NOT_READY")

    def test_clean_without_approval_waiting(self) -> None:
        plan = self._plan(self.clean_evidence, self.clean_assessment)
        self.assertEqual(plan["executionState"], "WAITING_FOR_APPROVAL")
        self.assertEqual(plan["approvalStatus"], "MISSING")

    def test_clean_with_matching_approval_approved(self) -> None:
        scope = _default_scope()
        approval = _synthetic_approval(scope, self.clean_assessment)
        plan = self._plan(self.clean_evidence, self.clean_assessment, scope=scope, approvals=(approval,))
        self.assertEqual(plan["executionState"], "APPROVED_FOR_LIMITED_READ_VALIDATION")
        self.assertEqual(plan["approvalStatus"], "APPROVED")

    def test_synthetic_production_migration_blocked(self) -> None:
        scope = _default_scope()
        approval = _synthetic_approval(scope, self.clean_assessment)
        plan = self._plan(
            self.clean_evidence,
            self.clean_assessment,
            scope=scope,
            approvals=(approval,),
            migration_intent="PRODUCTION_MIGRATION",
        )
        self.assertEqual(plan["executionState"], "EXECUTION_BLOCKED")

    def test_expired_approval_blocked(self) -> None:
        scope = _default_scope()
        approval = ApprovalRecord(
            approval_id="expired-001",
            approval_type="SYNTHETIC_LIMITED_READ_VALIDATION",
            approved_by_role="ARCHITECTURE_OWNER",
            scope_digest=scope.scope_digest(),
            evidence_digest=self.clean_assessment["evidenceDigest"],
            readiness_result_digest=self.clean_assessment["resultDigest"],
            issued_at_policy="2026-01-01T00:00:00Z",
            expires_at="2026-06-01T00:00:00Z",
            status="ACTIVE",
            constraints=("READ_ONLY_VALIDATION",),
        )
        plan = self._plan(self.clean_evidence, self.clean_assessment, scope=scope, approvals=(approval,))
        self.assertEqual(plan["executionState"], "EXECUTION_BLOCKED")
        self.assertIn("APPROVAL_EXPIRY_GATE", plan["failedPreconditions"])

    def test_scope_digest_mismatch_blocked(self) -> None:
        scope = _default_scope()
        approval = ApprovalRecord(
            approval_id="scope-mismatch-001",
            approval_type="SYNTHETIC_LIMITED_READ_VALIDATION",
            approved_by_role="ARCHITECTURE_OWNER",
            scope_digest="deadbeef" * 8,
            evidence_digest=self.clean_assessment["evidenceDigest"],
            readiness_result_digest=self.clean_assessment["resultDigest"],
            issued_at_policy="2026-06-01T00:00:00Z",
            expires_at="2026-12-31T23:59:59Z",
            status="ACTIVE",
            constraints=("READ_ONLY_VALIDATION",),
        )
        plan = self._plan(self.clean_evidence, self.clean_assessment, scope=scope, approvals=(approval,))
        self.assertEqual(plan["executionState"], "EXECUTION_BLOCKED")
        self.assertIn("APPROVAL_SCOPE_MATCH_GATE", plan["failedPreconditions"])

    def test_forbidden_operation_blocked(self) -> None:
        scope = _default_scope()
        approval = _synthetic_approval(scope, self.clean_assessment)
        plan = self._plan(
            self.clean_evidence,
            self.clean_assessment,
            scope=scope,
            approvals=(approval,),
            requested_operations=("WRITE_CANONICAL",),
        )
        self.assertEqual(plan["executionState"], "EXECUTION_BLOCKED")
        self.assertIn("FORBIDDEN_OPERATION_GATE", plan["failedPreconditions"])

    def test_write_cutover_prohibition(self) -> None:
        scope = _default_scope()
        approval = _synthetic_approval(scope, self.clean_assessment)
        plan = self._plan(
            self.clean_evidence,
            self.clean_assessment,
            scope=scope,
            approvals=(approval,),
            migration_intent="WRITE_CUTOVER",
            requested_operations=("APPROVE_WRITE_CUTOVER",),
        )
        self.assertEqual(plan["executionState"], "EXECUTION_BLOCKED")
        self.assertEqual(plan["writeCutoverStatus"], "NOT_READY_FOR_WRITE_CUTOVER")
        self.assertNotIn(plan["executionState"], self.contract["forbiddenExecutionStates"])

    def test_write_cutover_status_on_plan(self) -> None:
        plan = self._plan(self.clean_evidence, self.clean_assessment)
        self.assertEqual(plan["writeCutoverStatus"], "NOT_READY_FOR_WRITE_CUTOVER")

    def test_all_precondition_gates_present(self) -> None:
        plan = self._plan(self.clean_evidence, self.clean_assessment)
        codes = {item["gateCode"] for item in plan["preconditions"]}
        for gate in self.contract["preconditionGates"]:
            self.assertIn(gate, codes)

    def test_rollback_requirement(self) -> None:
        scope = _default_scope(rollbackPolicy="short")
        plan = self._plan(self.clean_evidence, self.clean_assessment, scope=scope)
        self.assertIn("ROLLBACK_PLAN_GATE", plan["failedPreconditions"])

    def test_retention_requirement(self) -> None:
        scope = _default_scope(retentionPolicy="tiny")
        plan = self._plan(self.clean_evidence, self.clean_assessment, scope=scope)
        self.assertIn("RETENTION_POLICY_GATE", plan["failedPreconditions"])

    def test_count_boundary_gate(self) -> None:
        scope = _default_scope(maximumDeviceCount=0)
        plan = self._plan(self.clean_evidence, self.clean_assessment, scope=scope)
        self.assertIn("COUNT_BOUNDARY_GATE", plan["failedPreconditions"])

    def test_hard_blocker_gate(self) -> None:
        assessment = copy.deepcopy(self.clean_assessment)
        assessment["hardBlockerCount"] = 2
        plan = self._plan(self.clean_evidence, assessment)
        self.assertIn("HARD_BLOCKER_GATE", plan["failedPreconditions"])

    def test_determinism_gate(self) -> None:
        plan = self._plan(
            self.clean_evidence,
            self.clean_assessment,
            deterministic_verification_confirmed=False,
        )
        self.assertIn("DETERMINISM_GATE", plan["failedPreconditions"])

    def test_policy_version_gate(self) -> None:
        assessment = copy.deepcopy(self.clean_assessment)
        assessment["policyVersion"] = "9.9.9"
        plan = self._plan(self.clean_evidence, assessment)
        self.assertIn("POLICY_VERSION_GATE", plan["failedPreconditions"])

    def test_mapping_version_gate(self) -> None:
        scope = _default_scope(mappingVersion="unsupported-version")
        plan = self._plan(self.clean_evidence, self.clean_assessment, scope=scope)
        self.assertIn("MAPPING_VERSION_GATE", plan["failedPreconditions"])

    def test_real_evidence_candidate_contract_path(self) -> None:
        scope = _default_scope(
            tenantScope="tenant-real-candidate",
            siteScope="site-real-candidate",
            maximumDeviceCount=10,
            maximumPointCount=100,
        )
        plan = self._plan(
            self.real_evidence,
            self.real_assessment,
            scope=scope,
            approvals=_real_approvals(scope, self.real_assessment),
            migration_intent="READ_MIGRATION_CANDIDATE_REVIEW",
        )
        self.assertEqual(self.real_assessment["decision"], "READY_FOR_READ_MIGRATION_CANDIDATE")
        self.assertEqual(plan["executionState"], "APPROVED_FOR_LIMITED_READ_VALIDATION")

    def test_real_evidence_without_approvals_waiting(self) -> None:
        plan = self._plan(self.real_evidence, self.real_assessment, migration_intent="READ_MIGRATION_CANDIDATE_REVIEW")
        self.assertEqual(plan["executionState"], "WAITING_FOR_APPROVAL")

    def test_synthetic_cannot_authorize_production_even_with_approval(self) -> None:
        scope = _default_scope()
        approval = _synthetic_approval(scope, self.clean_assessment)
        plan = self._plan(
            self.clean_evidence,
            self.clean_assessment,
            scope=scope,
            approvals=(approval,),
            migration_intent="PRODUCTION_MIGRATION",
        )
        self.assertEqual(plan["executionState"], "EXECUTION_BLOCKED")

    def test_approval_record_serialization(self) -> None:
        scope = _default_scope()
        approval = _synthetic_approval(scope, self.clean_assessment)
        payload = approval.serialize()
        self.assertEqual(payload["approvalType"], "SYNTHETIC_LIMITED_READ_VALIDATION")
        self.assertEqual(ApprovalRecord.from_mapping(payload).approval_id, approval.approval_id)

    def test_control_input_aggregate_only(self) -> None:
        scope = _default_scope()
        control_input = build_control_input(
            readiness_assessment=self.clean_assessment,
            evidence=self.clean_evidence,
            execution_scope=scope,
            evaluation_instant=EVALUATION_INSTANT,
        )
        text = json.dumps(control_input.serialize())
        for token in ("SYNTH-DEV-", "ag-device-", "ag-point-", "fieldCoverage"):
            self.assertNotIn(token, text)

    def test_no_raw_identifiers_in_plan(self) -> None:
        if self.blocker_assessment is None:
            plan = self._plan(self.clean_evidence, self.clean_assessment)
        else:
            plan = self._plan(self.blocker_rich, self.blocker_assessment)
        text = json.dumps(plan)
        for token in ("SYNTH-DEV-", "ag-device-", "ag-point-"):
            self.assertNotIn(token, text)

    def test_deterministic_result_digest(self) -> None:
        scope = _default_scope()
        approval = _synthetic_approval(scope, self.clean_assessment)
        one = self._plan(self.clean_evidence, self.clean_assessment, scope=scope, approvals=(approval,))
        two = self._plan(self.clean_evidence, self.clean_assessment, scope=scope, approvals=(approval,))
        self.assertEqual(one["resultDigest"], two["resultDigest"])

    def test_deterministic_byte_identical_output(self) -> None:
        scope = _default_scope()
        approval = _synthetic_approval(scope, self.clean_assessment)
        one = json.dumps(
            self._plan(self.clean_evidence, self.clean_assessment, scope=scope, approvals=(approval,)),
            indent=2,
            sort_keys=True,
        )
        two = json.dumps(
            self._plan(self.clean_evidence, self.clean_assessment, scope=scope, approvals=(approval,)),
            indent=2,
            sort_keys=True,
        )
        self.assertEqual(one, two)

    def test_contract_rejects_missing_forbidden_state(self) -> None:
        bad = copy.deepcopy(self.contract)
        bad["forbiddenExecutionStates"] = []
        with self.assertRaises(MigrationControlContractError):
            from src.asset_graph.reconciliation.migration_control.contract import _validate_contract

            _validate_contract(bad)

    def test_execution_scope_fields(self) -> None:
        scope = _default_scope()
        payload = scope.serialize()
        for field in self.contract["executionScopeFields"]:
            self.assertIn(field, payload)


if __name__ == "__main__":
    unittest.main()
