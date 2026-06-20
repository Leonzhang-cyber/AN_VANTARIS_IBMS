from __future__ import annotations

import json
import unittest
from pathlib import Path

from api_frontend_implementation_gate.validation import validate_api_frontend_implementation_readiness_gate, validate_boundary
from industry_profiles.airport.api_frontend_implementation_gate import build_airport_api_frontend_implementation_readiness_gate

ROOT = Path(__file__).resolve().parents[3]


class ApiFrontendImplementationGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = build_airport_api_frontend_implementation_readiness_gate()
        self.summary = self.gate["summary"]

    def test_expected_counts(self) -> None:
        expected = {
            "apiEndpointCandidateCount": 8,
            "readOnlyEndpointCandidateCount": 8,
            "frontendPageCandidateCount": 8,
            "frontendRouteCandidateCount": 8,
            "dataBindingContractCount": 15,
            "cardBindingContractCount": 8,
            "queueBindingContractCount": 8,
            "authPolicyRequiredCount": 8,
            "contractReadinessGateCount": 15,
            "contractPassedGateCount": 15,
            "implementationReleaseGateCount": 16,
            "implementationPassedGateCount": 16,
            "blockingGateFailureCount": 0,
        }
        for key, value in expected.items():
            self.assertEqual(self.summary[key], value)

    def test_dependency_flags(self) -> None:
        self.assertTrue(self.summary["a5HandoffAllowed"])
        self.assertTrue(self.summary["a4ReleaseAllowed"])
        self.assertTrue(self.summary["a3ReleaseAllowed"])

    def test_implementation_decision(self) -> None:
        decision = self.gate["implementationDecision"]
        self.assertEqual(decision["decisionState"], "READY_FOR_READ_ONLY_SKELETON_PLANNING")
        self.assertTrue(decision["apiSkeletonPhaseAllowed"])
        self.assertTrue(decision["frontendSkeletonPhaseAllowed"])
        for key in ("productionApiAllowed", "productionFrontendAllowed", "databaseWriteAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed"):
            self.assertFalse(decision[key])

    def test_boundaries(self) -> None:
        for key in ("databaseWriteCount", "canonicalWriteCount", "decisionWriteCount", "approvalWriteCount", "auditWriteCount"):
            self.assertEqual(self.summary[key], 0)
        for key in ("productionApiAllowed", "productionFrontendAllowed", "databaseWriteAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "apiEnabled", "frontendEnabled", "containsCustomerAssetIdentifiers"):
            self.assertFalse(self.summary[key])
        self.assertTrue(self.summary["apiSkeletonPhaseAllowed"])
        self.assertTrue(self.summary["frontendSkeletonPhaseAllowed"])
        self.assertTrue(self.summary["crossIndustry"])
        self.assertFalse(self.summary["airportSpecific"])

    def test_readiness_objects(self) -> None:
        api = self.gate["apiImplementationReadiness"]
        frontend = self.gate["frontendImplementationReadiness"]
        self.assertEqual(api["candidateEndpointCount"], 8)
        self.assertEqual(api["readOnlyEndpointCandidateCount"], 8)
        self.assertEqual(api["endpointContractCoverageCount"], 8)
        self.assertEqual(api["authPolicyRequiredCount"], 8)
        self.assertFalse(api["implementationAllowed"])
        self.assertFalse(api["publicApiEnabled"])
        self.assertFalse(api["databaseAccessAllowed"])
        self.assertFalse(api["writeOperationAllowed"])
        self.assertTrue(api["skeletonPhaseAllowed"])
        self.assertEqual(frontend["pageCandidateCount"], 8)
        self.assertEqual(frontend["routeCandidateCount"], 8)
        self.assertEqual(frontend["cardCandidateCount"], 8)
        self.assertEqual(frontend["dataBindingContractCount"], 15)
        self.assertEqual(frontend["routeContractCoverageCount"], 8)
        self.assertFalse(frontend["implementationAllowed"])
        self.assertFalse(frontend["routeImplementationAllowed"])
        self.assertFalse(frontend["runtimeDataMutationAllowed"])
        self.assertTrue(frontend["skeletonPhaseAllowed"])

    def test_matrices_and_gates(self) -> None:
        self.assertTrue(all(entry["status"] == "PASS" for entry in self.gate["contractCoverageMatrix"]))
        self.assertTrue(all(entry["status"] == "PASS" for entry in self.gate["implementationBoundaryMatrix"]))
        self.assertEqual(len(self.gate["dependencyGateResults"]), 3)
        self.assertTrue(all(entry["status"] == "PASS" for entry in self.gate["dependencyGateResults"]))
        self.assertEqual(len(self.gate["releaseGateResults"]), 16)
        self.assertTrue(all(entry["status"] == "PASS" for entry in self.gate["releaseGateResults"]))

    def test_no_identifier_leakage(self) -> None:
        serialized = json.dumps(self.gate, sort_keys=True)
        self.assertNotIn("deviceId", serialized)
        self.assertNotIn("assetId", serialized)
        self.assertNotIn("customerAssetIdentifier", serialized)

    def test_deterministic_generation(self) -> None:
        again = build_airport_api_frontend_implementation_readiness_gate()
        self.assertEqual(
            json.dumps(self.gate, sort_keys=True, separators=(",", ":")),
            json.dumps(again, sort_keys=True, separators=(",", ":")),
        )

    def test_validation(self) -> None:
        validate_api_frontend_implementation_readiness_gate(self.gate)
        self.assertEqual(self.gate["implementationStatus"], "API_FRONTEND_IMPLEMENTATION_READINESS_RELEASE_GATE_COMPLETE")
        self.assertEqual(self.gate["readinessOutcome"], "API_FRONTEND_READY_FOR_READ_ONLY_SKELETON_PLANNING")


class ApiFrontendImplementationBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/api_frontend_implementation_gate").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/api_frontend_implementation_gate.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
