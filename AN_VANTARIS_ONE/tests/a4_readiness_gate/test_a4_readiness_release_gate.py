from __future__ import annotations

import json
import unittest
from pathlib import Path

from a4_readiness_gate.validation import validate_a4_readiness_release_gate, validate_boundary
from industry_profiles.airport.a4_readiness_release_gate import build_airport_a4_readiness_release_gate

ROOT = Path(__file__).resolve().parents[3]


class AirportA4ReadinessReleaseGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.release_gate = build_airport_a4_readiness_release_gate()
        self.summary = self.release_gate["summary"]
        self.stages = self.release_gate["stageResults"]
        self.gates = self.release_gate["gateResults"]
        self.decision = self.release_gate["releaseDecision"]

    def test_stage_and_gate_counts(self) -> None:
        self.assertEqual(self.summary["a4StageCount"], 3)
        self.assertEqual(self.summary["passedStageCount"], 3)
        self.assertEqual(self.summary["failedStageCount"], 0)
        self.assertEqual(self.summary["gateCount"], 15)
        self.assertEqual(self.summary["passedGateCount"], 15)
        self.assertEqual(self.summary["blockingGateFailureCount"], 0)
        self.assertEqual(len(self.stages), 3)
        self.assertEqual(len(self.gates), 15)

    def test_expected_counts(self) -> None:
        expected = {
            "decisionItemCount": 46,
            "queueRowCount": 46,
            "queueGroupCount": 8,
            "queueCardCount": 8,
            "policyGuardResultCount": 46,
            "auditPreviewCount": 46,
            "guardGroupCount": 8,
            "pendingDecisionCount": 46,
            "blockingDecisionCount": 45,
            "nonBlockingDecisionCount": 1,
            "eligibleForPreviewCount": 46,
            "eligibleForExecutionCount": 0,
            "blockedByPolicyCount": 46,
            "affectedSourceSystemCount": 5,
            "totalDeviceEvidenceCount": 470,
        }
        for key, value in expected.items():
            self.assertEqual(self.summary[key], value)

    def test_boundaries(self) -> None:
        for key in ("decisionWriteCount", "approvalWriteCount", "auditWriteCount", "canonicalWriteCount", "databaseWriteCount"):
            self.assertEqual(self.summary[key], 0)
        for key in ("apiEnabled", "frontendEnabled", "pushAllowed", "productionActivationAllowed", "runtimeActivationAllowed", "containsCustomerAssetIdentifiers"):
            self.assertFalse(self.summary[key])
        self.assertTrue(self.summary["crossIndustry"])
        self.assertFalse(self.summary["airportSpecific"])

    def test_release_decision(self) -> None:
        self.assertEqual(self.decision["decisionState"], "RELEASE_GATE_PASS")
        self.assertTrue(self.decision["releaseAllowed"])
        for key in (
            "pushAllowed",
            "productionActivationAllowed",
            "runtimeActivationAllowed",
            "databaseWriteAllowed",
            "apiEnabled",
            "frontendEnabled",
            "decisionWriteAllowed",
            "approvalWriteAllowed",
            "auditWriteAllowed",
        ):
            self.assertFalse(self.decision[key])

    def test_pass_markers_and_gates(self) -> None:
        self.assertEqual(
            {stage["passMarker"] for stage in self.stages},
            {
                "ONE_AIRPORT_A4_01_OPERATOR_REVIEW_DECISION_LAYER_FOUNDATION_PASS",
                "ONE_AIRPORT_A4_02_OPERATOR_REVIEW_UCONSOLE_QUEUE_PROJECTION_PASS",
                "ONE_AIRPORT_A4_03_OPERATOR_REVIEW_DECISION_AUDIT_AND_POLICY_GUARD_PASS",
            },
        )
        self.assertTrue(all(stage["status"] == "PASS" for stage in self.stages))
        self.assertTrue(all(gate["status"] == "PASS" for gate in self.gates))

    def test_deterministic_projection(self) -> None:
        again = build_airport_a4_readiness_release_gate()
        self.assertEqual(self.release_gate["releaseGateId"], again["releaseGateId"])
        self.assertEqual(
            json.dumps(self.release_gate, sort_keys=True, separators=(",", ":")),
            json.dumps(again, sort_keys=True, separators=(",", ":")),
        )

    def test_validation(self) -> None:
        validate_a4_readiness_release_gate(self.release_gate)
        self.assertEqual(self.release_gate["implementationStatus"], "A4_OPERATOR_REVIEW_READINESS_AND_RELEASE_GATE_COMPLETE")
        self.assertEqual(self.release_gate["readinessOutcome"], "A4_OPERATOR_REVIEW_READ_ONLY_RELEASE_GATE_PASS")


class A4ReadinessBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/a4_readiness_gate").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/a4_readiness_release_gate.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
