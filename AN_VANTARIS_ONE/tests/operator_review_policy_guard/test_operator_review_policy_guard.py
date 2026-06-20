from __future__ import annotations

import json
import unittest
from pathlib import Path

from industry_profiles.airport.operator_review_policy_guard_projection import build_airport_operator_review_policy_guard_projection
from operator_review_policy_guard.policy import evaluate_decision_policy
from operator_review_policy_guard.projection import build_facets, build_filters, paginate_guard_results, sort_guard_results
from operator_review_policy_guard.validation import validate_boundary, validate_policy_guard_projection

ROOT = Path(__file__).resolve().parents[3]


class AirportOperatorReviewPolicyGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.projection = build_airport_operator_review_policy_guard_projection()
        self.summary = self.projection["summary"]
        self.results = self.projection["policyGuardResults"]
        self.previews = self.projection["auditPreviews"]
        self.groups = self.projection["guardGroups"]

    def test_expected_counts(self) -> None:
        expected = {
            "decisionItemCount": 46,
            "policyGuardResultCount": 46,
            "auditPreviewCount": 46,
            "guardGroupCount": 8,
            "eligibleForPreviewCount": 46,
            "eligibleForExecutionCount": 0,
            "blockedByPolicyCount": 46,
            "writeAllowedCount": 0,
            "approvalAllowedCount": 0,
            "runtimeActivationAllowedCount": 0,
            "productionActivationAllowedCount": 0,
            "auditPreviewGeneratedCount": 46,
            "decisionWriteCount": 0,
            "approvalWriteCount": 0,
            "canonicalWriteCount": 0,
            "databaseWriteCount": 0,
        }
        for key, value in expected.items():
            self.assertEqual(self.summary[key], value)

    def test_all_guards_are_preview_only_and_block_execution(self) -> None:
        for result in self.results:
            self.assertEqual(result["requestedDecision"], "PREVIEW_ONLY")
            self.assertEqual(result["currentDecision"], "KEEP_PENDING")
            self.assertEqual(result["guardState"], "BLOCKED_BY_POLICY")
            self.assertEqual(result["eligibilityState"], "ELIGIBLE_FOR_PREVIEW")
            self.assertFalse(result["writeAllowed"])
            self.assertFalse(result["approvalAllowed"])
            self.assertFalse(result["runtimeActivationAllowed"])
            self.assertFalse(result["productionActivationAllowed"])
            self.assertFalse(result["apiRequired"])
            self.assertFalse(result["frontendRequired"])

    def test_audit_previews_are_read_only(self) -> None:
        for preview in self.previews:
            self.assertEqual(preview["auditPreviewState"], "GENERATED_READ_ONLY")
            self.assertEqual(preview["writeTarget"], "READ_ONLY_PREVIEW")
            self.assertFalse(preview["writeAllowed"])
            self.assertFalse(preview["approvalWriteAllowed"])

    def test_groups(self) -> None:
        self.assertEqual(
            [group["groupType"] for group in self.groups],
            [
                "ALL_DECISION_GUARDS",
                "SOURCE_SYSTEM_GUARDS",
                "ASSET_RESOLUTION_GUARDS",
                "ALARM_EVENT_GUARDS",
                "FAULTCASE_GUARDS",
                "WORKORDER_INTENT_GUARDS",
                "EVIDENCE_INVESTIGATION_GUARDS",
                "RELEASE_GATE_GUARDS",
            ],
        )
        self.assertEqual(self.groups[0]["eligibleCount"], 46)
        self.assertEqual(self.groups[0]["blockedCount"], 46)
        self.assertTrue(all(group["writeAllowedCount"] == 0 for group in self.groups))
        self.assertTrue(all(group["approvalAllowedCount"] == 0 for group in self.groups))

    def test_fail_closed_policy_rules(self) -> None:
        missing_id = evaluate_decision_policy({"decisionType": "REGISTRY_APPROVAL", "decisionState": "PENDING"})
        self.assertEqual(missing_id["guardState"], "BLOCKED_BY_PRECONDITION")
        self.assertIn("decisionItemId", missing_id["missingPreconditions"])
        approved = evaluate_decision_policy({"decisionItemId": "x", "decisionType": "REGISTRY_APPROVAL", "decisionState": "APPROVED"})
        self.assertEqual(approved["guardState"], "BLOCKED_BY_POLICY")
        self.assertIn("INPUT_DECISION_ALREADY_APPLIED", approved["reasonCodes"])

    def test_no_identifier_leakage(self) -> None:
        text = json.dumps(self.projection, sort_keys=True).lower()
        for forbidden in ("customer_device_id", "customer_asset_id", "customer asset identifier:", "live alarm timestamp"):
            self.assertNotIn(forbidden, text)

    def test_deterministic_helpers(self) -> None:
        self.assertEqual(self.results, sort_guard_results(self.results))
        self.assertEqual(self.projection["facets"], build_facets(self.results, self.previews))
        self.assertEqual(self.projection["filters"], build_filters(self.results, self.previews))
        self.assertEqual(self.projection["defaultPage"], paginate_guard_results(self.results, page_size=25))

    def test_deterministic_projection(self) -> None:
        again = build_airport_operator_review_policy_guard_projection()
        self.assertEqual(
            json.dumps(self.projection, sort_keys=True, separators=(",", ":")),
            json.dumps(again, sort_keys=True, separators=(",", ":")),
        )

    def test_projection_validation(self) -> None:
        validate_policy_guard_projection(self.projection)
        self.assertEqual(self.projection["implementationStatus"], "OPERATOR_REVIEW_DECISION_AUDIT_AND_POLICY_GUARD_COMPLETE")
        self.assertEqual(self.projection["readinessOutcome"], "OPERATOR_REVIEW_POLICY_GUARD_READY_FOR_READ_ONLY_PREVIEW")


class OperatorReviewPolicyGuardBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_imports_or_terms(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/operator_review_policy_guard").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/operator_review_policy_guard_projection.py"
        ]
        validate_boundary("\n".join(path.read_text(encoding="utf-8") for path in owned_paths))


if __name__ == "__main__":
    unittest.main()
