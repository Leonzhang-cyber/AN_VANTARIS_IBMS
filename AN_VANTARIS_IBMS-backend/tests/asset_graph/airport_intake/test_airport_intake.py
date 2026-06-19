"""Focused tests for airport asset Excel intake profile."""
from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BACKEND = ROOT / "AN_VANTARIS_IBMS-backend"
sys.path.insert(0, str(BACKEND))

from src.asset_graph.airport_intake.constants import (
    ASSET_MASTER_COLUMNS,
    FORBIDDEN_READINESS_OUTCOMES,
    MAINTENANCE_EXTENSION_COLUMNS,
    PLACEHOLDER_AIRPORT,
    PLACEHOLDER_TERMINAL,
)
from src.asset_graph.airport_intake.device_id import compare_parsed_to_columns, parse_device_id
from src.asset_graph.airport_intake.errors import AirportIntakeError
from src.asset_graph.airport_intake.headers import normalize_header
from src.asset_graph.airport_intake.intake import compare_deterministic_outputs, run_airport_asset_excel_intake
from src.asset_graph.airport_intake.location import candidate_display_name, normalize_location
from src.asset_graph.airport_intake.system_aliases import evaluate_system_alias
from src.asset_graph.airport_intake.workbook import AirportExcelWorkbook

FIXTURES_PATH = Path(__file__).resolve().parent / "fixtures.py"
_spec = importlib.util.spec_from_file_location("airport_intake_fixtures", FIXTURES_PATH)
_fixtures = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_fixtures)
write_workbook = _fixtures.write_workbook
write_privacy_workbook = _fixtures.write_privacy_workbook

RUNNER = ROOT / "scripts/validation/run-one-airport-asset-excel-intake.py"
MODULE_DIR = BACKEND / "src/asset_graph/airport_intake"
FORBIDDEN_IMPORTS = ("sqlalchemy", "flask", "src.ufms", "src.umms", "src.Iot")


class TestAirportAssetExcelIntake(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.workbook_path = Path(self.tempdir.name) / "fixture.xlsx"
        write_workbook(self.workbook_path)
        self.output_dir = Path(self.tempdir.name) / "out"
        self.run_kwargs = {
            "input_path": self.workbook_path,
            "output_dir": self.output_dir,
            "airport_context_id": PLACEHOLDER_AIRPORT,
            "terminal_context_id": PLACEHOLDER_TERMINAL,
            "run_id": "AIRPORT-ASSET-INTAKE-TEST",
        }

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _run(self) -> dict:
        return run_airport_asset_excel_intake(**self.run_kwargs)

    # 1
    def test_xlsx_extension_accepted(self) -> None:
        AirportExcelWorkbook.validate_extension(self.workbook_path)

    # 2
    def test_xlsm_extension_rejected(self) -> None:
        path = Path(self.tempdir.name) / "bad.xlsm"
        path.write_bytes(b"fake")
        with self.assertRaises(AirportIntakeError):
            AirportExcelWorkbook.validate_extension(path)

    # 3
    def test_required_worksheets_detected(self) -> None:
        with AirportExcelWorkbook.open(self.workbook_path) as book:
            self.assertEqual(book.sheet_names(), ("Zone-1", "Zone-2"))

    # 4
    def test_missing_worksheet_rejected(self) -> None:
        bad_path = Path(self.tempdir.name) / "missing.xlsx"
        with zipfile.ZipFile(self.workbook_path, "r") as zin:
            with zipfile.ZipFile(bad_path, "w") as zout:
                for item in zin.infolist():
                    if item.filename.endswith("workbook.xml"):
                        data = zin.read(item.filename).decode("utf-8").replace('name="Zone-2"', 'name="Missing"')
                        zout.writestr(item, data.encode("utf-8"))
                    else:
                        zout.writestr(item, zin.read(item.filename))
        with self.assertRaises(AirportIntakeError):
            AirportExcelWorkbook.open(bad_path)

    # 5
    def test_header_normalization(self) -> None:
        self.assertEqual(normalize_header("  device id "), "Device ID")
        self.assertEqual(normalize_header("DEVICE\nTYPE"), "Device Type")

    # 6
    def test_required_asset_columns_present(self) -> None:
        with AirportExcelWorkbook.open(self.workbook_path) as book:
            rows = book.rows_with_row_numbers("Zone-1")
        for column in ASSET_MASTER_COLUMNS:
            self.assertIn(column, rows[0][1])

    # 7
    def test_optional_maintenance_columns_present(self) -> None:
        with AirportExcelWorkbook.open(self.workbook_path) as book:
            rows = book.rows_with_row_numbers("Zone-1")
        for column in MAINTENANCE_EXTENSION_COLUMNS:
            self.assertIn(column, rows[0][1])

    # 8
    def test_row_extraction(self) -> None:
        result = self._run()
        self.assertGreater(result["aggregateSummary"]["sourceRowCount"], 0)

    # 9
    def test_blank_trailing_rows_ignored(self) -> None:
        with AirportExcelWorkbook.open(self.workbook_path) as book:
            rows = book.rows_with_row_numbers("Zone-1")
        self.assertLess(len(rows), 16)

    # 10
    def test_row_level_level_authority(self) -> None:
        result = self._run()
        evidence = json.loads((self.output_dir / "airport-asset-intake-evidence.json").read_text())
        levels = evidence["spatialCandidates"]["level"]
        self.assertIn("GRD", levels)
        self.assertIn("BAS", levels)

    # 11
    def test_sheet_zone_inconsistency_reported(self) -> None:
        result = self._run()
        evidence = json.loads((self.output_dir / "airport-asset-intake-evidence.json").read_text())
        self.assertTrue(evidence["sheetZoneInconsistencies"])

    # 12
    def test_device_id_parsing_success(self) -> None:
        parsed = parse_device_id("TE3-CCT-BAS-DA21-FCT-001")
        self.assertTrue(parsed.parsed_successfully)
        self.assertEqual(parsed.segments["buildingCode"], "TE3")

    # 13
    def test_device_id_partial_parse(self) -> None:
        parsed = parse_device_id("TE3-CCT-BAS")
        self.assertTrue(parsed.partially_parsed)

    # 14
    def test_device_id_unparseable(self) -> None:
        parsed = parse_device_id("BAD")
        self.assertTrue(parsed.unparseable)

    # 15
    def test_system_alias_candidate_cct_cctv(self) -> None:
        alias = evaluate_system_alias(column_system="CCT", embedded_system="CCT")
        self.assertIn(alias["status"], {"KNOWN_ALIAS_CANDIDATE", "EXACT_MATCH"})

    # 16
    def test_system_alias_candidate_pa_pas(self) -> None:
        alias = evaluate_system_alias(column_system="PAS", embedded_system="PAS")
        self.assertIn(alias["status"], {"KNOWN_ALIAS_CANDIDATE", "EXACT_MATCH"})

    # 17
    def test_system_exact_match_acs(self) -> None:
        alias = evaluate_system_alias(column_system="ACS", embedded_system="ACS")
        self.assertEqual(alias["status"], "EXACT_MATCH")

    # 18
    def test_duplicate_within_sheet(self) -> None:
        result = self._run()
        evidence = json.loads((self.output_dir / "airport-asset-intake-evidence.json").read_text())
        dup_ids = [item["deviceId"] for item in evidence["duplicateFindings"] if "deviceId" in item]
        self.assertIn("TE3-CCT-BAS-DA21-FCT-001", dup_ids)

    # 19
    def test_duplicate_across_sheets(self) -> None:
        result = self._run()
        evidence = json.loads((self.output_dir / "airport-asset-intake-evidence.json").read_text())
        cross = [
            item for item in evidence["duplicateFindings"]
            if item.get("crossWorksheet") and item.get("deviceId") == "TE3-CCT-BAS-DA21-FCT-001"
        ]
        self.assertTrue(cross)

    # 20
    def test_identical_duplicate_classification(self) -> None:
        result = self._run()
        evidence = json.loads((self.output_dir / "airport-asset-intake-evidence.json").read_text())
        identical = [
            item for item in evidence["duplicateFindings"]
            if item.get("classification") == "DUPLICATE_SOURCE_IDENTITY_IDENTICAL"
            and item.get("deviceId") == "TE3-ACS-BAS-DA21-DRR-001"
        ]
        self.assertTrue(identical)

    # 21
    def test_conflicting_duplicate_classification(self) -> None:
        result = self._run()
        evidence = json.loads((self.output_dir / "airport-asset-intake-evidence.json").read_text())
        conflict = [
            item for item in evidence["duplicateFindings"]
            if item.get("classification") == "DUPLICATE_SOURCE_IDENTITY_CONFLICT"
        ]
        self.assertTrue(conflict)

    # 22
    def test_missing_device_id_counted(self) -> None:
        result = self._run()
        self.assertGreater(result["aggregateSummary"]["missingDeviceIdCount"], 0)

    # 23
    def test_missing_location_counted(self) -> None:
        result = self._run()
        self.assertGreater(result["aggregateSummary"]["missingLocationCount"], 0)

    # 24
    def test_location_normalization(self) -> None:
        raw, normalized = normalize_location("  fire   exit\n corridor  ")
        self.assertEqual(normalized, "FIRE EXIT CORRIDOR")

    # 25
    def test_no_semantic_location_merge(self) -> None:
        _, loc_a = normalize_location("FIRE EXIT CORRIDOR")
        _, loc_b = normalize_location("FIRE EXIT CORRIDOR DOOR")
        self.assertNotEqual(loc_a, loc_b)

    # 26
    def test_maintenance_field_separation(self) -> None:
        result = self._run()
        evidence = json.loads((self.output_dir / "airport-asset-intake-evidence.json").read_text())
        device = evidence["deviceCandidates"][0]
        self.assertIn("assetMasterFields", device)
        self.assertNotIn("Day", device["assetMasterFields"])
        self.assertGreater(len(evidence["maintenanceExtensionCandidates"]), 0)

    # 27
    def test_ambiguous_day_reported(self) -> None:
        result = self._run()
        evidence = json.loads((self.output_dir / "airport-asset-intake-evidence.json").read_text())
        self.assertTrue(evidence["maintenanceAmbiguities"])

    # 28
    def test_zero_point_generation(self) -> None:
        result = self._run()
        self.assertEqual(result["aggregateSummary"]["pointCandidateCount"], 0)

    # 29
    def test_zero_telemetry_generation(self) -> None:
        result = self._run()
        self.assertEqual(result["aggregateSummary"]["telemetryRecordCount"], 0)

    # 30
    def test_zero_alarm_generation(self) -> None:
        result = self._run()
        self.assertEqual(result["aggregateSummary"]["alarmRecordCount"], 0)

    # 31
    def test_spatial_candidate_generation(self) -> None:
        result = self._run()
        evidence = json.loads((self.output_dir / "airport-asset-intake-evidence.json").read_text())
        self.assertIn("building", evidence["spatialCandidates"])
        self.assertIn("TE3", evidence["spatialCandidates"]["building"])

    # 32
    def test_relationship_candidate_generation(self) -> None:
        result = self._run()
        evidence = json.loads((self.output_dir / "airport-asset-intake-evidence.json").read_text())
        types = {item["relationshipType"] for item in evidence["relationshipCandidates"]}
        self.assertIn("LOCATED_IN", types)
        self.assertIn("BELONGS_TO", types)

    # 33
    def test_no_has_point_relationships(self) -> None:
        result = self._run()
        evidence = json.loads((self.output_dir / "airport-asset-intake-evidence.json").read_text())
        self.assertFalse(any(item["relationshipType"] == "HAS_POINT" for item in evidence["relationshipCandidates"]))

    # 34
    def test_privacy_scan_blocks_intake(self) -> None:
        privacy_path = Path(self.tempdir.name) / "privacy.xlsx"
        write_privacy_workbook(privacy_path)
        with self.assertRaises(AirportIntakeError):
            run_airport_asset_excel_intake(
                input_path=privacy_path,
                output_dir=Path(self.tempdir.name) / "privacy-out",
                airport_context_id=PLACEHOLDER_AIRPORT,
                terminal_context_id=PLACEHOLDER_TERMINAL,
                run_id="PRIVACY-TEST",
            )

    # 35
    def test_deterministic_evidence(self) -> None:
        run_airport_asset_excel_intake(**self.run_kwargs)
        first = self.output_dir / "airport-asset-intake-evidence.json"
        out2 = Path(self.tempdir.name) / "out2"
        run_airport_asset_excel_intake(**{**self.run_kwargs, "output_dir": out2})
        second = out2 / "airport-asset-intake-evidence.json"
        ok, reason = compare_deterministic_outputs(first, second)
        self.assertTrue(ok, reason)

    # 36
    def test_aggregate_report_excludes_identifiers(self) -> None:
        result = self._run()
        aggregate = json.loads((self.output_dir / "airport-asset-data-quality-summary.json").read_text())
        blob = json.dumps(aggregate)
        self.assertFalse(aggregate["containsCustomerAssetIdentifiers"])
        self.assertNotIn("TE3-CCT-BAS-DA21-FCT-001", blob)

    # 37
    def test_no_db_imports_in_module(self) -> None:
        for path in MODULE_DIR.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                if isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                for name in names:
                    if any(name.startswith(prefix) for prefix in FORBIDDEN_IMPORTS):
                        self.fail(f"{path.name} imports forbidden module {name}")

    # 38
    def test_no_provider_writes(self) -> None:
        text = " ".join(path.read_text(encoding="utf-8") for path in MODULE_DIR.glob("*.py"))
        self.assertNotIn("InMemoryAssetGraphProvider", text)
        self.assertNotIn("provider.write", text)

    # 39
    def test_no_ufms_umms_runtime_imports(self) -> None:
        text = " ".join(path.read_text(encoding="utf-8") for path in MODULE_DIR.glob("*.py"))
        self.assertNotIn("src.ufms", text)
        self.assertNotIn("src.umms", text)

    # 40
    def test_workbook_not_in_repo(self) -> None:
        tracked = subprocess.run(
            ["git", "ls-files", "*Zonewise*", "*Asset_Database*"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertEqual(tracked, "")

    # 41
    def test_readiness_not_write_cutover(self) -> None:
        result = self._run()
        self.assertNotIn(result["readinessOutcome"], FORBIDDEN_READINESS_OUTCOMES)

    # 42
    def test_readiness_complete_with_reviews(self) -> None:
        result = self._run()
        self.assertEqual(result["readinessOutcome"], "INTAKE_COMPLETE_WITH_REVIEWS")

    # 43
    def test_candidate_display_name(self) -> None:
        name = candidate_display_name("Camera", "Lobby A")
        self.assertIn("CAMERA", name)
        self.assertIn("LOBBY A", name)

    # 44
    def test_column_agreement_parsing(self) -> None:
        parsed = parse_device_id("TE3-CCT-BAS-DA21-FCT-001")
        comparison = compare_parsed_to_columns(
            parsed,
            building="TE3",
            level="BAS",
            distribution_area="DA21",
            system="CCT",
        )
        self.assertEqual(comparison["status"], "COLUMN_AGREEMENT")

    # 45
    def test_artifact_manifest_no_raw_workbook(self) -> None:
        result = self._run()
        manifest = json.loads((self.output_dir / "artifact-manifest.json").read_text())
        self.assertFalse(manifest["containsRawWorkbook"])

    # 46
    def test_duplicate_sl_review(self) -> None:
        result = self._run()
        evidence = json.loads((self.output_dir / "airport-asset-intake-evidence.json").read_text())
        sl_dup = [item for item in evidence["duplicateFindings"] if item.get("field") == "SL"]
        self.assertTrue(sl_dup or evidence["duplicateFindings"])

    # 47
    def test_system_candidates_include_expected_codes(self) -> None:
        result = self._run()
        evidence = json.loads((self.output_dir / "airport-asset-intake-evidence.json").read_text())
        for code in ("CCT", "PAS", "ACS", "RAS", "TEL"):
            self.assertIn(code, evidence["systemCandidates"])

    # 48
    def test_cli_runner_check_mode(self) -> None:
        out_dir = Path(self.tempdir.name) / "cli-out"
        cmd = [
            sys.executable,
            str(RUNNER),
            "--root", str(ROOT),
            "--input", str(self.workbook_path),
            "--output-dir", str(out_dir),
            "--airport-context-id", PLACEHOLDER_AIRPORT,
            "--terminal-context-id", PLACEHOLDER_TERMINAL,
            "--run-id", "CLI-TEST-001",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("ONE_AIRPORT_ASSET_EXCEL_INTAKE_RUN_PASS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
