"""Smoke tests for IBMS-neutral Reports runtime skeleton API."""

import unittest

from flask import Flask

from src.api import api_bp


class TestReportsAPI(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.register_blueprint(api_bp)
        self.client = app.test_client()

    def test_health(self):
        response = self.client.get("/api/v1/reports/health")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["data"]["sourceSemantics"], "ibms-neutral")

    def test_catalog_list(self):
        response = self.client.get("/api/v1/reports/catalog")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertGreaterEqual(payload["data"]["total"], 8)

    def test_catalog_detail(self):
        response = self.client.get("/api/v1/reports/catalog/incident-summary")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["data"]["reportId"], "incident-summary")

    def test_query_success(self):
        response = self.client.post(
            "/api/v1/reports/query",
            json={"reportId": "event-trend", "limit": 5, "filters": {"moduleId": "source-reference"}},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(len(payload["data"]["rows"]), 5)
        self.assertEqual(payload["data"]["provider"], "local-mock-provider")
        self.assertTrue(payload["data"]["mockData"])
        self.assertIn("integrity", payload["data"])
        self.assertIn("queryHash", payload["data"]["integrity"])
        self.assertIn("payloadHash", payload["data"]["integrity"])
        self.assertIn("audit", payload["data"])
        self.assertEqual(payload["data"]["audit"]["auditEventType"], "report.query")
        self.assertIn("auditId", payload["data"]["audit"])
        self.assertIn("permissionMode", payload["data"]["audit"])
        self.assertIn("auditRecordHash", payload["data"]["audit"])
        self.assertIn("previousAuditHash", payload["data"]["audit"])
        self.assertIn("retentionClass", payload["data"]["audit"])
        self.assertIn("traceability", payload["data"])

    def test_query_invalid_report_id(self):
        response = self.client.post("/api/v1/reports/query", json={"reportId": "unknown-report"})
        self.assertEqual(response.status_code, 404)
        payload = response.get_json()
        self.assertEqual(payload["message"], "reportId not found")

    def test_export_manifest_preview_success(self):
        response = self.client.post(
            "/api/v1/reports/export/manifest",
            json={
                "reportId": "incident-summary",
                "queryId": "q-1",
                "generatedAt": "2026-01-01T00:00:00Z",
                "columns": ["recordId", "sourceReferenceId"],
                "rows": [{"recordId": "1", "sourceReferenceId": "ref-1"}],
                "summary": {"rowCount": 1},
                "filters": {"timeRange": "last_24h"},
                "provider": "local-mock-provider",
                "runtimeMode": "skeleton",
                "mockData": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        manifest = payload["data"]["manifest"]
        self.assertIn("exportHash", manifest)
        self.assertIn("queryHash", manifest)
        self.assertIn("payloadHash", manifest)
        self.assertIn("auditId", manifest)
        self.assertIn("permissionMode", manifest)
        self.assertIn("auditRecordHash", manifest)
        self.assertIn("retentionPolicy", manifest)
        self.assertEqual(manifest["certified"], False)
        self.assertEqual(manifest["iec62443Certified"], False)

    def test_export_manifest_preview_invalid_report_id(self):
        response = self.client.post(
            "/api/v1/reports/export/manifest",
            json={
                "reportId": "unknown-report",
                "columns": ["recordId"],
                "rows": [],
                "summary": {},
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_audit_list_endpoint(self):
        self.client.post(
            "/api/v1/reports/query",
            json={"reportId": "incident-summary", "limit": 1, "filters": {"moduleId": "source-reference"}},
        )
        response = self.client.get("/api/v1/reports/audit?limit=20")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("items", payload["data"])
        self.assertIn("permissionMode", payload["data"])
        self.assertIn("readStats", payload["data"])

    def test_audit_detail_not_found(self):
        response = self.client.get("/api/v1/reports/audit/not-found")
        self.assertEqual(response.status_code, 404)

    def test_audit_verify_endpoint(self):
        self.client.post(
            "/api/v1/reports/query",
            json={"reportId": "incident-summary", "limit": 1, "filters": {"moduleId": "source-reference"}},
        )
        self.client.post(
            "/api/v1/reports/query",
            json={"reportId": "event-trend", "limit": 1, "filters": {"moduleId": "source-reference"}},
        )
        response = self.client.get("/api/v1/reports/audit/verify")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("verified", payload["data"])
        self.assertIn("verificationMode", payload["data"])
        self.assertEqual(payload["data"]["certified"], False)
        self.assertEqual(payload["data"]["iec62443Certified"], False)

    def test_audit_retention_policy_endpoint(self):
        response = self.client.get("/api/v1/reports/audit/retention-policy")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["data"]["retentionMode"], "placeholder-local-jsonl")
        self.assertEqual(payload["data"]["certified"], False)
        self.assertEqual(payload["data"]["iec62443Certified"], False)


if __name__ == "__main__":
    unittest.main()

