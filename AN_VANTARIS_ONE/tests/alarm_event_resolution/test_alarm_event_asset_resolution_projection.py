from __future__ import annotations

import json
import unittest
from pathlib import Path

from alarm_event_resolution.projection import build_facets, paginate_rows, sort_rows
from alarm_event_resolution.validation import validate_projection_boundary, validate_resolution_projection
from industry_profiles.airport.alarm_event_asset_resolution_projection import (
    build_airport_alarm_event_asset_resolution_projection,
)

ROOT = Path(__file__).resolve().parents[3]


class AirportAlarmEventAssetResolutionProjectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.projection = build_airport_alarm_event_asset_resolution_projection()
        self.summary = self.projection["summary"]
        self.rows = self.projection["resolutionRows"]
        self.cards = self.projection["reviewCards"]

    def test_exactly_five_rows_and_seven_review_cards(self) -> None:
        self.assertEqual(len(self.rows), 5)
        self.assertEqual(len(self.cards), 7)
        self.assertEqual(self.summary["resolutionRowCount"], 5)
        self.assertEqual(self.summary["reviewCardCount"], 7)

    def test_total_and_source_evidence_counts(self) -> None:
        by_key = {row["sourceSystemKey"]: row for row in self.rows}
        self.assertEqual(self.summary["totalDeviceEvidenceCount"], 470)
        self.assertEqual(by_key["ACS"]["deviceEvidenceCount"], 129)
        self.assertEqual(by_key["RAS"]["deviceEvidenceCount"], 28)
        self.assertEqual(by_key["CCTV"]["deviceEvidenceCount"], 52)
        self.assertEqual(by_key["PA"]["deviceEvidenceCount"], 247)
        self.assertEqual(by_key["TEL"]["deviceEvidenceCount"], 14)

    def test_expected_review_states(self) -> None:
        by_key = {row["sourceSystemKey"]: row for row in self.rows}
        self.assertEqual(by_key["ACS"]["sourceSystemReviewState"], "REGISTRY_APPROVAL_PENDING")
        self.assertEqual(by_key["RAS"]["sourceSystemReviewState"], "REGISTRY_APPROVAL_PENDING")
        self.assertEqual(by_key["CCTV"]["sourceSystemReviewState"], "ALIAS_APPROVAL_PENDING")
        self.assertEqual(by_key["PA"]["sourceSystemReviewState"], "ALIAS_APPROVAL_PENDING")
        self.assertEqual(by_key["TEL"]["sourceSystemReviewState"], "NAMESPACE_INTERPRETATION_PENDING")
        for row in self.rows:
            self.assertIn("RESOLUTION_REVIEW_REQUIRED", row["reviewReasons"])

    def test_resolution_states_require_review(self) -> None:
        for row in self.rows:
            self.assertIn(row["assetResolutionState"], {"REVIEW_REQUIRED", "UNRESOLVED"})
            self.assertIn(row["pointResolutionState"], {"REVIEW_REQUIRED", "UNRESOLVED"})
            self.assertIn(row["locationResolutionState"], {"REVIEW_REQUIRED", "UNRESOLVED"})
            self.assertTrue(row["decisionRequired"])
            self.assertEqual(row["downstreamCreationState"], "NOT_AUTHORIZED")

    def test_no_downstream_canonical_db_or_runtime_writes(self) -> None:
        for key in (
            "ufmsFaultCaseCreatedCount",
            "workOrderIntentCreatedCount",
            "workOrderCreatedCount",
            "canonicalWriteCount",
            "databaseWriteCount",
            "runtimeAlarmObservedCount",
        ):
            self.assertEqual(self.summary[key], 0)

    def test_no_customer_identifier_leakage(self) -> None:
        self.assertFalse(self.summary["containsCustomerAssetIdentifiers"])
        text = json.dumps(self.projection, sort_keys=True).lower()
        for forbidden in ("customer_device_id", "customer_asset_id", "customer asset identifier:", "live alarm"):
            self.assertNotIn(forbidden, text)

    def test_review_cards_are_aggregated_root_causes(self) -> None:
        self.assertEqual(
            {card["reviewType"] for card in self.cards},
            {
                "REGISTRY_APPROVAL_REQUIRED",
                "ALIAS_APPROVAL_REQUIRED",
                "NAMESPACE_INTERPRETATION_REQUIRED",
                "ASSET_RESOLUTION_REQUIRED",
                "POINT_RESOLUTION_REQUIRED",
                "LOCATION_RESOLUTION_REQUIRED",
                "DOWNSTREAM_CREATION_NOT_AUTHORIZED",
            },
        )
        by_type = {card["reviewType"]: card for card in self.cards}
        self.assertEqual(by_type["REGISTRY_APPROVAL_REQUIRED"]["affectedSourceSystemKeys"], ["ACS", "RAS"])
        self.assertEqual(by_type["ALIAS_APPROVAL_REQUIRED"]["affectedSourceSystemKeys"], ["CCTV", "PA"])
        self.assertEqual(by_type["NAMESPACE_INTERPRETATION_REQUIRED"]["affectedSourceSystemKeys"], ["TEL"])
        self.assertEqual(by_type["ASSET_RESOLUTION_REQUIRED"]["affectedCandidateCount"], 5)
        self.assertEqual(by_type["POINT_RESOLUTION_REQUIRED"]["affectedDeviceEvidenceCount"], 470)
        self.assertEqual(by_type["DOWNSTREAM_CREATION_NOT_AUTHORIZED"]["affectedCandidateCount"], 5)

    def test_deterministic_rows_cards_facets_pagination_and_repeated_run(self) -> None:
        self.assertEqual(self.rows, sort_rows(self.rows))
        self.assertEqual(self.projection["facets"], build_facets(self.rows))
        self.assertEqual(self.projection["defaultPage"], paginate_rows(self.rows, page_size=25))
        again = build_airport_alarm_event_asset_resolution_projection()
        self.assertEqual(
            json.dumps(self.projection, sort_keys=True, separators=(",", ":")),
            json.dumps(again, sort_keys=True, separators=(",", ":")),
        )

    def test_projection_validation(self) -> None:
        validate_resolution_projection(self.projection)
        self.assertEqual(
            self.projection["implementationStatus"],
            "ALARM_EVENT_ASSET_RESOLUTION_REVIEW_PROJECTION_COMPLETE",
        )
        self.assertEqual(
            self.projection["readinessOutcome"],
            "ALARM_EVENT_RESOLUTION_REVIEW_COMPLETE_WITH_PENDING_DECISIONS",
        )


class AlarmEventResolutionBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/alarm_event_resolution").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/alarm_event_asset_resolution_projection.py"
        ]
        validate_projection_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
