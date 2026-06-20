from __future__ import annotations

import json
import unittest
from pathlib import Path

from a3_readiness_gate.validation import validate_a3_readiness_release_gate, validate_boundary
from industry_profiles.airport.a3_readiness_release_gate import build_airport_a3_readiness_release_gate

ROOT = Path(__file__).resolve().parents[3]


class AirportA3ReadinessReleaseGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.release_gate = build_airport_a3_readiness_release_gate()
        self.summary = self.release_gate["summary"]
        self.stages = self.release_gate["stageResults"]
        self.gates = self.release_gate["gateResults"]
        self.decision = self.release_gate["releaseDecision"]

    def test_six_stages_and_markers(self) -> None:
        self.assertEqual(len(self.stages), 6)
        self.assertEqual(self.summary["a3StageCount"], 6)
        self.assertEqual(self.summary["passedStageCount"], 6)
        self.assertEqual(self.summary["failedStageCount"], 0)
        self.assertEqual(
            {stage["passMarker"] for stage in self.stages},
            {
                "ONE_AIRPORT_A3_01_CANONICAL_ALARM_EVENT_INTAKE_FOUNDATION_PASS",
                "ONE_AIRPORT_A3_02_ALARM_EVENT_ASSET_RESOLUTION_REVIEW_PROJECTION_PASS",
                "ONE_AIRPORT_A3_03_UFMS_FAULTCASE_CANDIDATE_PROJECTION_PASS",
                "ONE_AIRPORT_A3_04_WORKORDER_INTENT_CANDIDATE_PROJECTION_PASS",
                "ONE_AIRPORT_A3_05_EVIDENCE_LINKAGE_AND_INVESTIGATION_PROJECTION_PASS",
                "ONE_AIRPORT_A3_06_READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_PASS",
            },
        )

    def test_twelve_gates_pass(self) -> None:
        self.assertEqual(len(self.gates), 12)
        self.assertEqual(self.summary["gateCount"], 12)
        self.assertEqual(self.summary["passedGateCount"], 12)
        self.assertEqual(self.summary["blockingGateFailureCount"], 0)
        self.assertEqual(
            [gate["gateId"] for gate in self.gates],
            [
                "G01_A3_STAGE_COMPLETENESS",
                "G02_A3_PASS_MARKER_COMPLETENESS",
                "G03_A3_CANDIDATE_CHAIN_COMPLETENESS",
                "G04_A3_EVIDENCE_TOTAL_CONSISTENCY",
                "G05_A3_READ_ONLY_BOUNDARY",
                "G06_A3_RUNTIME_BOUNDARY",
                "G07_A3_UFMS_WORKORDER_BOUNDARY",
                "G08_A3_API_FRONTEND_BOUNDARY",
                "G09_A3_CUSTOMER_IDENTIFIER_SAFETY",
                "G10_A3_DETERMINISTIC_OUTPUT",
                "G11_A3_BOUNDARY_VALIDATOR",
                "G12_A3_RELEASE_DECISION",
            ],
        )
        self.assertTrue(all(gate["status"] == "PASS" for gate in self.gates))
        self.assertTrue(all(gate["blocking"] for gate in self.gates))

    def test_aggregated_counts(self) -> None:
        expected = {
            "alarmEventCandidateCount": 5,
            "resolutionRowCount": 5,
            "faultCaseCandidateCount": 5,
            "workOrderIntentCandidateCount": 5,
            "investigationCaseCount": 5,
            "operationsRowCount": 5,
            "totalDeviceEvidenceCount": 470,
            "decisionRequiredCount": 5,
            "reviewRequiredRowCount": 5,
        }
        for key, value in expected.items():
            self.assertEqual(self.summary[key], value)

    def test_boundaries_remain_closed(self) -> None:
        for key in (
            "runtimeObservedCount",
            "runtimeAlarmObservedCount",
            "ufmsFaultCaseCreatedCount",
            "workOrderIntentCreatedCount",
            "workOrderCreatedCount",
            "evidenceCenterWriteCount",
            "ummsWriteCount",
            "oneWorkManagementWriteCount",
            "canonicalWriteCount",
            "databaseWriteCount",
        ):
            self.assertEqual(self.summary[key], 0)
        self.assertFalse(self.summary["apiEnabled"])
        self.assertFalse(self.summary["frontendEnabled"])
        self.assertFalse(self.summary["containsCustomerAssetIdentifiers"])
        self.assertTrue(self.summary["crossIndustry"])
        self.assertFalse(self.summary["airportSpecific"])

    def test_release_decision(self) -> None:
        self.assertEqual(self.decision["decisionState"], "RELEASE_GATE_PASS")
        self.assertTrue(self.decision["releaseAllowed"])
        self.assertFalse(self.decision["pushAllowed"])
        self.assertFalse(self.decision["productionActivationAllowed"])
        self.assertFalse(self.decision["runtimeActivationAllowed"])
        self.assertFalse(self.decision["databaseWriteAllowed"])
        self.assertFalse(self.decision["apiEnabled"])
        self.assertFalse(self.decision["frontendEnabled"])

    def test_matrices(self) -> None:
        self.assertEqual(len(self.release_gate["regressionMatrix"]), 7)
        self.assertGreaterEqual(len(self.release_gate["boundaryMatrix"]), 15)
        self.assertTrue(all(entry["status"] == "PASS" for entry in self.release_gate["regressionMatrix"]))
        self.assertTrue(all(entry["status"] == "PASS" for entry in self.release_gate["boundaryMatrix"]))
        self.assertEqual(len(self.release_gate["artifactReferences"]), 6)

    def test_deterministic_release_gate(self) -> None:
        again = build_airport_a3_readiness_release_gate()
        self.assertEqual(self.release_gate["releaseGateId"], again["releaseGateId"])
        self.assertEqual(
            json.dumps(self.release_gate, sort_keys=True, separators=(",", ":")),
            json.dumps(again, sort_keys=True, separators=(",", ":")),
        )

    def test_projection_validation(self) -> None:
        validate_a3_readiness_release_gate(self.release_gate)
        self.assertEqual(
            self.release_gate["implementationStatus"],
            "A3_READINESS_AGGREGATION_AND_RELEASE_GATE_COMPLETE",
        )
        self.assertEqual(self.release_gate["readinessOutcome"], "A3_READ_ONLY_RELEASE_GATE_PASS")


class A3ReadinessBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/a3_readiness_gate").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/a3_readiness_release_gate.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
