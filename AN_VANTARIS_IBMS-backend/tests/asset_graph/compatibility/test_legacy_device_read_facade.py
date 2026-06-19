"""Focused tests for the READ_ONLY legacy Device compatibility facade."""
from __future__ import annotations

import dataclasses
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.asset_graph.compatibility import (
    FixtureLegacyDeviceReadPort, LegacyDeviceReadCompatibilityFacade,
    LegacyDeviceReadPort, LegacyDeviceSnapshot, LegacyFieldSnapshot,
    LegacyReadQuery, ProjectionCategory, ProjectionContext,
    READ_ONLY_COMPATIBILITY_FACADE, TEMPORARY_LEGACY_SOURCE,
)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def context(**changes):
    values = dict(
        tenant_id="tenant-1", site_id="site-1", source_system_id="legacy-ibms",
        source_namespace="legacy.iot.devices", default_device_type="CONTROLLER",
    )
    values.update(changes)
    return ProjectionContext(**values)


def device(**changes):
    values = dict(
        source_id="legacy-1", device_name="Plant Controller", device_code="PLC-01",
        description="Legacy projection", manufacturer="Example", model="X1",
        serial_number="SER-1", status=1, created_at=NOW, updated_at=NOW,
        source_version="7",
    )
    values.update(changes)
    return LegacyDeviceSnapshot(**values)


def field(**changes):
    values = dict(
        source_id="field-1", field_code="supply_temperature",
        field_name="Supply Temperature", field_type="float", unit="Cel",
        created_at=NOW, updated_at=NOW,
    )
    values.update(changes)
    return LegacyFieldSnapshot(**values)


class TestFacade(unittest.TestCase):
    def setUp(self):
        self.facade = LegacyDeviceReadCompatibilityFacade()

    def project(self, record=None, ctx=None, fields=()):
        return self.facade.project_device(record or device(), ctx or context(), fields)

    def test_valid_device_projection(self):
        result = self.project()
        self.assertTrue(result.accepted)
        self.assertEqual(result.category, ProjectionCategory.PROJECTED.value)

    def test_deterministic_global_id(self):
        self.assertEqual(
            self.project().canonical_device.global_id,
            self.project().canonical_device.global_id,
        )

    def test_tenant_separation(self):
        self.assertNotEqual(
            self.project(ctx=context(tenant_id="a")).canonical_device.global_id,
            self.project(ctx=context(tenant_id="b")).canonical_device.global_id,
        )

    def test_source_system_separation(self):
        self.assertNotEqual(
            self.project(ctx=context(source_system_id="a")).canonical_device.global_id,
            self.project(ctx=context(source_system_id="b")).canonical_device.global_id,
        )

    def test_source_identity_creation(self):
        identity = self.project().source_identity
        self.assertEqual(str(identity.source_object_id), "legacy-1")
        self.assertEqual(identity.external_tag_name, "PLC-01")

    def test_missing_source_id_rejection(self):
        result = self.facade.project_device(
            {"id": "", "device_name": "Bad", "created_at": NOW},
            context(),
        )
        self.assertFalse(result.accepted)

    def test_missing_tenant_rejection(self):
        result = self.project(ctx=context(tenant_id=""))
        self.assertEqual(result.error_code, "MISSING_TENANT")

    def test_display_name_mapping(self):
        self.assertEqual(self.project().canonical_device.display_name, "Plant Controller")

    def test_manufacturer_model_serial_mapping(self):
        projected = self.project().canonical_device
        self.assertEqual((projected.manufacturer, projected.model, projected.serial_number), ("Example", "X1", "SER-1"))

    def test_lifecycle_mapping(self):
        self.assertEqual(self.project().canonical_device.lifecycle_status, "ACTIVE")

    def test_operational_status_mapping(self):
        for status, expected in ((0, "UNAVAILABLE"), (1, "AVAILABLE"), (2, "DEGRADED")):
            self.assertEqual(self.project(device(status=status)).canonical_device.operational_status, expected)

    def test_unknown_status_behavior(self):
        result = self.project(device(status=99))
        self.assertEqual(result.canonical_device.operational_status, "UNKNOWN")
        self.assertEqual(result.category, "PROJECTED_WITH_WARNINGS")

    def test_password_excluded(self):
        result = self.facade.project_device(
            {"id": "1", "device_name": "Bad", "password": "hidden", "created_at": NOW},
            context(),
        )
        self.assertEqual(result.category, "PROHIBITED_FIELD_REJECTED")

    def test_token_excluded(self):
        result = self.facade.project_device(
            {"id": "1", "device_name": "Bad", "bearer_token": "hidden", "created_at": NOW},
            context(),
        )
        self.assertEqual(result.category, "PROHIBITED_FIELD_REJECTED")

    def test_private_key_excluded(self):
        result = self.facade.project_device(
            {"id": "1", "device_name": "Bad", "private_key": "hidden", "created_at": NOW},
            context(),
        )
        self.assertEqual(result.category, "PROHIBITED_FIELD_REJECTED")

    def test_connection_credential_excluded(self):
        result = self.facade.project_device(
            {"id": "1", "device_name": "Bad", "connect_config": {"password": "x"}, "created_at": NOW},
            context(),
        )
        self.assertEqual(result.category, "PROHIBITED_FIELD_REJECTED")

    def test_current_telemetry_value_excluded(self):
        result = self.facade.project_device(
            {"id": "1", "device_name": "Bad", "current_value": 4, "created_at": NOW},
            context(),
        )
        self.assertEqual(result.category, "PROHIBITED_FIELD_REJECTED")

    def test_protocol_runtime_state_excluded(self):
        result = self.facade.project_device(
            {"id": "1", "device_name": "Bad", "runtime_state": "connected", "created_at": NOW},
            context(),
        )
        self.assertEqual(result.category, "PROHIBITED_FIELD_REJECTED")

    def test_valid_point_projection(self):
        result = self.project(fields=(field(),))
        self.assertEqual(len(result.canonical_points), 1)
        self.assertEqual(result.canonical_points[0].point_type, "SUPPLY_TEMPERATURE")

    def test_point_references_device(self):
        result = self.project(fields=(field(),))
        self.assertEqual(result.canonical_points[0].device_id, result.canonical_device.global_id)

    def test_point_excludes_live_value(self):
        result = self.project(fields=({"id": "f", "field_code": "x", "field_name": "X", "field_type": "float", "live_value": 9},))
        self.assertEqual(result.reviews, ("PROHIBITED_FIELD_REJECTED",))
        self.assertEqual(result.canonical_points, ())

    def test_ambiguous_field_review(self):
        result = self.project(fields=(field(field_type="json"),))
        self.assertIn("AMBIGUOUS_FIELD:field-1", result.reviews)

    def test_valid_source_tag_projection(self):
        tags = self.project().canonical_tags
        self.assertTrue(any(item.tag_type == "SOURCE_TAG_NAME" and item.value == "PLC-01" for item in tags))

    def test_duplicate_tag_deduplication(self):
        result = self.project(device(device_code="legacy-1"))
        pairs = {(item.tag_type, item.value) for item in result.canonical_tags}
        self.assertEqual(len(pairs), len(result.canonical_tags))

    def test_credential_like_tag_rejection(self):
        result = self.project(device(device_code="password=oops"))
        self.assertEqual(result.category, "PROHIBITED_FIELD_REJECTED")
        self.assertNotIn("oops", result.serialize())

    def test_has_point_relationship(self):
        result = self.project(fields=(field(),))
        self.assertTrue(any(item.relationship_type == "HAS_POINT" for item in result.relationships))

    def test_unresolved_parent_relationship_review(self):
        result = self.project(device(parent_reference="legacy-parent"))
        self.assertEqual(result.unresolved_relationships[0].relationship_type, "LOCATED_IN")
        self.assertEqual(result.category, "REVIEW_REQUIRED")

    def test_resolved_parent_relationship(self):
        result = self.project(ctx=context(parent_asset_id="asset-1"))
        self.assertTrue(any(item.relationship_type == "LOCATED_IN" for item in result.relationships))

    def test_deterministic_serialization(self):
        self.assertEqual(self.project().serialize(), self.project().serialize())

    def test_deterministic_batch_ordering(self):
        batch = self.facade.project_devices((device(source_id="z"), device(source_id="a")), context())
        ids = [str(item.source_identity.source_object_id) for item in batch.results]
        self.assertEqual(ids, ["a", "z"])

    def test_bounded_batch_size(self):
        with self.assertRaisesRegex(ValueError, "maximum"):
            self.facade.project_devices(tuple(device(source_id=str(i)) for i in range(101)), context())

    def test_duplicate_source_identity_conflict(self):
        batch = self.facade.project_devices((device(), device()), context())
        self.assertEqual(batch.results[1].category, "IDENTITY_CONFLICT")

    def test_duplicate_point_source_identity_review(self):
        result = self.project(fields=(field(), field(field_name="Duplicate")))
        self.assertEqual(len(result.canonical_points), 1)
        self.assertIn("POINT_SOURCE_IDENTITY_CONFLICT:field-1", result.reviews)

    def test_invalid_batch_record_does_not_remove_valid_result(self):
        batch = self.facade.project_devices(
            (device(source_id="good"), {"id": "", "device_name": "Bad", "created_at": NOW}),
            context(),
        )
        self.assertEqual(len(batch.results), 2)
        self.assertEqual(sum(item.accepted for item in batch.results), 1)

    def test_tenant_mismatch(self):
        result = self.project(device(source_tenant_id="tenant-2"))
        self.assertEqual(result.category, "SCOPE_MISMATCH")

    def test_site_mismatch(self):
        result = self.project(device(source_site_id="site-2"))
        self.assertEqual(result.category, "SCOPE_MISMATCH")

    def test_models_are_immutable(self):
        with self.assertRaises(dataclasses.FrozenInstanceError):
            device().device_name = "changed"

    def test_fixture_read_port_is_read_only(self):
        port = FixtureLegacyDeviceReadPort((device(),), {"legacy-1": (field(),)})
        self.assertIsInstance(port, LegacyDeviceReadPort)
        self.assertFalse(any(hasattr(port, name) for name in ("add", "create", "update", "delete", "save")))
        self.assertEqual(port.get_legacy_device_by_id("legacy-1", "tenant-1"), device())

    def test_fixture_read_port_is_bounded(self):
        port = FixtureLegacyDeviceReadPort((device(),))
        with self.assertRaises(ValueError):
            port.list_legacy_devices(LegacyReadQuery("tenant-1", limit=101))

    def test_no_asset_graph_provider_writes(self):
        source = Path(__file__).parents[3] / "src/asset_graph/compatibility/facade.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("add_device(", text)
        self.assertNotIn("add_point(", text)

    def test_no_legacy_model_writes_or_imports(self):
        source = Path(__file__).parents[3] / "src/asset_graph/compatibility"
        text = "\n".join(path.read_text(encoding="utf-8") for path in source.glob("*.py"))
        self.assertNotIn("src.Iot", text)
        self.assertNotIn("db.session", text)

    def test_no_orm_persistence_declaration(self):
        source = Path(__file__).parents[3] / "src/asset_graph/compatibility"
        text = "\n".join(path.read_text(encoding="utf-8") for path in source.glob("*.py"))
        self.assertNotIn("__tablename__", text)
        self.assertNotIn("sqlalchemy", text.lower())

    def test_no_public_api(self):
        source = Path(__file__).parents[3] / "src/asset_graph/compatibility"
        text = "\n".join(path.read_text(encoding="utf-8") for path in source.glob("*.py"))
        self.assertNotIn("Blueprint", text)
        self.assertNotIn("@api_bp.route", text)

    def test_no_edge_runtime_import(self):
        source = Path(__file__).parents[3] / "src/asset_graph/compatibility"
        text = "\n".join(path.read_text(encoding="utf-8") for path in source.glob("*.py"))
        self.assertNotIn("src.uedge", text.lower())
        self.assertNotIn("src.iot", text.lower())

    def test_projection_result_never_leaks_prohibited_values(self):
        result = self.facade.project_device(
            {"id": "1", "device_name": "Bad", "private_key": "super-secret-value", "created_at": NOW},
            context(),
        )
        self.assertNotIn("super-secret-value", result.serialize())

    def test_boundary_markers(self):
        self.assertEqual(self.facade.boundary, READ_ONLY_COMPATIBILITY_FACADE)
        self.assertEqual(self.facade.source_ownership, TEMPORARY_LEGACY_SOURCE)

    def test_audit_metadata_is_description_only(self):
        metadata = self.project().audit_metadata
        self.assertEqual(metadata.source_model, "IMSDevice")
        self.assertFalse(hasattr(metadata, "audit_record"))


if __name__ == "__main__":
    unittest.main()
