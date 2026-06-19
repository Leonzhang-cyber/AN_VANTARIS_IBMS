"""Tests for Asset Graph read migration readiness gate."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from src.asset_graph.reconciliation.readiness import assess_readiness, load_readiness_policy
from src.asset_graph.reconciliation.readiness.evidence import classify_evidence, extract_evidence_snapshot
from src.asset_graph.reconciliation.readiness.gates import evaluate_gates

ROOT = Path(__file__).resolve().parents[5]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CLEAN = FIXTURES / "clean-synthetic-evidence-report.json"
REAL = FIXTURES / "real-sanitized-evidence-report.json"
MULTI_SITE = Path("/tmp/one-p1-16h/run-1-report.json")


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8")) if (FIXTURES / name).is_file() else {}


class TestReadinessGate(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_readiness_policy(root=ROOT)
        cls.clean = json.loads(CLEAN.read_text(encoding="utf-8"))
        cls.real = json.loads(REAL.read_text(encoding="utf-8"))
        cls.blocker_rich = json.loads(MULTI_SITE.read_text(encoding="utf-8")) if MULTI_SITE.is_file() else None

    def _assess(self, evidence: dict, *, determinism_confirmed: bool = True) -> dict:
        return assess_readiness(evidence, self.policy, determinism_confirmed=determinism_confirmed).serialize()

    def _gate(self, payload: dict, code: str) -> dict:
        return next(item for item in payload["gateResults"] if item["gateCode"] == code)

    def test_policy_loads(self) -> None:
        self.assertEqual(self.policy["policyVersion"], "1.0.0")

    def test_all_required_gates_present(self) -> None:
        payload = self._assess(self.clean)
        codes = {item["gateCode"] for item in payload["gateResults"]}
        required = {
            "PRIVACY_GATE", "EVIDENCE_FORMAT_GATE", "DETERMINISM_GATE", "MAPPING_VERSION_GATE",
            "REQUIRED_FIELD_COVERAGE_GATE", "SAFE_SOURCE_COVERAGE_GATE", "SOURCE_IDENTITY_GATE",
            "GLOBAL_ID_GATE", "TENANT_SCOPE_GATE", "SITE_SCOPE_GATE", "POINT_PARENT_GATE",
            "HAS_POINT_PARITY_GATE", "ORPHAN_RELATIONSHIP_GATE", "UNRESOLVED_RELATIONSHIP_GATE",
            "DUPLICATE_RELATIONSHIP_GATE", "REVIEW_RATIO_GATE", "WARNING_RATIO_GATE",
            "EVIDENCE_CLASSIFICATION_GATE", "WRITE_CUTOVER_PROHIBITION_GATE",
        }
        self.assertTrue(required.issubset(codes))

    def test_privacy_gate_pass_clean(self) -> None:
        self.assertEqual(self._gate(self._assess(self.clean), "PRIVACY_GATE")["status"], "PASS")

    def test_evidence_format_gate_fail_missing_fields(self) -> None:
        bad = copy.deepcopy(self.clean)
        del bad["relationshipMetrics"]
        payload = self._assess(bad)
        self.assertEqual(self._gate(payload, "EVIDENCE_FORMAT_GATE")["status"], "FAIL")
        self.assertEqual(payload["decision"], "INPUT_REJECTED")

    def test_determinism_gate_requires_confirmation(self) -> None:
        payload = self._assess(self.clean, determinism_confirmed=False)
        self.assertEqual(self._gate(payload, "DETERMINISM_GATE")["status"], "FAIL")

    def test_mapping_version_gate(self) -> None:
        bad = copy.deepcopy(self.clean)
        bad["mappingVersion"] = "9.9.9"
        self.assertEqual(self._gate(self._assess(bad), "MAPPING_VERSION_GATE")["status"], "FAIL")

    def test_required_field_coverage_gate(self) -> None:
        bad = copy.deepcopy(self.clean)
        bad["fieldCoverage"][0]["requiredFieldCoverage"] = "90.00%"
        self.assertEqual(self._gate(self._assess(bad), "REQUIRED_FIELD_COVERAGE_GATE")["status"], "FAIL")

    def test_safe_source_coverage_gate(self) -> None:
        bad = copy.deepcopy(self.clean)
        bad["fieldCoverage"][0]["safeSourceFieldCoverage"] = "50.00%"
        self.assertEqual(self._gate(self._assess(bad), "SAFE_SOURCE_COVERAGE_GATE")["status"], "FAIL")

    def test_safe_source_coverage_boundary_pass(self) -> None:
        edge = copy.deepcopy(self.clean)
        edge["fieldCoverage"][0]["safeSourceFieldCoverage"] = "75.00%"
        self.assertEqual(self._gate(self._assess(edge), "SAFE_SOURCE_COVERAGE_GATE")["status"], "PASS")

    def test_source_identity_gate_blocker(self) -> None:
        bad = copy.deepcopy(self.clean)
        bad["blockers"] = ["DUPLICATE_SOURCE_IDENTITY"]
        self.assertEqual(self._gate(self._assess(bad), "SOURCE_IDENTITY_GATE")["status"], "FAIL")

    def test_global_id_gate_blocker(self) -> None:
        bad = copy.deepcopy(self.clean)
        bad["blockers"] = ["GLOBAL_ID_COLLISION"]
        self.assertEqual(self._gate(self._assess(bad), "GLOBAL_ID_GATE")["status"], "FAIL")

    def test_tenant_scope_gate_blocker(self) -> None:
        bad = copy.deepcopy(self.clean)
        bad["blockers"] = ["TENANT_SCOPE_MISMATCH"]
        self.assertEqual(self._gate(self._assess(bad), "TENANT_SCOPE_GATE")["status"], "FAIL")

    def test_site_scope_gate_blocker(self) -> None:
        bad = copy.deepcopy(self.clean)
        bad["blockers"] = ["SITE_SCOPE_MISMATCH"]
        self.assertEqual(self._gate(self._assess(bad), "SITE_SCOPE_GATE")["status"], "FAIL")

    def test_has_point_parity_gate(self) -> None:
        bad = copy.deepcopy(self.clean)
        bad["relationshipMetrics"]["relationshipTypeCounts"]["HAS_POINT"]["passCount"] = 1
        self.assertEqual(self._gate(self._assess(bad), "HAS_POINT_PARITY_GATE")["status"], "FAIL")

    def test_unresolved_relationship_gate_review(self) -> None:
        edge = copy.deepcopy(self.clean)
        edge["relationshipMetrics"]["unresolvedRelationshipCount"] = 1
        edge["relationshipMetrics"]["relationshipResultCount"] = 3
        gate = self._gate(self._assess(edge), "UNRESOLVED_RELATIONSHIP_GATE")
        self.assertEqual(gate["status"], "PASS")

    def test_unresolved_relationship_gate_fail_for_candidate(self) -> None:
        edge = copy.deepcopy(self.real)
        edge["relationshipMetrics"]["unresolvedRelationshipCount"] = 1
        gate = self._gate(self._assess(edge), "UNRESOLVED_RELATIONSHIP_GATE")
        self.assertTrue(gate["blocking"])

    def test_duplicate_relationship_gate_fail(self) -> None:
        bad = copy.deepcopy(self.clean)
        bad["relationshipMetrics"]["duplicateCanonicalRelationshipCount"] = 5
        bad["relationshipMetrics"]["duplicateHasPointPairCount"] = 5
        self.assertEqual(self._gate(self._assess(bad), "DUPLICATE_RELATIONSHIP_GATE")["status"], "FAIL")

    def test_review_ratio_gate(self) -> None:
        bad = copy.deepcopy(self.clean)
        bad["reconciliationSummary"]["reviewCount"] = 5
        bad["reconciliationSummary"]["totalRecords"] = 10
        self.assertEqual(self._gate(self._assess(bad), "REVIEW_RATIO_GATE")["status"], "REVIEW")

    def test_warning_ratio_gate(self) -> None:
        bad = copy.deepcopy(self.clean)
        bad["reconciliationSummary"]["warningCount"] = 5
        bad["reconciliationSummary"]["totalRecords"] = 10
        self.assertEqual(self._gate(self._assess(bad), "WARNING_RATIO_GATE")["status"], "REVIEW")

    def test_write_cutover_prohibition_gate(self) -> None:
        bad = copy.deepcopy(self.clean)
        bad["cutoverDecision"] = "READY_FOR_WRITE_CUTOVER"
        self.assertEqual(self._gate(self._assess(bad), "WRITE_CUTOVER_PROHIBITION_GATE")["status"], "FAIL")

    def test_unknown_evidence_classification(self) -> None:
        unknown = copy.deepcopy(self.clean)
        unknown["sourceSummary"]["notes"] = "unclassified export"
        payload = self._assess(unknown)
        self.assertEqual(payload["evidenceClassification"], "UNKNOWN")
        self.assertEqual(payload["decision"], "NOT_READY")

    def test_synthetic_decision_ceiling(self) -> None:
        payload = self._assess(self.clean)
        self.assertEqual(payload["decision"], "READY_FOR_LIMITED_READ_VALIDATION")
        self.assertNotEqual(payload["decision"], "READY_FOR_READ_MIGRATION_CANDIDATE")

    def test_real_evidence_candidate_path(self) -> None:
        payload = self._assess(self.real)
        self.assertEqual(payload["decision"], "READY_FOR_READ_MIGRATION_CANDIDATE")

    def test_hard_blocker_precedence(self) -> None:
        bad = copy.deepcopy(self.real)
        bad["blockers"] = ["GLOBAL_ID_COLLISION"]
        self.assertEqual(self._assess(bad)["decision"], "NOT_READY")

    def test_clean_control_result(self) -> None:
        payload = self._assess(self.clean)
        self.assertEqual(payload["relationshipSummary"]["duplicateCanonicalRelationshipCount"], 0)
        self.assertEqual(payload["relationshipSummary"]["unresolvedRelationshipCount"], 0)

    def test_blocker_rich_synthetic_result(self) -> None:
        if self.blocker_rich is None:
            self.skipTest("multi-site synthetic report unavailable")
        payload = self._assess(self.blocker_rich)
        self.assertEqual(payload["decision"], "NOT_READY")
        self.assertEqual(self._gate(payload, "DUPLICATE_RELATIONSHIP_GATE")["status"], "FAIL")

    def test_multi_site_relationship_counts(self) -> None:
        if self.blocker_rich is None:
            self.skipTest("multi-site synthetic report unavailable")
        rel = self.blocker_rich["relationshipMetrics"]
        self.assertEqual(rel["relationshipResultCount"], 589)
        self.assertEqual(rel["canonicalRelationshipCount"], 588)
        self.assertEqual(rel["unresolvedRelationshipCount"], 1)

    def test_type_counts_reconcile(self) -> None:
        if self.blocker_rich is None:
            self.skipTest("multi-site synthetic report unavailable")
        payload = self._assess(self.blocker_rich)
        rel = payload["relationshipSummary"]
        self.assertEqual(rel["relationshipResultCount"], 589)
        self.assertEqual(rel["canonicalRelationshipCount"], 588)

    def test_no_raw_identifiers_in_assessment(self) -> None:
        payload = self._assess(self.blocker_rich or self.clean)
        text = json.dumps(payload)
        for token in ("SYNTH-DEV-", "ag-device-", "ag-point-"):
            self.assertNotIn(token, text)

    def test_deterministic_result_digest(self) -> None:
        one = self._assess(self.clean)
        two = self._assess(self.clean)
        self.assertEqual(one["resultDigest"], two["resultDigest"])

    def test_gate_status_counts(self) -> None:
        payload = self._assess(self.clean)
        self.assertEqual(payload["passedGateCount"] + payload["failedGateCount"], len(payload["gateResults"]))

    def test_classify_synthetic_representative(self) -> None:
        self.assertEqual(classify_evidence(self.clean, self.policy), "SYNTHETIC_REPRESENTATIVE_ONLY")

    def test_classify_real_sanitized(self) -> None:
        self.assertEqual(classify_evidence(self.real, self.policy), "REAL_SANITIZED_EVIDENCE")

    def test_snapshot_extracts_aggregate_metrics(self) -> None:
        snapshot = extract_evidence_snapshot(self.clean, self.policy)
        self.assertEqual(snapshot.projected_point_count, 2)
        self.assertFalse(snapshot.source_identity_collision)

    def test_evaluate_gates_count(self) -> None:
        snapshot = extract_evidence_snapshot(self.clean, self.policy)
        gates = evaluate_gates(self.clean, snapshot, self.policy, determinism_confirmed=True)
        self.assertEqual(len(gates), 19)

    def test_synthetic_negative_test_classification(self) -> None:
        negative = copy.deepcopy(self.clean)
        negative["sourceSummary"]["notes"] = "intentional blocker negative test fixture"
        self.assertEqual(classify_evidence(negative, self.policy), "SYNTHETIC_NEGATIVE_TEST")
        self.assertEqual(self._assess(negative)["decision"], "NOT_READY")

    def test_point_parent_gate(self) -> None:
        bad = copy.deepcopy(self.clean)
        bad["blockers"] = ["POINT_DEVICE_REFERENCE"]
        self.assertEqual(self._gate(self._assess(bad), "POINT_PARENT_GATE")["status"], "FAIL")

    def test_orphan_relationship_gate(self) -> None:
        bad = copy.deepcopy(self.clean)
        bad["blockers"] = ["ORPHAN_RELATIONSHIP"]
        self.assertEqual(self._gate(self._assess(bad), "ORPHAN_RELATIONSHIP_GATE")["status"], "FAIL")

    def test_legacy_single_site_backward_compatible(self) -> None:
        legacy = copy.deepcopy(self.clean)
        legacy["sourceSummary"]["notes"] = "Synthetic sample package only."
        payload = self._assess(legacy)
        self.assertIn(payload["decision"], {"READY_FOR_LIMITED_READ_VALIDATION", "NOT_READY", "UNKNOWN"})


if __name__ == "__main__":
    unittest.main()
