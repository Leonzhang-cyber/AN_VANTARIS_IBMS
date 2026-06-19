"""Tests for airport source-system evidence binding and review projection."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from source_system_registry.enums import RegistryApprovalState, RegistryLifecycleState
from source_system_registry.errors import SourceSystemRegistryError

from industry_profiles.airport.candidate_projection import build_airport_source_system_candidates
from industry_profiles.airport.source_system_evidence_binding import (
    build_source_system_evidence_binding,
    build_source_system_evidence_bindings,
)
from industry_profiles.airport.source_system_review_projection import (
    build_review_cards,
    compare_deterministic_outputs,
    paginate_bindings,
    run_airport_source_system_review_projection,
)

AIRPORT_PROFILE = ROOT / "industry_profiles/airport/source-system-profile.v1.json"
REVIEW_PROJECTION = ROOT / "industry_profiles/airport/projections/airport-source-system-review.v1.json"
GENERIC_DIR = ROOT / "source_system_registry"
AIRPORT_DIR = ROOT / "industry_profiles/airport"


def _synthetic_bindings() -> list[dict]:
    categories = [
        ("ACCESS_CONTROL", 129, "ACS", ""),
        ("RADIO_COMMUNICATION", 28, "RAS", ""),
        ("VIDEO_SURVEILLANCE", 52, "CCTV", "CCT"),
        ("PUBLIC_ADDRESS", 247, "PA", "PAS"),
        ("TELECOMMUNICATION", 14, "TEL", ""),
    ]
    bindings: list[dict] = []
    for category, count, system_value, embedded in categories:
        for _ in range(count):
            bindings.append(
                {
                    "genericSystemCategory": category,
                    "sourceSystemValue": system_value,
                    "embeddedSystemCode": embedded,
                    "sourceNamespaceCode": "SCN" if category == "TELECOMMUNICATION" else "",
                    "systemMappingStatus": "REVIEW_REQUIRED" if category == "TELECOMMUNICATION" else "EXACT_MATCH",
                }
            )
    return bindings


def _synthetic_alias_package() -> list[dict]:
    return [
        {"proposalType": "SYSTEM_ALIAS", "targetValue": "CCTV", "decisionStatus": "APPROVAL_REQUIRED", "proposalId": "a1", "affectedRecordCount": 52},
        {"proposalType": "SYSTEM_ALIAS", "targetValue": "PA", "decisionStatus": "APPROVAL_REQUIRED", "proposalId": "a2", "affectedRecordCount": 247},
        {"proposalType": "SOURCE_NAMESPACE", "targetValue": "SOURCE_NAMESPACE_SEMANTIC_REVIEW", "decisionStatus": "APPROVAL_REQUIRED", "proposalId": "a3", "affectedRecordCount": 14},
    ]


def _synthetic_candidates() -> list[dict]:
    profile = json.loads(AIRPORT_PROFILE.read_text(encoding="utf-8"))
    return build_airport_source_system_candidates(
        bindings=_synthetic_bindings(),
        alias_package=_synthetic_alias_package(),
        airport_profile=profile,
    )


class TestEvidenceBinding(unittest.TestCase):
    def test_exactly_five_bindings(self) -> None:
        bindings = build_source_system_evidence_bindings(_synthetic_candidates())
        self.assertEqual(len(bindings), 5)

    def test_total_evidence_count_470(self) -> None:
        bindings = build_source_system_evidence_bindings(_synthetic_candidates())
        total = sum(item["deviceEvidenceCount"] for item in bindings)
        self.assertEqual(total, 470)

    def test_acs_count_129(self) -> None:
        bindings = build_source_system_evidence_bindings(_synthetic_candidates())
        acs = next(item for item in bindings if item["sourceSystemKey"] == "ACS")
        self.assertEqual(acs["deviceEvidenceCount"], 129)

    def test_ras_count_28(self) -> None:
        bindings = build_source_system_evidence_bindings(_synthetic_candidates())
        ras = next(item for item in bindings if item["sourceSystemKey"] == "RAS")
        self.assertEqual(ras["deviceEvidenceCount"], 28)

    def test_cctv_count_52(self) -> None:
        bindings = build_source_system_evidence_bindings(_synthetic_candidates())
        cctv = next(item for item in bindings if item["sourceSystemKey"] == "CCTV")
        self.assertEqual(cctv["deviceEvidenceCount"], 52)
        self.assertEqual(cctv["observedSourceValues"], ["CCT"])
        self.assertEqual(cctv["normalizedProposal"], "CCTV")

    def test_pa_count_247(self) -> None:
        bindings = build_source_system_evidence_bindings(_synthetic_candidates())
        pa = next(item for item in bindings if item["sourceSystemKey"] == "PA")
        self.assertEqual(pa["deviceEvidenceCount"], 247)
        self.assertEqual(pa["observedSourceValues"], ["PAS"])

    def test_tel_count_14(self) -> None:
        bindings = build_source_system_evidence_bindings(_synthetic_candidates())
        tel = next(item for item in bindings if item["sourceSystemKey"] == "TEL")
        self.assertEqual(tel["deviceEvidenceCount"], 14)
        self.assertEqual(tel["evidenceType"], "namespace_review")

    def test_binding_required_fields(self) -> None:
        bindings = build_source_system_evidence_bindings(_synthetic_candidates())
        for binding in bindings:
            for field in (
                "registryEntryId",
                "sourceSystemKey",
                "observedSourceValues",
                "normalizedProposal",
                "sourceRecordCount",
                "deviceEvidenceCount",
                "evidenceReferences",
                "provenance",
                "bindingDigest",
                "reviewReasons",
                "lifecycleState",
                "approvalState",
            ):
                self.assertIn(field, binding)

    def test_wrong_candidate_count_rejected(self) -> None:
        with self.assertRaises(SourceSystemRegistryError):
            build_source_system_evidence_bindings(_synthetic_candidates()[:2])


class TestReviewProjection(unittest.TestCase):
    def setUp(self) -> None:
        self.candidates = _synthetic_candidates()
        self.bindings = build_source_system_evidence_bindings(self.candidates)

    def test_exactly_five_review_cards(self) -> None:
        cards = build_review_cards(candidates=self.candidates, bindings=self.bindings)
        self.assertEqual(len(cards), 5)

    def test_two_alias_cards(self) -> None:
        cards = build_review_cards(candidates=self.candidates, bindings=self.bindings)
        alias = [item for item in cards if item["reviewType"] == "ALIAS_APPROVAL"]
        self.assertEqual(len(alias), 2)

    def test_one_namespace_card(self) -> None:
        cards = build_review_cards(candidates=self.candidates, bindings=self.bindings)
        namespace = [item for item in cards if item["reviewType"] == "NAMESPACE_INTERPRETATION"]
        self.assertEqual(len(namespace), 1)
        self.assertEqual(namespace[0]["rootCause"], "SOURCE_NAMESPACE_SCN_SEMANTIC_REVIEW")

    def test_two_registry_approval_cards(self) -> None:
        cards = build_review_cards(candidates=self.candidates, bindings=self.bindings)
        registry = [item for item in cards if item["reviewType"] == "REGISTRY_APPROVAL"]
        self.assertEqual(len(registry), 2)
        keys = {key for item in registry for key in item["affectedSourceSystemKeys"]}
        self.assertEqual(keys, {"ACS", "RAS"})

    def test_cct_not_auto_approved(self) -> None:
        cctv = next(item for item in self.candidates if item["sourceSystemKey"] == "CCTV")
        self.assertFalse(cctv["airportConsumerMetadata"]["autoApproved"])
        cards = build_review_cards(candidates=self.candidates, bindings=self.bindings)
        cctv_card = next(item for item in cards if "CCTV" in item["affectedSourceSystemKeys"] and item["reviewType"] == "ALIAS_APPROVAL")
        self.assertEqual(cctv_card["currentDecision"], "PENDING")

    def test_pas_not_auto_approved(self) -> None:
        pa = next(item for item in self.candidates if item["sourceSystemKey"] == "PA")
        self.assertFalse(pa["airportConsumerMetadata"]["autoApproved"])

    def test_scn_namespace_not_tel_alias(self) -> None:
        tel = next(item for item in self.candidates if item["sourceSystemKey"] == "TEL")
        self.assertTrue(tel["airportConsumerMetadata"]["namespaceReviewRequired"])
        self.assertFalse(tel["airportConsumerMetadata"]["aliasReviewRequired"])
        cards = build_review_cards(candidates=self.candidates, bindings=self.bindings)
        alias_for_tel = [item for item in cards if item["reviewType"] == "ALIAS_APPROVAL" and "TEL" in item["affectedSourceSystemKeys"]]
        self.assertEqual(len(alias_for_tel), 0)

    def test_acs_unapproved(self) -> None:
        acs = next(item for item in self.bindings if item["sourceSystemKey"] == "ACS")
        self.assertNotEqual(acs["approvalState"], RegistryApprovalState.APPROVED.value)

    def test_ras_unapproved(self) -> None:
        ras = next(item for item in self.bindings if item["sourceSystemKey"] == "RAS")
        self.assertNotEqual(ras["approvalState"], RegistryApprovalState.APPROVED.value)

    def test_zero_active_registered_approved(self) -> None:
        cards = build_review_cards(candidates=self.candidates, bindings=self.bindings)
        summary_bindings = self.bindings
        self.assertEqual(sum(1 for item in summary_bindings if item["lifecycleState"] == "ACTIVE"), 0)
        self.assertEqual(sum(1 for item in summary_bindings if item["lifecycleState"] == RegistryLifecycleState.REGISTERED.value), 0)
        self.assertEqual(sum(1 for item in summary_bindings if item["approvalState"] == RegistryApprovalState.APPROVED.value), 0)
        self.assertEqual(sum(1 for item in cards if item["currentDecision"] == "APPROVED"), 0)

    def test_review_card_fields(self) -> None:
        cards = build_review_cards(candidates=self.candidates, bindings=self.bindings)
        for card in cards:
            for field in (
                "reviewCardId",
                "reviewType",
                "title",
                "affectedSourceSystemKeys",
                "affectedRecordCount",
                "evidenceReferences",
                "decisionRequired",
                "allowedDecisions",
                "currentDecision",
                "blockingEffect",
                "rootCause",
                "deterministicDigest",
            ):
                self.assertIn(field, card)

    def test_deterministic_ordering(self) -> None:
        first = build_review_cards(candidates=self.candidates, bindings=self.bindings)
        second = build_review_cards(candidates=self.candidates, bindings=self.bindings)
        self.assertEqual(first, second)

    def test_deterministic_pagination(self) -> None:
        from source_system_registry.digest import sha256_digest

        digest = sha256_digest({"count": 5})
        first = paginate_bindings(self.bindings, page_size=25, projection_state_digest=digest)
        second = paginate_bindings(self.bindings, page_size=25, projection_state_digest=digest)
        self.assertEqual(first["continuationToken"], second["continuationToken"])

    def test_full_projection_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            evidence = base / "evidence"
            evidence.mkdir()
            bindings = _synthetic_bindings()
            (evidence / "airport-device-classification-bindings.json").write_text(json.dumps(bindings), encoding="utf-8")
            (evidence / "airport-alias-approval-package.json").write_text(
                json.dumps(_synthetic_alias_package()), encoding="utf-8"
            )
            projection = run_airport_source_system_review_projection(
                evidence_dir=evidence,
                profile_path=AIRPORT_PROFILE,
            )
            summary = projection["summary"]
            self.assertEqual(summary["sourceSystemEvidenceBindingCount"], 5)
            self.assertEqual(summary["totalBoundDeviceEvidenceCount"], 470)
            self.assertEqual(summary["aliasReviewCardCount"], 2)
            self.assertEqual(summary["namespaceReviewCardCount"], 1)
            self.assertEqual(summary["registryApprovalReviewCardCount"], 2)
            self.assertEqual(summary["pendingDecisionCount"], 5)
            self.assertEqual(projection["readinessOutcome"], "SOURCE_SYSTEM_REVIEW_PROJECTION_COMPLETE_WITH_PENDING_DECISIONS")

    def test_aggregate_no_device_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            evidence = base / "evidence"
            evidence.mkdir()
            (evidence / "airport-device-classification-bindings.json").write_text(json.dumps(_synthetic_bindings()), encoding="utf-8")
            (evidence / "airport-alias-approval-package.json").write_text(json.dumps(_synthetic_alias_package()), encoding="utf-8")
            projection = run_airport_source_system_review_projection(evidence_dir=evidence, profile_path=AIRPORT_PROFILE)
            text = json.dumps({"summary": projection["summary"], "facets": projection["facets"]})
            self.assertNotIn("TE3-", text)
            self.assertNotIn("deviceCode", text)


class TestReviewProjectionArtifact(unittest.TestCase):
    def test_committed_projection_exists(self) -> None:
        self.assertTrue(REVIEW_PROJECTION.is_file())

    def test_committed_summary(self) -> None:
        projection = json.loads(REVIEW_PROJECTION.read_text(encoding="utf-8"))
        summary = projection["summary"]
        self.assertEqual(summary["sourceSystemEvidenceBindingCount"], 5)
        self.assertEqual(summary["totalBoundDeviceEvidenceCount"], 470)
        self.assertEqual(summary["pendingDecisionCount"], 5)
        self.assertEqual(summary["activeSystemCount"], 0)


class TestRealEvidenceReviewProjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.real_available = Path("/tmp/one-airport-a1-03/run-1/airport-device-classification-bindings.json").is_file()

    def test_real_deterministic_runs(self) -> None:
        if not self.real_available:
            self.skipTest("real A1 evidence unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for run in ("run-1", "run-2"):
                evidence = base / run / "evidence"
                evidence.mkdir(parents=True)
                copy("/tmp/one-airport-a1-03/run-1/airport-device-classification-bindings.json", evidence / "airport-device-classification-bindings.json")
                copy("/tmp/one-airport-a1-04/run-1/airport-alias-approval-package.json", evidence / "airport-alias-approval-package.json")
                run_airport_source_system_review_projection(
                    evidence_dir=evidence,
                    profile_path=AIRPORT_PROFILE,
                    output_path=base / run / "projection.json",
                )
            ok, _ = compare_deterministic_outputs(base / "run-1/projection.json", base / "run-2/projection.json")
            self.assertTrue(ok)


class TestBoundaryIsolation(unittest.TestCase):
    def test_no_db_imports(self) -> None:
        forbidden = ("sqlalchemy", "flask", "psycopg", "pymongo")
        for path in AIRPORT_DIR.rglob("*.py"):
            if path.name.startswith("candidate_projection"):
                continue
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text)

    def test_airport_logic_outside_generic_core(self) -> None:
        generic_text = " ".join(path.read_text(encoding="utf-8") for path in GENERIC_DIR.rglob("*.py"))
        self.assertNotIn("ALIAS_APPROVAL", generic_text)
        self.assertNotIn("SCN", generic_text)


if __name__ == "__main__":
    unittest.main()
