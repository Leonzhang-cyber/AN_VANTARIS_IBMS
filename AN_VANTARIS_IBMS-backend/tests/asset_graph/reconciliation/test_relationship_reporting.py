"""Tests for relationship evidence reporting clarity."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BACKEND = ROOT / "AN_VANTARIS_IBMS-backend"
SAMPLE = ROOT / "AN_VANTARIS_ONE/evidence/device-reconciliation/sample/minimal-valid-device.json"
RUNNER = ROOT / "scripts/validation/run-one-device-reconciliation-evidence.py"
EXCEL_RUNNER = ROOT / "scripts/validation/run-one-device-reconciliation-excel.py"
FIXTURES = Path(__file__).resolve().parent / "evidence/excel/fixtures.py"


def _run_evidence(sample: Path, output: Path, run_id: str) -> dict:
    result = subprocess.run(
        [
            "python3", str(RUNNER), "--root", str(ROOT), "--input", str(sample),
            "--output", str(output), "--run-id", run_id, "--format", "json",
        ],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(output.read_text(encoding="utf-8"))


class TestRelationshipEvidenceReporting(unittest.TestCase):
    maxDiff = None

    def _multi_site_report(self, run_id: str = "REL-METRICS-001") -> dict:
        spec = importlib.util.spec_from_file_location("excel_fixtures", FIXTURES)
        fixtures = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(fixtures)
        with tempfile.TemporaryDirectory() as directory:
            workbook = Path(directory) / "fixture.xlsx"
            fixtures.write_workbook(workbook)
            package = Path(directory) / "package.json"
            report = Path(directory) / "report.json"
            result = subprocess.run(
                [
                    "python3", str(EXCEL_RUNNER), "--root", str(ROOT),
                    "--input", str(workbook),
                    "--json-output", str(package),
                    "--report-output", str(report),
                    "--run-id", run_id,
                ],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(report.read_text(encoding="utf-8"))

    def test_multi_site_relationship_metrics_shape(self) -> None:
        report = self._multi_site_report()
        metrics = report["relationshipMetrics"]
        self.assertEqual(metrics["relationshipResultCount"], 589)
        self.assertEqual(metrics["canonicalRelationshipCount"], 588)
        self.assertEqual(metrics["passRelationshipCount"], 588)
        self.assertEqual(metrics["reviewRelationshipCount"], 1)
        self.assertEqual(metrics["unresolvedRelationshipCount"], 1)
        self.assertEqual(metrics["relationshipTypeCounts"]["HAS_POINT"]["passCount"], 588)
        self.assertEqual(metrics["relationshipTypeCounts"]["LOCATED_IN"]["reviewCount"], 1)
        self.assertEqual(metrics["relationshipTypeCounts"]["LOCATED_IN"]["unresolvedCount"], 1)

    def test_canonical_count_excludes_unresolved_rows(self) -> None:
        report = self._multi_site_report()
        metrics = report["relationshipMetrics"]
        self.assertEqual(
            metrics["canonicalRelationshipCount"] + metrics["unresolvedRelationshipCount"],
            metrics["passRelationshipCount"] + metrics["reviewRelationshipCount"],
        )
        self.assertGreater(metrics["relationshipResultCount"], metrics["canonicalRelationshipCount"])

    def test_type_counts_reconcile_to_total(self) -> None:
        report = self._multi_site_report()
        metrics = report["relationshipMetrics"]
        type_total = sum(
            metrics["relationshipTypeCounts"][key]["resultCount"]
            for key in metrics["relationshipTypeCounts"]
        )
        self.assertEqual(type_total, metrics["relationshipResultCount"])

    def test_status_counts_reconcile_to_total(self) -> None:
        report = self._multi_site_report()
        metrics = report["relationshipMetrics"]
        status_total = (
            metrics["passRelationshipCount"]
            + metrics["reviewRelationshipCount"]
            + metrics["blockerRelationshipCount"]
        )
        self.assertEqual(status_total, metrics["relationshipResultCount"])

    def test_duplicate_has_point_pairs_reported_separately(self) -> None:
        report = self._multi_site_report()
        metrics = report["relationshipMetrics"]
        self.assertEqual(metrics["duplicateHasPointPairCount"], 20)
        self.assertEqual(metrics["duplicateCanonicalRelationshipCount"], 20)
        self.assertTrue(metrics["duplicateRelationshipBlockerPresent"])

    def test_no_raw_identifiers_in_relationship_metrics(self) -> None:
        report = self._multi_site_report()
        text = json.dumps(report["relationshipMetrics"])
        for token in ("SYNTH-DEV-", "ag-device-", "ag-point-", "SYNTH-SITE-"):
            self.assertNotIn(token, text)

    def test_projection_summary_backward_compatible(self) -> None:
        report = self._multi_site_report()
        summary = report["projectionSummary"]
        self.assertEqual(summary["projectedRelationshipCount"], 589)
        self.assertEqual(summary["projectedPointCount"], 588)
        self.assertIn("projectedRelationshipCountSemantics", summary)
        self.assertEqual(
            report["relationshipResults"]["relationshipResultCount"],
            summary["projectedRelationshipCount"],
        )
        self.assertIn("pass", report["relationshipResults"])
        self.assertIn("review", report["relationshipResults"])

    def test_legacy_single_site_package_supported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = _run_evidence(SAMPLE, Path(directory) / "legacy.json", "REL-LEGACY-001")
        metrics = report["relationshipMetrics"]
        self.assertEqual(metrics["relationshipResultCount"], metrics["canonicalRelationshipCount"])
        self.assertEqual(metrics["unresolvedRelationshipCount"], 0)
        self.assertEqual(report["projectionSummary"]["projectedRelationshipCount"], metrics["relationshipResultCount"])

    def test_deterministic_relationship_metrics(self) -> None:
        report1 = self._multi_site_report("REL-DET-001")
        report2 = self._multi_site_report("REL-DET-001")
        self.assertEqual(report1["relationshipMetrics"], report2["relationshipMetrics"])


if __name__ == "__main__":
    unittest.main()
