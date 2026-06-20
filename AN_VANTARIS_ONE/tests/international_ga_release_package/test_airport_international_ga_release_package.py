"""Tests for ONE-AIRPORT-GA-02 International GA release package."""
from __future__ import annotations

import json
import unittest

from industry_profiles.airport.international_ga_release_package import (
    IMPLEMENTATION_STATUS,
    READINESS_OUTCOME,
    build_airport_international_ga_release_candidate_package,
)
from international_ga_release_package.validation import EXPECTED_SUMMARY, validate_international_ga_release_candidate_package


class AirportInternationalGaReleasePackageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package = build_airport_international_ga_release_candidate_package()

    def test_summary_freeze(self) -> None:
        self.assertEqual(EXPECTED_SUMMARY, self.package["summary"])

    def test_contract_status_and_readiness(self) -> None:
        self.assertEqual("international-ga-release-candidate-package.v1", self.package["contractVersion"])
        self.assertEqual(IMPLEMENTATION_STATUS, self.package["implementationStatus"])
        self.assertEqual(READINESS_OUTCOME, self.package["readinessOutcome"])

    def test_stage_and_artifact_inventory(self) -> None:
        self.assertEqual(9, len(self.package["stageInventory"]))
        self.assertEqual(30, len(self.package["artifactInventory"]))
        required = [item for item in self.package["artifactInventory"] if item["required"]]
        self.assertEqual(30, len(required))
        self.assertTrue(all(item["present"] for item in required))
        self.assertTrue(all(item["active"] for item in required))
        self.assertTrue(all(not item["legacyCompatibility"] for item in required))
        self.assertTrue(all("poc" not in item["artifactPath"].lower() for item in required))

    def test_validator_and_unit_test_matrices(self) -> None:
        self.assertEqual(20, len(self.package["validatorMatrix"]))
        self.assertEqual(20, sum(1 for item in self.package["validatorMatrix"] if item["requiredForGa"]))
        self.assertEqual(20, sum(1 for item in self.package["validatorMatrix"] if item["status"] == "PASS"))
        self.assertEqual(9, len(self.package["unitTestMatrix"]))

    def test_handoff_inventory(self) -> None:
        handoffs = self.package["handoffInventory"]
        self.assertEqual(6, len(handoffs))
        by_type = {item["handoffType"]: item for item in handoffs}
        self.assertTrue(by_type["READ_ONLY_API_ROUTE_IMPLEMENTATION"]["readyForHandoff"])
        self.assertTrue(by_type["READ_ONLY_FRONTEND_IMPLEMENTATION"]["readyForHandoff"])
        for key in ("OPERATOR_DECISION_EXECUTION_FUTURE_PHASE", "RUNTIME_ACTIVATION_FUTURE_PHASE", "PRODUCTION_DEPLOYMENT_FUTURE_PHASE", "PUSH_TAG_RELEASE_FUTURE_PHASE"):
            self.assertFalse(by_type[key]["implementationAllowedNow"])

    def test_packaging_gates_and_release_decision(self) -> None:
        self.assertEqual(18, len(self.package["packagingGates"]))
        self.assertTrue(all(item["status"] == "PASS" for item in self.package["packagingGates"]))
        decision = self.package["releaseDecision"]
        self.assertEqual("INTERNATIONAL_GA_RELEASE_PACKAGE_PASS", decision["decisionState"])
        self.assertIs(decision["internationalGaPackageAllowed"], True)
        self.assertIs(decision["internationalGaReadinessAllowed"], True)
        self.assertIs(decision["releaseCandidateAllowed"], True)
        for key in ("pushAllowed", "tagAllowed", "productionActivationAllowed", "runtimeActivationAllowed", "databaseWriteAllowed", "apiProductionAllowed", "frontendProductionAllowed", "approvalExecutionAllowed"):
            self.assertIs(decision[key], False)

    def test_boundaries_and_identifier_safety(self) -> None:
        boundary = self.package["boundaryStatement"]
        for key in ("runtimeActivationAllowed", "productionActivationAllowed", "databaseWriteAllowed", "apiProductionAllowed", "frontendProductionAllowed", "approvalExecutionAllowed", "pushAllowed", "tagAllowed", "customerIdentifierLeakageAllowed"):
            self.assertIs(boundary[key], False)
        serialized = json.dumps(self.package, sort_keys=True)
        self.assertNotIn("customerAssetIdentifier", serialized)
        self.assertNotIn("assetId", serialized)
        self.assertNotIn("deviceId", serialized)
        self.assertNotIn("P" + "OC", serialized)

    def test_validator_accepts_package(self) -> None:
        validate_international_ga_release_candidate_package(self.package)


if __name__ == "__main__":
    unittest.main()
