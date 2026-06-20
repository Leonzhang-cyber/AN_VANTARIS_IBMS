from __future__ import annotations

import json
import unittest
from pathlib import Path

from industry_profiles.airport.read_only_frontend_skeleton import build_airport_read_only_frontend_skeleton
from read_only_frontend_skeleton.validation import validate_boundary, validate_read_only_frontend_skeleton

ROOT = Path(__file__).resolve().parents[3]


class AirportReadOnlyFrontendSkeletonTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skeleton = build_airport_read_only_frontend_skeleton()
        self.summary = self.skeleton["summary"]

    def test_expected_counts(self) -> None:
        expected = {
            "pageSkeletonCount": 8,
            "routeSkeletonCount": 8,
            "componentSkeletonCount": 24,
            "dataBindingSkeletonCount": 8,
            "cardSkeletonCount": 8,
            "queueSkeletonCount": 8,
            "frontendReadinessGateCount": 15,
            "passedGateCount": 15,
            "blockingGateFailureCount": 0,
            "staticOnlyPageCount": 8,
            "readOnlyPageCount": 8,
            "productionEnabledPageCount": 0,
            "liveApiCallEnabledPageCount": 0,
            "dataMutationEnabledPageCount": 0,
            "productionRouteEnabledCount": 0,
            "liveApiCallEnabledBindingCount": 0,
            "mockDataAllowedBindingCount": 8,
            "projectionBindingRequiredCount": 8,
        }
        for key, value in expected.items():
            self.assertEqual(self.summary[key], value)

    def test_page_and_route_skeletons(self) -> None:
        expected_pages = {
            "AIRPORT_OVERVIEW": "Airport Overview",
            "SYSTEMS_INTEGRATION_HEALTH": "Systems & Integration Health",
            "ASSETS_TOPOLOGY": "Assets & Topology",
            "ALARMS_EVENTS": "Alarms & Events",
            "FAULT_CASES": "Fault Cases",
            "MAINTENANCE_WORK_ORDERS": "Maintenance Work Orders",
            "EVIDENCE_INVESTIGATION": "Evidence & Investigation",
            "REPORTS": "Reports",
        }
        self.assertEqual({item["pageKey"]: item["title"] for item in self.skeleton["pageSkeletons"]}, expected_pages)
        for page in self.skeleton["pageSkeletons"]:
            self.assertTrue(page["staticOnly"])
            self.assertTrue(page["readOnly"])
            self.assertFalse(page["productionEnabled"])
            self.assertFalse(page["liveApiCallEnabled"])
            self.assertFalse(page["dataMutationEnabled"])
            self.assertEqual(page["implementationState"], "SKELETON_DEFINED")
            self.assertEqual(len(page["componentSkeletonIds"]), 3)
            self.assertEqual(len(page["cardSkeletonIds"]), 1)
            self.assertEqual(len(page["queueSkeletonIds"]), 1)
        for route in self.skeleton["routeSkeletons"]:
            self.assertFalse(route["productionRouteEnabled"])
            self.assertEqual(route["implementationState"], "SKELETON_DEFINED")
            self.assertTrue(route["pathCandidate"].startswith("/one/airport/"))

    def test_component_and_binding_skeletons(self) -> None:
        component_counts: dict[str, int] = {}
        for component in self.skeleton["componentSkeletons"]:
            component_counts[component["pageKey"]] = component_counts.get(component["pageKey"], 0) + 1
            self.assertTrue(component["staticOnly"])
            self.assertTrue(component["readOnly"])
            self.assertEqual(len(component["dataBindingSkeletonIds"]), 1)
        self.assertTrue(all(count == 3 for count in component_counts.values()))
        for binding in self.skeleton["dataBindingSkeletons"]:
            self.assertFalse(binding["liveApiCallEnabled"])
            self.assertTrue(binding["mockDataAllowed"])
            self.assertTrue(binding["projectionBindingRequired"])
            self.assertTrue(binding["sourceArtifactPath"].startswith("AN_VANTARIS_ONE/industry_profiles/airport/projections/"))
        for card in self.skeleton["cardSkeletons"]:
            self.assertTrue(card["staticOnly"])
            self.assertTrue(card["readOnly"])
        for queue in self.skeleton["queueSkeletons"]:
            self.assertTrue(queue["staticOnly"])
            self.assertTrue(queue["readOnly"])
            self.assertEqual(queue["rowCountPolicy"], "STATIC_PROJECTION_ROWS_ONLY")

    def test_readiness_gates_and_dependencies(self) -> None:
        self.assertEqual(len(self.skeleton["frontendReadinessGates"]), 15)
        self.assertTrue(all(gate["status"] == "PASS" for gate in self.skeleton["frontendReadinessGates"]))
        self.assertEqual(self.skeleton["frontendReadinessGates"][0]["gateId"], "G01_FRONTEND_PAGE_SKELETON_COMPLETENESS")
        self.assertEqual(self.skeleton["frontendReadinessGates"][-1]["gateId"], "G15_FRONTEND_SKELETON_DECISION")
        self.assertTrue(self.summary["a7ReadOnlyApiRouteImplementationAllowed"])
        self.assertTrue(self.summary["a6FrontendSkeletonPhaseAllowed"])
        self.assertTrue(self.summary["frontendSkeletonPhaseAllowed"])

    def test_boundaries(self) -> None:
        for key in ("productionFrontendAllowed", "frontendEnabled", "apiEnabled", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "containsCustomerAssetIdentifiers", "airportSpecific"):
            self.assertFalse(self.summary[key])
        for key in ("databaseWriteCount", "canonicalWriteCount", "decisionWriteCount", "approvalWriteCount", "auditWriteCount"):
            self.assertEqual(self.summary[key], 0)
        self.assertTrue(self.summary["crossIndustry"])

    def test_no_identifier_leakage(self) -> None:
        serialized = json.dumps(self.skeleton, sort_keys=True)
        self.assertNotIn("deviceId", serialized)
        self.assertNotIn("assetId", serialized)
        self.assertNotIn("customerAssetIdentifier", serialized)

    def test_determinism_and_validation(self) -> None:
        validate_read_only_frontend_skeleton(self.skeleton)
        again = build_airport_read_only_frontend_skeleton()
        self.assertEqual(json.dumps(self.skeleton, sort_keys=True, separators=(",", ":")), json.dumps(again, sort_keys=True, separators=(",", ":")))
        self.assertEqual(self.skeleton["implementationStatus"], "READ_ONLY_FRONTEND_SKELETON_FOUNDATION_COMPLETE")
        self.assertEqual(self.skeleton["readinessOutcome"], "READ_ONLY_FRONTEND_SKELETON_READY_FOR_FUTURE_UI_IMPLEMENTATION")


class ReadOnlyFrontendSkeletonBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/read_only_frontend_skeleton").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/read_only_frontend_skeleton.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
