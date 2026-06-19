"""Focused tests for the canonical Asset Graph foundation."""
from __future__ import annotations

import dataclasses
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.asset_graph import (
    ASSET_GRAPH_OWNER, AssetGraphValidationError, AssetRelationship,
    AuditEventDescription, Device, DeviceQuery, GlobalId,
    InMemoryAssetGraphProvider, LifecycleStatus, OperationalStatus, Point,
    PointAccessMode, PointQuery, RelationshipQuery, RelationshipType, SiteId,
    SourceIdentity, SourceObjectId, SourceSystemId, Tag, TagQuery, TagType,
    TenantId,
)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def source(object_id="legacy-1", namespace="legacy.iot"):
    return SourceIdentity(
        SourceSystemId("legacy-ibms"), SourceObjectId(object_id),
        "Device", namespace, external_tag_name=f"tag-{object_id}",
    )


def device(gid="device-1", tenant="tenant-1", site="site-1", identities=None, **changes):
    values = dict(
        global_id=GlobalId(gid), tenant_id=TenantId(tenant), site_id=SiteId(site),
        asset_id=GlobalId("asset-1"), display_name="Chiller Controller",
        description="Canonical identity only", device_type="CONTROLLER",
        manufacturer="Example", model="C1", serial_number="SER-1",
        lifecycle_status=LifecycleStatus.ACTIVE.value,
        operational_status=OperationalStatus.AVAILABLE.value,
        classification_ids=("class-hvac",), source_identities=tuple(identities or [source()]),
        created_at=NOW, updated_at=NOW, contract_version="1.0.0",
        metadata_classification="INTERNAL",
    )
    values.update(changes)
    return Device(**values)


def point(gid="point-1", device_id="device-1", tenant="tenant-1", site="site-1", identities=None, **changes):
    values = dict(
        global_id=GlobalId(gid), tenant_id=TenantId(tenant), site_id=SiteId(site),
        device_id=GlobalId(device_id), display_name="Supply Temperature",
        point_type="TEMPERATURE", unit="Cel", data_type="NUMBER",
        access_mode=PointAccessMode.READ_ONLY.value,
        lifecycle_status=LifecycleStatus.ACTIVE.value,
        classification_ids=("class-temperature",),
        source_identities=tuple(identities or [source("field-1", "legacy.fields")]),
        created_at=NOW, updated_at=NOW, contract_version="1.0.0",
        metadata_classification="INTERNAL",
    )
    values.update(changes)
    return Point(**values)


def tag(tag_id="tag-1", object_id="device-1", value="AHU-01", **changes):
    values = dict(
        tag_id=GlobalId(tag_id), tenant_id=TenantId("tenant-1"), site_id=SiteId("site-1"),
        canonical_object_id=GlobalId(object_id), tag_type=TagType.SOURCE_TAG_NAME.value,
        value=value, source_system_id=SourceSystemId("legacy-ibms"),
        source_namespace="legacy.tags", contract_version="1.0.0",
    )
    values.update(changes)
    return Tag(**values)


def relationship(rid="rel-1", source_id="device-1", target_id="point-1", **changes):
    values = dict(
        relationship_id=GlobalId(rid), tenant_id=TenantId("tenant-1"),
        site_id=SiteId("site-1"), relationship_type=RelationshipType.HAS_POINT.value,
        source_global_id=GlobalId(source_id), target_global_id=GlobalId(target_id),
        lifecycle_status=LifecycleStatus.ACTIVE.value, valid_from=NOW,
        valid_to=None, contract_version="1.0.0",
    )
    values.update(changes)
    return AssetRelationship(**values)


class TestCanonicalModels(unittest.TestCase):
    def test_valid_device(self): self.assertEqual(device().display_name, "Chiller Controller")
    def test_valid_point(self): self.assertEqual(point().device_id, GlobalId("device-1"))
    def test_valid_tag(self): self.assertEqual(tag().tag_type, "SOURCE_TAG_NAME")
    def test_valid_relationship(self): self.assertEqual(relationship().relationship_type, "HAS_POINT")

    def test_models_are_immutable(self):
        for value in (device(), point(), tag(), relationship()):
            with self.assertRaises(dataclasses.FrozenInstanceError):
                value.contract_version = "2.0.0"

    def test_deterministic_serialization(self):
        self.assertEqual(device().serialize(), device().serialize())
        self.assertIn("2026-01-01T00:00:00.000000Z", device().serialize())

    def test_secret_like_device_field_rejected(self):
        with self.assertRaisesRegex(AssetGraphValidationError, "prohibited field"):
            Device.from_mapping({"private_key": "forbidden"})

    def test_protocol_credential_rejected(self):
        with self.assertRaisesRegex(AssetGraphValidationError, "prohibited field"):
            Device.from_mapping({"connect_config": {"password": "forbidden"}})

    def test_point_rejects_live_telemetry_storage(self):
        with self.assertRaisesRegex(AssetGraphValidationError, "prohibited field"):
            Point.from_mapping({"live_value": 42})

    def test_duplicate_source_identity_in_object_rejected(self):
        identity = source()
        with self.assertRaisesRegex(AssetGraphValidationError, "duplicate source identity"):
            device(identities=[identity, identity])

    def test_self_relationship_rejected(self):
        with self.assertRaisesRegex(AssetGraphValidationError, "self relationship"):
            relationship(source_id="device-1", target_id="device-1")

    def test_lifecycle_separate_from_operational_status(self):
        value = device(
            lifecycle_status=LifecycleStatus.ACTIVE.value,
            operational_status=OperationalStatus.MAINTENANCE.value,
        )
        self.assertNotEqual(value.lifecycle_status, value.operational_status)

    def test_tag_does_not_replace_identity(self):
        value = tag()
        self.assertNotEqual(value.tag_id, value.canonical_object_id)
        self.assertEqual(value.canonical_object_id, GlobalId("device-1"))

    def test_audit_record_ownership_is_external(self):
        hook = AuditEventDescription(
            "CANONICAL_OBJECT_CREATE", "device.create", "Device",
            GlobalId("device-1"), TenantId("tenant-1"), SiteId("site-1"),
        )
        self.assertEqual(ASSET_GRAPH_OWNER, "ONE Asset Graph")
        self.assertFalse(hasattr(hook, "audit_record"))


class TestInMemoryProvider(unittest.TestCase):
    def setUp(self):
        self.provider = InMemoryAssetGraphProvider()
        self.assertTrue(self.provider.add_device(device()).accepted)

    def test_identical_device_duplicate_idempotent(self):
        result = self.provider.add_device(device())
        self.assertTrue(result.accepted); self.assertTrue(result.duplicate)
        self.assertEqual(result.status, "DUPLICATE_IDENTICAL")

    def test_conflicting_device_duplicate(self):
        result = self.provider.add_device(device(display_name="Different"))
        self.assertFalse(result.accepted); self.assertEqual(result.status, "CONFLICT")

    def test_device_source_identity_conflict(self):
        result = self.provider.add_device(device(gid="device-2"))
        self.assertEqual(result.error_code, "SOURCE_IDENTITY_CONFLICT")

    def test_identical_point_duplicate(self):
        self.assertTrue(self.provider.add_point(point()).accepted)
        result = self.provider.add_point(point())
        self.assertTrue(result.duplicate); self.assertEqual(result.status, "DUPLICATE_IDENTICAL")

    def test_point_source_identity_conflict(self):
        self.provider.add_point(point())
        result = self.provider.add_point(point(gid="point-2"))
        self.assertEqual(result.error_code, "SOURCE_IDENTITY_CONFLICT")

    def test_point_belongs_to_one_device(self):
        self.provider.add_device(device(gid="device-2", identities=[source("legacy-2")]))
        self.provider.add_point(point())
        result = self.provider.add_point(point(gid="point-1", device_id="device-2"))
        self.assertEqual(result.status, "CONFLICT")

    def test_tenant_mismatch_rejected(self):
        result = self.provider.add_point(point(tenant="tenant-2"))
        self.assertEqual(result.error_code, "DEVICE_SCOPE_MISMATCH")

    def test_site_mismatch_rejected(self):
        result = self.provider.add_point(point(site="site-2"))
        self.assertEqual(result.error_code, "DEVICE_SCOPE_MISMATCH")

    def test_duplicate_active_relationship_rejected(self):
        self.provider.add_point(point())
        self.assertTrue(self.provider.add_relationship(relationship()).accepted)
        result = self.provider.add_relationship(relationship(rid="rel-2"))
        self.assertEqual(result.error_code, "ACTIVE_RELATIONSHIP_CONFLICT")

    def test_has_point_validation(self):
        self.provider.add_device(device(gid="device-2", identities=[source("legacy-2")]))
        result = self.provider.add_relationship(relationship(target_id="device-2"))
        self.assertEqual(result.error_code, "HAS_POINT_TYPE_MISMATCH")

    def test_device_query_by_tenant_and_site(self):
        self.provider.add_device(device(gid="device-2", site="site-2", identities=[source("legacy-2")]))
        rows = self.provider.query_devices(DeviceQuery("tenant-1", site_id="site-1")).items
        self.assertEqual([str(row.global_id) for row in rows], ["device-1"])

    def test_device_query_by_source_identity(self):
        rows = self.provider.query_devices(DeviceQuery("tenant-1", source_identity=source())).items
        self.assertEqual(len(rows), 1)
        self.assertEqual(self.provider.find_device_by_source_identity(source()), device())

    def test_point_query_by_device(self):
        self.provider.add_point(point())
        rows = self.provider.query_points(PointQuery("tenant-1", device_id="device-1")).items
        self.assertEqual([str(row.global_id) for row in rows], ["point-1"])

    def test_point_query_by_unit_and_type(self):
        self.provider.add_point(point())
        rows = self.provider.query_points(PointQuery("tenant-1", unit="Cel", point_type="TEMPERATURE")).items
        self.assertEqual(len(rows), 1)

    def test_relationship_query(self):
        self.provider.add_point(point()); self.provider.add_relationship(relationship())
        rows = self.provider.query_relationships(RelationshipQuery("tenant-1", relationship_type="HAS_POINT")).items
        self.assertEqual([str(row.relationship_id) for row in rows], ["rel-1"])

    def test_tag_uniqueness_and_query(self):
        self.assertTrue(self.provider.add_tag(tag()).accepted)
        result = self.provider.add_tag(tag(tag_id="tag-2", object_id="device-1"))
        self.assertEqual(result.error_code, "SOURCE_TAG_CONFLICT")
        rows = self.provider.query_tags(TagQuery("tenant-1", canonical_object_id="device-1")).items
        self.assertEqual(len(rows), 1)
        self.provider.add_device(device(gid="device-2", identities=[source("legacy-2")]))
        conflict = self.provider.add_tag(tag(tag_id="tag-3", object_id="device-2"))
        self.assertEqual(conflict.error_code, "SOURCE_TAG_CONFLICT")

    def test_platform_query_may_omit_tenant(self):
        rows = self.provider.query_devices(DeviceQuery(platform_query=True)).items
        self.assertEqual([str(row.global_id) for row in rows], ["device-1"])

    def test_non_platform_query_requires_tenant(self):
        with self.assertRaisesRegex(AssetGraphValidationError, "tenant_id"):
            self.provider.query_devices(DeviceQuery())

    def test_deterministic_query_order(self):
        self.provider.add_device(device(gid="device-0", identities=[source("legacy-0")]))
        rows = self.provider.query_devices(DeviceQuery("tenant-1")).items
        self.assertEqual([str(row.global_id) for row in rows], ["device-0", "device-1"])

    def test_bounded_query_limit_and_cursor(self):
        self.provider.add_device(device(gid="device-2", identities=[source("legacy-2")]))
        first = self.provider.query_devices(DeviceQuery("tenant-1", limit=1))
        self.assertEqual(len(first.items), 1); self.assertIsNotNone(first.next_cursor)
        second = self.provider.query_devices(DeviceQuery("tenant-1", limit=1, cursor=first.next_cursor))
        self.assertEqual(len(second.items), 1)
        with self.assertRaisesRegex(AssetGraphValidationError, "limit"):
            self.provider.query_devices(DeviceQuery("tenant-1", limit=101))

    def test_provider_instance_isolation(self):
        second = InMemoryAssetGraphProvider()
        self.assertIsNone(second.get_device(GlobalId("device-1")))

    def test_no_filesystem_persistence(self):
        with tempfile.TemporaryDirectory() as directory:
            before = set(os.listdir(directory))
            self.provider.add_point(point())
            self.assertEqual(before, set(os.listdir(directory)))

    def test_no_orm_or_edge_runtime_dependency(self):
        import src.asset_graph.in_memory as module
        source_text = Path(module.__file__).read_text(encoding="utf-8")
        self.assertNotIn("sqlalchemy", source_text.lower())
        self.assertNotIn("src.uedge", source_text.lower())
        self.assertNotIn("__tablename__", source_text)

    def test_reset_is_explicit(self):
        self.provider.clear_for_test()
        self.assertIsNone(self.provider.get_device(GlobalId("device-1")))


if __name__ == "__main__":
    unittest.main()
