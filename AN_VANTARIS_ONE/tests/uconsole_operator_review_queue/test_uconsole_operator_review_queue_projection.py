from __future__ import annotations

import json
import unittest
from pathlib import Path

from industry_profiles.airport.uconsole_operator_review_queue_projection import (
    build_airport_uconsole_operator_review_queue_projection,
)
from uconsole_operator_review_queue.projection import build_facets, build_filters, paginate_queue_rows, sort_queue_rows
from uconsole_operator_review_queue.validation import validate_boundary, validate_uconsole_operator_review_queue_projection

ROOT = Path(__file__).resolve().parents[3]


class AirportUConsoleOperatorReviewQueueProjectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.projection = build_airport_uconsole_operator_review_queue_projection()
        self.summary = self.projection["summary"]
        self.rows = self.projection["queueRows"]
        self.groups = self.projection["queueGroups"]
        self.cards = self.projection["queueCards"]

    def test_expected_counts(self) -> None:
        expected = {
            "decisionItemCount": 46,
            "queueRowCount": 46,
            "queueGroupCount": 8,
            "queueCardCount": 8,
            "pendingDecisionCount": 46,
            "blockingDecisionCount": 45,
            "nonBlockingDecisionCount": 1,
            "sourceSystemRegistryDecisionCount": 5,
            "assetResolutionDecisionCount": 5,
            "pointResolutionDecisionCount": 5,
            "locationResolutionDecisionCount": 5,
            "alarmEventReviewDecisionCount": 5,
            "faultCaseReviewDecisionCount": 5,
            "workOrderIntentReviewDecisionCount": 5,
            "evidenceInvestigationDecisionCount": 5,
            "downstreamCreationAuthorizationDecisionCount": 5,
            "releaseGateDecisionCount": 1,
            "affectedSourceSystemCount": 5,
            "totalDeviceEvidenceCount": 470,
        }
        for key, value in expected.items():
            self.assertEqual(self.summary[key], value)

    def test_rows_not_approved_and_boundaries(self) -> None:
        self.assertFalse(any(row["decisionState"] == "APPROVED" for row in self.rows))
        for key in ("decisionWriteCount", "approvalWriteCount", "canonicalWriteCount", "databaseWriteCount"):
            self.assertEqual(self.summary[key], 0)
        for key in (
            "apiEnabled",
            "frontendEnabled",
            "runtimeActivationAllowed",
            "productionActivationAllowed",
            "pushAllowed",
            "containsCustomerAssetIdentifiers",
        ):
            self.assertFalse(self.summary[key])
        self.assertTrue(self.summary["crossIndustry"])
        self.assertFalse(self.summary["airportSpecific"])

    def test_queue_groups_and_cards(self) -> None:
        expected_queues = [
            "ALL_PENDING_QUEUE",
            "SOURCE_SYSTEM_QUEUE",
            "ASSET_RESOLUTION_QUEUE",
            "ALARM_EVENT_QUEUE",
            "FAULTCASE_QUEUE",
            "WORKORDER_INTENT_QUEUE",
            "EVIDENCE_INVESTIGATION_QUEUE",
            "RELEASE_GATE_QUEUE",
        ]
        self.assertEqual([group["queueType"] for group in self.groups], expected_queues)
        self.assertEqual([card["queueType"] for card in self.cards], expected_queues)
        by_group = {group["queueType"]: group for group in self.groups}
        self.assertEqual(by_group["ALL_PENDING_QUEUE"]["openDecisionCount"], 46)
        self.assertEqual(by_group["ALL_PENDING_QUEUE"]["blockingDecisionCount"], 45)
        self.assertEqual(by_group["RELEASE_GATE_QUEUE"]["openDecisionCount"], 1)
        self.assertEqual(by_group["RELEASE_GATE_QUEUE"]["blockingDecisionCount"], 0)

    def test_decision_type_distribution(self) -> None:
        counts: dict[str, int] = {}
        for row in self.rows:
            counts[row["decisionType"]] = counts.get(row["decisionType"], 0) + 1
        self.assertEqual(counts["REGISTRY_APPROVAL"], 2)
        self.assertEqual(counts["ALIAS_APPROVAL"], 2)
        self.assertEqual(counts["NAMESPACE_INTERPRETATION"], 1)
        for decision_type in (
            "ASSET_RESOLUTION",
            "POINT_RESOLUTION",
            "LOCATION_RESOLUTION",
            "ALARM_EVENT_REVIEW",
            "FAULTCASE_CANDIDATE_REVIEW",
            "WORKORDER_INTENT_REVIEW",
            "EVIDENCE_INVESTIGATION_REVIEW",
            "DOWNSTREAM_CREATION_AUTHORIZATION",
        ):
            self.assertEqual(counts[decision_type], 5)
        self.assertEqual(counts["RELEASE_GATE_REVIEW"], 1)

    def test_no_identifier_leakage(self) -> None:
        text = json.dumps(self.projection, sort_keys=True).lower()
        for forbidden in ("customer_device_id", "customer_asset_id", "customer asset identifier:", "live alarm timestamp"):
            self.assertNotIn(forbidden, text)

    def test_deterministic_helpers(self) -> None:
        self.assertEqual(self.rows, sort_queue_rows(self.rows))
        self.assertEqual(self.projection["facets"], build_facets(self.rows))
        self.assertEqual(self.projection["filters"], build_filters(self.rows))
        self.assertEqual(self.projection["defaultPage"], paginate_queue_rows(self.rows, page_size=25))

    def test_deterministic_projection(self) -> None:
        again = build_airport_uconsole_operator_review_queue_projection()
        self.assertEqual(
            json.dumps(self.projection, sort_keys=True, separators=(",", ":")),
            json.dumps(again, sort_keys=True, separators=(",", ":")),
        )

    def test_projection_validation(self) -> None:
        validate_uconsole_operator_review_queue_projection(self.projection)
        self.assertEqual(self.projection["implementationStatus"], "OPERATOR_REVIEW_UCONSOLE_QUEUE_PROJECTION_COMPLETE")
        self.assertEqual(
            self.projection["readinessOutcome"],
            "UCONSOLE_OPERATOR_REVIEW_QUEUE_READY_FOR_READ_ONLY_CONSUMPTION",
        )


class UConsoleOperatorReviewQueueBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/uconsole_operator_review_queue").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/uconsole_operator_review_queue_projection.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
