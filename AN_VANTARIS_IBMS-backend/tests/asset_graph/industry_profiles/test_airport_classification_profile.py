"""Tests for airport system and device classification profile."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BACKEND = ROOT / "AN_VANTARIS_IBMS-backend"
sys.path.insert(0, str(BACKEND))

from src.asset_graph.industry_profiles.airport_classification import (
    AirportClassificationProfileError,
    compare_deterministic_outputs,
    run_airport_classification,
)
from src.asset_graph.industry_profiles.airport_classification.compatibility import evaluate_compatibility
from src.asset_graph.industry_profiles.airport_classification.constants import (
    AUTHORITY,
    DEVICE_TYPE_DEFINITIONS,
    EMBEDDED_SYSTEM_ALIAS_CANDIDATES,
    IMPLEMENTATION_MODE,
    INDUSTRY_TO_GENERIC,
    KNOWN_SOURCE_NAMESPACES,
    PROFILE_ID,
    PROFILE_NAME,
)
from src.asset_graph.industry_profiles.airport_classification.context import AirportClassificationContext
from src.asset_graph.industry_profiles.airport_classification.device_id_segments import parse_device_id_segments
from src.asset_graph.industry_profiles.airport_classification.device_type_classifier import classify_device_type
from src.asset_graph.industry_profiles.airport_classification.duplicates import compare_duplicate_classifications
from src.asset_graph.industry_profiles.airport_classification.system_classifier import classify_system
from src.asset_graph.constants import RelationshipType

FIXTURES = Path(__file__).resolve().parent / "fixtures.py"
_spec = importlib.util.spec_from_file_location("classification_fixtures", FIXTURES)
_fx = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_fx)

REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/airport-classification-profile.v1.json"
MODELS = BACKEND / "src/asset_graph/models.py"

DEVICE_TYPE_CASES = [
    ("FCT", "Fixed Camera", "CAMERA"),
    ("PCT", "PTZ Camera", "CAMERA"),
    ("TEL", "IP Telephone", "TELEPHONE"),
    ("ANT", "Radio Antenna", "ANTENNA"),
    ("10DC", "Directional Coupler", "COUPLER"),
    ("6DC", "Directional Coupler", "COUPLER"),
    ("2LS", "Two-Way Splitter", "SPLITTER"),
    ("3LS", "Three-Way Splitter", "SPLITTER"),
    ("ADCP", "Intelligent Controller", "CONTROLLER"),
    ("DC1", "Electromagnetic Lock", "LOCK"),
    ("DC2", "Electromagnetic Lock", "LOCK"),
    ("BG", "Emergency Break Glass", "BREAK_GLASS"),
    ("PB", "Push Button", "PUSH_BUTTON"),
    ("INCR", "In Card Reader", "CARD_READER"),
    ("OTCR", "Out Card Reader", "CARD_READER"),
    ("HSP", "Horn Speaker", "SPEAKER"),
    ("PSP", "Projection Speaker", "SPEAKER"),
    ("CSP", "Ceiling Speaker", "SPEAKER"),
    ("BSP", "Box Speaker", "SPEAKER"),
    ("ONI", "Omneo Interface", "INTERFACE"),
    ("NCO", "Network Controller", "NETWORK_CONTROLLER"),
    ("AMP", "Amplifier", "AMPLIFIER"),
    ("NOS", "Noise Sensor", "SENSOR"),
    ("STAMP", "Standby Amplifier", "AMPLIFIER"),
    ("LTV", "IPTV Endpoint", "ENDPOINT"),
    ("OUT", "Outlet", "OUTLET"),
]


def _run_classification(base: Path, devices: list[dict]) -> dict:
    base.mkdir(parents=True, exist_ok=True)
    intake = _fx.build_intake_evidence(devices=devices)
    intake_path = base / "intake.json"
    intake_path.write_text(json.dumps(intake, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    spatial = _fx.build_spatial_result(intake_digest=intake["resultDigest"])
    spatial_path = base / "spatial.json"
    spatial_path.write_text(json.dumps(spatial, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    bindings = _fx.build_spatial_bindings(devices)
    bindings_path = base / "bindings.json"
    bindings_path.write_text(json.dumps(bindings, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_dir = base / "out"
    context = AirportClassificationContext(**_fx.classification_context_kwargs(intake["resultDigest"]))
    return run_airport_classification(
        intake_evidence_path=intake_path,
        spatial_result_path=spatial_path,
        spatial_bindings_path=bindings_path,
        output_dir=output_dir,
        context=context,
        run_id="test-run",
    )


class TestAirportClassificationProfile(unittest.TestCase):
    def test_registry_exists(self) -> None:
        self.assertTrue(REGISTRY.is_file())

    def test_registry_industry_profile(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(registry["profileType"], "INDUSTRY_PROFILE")

    def test_registry_platform_not_airportized(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertFalse(registry["platformCoreAirportized"])

    def test_registry_authority(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(registry["authority"], AUTHORITY)

    def test_registry_implementation_mode(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(registry["implementationMode"], IMPLEMENTATION_MODE)

    def test_generic_node_types_exclude_airport_codes(self) -> None:
        values = {item.value for item in RelationshipType}
        for code in ("CCT", "PAS", "SCN", "TE3", "HSP", "ADCP"):
            self.assertNotIn(code, values)

    def test_industry_labels_not_in_generic_enums(self) -> None:
        values = {item.value for item in RelationshipType}
        for label in INDUSTRY_TO_GENERIC:
            self.assertNotIn(label, values)

    def test_generic_asset_graph_models_unchanged(self) -> None:
        text = MODELS.read_text(encoding="utf-8")
        self.assertNotIn("SCN", text)
        self.assertNotIn("CCT", text)

    def test_intake_digest_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            intake = _fx.build_intake_evidence()
            intake_path = base / "intake.json"
            intake_path.write_text(json.dumps(intake, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            spatial_path = base / "spatial.json"
            spatial_path.write_text(
                json.dumps(_fx.build_spatial_result(intake_digest=intake["resultDigest"]), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            bindings_path = base / "bindings.json"
            bindings_path.write_text("[]\n", encoding="utf-8")
            context = AirportClassificationContext(
                tenant_id="T",
                site_id="S",
                source_workbook_digest=_fx.WORKBOOK_DIGEST,
                expected_intake_result_digest="wrong-digest",
            )
            with self.assertRaises(AirportClassificationProfileError):
                run_airport_classification(
                    intake_evidence_path=intake_path,
                    spatial_result_path=spatial_path,
                    spatial_bindings_path=bindings_path,
                    output_dir=base / "out",
                    context=context,
                    run_id="run",
                )

    def test_spatial_digest_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            intake = _fx.build_intake_evidence()
            intake_path = base / "intake.json"
            intake_path.write_text(json.dumps(intake, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            spatial = _fx.build_spatial_result(intake_digest=intake["resultDigest"])
            spatial_path = base / "spatial.json"
            spatial_path.write_text(json.dumps(spatial, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            bindings_path = base / "bindings.json"
            bindings_path.write_text("[]\n", encoding="utf-8")
            context = AirportClassificationContext(
                tenant_id="T",
                site_id="S",
                source_workbook_digest=_fx.WORKBOOK_DIGEST,
                expected_intake_result_digest=intake["resultDigest"],
                expected_spatial_result_digest="wrong-digest",
            )
            with self.assertRaises(AirportClassificationProfileError):
                run_airport_classification(
                    intake_evidence_path=intake_path,
                    spatial_result_path=spatial_path,
                    spatial_bindings_path=bindings_path,
                    output_dir=base / "out",
                    context=context,
                    run_id="run",
                )

    def _classify(self, source_id: str, system: str) -> dict:
        segment = parse_device_id_segments(source_id)
        return classify_system(
            source_system_value=system,
            segment_parse=segment,
            source_evidence_digest="digest",
        )

    def test_cct_cctv_alias_candidate(self) -> None:
        result = self._classify("TE3-CCT-BAS-DA21-FCT-001", "CCTV")
        self.assertEqual(result["mappingStatus"], "ALIAS_CANDIDATE")
        self.assertEqual(result["genericSystemCategory"], "VIDEO_SURVEILLANCE")

    def test_pas_pa_alias_candidate(self) -> None:
        result = self._classify("TE3-PAS-BAS-DA21-HSP-001", "PA")
        self.assertEqual(result["mappingStatus"], "ALIAS_CANDIDATE")
        self.assertEqual(result["genericSystemCategory"], "PUBLIC_ADDRESS")

    def test_acs_exact_match(self) -> None:
        result = self._classify("TE3-ACS-BAS-DA21-ADCP-001", "ACS")
        self.assertEqual(result["mappingStatus"], "EXACT_MATCH")
        self.assertEqual(result["genericSystemCategory"], "ACCESS_CONTROL")

    def test_ras_exact_match(self) -> None:
        result = self._classify("TE3-RAS-BAS-DA21-ANT-001", "RAS")
        self.assertEqual(result["mappingStatus"], "EXACT_MATCH")
        self.assertEqual(result["genericSystemCategory"], "RADIO_COMMUNICATION")

    def test_tel_exact_match_without_scn(self) -> None:
        result = self._classify("TE3-TEL-BAS-DA21-TEL-001", "TEL")
        self.assertEqual(result["mappingStatus"], "EXACT_MATCH")
        self.assertEqual(result["genericSystemCategory"], "TELECOMMUNICATION")

    def test_scn_semantic_review_required(self) -> None:
        result = self._classify("TE3-SCN-BAS-DA31-TEL-001", "TEL")
        self.assertEqual(result["mappingStatus"], "REVIEW_REQUIRED")
        self.assertIn("SCN_SEMANTIC_REVIEW_REQUIRED", result["reviewReasons"])
        self.assertEqual(result["sourceNamespace"], "SCN")

    def test_scn_not_auto_mapped_to_tel_system(self) -> None:
        result = self._classify("TE3-SCN-BAS-DA31-TEL-001", "TEL")
        self.assertNotIn("SCN", result["embeddedSystemCode"])
        self.assertEqual(result["industrySystemLabel"], "TEL")

    def test_scn_is_namespace_not_system(self) -> None:
        segment = parse_device_id_segments("TE3-SCN-BAS-DA31-TEL-001")
        self.assertEqual(segment.source_namespace_code, "SCN")
        self.assertEqual(segment.device_type_code, "TEL")
        self.assertIn("SCN", KNOWN_SOURCE_NAMESPACES)

    def test_standard_six_segment_parse(self) -> None:
        segment = parse_device_id_segments("TE3-CCT-BAS-DA21-FCT-001")
        self.assertEqual(segment.parse_status, "FULLY_PARSED")
        self.assertEqual(segment.building_code, "TE3")
        self.assertEqual(segment.device_type_code, "FCT")

    def test_non_standard_three_segment(self) -> None:
        segment = parse_device_id_segments("BAS-EML/DC1-001")
        self.assertEqual(segment.parse_status, "NON_STANDARD_PATTERN")
        self.assertEqual(segment.device_type_code, "EML/DC1")

    def test_segment_fields_present(self) -> None:
        segment = parse_device_id_segments("TE3-PAS-BAS-DA21-HSP-001")
        self.assertEqual(segment.level_code, "BAS")
        self.assertEqual(segment.distribution_area_code, "DA21")
        self.assertEqual(segment.sequence_code, "001")

    def test_known_device_type_mappings(self) -> None:
        for code, label, generic_class in DEVICE_TYPE_CASES:
            with self.subTest(code=code):
                result = classify_device_type(
                    device_type_code=code,
                    source_device_type_label=label,
                    source_evidence_digest="digest",
                )
                self.assertEqual(result["deviceTypeMappingStatus"], "EXACT_TYPE_MATCH")
                self.assertEqual(result["genericDeviceClass"], generic_class)

    def test_unknown_device_type_code(self) -> None:
        result = classify_device_type(
            device_type_code="ZZZ",
            source_device_type_label="Unknown Widget",
            source_evidence_digest="digest",
        )
        self.assertEqual(result["deviceTypeMappingStatus"], "UNKNOWN_DEVICE_TYPE_CODE")

    def test_device_type_column_conflict(self) -> None:
        result = classify_device_type(
            device_type_code="FCT",
            source_device_type_label="Wrong Label",
            source_evidence_digest="digest",
        )
        self.assertEqual(result["deviceTypeMappingStatus"], "DEVICE_TYPE_COLUMN_CONFLICT")

    def test_fct_compatible_with_video_surveillance(self) -> None:
        status, _ = evaluate_compatibility(
            generic_system_category="VIDEO_SURVEILLANCE",
            device_type_code="FCT",
            system_mapping_status="ALIAS_CANDIDATE",
            device_type_mapping_status="EXACT_TYPE_MATCH",
        )
        self.assertEqual(status, "SYSTEM_DEVICE_COMPATIBLE")

    def test_adcp_compatible_with_access_control(self) -> None:
        status, _ = evaluate_compatibility(
            generic_system_category="ACCESS_CONTROL",
            device_type_code="ADCP",
            system_mapping_status="EXACT_MATCH",
            device_type_mapping_status="EXACT_TYPE_MATCH",
        )
        self.assertEqual(status, "SYSTEM_DEVICE_COMPATIBLE")

    def test_hsp_compatible_with_public_address(self) -> None:
        status, _ = evaluate_compatibility(
            generic_system_category="PUBLIC_ADDRESS",
            device_type_code="HSP",
            system_mapping_status="ALIAS_CANDIDATE",
            device_type_mapping_status="EXACT_TYPE_MATCH",
        )
        self.assertEqual(status, "SYSTEM_DEVICE_COMPATIBLE")

    def test_tel_compatible_with_telecommunication(self) -> None:
        status, _ = evaluate_compatibility(
            generic_system_category="TELECOMMUNICATION",
            device_type_code="TEL",
            system_mapping_status="EXACT_MATCH",
            device_type_mapping_status="EXACT_TYPE_MATCH",
        )
        self.assertEqual(status, "SYSTEM_DEVICE_COMPATIBLE")

    def test_ant_compatible_with_radio(self) -> None:
        status, _ = evaluate_compatibility(
            generic_system_category="RADIO_COMMUNICATION",
            device_type_code="ANT",
            system_mapping_status="EXACT_MATCH",
            device_type_mapping_status="EXACT_TYPE_MATCH",
        )
        self.assertEqual(status, "SYSTEM_DEVICE_COMPATIBLE")

    def test_unknown_type_produces_review(self) -> None:
        status, reasons = evaluate_compatibility(
            generic_system_category="VIDEO_SURVEILLANCE",
            device_type_code="ZZZ",
            system_mapping_status="EXACT_MATCH",
            device_type_mapping_status="UNKNOWN_DEVICE_TYPE_CODE",
        )
        self.assertEqual(status, "COMPATIBILITY_REVIEW_REQUIRED")
        self.assertIn("UNKNOWN_DEVICE_TYPE", reasons)

    def test_duplicate_agreement(self) -> None:
        rows = [
            {
                "sourceId": "DUP-001",
                "systemMappingStatus": "ALIAS_CANDIDATE",
                "genericSystemCategory": "PUBLIC_ADDRESS",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericDeviceClass": "SPEAKER",
                "compatibilityStatus": "SYSTEM_DEVICE_COMPATIBLE",
                "deviceCandidateDigest": "a",
            },
            {
                "sourceId": "DUP-001",
                "systemMappingStatus": "ALIAS_CANDIDATE",
                "genericSystemCategory": "PUBLIC_ADDRESS",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericDeviceClass": "SPEAKER",
                "compatibilityStatus": "SYSTEM_DEVICE_COMPATIBLE",
                "deviceCandidateDigest": "b",
            },
        ]
        findings = compare_duplicate_classifications(rows)
        self.assertEqual(findings[0]["classification"], "DUPLICATE_CLASSIFICATION_AGREEMENT")

    def test_duplicate_system_conflict(self) -> None:
        rows = [
            {
                "sourceId": "DUP-002",
                "systemMappingStatus": "EXACT_MATCH",
                "genericSystemCategory": "ACCESS_CONTROL",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericDeviceClass": "LOCK",
                "compatibilityStatus": "SYSTEM_DEVICE_COMPATIBLE",
                "deviceCandidateDigest": "a",
            },
            {
                "sourceId": "DUP-002",
                "systemMappingStatus": "ALIAS_CANDIDATE",
                "genericSystemCategory": "PUBLIC_ADDRESS",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericDeviceClass": "LOCK",
                "compatibilityStatus": "SYSTEM_DEVICE_UNEXPECTED",
                "deviceCandidateDigest": "b",
            },
        ]
        findings = compare_duplicate_classifications(rows)
        self.assertEqual(findings[0]["classification"], "DUPLICATE_SYSTEM_CONFLICT")

    def test_exact_match_uses_platform_authority(self) -> None:
        result = classify_system(
            source_system_value="ACS",
            segment_parse=parse_device_id_segments("TE3-ACS-BAS-DA21-ADCP-001"),
            source_evidence_digest="digest",
        )
        self.assertEqual(result["mappingAuthority"], "PLATFORM_GENERIC_CATEGORY")

    def test_alias_candidate_uses_evidence_only(self) -> None:
        result = classify_system(
            source_system_value="CCTV",
            segment_parse=parse_device_id_segments("TE3-CCT-BAS-DA21-FCT-001"),
            source_evidence_digest="digest",
        )
        self.assertEqual(result["mappingAuthority"], "EVIDENCE_ONLY")

    def test_summary_excludes_customer_identifiers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_classification(base, devices)
            summary = json.loads((base / "out" / "airport-classification-summary.json").read_text(encoding="utf-8"))
            self.assertFalse(summary["containsCustomerAssetIdentifiers"])
            self.assertNotIn("TE3-CCT-BAS-DA21-FCT-001", json.dumps(summary))

    def test_bindings_aggregate_exclude_raw_source_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_classification(base, devices)
            bindings = json.loads((base / "out" / "airport-device-classification-bindings.json").read_text(encoding="utf-8"))
            self.assertTrue(bindings)
            self.assertNotIn("sourceId", bindings[0])

    def test_identical_runs_produce_identical_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [
                _fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV"),
                _fx._device_with_type("TE3-PAS-BAS-DA21-HSP-002", row=3, system="PA", device_type="Horn Speaker"),
            ]
            _run_classification(base / "run1", devices)
            _run_classification(base / "run2", devices)
            first = base / "run1" / "out" / "airport-classification-summary.json"
            second = base / "run2" / "out" / "airport-classification-summary.json"
            matched, status = compare_deterministic_outputs(first, second)
            self.assertTrue(matched, status)

    def test_readiness_with_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [
                _fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV"),
                _fx._device_with_type("TE3-SCN-BAS-DA31-TEL-001", row=3, da="DA31", system="TEL", device_type="IP Telephone"),
            ]
            result = _run_classification(base, devices)
            self.assertEqual(result["readinessOutcome"], "CLASSIFICATION_COMPLETE_WITH_REVIEWS")

    def test_outputs_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-ACS-BAS-DA21-ADCP-001", system="ACS", device_type="Intelligent Controller")]
            _run_classification(base, devices)
            out = base / "out"
            for name in (
                "airport-system-classification-result.json",
                "airport-device-type-classification-result.json",
                "airport-device-classification-bindings.json",
                "airport-classification-review-findings.json",
                "airport-classification-summary.json",
                "artifact-manifest.json",
            ):
                self.assertTrue((out / name).is_file())

    def test_profile_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-RAS-BAS-DA21-ANT-001", system="RAS", device_type="Radio Antenna")]
            _run_classification(base, devices)
            system_doc = json.loads((base / "out" / "airport-system-classification-result.json").read_text(encoding="utf-8"))
            self.assertEqual(system_doc["profileName"], PROFILE_NAME)
            self.assertEqual(system_doc["profileId"], PROFILE_ID)
            self.assertFalse(system_doc["platformCoreAirportized"])

    def test_embedded_alias_constants_not_in_generic_models(self) -> None:
        text = MODELS.read_text(encoding="utf-8")
        for alias in EMBEDDED_SYSTEM_ALIAS_CANDIDATES:
            self.assertNotIn(alias, text)

    def test_device_type_registry_bounded(self) -> None:
        self.assertIn("FCT", DEVICE_TYPE_DEFINITIONS)
        self.assertGreaterEqual(len(DEVICE_TYPE_DEFINITIONS), 20)

    def test_raw_source_preserved_in_binding_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_classification(base, devices)
            bindings = json.loads((base / "out" / "airport-device-classification-bindings.json").read_text(encoding="utf-8"))
            self.assertEqual(bindings[0]["embeddedDeviceTypeCode"], "FCT")
            self.assertEqual(bindings[0]["sourceSystemValue"], "CCTV")

    def test_no_db_imports(self) -> None:
        module_dir = BACKEND / "src/asset_graph/industry_profiles/airport_classification"
        forbidden = ("sqlalchemy", "flask", "psycopg", "pymongo")
        for path in module_dir.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text)

    def test_read_only_classification_mode(self) -> None:
        module_dir = BACKEND / "src/asset_graph/industry_profiles/airport_classification"
        text = " ".join(path.read_text(encoding="utf-8") for path in module_dir.rglob("*.py"))
        self.assertIn("READ_ONLY_CLASSIFICATION", text)

    def test_forbidden_readiness_not_returned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            result = _run_classification(base, devices)
            self.assertNotIn(
                result["readinessOutcome"],
                {"READY_FOR_DATABASE_IMPORT", "READY_FOR_CANONICAL_WRITE", "READY_FOR_WRITE_CUTOVER"},
            )

    def test_profile_id_constant(self) -> None:
        self.assertEqual(PROFILE_ID, "airport-classification-v1")

    def test_coupler_splitter_device_types(self) -> None:
        for code in ("10DC", "6DC", "2LS", "3LS"):
            with self.subTest(code=code):
                result = classify_device_type(
                    device_type_code=code,
                    source_device_type_label=DEVICE_TYPE_DEFINITIONS[code]["label"],
                    source_evidence_digest="digest",
                )
                self.assertEqual(result["deviceTypeMappingStatus"], "EXACT_TYPE_MATCH")

    def test_eml_lock_non_standard_type(self) -> None:
        result = classify_device_type(
            device_type_code="EML/DC1",
            source_device_type_label="Electromagnetic Lock",
            source_evidence_digest="digest",
        )
        self.assertEqual(result["deviceTypeMappingStatus"], "EXACT_TYPE_MATCH")
        self.assertEqual(result["genericDeviceClass"], "LOCK")

    def test_source_namespace_separated_from_system_category(self) -> None:
        segment = parse_device_id_segments("TE3-SCN-BAS-DA31-TEL-001")
        result = self._classify("TE3-SCN-BAS-DA31-TEL-001", "TEL")
        self.assertEqual(segment.source_namespace_code, "SCN")
        self.assertEqual(result["genericSystemCategory"], "TELECOMMUNICATION")

    def test_acs_non_standard_column_authoritative(self) -> None:
        result = self._classify("BAS-EML/DC1-001", "ACS")
        self.assertEqual(result["mappingStatus"], "EXACT_MATCH")
        self.assertEqual(result["genericSystemCategory"], "ACCESS_CONTROL")

    def test_manifest_generated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_classification(base, devices)
            manifest = json.loads((base / "out" / "artifact-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["authority"], AUTHORITY)
            self.assertFalse(manifest["containsRawWorkbook"])

    def test_system_result_contains_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_classification(base, devices)
            system_doc = json.loads((base / "out" / "airport-system-classification-result.json").read_text(encoding="utf-8"))
            self.assertTrue(system_doc["candidates"])

    def test_device_type_result_contains_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_classification(base, devices)
            type_doc = json.loads((base / "out" / "airport-device-type-classification-result.json").read_text(encoding="utf-8"))
            self.assertTrue(type_doc["candidates"])

    def test_binding_count_matches_devices(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [
                _fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV"),
                _fx._device_with_type("TE3-PAS-BAS-DA21-HSP-002", row=3, system="PA", device_type="Horn Speaker"),
            ]
            _run_classification(base, devices)
            summary = json.loads((base / "out" / "airport-classification-summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["deviceCandidateCount"], 2)

    def test_scn_review_finding_emitted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-SCN-BAS-DA31-TEL-001", system="TEL", device_type="IP Telephone")]
            _run_classification(base, devices)
            reviews = json.loads((base / "out" / "airport-classification-review-findings.json").read_text(encoding="utf-8"))
            classifications = {item.get("classification") for item in reviews}
            self.assertIn("SCN_SEMANTIC_REVIEW_REQUIRED", classifications)


if __name__ == "__main__":
    unittest.main()
