from __future__ import annotations

import json
import unittest
from pathlib import Path

from industry_profiles.airport.workorder_intent_candidate_projection import (
    build_airport_workorder_intent_candidate_projection,
)
from workorder_intent_candidate.projection import build_facets, paginate_candidates, sort_candidates
from workorder_intent_candidate.validation import validate_boundary, validate_workorder_intent_projection

ROOT = Path(__file__).resolve().parents[3]


class AirportWorkOrderIntentCandidateProjectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.projection = build_airport_workorder_intent_candidate_projection()
        self.summary = self.projection["summary"]
        self.candidates = self.projection["workOrderIntentCandidates"]
        self.cards = self.projection["reviewCards"]

    def test_exact_counts(self) -> None:
        self.assertEqual(len(self.candidates), 5)
        self.assertEqual(len(self.cards), 10)
        self.assertEqual(self.summary["workOrderIntentCandidateCount"], 5)
        self.assertEqual(self.summary["reviewCardCount"], 10)
        self.assertEqual(self.summary["totalDeviceEvidenceCount"], 470)

    def test_source_types_and_disciplines(self) -> None:
        by_key = {item["sourceSystemKey"]: item for item in self.candidates}
        self.assertEqual(set(by_key), {"ACS", "RAS", "CCTV", "PA", "TEL"})
        self.assertEqual(by_key["ACS"]["deviceEvidenceCount"], 129)
        self.assertEqual(by_key["RAS"]["deviceEvidenceCount"], 28)
        self.assertEqual(by_key["CCTV"]["deviceEvidenceCount"], 52)
        self.assertEqual(by_key["PA"]["deviceEvidenceCount"], 247)
        self.assertEqual(by_key["TEL"]["deviceEvidenceCount"], 14)
        self.assertEqual(by_key["ACS"]["proposedWorkOrderIntentType"], "CORRECTIVE_MAINTENANCE")
        self.assertEqual(by_key["RAS"]["proposedWorkOrderIntentType"], "INVESTIGATION_REQUEST")
        self.assertEqual(by_key["CCTV"]["proposedWorkOrderIntentType"], "INVESTIGATION_REQUEST")
        self.assertEqual(by_key["PA"]["proposedWorkOrderIntentType"], "CORRECTIVE_MAINTENANCE")
        self.assertEqual(by_key["TEL"]["proposedWorkOrderIntentType"], "INVESTIGATION_REQUEST")
        self.assertEqual(by_key["ACS"]["proposedTradeDiscipline"], "SECURITY")
        self.assertEqual(by_key["RAS"]["proposedTradeDiscipline"], "COMMUNICATION")
        self.assertEqual(by_key["CCTV"]["proposedTradeDiscipline"], "SECURITY")
        self.assertEqual(by_key["PA"]["proposedTradeDiscipline"], "ELV")
        self.assertEqual(by_key["TEL"]["proposedTradeDiscipline"], "COMMUNICATION")
        self.assertEqual(self.summary["correctiveMaintenanceCandidateCount"], 2)
        self.assertEqual(self.summary["investigationRequestCandidateCount"], 3)

    def test_all_candidates_blocked_or_review_only(self) -> None:
        for candidate in self.candidates:
            self.assertTrue(candidate["decisionRequired"])
            self.assertIn(candidate["eligibilityState"], {
                "ELIGIBLE_FOR_REVIEW",
                "BLOCKED_BY_FAULTCASE_REVIEW",
                "BLOCKED_BY_RESOLUTION",
                "BLOCKED_BY_SOURCE_SYSTEM_REVIEW",
                "BLOCKED_BY_POLICY",
            })
            self.assertEqual(candidate["downstreamCreationState"], "NOT_AUTHORIZED")
            self.assertIn("BLOCKED_BY_FAULTCASE_REVIEW", candidate["blockingReasons"])
            self.assertIn("BLOCKED_BY_RESOLUTION", candidate["blockingReasons"])
            self.assertIn("BLOCKED_BY_SOURCE_SYSTEM_REVIEW", candidate["blockingReasons"])
            self.assertIn("WORK_MANAGEMENT_POLICY_REVIEW_REQUIRED", candidate["reviewReasons"])
        self.assertEqual(self.summary["blockedByFaultCaseReviewCount"], 5)
        self.assertEqual(self.summary["blockedByResolutionCount"], 5)
        self.assertEqual(self.summary["blockedBySourceSystemReviewCount"], 5)
        self.assertEqual(self.summary["workManagementPolicyReviewRequiredCount"], 5)
        self.assertEqual(self.summary["decisionRequiredCount"], 5)

    def test_no_downstream_or_runtime_writes(self) -> None:
        for key in (
            "workOrderIntentCreatedCount",
            "workOrderCreatedCount",
            "ummsWriteCount",
            "oneWorkManagementWriteCount",
            "canonicalWriteCount",
            "databaseWriteCount",
            "runtimeAlarmObservedCount",
        ):
            self.assertEqual(self.summary[key], 0)

    def test_no_identifier_leakage(self) -> None:
        self.assertFalse(self.summary["containsCustomerAssetIdentifiers"])
        text = json.dumps(self.projection, sort_keys=True).lower()
        for forbidden in ("customer_device_id", "customer_asset_id", "customer asset identifier:", "live alarm"):
            self.assertNotIn(forbidden, text)

    def test_review_cards_are_aggregated(self) -> None:
        by_type = {card["reviewType"]: card for card in self.cards}
        self.assertEqual(len(by_type), 10)
        self.assertEqual(by_type["REGISTRY_APPROVAL_REQUIRED"]["affectedSourceSystemKeys"], ["ACS", "RAS"])
        self.assertEqual(by_type["ALIAS_APPROVAL_REQUIRED"]["affectedSourceSystemKeys"], ["CCTV", "PA"])
        self.assertEqual(by_type["NAMESPACE_INTERPRETATION_REQUIRED"]["affectedSourceSystemKeys"], ["TEL"])
        self.assertEqual(by_type["WORKORDER_INTENT_CREATION_NOT_AUTHORIZED"]["affectedCandidateCount"], 5)
        self.assertEqual(by_type["WORK_MANAGEMENT_POLICY_REVIEW_REQUIRED"]["affectedDeviceEvidenceCount"], 470)

    def test_deterministic_candidates_cards_facets_pagination_and_repeated_run(self) -> None:
        self.assertEqual(self.candidates, sort_candidates(self.candidates))
        self.assertEqual(self.projection["facets"], build_facets(self.candidates))
        self.assertEqual(self.projection["defaultPage"], paginate_candidates(self.candidates, page_size=25))
        again = build_airport_workorder_intent_candidate_projection()
        self.assertEqual(
            json.dumps(self.projection, sort_keys=True, separators=(",", ":")),
            json.dumps(again, sort_keys=True, separators=(",", ":")),
        )

    def test_projection_validation(self) -> None:
        validate_workorder_intent_projection(self.projection)
        self.assertEqual(self.projection["implementationStatus"], "WORKORDER_INTENT_CANDIDATE_PROJECTION_COMPLETE")
        self.assertEqual(self.projection["readinessOutcome"], "WORKORDER_INTENT_CANDIDATES_COMPLETE_WITH_PENDING_REVIEWS")


class WorkOrderIntentCandidateBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/workorder_intent_candidate").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/workorder_intent_candidate_projection.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
