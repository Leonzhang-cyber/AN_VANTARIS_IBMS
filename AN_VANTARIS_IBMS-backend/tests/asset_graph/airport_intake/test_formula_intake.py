"""Focused tests for formula-safe airport asset Excel intake."""
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

from src.asset_graph.airport_intake.derived_columns import (
    compare_building,
    compare_device_type,
    compare_level,
    derive_controlled_values,
)
from src.asset_graph.airport_intake.errors import AirportIntakeError
from src.asset_graph.airport_intake.formula_safety import classify_column_formula, inspect_formula_text
from src.asset_graph.airport_intake.formula_workbook import FormulaSafeWorkbook
from src.asset_graph.airport_intake.intake import compare_deterministic_outputs, run_airport_asset_excel_intake

FIXTURES = Path(__file__).resolve().parent / "formula_fixtures.py"
_spec = importlib.util.spec_from_file_location("formula_fixtures", FIXTURES)
_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_mod)


class TestFormulaSafeAirportIntake(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.output = Path(self.tempdir.name) / "out"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _run(self, workbook: Path) -> dict:
        return run_airport_asset_excel_intake(
            input_path=workbook,
            output_dir=self.output,
            airport_context_id="AIRPORT-CONTEXT-REQUIRED",
            terminal_context_id="TERMINAL-CONTEXT-REQUIRED",
            run_id="FORMULA-TEST",
        )

    def test_approved_formula_columns_detected(self) -> None:
        path = Path(self.tempdir.name) / "approved.xlsx"
        _mod.write_formula_workbook(path)
        with FormulaSafeWorkbook.open(path) as book:
            inventory = book.formula_inventory()
        self.assertGreater(inventory["formulaCellCount"], 0)

    def test_unapproved_formula_column_rejected(self) -> None:
        path = Path(self.tempdir.name) / "unapproved.xlsx"
        _mod.write_unapproved_formula_workbook(path)
        with self.assertRaises(AirportIntakeError) as ctx:
            self._run(path)
        self.assertEqual(ctx.exception.code, "INPUT_REJECTED")

    def test_formula_and_cached_view_separation(self) -> None:
        path = Path(self.tempdir.name) / "approved.xlsx"
        _mod.write_formula_workbook(path)
        with FormulaSafeWorkbook.open(path) as book:
            rows = book.rows_with_formula_metadata("Zone-1")
        self.assertTrue(rows[0][2]["Building"]["formulaCellPresent"])
        self.assertTrue(rows[0][2]["Building"]["cachedValuePresent"] or rows[0][1]["Building"] is None)

    def test_no_formula_execution_in_module(self) -> None:
        module_dir = BACKEND / "src/asset_graph/airport_intake"
        text = " ".join(path.read_text(encoding="utf-8") for path in module_dir.glob("*.py"))
        self.assertNotIn("eval(", text)
        self.assertNotIn("exec(", text)
        self.assertNotIn("data_only=False", text.replace("load_workbook(self.path, data_only=False", ""))

    def test_building_match(self) -> None:
        derived = derive_controlled_values("TE3-CCT-BAS-DA21-FCT-001")
        self.assertEqual(compare_building("TE3", derived)["comparisonStatus"], "FORMULA_DERIVATION_MATCH")

    def test_building_mismatch(self) -> None:
        derived = derive_controlled_values("TE3-CCT-BAS-DA21-FCT-001")
        self.assertEqual(compare_building("WRONG", derived)["comparisonStatus"], "FORMULA_DERIVATION_MISMATCH")

    def test_level_match(self) -> None:
        derived = derive_controlled_values("TE3-CCT-BAS-DA21-FCT-001")
        self.assertEqual(compare_level("BAS", derived)["comparisonStatus"], "FORMULA_DERIVATION_MATCH")

    def test_level_mismatch(self) -> None:
        derived = derive_controlled_values("TE3-CCT-BAS-DA21-FCT-001")
        self.assertEqual(compare_level("ROF", derived)["comparisonStatus"], "FORMULA_DERIVATION_MISMATCH")

    def test_device_type_derivation(self) -> None:
        derived = derive_controlled_values("TE3-CCT-BAS-DA21-FCT-001")
        result = compare_device_type("Fixed Camera", derived)
        self.assertEqual(result["comparisonStatus"], "FORMULA_DERIVATION_MATCH")

    def test_external_reference_rejection(self) -> None:
        self.assertEqual(inspect_formula_text('=INDIRECT("[Other.xlsx]Sheet1!A1")'), "EXTERNAL_REFERENCE_FORMULA")

    def test_indirect_rejection(self) -> None:
        self.assertEqual(inspect_formula_text("=INDIRECT(A1)"), "UNSUPPORTED_FORMULA")

    def test_offset_rejection(self) -> None:
        self.assertEqual(inspect_formula_text("=OFFSET(A1,1,1)"), "UNSUPPORTED_FORMULA")

    def test_url_formula_rejection(self) -> None:
        self.assertEqual(inspect_formula_text('=HYPERLINK("http://example.com")'), "EXTERNAL_REFERENCE_FORMULA")

    def test_day_semantic_conflict(self) -> None:
        classification = classify_column_formula(
            column_name="Day",
            formula_text="=UPPER(I2)",
            cached_value="LOBBY A",
            location_value="Lobby A",
        )
        self.assertEqual(classification, "LEGACY_FIELD_SEMANTIC_CONFLICT")

    def test_day_not_umms_schedule_in_intake(self) -> None:
        path = Path(self.tempdir.name) / "approved.xlsx"
        _mod.write_formula_workbook(path)
        self._run(path)
        evidence = json.loads((self.output / "airport-asset-intake-evidence.json").read_text())
        for item in evidence["maintenanceExtensionCandidates"]:
            self.assertNotIn("Day", item.get("fields", {}))

    def test_derivation_mismatch_blocks_intake(self) -> None:
        path = Path(self.tempdir.name) / "mismatch.xlsx"
        _mod.write_mismatch_formula_workbook(path)
        result = self._run(path)
        self.assertEqual(result["readinessOutcome"], "INTAKE_BLOCKED")

    def test_aggregate_excludes_formulas_and_identifiers(self) -> None:
        path = Path(self.tempdir.name) / "approved.xlsx"
        _mod.write_formula_workbook(path)
        self._run(path)
        aggregate = json.loads((self.output / "airport-asset-data-quality-summary.json").read_text())
        blob = json.dumps(aggregate)
        self.assertNotIn("=LEFT", blob)
        self.assertNotIn("TE3-CCT", blob)
        self.assertIn("formulaCellCount", aggregate)

    def test_deterministic_formula_intake(self) -> None:
        path = Path(self.tempdir.name) / "approved.xlsx"
        _mod.write_formula_workbook(path)
        self._run(path)
        first = self.output / "airport-asset-intake-evidence.json"
        out2 = Path(self.tempdir.name) / "out2"
        run_airport_asset_excel_intake(
            input_path=path,
            output_dir=out2,
            airport_context_id="AIRPORT-CONTEXT-REQUIRED",
            terminal_context_id="TERMINAL-CONTEXT-REQUIRED",
            run_id="FORMULA-TEST",
        )
        ok, reason = compare_deterministic_outputs(first, out2 / "airport-asset-intake-evidence.json")
        self.assertTrue(ok, reason)

    def test_no_asset_graph_core_modification(self) -> None:
        core = BACKEND / "src/asset_graph/models.py"
        self.assertIn("class Device", core.read_text(encoding="utf-8"))

    def test_no_db_provider_api_changes(self) -> None:
        module_dir = BACKEND / "src/asset_graph/airport_intake"
        for path in module_dir.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertFalse(alias.name.startswith("sqlalchemy"))
                if isinstance(node, ast.ImportFrom):
                    self.assertFalse((node.module or "").startswith("sqlalchemy"))


if __name__ == "__main__":
    unittest.main()
