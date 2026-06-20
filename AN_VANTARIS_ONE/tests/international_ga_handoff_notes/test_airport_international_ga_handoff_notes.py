"""Tests for ONE-AIRPORT-GA-03 International GA handoff notes."""
from __future__ import annotations

import json
import unittest

from industry_profiles.airport.international_ga_handoff_notes import (
    IMPLEMENTATION_STATUS,
    READINESS_OUTCOME,
    build_airport_international_ga_handoff_notes,
)
from international_ga_handoff_notes.validation import EXPECTED_SUMMARY, validate_international_ga_handoff_notes


class AirportInternationalGaHandoffNotesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.notes = build_airport_international_ga_handoff_notes()

    def test_summary_freeze(self) -> None:
        self.assertEqual(EXPECTED_SUMMARY, self.notes["summary"])

    def test_release_notes(self) -> None:
        release = self.notes["releaseNotes"]
        self.assertEqual("VANTARIS ONE Airport International GA-ready Read-only Release Candidate", release["releaseTitle"])
        self.assertEqual("INTERNATIONAL_GA_READY_READ_ONLY_FOUNDATION", release["releaseType"])
        self.assertEqual("VANTARIS_ONE_AIRPORT_INTERNATIONAL_GA_READY_RC", release["releaseCandidateName"])
        self.assertEqual(10, len(release["includedStageGroups"]))
        self.assertEqual(15, len(release["includedBusinessCapabilities"]))
        self.assertEqual(IMPLEMENTATION_STATUS, self.notes["implementationStatus"])
        self.assertEqual(READINESS_OUTCOME, self.notes["readinessOutcome"])

    def test_handoff_sections(self) -> None:
        self.assertEqual(7, len(self.notes["stakeholderHandoffSections"]))
        self.assertEqual(6, len(self.notes["engineeringHandoffSections"]))
        engineering = {item["engineeringArea"]: item for item in self.notes["engineeringHandoffSections"]}
        self.assertTrue(engineering["READ_ONLY_API_ROUTE_IMPLEMENTATION"]["nextPhaseAllowed"])
        self.assertTrue(engineering["READ_ONLY_FRONTEND_IMPLEMENTATION"]["nextPhaseAllowed"])
        self.assertFalse(engineering["RUNTIME_ACTIVATION_FUTURE_PHASE"]["implementationAllowedNow"])
        self.assertFalse(engineering["PRODUCTION_DEPLOYMENT_FUTURE_PHASE"]["implementationAllowedNow"])

    def test_validation_warnings_and_gates(self) -> None:
        self.assertEqual(21, len(self.notes["validationCommandSet"]))
        self.assertTrue(all(item["requiredForHandoff"] for item in self.notes["validationCommandSet"]))
        self.assertEqual(5, len(self.notes["knownWarnings"]))
        self.assertFalse(any(item["blocking"] for item in self.notes["knownWarnings"]))
        self.assertEqual(13, len(self.notes["handoffGates"]))
        self.assertTrue(all(item["status"] == "PASS" for item in self.notes["handoffGates"]))

    def test_next_phase_plan(self) -> None:
        phases = {item["phaseKey"]: item for item in self.notes["nextPhasePlan"]}
        self.assertEqual(6, len(phases))
        self.assertTrue(phases["READ_ONLY_API_ROUTE_IMPLEMENTATION"]["allowed"])
        self.assertTrue(phases["READ_ONLY_FRONTEND_IMPLEMENTATION"]["allowed"])
        for key in ("OPERATOR_DECISION_EXECUTION", "RUNTIME_ACTIVATION", "PRODUCTION_DEPLOYMENT", "PUSH_AND_TAG_RELEASE"):
            self.assertFalse(phases[key]["allowed"])

    def test_boundary_statement(self) -> None:
        boundary = self.notes["boundaryStatement"]
        for key in ("databaseWriteAllowed", "runtimeActivationAllowed", "productionActivationAllowed", "apiProductionAllowed", "frontendProductionAllowed", "approvalExecutionAllowed", "pushAllowed", "tagAllowed", "customerIdentifierLeakageAllowed"):
            self.assertIs(boundary[key], False)

    def test_identifier_and_terminology_safety(self) -> None:
        serialized = json.dumps(self.notes, sort_keys=True)
        self.assertNotIn("customerAssetIdentifier", serialized)
        self.assertNotIn("assetId", serialized)
        self.assertNotIn("deviceId", serialized)
        allowed = "historical " + "P" + "OC" + "-named artifacts are compatibility-only"
        self.assertNotIn("P" + "OC", serialized.replace(allowed, ""))

    def test_validator_accepts_notes(self) -> None:
        validate_international_ga_handoff_notes(self.notes)


if __name__ == "__main__":
    unittest.main()
