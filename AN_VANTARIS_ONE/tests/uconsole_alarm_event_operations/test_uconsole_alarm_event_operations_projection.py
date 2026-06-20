from __future__ import annotations

import json
import unittest
from pathlib import Path

from industry_profiles.airport.uconsole_alarm_event_operations_projection import (
    build_airport_uconsole_alarm_event_operations_projection,
)
from uconsole_alarm_event_operations.projection import build_facets, paginate_rows, sort_rows
from uconsole_alarm_event_operations.validation import validate_boundary, validate_operations_projection

ROOT = Path(__file__).resolve().parents[3]


class AirportUConsoleAlarmEventOperationsProjectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.projection = build_airport_uconsole_alarm_event_operations_projection()
        self.summary = self.projection["summary"]
        self.rows = self.projection["operationsRows"]
        self.cards = self.projection["operationsCards"]

    def test_exact_counts(self) -> None:
        self.assertEqual(len(self.rows), 5)
        self.assertEqual(len(self.cards), 7)
        self.assertEqual(self.summary["operationsRowCount"], 5)
        self.assertEqual(self.summary["operationsCardCount"], 7)
        self.assertEqual(self.summary["alarmEventCandidateCount"], 5)
        self.assertEqual(self.summary["resolutionRowCount"], 5)
        self.assertEqual(self.summary["faultCaseCandidateCount"], 5)
        self.assertEqual(self.summary["workOrderIntentCandidateCount"], 5)
        self.assertEqual(self.summary["investigationCaseCount"], 5)
        self.assertEqual(self.summary["totalDeviceEvidenceCount"], 470)

    def test_source_counts_and_links(self) -> None:
        by_key = {row["sourceSystemKey"]: row for row in self.rows}
        self.assertEqual(set(by_key), {"ACS", "RAS", "CCTV", "PA", "TEL"})
        self.assertEqual(by_key["ACS"]["deviceEvidenceCount"], 129)
        self.assertEqual(by_key["RAS"]["deviceEvidenceCount"], 28)
        self.assertEqual(by_key["CCTV"]["deviceEvidenceCount"], 52)
        self.assertEqual(by_key["PA"]["deviceEvidenceCount"], 247)
        self.assertEqual(by_key["TEL"]["deviceEvidenceCount"], 14)
        for row in self.rows:
            self.assertTrue(row["alarmEventCandidateId"])
            self.assertTrue(row["resolutionRowId"])
            self.assertTrue(row["faultCaseCandidateId"])
            self.assertTrue(row["workOrderIntentCandidateId"])
            self.assertTrue(row["investigationCaseId"])

    def test_rows_are_blocked_and_decision_required(self) -> None:
        for row in self.rows:
            self.assertEqual(row["operationalStatus"], "BLOCKED")
            self.assertTrue(row["decisionRequired"])
            self.assertGreaterEqual(row["pendingDecisionCount"], 1)
            self.assertIn("RUNTIME_PENDING", row["blockingReasons"])
            self.assertIn("EVIDENCE_INVESTIGATION_REVIEW_REQUIRED", row["reviewReasons"])
        self.assertEqual(self.summary["decisionRequiredCount"], 5)
        self.assertEqual(self.summary["reviewRequiredRowCount"], 5)
        self.assertEqual(self.summary["blockedRowCount"], 5)
        self.assertEqual(self.summary["runtimePendingCount"], 5)

    def test_review_pending_counts(self) -> None:
        self.assertEqual(self.summary["registryApprovalPendingCount"], 2)
        self.assertEqual(self.summary["aliasApprovalPendingCount"], 2)
        self.assertEqual(self.summary["namespaceReviewPendingCount"], 1)
        self.assertEqual(self.summary["assetResolutionRequiredCount"], 5)
        self.assertEqual(self.summary["faultCaseReviewRequiredCount"], 5)
        self.assertEqual(self.summary["workOrderIntentReviewRequiredCount"], 5)
        self.assertEqual(self.summary["evidenceInvestigationReviewRequiredCount"], 5)

    def test_operations_cards(self) -> None:
        self.assertEqual(
            [card["cardType"] for card in self.cards],
            [
                "ALARM_EVENT_QUEUE",
                "FAULTCASE_CANDIDATE_QUEUE",
                "WORKORDER_INTENT_QUEUE",
                "EVIDENCE_INVESTIGATION_QUEUE",
                "REVIEW_REQUIRED_SUMMARY",
                "RUNTIME_PENDING_SUMMARY",
                "SOURCE_SYSTEM_SUMMARY",
            ],
        )
        for card in self.cards:
            self.assertTrue(card["decisionRequired"])
            self.assertEqual(sorted(card["affectedSourceSystemKeys"]), ["ACS", "CCTV", "PA", "RAS", "TEL"])

    def test_no_downstream_runtime_or_ui_writes(self) -> None:
        for key in (
            "runtimeAlarmObservedCount",
            "ufmsFaultCaseCreatedCount",
            "workOrderIntentCreatedCount",
            "workOrderCreatedCount",
            "evidenceCenterWriteCount",
            "ummsWriteCount",
            "oneWorkManagementWriteCount",
            "canonicalWriteCount",
            "databaseWriteCount",
        ):
            self.assertEqual(self.summary[key], 0)
        self.assertFalse(self.summary["apiEnabled"])
        self.assertFalse(self.summary["frontendEnabled"])
        self.assertFalse(self.summary["containsCustomerAssetIdentifiers"])
        self.assertTrue(self.summary["crossIndustry"])
        self.assertFalse(self.summary["airportSpecific"])

    def test_deterministic_projection(self) -> None:
        self.assertEqual(self.rows, sort_rows(self.rows))
        self.assertEqual(self.projection["facets"], build_facets(self.rows))
        self.assertEqual(self.projection["defaultPage"], paginate_rows(self.rows, page_size=25))
        again = build_airport_uconsole_alarm_event_operations_projection()
        self.assertEqual(
            json.dumps(self.projection, sort_keys=True, separators=(",", ":")),
            json.dumps(again, sort_keys=True, separators=(",", ":")),
        )

    def test_projection_validation(self) -> None:
        validate_operations_projection(self.projection)
        self.assertEqual(
            self.projection["implementationStatus"],
            "READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_COMPLETE",
        )
        self.assertEqual(
            self.projection["readinessOutcome"],
            "UCONSOLE_ALARM_EVENT_OPERATIONS_READ_ONLY_PROJECTION_COMPLETE_PENDING_REVIEWS",
        )


class UConsoleAlarmEventOperationsBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/uconsole_alarm_event_operations").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/uconsole_alarm_event_operations_projection.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
