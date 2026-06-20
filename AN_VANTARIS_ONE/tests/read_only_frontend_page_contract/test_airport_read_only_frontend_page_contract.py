from __future__ import annotations

import json
import unittest
from pathlib import Path

from industry_profiles.airport.read_only_frontend_page_contract import build_airport_read_only_frontend_page_contract
from read_only_frontend_page_contract.validation import validate_boundary, validate_read_only_frontend_page_contract

ROOT = Path(__file__).resolve().parents[3]


class AirportReadOnlyFrontendPageContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = build_airport_read_only_frontend_page_contract()
        self.summary = self.contract["summary"]

    def test_expected_counts(self) -> None:
        expected = {
            "pageContractCount": 8,
            "layoutContractCount": 8,
            "componentBindingContractCount": 24,
            "uiStateContractCount": 48,
            "interactionContractCount": 64,
            "localSmokeCaseCount": 8,
            "smokeGateCount": 16,
            "passedSmokeGateCount": 16,
            "blockingGateFailureCount": 0,
            "staticOnlyPageCount": 8,
            "readOnlyPageCount": 8,
            "productionEnabledPageCount": 0,
            "liveApiCallEnabledPageCount": 0,
            "dataMutationEnabledPageCount": 0,
            "liveApiCallEnabledComponentCount": 0,
            "dataMutationEnabledComponentCount": 0,
            "mutationAllowedInteractionCount": 0,
            "browserLaunchRequiredCount": 0,
            "networkCallRequiredCount": 0,
            "localhostCallRequiredCount": 0,
            "productionRouteEnabledCount": 0,
            "a8FrontendSkeletonPageCount": 8,
        }
        for key, value in expected.items():
            self.assertEqual(self.summary[key], value)

    def test_page_layout_and_component_contracts(self) -> None:
        self.assertEqual(len(self.contract["pageContracts"]), 8)
        for page in self.contract["pageContracts"]:
            self.assertTrue(page["staticOnly"])
            self.assertTrue(page["readOnly"])
            self.assertFalse(page["productionEnabled"])
            self.assertFalse(page["liveApiCallEnabled"])
            self.assertFalse(page["dataMutationEnabled"])
            self.assertEqual(len(page["componentBindingIds"]), 3)
            self.assertEqual(len(page["uiStateContractIds"]), 6)
            self.assertEqual(len(page["interactionContractIds"]), 8)
        for layout in self.contract["layoutContracts"]:
            self.assertEqual(layout["requiredRegions"], ["header", "summary", "content", "filters", "footer/status"])
            self.assertEqual(layout["responsivePolicy"], "STATIC_RESPONSIVE_CONTRACT_ONLY")
        for binding in self.contract["componentBindingContracts"]:
            self.assertTrue(binding["readOnly"])
            self.assertFalse(binding["liveApiCallEnabled"])
            self.assertFalse(binding["dataMutationEnabled"])

    def test_ui_states_interactions_and_smoke(self) -> None:
        states_by_page: dict[str, set[str]] = {}
        interactions_by_page: dict[str, set[str]] = {}
        for state in self.contract["uiStateContracts"]:
            self.assertTrue(state["required"])
            states_by_page.setdefault(state["pageKey"], set()).add(state["stateType"])
        for interaction in self.contract["interactionContracts"]:
            self.assertTrue(interaction["readOnly"])
            self.assertFalse(interaction["mutationAllowed"])
            self.assertTrue(interaction["supported"])
            interactions_by_page.setdefault(interaction["pageKey"], set()).add(interaction["interactionType"])
        self.assertTrue(all(len(states) == 6 for states in states_by_page.values()))
        self.assertTrue(all(len(interactions) == 8 for interactions in interactions_by_page.values()))
        for smoke in self.contract["localSmokeCases"]:
            self.assertTrue(smoke["expectedPageContract"])
            self.assertTrue(smoke["expectedLayout"])
            self.assertGreaterEqual(smoke["expectedComponents"], 3)
            self.assertEqual(smoke["expectedUiStates"], 6)
            self.assertEqual(smoke["expectedInteractions"], 8)
            self.assertTrue(smoke["expectedNoLiveApiCall"])
            self.assertTrue(smoke["expectedNoMutation"])
            self.assertTrue(smoke["expectedNoProductionRoute"])
            self.assertFalse(smoke["browserLaunchRequired"])
            self.assertFalse(smoke["networkCallRequired"])
            self.assertFalse(smoke["localhostCallRequired"])

    def test_smoke_gates_and_dependencies(self) -> None:
        self.assertEqual(len(self.contract["smokeGateResults"]), 16)
        self.assertTrue(all(gate["status"] == "PASS" for gate in self.contract["smokeGateResults"]))
        self.assertEqual(self.contract["smokeGateResults"][0]["gateId"], "G01_PAGE_CONTRACT_COMPLETENESS")
        self.assertEqual(self.contract["smokeGateResults"][-1]["gateId"], "G16_FRONTEND_PAGE_CONTRACT_DECISION")
        self.assertTrue(self.summary["a7ReadOnlyApiRouteImplementationAllowed"])

    def test_boundaries(self) -> None:
        for key in ("frontendEnabled", "apiEnabled", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "containsCustomerAssetIdentifiers", "airportSpecific"):
            self.assertFalse(self.summary[key])
        for key in ("databaseWriteCount", "canonicalWriteCount", "decisionWriteCount", "approvalWriteCount", "auditWriteCount"):
            self.assertEqual(self.summary[key], 0)
        self.assertTrue(self.summary["crossIndustry"])

    def test_no_identifier_leakage(self) -> None:
        serialized = json.dumps(self.contract, sort_keys=True)
        self.assertNotIn("deviceId", serialized)
        self.assertNotIn("assetId", serialized)
        self.assertNotIn("customerAssetIdentifier", serialized)

    def test_determinism_and_validation(self) -> None:
        validate_read_only_frontend_page_contract(self.contract)
        again = build_airport_read_only_frontend_page_contract()
        self.assertEqual(json.dumps(self.contract, sort_keys=True, separators=(",", ":")), json.dumps(again, sort_keys=True, separators=(",", ":")))
        self.assertEqual(self.contract["implementationStatus"], "READ_ONLY_FRONTEND_PAGE_CONTRACT_AND_LOCAL_SMOKE_GATE_COMPLETE")
        self.assertEqual(self.contract["readinessOutcome"], "READ_ONLY_FRONTEND_PAGE_CONTRACT_READY_FOR_FUTURE_UI_IMPLEMENTATION")


class ReadOnlyFrontendPageContractBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/read_only_frontend_page_contract").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/read_only_frontend_page_contract.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
