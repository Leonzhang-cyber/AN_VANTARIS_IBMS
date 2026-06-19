"""Tests for bounded multi-site reconciliation context."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.asset_graph.compatibility import LegacyDeviceReadCompatibilityFacade, ProjectionContext
from src.asset_graph.compatibility.models import LegacyDeviceSnapshot
from src.asset_graph.reconciliation.evidence.excel.converter import convert_workbook_rows
from src.asset_graph.reconciliation.evidence.excel.workbook import ExcelWorkbook
from src.asset_graph.reconciliation.evidence.runner import run_device_reconciliation_evidence
from src.asset_graph.reconciliation.site_context import (
    MULTI_SITE_DECLARED,
    SINGLE_SITE_STRICT,
    SiteContextError,
    collect_scope_metrics,
    parse_site_context,
)

ROOT = Path(__file__).resolve().parents[4]
SAMPLE = ROOT / "AN_VANTARIS_ONE/evidence/device-reconciliation/sample/minimal-valid-device.json"
FIXTURES = Path(__file__).resolve().parent / "evidence/excel/fixtures.py"


def _base_package() -> dict:
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def _device(source_id: str, *, site_id: str = "site-sample-a", tenant_id: str = "tenant-sample-a") -> dict:
    return {
        "sourceId": source_id,
        "sourceNamespace": "legacy.iot.devices",
        "tenantId": tenant_id,
        "siteId": site_id,
        "name": f"Device {source_id}",
        "deviceType": "CONTROLLER",
        "operationalStatus": "AVAILABLE",
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
        "approvedMetadata": {},
    }


class TestSiteContextParsing(unittest.TestCase):
    def test_legacy_site_id_context_remains_strict(self) -> None:
        ctx = parse_site_context({"siteId": "SITE-001"}, tenant_id="tenant-a")
        self.assertEqual(ctx.site_scope_mode, SINGLE_SITE_STRICT)
        self.assertEqual(ctx.site_id, "SITE-001")
        self.assertEqual(ctx.allowed_site_ids, ("SITE-001",))
        self.assertTrue(ctx.allows_record_site("SITE-001"))
        self.assertFalse(ctx.allows_record_site("SITE-002"))

    def test_explicit_single_site_strict(self) -> None:
        ctx = parse_site_context(
            {"mode": SINGLE_SITE_STRICT, "siteId": "SITE-001"},
            tenant_id="tenant-a",
        )
        self.assertEqual(ctx.site_scope_mode, SINGLE_SITE_STRICT)
        self.assertFalse(ctx.allows_record_site("SITE-002"))

    def test_valid_multi_site_declared(self) -> None:
        ctx = parse_site_context(
            {
                "mode": MULTI_SITE_DECLARED,
                "primarySiteId": "SITE-001",
                "allowedSiteIds": ["SITE-003", "SITE-001", "SITE-002"],
            },
            tenant_id="tenant-a",
        )
        self.assertEqual(ctx.site_scope_mode, MULTI_SITE_DECLARED)
        self.assertEqual(ctx.primary_site_id, "SITE-001")
        self.assertEqual(ctx.allowed_site_ids, ("SITE-001", "SITE-002", "SITE-003"))

    def test_empty_allowed_site_ids_rejected(self) -> None:
        with self.assertRaises(SiteContextError):
            parse_site_context(
                {"mode": MULTI_SITE_DECLARED, "primarySiteId": "SITE-001", "allowedSiteIds": []},
                tenant_id="tenant-a",
            )

    def test_duplicate_allowed_site_rejected(self) -> None:
        with self.assertRaises(SiteContextError):
            parse_site_context(
                {
                    "mode": MULTI_SITE_DECLARED,
                    "primarySiteId": "SITE-001",
                    "allowedSiteIds": ["SITE-001", "SITE-001"],
                },
                tenant_id="tenant-a",
            )

    def test_more_than_100_sites_rejected(self) -> None:
        with self.assertRaises(SiteContextError):
            parse_site_context(
                {
                    "mode": MULTI_SITE_DECLARED,
                    "primarySiteId": "SITE-000",
                    "allowedSiteIds": [f"SITE-{index:03d}" for index in range(101)],
                },
                tenant_id="tenant-a",
            )

    def test_primary_site_missing_rejected(self) -> None:
        with self.assertRaises(SiteContextError):
            parse_site_context(
                {"mode": MULTI_SITE_DECLARED, "allowedSiteIds": ["SITE-001"]},
                tenant_id="tenant-a",
            )

    def test_primary_site_outside_allowed_list_rejected(self) -> None:
        with self.assertRaises(SiteContextError):
            parse_site_context(
                {
                    "mode": MULTI_SITE_DECLARED,
                    "primarySiteId": "SITE-999",
                    "allowedSiteIds": ["SITE-001", "SITE-002"],
                },
                tenant_id="tenant-a",
            )

    def test_unsupported_mode_rejected(self) -> None:
        for mode in ("ALL_SITES", "ANY_SITE", "UNRESTRICTED", "WILDCARD_MODE"):
            with self.subTest(mode=mode):
                with self.assertRaises(SiteContextError):
                    parse_site_context({"mode": mode, "siteId": "SITE-001"}, tenant_id="tenant-a")

    def test_wildcard_rejected(self) -> None:
        with self.assertRaises(SiteContextError):
            parse_site_context({"siteId": "SITE-*"}, tenant_id="tenant-a")

    def test_deterministic_allowed_site_ordering(self) -> None:
        ctx = parse_site_context(
            {
                "mode": MULTI_SITE_DECLARED,
                "primarySiteId": "SITE-B",
                "allowedSiteIds": ["SITE-C", "SITE-A", "SITE-B"],
            },
            tenant_id="tenant-a",
        )
        self.assertEqual(ctx.allowed_site_ids, ("SITE-A", "SITE-B", "SITE-C"))


class TestSiteContextProjection(unittest.TestCase):
    def _run_package(self, package: dict, run_id: str = "SITE-CTX-001") -> dict:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.json"
            output_path = Path(directory) / "output.json"
            input_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            return run_device_reconciliation_evidence(
                root=ROOT,
                input_path=input_path,
                output_path=output_path,
                run_id=run_id,
            )

    def test_record_in_primary_site_projects(self) -> None:
        package = _base_package()
        package["siteContext"] = {
            "mode": MULTI_SITE_DECLARED,
            "primarySiteId": "site-sample-a",
            "allowedSiteIds": ["site-sample-a", "site-sample-b"],
        }
        report = self._run_package(package)
        self.assertEqual(report["projectionSummary"]["projectedDeviceCount"], 1)

    def test_record_in_secondary_declared_site_projects(self) -> None:
        package = _base_package()
        package["devices"] = [_device("dev-secondary", site_id="site-sample-b")]
        package["siteContext"] = {
            "mode": MULTI_SITE_DECLARED,
            "primarySiteId": "site-sample-a",
            "allowedSiteIds": ["site-sample-a", "site-sample-b"],
        }
        report = self._run_package(package)
        self.assertEqual(report["projectionSummary"]["projectedDeviceCount"], 1)

    def test_undeclared_site_rejected(self) -> None:
        package = _base_package()
        package["devices"] = [_device("dev-other", site_id="site-sample-c")]
        package["siteContext"] = {
            "mode": MULTI_SITE_DECLARED,
            "primarySiteId": "site-sample-a",
            "allowedSiteIds": ["site-sample-a", "site-sample-b"],
        }
        report = self._run_package(package)
        self.assertEqual(report["projectionSummary"]["projectedDeviceCount"], 0)
        self.assertIn("SITE_SCOPE_MISMATCH", report["blockers"])

    def test_tenant_mismatch_still_blocked(self) -> None:
        package = _base_package()
        package["devices"] = [_device("dev-tenant", tenant_id="tenant-other")]
        report = self._run_package(package)
        self.assertTrue(any("TENANT" in item for item in report["blockers"]))

    def test_record_site_never_overwritten(self) -> None:
        facade = LegacyDeviceReadCompatibilityFacade()
        context = ProjectionContext(
            tenant_id="tenant-sample-a",
            source_system_id="legacy-ibms",
            source_namespace="legacy.iot.devices",
            site_id="site-sample-a",
            site_scope_mode=MULTI_SITE_DECLARED,
            primary_site_id="site-sample-a",
            allowed_site_ids=("site-sample-a", "site-sample-b"),
            default_device_type="CONTROLLER",
        )
        record = LegacyDeviceSnapshot(
            source_id="dev-site-b",
            device_name="Secondary Site Device",
            device_type="CONTROLLER",
            source_tenant_id="tenant-sample-a",
            source_site_id="site-sample-b",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        result = facade.project_device(record, context)
        self.assertTrue(result.accepted)
        self.assertIsNotNone(result.canonical_device)
        assert result.canonical_device is not None
        self.assertEqual(str(result.canonical_device.site_id), "site-sample-b")

    def test_backward_compatible_evidence_package(self) -> None:
        report = self._run_package(_base_package(), run_id="LEGACY-001")
        self.assertEqual(report["scopeMetrics"]["scopeMode"], SINGLE_SITE_STRICT)
        self.assertEqual(report["projectionSummary"]["projectedDeviceCount"], 1)

    def test_scope_aggregate_counters(self) -> None:
        package = _base_package()
        package["devices"] = [
            _device("dev-a", site_id="site-sample-a"),
            _device("dev-b", site_id="site-sample-b"),
            _device("dev-c", site_id="site-sample-c"),
        ]
        package["siteContext"] = {
            "mode": MULTI_SITE_DECLARED,
            "primarySiteId": "site-sample-a",
            "allowedSiteIds": ["site-sample-a", "site-sample-b"],
        }
        report = self._run_package(package)
        metrics = report["scopeMetrics"]
        self.assertEqual(metrics["scopeMode"], MULTI_SITE_DECLARED)
        self.assertEqual(metrics["allowedSiteCount"], 2)
        self.assertEqual(metrics["recordsInDeclaredSiteScope"], 2)
        self.assertEqual(metrics["recordsOutsideDeclaredSiteScope"], 1)
        self.assertGreaterEqual(metrics["multiSiteUndeclaredSiteCount"], 1)

    def test_deterministic_report_output(self) -> None:
        package = copy.deepcopy(_base_package())
        package["siteContext"] = {
            "mode": MULTI_SITE_DECLARED,
            "primarySiteId": "site-sample-a",
            "allowedSiteIds": ["site-sample-a", "site-sample-b"],
        }
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.json"
            out1 = Path(directory) / "out1.json"
            out2 = Path(directory) / "out2.json"
            input_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            run_device_reconciliation_evidence(root=ROOT, input_path=input_path, output_path=out1, run_id="DET-001")
            run_device_reconciliation_evidence(root=ROOT, input_path=input_path, output_path=out2, run_id="DET-001")
            self.assertEqual(out1.read_bytes(), out2.read_bytes())


class TestExcelMultiSiteContext(unittest.TestCase):
    def test_converter_emits_three_declared_sites(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location("excel_fixtures", FIXTURES)
        fixtures = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(fixtures)
        with tempfile.TemporaryDirectory() as directory:
            workbook_path = Path(directory) / "fixture.xlsx"
            fixtures.write_workbook(workbook_path)
            with ExcelWorkbook.open(workbook_path) as book:
                package = convert_workbook_rows(book.rows("Devices"), book.rows("StandardFields"))
        site_context = package["siteContext"]
        self.assertEqual(site_context["mode"], MULTI_SITE_DECLARED)
        self.assertEqual(site_context["primarySiteId"], "SYNTH-SITE-001")
        self.assertEqual(
            site_context["allowedSiteIds"],
            ["SYNTH-SITE-001", "SYNTH-SITE-002", "SYNTH-SITE-003"],
        )
        self.assertNotIn("SYNTH-SITE-MISMATCH", site_context["allowedSiteIds"])

    def test_intentional_mismatch_site_remains_blocked(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location("excel_fixtures", FIXTURES)
        fixtures = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(fixtures)
        with tempfile.TemporaryDirectory() as directory:
            workbook_path = Path(directory) / "fixture.xlsx"
            fixtures.write_workbook(workbook_path)
            with ExcelWorkbook.open(workbook_path) as book:
                package = convert_workbook_rows(book.rows("Devices"), book.rows("StandardFields"))
            input_path = Path(directory) / "package.json"
            report_path = Path(directory) / "report.json"
            input_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            report = run_device_reconciliation_evidence(
                root=ROOT,
                input_path=input_path,
                output_path=report_path,
                run_id="MISMATCH-001",
            )
        self.assertIn("SITE_SCOPE_MISMATCH", report["blockers"])


class TestCollectScopeMetrics(unittest.TestCase):
    def test_collect_scope_metrics_shape(self) -> None:
        context = parse_site_context({"siteId": "SITE-001"}, tenant_id="tenant-a")
        context = context.__class__(
            tenant_id="tenant-a",
            source_system_id="legacy",
            source_namespace="legacy.iot.devices",
            site_id=context.site_id,
            site_scope_mode=context.site_scope_mode,
            primary_site_id=context.primary_site_id,
            allowed_site_ids=context.allowed_site_ids,
        )
        metrics = collect_scope_metrics(
            context,
            [{"siteId": "SITE-001"}, {"siteId": "SITE-002"}],
            [{"code": "SITE_SCOPE_MISMATCH"}],
            [],
        )
        for key in (
            "scopeMode",
            "primarySiteIdDeclared",
            "allowedSiteCount",
            "recordsInDeclaredSiteScope",
            "recordsOutsideDeclaredSiteScope",
            "singleSiteMismatchCount",
            "multiSiteUndeclaredSiteCount",
            "tenantMismatchCount",
            "siteScopePassCount",
            "siteScopeBlockerCount",
        ):
            self.assertIn(key, metrics)


if __name__ == "__main__":
    unittest.main()
