from __future__ import annotations

import json
import unittest
from pathlib import Path

from api_frontend_readiness_contract.validation import validate_api_frontend_readiness_contract, validate_boundary
from industry_profiles.airport.api_frontend_readiness_contract import build_airport_api_frontend_readiness_contract

ROOT = Path(__file__).resolve().parents[3]


class ApiFrontendReadinessContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = build_airport_api_frontend_readiness_contract()
        self.summary = self.contract["summary"]

    def test_expected_counts(self) -> None:
        expected = {
            "apiEndpointCandidateCount": 8,
            "frontendPageCandidateCount": 8,
            "frontendRouteCandidateCount": 8,
            "dataBindingContractCount": 15,
            "cardBindingContractCount": 8,
            "queueBindingContractCount": 8,
            "readinessGateCount": 15,
            "passedGateCount": 15,
            "blockingGateFailureCount": 0,
            "readOnlyEndpointCandidateCount": 8,
            "apiImplementationAllowedCount": 0,
            "frontendImplementationAllowedCount": 0,
            "routeImplementationAllowedCount": 0,
            "databaseAccessAllowedCount": 0,
            "writeOperationAllowedCount": 0,
            "authPolicyRequiredCount": 8,
            "pageCandidateCount": 8,
            "cardCandidateCount": 8,
        }
        for key, value in expected.items():
            self.assertEqual(self.summary[key], value)

    def test_inherited_counts(self) -> None:
        expected = {
            "sourceSystemCandidateCount": 5,
            "alarmEventCandidateCount": 5,
            "faultCaseCandidateCount": 5,
            "workOrderIntentCandidateCount": 5,
            "investigationCaseCount": 5,
            "decisionItemCount": 46,
            "queueRowCount": 46,
            "totalDeviceEvidenceCount": 470,
        }
        for key, value in expected.items():
            self.assertEqual(self.summary[key], value)

    def test_endpoint_boundaries(self) -> None:
        self.assertEqual({item["method"] for item in self.contract["apiEndpointCandidates"]}, {"GET"})
        for endpoint in self.contract["apiEndpointCandidates"]:
            self.assertTrue(endpoint["readOnly"])
            self.assertFalse(endpoint["implementationAllowed"])
            self.assertFalse(endpoint["publicApiEnabled"])
            self.assertFalse(endpoint["databaseAccessAllowed"])
            self.assertFalse(endpoint["writeOperationAllowed"])
            self.assertTrue(endpoint["authPolicyRequired"])
            self.assertEqual(endpoint["responseContractState"], "FROZEN_FOR_PLANNING")

    def test_frontend_candidate_boundaries(self) -> None:
        for page in self.contract["frontendPageCandidates"]:
            self.assertFalse(page["implementationAllowed"])
            self.assertFalse(page["routeImplementationAllowed"])
            self.assertFalse(page["runtimeDataMutationAllowed"])
            self.assertIn(page["readinessState"], {"READY_FOR_IMPLEMENTATION_PLANNING", "FROZEN_FOR_PLANNING"})
        for route in self.contract["frontendRouteCandidates"]:
            self.assertFalse(route["implementationAllowed"])
            self.assertFalse(route["runtimeDataMutationAllowed"])

    def test_binding_counts_and_read_only(self) -> None:
        self.assertEqual(len(self.contract["dataBindingContracts"]), 15)
        self.assertEqual(len(self.contract["cardBindingContracts"]), 8)
        self.assertEqual(len(self.contract["queueBindingContracts"]), 8)
        for collection in ("dataBindingContracts", "cardBindingContracts", "queueBindingContracts"):
            self.assertTrue(all(item["readOnly"] for item in self.contract[collection]))

    def test_summary_boundaries(self) -> None:
        for key in ("databaseWriteCount", "canonicalWriteCount", "decisionWriteCount", "approvalWriteCount", "auditWriteCount"):
            self.assertEqual(self.summary[key], 0)
        for key in ("apiEnabled", "frontendEnabled", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "containsCustomerAssetIdentifiers"):
            self.assertFalse(self.summary[key])
        self.assertTrue(self.summary["crossIndustry"])
        self.assertFalse(self.summary["airportSpecific"])

    def test_readiness_gates_pass(self) -> None:
        self.assertEqual(len(self.contract["readinessGates"]), 15)
        self.assertTrue(all(gate["status"] == "PASS" for gate in self.contract["readinessGates"]))
        self.assertTrue(all(gate["blocking"] for gate in self.contract["readinessGates"]))

    def test_deterministic_generation(self) -> None:
        again = build_airport_api_frontend_readiness_contract()
        self.assertEqual(
            json.dumps(self.contract, sort_keys=True, separators=(",", ":")),
            json.dumps(again, sort_keys=True, separators=(",", ":")),
        )

    def test_no_identifier_leakage(self) -> None:
        serialized = json.dumps(self.contract, sort_keys=True)
        self.assertNotIn("deviceId", serialized)
        self.assertNotIn("assetId", serialized)
        self.assertNotIn("customerAssetIdentifier", serialized)

    def test_validation(self) -> None:
        validate_api_frontend_readiness_contract(self.contract)
        self.assertEqual(self.contract["implementationStatus"], "API_FRONTEND_READINESS_CONTRACT_FREEZE_COMPLETE")
        self.assertEqual(self.contract["readinessOutcome"], "API_FRONTEND_CONTRACT_FROZEN_FOR_FUTURE_IMPLEMENTATION_PLANNING")


class ApiFrontendReadinessBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/api_frontend_readiness_contract").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/api_frontend_readiness_contract.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
