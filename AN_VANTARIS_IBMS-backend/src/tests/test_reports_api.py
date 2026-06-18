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

    def test_query_invalid_report_id(self):
        response = self.client.post("/api/v1/reports/query", json={"reportId": "unknown-report"})
        self.assertEqual(response.status_code, 404)
        payload = response.get_json()
        self.assertEqual(payload["message"], "reportId not found")


if __name__ == "__main__":
    unittest.main()

