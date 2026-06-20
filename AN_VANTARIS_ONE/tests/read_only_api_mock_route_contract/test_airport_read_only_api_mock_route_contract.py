from __future__ import annotations

import json
import unittest
from pathlib import Path

from industry_profiles.airport.read_only_api_mock_route_contract import build_airport_read_only_api_mock_route_contract
from read_only_api_mock_route_contract.validation import validate_boundary, validate_read_only_api_mock_route_contract

ROOT = Path(__file__).resolve().parents[3]


class AirportReadOnlyApiMockRouteContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = build_airport_read_only_api_mock_route_contract()
        self.summary = self.contract["summary"]

    def test_expected_counts(self) -> None:
        expected = {
            "mockRouteContractCount": 8,
            "localSmokeCaseCount": 8,
            "smokeGateCount": 15,
            "passedSmokeGateCount": 15,
            "blockingGateFailureCount": 0,
            "getRouteCount": 8,
            "readOnlyRouteCount": 8,
            "productionRouteEnabledCount": 0,
            "databaseAccessEnabledRouteCount": 0,
            "writeOperationEnabledRouteCount": 0,
            "runtimeActivationEnabledRouteCount": 0,
            "responseContractLinkedCount": 8,
            "authPolicyLinkedCount": 8,
            "expectedStatus200Count": 8,
            "expectedEnvelopeRequiredCount": 8,
            "expectedAuthRequiredCount": 8,
            "expectedPaginationSupportedCount": 8,
            "expectedFiltersSupportedCount": 8,
            "expectedFacetsSupportedCount": 8,
            "expectedNoWriteCount": 8,
            "networkCallRequiredCount": 0,
            "localhostCallRequiredCount": 0,
            "backendRouteImplementationCount": 0,
        }
        for key, value in expected.items():
            self.assertEqual(self.summary[key], value)

    def test_mock_routes_match_a7_contracts(self) -> None:
        response_contract = json.loads((ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-api-response-contract.v1.json").read_text(encoding="utf-8"))
        response_ids = {item["endpointResponseContractId"] for item in response_contract["endpointResponseContracts"]}
        auth_ids = {item["authPolicyContractId"] for item in response_contract["authPolicyContracts"]}
        for item in self.contract["mockRouteContracts"]:
            self.assertEqual(item["method"], "GET")
            self.assertEqual(item["routeMode"], "MOCK_CONTRACT_ONLY")
            self.assertTrue(item["readOnly"])
            self.assertFalse(item["productionRouteEnabled"])
            self.assertFalse(item["databaseAccessEnabled"])
            self.assertFalse(item["writeOperationEnabled"])
            self.assertFalse(item["runtimeActivationEnabled"])
            self.assertEqual(item["expectedStatusCodes"], [200])
            self.assertIn(item["responseContractId"], response_ids)
            self.assertIn(item["authPolicyContractId"], auth_ids)

    def test_local_smoke_cases_are_contract_only(self) -> None:
        for item in self.contract["localSmokeCases"]:
            self.assertEqual(item["method"], "GET")
            self.assertEqual(item["expectedStatusCode"], 200)
            self.assertTrue(item["expectedEnvelopeRequired"])
            self.assertTrue(item["expectedPaginationSupported"])
            self.assertTrue(item["expectedFiltersSupported"])
            self.assertTrue(item["expectedFacetsSupported"])
            self.assertTrue(item["expectedAuthRequired"])
            self.assertTrue(item["expectedReadOnly"])
            self.assertTrue(item["expectedNoWrite"])
            self.assertFalse(item["networkCallRequired"])
            self.assertFalse(item["localhostCallRequired"])

    def test_boundaries(self) -> None:
        for key in ("apiEnabled", "productionApiAllowed", "frontendEnabled", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "containsCustomerAssetIdentifiers", "airportSpecific"):
            self.assertFalse(self.summary[key])
        for key in ("databaseWriteCount", "canonicalWriteCount", "decisionWriteCount", "approvalWriteCount", "auditWriteCount"):
            self.assertEqual(self.summary[key], 0)
        self.assertTrue(self.summary["crossIndustry"])

    def test_smoke_gates_and_determinism(self) -> None:
        self.assertEqual(len(self.contract["smokeGateResults"]), 15)
        self.assertTrue(all(gate["status"] == "PASS" for gate in self.contract["smokeGateResults"]))
        gate_ids = [gate["gateId"] for gate in self.contract["smokeGateResults"]]
        self.assertEqual(gate_ids[0], "G01_MOCK_ROUTE_CONTRACT_COMPLETENESS")
        self.assertEqual(gate_ids[-1], "G15_MOCK_ROUTE_CONTRACT_DECISION")
        again = build_airport_read_only_api_mock_route_contract()
        self.assertEqual(json.dumps(self.contract, sort_keys=True, separators=(",", ":")), json.dumps(again, sort_keys=True, separators=(",", ":")))

    def test_no_identifier_leakage(self) -> None:
        serialized = json.dumps(self.contract, sort_keys=True)
        self.assertNotIn("deviceId", serialized)
        self.assertNotIn("assetId", serialized)
        self.assertNotIn("customerAssetIdentifier", serialized)

    def test_validation(self) -> None:
        validate_read_only_api_mock_route_contract(self.contract)
        self.assertEqual(self.contract["implementationStatus"], "READ_ONLY_API_MOCK_ROUTE_CONTRACT_AND_LOCAL_SMOKE_GATE_COMPLETE")
        self.assertEqual(self.contract["readinessOutcome"], "READ_ONLY_API_MOCK_ROUTE_CONTRACT_READY_FOR_FUTURE_ROUTE_IMPLEMENTATION")


class ReadOnlyApiMockRouteContractBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/read_only_api_mock_route_contract").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/read_only_api_mock_route_contract.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
