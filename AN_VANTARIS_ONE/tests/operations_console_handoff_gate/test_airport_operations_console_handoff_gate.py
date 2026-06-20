from __future__ import annotations

import json
import unittest
from pathlib import Path

from industry_profiles.airport.operations_console_handoff_gate import build_airport_operations_console_handoff_gate
from operations_console_handoff_gate.validation import validate_boundary, validate_operations_console_handoff_gate

ROOT = Path(__file__).resolve().parents[3]


class AirportOperationsConsoleHandoffGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = build_airport_operations_console_handoff_gate()
        self.summary = self.gate["summary"]

    def test_expected_counts(self) -> None:
        expected = {
            "pageHandoffCount": 8,
            "dataSourceHandoffCount": 15,
            "cardHandoffCount": 8,
            "releaseGateCount": 15,
            "passedGateCount": 15,
            "blockingGateFailureCount": 0,
            "candidateEndpointCount": 8,
            "readOnlyEndpointCandidateCount": 8,
            "pageCandidateCount": 8,
            "cardCandidateCount": 8,
            "decisionItemCount": 46,
            "queueRowCount": 46,
            "policyGuardResultCount": 46,
            "auditPreviewCount": 46,
            "totalDeviceEvidenceCount": 470,
            "pendingDecisionCount": 46,
            "blockingDecisionCount": 45,
        }
        for key, value in expected.items():
            self.assertEqual(self.summary[key], value)

    def test_boundaries(self) -> None:
        for key in (
            "runtimeObservedCount",
            "runtimeAlarmObservedCount",
            "ufmsFaultCaseCreatedCount",
            "workOrderIntentCreatedCount",
            "workOrderCreatedCount",
            "evidenceCenterWriteCount",
            "ummsWriteCount",
            "oneWorkManagementWriteCount",
            "decisionWriteCount",
            "approvalWriteCount",
            "auditWriteCount",
            "canonicalWriteCount",
            "databaseWriteCount",
        ):
            self.assertEqual(self.summary[key], 0)
        for key in ("apiEnabled", "frontendEnabled", "endpointImplementationAllowed", "frontendImplementationAllowed", "routeImplementationAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "containsCustomerAssetIdentifiers"):
            self.assertFalse(self.summary[key])
        self.assertTrue(self.summary["handoffAllowed"])
        self.assertTrue(self.summary["crossIndustry"])
        self.assertFalse(self.summary["airportSpecific"])

    def test_handoff_matrices(self) -> None:
        self.assertEqual(len(self.gate["pageHandoffMatrix"]), 8)
        self.assertEqual(len(self.gate["dataSourceHandoffMatrix"]), 15)
        self.assertEqual(len(self.gate["cardHandoffMatrix"]), 8)
        self.assertEqual(
            [page["pageKey"] for page in self.gate["pageHandoffMatrix"]],
            [
                "AIRPORT_OVERVIEW",
                "ALARMS_EVENTS",
                "ASSETS_TOPOLOGY",
                "EVIDENCE_INVESTIGATION",
                "FAULT_CASES",
                "MAINTENANCE_WORK_ORDERS",
                "REPORTS",
                "SYSTEMS_INTEGRATION_HEALTH",
            ],
        )
        self.assertTrue(all(page["apiContractCandidateState"] in {"CANDIDATE_READY", "READ_ONLY_ONLY"} for page in self.gate["pageHandoffMatrix"]))
        self.assertTrue(all(page["frontendContractCandidateState"] in {"CANDIDATE_READY", "READ_ONLY_ONLY"} for page in self.gate["pageHandoffMatrix"]))
        self.assertTrue(all(page["blocked"] is False for page in self.gate["pageHandoffMatrix"]))

    def test_data_sources_are_read_only(self) -> None:
        for data_source in self.gate["dataSourceHandoffMatrix"]:
            self.assertTrue(data_source["readOnly"])
            self.assertFalse(data_source["apiEnabled"])
            self.assertFalse(data_source["frontendEnabled"])
            self.assertFalse(data_source["databaseAccessEnabled"])

    def test_api_frontend_contracts(self) -> None:
        api = self.gate["apiReadinessContract"]
        frontend = self.gate["frontendReadinessContract"]
        self.assertEqual(api["contractState"], "READY_FOR_HANDOFF")
        self.assertFalse(api["endpointImplementationAllowed"])
        self.assertFalse(api["publicApiEnabled"])
        self.assertFalse(api["databaseAccessAllowed"])
        self.assertFalse(api["writeOperationAllowed"])
        self.assertEqual(api["candidateEndpointCount"], 8)
        self.assertEqual(api["readOnlyEndpointCandidateCount"], 8)
        self.assertEqual(frontend["contractState"], "READY_FOR_HANDOFF")
        self.assertFalse(frontend["frontendImplementationAllowed"])
        self.assertFalse(frontend["routeImplementationAllowed"])
        self.assertFalse(frontend["runtimeDataMutationAllowed"])
        self.assertEqual(frontend["pageCandidateCount"], 8)
        self.assertEqual(frontend["cardCandidateCount"], 8)

    def test_release_gates_and_decision(self) -> None:
        self.assertEqual(len(self.gate["releaseGateResults"]), 15)
        self.assertTrue(all(gate["status"] == "PASS" for gate in self.gate["releaseGateResults"]))
        decision = self.gate["handoffDecision"]
        self.assertEqual(decision["decisionState"], "READY_FOR_HANDOFF")
        self.assertTrue(decision["handoffAllowed"])
        for key in ("apiImplementationAllowed", "frontendImplementationAllowed", "databaseWriteAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed"):
            self.assertFalse(decision[key])

    def test_deterministic_generation(self) -> None:
        again = build_airport_operations_console_handoff_gate()
        self.assertEqual(
            json.dumps(self.gate, sort_keys=True, separators=(",", ":")),
            json.dumps(again, sort_keys=True, separators=(",", ":")),
        )

    def test_no_identifier_leakage(self) -> None:
        serialized = json.dumps(self.gate, sort_keys=True)
        self.assertNotIn("deviceId", serialized)
        self.assertNotIn("assetId", serialized)
        self.assertNotIn("customerAssetIdentifier", serialized)

    def test_validation(self) -> None:
        validate_operations_console_handoff_gate(self.gate)
        self.assertEqual(self.gate["implementationStatus"], "AIRPORT_CONSOLE_PACKAGE_HANDOFF_GATE_COMPLETE")
        self.assertEqual(self.gate["readinessOutcome"], "AIRPORT_CONSOLE_PACKAGE_READY_FOR_API_FRONTEND_PLANNING")


class OperationsConsoleHandoffGateBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/operations_console_handoff_gate").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/operations_console_handoff_gate.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
