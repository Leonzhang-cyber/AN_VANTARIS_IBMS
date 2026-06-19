"""Focused route tests for the Governance Audit Integration Pilot."""
from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

from flask import Flask, g

from src.api.system import menu_api
from src.governance.audit import (
    AuditProvider,
    AuditQuery,
    AuditService,
    InMemoryAuditProvider,
)
from src.governance.audit.pilot import install_pilot_audit_service


class FailingPilotProvider(AuditProvider):
    def emit(self, record, failure_policy):
        raise RuntimeError("non-public provider failure")

    def get_by_id(self, audit_id):
        return None

    def query(self, query_spec):
        raise RuntimeError("not used")


class FakeResult:
    def __init__(self, row=None):
        self._row = row

    def fetchone(self):
        return self._row


class TestGovernanceAuditIntegrationPilot(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.provider = InMemoryAuditProvider()

    def _invoke(self, provider, headers=None, payload=None):
        session = MagicMock()
        session.execute.side_effect = [FakeResult(None), FakeResult(None), FakeResult((37,))]
        fake_db = MagicMock()
        fake_db.session = session
        request_headers = {
            "X-Request-ID": "request-pilot-001",
            "X-Trace-ID": "trace-pilot-001",
            "X-Correlation-ID": "correlation-pilot-001",
        }
        request_headers.update(headers or {})
        with self.app.test_request_context(
            "/api/system/versions",
            method="POST",
            json=payload or {
                "version_code": "pilot-v1",
                "version_name": "Pilot Version",
                "description": "safe configuration",
            },
            headers=request_headers,
        ):
            g.current_did = "did:user:pilot-admin"
            g.jwt_payload = {"sub": g.current_did, "tenant_id": "tenant-pilot"}
            install_pilot_audit_service(AuditService(provider))
            with patch.object(menu_api, "db", fake_db):
                response, status = menu_api.create_version.__wrapped__()
        return response, status, session

    def test_success_response_and_canonical_audit(self):
        response, status, session = self._invoke(self.provider)
        payload = response.get_json()
        self.assertEqual(status, 200)
        self.assertEqual(payload["message"], "success")
        self.assertEqual(payload["data"]["version_code"], "pilot-v1")
        session.commit.assert_called_once()

        result = self.provider.query(AuditQuery(tenant_id="tenant-pilot"))
        self.assertEqual(len(result.records), 1)
        record = result.records[0]
        self.assertEqual(record.event_class, "CONFIGURATION_CHANGE")
        self.assertEqual(record.action, "platform.version.create")
        self.assertEqual(record.route_id, "ROUTE-POST-C39FFBE9F5DC")
        self.assertEqual(record.package_id, "PKG-UCORE")
        self.assertEqual(record.permission, "context:update")
        self.assertEqual(record.actor_id, "did:user:pilot-admin")
        self.assertEqual(record.tenant_id, "tenant-pilot")
        self.assertIsNone(record.site_id)
        self.assertEqual(
            {record.request_id, record.trace_id, record.correlation_id},
            {"request-pilot-001", "trace-pilot-001", "correlation-pilot-001"},
        )
        self.assertEqual(len(record.resulting_state_digest), 64)
        serialized = record.serialize().lower()
        self.assertNotIn("pilot version", serialized)
        self.assertNotIn("safe configuration", serialized)
        self.assertNotIn("authorization", serialized)
        self.assertNotIn("password", serialized)
        self.assertNotIn("private_key", serialized)
        self.assertNotIn("token", serialized)

    def test_provider_failure_obeys_failure_policy(self):
        response, status, session = self._invoke(FailingPilotProvider())
        payload = response.get_json()
        self.assertEqual(status, 500)
        self.assertEqual(payload["message"], "Audit emission failed")
        session.commit.assert_called_once()

    def test_provider_isolation(self):
        second = InMemoryAuditProvider()
        self._invoke(self.provider, payload={
            "version_code": "pilot-one", "version_name": "One",
        })
        self._invoke(second, payload={
            "version_code": "pilot-two", "version_name": "Two",
        })
        first_rows = self.provider.query(AuditQuery(tenant_id="tenant-pilot")).records
        second_rows = second.query(AuditQuery(tenant_id="tenant-pilot")).records
        self.assertEqual(len(first_rows), 1)
        self.assertEqual(len(second_rows), 1)
        self.assertNotEqual(first_rows[0].audit_id, second_rows[0].audit_id)

    def test_missing_identifiers_use_distinct_compatibility_values(self):
        response, status, _session = self._invoke(self.provider, headers={
            "X-Request-ID": "",
            "X-Trace-ID": "",
            "X-Correlation-ID": "",
        })
        self.assertEqual(status, 200)
        record = self.provider.query(AuditQuery(tenant_id="tenant-pilot")).records[0]
        self.assertEqual(len({record.request_id, record.trace_id, record.correlation_id}), 3)
        self.assertTrue(record.request_id.startswith("request-compat-"))
        self.assertTrue(record.trace_id.startswith("trace-compat-"))
        self.assertTrue(record.correlation_id.startswith("correlation-compat-"))

    def test_one_request_emits_one_record(self):
        self._invoke(self.provider)
        records = self.provider.query(AuditQuery(tenant_id="tenant-pilot")).records
        self.assertEqual(len(records), 1)

    def test_no_reports_jsonl_write(self):
        self._invoke(self.provider)
        record = self.provider.query(AuditQuery(tenant_id="tenant-pilot")).records[0]
        self.assertNotIn("jsonl", json.dumps(record.to_dict()).lower())


if __name__ == "__main__":
    unittest.main()
