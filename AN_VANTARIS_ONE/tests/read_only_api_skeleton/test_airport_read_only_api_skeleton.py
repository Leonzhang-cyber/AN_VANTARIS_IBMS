from __future__ import annotations

import json
import unittest
from pathlib import Path

from industry_profiles.airport.read_only_api_skeleton import build_airport_read_only_api_skeleton
from read_only_api_skeleton.validation import validate_boundary, validate_read_only_api_skeleton

ROOT = Path(__file__).resolve().parents[3]


class AirportReadOnlyApiSkeletonTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skeleton = build_airport_read_only_api_skeleton()
        self.summary = self.skeleton["summary"]

    def test_expected_counts(self) -> None:
        expected = {
            "endpointSkeletonCount": 8,
            "getEndpointCount": 8,
            "readOnlyEndpointCount": 8,
            "responseContractCount": 8,
            "routeGroupCount": 3,
            "readinessGateCount": 14,
            "passedGateCount": 14,
            "blockingGateFailureCount": 0,
            "authPolicyRequiredCount": 8,
            "productionEnabledEndpointCount": 0,
            "databaseAccessEnabledEndpointCount": 0,
            "writeOperationEnabledEndpointCount": 0,
            "runtimeActivationEnabledEndpointCount": 0,
        }
        for key, value in expected.items():
            self.assertEqual(self.summary[key], value)

    def test_endpoint_boundaries(self) -> None:
        for endpoint in self.skeleton["endpointSkeletons"]:
            self.assertEqual(endpoint["method"], "GET")
            self.assertTrue(endpoint["readOnly"])
            self.assertIn(endpoint["implementationState"], {"SKELETON_DEFINED", "CONTRACT_ONLY"})
            self.assertFalse(endpoint["productionEnabled"])
            self.assertFalse(endpoint["databaseAccessEnabled"])
            self.assertFalse(endpoint["writeOperationEnabled"])
            self.assertFalse(endpoint["runtimeActivationEnabled"])
            self.assertIn(endpoint["authPolicy"], {"AUTH_REQUIRED", "ROLE_POLICY_REQUIRED"})

    def test_expected_paths_and_groups(self) -> None:
        paths = {item["endpointKey"]: item["path"] for item in self.skeleton["endpointSkeletons"]}
        self.assertEqual(paths["AIRPORT_OVERVIEW"], "/api/v1/one/airport/console/overview")
        self.assertEqual(paths["SYSTEMS_INTEGRATION_HEALTH"], "/api/v1/one/airport/console/systems-integration-health")
        self.assertEqual(paths["ASSETS_TOPOLOGY"], "/api/v1/one/airport/console/assets-topology")
        self.assertEqual(paths["ALARMS_EVENTS"], "/api/v1/one/airport/console/alarms-events")
        self.assertEqual(paths["FAULT_CASES"], "/api/v1/one/airport/console/fault-cases")
        self.assertEqual(paths["MAINTENANCE_WORK_ORDERS"], "/api/v1/one/airport/console/maintenance-work-orders")
        self.assertEqual(paths["EVIDENCE_INVESTIGATION"], "/api/v1/one/airport/console/evidence-investigation")
        self.assertEqual(paths["REPORTS"], "/api/v1/one/airport/console/reports")
        self.assertEqual({group["groupKey"] for group in self.skeleton["routeGroups"]}, {"AIRPORT_OPERATIONS_API", "ALARM_FAULT_WORK_API", "EVIDENCE_REPORTING_API"})

    def test_response_contracts(self) -> None:
        self.assertEqual(len(self.skeleton["responseContracts"]), 8)
        for response in self.skeleton["responseContracts"]:
            self.assertTrue(response["paginationSupported"])
            self.assertTrue(response["filtersSupported"])
            self.assertTrue(response["facetsSupported"])
            self.assertFalse(response["containsCustomerAssetIdentifiers"])

    def test_summary_boundaries(self) -> None:
        self.assertTrue(self.summary["apiSkeletonPhaseAllowed"])
        for key in ("productionApiAllowed", "apiEnabled", "frontendEnabled", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "containsCustomerAssetIdentifiers"):
            self.assertFalse(self.summary[key])
        for key in ("databaseWriteCount", "canonicalWriteCount", "decisionWriteCount", "approvalWriteCount", "auditWriteCount"):
            self.assertEqual(self.summary[key], 0)
        self.assertTrue(self.summary["crossIndustry"])
        self.assertFalse(self.summary["airportSpecific"])

    def test_gates_and_determinism(self) -> None:
        self.assertEqual(len(self.skeleton["apiReadinessGates"]), 14)
        self.assertTrue(all(gate["status"] == "PASS" for gate in self.skeleton["apiReadinessGates"]))
        again = build_airport_read_only_api_skeleton()
        self.assertEqual(json.dumps(self.skeleton, sort_keys=True, separators=(",", ":")), json.dumps(again, sort_keys=True, separators=(",", ":")))

    def test_no_identifier_leakage(self) -> None:
        serialized = json.dumps(self.skeleton, sort_keys=True)
        self.assertNotIn("deviceId", serialized)
        self.assertNotIn("assetId", serialized)
        self.assertNotIn("customerAssetIdentifier", serialized)

    def test_validation(self) -> None:
        validate_read_only_api_skeleton(self.skeleton)
        self.assertEqual(self.skeleton["implementationStatus"], "READ_ONLY_API_SKELETON_FOUNDATION_COMPLETE")
        self.assertEqual(self.skeleton["readinessOutcome"], "READ_ONLY_API_SKELETON_READY_FOR_FUTURE_IMPLEMENTATION")


class ReadOnlyApiSkeletonBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/read_only_api_skeleton").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/read_only_api_skeleton.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
