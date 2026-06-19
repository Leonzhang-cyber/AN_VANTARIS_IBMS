"""Tests for readiness policy semantics and operator explanations."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from src.asset_graph.reconciliation.readiness import (
    APPROVED_AGGREGATIONS,
    assess_readiness,
    load_readiness_policy,
    validate_gate_semantics,
)
from src.asset_graph.reconciliation.readiness.semantics import GateSemanticsError

ROOT = Path(__file__).resolve().parents[5]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CLEAN = FIXTURES / "clean-synthetic-evidence-report.json"
MULTI_SITE = Path("/tmp/one-p1-16h/run-1-report.json")

NUMERIC_GATES = (
    "REQUIRED_FIELD_COVERAGE_GATE",
    "SAFE_SOURCE_COVERAGE_GATE",
    "UNRESOLVED_RELATIONSHIP_GATE",
    "DUPLICATE_RELATIONSHIP_GATE",
    "REVIEW_RATIO_GATE",
    "WARNING_RATIO_GATE",
    "HAS_POINT_PARITY_GATE",
    "TENANT_SCOPE_GATE",
    "SITE_SCOPE_GATE",
)

LEGACY_FIELDS = (
    "decision",
    "hardBlockerCount",
    "gateResults",
    "coverageSummary",
    "identitySummary",
    "scopeSummary",
    "relationshipSummary",
    "resultDigest",
)


class TestReadinessSemantics(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_readiness_policy(root=ROOT)
        cls.clean = json.loads(CLEAN.read_text(encoding="utf-8"))
        cls.blocker_rich = (
            json.loads(MULTI_SITE.read_text(encoding="utf-8")) if MULTI_SITE.is_file() else None
        )

    def _assess(self, evidence: dict) -> dict:
        return assess_readiness(evidence, self.policy, determinism_confirmed=True).serialize()

    def _gate(self, payload: dict, code: str) -> dict:
        return next(item for item in payload["gateResults"] if item["gateCode"] == code)

    def test_policy_declares_safe_source_aggregation(self) -> None:
        entry = self.policy["gateSemantics"]["SAFE_SOURCE_COVERAGE_GATE"]
        self.assertEqual(entry["aggregation"], "MINIMUM_PER_RECORD")
        self.assertEqual(entry["recordScope"], "DEVICE_FIELD_COVERAGE_ROWS")
        self.assertEqual(entry["comparison"], "observed >= threshold")
        self.assertEqual(entry["percentageScale"], "0_TO_100")

    def test_safe_source_threshold_remains_75(self) -> None:
        self.assertEqual(
            self.policy["coverageThresholds"]["safeSourceFieldCoverageMinimumPercent"],
            75,
        )

    def test_all_numeric_gates_have_semantics(self) -> None:
        semantics = self.policy["gateSemantics"]
        for gate_code in NUMERIC_GATES:
            self.assertIn(gate_code, semantics)
            self.assertIn(semantics[gate_code]["aggregation"], APPROVED_AGGREGATIONS)

    def test_unsupported_aggregation_label_rejected(self) -> None:
        bad = copy.deepcopy(self.policy)
        bad["gateSemantics"] = dict(bad["gateSemantics"])
        bad["gateSemantics"]["SAFE_SOURCE_COVERAGE_GATE"] = dict(
            bad["gateSemantics"]["SAFE_SOURCE_COVERAGE_GATE"]
        )
        bad["gateSemantics"]["SAFE_SOURCE_COVERAGE_GATE"]["aggregation"] = "CUSTOM_AVERAGE"
        with self.assertRaises(GateSemanticsError):
            validate_gate_semantics(bad)

    def test_legacy_fields_remain_present(self) -> None:
        payload = self._assess(self.clean)
        for field in LEGACY_FIELDS:
            self.assertIn(field, payload)

    def test_coverage_statistics_present(self) -> None:
        payload = self._assess(self.clean)
        stats = payload["coverageStatistics"]
        required = (
            "requiredCoverageMinimumPercent",
            "requiredCoverageAveragePercent",
            "safeSourceCoverageMinimumPercent",
            "safeSourceCoverageAveragePercent",
            "safeSourceCoverageMaximumPercent",
            "safeSourceRecordsBelowThreshold",
            "safeSourceRecordCount",
        )
        for key in required:
            self.assertIn(key, stats)

    def test_gate_results_include_operator_explanation(self) -> None:
        payload = self._assess(self.clean)
        for gate in payload["gateResults"]:
            self.assertIn("comparisonMetric", gate)
            self.assertIn("aggregation", gate)
            self.assertIn("comparisonScale", gate)
            self.assertIn("explanation", gate)
            self.assertTrue(gate["explanation"])

    def test_safe_source_gate_enriched_fields(self) -> None:
        gate = self._gate(self._assess(self.clean), "SAFE_SOURCE_COVERAGE_GATE")
        self.assertEqual(gate["aggregation"], "MINIMUM_PER_RECORD")
        self.assertEqual(gate["comparisonScale"], "0_TO_100")
        self.assertEqual(gate["comparisonMetric"], "minimumPerRecordSafeSourceCoverage")

    def test_minimum_73_with_average_78_fails(self) -> None:
        if self.blocker_rich is None:
            self.skipTest("multi-site synthetic report unavailable")
        payload = self._assess(self.blocker_rich)
        gate = self._gate(payload, "SAFE_SOURCE_COVERAGE_GATE")
        stats = payload["coverageStatistics"]
        self.assertEqual(gate["status"], "FAIL")
        self.assertEqual(gate["observedValue"], "73.33%")
        self.assertEqual(gate["requiredValue"], ">=75.00%")
        self.assertAlmostEqual(stats["safeSourceCoverageMinimumPercent"], 73.33, places=2)
        self.assertGreater(stats["safeSourceCoverageAveragePercent"], 75.0)
        self.assertEqual(payload["decision"], "NOT_READY")

    def test_minimum_75_passes(self) -> None:
        edge = copy.deepcopy(self.clean)
        edge["fieldCoverage"][0]["safeSourceFieldCoverage"] = "75.00%"
        gate = self._gate(self._assess(edge), "SAFE_SOURCE_COVERAGE_GATE")
        self.assertEqual(gate["status"], "PASS")
        self.assertEqual(gate["observedValue"], "75.00%")

    def test_displayed_observed_matches_minimum(self) -> None:
        if self.blocker_rich is None:
            self.skipTest("multi-site synthetic report unavailable")
        payload = self._assess(self.blocker_rich)
        gate = self._gate(payload, "SAFE_SOURCE_COVERAGE_GATE")
        minimum = payload["coverageStatistics"]["safeSourceCoverageMinimumPercent"]
        observed = float(gate["observedValue"].rstrip("%"))
        self.assertAlmostEqual(observed, minimum, places=2)

    def test_average_remains_informational_on_failure(self) -> None:
        if self.blocker_rich is None:
            self.skipTest("multi-site synthetic report unavailable")
        payload = self._assess(self.blocker_rich)
        stats = payload["coverageStatistics"]
        gate = self._gate(payload, "SAFE_SOURCE_COVERAGE_GATE")
        self.assertGreater(stats["safeSourceCoverageAveragePercent"], 75.0)
        self.assertEqual(gate["status"], "FAIL")
        self.assertIn("informational", gate["explanation"].lower() + self.policy["gateSemantics"]["SAFE_SOURCE_COVERAGE_GATE"]["explanation"].lower())

    def test_records_below_threshold_correct(self) -> None:
        if self.blocker_rich is None:
            self.skipTest("multi-site synthetic report unavailable")
        stats = self._assess(self.blocker_rich)["coverageStatistics"]
        threshold = self.policy["coverageThresholds"]["safeSourceFieldCoverageMinimumPercent"]
        self.assertEqual(stats["safeSourceRecordsBelowThreshold"], 1)
        self.assertEqual(stats["safeSourceRecordCount"], stats["safeSourceRecordsBelowThreshold"] + 58)

    def test_percentage_scale_explicit_in_policy(self) -> None:
        for gate_code in ("REQUIRED_FIELD_COVERAGE_GATE", "SAFE_SOURCE_COVERAGE_GATE", "REVIEW_RATIO_GATE", "WARNING_RATIO_GATE"):
            scale = self.policy["gateSemantics"][gate_code]["percentageScale"]
            self.assertEqual(scale, "0_TO_100")

    def test_synthetic_decision_ceiling_enforced(self) -> None:
        payload = self._assess(self.clean)
        self.assertEqual(payload["decision"], "READY_FOR_LIMITED_READ_VALIDATION")
        self.assertNotEqual(payload["decision"], "READY_FOR_READ_MIGRATION_CANDIDATE")

    def test_blocker_rich_remains_not_ready(self) -> None:
        if self.blocker_rich is None:
            self.skipTest("multi-site synthetic report unavailable")
        self.assertEqual(self._assess(self.blocker_rich)["decision"], "NOT_READY")

    def test_deterministic_byte_identical_output(self) -> None:
        one = json.dumps(self._assess(self.clean), indent=2, sort_keys=True)
        two = json.dumps(self._assess(self.clean), indent=2, sort_keys=True)
        self.assertEqual(one, two)

    def test_no_raw_identifiers_in_explanations(self) -> None:
        evidence = self.blocker_rich or self.clean
        payload = self._assess(evidence)
        text = json.dumps(payload["gateResults"]) + json.dumps(payload.get("coverageStatistics", {}))
        for token in ("SYNTH-DEV-", "ag-device-", "ag-point-"):
            self.assertNotIn(token, text)

    def test_gate_semantics_index_in_output(self) -> None:
        payload = self._assess(self.clean)
        self.assertEqual(payload["gateSemantics"], self.policy["gateSemantics"])


if __name__ == "__main__":
    unittest.main()
