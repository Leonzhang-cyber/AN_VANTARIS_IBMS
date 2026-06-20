from __future__ import annotations

import json
import unittest
from pathlib import Path

from industry_profiles.airport.read_only_api_release_gate import build_airport_read_only_api_release_gate
from read_only_api_release_gate.validation import validate_boundary, validate_read_only_api_release_gate

ROOT = Path(__file__).resolve().parents[3]


class AirportReadOnlyApiReleaseGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = build_airport_read_only_api_release_gate()
        self.summary = self.gate["summary"]

    def test_expected_counts(self) -> None:
        expected = {
            "a7StageCount": 3,
            "passedStageCount": 3,
            "failedStageCount": 0,
            "endpointCount": 8,
            "endpointSkeletonCount": 8,
            "endpointResponseContractCount": 8,
            "paginationContractCount": 8,
            "filterContractCount": 8,
            "facetContractCount": 8,
            "errorContractCount": 8,
            "authPolicyContractCount": 8,
            "mockRouteContractCount": 8,
            "localSmokeCaseCount": 8,
            "coverageEntryCount": 8,
            "mockRouteCoverageEntryCount": 8,
            "releaseGateCount": 19,
            "passedGateCount": 19,
            "blockingGateFailureCount": 0,
            "getEndpointCount": 8,
            "readOnlyEndpointCount": 8,
            "readOnlyRouteCount": 8,
            "authRequiredCount": 8,
            "rolePolicyRequiredCount": 8,
            "networkCallRequiredCount": 0,
            "localhostCallRequiredCount": 0,
            "backendRouteImplementationCount": 0,
            "productionEnabledEndpointCount": 0,
            "databaseAccessEnabledEndpointCount": 0,
            "writeOperationEnabledEndpointCount": 0,
            "runtimeActivationEnabledEndpointCount": 0,
        }
        for key, value in expected.items():
            self.assertEqual(self.summary[key], value)

    def test_stage_results_and_pass_markers(self) -> None:
        self.assertEqual(len(self.gate["stageResults"]), 3)
        markers = {item["passMarker"] for item in self.gate["stageResults"]}
        self.assertEqual(
            markers,
            {
                "ONE_AIRPORT_A7_01_READ_ONLY_API_SKELETON_FOUNDATION_PASS",
                "ONE_AIRPORT_A7_02_READ_ONLY_API_RESPONSE_CONTRACT_AND_VALIDATION_GATE_PASS",
                "ONE_AIRPORT_A7_03_READ_ONLY_API_MOCK_ROUTE_CONTRACT_AND_LOCAL_SMOKE_GATE_PASS",
            },
        )
        self.assertTrue(all(item["status"] == "PASS" for item in self.gate["stageResults"]))

    def test_coverage_matrices(self) -> None:
        self.assertEqual(len(self.gate["apiContractCoverageMatrix"]), 8)
        self.assertEqual(len(self.gate["mockRouteCoverageMatrix"]), 8)
        for item in self.gate["apiContractCoverageMatrix"]:
            self.assertTrue(item["endpointSkeletonPresent"])
            self.assertTrue(item["responseContractPresent"])
            self.assertTrue(item["paginationContractPresent"])
            self.assertTrue(item["filterContractPresent"])
            self.assertTrue(item["facetContractPresent"])
            self.assertTrue(item["errorContractPresent"])
            self.assertTrue(item["authPolicyContractPresent"])
            self.assertTrue(item["mockRouteContractPresent"])
            self.assertTrue(item["localSmokeCasePresent"])
            self.assertEqual(item["status"], "PASS")
        for item in self.gate["mockRouteCoverageMatrix"]:
            self.assertEqual(item["method"], "GET")
            self.assertTrue(item["responseContractLinked"])
            self.assertTrue(item["authPolicyLinked"])
            self.assertTrue(item["localSmokeDefined"])
            self.assertFalse(item["networkCallRequired"])
            self.assertFalse(item["localhostCallRequired"])
            self.assertFalse(item["productionRouteEnabled"])
            self.assertEqual(item["status"], "PASS")

    def test_release_gates_and_dependencies(self) -> None:
        self.assertEqual(len(self.gate["releaseGateResults"]), 19)
        self.assertTrue(all(item["status"] == "PASS" for item in self.gate["releaseGateResults"]))
        self.assertEqual(self.gate["releaseGateResults"][0]["gateId"], "G01_A7_STAGE_COMPLETENESS")
        self.assertEqual(self.gate["releaseGateResults"][-1]["gateId"], "G19_IMPLEMENTATION_DECISION")
        self.assertTrue(all(item["status"] == "PASS" for item in self.gate["dependencyGateResults"]))

    def test_implementation_decision(self) -> None:
        decision = self.gate["implementationDecision"]
        self.assertEqual(decision["decisionState"], "READY_FOR_READ_ONLY_ROUTE_IMPLEMENTATION")
        self.assertTrue(decision["readOnlyApiRouteImplementationAllowed"])
        for key in ("productionApiAllowed", "backendRouteImplementationAllowed", "databaseAccessAllowed", "writeOperationAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "frontendImplementationAllowed", "pushAllowed"):
            self.assertFalse(decision[key])
            self.assertFalse(self.summary[key])

    def test_boundaries(self) -> None:
        for key in ("productionApiAllowed", "backendRouteImplementationAllowed", "databaseAccessAllowed", "writeOperationAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "frontendImplementationAllowed", "pushAllowed", "apiEnabled", "frontendEnabled", "containsCustomerAssetIdentifiers", "airportSpecific"):
            self.assertFalse(self.summary[key])
        for key in ("databaseWriteCount", "canonicalWriteCount", "decisionWriteCount", "approvalWriteCount", "auditWriteCount"):
            self.assertEqual(self.summary[key], 0)
        self.assertTrue(self.summary["readOnlyApiRouteImplementationAllowed"])
        self.assertTrue(self.summary["crossIndustry"])

    def test_no_identifier_leakage(self) -> None:
        serialized = json.dumps(self.gate, sort_keys=True)
        self.assertNotIn("deviceId", serialized)
        self.assertNotIn("assetId", serialized)
        self.assertNotIn("customerAssetIdentifier", serialized)

    def test_determinism_and_validation(self) -> None:
        validate_read_only_api_release_gate(self.gate)
        again = build_airport_read_only_api_release_gate()
        self.assertEqual(json.dumps(self.gate, sort_keys=True, separators=(",", ":")), json.dumps(again, sort_keys=True, separators=(",", ":")))
        self.assertEqual(self.gate["implementationStatus"], "READ_ONLY_API_IMPLEMENTATION_RELEASE_GATE_COMPLETE")
        self.assertEqual(self.gate["readinessOutcome"], "READ_ONLY_API_READY_FOR_FUTURE_ROUTE_IMPLEMENTATION")


class ReadOnlyApiReleaseGateBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/read_only_api_release_gate").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/read_only_api_release_gate.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
