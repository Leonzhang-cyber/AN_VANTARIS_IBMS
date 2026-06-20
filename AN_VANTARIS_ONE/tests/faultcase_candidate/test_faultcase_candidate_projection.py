from __future__ import annotations

import json
import unittest
from pathlib import Path

from faultcase_candidate.projection import build_facets, paginate_candidates, sort_candidates
from faultcase_candidate.validation import validate_boundary, validate_faultcase_projection
from industry_profiles.airport.faultcase_candidate_projection import build_airport_faultcase_candidate_projection

ROOT = Path(__file__).resolve().parents[3]


class AirportFaultCaseCandidateProjectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.projection = build_airport_faultcase_candidate_projection()
        self.summary = self.projection["summary"]
        self.candidates = self.projection["faultCaseCandidates"]
        self.cards = self.projection["reviewCards"]

    def test_exact_counts(self) -> None:
        self.assertEqual(len(self.candidates), 5)
        self.assertEqual(len(self.cards), 8)
        self.assertEqual(self.summary["faultCaseCandidateCount"], 5)
        self.assertEqual(self.summary["reviewCardCount"], 8)
        self.assertEqual(self.summary["totalDeviceEvidenceCount"], 470)

    def test_source_counts_and_fault_types(self) -> None:
        by_key = {item["sourceSystemKey"]: item for item in self.candidates}
        self.assertEqual(set(by_key), {"ACS", "RAS", "CCTV", "PA", "TEL"})
        self.assertEqual(by_key["ACS"]["proposedFaultCaseType"], "SECURITY_FAULT")
        self.assertEqual(by_key["RAS"]["proposedFaultCaseType"], "COMMUNICATION_FAULT")
        self.assertEqual(by_key["CCTV"]["proposedFaultCaseType"], "SECURITY_FAULT")
        self.assertEqual(by_key["PA"]["proposedFaultCaseType"], "EQUIPMENT_FAULT")
        self.assertEqual(by_key["TEL"]["proposedFaultCaseType"], "COMMUNICATION_FAULT")
        self.assertEqual(self.summary["securityFaultCandidateCount"], 2)
        self.assertEqual(self.summary["communicationFaultCandidateCount"], 2)
        self.assertEqual(self.summary["equipmentFaultCandidateCount"], 1)

    def test_all_candidates_are_review_only_and_blocked(self) -> None:
        for candidate in self.candidates:
            self.assertTrue(candidate["decisionRequired"])
            self.assertIn(candidate["proposedFaultState"], {"REVIEW_REQUIRED", "BLOCKED"})
            self.assertIn(candidate["eligibilityState"], {"BLOCKED_BY_RESOLUTION", "BLOCKED_BY_SOURCE_SYSTEM_REVIEW", "BLOCKED_BY_POLICY", "ELIGIBLE_FOR_REVIEW"})
            self.assertEqual(candidate["downstreamCreationState"], "NOT_AUTHORIZED")
            self.assertIn("BLOCKED_BY_RESOLUTION", candidate["blockingReasons"])
            self.assertIn("BLOCKED_BY_SOURCE_SYSTEM_REVIEW", candidate["blockingReasons"])
        self.assertEqual(self.summary["blockedByResolutionCount"], 5)
        self.assertEqual(self.summary["blockedBySourceSystemReviewCount"], 5)
        self.assertEqual(self.summary["decisionRequiredCount"], 5)

    def test_no_downstream_or_runtime_writes(self) -> None:
        for key in (
            "ufmsFaultCaseCreatedCount",
            "workOrderIntentCreatedCount",
            "workOrderCreatedCount",
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
        self.assertEqual(
            set(by_type),
            {
                "FAULTCASE_CREATION_NOT_AUTHORIZED",
                "SOURCE_SYSTEM_REVIEW_REQUIRED",
                "ASSET_RESOLUTION_REQUIRED",
                "POINT_RESOLUTION_REQUIRED",
                "LOCATION_RESOLUTION_REQUIRED",
                "REGISTRY_APPROVAL_REQUIRED",
                "ALIAS_APPROVAL_REQUIRED",
                "NAMESPACE_INTERPRETATION_REQUIRED",
            },
        )
        self.assertEqual(by_type["REGISTRY_APPROVAL_REQUIRED"]["affectedSourceSystemKeys"], ["ACS", "RAS"])
        self.assertEqual(by_type["ALIAS_APPROVAL_REQUIRED"]["affectedSourceSystemKeys"], ["CCTV", "PA"])
        self.assertEqual(by_type["NAMESPACE_INTERPRETATION_REQUIRED"]["affectedSourceSystemKeys"], ["TEL"])
        self.assertEqual(by_type["FAULTCASE_CREATION_NOT_AUTHORIZED"]["affectedCandidateCount"], 5)
        self.assertEqual(by_type["SOURCE_SYSTEM_REVIEW_REQUIRED"]["affectedDeviceEvidenceCount"], 470)

    def test_deterministic_candidates_cards_facets_pagination_and_repeated_run(self) -> None:
        self.assertEqual(self.candidates, sort_candidates(self.candidates))
        self.assertEqual(self.projection["facets"], build_facets(self.candidates))
        self.assertEqual(self.projection["defaultPage"], paginate_candidates(self.candidates, page_size=25))
        again = build_airport_faultcase_candidate_projection()
        self.assertEqual(
            json.dumps(self.projection, sort_keys=True, separators=(",", ":")),
            json.dumps(again, sort_keys=True, separators=(",", ":")),
        )

    def test_projection_validation(self) -> None:
        validate_faultcase_projection(self.projection)
        self.assertEqual(self.projection["implementationStatus"], "UFMS_FAULTCASE_CANDIDATE_PROJECTION_COMPLETE")
        self.assertEqual(self.projection["readinessOutcome"], "FAULTCASE_CANDIDATES_COMPLETE_WITH_PENDING_REVIEWS")


class FaultCaseCandidateBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/faultcase_candidate").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/faultcase_candidate_projection.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
