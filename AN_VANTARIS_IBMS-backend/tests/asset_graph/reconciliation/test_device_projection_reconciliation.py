"""Focused deterministic Device projection reconciliation tests."""
from __future__ import annotations

import dataclasses
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.asset_graph.compatibility import (
    LegacyDeviceReadCompatibilityFacade, LegacyDeviceSnapshot,
    LegacyFieldSnapshot, ProjectionContext,
)
from src.asset_graph.reconciliation import (
    DeviceProjectionReconciliationService, PointClassification,
    ReconciliationInput,
)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def context(**changes):
    values = dict(
        tenant_id="tenant-1", site_id="site-1", source_system_id="legacy-ibms",
        source_namespace="legacy.iot.devices", default_device_type="CONTROLLER",
    )
    values.update(changes)
    return ProjectionContext(**values)


def device(source_id="device-1", **changes):
    values = dict(
        source_id=source_id, device_name=f"Device {source_id}", device_code=f"CODE-{source_id}",
        description="Safe description", manufacturer="Example", model="X1",
        serial_number=f"SER-{source_id}", status=1, created_at=NOW, updated_at=NOW,
    )
    values.update(changes)
    return LegacyDeviceSnapshot(**values)


def field(source_id="field-1", **changes):
    values = dict(
        source_id=source_id, field_code="supply_temperature",
        field_name="Supply Temperature", field_type="float", unit="Cel",
        created_at=NOW, updated_at=NOW,
    )
    values.update(changes)
    return LegacyFieldSnapshot(**values)


def input_for(devices=None, fields=None, ctx=None, version="legacy-device-v1"):
    rows = tuple(devices or (device(),))
    return ReconciliationInput(
        devices=rows, fields_by_device=fields or {},
        context=ctx or context(), mapping_version=version,
    )


class ConstantIdFacade(LegacyDeviceReadCompatibilityFacade):
    @staticmethod
    def _id(kind, projection_context, source_id):
        if kind == "device":
            from src.asset_graph import GlobalId
            return GlobalId("ag-device-collision")
        return LegacyDeviceReadCompatibilityFacade._id(kind, projection_context, source_id)


class TestReconciliation(unittest.TestCase):
    def setUp(self):
        self.service = DeviceProjectionReconciliationService()

    def execute(self, value=None, run_id="run-1"):
        return self.service.reconcile_batch(run_id, value or input_for())

    def record(self, source=None, fields=(), ctx=None, version="legacy-device-v1"):
        return self.service.reconcile_record("run", source or device(), ctx or context(), fields, version)

    def test_valid_single_device_reconciliation(self):
        run = self.execute()
        self.assertEqual(run.summary.projected_records, 1)
        self.assertEqual(run.record_results[0].projection_status, "PROJECTED")

    def test_valid_device_and_points_reconciliation(self):
        run = self.execute(input_for(fields={"device-1": (field(),)}))
        self.assertEqual(run.record_results[0].point_results[0].classification, "PROJECTED_POINT")

    def test_deterministic_input_digest(self):
        self.assertEqual(self.execute(run_id="a").input_digest, self.execute(run_id="b").input_digest)

    def test_deterministic_projection_digest(self):
        self.assertEqual(self.record().projection_digest, self.record().projection_digest)

    def test_deterministic_result_digest(self):
        self.assertEqual(self.execute(run_id="a").result_digest, self.execute(run_id="b").result_digest)

    def test_repeat_run_identical_result(self):
        comparison = self.service.compare_runs(self.execute(run_id="a"), self.execute(run_id="b"))
        self.assertTrue(comparison.identical_except_run_id)

    def test_changed_safe_source_field_changes_projection_digest(self):
        self.assertNotEqual(self.record().projection_digest, self.record(device(description="Changed")).projection_digest)

    def test_prohibited_value_absent_from_digest(self):
        first = self.record({"id": "x", "device_name": "Bad", "private_key": "alpha", "created_at": NOW})
        second = self.record({"id": "x", "device_name": "Bad", "private_key": "beta", "created_at": NOW})
        self.assertEqual(first.projection_digest, second.projection_digest)
        self.assertNotIn("alpha", dataclasses.asdict(first).__str__())

    def test_same_source_gives_same_global_id(self):
        self.assertEqual(self.record().canonical_global_id, self.record().canonical_global_id)

    def test_tenant_changes_global_id(self):
        self.assertNotEqual(self.record(ctx=context(tenant_id="a")).canonical_global_id, self.record(ctx=context(tenant_id="b")).canonical_global_id)

    def test_source_system_changes_global_id(self):
        self.assertNotEqual(self.record(ctx=context(source_system_id="a")).canonical_global_id, self.record(ctx=context(source_system_id="b")).canonical_global_id)

    def test_source_namespace_changes_global_id(self):
        self.assertNotEqual(self.record(ctx=context(source_namespace="a")).canonical_global_id, self.record(ctx=context(source_namespace="b")).canonical_global_id)

    def test_source_identity_collision(self):
        run = self.execute(input_for(devices=(device(), device())))
        dimension = next(item for item in run.dimension_results if item.dimension_id == "SOURCE_IDENTITY_COLLISION")
        self.assertEqual(dimension.status, "COLLISION")

    def test_global_id_collision(self):
        service = DeviceProjectionReconciliationService(ConstantIdFacade())
        run = service.reconcile_batch("run", input_for(devices=(device("a"), device("b"))))
        dimension = next(item for item in run.dimension_results if item.dimension_id == "GLOBAL_ID_COLLISION")
        self.assertTrue(dimension.cutover_blocking)

    def test_missing_required_device_field(self):
        record = self.record(device(device_type=None), ctx=context(default_device_type=None))
        self.assertIn("REQUIRED_DEVICE_TYPE", record.cutover_blockers)

    def test_defaulted_device_field(self):
        self.assertIn("device_type", self.record().defaulted_fields)

    def test_omitted_optional_field(self):
        self.assertIn("protocol", self.record().omitted_fields)

    def test_prohibited_credential_excluded(self):
        record = self.record({"id": "x", "device_name": "Bad", "password": "hidden", "created_at": NOW})
        self.assertIn("password", record.prohibited_fields_detected)

    def test_telemetry_excluded(self):
        record = self.record({"id": "x", "device_name": "Bad", "current_value": 4, "created_at": NOW})
        self.assertIn("current_value", record.prohibited_fields_detected)

    def test_lifecycle_mapping_pass(self):
        self.assertEqual(self.service.facade.project_device(device(status=0), context()).canonical_device.lifecycle_status, "ACTIVE")

    def test_unknown_lifecycle_review(self):
        self.assertIn("status", self.record(device(status=99)).review_fields)

    def test_operational_status_mapping_pass(self):
        self.assertEqual(self.service.facade.project_device(device(status=2), context()).canonical_device.operational_status, "DEGRADED")

    def test_point_belongs_to_device(self):
        result = self.record(fields=(field(),)).point_results[0]
        self.assertIsNotNone(result.device_global_id)
        self.assertEqual(result.blockers, ())

    def test_point_missing_device_blocker(self):
        result = self.record(device(device_type=None), fields=(field(),), ctx=context(default_device_type=None))
        self.assertIsNone(result.point_results[0].canonical_global_id)

    def test_point_tenant_mismatch(self):
        result = self.record(device(source_tenant_id="wrong"), fields=(field(),))
        self.assertIn("TENANT_SCOPE_MISMATCH", result.cutover_blockers)

    def test_point_site_mismatch(self):
        result = self.record(device(source_site_id="wrong"), fields=(field(),))
        self.assertIn("SITE_SCOPE_MISMATCH", result.cutover_blockers)

    def test_point_unit_mapping(self):
        self.assertEqual(self.record(fields=(field(),)).point_results[0].unit_status, "PASS")

    def test_point_data_type_mapping(self):
        self.assertEqual(self.record(fields=(field(),)).point_results[0].data_type_status, "PASS")

    def test_point_access_mode_mapping(self):
        self.assertEqual(self.record(fields=(field(),)).point_results[0].access_mode_status, "PASS")

    def test_ambiguous_standard_field_review(self):
        result = self.record(fields=(field(field_type="json"),)).point_results[0]
        self.assertEqual(result.classification, PointClassification.REVIEW_REQUIRED.value)

    def test_configuration_field_not_projected(self):
        result = self.record(fields=(field(is_configuration=True),)).point_results[0]
        self.assertEqual(result.classification, "CONFIGURATION_FIELD")

    def test_prohibited_point_excluded(self):
        result = self.record(fields=({"id": "f", "field_code": "x", "field_name": "X", "field_type": "float", "live_value": 3},)).point_results[0]
        self.assertEqual(result.classification, "EXCLUDED_PROHIBITED")

    def test_tag_duplicate_deduplication(self):
        record = self.record(device(device_code="device-1"))
        self.assertEqual(len(record.tag_keys), len(set(record.tag_keys)))

    def test_tag_conflict(self):
        run = self.execute(input_for(devices=(device("a", device_code="SAME"), device("b", device_code="SAME"))))
        dimension = next(item for item in run.dimension_results if item.dimension_id == "TAG_NAMESPACE_UNIQUENESS")
        self.assertEqual(dimension.status, "COLLISION")

    def test_has_point_completeness(self):
        record = self.record(fields=(field(),))
        self.assertTrue(any(item.relationship_type == "HAS_POINT" and item.status == "PASS" for item in record.relationship_results))

    def test_unresolved_parent_review(self):
        record = self.record(device(parent_reference="legacy-parent"))
        self.assertTrue(any(item.status == "REVIEW_REQUIRED" for item in record.relationship_results))

    def test_relationship_scope_is_preserved(self):
        record = self.record(fields=(field(),))
        self.assertFalse(any(item.cutover_blocking for item in record.relationship_results))

    def test_bounded_batch_size(self):
        with self.assertRaisesRegex(ValueError, "maximum"):
            self.execute(input_for(devices=tuple(device(str(i)) for i in range(101))))

    def test_deterministic_batch_ordering(self):
        run = self.execute(input_for(devices=(device("z"), device("a"))))
        self.assertEqual([item.source_object_id for item in run.record_results], ["a", "z"])

    def test_partial_batch_preserves_valid_results(self):
        run = self.execute(input_for(devices=(device("good"), {"id": "", "device_name": "Bad", "created_at": NOW})))
        self.assertEqual(len(run.record_results), 2)
        self.assertEqual(run.summary.projected_records, 1)

    def test_run_comparison_detects_mapping_change(self):
        left = self.execute()
        right = self.execute(input_for(version="legacy-device-v2"), run_id="right")
        self.assertTrue(self.service.compare_runs(left, right).mapping_version_changed)

    def test_run_comparison_ignores_run_id_only_difference(self):
        self.assertTrue(self.service.compare_runs(self.execute(run_id="a"), self.execute(run_id="b")).identical_except_run_id)

    def test_run_comparison_detects_safe_change(self):
        left = self.execute()
        right = self.execute(input_for(devices=(device(description="changed"),)), run_id="right")
        self.assertEqual(self.service.compare_runs(left, right).projection_digests_changed, ("device-1",))

    def test_field_coverage_calculation(self):
        coverage = self.record().field_coverage
        self.assertEqual(coverage.required_denominator, 5)
        self.assertTrue(coverage.required_field_coverage.endswith("%"))

    def test_field_coverage_denominators_visible(self):
        coverage = self.record().field_coverage
        self.assertGreaterEqual(coverage.safe_source_denominator, coverage.safe_source_numerator)

    def test_blocker_summary(self):
        run = self.execute(input_for(devices=(device(device_type=None),), ctx=context(default_device_type=None)))
        self.assertGreater(run.summary.blocker_count, 0)

    def test_safe_default_not_ready_for_write_cutover(self):
        self.assertEqual(self.execute().cutover_decision, "NOT_READY_FOR_WRITE_CUTOVER")

    def test_unapproved_mapping_version_blocks(self):
        self.assertEqual(self.execute(input_for(version="unapproved")).cutover_decision, "BLOCKED_BY_REVIEW")

    def test_result_models_are_immutable(self):
        with self.assertRaises(dataclasses.FrozenInstanceError):
            self.execute().cutover_decision = "READY_FOR_WRITE_CUTOVER"

    def test_no_legacy_or_asset_graph_writes(self):
        text = (Path(__file__).parents[3] / "src/asset_graph/reconciliation/engine.py").read_text()
        for term in ("db.session", "add_device(", "add_point(", "update_device(", "delete_device("):
            self.assertNotIn(term, text)

    def test_no_database_or_filesystem_persistence(self):
        folder = Path(__file__).parents[3] / "src/asset_graph/reconciliation"
        text = "\n".join(path.read_text() for path in folder.glob("*.py"))
        for term in ("sqlalchemy", "__tablename__", ".jsonl", "write_text(", "open("):
            self.assertNotIn(term.lower(), text.lower())

    def test_no_credentials_in_result(self):
        run = self.execute(input_for(devices=({"id": "x", "device_name": "Bad", "private_key": "super-secret", "created_at": NOW},)))
        self.assertNotIn("super-secret", run.serialize())

    def test_no_telemetry_in_result(self):
        run = self.execute(input_for(devices=({"id": "x", "device_name": "Bad", "live_value": "raw-telemetry-secret", "created_at": NOW},)))
        self.assertNotIn("raw-telemetry-secret", run.serialize())
        self.assertIn("live_value", run.record_results[0].prohibited_fields_detected)

    def test_no_public_api_or_edge_runtime_dependency(self):
        folder = Path(__file__).parents[3] / "src/asset_graph/reconciliation"
        text = "\n".join(path.read_text() for path in folder.glob("*.py")).lower()
        for term in ("blueprint", "@api_bp.route", "src.uedge", "src.iot", "src.link", "src.ufms"):
            self.assertNotIn(term, text)

    def test_reconciliation_reuses_facade(self):
        self.assertIsInstance(self.service.facade, LegacyDeviceReadCompatibilityFacade)

    def test_mapping_logic_not_duplicated(self):
        text = (Path(__file__).parents[3] / "src/asset_graph/reconciliation/engine.py").read_text()
        self.assertNotIn("operational_map =", text)
        self.assertNotIn("field_type_map =", text)


if __name__ == "__main__":
    unittest.main()
