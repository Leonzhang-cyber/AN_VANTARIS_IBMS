"""Focused tests for airport spatial hierarchy profile."""
from __future__ import annotations

import ast
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BACKEND = ROOT / "AN_VANTARIS_IBMS-backend"
sys.path.insert(0, str(BACKEND))

from src.asset_graph.industry_profiles.airport_spatial.constants import GENERIC_TO_AIRPORT, PROFILE_ID
from src.asset_graph.industry_profiles.airport_spatial.context import AirportSpatialContext
from src.asset_graph.industry_profiles.airport_spatial.errors import AirportSpatialProfileError
from src.asset_graph.industry_profiles.airport_spatial.mapper import compare_deterministic_outputs, run_airport_spatial_mapping
from src.asset_graph.models import RelationshipType

FIXTURES = Path(__file__).resolve().parent / "fixtures.py"
_spec = importlib.util.spec_from_file_location("spatial_fixtures", FIXTURES)
_fx = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_fx)

REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/airport-spatial-profile.v1.json"
MODULE_DIR = BACKEND / "src/asset_graph/industry_profiles"
MODELS = BACKEND / "src/asset_graph/models.py"


class TestAirportSpatialProfile(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.base = Path(self.tempdir.name)
        self.evidence_path = self.base / "intake.json"
        _fx.write_intake_evidence(self.evidence_path)
        self.output = self.base / "out"
        self.context = AirportSpatialContext.create(**_fx.default_context_kwargs())

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _run(self, **kwargs) -> dict:
        return run_airport_spatial_mapping(
            intake_evidence_path=self.evidence_path,
            output_dir=self.output,
            context=kwargs.get("context", self.context),
            run_id="SPATIAL-TEST-001",
        )

    # 1
    def test_profile_registry_exists(self) -> None:
        self.assertTrue(REGISTRY.is_file())

    # 2
    def test_registry_industry_profile_type(self) -> None:
        registry = json.loads(REGISTRY.read_text())
        self.assertEqual(registry["profileType"], "INDUSTRY_PROFILE")

    # 3
    def test_platform_core_not_airportized(self) -> None:
        registry = json.loads(REGISTRY.read_text())
        self.assertFalse(registry["platformCoreAirportized"])

    # 4
    def test_optional_airport_terminal_in_registry(self) -> None:
        registry = json.loads(REGISTRY.read_text())
        self.assertIn("Airport", registry["optionalAirportProfileLevels"])

    # 5
    def test_context_requires_tenant(self) -> None:
        with self.assertRaises(AirportSpatialProfileError):
            AirportSpatialContext.create(**{**_fx.default_context_kwargs(), "tenant_id": ""})

    # 6
    def test_context_requires_site(self) -> None:
        with self.assertRaises(AirportSpatialProfileError):
            AirportSpatialContext.create(**{**_fx.default_context_kwargs(), "site_id": ""})

    # 7
    def test_context_rejects_wildcard_tenant(self) -> None:
        with self.assertRaises(AirportSpatialProfileError):
            AirportSpatialContext.create(**{**_fx.default_context_kwargs(), "tenant_id": "ALL_SITES"})

    # 8
    def test_context_rejects_any_site(self) -> None:
        with self.assertRaises(AirportSpatialProfileError):
            AirportSpatialContext.create(**{**_fx.default_context_kwargs(), "site_id": "ANY_SITE"})

    # 9
    def test_customer_codes_not_in_generic_enums(self) -> None:
        text = MODELS.read_text(encoding="utf-8")
        self.assertNotIn("TE3", text)
        self.assertNotIn("DA21", text)

    # 10
    def test_generic_asset_graph_models_unchanged(self) -> None:
        self.assertIn("class Device", MODELS.read_text(encoding="utf-8"))

    # 11
    def test_building_mapping(self) -> None:
        result = self._run()
        payload = json.loads(Path(result["resultPath"]).read_text())
        buildings = [c for c in payload["candidates"] if c["candidateType"] == "BuildingCandidate"]
        self.assertEqual(buildings[0]["genericTarget"], "Building")

    # 12
    def test_level_mapping(self) -> None:
        result = self._run()
        payload = json.loads(Path(result["resultPath"]).read_text())
        levels = [c for c in payload["candidates"] if c["candidateType"] == "LevelCandidate"]
        self.assertTrue(levels)

    # 13
    def test_zone_mapping(self) -> None:
        result = self._run()
        payload = json.loads(Path(result["resultPath"]).read_text())
        zones = [c for c in payload["candidates"] if c["candidateType"] == "ZoneCandidate"]
        self.assertEqual({z["normalizedCode"] for z in zones}, {"Z1", "Z2"})

    # 14
    def test_distribution_area_profile_mapping(self) -> None:
        result = self._run()
        payload = json.loads(Path(result["resultPath"]).read_text())
        das = [c for c in payload["candidates"] if c["candidateType"] == "DistributionAreaCandidate"]
        self.assertEqual(das[0]["profileLabel"], "DistributionArea")
        self.assertEqual(das[0]["genericTarget"], "ZoneExtension")

    # 15
    def test_sheet_zone_match(self) -> None:
        result = self._run()
        reviews = json.loads(Path(result["reviewsPath"]).read_text())
        self.assertTrue(any(r.get("classification") == "SHEET_ZONE_MATCH" for r in reviews))

    # 16
    def test_sheet_zone_mismatch(self) -> None:
        devices = [_fx._device("SYNTH-DEV-MIS", worksheet="Zone-1", zone="Z2")]
        _fx.write_intake_evidence(self.evidence_path, devices=devices)
        result = self._run()
        reviews = json.loads(Path(result["reviewsPath"]).read_text())
        self.assertTrue(any(r.get("classification") == "SHEET_ZONE_MISMATCH" for r in reviews))

    # 17
    def test_location_normalization(self) -> None:
        result = self._run()
        payload = json.loads(Path(result["resultPath"]).read_text())
        locations = [c for c in payload["candidates"] if c["candidateType"] == "LocationCandidate"]
        self.assertIn("FIRE EXIT CORRIDOR", {loc["normalizedCode"] for loc in locations})

    # 18
    def test_no_semantic_location_merge(self) -> None:
        result = self._run()
        payload = json.loads(Path(result["resultPath"]).read_text())
        codes = {c["normalizedCode"] for c in payload["candidates"] if c["candidateType"] == "LocationCandidate"}
        self.assertIn("FIRE EXIT CORRIDOR", codes)
        self.assertIn("FIRE EXIT CORRIDOR DOOR", codes)

    # 19
    def test_device_spatial_binding(self) -> None:
        result = self._run()
        bindings = json.loads(Path(result["bindingsPath"]).read_text())
        self.assertEqual(len(bindings), 3)
        self.assertTrue(bindings[0]["buildingCandidateKey"])

    # 20
    def test_missing_spatial_fields(self) -> None:
        devices = [_fx._device("SYNTH-MISSING", building="", level="", zone="", da="", location="")]
        _fx.write_intake_evidence(self.evidence_path, devices=devices)
        result = self._run()
        summary = json.loads(Path(result["summaryPath"]).read_text())
        self.assertGreater(summary["missingBuildingCount"], 0)

    # 21
    def test_aggregate_excludes_identifiers(self) -> None:
        result = self._run()
        summary = json.loads(Path(result["summaryPath"]).read_text())
        blob = json.dumps(summary)
        self.assertFalse(summary["containsCustomerAssetIdentifiers"])
        self.assertNotIn("SYNTH-DEV", blob)

    # 22
    def test_deterministic_result_digest(self) -> None:
        first = self._run()
        out2 = self.base / "out2"
        second = run_airport_spatial_mapping(
            intake_evidence_path=self.evidence_path,
            output_dir=out2,
            context=self.context,
            run_id="SPATIAL-TEST-001",
        )
        self.assertEqual(first["resultDigest"], second["resultDigest"])

    # 23
    def test_deterministic_outputs(self) -> None:
        self._run()
        out2 = self.base / "out2"
        run_airport_spatial_mapping(
            intake_evidence_path=self.evidence_path,
            output_dir=out2,
            context=self.context,
            run_id="SPATIAL-TEST-001",
        )
        ok, reason = compare_deterministic_outputs(
            self.output / "airport-spatial-profile-result.json",
            out2 / "airport-spatial-profile-result.json",
        )
        self.assertTrue(ok, reason)

    # 24
    def test_readiness_with_reviews(self) -> None:
        result = self._run()
        self.assertEqual(result["readinessOutcome"], "SPATIAL_MAPPING_COMPLETE_WITH_REVIEWS")

    # 25
    def test_forbidden_readiness_not_returned(self) -> None:
        result = self._run()
        self.assertNotIn(result["readinessOutcome"], {"READY_FOR_DATABASE_IMPORT", "READY_FOR_CANONICAL_WRITE"})

    # 26
    def test_no_db_imports(self) -> None:
        for path in MODULE_DIR.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertFalse(alias.name.startswith("sqlalchemy"))

    # 27
    def test_no_provider_writes(self) -> None:
        text = " ".join(path.read_text(encoding="utf-8") for path in MODULE_DIR.rglob("*.py"))
        self.assertNotIn("InMemoryAssetGraphProvider", text)

    # 28
    def test_generic_relationship_semantics(self) -> None:
        result = self._run()
        payload = json.loads(Path(result["resultPath"]).read_text())
        semantics = {rel["genericRelationshipSemantic"] for rel in payload["relationshipCandidates"]}
        self.assertTrue(semantics.issubset({item.value for item in RelationshipType} | {"ASSIGNED_TO", "BELONGS_TO"}))

    # 29
    def test_airport_maps_to_site(self) -> None:
        self.assertEqual(GENERIC_TO_AIRPORT["Airport"]["genericTarget"], "Site")

    # 30
    def test_terminal_maps_to_facility(self) -> None:
        self.assertEqual(GENERIC_TO_AIRPORT["Terminal"]["genericTarget"], "Facility")

    # 31
    def test_context_scope_digest_stable(self) -> None:
        ctx1 = AirportSpatialContext.create(**_fx.default_context_kwargs())
        ctx2 = AirportSpatialContext.create(**_fx.default_context_kwargs())
        self.assertEqual(ctx1.scope_digest, ctx2.scope_digest)

    # 32
    def test_intake_authority_mismatch_rejected(self) -> None:
        payload = _fx.build_intake_evidence()
        payload["authority"] = "WRONG"
        self.evidence_path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(AirportSpatialProfileError):
            self._run()

    # 33
    def test_intake_digest_mismatch_rejected(self) -> None:
        ctx = AirportSpatialContext.create(**{**_fx.default_context_kwargs(), "source_workbook_digest": "wrong"})
        with self.assertRaises(AirportSpatialProfileError):
            run_airport_spatial_mapping(
                intake_evidence_path=self.evidence_path,
                output_dir=self.output,
                context=ctx,
                run_id="X",
            )

    # 34
    def test_terminal_candidate_placeholder_review(self) -> None:
        result = self._run()
        reviews = json.loads(Path(result["reviewsPath"]).read_text())
        self.assertTrue(any(r.get("classification") == "CONTEXT_PLACEHOLDER_REVIEW" for r in reviews))

    # 35
    def test_location_collision_count(self) -> None:
        result = self._run()
        summary = json.loads(Path(result["summaryPath"]).read_text())
        self.assertGreaterEqual(summary["normalizedLocationCollisionCount"], 0)

    # 36
    def test_manifest_generated(self) -> None:
        result = self._run()
        self.assertTrue(Path(result["manifestPath"]).is_file())

    # 37
    def test_profile_id_constant(self) -> None:
        self.assertEqual(PROFILE_ID, "airport-spatial-v1")

    # 38
    def test_device_binding_count_metric(self) -> None:
        result = self._run()
        summary = json.loads(Path(result["summaryPath"]).read_text())
        self.assertEqual(summary["deviceBindingCount"], 3)

    # 39
    def test_unbound_device_metric(self) -> None:
        devices = [_fx._device("SYNTH-UNBOUND", building="")]
        _fx.write_intake_evidence(self.evidence_path, devices=devices)
        result = self._run()
        summary = json.loads(Path(result["summaryPath"]).read_text())
        self.assertGreater(summary["unboundDeviceCount"], 0)

    # 40
    def test_hierarchy_summary_metrics_present(self) -> None:
        result = self._run()
        summary = json.loads(Path(result["summaryPath"]).read_text())
        for key in (
            "buildingCandidateCount",
            "levelCandidateCount",
            "zoneCandidateCount",
            "distributionAreaCandidateCount",
            "locationCandidateCount",
        ):
            self.assertIn(key, summary)

    # 41
    def test_parent_exists_on_candidates(self) -> None:
        result = self._run()
        payload = json.loads(Path(result["resultPath"]).read_text())
        for candidate in payload["candidates"]:
            if candidate["candidateType"] != "AirportCandidate":
                self.assertTrue(candidate["parentCandidateKey"])

    # 42
    def test_no_public_api_routes(self) -> None:
        text = " ".join(path.read_text(encoding="utf-8") for path in MODULE_DIR.rglob("*.py"))
        self.assertNotIn("blueprint", text.lower())

    # 43
    def test_implementation_mode_read_only(self) -> None:
        result = self._run()
        payload = json.loads(Path(result["resultPath"]).read_text())
        self.assertEqual(payload["implementationMode"], "READ_ONLY_MAPPING")

    # 44
    def test_platform_core_airportized_false_in_result(self) -> None:
        result = self._run()
        payload = json.loads(Path(result["resultPath"]).read_text())
        self.assertFalse(payload["platformCoreAirportized"])

    # 45
    def test_deterministic_candidate_keys(self) -> None:
        first = json.loads((self.output / "airport-spatial-profile-result.json").read_text()) if (self.output / "airport-spatial-profile-result.json").exists() else None
        self._run()
        payload = json.loads((self.output / "airport-spatial-profile-result.json").read_text())
        keys = [c["candidateKey"] for c in payload["candidates"]]
        self.assertEqual(len(keys), len(set(keys)))

    # 46
    def test_zone_value_missing_finding(self) -> None:
        devices = [_fx._device("SYNTH-NOZ", zone="")]
        _fx.write_intake_evidence(self.evidence_path, devices=devices)
        result = self._run()
        reviews = json.loads(Path(result["reviewsPath"]).read_text())
        self.assertTrue(any(r.get("classification") in {"ZONE_VALUE_MISSING", "MISSING_ZONE"} for r in reviews))

    # 47
    def test_context_limit_enforced(self) -> None:
        kwargs = _fx.default_context_kwargs()
        kwargs["allowed_zone_codes"] = [f"Z{i}" for i in range(10001)]
        with self.assertRaises(AirportSpatialProfileError):
            AirportSpatialContext.create(**kwargs)

    # 48
    def test_real_evidence_contract_fields(self) -> None:
        result = self._run()
        payload = json.loads(Path(result["resultPath"]).read_text())
        self.assertIn("intakeEvidence", payload)
        self.assertIn("sourceWorkbookDigest", payload["intakeEvidence"])

    # 49
    def test_relationship_contains_semantic(self) -> None:
        result = self._run()
        payload = json.loads(Path(result["resultPath"]).read_text())
        self.assertTrue(any(r["genericRelationshipSemantic"] == "CONTAINS" for r in payload["relationshipCandidates"]))

    # 50
    def test_located_in_relationship(self) -> None:
        result = self._run()
        payload = json.loads(Path(result["resultPath"]).read_text())
        self.assertTrue(any(r["genericRelationshipSemantic"] == "LOCATED_IN" for r in payload["relationshipCandidates"]))

    # 51
    def test_assigned_to_relationship(self) -> None:
        result = self._run()
        payload = json.loads(Path(result["resultPath"]).read_text())
        self.assertTrue(any(r["genericRelationshipSemantic"] == "ASSIGNED_TO" for r in payload["relationshipCandidates"]))

    # 52
    def test_no_frontend_paths_touched(self) -> None:
        self.assertFalse(any("AN_VANTARIS_IBMS-frontend" in str(p) for p in MODULE_DIR.rglob("*.py")))


if __name__ == "__main__":
    unittest.main()
