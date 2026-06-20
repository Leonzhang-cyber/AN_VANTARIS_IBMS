from __future__ import annotations

import json
import unittest
from pathlib import Path

from industry_profiles.airport.read_only_api_response_contract import build_airport_read_only_api_response_contract
from read_only_api_response_contract.validation import validate_boundary, validate_read_only_api_response_contract

ROOT = Path(__file__).resolve().parents[3]


class AirportReadOnlyApiResponseContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = build_airport_read_only_api_response_contract()
        self.summary = self.contract["summary"]

    def test_expected_counts(self) -> None:
        expected = {
            "endpointResponseContractCount": 8,
            "paginationContractCount": 8,
            "filterContractCount": 8,
            "facetContractCount": 8,
            "errorContractCount": 8,
            "authPolicyContractCount": 8,
            "readinessGateCount": 17,
            "passedGateCount": 17,
            "blockingGateFailureCount": 0,
            "getEndpointCount": 8,
            "readOnlyEndpointCount": 8,
            "envelopeRequiredCount": 8,
            "paginationSupportedCount": 8,
            "filtersSupportedCount": 8,
            "facetsSupportedCount": 8,
            "stableContinuationTokenRequiredCount": 8,
            "deterministicOrderingRequiredCount": 8,
            "authRequiredCount": 8,
            "rolePolicyRequiredCount": 8,
            "anonymousAccessAllowedCount": 0,
            "noStackTraceLeakageCount": 8,
            "noCredentialLeakageCount": 8,
            "apiSkeletonEndpointCount": 8,
        }
        for key, value in expected.items():
            self.assertEqual(self.summary[key], value)

    def test_endpoint_contracts(self) -> None:
        for item in self.contract["endpointResponseContracts"]:
            self.assertEqual(item["method"], "GET")
            self.assertTrue(item["readOnly"])
            self.assertTrue(item["envelopeRequired"])
            self.assertTrue(item["paginationSupported"])
            self.assertTrue(item["filtersSupported"])
            self.assertTrue(item["facetsSupported"])
            self.assertFalse(item["containsCustomerAssetIdentifiers"])

    def test_pagination_filter_facet_contracts(self) -> None:
        for item in self.contract["paginationContracts"]:
            self.assertTrue(item["supported"])
            self.assertEqual(item["defaultPageSize"], 25)
            self.assertGreaterEqual(item["maxPageSize"], 100)
            self.assertTrue(item["stableContinuationTokenRequired"])
            self.assertTrue(item["deterministicOrderingRequired"])
        self.assertEqual(len(self.contract["filterContracts"]), 8)
        self.assertEqual(len(self.contract["facetContracts"]), 8)
        for item in self.contract["filterContracts"] + self.contract["facetContracts"]:
            self.assertTrue(item["supported"])
            self.assertTrue(item["deterministic"])
            self.assertGreaterEqual(len(item.get("filterKeys", item.get("facetKeys", []))), 3)

    def test_error_and_auth_contracts(self) -> None:
        for item in self.contract["errorContracts"]:
            self.assertEqual(item["errorShape"], "STANDARD_ERROR_ENVELOPE")
            self.assertEqual(item["allowedStatusCodes"], [400, 401, 403, 404, 500])
            self.assertTrue(item["noStackTraceLeakage"])
            self.assertTrue(item["noCredentialLeakage"])
        for item in self.contract["authPolicyContracts"]:
            self.assertTrue(item["authRequired"])
            self.assertTrue(item["rolePolicyRequired"])
            self.assertFalse(item["anonymousAccessAllowed"])
            self.assertTrue({"OPERATOR", "ENGINEER", "ADMIN"}.issubset(set(item["allowedRoles"])))

    def test_boundaries(self) -> None:
        for key in ("apiEnabled", "productionApiAllowed", "databaseAccessEnabled", "frontendEnabled", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "containsCustomerAssetIdentifiers"):
            self.assertFalse(self.summary[key])
        for key in ("databaseWriteCount", "writeOperationEnabledCount", "canonicalWriteCount", "decisionWriteCount", "approvalWriteCount", "auditWriteCount"):
            self.assertEqual(self.summary[key], 0)
        self.assertTrue(self.summary["crossIndustry"])
        self.assertFalse(self.summary["airportSpecific"])

    def test_gates_and_determinism(self) -> None:
        self.assertEqual(len(self.contract["responseReadinessGates"]), 17)
        self.assertTrue(all(gate["status"] == "PASS" for gate in self.contract["responseReadinessGates"]))
        again = build_airport_read_only_api_response_contract()
        self.assertEqual(json.dumps(self.contract, sort_keys=True, separators=(",", ":")), json.dumps(again, sort_keys=True, separators=(",", ":")))

    def test_no_identifier_leakage(self) -> None:
        serialized = json.dumps(self.contract, sort_keys=True)
        self.assertNotIn("deviceId", serialized)
        self.assertNotIn("assetId", serialized)
        self.assertNotIn("customerAssetIdentifier", serialized)

    def test_validation(self) -> None:
        validate_read_only_api_response_contract(self.contract)
        self.assertEqual(self.contract["implementationStatus"], "READ_ONLY_API_RESPONSE_CONTRACT_AND_VALIDATION_GATE_COMPLETE")
        self.assertEqual(self.contract["readinessOutcome"], "READ_ONLY_API_RESPONSE_CONTRACT_READY_FOR_FUTURE_ROUTE_IMPLEMENTATION")


class ReadOnlyApiResponseContractBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/read_only_api_response_contract").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/read_only_api_response_contract.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
