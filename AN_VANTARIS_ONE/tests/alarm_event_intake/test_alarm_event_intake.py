from __future__ import annotations

import json
import unittest
from pathlib import Path

from alarm_event_intake.normalization import normalize_intake_envelope
from alarm_event_intake.projection import build_facets, paginate_candidates, sort_candidates
from industry_profiles.airport.alarm_event_intake_profile import (
    ALLOWED_SOURCE_SYSTEM_KEYS,
    build_airport_alarm_event_intake_projection,
)

ROOT = Path(__file__).resolve().parents[3]


class AlarmEventIntakeFoundationTest(unittest.TestCase):
    def _valid_raw(self) -> dict[str, object]:
        return {
            "sourceSystemKey": "ACS",
            "registryEntryId": "registry-acs",
            "eventKind": "ALARM",
            "eventCategory": "SECURITY",
            "eventSeverity": "HIGH",
            "eventState": "RAISED",
            "sourceEventReference": "safe-source-event-digest",
            "eventTemplate": "offline fixture candidate",
            "assetReferenceDigest": "asset-digest",
            "pointReferenceDigest": "point-digest",
            "locationReferenceDigest": "location-digest",
            "reviewReasons": ["REGISTRY_APPROVAL_REQUIRED"],
            "evidenceReferences": [],
        }

    def test_valid_envelope_accepted_as_candidate(self) -> None:
        envelope = normalize_intake_envelope(self._valid_raw(), allowed_source_system_keys=ALLOWED_SOURCE_SYSTEM_KEYS)
        self.assertEqual(envelope["validationState"], "ACCEPTED_AS_CANDIDATE")

    def test_missing_source_system_key_rejected(self) -> None:
        raw = self._valid_raw()
        raw["sourceSystemKey"] = ""
        envelope = normalize_intake_envelope(raw, allowed_source_system_keys=ALLOWED_SOURCE_SYSTEM_KEYS)
        self.assertEqual(envelope["validationState"], "REJECTED")
        self.assertIn("SOURCE_SYSTEM_KEY_REQUIRED", envelope["rejectionReasons"])

    def test_unknown_source_system_key_rejected(self) -> None:
        raw = self._valid_raw()
        raw["sourceSystemKey"] = "UNKNOWN_SYSTEM"
        envelope = normalize_intake_envelope(raw, allowed_source_system_keys=ALLOWED_SOURCE_SYSTEM_KEYS)
        self.assertEqual(envelope["validationState"], "REJECTED")
        self.assertIn("SOURCE_SYSTEM_KEY_UNKNOWN", envelope["rejectionReasons"])

    def test_missing_event_kind_rejected(self) -> None:
        raw = self._valid_raw()
        raw["eventKind"] = ""
        envelope = normalize_intake_envelope(raw, allowed_source_system_keys=ALLOWED_SOURCE_SYSTEM_KEYS)
        self.assertEqual(envelope["validationState"], "REJECTED")
        self.assertIn("EVENT_KIND_REQUIRED", envelope["rejectionReasons"])

    def test_missing_source_event_reference_rejected(self) -> None:
        raw = self._valid_raw()
        raw["sourceEventReference"] = ""
        envelope = normalize_intake_envelope(raw, allowed_source_system_keys=ALLOWED_SOURCE_SYSTEM_KEYS)
        self.assertEqual(envelope["validationState"], "REJECTED")
        self.assertIn("SOURCE_EVENT_REFERENCE_REQUIRED", envelope["rejectionReasons"])

    def test_missing_severity_review_required_without_profile_permission(self) -> None:
        raw = self._valid_raw()
        raw["eventSeverity"] = ""
        envelope = normalize_intake_envelope(raw, allowed_source_system_keys=ALLOWED_SOURCE_SYSTEM_KEYS)
        self.assertEqual(envelope["validationState"], "REVIEW_REQUIRED")
        self.assertIn("EVENT_SEVERITY_REQUIRED", envelope["reviewReasons"])

    def test_deterministic_intake_ids_and_payload_digest(self) -> None:
        left = normalize_intake_envelope(self._valid_raw(), allowed_source_system_keys=ALLOWED_SOURCE_SYSTEM_KEYS)
        right = normalize_intake_envelope(self._valid_raw(), allowed_source_system_keys=ALLOWED_SOURCE_SYSTEM_KEYS)
        self.assertEqual(left["intakeEnvelopeId"], right["intakeEnvelopeId"])
        self.assertEqual(left["payloadDigest"], right["payloadDigest"])
        self.assertEqual(left["deterministicDigest"], right["deterministicDigest"])

    def test_no_volatile_timestamp_or_runtime_flags(self) -> None:
        envelope = normalize_intake_envelope(self._valid_raw(), allowed_source_system_keys=ALLOWED_SOURCE_SYSTEM_KEYS)
        serialized = json.dumps(envelope, sort_keys=True)
        self.assertNotIn("lastSeen", serialized)
        self.assertNotIn("latency", serialized.lower())
        self.assertEqual(envelope["eventTimePolicy"], "DETERMINISTIC_NO_VOLATILE_TIMESTAMP")
        self.assertFalse(envelope["payload"]["runtimeAlarmObserved"])


class AirportAlarmEventIntakeProjectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.projection = build_airport_alarm_event_intake_projection()
        self.summary = self.projection["summary"]
        self.candidates = self.projection["candidates"]

    def test_exactly_five_source_systems_envelopes_and_candidates(self) -> None:
        self.assertEqual(self.summary["sourceSystemCandidateCount"], 5)
        self.assertEqual(self.summary["intakeEnvelopeCount"], 5)
        self.assertEqual(self.summary["canonicalAlarmEventCandidateCount"], 5)
        self.assertEqual({item["sourceSystemKey"] for item in self.candidates}, {"ACS", "RAS", "CCTV", "PA", "TEL"})

    def test_expected_counts(self) -> None:
        self.assertEqual(self.summary["acceptedAsCandidateCount"], 5)
        self.assertEqual(self.summary["rejectedEnvelopeCount"], 0)
        self.assertEqual(self.summary["reviewRequiredCandidateCount"], 5)

    def test_source_specific_reviews(self) -> None:
        by_key = {item["sourceSystemKey"]: item for item in self.candidates}
        self.assertIn("REGISTRY_APPROVAL_REQUIRED", by_key["ACS"]["reviewReasons"])
        self.assertIn("REGISTRY_APPROVAL_REQUIRED", by_key["RAS"]["reviewReasons"])
        self.assertIn("ALIAS_APPROVAL_REQUIRED", by_key["CCTV"]["reviewReasons"])
        self.assertIn("ALIAS_APPROVAL_REQUIRED", by_key["PA"]["reviewReasons"])
        self.assertIn("NAMESPACE_INTERPRETATION_REQUIRED", by_key["TEL"]["reviewReasons"])

    def test_resolution_remains_review_required(self) -> None:
        for candidate in self.candidates:
            self.assertEqual(candidate["assetResolutionState"], "REVIEW_REQUIRED")
            self.assertEqual(candidate["pointResolutionState"], "REVIEW_REQUIRED")
            self.assertEqual(candidate["locationResolutionState"], "REVIEW_REQUIRED")
            self.assertEqual(candidate["ufmsFaultCaseCandidateState"], "BLOCKED")
            self.assertEqual(candidate["workOrderIntentCandidateState"], "BLOCKED")

    def test_no_downstream_or_runtime_creation(self) -> None:
        for key in (
            "ufmsFaultCaseCreatedCount",
            "workOrderIntentCreatedCount",
            "workOrderCreatedCount",
            "evidenceCenterWriteCount",
            "runtimeAlarmObservedCount",
            "databaseWriteCount",
            "canonicalWriteCount",
        ):
            self.assertEqual(self.summary[key], 0)
        self.assertFalse(self.summary["liveAlarmPollingEnabled"])
        self.assertFalse(self.summary["connectorExecutionEnabled"])
        self.assertFalse(self.summary["productionActivationEnabled"])
        self.assertFalse(self.summary["containsCustomerAssetIdentifiers"])

    def test_review_cards_are_aggregated_root_causes(self) -> None:
        reasons = {card["reason"] for card in self.projection["reviewCards"]}
        self.assertEqual(
            reasons,
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
        self.assertLess(len(self.projection["reviewCards"]), len(self.candidates) * 2)

    def test_deterministic_ordering_pagination_facets_and_repeated_run(self) -> None:
        self.assertEqual(self.candidates, sort_candidates(self.candidates))
        self.assertEqual(self.projection["defaultPage"], paginate_candidates(self.candidates, page_size=25))
        self.assertEqual(self.projection["facets"], build_facets(self.candidates))
        again = build_airport_alarm_event_intake_projection()
        self.assertEqual(
            json.dumps(self.projection, sort_keys=True, separators=(",", ":")),
            json.dumps(again, sort_keys=True, separators=(",", ":")),
        )

    def test_no_customer_device_or_asset_identifier_leakage(self) -> None:
        text = json.dumps(self.projection, sort_keys=True).lower()
        self.assertFalse(self.summary["containsCustomerAssetIdentifiers"])
        for forbidden in ("customer_device_id", "customer_asset_id", "customer asset identifier:", "live alarm"):
            self.assertNotIn(forbidden, text)

    def test_contract_status_and_readiness(self) -> None:
        self.assertEqual(self.projection["implementationStatus"], "CANONICAL_ALARM_EVENT_INTAKE_FOUNDATION_COMPLETE")
        self.assertEqual(
            self.projection["readinessOutcome"],
            "ALARM_EVENT_INTAKE_CANDIDATES_COMPLETE_WITH_PENDING_REVIEWS",
        )


class AlarmEventIntakeBoundaryTest(unittest.TestCase):
    def test_no_forbidden_runtime_terms_in_owned_source(self) -> None:
        owned_paths = list((ROOT / "AN_VANTARIS_ONE/alarm_event_intake").glob("*.py")) + [
            ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/alarm_event_intake_profile.py"
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in owned_paths).lower()
        for forbidden in (
            "sqlalchemy",
            "flask",
            "requests.",
            "urllib",
            "socket",
            "blueprint",
            "react",
            "heartbeat",
            "polling loop",
            "faultcase_created",
            "work_order_created",
        ):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
