"""Tests for ONE-AIRPORT-GA-01 final International GA readiness release gate."""
from __future__ import annotations

import json
import unittest

from airport_international_ga_release_gate.validation import EXPECTED_SUMMARY, validate_airport_international_ga_release_gate
from industry_profiles.airport.airport_international_ga_release_gate import (
    IMPLEMENTATION_STATUS,
    READINESS_OUTCOME,
    build_airport_international_ga_release_gate,
)


class AirportInternationalGaReleaseGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = build_airport_international_ga_release_gate()

    def test_summary_freeze(self) -> None:
        self.assertEqual(EXPECTED_SUMMARY, self.gate["summary"])

    def test_contract_and_readiness_freeze(self) -> None:
        self.assertEqual("airport-international-ga-release-gate.v1", self.gate["contractVersion"])
        self.assertEqual(IMPLEMENTATION_STATUS, self.gate["implementationStatus"])
        self.assertEqual(READINESS_OUTCOME, self.gate["readinessOutcome"])

    def test_stage_aggregation(self) -> None:
        stages = self.gate["stageResults"]
        self.assertEqual(8, len(stages))
        self.assertEqual([f"A{index}" for index in range(1, 9)], [stage["stageId"] for stage in stages])
        self.assertTrue(all(stage["status"] == "PASS" for stage in stages))
        self.assertTrue(all(stage["passMarker"].startswith("ONE_AIRPORT_") for stage in stages))

    def test_business_capability_matrix(self) -> None:
        capabilities = self.gate["businessCapabilityMatrix"]
        self.assertEqual(15, len(capabilities))
        self.assertTrue(all(item["readOnly"] is True for item in capabilities))
        self.assertTrue(all(item["productionEnabled"] is False for item in capabilities))
        self.assertTrue(all(item["readinessState"] == "COMPLETE" for item in capabilities))

    def test_release_gates(self) -> None:
        release_gates = self.gate["releaseGateResults"]
        self.assertEqual(20, len(release_gates))
        self.assertTrue(all(item["status"] == "PASS" for item in release_gates))
        self.assertTrue(all(item["blocking"] is True for item in release_gates))

    def test_required_artifact_coverage(self) -> None:
        coverage = self.gate["artifactCoverageMatrix"]
        self.assertEqual(27, len(coverage))
        self.assertTrue(all(item["required"] is True for item in coverage))
        self.assertTrue(all(item["present"] is True for item in coverage))
        self.assertTrue(all(item["status"] == "PASS" for item in coverage))

    def test_release_decision(self) -> None:
        decision = self.gate["releaseDecision"]
        self.assertEqual("INTERNATIONAL_GA_READINESS_PASS", decision["decisionState"])
        self.assertIs(decision["internationalGaReadinessAllowed"], True)
        self.assertIs(decision["releaseCandidateAllowed"], True)
        for key in (
            "pushAllowed",
            "tagAllowed",
            "productionActivationAllowed",
            "runtimeActivationAllowed",
            "databaseWriteAllowed",
            "apiProductionAllowed",
            "frontendProductionAllowed",
            "approvalExecutionAllowed",
        ):
            self.assertIs(decision[key], False)

    def test_technical_boundaries_and_identifier_safety(self) -> None:
        boundaries = self.gate["technicalBoundaryMatrix"]
        self.assertTrue(boundaries)
        self.assertTrue(all(item["status"] == "PASS" for item in boundaries))
        serialized = json.dumps(self.gate, sort_keys=True)
        self.assertNotIn("customerAssetIdentifier", serialized)
        self.assertNotIn("assetId", serialized)
        self.assertNotIn("deviceId", serialized)

    def test_validator_accepts_gate(self) -> None:
        validate_airport_international_ga_release_gate(self.gate)


if __name__ == "__main__":
    unittest.main()
