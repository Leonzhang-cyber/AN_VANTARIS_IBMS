"""Focused tests for the Governance Audit Provider foundation."""
from __future__ import annotations

import dataclasses
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from src.governance.audit import (
    AuditProvider,
    AuditQuery,
    AuditRecord,
    AuditService,
    AuditValidationError,
    InMemoryAuditProvider,
)


def make_record(**overrides) -> AuditRecord:
    value = {
        "audit_id": "audit-001",
        "event_class": "CANONICAL_OBJECT_UPDATE",
        "action": "asset.update",
        "occurred_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "actor_type": "USER",
        "actor_id": "user-001",
        "service_identity_id": None,
        "tenant_id": "tenant-001",
        "site_id": "site-001",
        "subject_type": "Asset",
        "subject_id": "asset-001",
        "target_type": "Asset",
        "target_id": "asset-001",
        "route_id": "ROUTE-PATCH-ASSET",
        "request_id": "request-001",
        "trace_id": "trace-001",
        "correlation_id": "correlation-001",
        "permission": "asset:update",
        "package_id": "PKG-ASSET-GRAPH",
        "outcome": "SUCCESS",
        "denial_code": None,
        "reason_code": "USER_REQUEST",
        "previous_state_digest": "a" * 64,
        "resulting_state_digest": "b" * 64,
        "source_ip_class": "PRIVATE_NETWORK",
        "user_agent_class": "BROWSER",
        "contract_version": "1.0.0",
        "metadata_classification": "INTERNAL",
        "evidence_reference_ids": ("evidence-ref-001",),
    }
    value.update(overrides)
    return AuditRecord(**value)


class FailingProvider(AuditProvider):
    def emit(self, record, failure_policy):
        raise RuntimeError("storage details must remain hidden")

    def get_by_id(self, audit_id):
        return None

    def query(self, query_spec):
        raise RuntimeError("not used")


class TestAuditRecord(unittest.TestCase):
    def test_valid_record(self):
        record = AuditRecord.from_mapping(make_record().to_dict() | {
            "occurred_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        })
        self.assertEqual(record.audit_id, "audit-001")

    def test_immutable(self):
        with self.assertRaises(dataclasses.FrozenInstanceError):
            make_record().action = "changed"

    def test_deterministic_serialization(self):
        record = make_record()
        self.assertEqual(record.serialize(), record.serialize())
        self.assertIn('"occurred_at":"2026-01-01T00:00:00.000000Z"', record.serialize())

    def test_prohibited_password_field(self):
        with self.assertRaisesRegex(AuditValidationError, "prohibited secret-like field"):
            AuditRecord.from_mapping(make_record().to_dict() | {"password": "never-log"})

    def test_prohibited_bearer_token_field(self):
        with self.assertRaisesRegex(AuditValidationError, "prohibited secret-like field"):
            AuditRecord.from_mapping(make_record().to_dict() | {"bearer_token": "never-log"})

    def test_prohibited_private_key_field(self):
        with self.assertRaisesRegex(AuditValidationError, "prohibited secret-like field"):
            AuditRecord.from_mapping(make_record().to_dict() | {"private_key": "never-log"})

    def test_invalid_event_class(self):
        with self.assertRaisesRegex(AuditValidationError, "event_class"):
            AuditRecord.from_mapping(make_record(event_class="PRIVATE_EVENT").to_dict() | {
                "occurred_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            })

    def test_actor_identity_validation(self):
        service = make_record(actor_type="SERVICE_IDENTITY", actor_id=None, service_identity_id=None)
        with self.assertRaisesRegex(AuditValidationError, "service_identity_id"):
            AuditService(InMemoryAuditProvider()).emit(service)

    def test_tenant_and_site_validation(self):
        with self.assertRaisesRegex(AuditValidationError, "tenant_id"):
            AuditService(InMemoryAuditProvider()).emit(make_record(tenant_id=None))
        with self.assertRaisesRegex(AuditValidationError, "site_id"):
            AuditService(InMemoryAuditProvider()).emit(make_record(site_id=None))

    def test_raw_state_rejected(self):
        with self.assertRaisesRegex(AuditValidationError, "digest"):
            AuditService(InMemoryAuditProvider()).emit(make_record(previous_state_digest='{"status":"raw"}'))

    def test_evidence_separation(self):
        record = make_record()
        self.assertFalse(hasattr(record, "evidence_record"))
        self.assertEqual(record.evidence_reference_ids, ("evidence-ref-001",))


class TestInMemoryAuditProvider(unittest.TestCase):
    def setUp(self):
        self.provider = InMemoryAuditProvider()
        self.service = AuditService(self.provider)

    def test_emit_success(self):
        result = self.service.emit(make_record())
        self.assertTrue(result.accepted)
        self.assertFalse(result.duplicate)
        self.assertEqual(result.provider_status, "NON_PRODUCTION_IN_MEMORY_PROVIDER")

    def test_identical_duplicate_is_idempotent(self):
        first = self.service.emit(make_record())
        second = self.service.emit(make_record())
        self.assertTrue(first.accepted)
        self.assertTrue(second.accepted)
        self.assertTrue(second.duplicate)

    def test_conflicting_duplicate_is_rejected(self):
        self.service.emit(make_record())
        result = self.service.emit(make_record(action="asset.retire"))
        self.assertFalse(result.accepted)
        self.assertTrue(result.duplicate)
        self.assertEqual(result.error_code, "AUDIT_ID_CONFLICT")

    def test_get_by_id(self):
        record = make_record()
        self.service.emit(record)
        self.assertEqual(self.service.get_by_id(record.audit_id), record)

    def test_tenant_scoped_query(self):
        self.service.emit(make_record(audit_id="a-1", tenant_id="tenant-1"))
        self.service.emit(make_record(audit_id="a-2", tenant_id="tenant-2"))
        result = self.service.query(AuditQuery(tenant_id="tenant-1"))
        self.assertEqual([row.audit_id for row in result.records], ["a-1"])

    def test_site_scoped_query(self):
        self.service.emit(make_record(audit_id="a-1", site_id="site-1"))
        self.service.emit(make_record(audit_id="a-2", site_id="site-2"))
        result = self.service.query(AuditQuery(tenant_id="tenant-001", site_id="site-2"))
        self.assertEqual([row.audit_id for row in result.records], ["a-2"])

    def test_event_class_query(self):
        self.service.emit(make_record(audit_id="a-1"))
        self.service.emit(make_record(
            audit_id="a-2", event_class="SENSITIVE_READ", site_id=None,
        ))
        result = self.service.query(AuditQuery(
            tenant_id="tenant-001", event_class="SENSITIVE_READ",
        ))
        self.assertEqual([row.audit_id for row in result.records], ["a-2"])

    def test_correlation_query(self):
        self.service.emit(make_record(audit_id="a-1", correlation_id="flow-1"))
        self.service.emit(make_record(audit_id="a-2", correlation_id="flow-2"))
        result = self.service.query(AuditQuery(
            tenant_id="tenant-001", correlation_id="flow-2",
        ))
        self.assertEqual([row.audit_id for row in result.records], ["a-2"])

    def test_deterministic_query_order(self):
        time = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.service.emit(make_record(audit_id="b", occurred_at=time))
        self.service.emit(make_record(audit_id="a", occurred_at=time))
        self.service.emit(make_record(audit_id="c", occurred_at=time + timedelta(seconds=1)))
        result = self.service.query(AuditQuery(tenant_id="tenant-001"))
        self.assertEqual([row.audit_id for row in result.records], ["a", "b", "c"])

    def test_bounded_query_limit_and_cursor(self):
        for number in range(3):
            self.service.emit(make_record(
                audit_id=f"a-{number}",
                occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=number),
            ))
        first = self.service.query(AuditQuery(tenant_id="tenant-001", limit=2))
        self.assertEqual(len(first.records), 2)
        self.assertIsNotNone(first.next_cursor)
        second = self.service.query(AuditQuery(
            tenant_id="tenant-001", limit=2, cursor=first.next_cursor,
        ))
        self.assertEqual([row.audit_id for row in second.records], ["a-2"])
        with self.assertRaisesRegex(AuditValidationError, "limit"):
            self.service.query(AuditQuery(tenant_id="tenant-001", limit=101))

    def test_platform_query_must_be_explicit(self):
        with self.assertRaisesRegex(AuditValidationError, "tenant_id"):
            self.service.query(AuditQuery())
        self.assertEqual(
            self.service.query(AuditQuery(platform_query=True)).records,
            (),
        )

    def test_failure_policy_is_not_silently_successful(self):
        service = AuditService(FailingProvider())
        result = service.emit(make_record())
        self.assertFalse(result.accepted)
        self.assertEqual(result.failure_policy, "FAIL_OPERATION_WITH_AUDIT_ERROR")
        self.assertEqual(result.error_code, "AUDIT_PROVIDER_FAILURE")

    def test_no_filesystem_or_jsonl_persistence(self):
        with tempfile.TemporaryDirectory() as directory:
            before = set(os.listdir(directory))
            self.service.emit(make_record())
            self.service.query(AuditQuery(tenant_id="tenant-001"))
            self.assertEqual(set(os.listdir(directory)), before)

    def test_clear_is_explicit_test_utility(self):
        self.service.emit(make_record())
        self.provider.clear_for_test()
        self.assertIsNone(self.service.get_by_id("audit-001"))


if __name__ == "__main__":
    unittest.main()
