"""Tests for ONE-AIRPORT-GA-04 final local verification."""
from __future__ import annotations

import json
import unittest

from industry_profiles.airport.international_ga_final_verification import build_airport_international_ga_final_local_verification
from international_ga_final_verification.validation import EXPECTED_SUMMARY, validate_international_ga_final_local_verification


class AirportInternationalGaFinalVerificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.verification = build_airport_international_ga_final_local_verification()

    def test_summary_freeze(self) -> None:
        self.assertEqual(EXPECTED_SUMMARY, self.verification["summary"])

    def test_verification_matrix(self) -> None:
        self.assertGreaterEqual(len(self.verification["localVerificationMatrix"]), 18)
        self.assertTrue(all(item["required"] for item in self.verification["localVerificationMatrix"]))
        self.assertTrue(all(item["status"] == "PASS" for item in self.verification["localVerificationMatrix"]))

    def test_commit_chain_and_artifacts(self) -> None:
        self.assertGreaterEqual(len(self.verification["commitChainSummary"]), 12)
        self.assertGreaterEqual(len(self.verification["activeArtifactSnapshot"]), 10)
        self.assertGreaterEqual(sum(1 for item in self.verification["activeArtifactSnapshot"] if item["present"]), 9)

    def test_tag_and_push_are_text_only(self) -> None:
        tag = self.verification["optionalTagPlan"]
        push = self.verification["optionalPushPlan"]
        self.assertFalse(tag["tagAllowedNow"])
        self.assertFalse(push["pushAllowedNow"])
        self.assertTrue(tag["requiresExplicitUserApproval"])
        self.assertTrue(push["requiresExplicitUserApproval"])
        self.assertIn("git tag -a airport-international-ga-ready-readonly-rc-20260620", tag["suggestedCommand"])
        self.assertIn("git push origin main", push["suggestedCommand"])

    def test_boundaries_and_decision(self) -> None:
        boundary = self.verification["finalBoundaryStatement"]
        for key in ("databaseWriteAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "apiProductionAllowed", "frontendProductionAllowed", "approvalExecutionAllowed", "pushAllowed", "tagAllowed", "customerIdentifierLeakageAllowed"):
            self.assertIs(boundary[key], False)
        decision = self.verification["finalReleaseDecision"]
        self.assertEqual("INTERNATIONAL_GA_LOCAL_VERIFICATION_PASS", decision["decisionState"])
        self.assertTrue(decision["internationalGaReleaseCandidateReady"])
        self.assertFalse(decision["pushAllowed"])
        self.assertFalse(decision["tagAllowed"])

    def test_handoff_and_gates(self) -> None:
        self.assertTrue(all(self.verification["handoffConfirmation"][key] for key in ("handoffNotesFrozen", "releasePackageReady", "releaseGatePassed", "validationMatrixReady", "stakeholderHandoffReady", "engineeringHandoffReady")))
        self.assertEqual(15, len(self.verification["verificationGates"]))
        self.assertTrue(all(item["status"] == "PASS" for item in self.verification["verificationGates"]))

    def test_identifier_safety(self) -> None:
        serialized = json.dumps(self.verification, sort_keys=True)
        self.assertNotIn("customerAssetIdentifier", serialized)
        self.assertNotIn("assetId", serialized)
        self.assertNotIn("deviceId", serialized)

    def test_validator_accepts_verification(self) -> None:
        validate_international_ga_final_local_verification(self.verification)


if __name__ == "__main__":
    unittest.main()
