from __future__ import annotations

import json
import unittest
from pathlib import Path

from evidence_investigation_projection.projection import build_facets, paginate_cases, sort_cases
from evidence_investigation_projection.validation import (
    validate_boundary,
    validate_evidence_investigation_projection,
)
from industry_profiles.airport.evidence_investigation_projection import build_airport_evidence_investigation_projection

ROOT = Path(__file__).resolve().parents[3]


class AirportEvidenceInvestigationProjectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.projection = build_airport_evidence_investigation_projection()
        self.summary = self.projection["summary"]
        self.cases = self.projection["investigationCases"]
        self.links = self.projection["evidenceLinks"]
        self.timeline = self.projection["investigationTimeline"]
        self.cards = self.projection["reviewCards"]

    def test_exact_core_counts(self) -> None:
        self.assertEqual(len(self.cases), 5)
        self.assertGreaterEqual(len(self.links), 20)
        self.assertGreaterEqual(len(self.timeline), 20)
        self.assertEqual(len(self.cards), 9)
        self.assertEqual(self.summary["investigationCaseCount"], 5)
        self.assertEqual(self.summary["evidenceLinkCount"], len(self.links))
        self.assertEqual(self.summary["timelineItemCount"], len(self.timeline))
        self.assertEqual(self.summary["reviewCardCount"], 9)
        self.assertEqual(self.summary["totalDeviceEvidenceCount"], 470)

    def test_source_counts(self) -> None:
        by_key = {case["sourceSystemKey"]: case for case in self.cases}
        self.assertEqual(set(by_key), {"ACS", "RAS", "CCTV", "PA", "TEL"})
        self.assertEqual(by_key["ACS"]["deviceEvidenceCount"], 129)
        self.assertEqual(by_key["RAS"]["deviceEvidenceCount"], 28)
        self.assertEqual(by_key["CCTV"]["deviceEvidenceCount"], 52)
        self.assertEqual(by_key["PA"]["deviceEvidenceCount"], 247)
        self.assertEqual(by_key["TEL"]["deviceEvidenceCount"], 14)

    def test_cases_linked_and_review_required(self) -> None:
        for case in self.cases:
            self.assertTrue(case["decisionRequired"])
            self.assertIn(case["investigationState"], {"REVIEW_REQUIRED", "BLOCKED"})
            self.assertIn(case["evidenceCompletenessState"], {"PARTIAL", "REVIEW_REQUIRED"})
            self.assertIn(case["linkageState"], {"LINKED", "REVIEW_REQUIRED"})
            self.assertEqual(len(case["evidenceLinkIds"]), 4)
            self.assertEqual(len(case["timelineItemIds"]), 4)
        self.assertEqual(self.summary["decisionRequiredCount"], 5)
        self.assertEqual(self.summary["partialEvidenceCaseCount"], 5)
        self.assertEqual(self.summary["linkedCaseCount"], 5)
        self.assertEqual(self.summary["registryApprovalPendingCount"], 2)
        self.assertEqual(self.summary["aliasApprovalPendingCount"], 2)
        self.assertEqual(self.summary["namespaceReviewPendingCount"], 1)

    def test_no_downstream_or_runtime_writes(self) -> None:
        for key in (
            "evidenceCenterWriteCount",
            "ufmsFaultCaseCreatedCount",
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

    def test_link_and_timeline_types(self) -> None:
        self.assertEqual(
            {link["linkType"] for link in self.links},
            {
                "ALARM_EVENT_TO_RESOLUTION",
                "RESOLUTION_TO_FAULTCASE_CANDIDATE",
                "FAULTCASE_TO_WORKORDER_INTENT_CANDIDATE",
                "SOURCE_SYSTEM_REVIEW_TO_INVESTIGATION",
            },
        )
        self.assertEqual(
            {item["itemType"] for item in self.timeline},
            {
                "ALARM_EVENT_CANDIDATE",
                "RESOLUTION_REVIEW",
                "FAULTCASE_CANDIDATE",
                "WORKORDER_INTENT_CANDIDATE",
            },
        )

    def test_review_cards_are_aggregated(self) -> None:
        by_type = {card["reviewType"]: card for card in self.cards}
        self.assertEqual(
            set(by_type),
            {
                "INVESTIGATION_REVIEW_REQUIRED",
                "EVIDENCE_CENTER_WRITE_NOT_AUTHORIZED",
                "FAULTCASE_REVIEW_REQUIRED",
                "WORKORDER_INTENT_REVIEW_REQUIRED",
                "ASSET_RESOLUTION_REQUIRED",
                "SOURCE_SYSTEM_REVIEW_REQUIRED",
                "REGISTRY_APPROVAL_REQUIRED",
                "ALIAS_APPROVAL_REQUIRED",
                "NAMESPACE_INTERPRETATION_REQUIRED",
            },
        )
        self.assertEqual(by_type["REGISTRY_APPROVAL_REQUIRED"]["affectedSourceSystemKeys"], ["ACS", "RAS"])
        self.assertEqual(by_type["ALIAS_APPROVAL_REQUIRED"]["affectedSourceSystemKeys"], ["CCTV", "PA"])
        self.assertEqual(by_type["NAMESPACE_INTERPRETATION_REQUIRED"]["affectedSourceSystemKeys"], ["TEL"])
        self.assertEqual(by_type["INVESTIGATION_REVIEW_REQUIRED"]["affectedCaseCount"], 5)
        self.assertEqual(by_type["EVIDENCE_CENTER_WRITE_NOT_AUTHORIZED"]["affectedDeviceEvidenceCount"], 470)

    def test_deterministic_projection(self) -> None:
        self.assertEqual(self.cases, sort_cases(self.cases))
        self.assertEqual(self.projection["facets"], build_facets(self.cases, self.links, self.timeline))
        self.assertEqual(self.projection["defaultPage"], paginate_cases(self.cases, page_size=25))
        again = build_airport_evidence_investigation_projection()
        self.assertEqual(
            json.dumps(self.projection, sort_keys=True, separators=(",", ":")),
            json.dumps(again, sort_keys=True, separators=(",", ":")),
        )

    def test_projection_validation(self) -> None:
        validate_evidence_investigation_projection(self.projection)
        self.assertEqual(self.projection["implementationStatus"], "EVIDENCE_INVESTIGATION_PROJECTION_COMPLETE")
        self.assertEqual(
            self.projection["readinessOutcome"],
            "EVIDENCE_INVESTIGATION_LINKAGE_COMPLETE_WITH_PENDING_REVIEWS",
        )


class EvidenceInvestigationBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/evidence_investigation_projection").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/evidence_investigation_projection.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
