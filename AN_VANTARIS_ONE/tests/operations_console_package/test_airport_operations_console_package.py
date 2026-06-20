from __future__ import annotations

import json
import unittest
from pathlib import Path

from industry_profiles.airport.operations_console_package import build_airport_operations_console_package
from operations_console_package.validation import validate_boundary, validate_operations_console_package

ROOT = Path(__file__).resolve().parents[3]


class AirportOperationsConsolePackageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.package = build_airport_operations_console_package()
        self.summary = self.package["summary"]

    def test_expected_counts(self) -> None:
        expected = {
            "pageDefinitionCount": 8,
            "navigationGroupCount": 3,
            "consoleCardCount": 8,
            "packageDataSourceCount": 15,
            "packageReadinessGateCount": 12,
            "sourceSystemCandidateCount": 5,
            "alarmEventCandidateCount": 5,
            "faultCaseCandidateCount": 5,
            "workOrderIntentCandidateCount": 5,
            "investigationCaseCount": 5,
            "operationsRowCount": 5,
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
        for key in ("apiEnabled", "frontendEnabled", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "containsCustomerAssetIdentifiers"):
            self.assertFalse(self.summary[key])
        self.assertTrue(self.summary["crossIndustry"])
        self.assertFalse(self.summary["airportSpecific"])

    def test_pages_and_navigation(self) -> None:
        self.assertEqual(
            [page["pageKey"] for page in self.package["pageDefinitions"]],
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
        self.assertEqual({group["groupKey"] for group in self.package["navigationGroups"]}, {"AIRPORT_OPERATIONS", "ALARM_FAULT_WORK", "EVIDENCE_REPORTING"})
        self.assertEqual(self.package["defaultPage"]["pageKey"], "AIRPORT_OVERVIEW")
        self.assertEqual(self.package["defaultPage"]["pageSize"], 25)
        self.assertEqual(self.package["defaultPage"]["orderBy"], ["pageKey", "pageId"])

    def test_data_sources_are_read_only(self) -> None:
        self.assertEqual(len(self.package["packageDataSources"]), 15)
        for data_source in self.package["packageDataSources"]:
            self.assertTrue(data_source["readOnly"])
            self.assertFalse(data_source["apiEnabled"])
            self.assertFalse(data_source["frontendEnabled"])
            self.assertFalse(data_source["databaseAccessEnabled"])

    def test_gates_pass(self) -> None:
        self.assertEqual(len(self.package["packageReadinessGates"]), 12)
        self.assertTrue(all(gate["status"] == "PASS" for gate in self.package["packageReadinessGates"]))
        self.assertTrue(all(gate["blocking"] for gate in self.package["packageReadinessGates"]))

    def test_filters_facets_and_pagination_are_deterministic(self) -> None:
        self.assertEqual({item["field"] for item in self.package["filters"]}, {"pageKey", "pageType", "readinessState", "navigationGroup", "cardType", "severity", "decisionRequired", "blocked", "sourceProjectionType"})
        self.assertEqual({item["field"] for item in self.package["facets"]}, {"pageKey", "pageType", "readinessState", "navigationGroup", "cardType", "severity", "decisionRequired", "blocked", "sourceProjectionType"})
        again = build_airport_operations_console_package()
        self.assertEqual(self.package["defaultPage"], again["defaultPage"])
        self.assertEqual(
            json.dumps(self.package, sort_keys=True, separators=(",", ":")),
            json.dumps(again, sort_keys=True, separators=(",", ":")),
        )

    def test_no_identifier_leakage(self) -> None:
        serialized = json.dumps(self.package, sort_keys=True)
        self.assertNotIn("deviceId", serialized)
        self.assertNotIn("assetId", serialized)
        self.assertNotIn("customerAssetIdentifier", serialized)
        self.assertFalse(self.summary["containsCustomerAssetIdentifiers"])

    def test_validation(self) -> None:
        validate_operations_console_package(self.package)
        self.assertEqual(self.package["implementationStatus"], "READ_ONLY_AIRPORT_OPERATIONS_CONSOLE_PACKAGE_FOUNDATION_COMPLETE")
        self.assertEqual(self.package["readinessOutcome"], "AIRPORT_OPERATIONS_CONSOLE_PACKAGE_READY_FOR_READ_ONLY_CONSUMPTION")


class OperationsConsolePackageBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/operations_console_package").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/operations_console_package.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
