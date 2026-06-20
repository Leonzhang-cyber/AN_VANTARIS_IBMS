from __future__ import annotations

import json
import unittest
from pathlib import Path

from industry_profiles.airport.operator_review_decision_projection import build_airport_operator_review_decision_projection
from operator_review_decision.projection import build_facets, build_filters, paginate_decision_items, sort_decision_items
from operator_review_decision.validation import validate_boundary, validate_operator_review_decision_projection

ROOT = Path(__file__).resolve().parents[3]


class AirportOperatorReviewDecisionProjectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.projection = build_airport_operator_review_decision_projection()
        self.summary = self.projection["summary"]
        self.items = self.projection["decisionItems"]
        self.groups = self.projection["decisionGroups"]
        self.queues = self.projection["decisionQueues"]

    def test_expected_counts(self) -> None:
        expected = {
            "decisionItemCount": 46,
            "decisionGroupCount": 8,
            "decisionQueueCount": 8,
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

    def test_decisions_are_pending_not_applied(self) -> None:
        self.assertTrue(all(item["decisionState"] in {"PENDING", "READY_FOR_REVIEW"} for item in self.items))
        self.assertFalse(any(item["decisionState"] == "APPROVED" for item in self.items))
        self.assertFalse(any(item["decisionState"] == "REJECTED" for item in self.items))
        self.assertTrue(all(item["currentDecision"] == "KEEP_PENDING" for item in self.items))

    def test_write_and_runtime_boundaries(self) -> None:
        for key in ("decisionWriteCount", "approvalWriteCount", "canonicalWriteCount", "databaseWriteCount"):
            self.assertEqual(self.summary[key], 0)
        for key in (
            "apiEnabled",
            "frontendEnabled",
            "pushAllowed",
            "runtimeActivationAllowed",
            "productionActivationAllowed",
            "containsCustomerAssetIdentifiers",
        ):
            self.assertFalse(self.summary[key])
        self.assertTrue(self.summary["crossIndustry"])
        self.assertFalse(self.summary["airportSpecific"])

    def test_queue_types(self) -> None:
        self.assertEqual(
            [queue["queueType"] for queue in self.queues],
            [
                "ALL_PENDING_QUEUE",
                "SOURCE_SYSTEM_QUEUE",
                "ASSET_RESOLUTION_QUEUE",
                "ALARM_EVENT_QUEUE",
                "FAULTCASE_QUEUE",
                "WORKORDER_INTENT_QUEUE",
                "EVIDENCE_INVESTIGATION_QUEUE",
                "RELEASE_GATE_QUEUE",
            ],
        )
        by_queue = {queue["queueType"]: queue for queue in self.queues}
        self.assertEqual(by_queue["ALL_PENDING_QUEUE"]["openDecisionCount"], 46)
        self.assertEqual(by_queue["ALL_PENDING_QUEUE"]["blockingDecisionCount"], 45)
        self.assertEqual(by_queue["RELEASE_GATE_QUEUE"]["openDecisionCount"], 1)
        self.assertEqual(by_queue["RELEASE_GATE_QUEUE"]["blockingDecisionCount"], 0)

    def test_type_distribution(self) -> None:
        counts: dict[str, int] = {}
        for item in self.items:
            counts[item["decisionType"]] = counts.get(item["decisionType"], 0) + 1
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

    def test_deterministic_projection_helpers(self) -> None:
        self.assertEqual(self.items, sort_decision_items(self.items))
        self.assertEqual(self.projection["facets"], build_facets(self.items, self.queues))
        self.assertEqual(self.projection["filters"], build_filters(self.items, self.queues))
        self.assertEqual(self.projection["defaultPage"], paginate_decision_items(self.items, page_size=25))

    def test_deterministic_projection(self) -> None:
        again = build_airport_operator_review_decision_projection()
        self.assertEqual(
            json.dumps(self.projection, sort_keys=True, separators=(",", ":")),
            json.dumps(again, sort_keys=True, separators=(",", ":")),
        )

    def test_projection_validation(self) -> None:
        validate_operator_review_decision_projection(self.projection)
        self.assertEqual(self.projection["implementationStatus"], "OPERATOR_REVIEW_DECISION_LAYER_FOUNDATION_COMPLETE")
        self.assertEqual(
            self.projection["readinessOutcome"],
            "OPERATOR_REVIEW_DECISION_QUEUE_COMPLETE_PENDING_OPERATOR_ACTION",
        )


class OperatorReviewDecisionBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/operator_review_decision").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/operator_review_decision_projection.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
