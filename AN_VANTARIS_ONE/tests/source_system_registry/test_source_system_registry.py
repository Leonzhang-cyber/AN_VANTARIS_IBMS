"""Tests for generic source-system registry foundation."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from source_system_registry.digest import sha256_digest
from source_system_registry.enums import (
    DeclarationState,
    RegistryApprovalState,
    RegistryLifecycleState,
    VerificationState,
)
from source_system_registry.errors import SourceSystemRegistryError
from source_system_registry.models import (
    build_capability_declaration,
    build_evidence_reference,
    build_integration_declaration,
)
from source_system_registry.registry import build_registry_candidate
from source_system_registry.validation import validate_registry_entry, validate_source_system_key

REGISTRY = ROOT / "registries/source-system-registry.v1.json"
AIRPORT_PROFILE = ROOT / "industry_profiles/airport/source-system-profile.v1.json"
AIRPORT_PROJECTION = ROOT / "industry_profiles/airport/projections/airport-source-system-candidates.v1.json"
GENERIC_DIR = ROOT / "source_system_registry"
AIRPORT_DIR = ROOT / "industry_profiles/airport"
REAL_EVIDENCE = Path("/tmp/one-airport-a2-01/evidence")


def _evidence_ref(count: int = 1) -> dict:
    return build_evidence_reference(
        evidence_type="TEST_EVIDENCE",
        evidence_id=sha256_digest({"count": count}),
        source_profile="test-profile",
        source_record_count=count,
        provenance="synthetic-test",
    )


def _valid_candidate(**overrides: object) -> dict:
    payload = {
        "source_system_key": "HVAC",
        "display_name": "HVAC",
        "system_category": "BUILDING_AUTOMATION",
        "created_from_profile": "test-profile-v1",
        "mapping_version": "test-v1",
        "schema_version": "1.0.0",
        "evidence_references": [_evidence_ref()],
    }
    payload.update(overrides)
    return build_registry_candidate(**payload)


def _synthetic_bindings() -> list[dict]:
    categories = [
        ("ACCESS_CONTROL", 129, "ACS", ""),
        ("RADIO_COMMUNICATION", 28, "RAS", ""),
        ("VIDEO_SURVEILLANCE", 52, "CCTV", "CCT"),
        ("PUBLIC_ADDRESS", 247, "PA", "PAS"),
        ("TELECOMMUNICATION", 14, "TEL", ""),
    ]
    bindings: list[dict] = []
    row = 1
    for category, count, system_value, embedded in categories:
        for _ in range(count):
            binding = {
                "genericSystemCategory": category,
                "sourceSystemValue": system_value,
                "embeddedSystemCode": embedded,
                "sourceNamespaceCode": "SCN" if category == "TELECOMMUNICATION" else "",
                "systemMappingStatus": "REVIEW_REQUIRED" if category == "TELECOMMUNICATION" else "EXACT_MATCH",
            }
            if embedded in {"CCT", "PAS"}:
                binding["systemMappingStatus"] = "ALIAS_CANDIDATE"
            bindings.append(binding)
            row += 1
    return bindings


def _synthetic_alias_package() -> list[dict]:
    return [
        {
            "proposalType": "SYSTEM_ALIAS",
            "targetValue": "CCTV",
            "decisionStatus": "APPROVAL_REQUIRED",
            "proposalId": sha256_digest({"alias": "CCT", "target": "CCTV"}),
            "affectedRecordCount": 52,
        },
        {
            "proposalType": "SYSTEM_ALIAS",
            "targetValue": "PA",
            "decisionStatus": "APPROVAL_REQUIRED",
            "proposalId": sha256_digest({"alias": "PAS", "target": "PA"}),
            "affectedRecordCount": 247,
        },
        {
            "proposalType": "SOURCE_NAMESPACE",
            "targetValue": "SOURCE_NAMESPACE_SEMANTIC_REVIEW",
            "decisionStatus": "APPROVAL_REQUIRED",
            "proposalId": sha256_digest({"namespace": "SCN"}),
            "affectedRecordCount": 14,
        },
    ]


class TestGenericRegistryFoundation(unittest.TestCase):
    def test_registry_spec_exists(self) -> None:
        self.assertTrue(REGISTRY.is_file())

    def test_registry_cross_industry(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertTrue(registry["crossIndustry"])
        self.assertFalse(registry["airportSpecific"])
        self.assertFalse(registry["databaseAccessEnabled"])

    def test_valid_cross_industry_candidate(self) -> None:
        candidate = _valid_candidate()
        self.assertEqual(candidate["lifecycleState"], RegistryLifecycleState.CANDIDATE.value)
        self.assertEqual(candidate["approvalState"], RegistryApprovalState.DRAFT.value)

    def test_rejects_missing_source_system_key(self) -> None:
        with self.assertRaises(SourceSystemRegistryError):
            validate_source_system_key("")

    def test_rejects_customer_derived_key(self) -> None:
        with self.assertRaises(SourceSystemRegistryError):
            validate_source_system_key("TE3-CCT")

    def test_rejects_unstable_key(self) -> None:
        with self.assertRaises(SourceSystemRegistryError):
            validate_source_system_key("bad key!")

    def test_approved_without_explicit_input_rejected(self) -> None:
        with self.assertRaises(SourceSystemRegistryError):
            build_registry_candidate(
                source_system_key="EMS",
                display_name="EMS",
                system_category="ENERGY_MANAGEMENT",
                created_from_profile="test-profile-v1",
                mapping_version="test-v1",
                schema_version="1.0.0",
                evidence_references=[_evidence_ref()],
                approval_state=RegistryApprovalState.APPROVED,
            )

    def test_verified_capability_requires_evidence(self) -> None:
        entry = _valid_candidate()
        entry["verifiedCapabilities"] = [
            build_capability_declaration(
                capability_key="HEALTH_SIGNAL",
                verification_state=VerificationState.VERIFIED,
                evidence_references=[],
            )
        ]
        with self.assertRaises(SourceSystemRegistryError):
            validate_registry_entry(entry)

    def test_connector_reference_declarative(self) -> None:
        candidate = _valid_candidate(
            integration_declarations=[
                build_integration_declaration(
                    connector_reference="connector://declared-only",
                    edge_gateway_reference="edge://declared-only",
                    link_route_reference="link://declared-only",
                    declaration_state=DeclarationState.DECLARED,
                )
            ]
        )
        decl = candidate["integrationDeclarations"][0]
        self.assertEqual(decl["connectorReference"], "connector://declared-only")
        self.assertEqual(decl["edgeGatewayReference"], "edge://declared-only")
        self.assertEqual(decl["linkRouteReference"], "link://declared-only")

    def test_no_db_imports(self) -> None:
        forbidden = ("sqlalchemy", "flask", "psycopg", "pymongo")
        for path in GENERIC_DIR.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text)

    def test_no_runtime_execution_helpers(self) -> None:
        text = " ".join(path.read_text(encoding="utf-8") for path in GENERIC_DIR.rglob("*.py"))
        for token in ("execute_connector", "connect(", "heartbeat", "retry(", "dlq"):
            self.assertNotIn(token, text)

    def test_registry_spec_no_airport_canonical_fields(self) -> None:
        text = REGISTRY.read_text(encoding="utf-8")
        for token in ("Terminal", "DA21", "DA31", "TE3", "Z1", "Z2"):
            self.assertNotIn(token, text)


class TestAirportConsumerProfile(unittest.TestCase):
    def setUp(self) -> None:
        from industry_profiles.airport.candidate_projection import build_airport_source_system_candidates

        self.build_candidates = build_airport_source_system_candidates
        self.profile = json.loads(AIRPORT_PROFILE.read_text(encoding="utf-8"))

    def test_exactly_five_candidates(self) -> None:
        candidates = self.build_candidates(
            bindings=_synthetic_bindings(),
            alias_package=_synthetic_alias_package(),
            airport_profile=self.profile,
        )
        self.assertEqual(len(candidates), 5)

    def test_evidence_counts_total_470(self) -> None:
        candidates = self.build_candidates(
            bindings=_synthetic_bindings(),
            alias_package=_synthetic_alias_package(),
            airport_profile=self.profile,
        )
        total = sum(item["airportConsumerMetadata"]["sourceRecordCount"] for item in candidates)
        self.assertEqual(total, 470)

    def test_acs_count_129(self) -> None:
        candidates = self.build_candidates(
            bindings=_synthetic_bindings(),
            alias_package=_synthetic_alias_package(),
            airport_profile=self.profile,
        )
        acs = next(item for item in candidates if item["sourceSystemKey"] == "ACS")
        self.assertEqual(acs["airportConsumerMetadata"]["sourceRecordCount"], 129)

    def test_ras_count_28(self) -> None:
        candidates = self.build_candidates(
            bindings=_synthetic_bindings(),
            alias_package=_synthetic_alias_package(),
            airport_profile=self.profile,
        )
        ras = next(item for item in candidates if item["sourceSystemKey"] == "RAS")
        self.assertEqual(ras["airportConsumerMetadata"]["sourceRecordCount"], 28)

    def test_cct_proposes_cctv(self) -> None:
        candidates = self.build_candidates(
            bindings=_synthetic_bindings(),
            alias_package=_synthetic_alias_package(),
            airport_profile=self.profile,
        )
        cctv = next(item for item in candidates if item["sourceSystemKey"] == "CCTV")
        meta = cctv["airportConsumerMetadata"]
        self.assertEqual(meta["observedSourceValue"], "CCT")
        self.assertEqual(meta["proposedNormalizedValue"], "CCTV")

    def test_pas_proposes_pa(self) -> None:
        candidates = self.build_candidates(
            bindings=_synthetic_bindings(),
            alias_package=_synthetic_alias_package(),
            airport_profile=self.profile,
        )
        pa = next(item for item in candidates if item["sourceSystemKey"] == "PA")
        meta = pa["airportConsumerMetadata"]
        self.assertEqual(meta["observedSourceValue"], "PAS")
        self.assertEqual(meta["proposedNormalizedValue"], "PA")

    def test_cct_alias_not_auto_approved(self) -> None:
        candidates = self.build_candidates(
            bindings=_synthetic_bindings(),
            alias_package=_synthetic_alias_package(),
            airport_profile=self.profile,
        )
        cctv = next(item for item in candidates if item["sourceSystemKey"] == "CCTV")
        self.assertFalse(cctv["airportConsumerMetadata"]["autoApproved"])
        self.assertEqual(cctv["airportConsumerMetadata"]["aliasDecisionStatus"], "APPROVAL_REQUIRED")

    def test_pas_alias_not_auto_approved(self) -> None:
        candidates = self.build_candidates(
            bindings=_synthetic_bindings(),
            alias_package=_synthetic_alias_package(),
            airport_profile=self.profile,
        )
        pa = next(item for item in candidates if item["sourceSystemKey"] == "PA")
        self.assertFalse(pa["airportConsumerMetadata"]["autoApproved"])

    def test_scn_is_namespace_not_alias(self) -> None:
        candidates = self.build_candidates(
            bindings=_synthetic_bindings(),
            alias_package=_synthetic_alias_package(),
            airport_profile=self.profile,
        )
        tel = next(item for item in candidates if item["sourceSystemKey"] == "TEL")
        meta = tel["airportConsumerMetadata"]
        self.assertTrue(meta["namespaceReviewRequired"])
        self.assertFalse(meta["aliasReviewRequired"])
        self.assertEqual(meta["sourceNamespaceCode"], "SCN")

    def test_tel_review_required(self) -> None:
        candidates = self.build_candidates(
            bindings=_synthetic_bindings(),
            alias_package=_synthetic_alias_package(),
            airport_profile=self.profile,
        )
        tel = next(item for item in candidates if item["sourceSystemKey"] == "TEL")
        self.assertEqual(tel["approvalState"], RegistryApprovalState.REVIEW_REQUIRED.value)

    def test_zero_active_systems(self) -> None:
        candidates = self.build_candidates(
            bindings=_synthetic_bindings(),
            alias_package=_synthetic_alias_package(),
            airport_profile=self.profile,
        )
        self.assertEqual(sum(1 for item in candidates if item.get("lifecycleState") == "ACTIVE"), 0)

    def test_deterministic_ordering(self) -> None:
        first = self.build_candidates(
            bindings=_synthetic_bindings(),
            alias_package=_synthetic_alias_package(),
            airport_profile=self.profile,
        )
        second = self.build_candidates(
            bindings=_synthetic_bindings(),
            alias_package=_synthetic_alias_package(),
            airport_profile=self.profile,
        )
        self.assertEqual([item["sourceSystemKey"] for item in first], [item["sourceSystemKey"] for item in second])
        self.assertEqual(first, second)

    def test_deterministic_identifiers(self) -> None:
        candidates = self.build_candidates(
            bindings=_synthetic_bindings(),
            alias_package=_synthetic_alias_package(),
            airport_profile=self.profile,
        )
        ids = [item["registryEntryId"] for item in candidates]
        self.assertEqual(len(set(ids)), 5)

    def test_aggregate_no_device_ids(self) -> None:
        from industry_profiles.airport.candidate_projection import build_airport_projection_summary

        candidates = self.build_candidates(
            bindings=_synthetic_bindings(),
            alias_package=_synthetic_alias_package(),
            airport_profile=self.profile,
        )
        summary = build_airport_projection_summary(candidates)
        text = json.dumps(summary)
        self.assertNotIn("TE3-", text)
        self.assertNotIn("deviceCode", text)

    def test_malformed_evidence_fail_closed(self) -> None:
        with self.assertRaises(SourceSystemRegistryError):
            self.build_candidates(bindings=[], alias_package=_synthetic_alias_package(), airport_profile=self.profile)

    def test_alias_rules_only_in_airport_profile(self) -> None:
        profile_text = AIRPORT_PROFILE.read_text(encoding="utf-8")
        generic_text = " ".join(path.read_text(encoding="utf-8") for path in GENERIC_DIR.rglob("*.py"))
        self.assertIn("CCT", profile_text)
        self.assertNotIn('"CCT"', generic_text)


class TestAirportProjectionArtifact(unittest.TestCase):
    def test_projection_artifact_exists(self) -> None:
        self.assertTrue(AIRPORT_PROJECTION.is_file())

    def test_projection_summary(self) -> None:
        projection = json.loads(AIRPORT_PROJECTION.read_text(encoding="utf-8"))
        summary = projection["summary"]
        self.assertEqual(summary["sourceSystemCandidateCount"], 5)
        self.assertEqual(summary["activeSystemCount"], 0)
        self.assertEqual(summary["registeredSystemCount"], 0)
        self.assertEqual(summary["approvedSystemCount"], 0)
        self.assertEqual(summary["exactEvidenceCandidateCount"], 2)
        self.assertEqual(summary["aliasReviewCandidateCount"], 2)
        self.assertEqual(summary["namespaceReviewCandidateCount"], 1)
        self.assertEqual(summary["totalEvidenceDeviceCount"], 470)

    def test_readiness_outcome(self) -> None:
        projection = json.loads(AIRPORT_PROJECTION.read_text(encoding="utf-8"))
        self.assertEqual(projection["readinessOutcome"], "SOURCE_SYSTEM_CANDIDATES_COMPLETE_WITH_PENDING_REVIEWS")
        self.assertEqual(projection["implementationStatus"], "GENERIC_SOURCE_SYSTEM_REGISTRY_FOUNDATION_COMPLETE")

    def test_projection_no_customer_identifiers(self) -> None:
        text = AIRPORT_PROJECTION.read_text(encoding="utf-8")
        self.assertNotIn("TE3-CCT", text)
        self.assertNotIn("FIRE EXIT", text)


class TestRealEvidenceProjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.real_available = (
            Path("/tmp/one-airport-a1-03/run-1/airport-device-classification-bindings.json").is_file()
            and Path("/tmp/one-airport-a1-04/run-1/airport-alias-approval-package.json").is_file()
        )

    def test_real_evidence_deterministic_runs(self) -> None:
        if not self.real_available:
            self.skipTest("real A1 evidence unavailable")
        from industry_profiles.airport.candidate_projection import compare_deterministic_outputs, run_airport_source_system_projection
        from shutil import copy

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for run in ("run-1", "run-2"):
                evidence = base / run
                evidence.mkdir(parents=True)
                copy("/tmp/one-airport-a1-03/run-1/airport-device-classification-bindings.json", evidence / "airport-device-classification-bindings.json")
                copy("/tmp/one-airport-a1-04/run-1/airport-alias-approval-package.json", evidence / "airport-alias-approval-package.json")
                run_airport_source_system_projection(
                    evidence_dir=evidence,
                    profile_path=AIRPORT_PROFILE,
                    output_path=base / run / "projection.json",
                )
            ok, _ = compare_deterministic_outputs(base / "run-1/projection.json", base / "run-2/projection.json")
            self.assertTrue(ok)


class TestBoundaryIsolation(unittest.TestCase):
    def _combined_text(self) -> str:
        parts: list[str] = []
        for base in (GENERIC_DIR, AIRPORT_DIR):
            parts.extend(path.read_text(encoding="utf-8") for path in base.rglob("*.py"))
        return " ".join(parts)

    def test_no_edge_imports(self) -> None:
        self.assertNotIn("AN_VANTARIS_EDGE", self._combined_text())

    def test_no_link_imports(self) -> None:
        self.assertNotIn("AN_VANTARIS_LINK", self._combined_text())

    def test_airport_profile_separate_path(self) -> None:
        self.assertTrue(AIRPORT_PROFILE.is_file())
        self.assertTrue(GENERIC_DIR.is_dir())


if __name__ == "__main__":
    unittest.main()
