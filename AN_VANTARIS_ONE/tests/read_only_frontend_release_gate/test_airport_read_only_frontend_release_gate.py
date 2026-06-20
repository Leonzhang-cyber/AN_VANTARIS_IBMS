from __future__ import annotations

import json
import unittest
from pathlib import Path

from industry_profiles.airport.read_only_frontend_release_gate import build_airport_read_only_frontend_release_gate
from read_only_frontend_release_gate.validation import validate_boundary, validate_read_only_frontend_release_gate

ROOT = Path(__file__).resolve().parents[3]


class AirportReadOnlyFrontendReleaseGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = build_airport_read_only_frontend_release_gate()
        self.summary = self.gate["summary"]

    def test_expected_counts(self) -> None:
        expected = {
            "a8StageCount": 2,
            "passedStageCount": 2,
            "failedStageCount": 0,
            "pageCount": 8,
            "pageSkeletonCount": 8,
            "pageContractCount": 8,
            "routeSkeletonCount": 8,
            "layoutContractCount": 8,
            "componentCoverageEntryCount": 8,
            "interactionCoverageEntryCount": 8,
            "releaseGateCount": 17,
            "passedGateCount": 17,
            "blockingGateFailureCount": 0,
            "componentBindingContractCount": 24,
            "uiStateContractCount": 48,
            "interactionContractCount": 64,
            "dataBindingSkeletonCount": 8,
            "cardSkeletonCount": 8,
            "queueSkeletonCount": 8,
            "staticOnlyPageCount": 8,
            "readOnlyPageCount": 8,
            "productionEnabledPageCount": 0,
            "productionRouteEnabledCount": 0,
            "realFrontendFileChangeCount": 0,
            "realMenuEntryChangeCount": 0,
            "liveApiCallEnabledCount": 0,
            "browserLaunchRequiredCount": 0,
            "networkCallRequiredCount": 0,
            "localhostCallRequiredCount": 0,
            "mutationAllowedInteractionCount": 0,
        }
        for key, value in expected.items():
            self.assertEqual(self.summary[key], value)

    def test_stage_and_coverage_results(self) -> None:
        self.assertEqual(len(self.gate["stageResults"]), 2)
        self.assertTrue(all(stage["status"] == "PASS" for stage in self.gate["stageResults"]))
        markers = {stage["passMarker"] for stage in self.gate["stageResults"]}
        self.assertEqual(markers, {"ONE_AIRPORT_A8_01_READ_ONLY_FRONTEND_SKELETON_FOUNDATION_PASS", "ONE_AIRPORT_A8_02_READ_ONLY_FRONTEND_PAGE_CONTRACT_AND_LOCAL_SMOKE_GATE_PASS"})
        for entry in self.gate["pageCoverageMatrix"]:
            self.assertEqual(entry["status"], "PASS")
            self.assertTrue(entry["pageSkeletonPresent"])
            self.assertTrue(entry["pageContractPresent"])
            self.assertTrue(entry["layoutContractPresent"])
            self.assertTrue(entry["routeSkeletonPresent"])
            self.assertTrue(entry["routeProductionDisabled"])
            self.assertTrue(entry["staticOnly"])
            self.assertTrue(entry["readOnly"])
            self.assertTrue(entry["liveApiCallDisabled"])
            self.assertTrue(entry["dataMutationDisabled"])

    def test_component_and_interaction_coverage(self) -> None:
        for entry in self.gate["componentCoverageMatrix"]:
            self.assertEqual(entry["status"], "PASS")
            self.assertEqual(entry["componentBindingCount"], 3)
            self.assertEqual(entry["uiStateContractCount"], 6)
            self.assertEqual(entry["interactionContractCount"], 8)
            self.assertTrue(entry["dataBindingPresent"])
            self.assertTrue(entry["cardBindingPresent"])
            self.assertTrue(entry["queueBindingPresent"])
        for entry in self.gate["interactionCoverageMatrix"]:
            self.assertEqual(entry["status"], "PASS")
            self.assertTrue(entry["filterSupported"])
            self.assertTrue(entry["facetSupported"])
            self.assertTrue(entry["paginationSupported"])
            self.assertTrue(entry["sortSupported"])
            self.assertTrue(entry["searchSupported"])
            self.assertTrue(entry["viewDetailsSupported"])
            self.assertTrue(entry["exportDisabled"])
            self.assertTrue(entry["approvalDisabled"])
            self.assertFalse(entry["mutationAllowed"])

    def test_release_gates_dependencies_and_decision(self) -> None:
        self.assertEqual(len(self.gate["releaseGateResults"]), 17)
        self.assertTrue(all(gate["status"] == "PASS" for gate in self.gate["releaseGateResults"]))
        self.assertTrue(all(gate["status"] == "PASS" for gate in self.gate["dependencyGateResults"]))
        decision = self.gate["implementationDecision"]
        self.assertEqual(decision["decisionState"], "READY_FOR_READ_ONLY_FRONTEND_IMPLEMENTATION")
        self.assertTrue(decision["readOnlyFrontendImplementationAllowed"])
        for key in ("productionFrontendAllowed", "realRouteImplementationAllowed", "menuImplementationAllowed", "liveApiCallAllowed", "dataMutationAllowed", "browserSmokeAllowed", "databaseWriteAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "apiImplementationRequired", "pushAllowed"):
            self.assertFalse(decision[key])
            self.assertFalse(self.summary[key])

    def test_boundaries(self) -> None:
        for key in ("apiEnabled", "frontendEnabled", "productionFrontendAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "containsCustomerAssetIdentifiers", "airportSpecific"):
            self.assertFalse(self.summary[key])
        for key in ("databaseWriteCount", "canonicalWriteCount", "decisionWriteCount", "approvalWriteCount", "auditWriteCount"):
            self.assertEqual(self.summary[key], 0)
        self.assertTrue(self.summary["crossIndustry"])

    def test_no_identifier_leakage(self) -> None:
        serialized = json.dumps(self.gate, sort_keys=True)
        self.assertNotIn("deviceId", serialized)
        self.assertNotIn("assetId", serialized)
        self.assertNotIn("customerAssetIdentifier", serialized)

    def test_determinism_and_validation(self) -> None:
        validate_read_only_frontend_release_gate(self.gate)
        again = build_airport_read_only_frontend_release_gate()
        self.assertEqual(json.dumps(self.gate, sort_keys=True, separators=(",", ":")), json.dumps(again, sort_keys=True, separators=(",", ":")))
        self.assertEqual(self.gate["implementationStatus"], "READ_ONLY_FRONTEND_IMPLEMENTATION_RELEASE_GATE_COMPLETE")
        self.assertEqual(self.gate["readinessOutcome"], "READ_ONLY_FRONTEND_READY_FOR_FUTURE_UI_IMPLEMENTATION")


class ReadOnlyFrontendReleaseGateBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/read_only_frontend_release_gate").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/read_only_frontend_release_gate.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
