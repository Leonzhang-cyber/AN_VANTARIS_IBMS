from __future__ import annotations

import json
import importlib.util
import sys
import types
import unittest
from pathlib import Path

from flask import Blueprint, Flask, jsonify

ROOT = Path(__file__).resolve().parents[3]
BACKEND_SRC = ROOT / "AN_VANTARIS_IBMS-backend"
SKELETON = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-api-skeleton.v1.json"
GA_R1_REPORT = ROOT / "ONE_AIRPORT_GA_R1_READONLY_API_ROUTE_IMPLEMENTATION_REPORT.md"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))


EXPECTED_ENDPOINTS = {
    "AIRPORT_OVERVIEW": "/api/v1/one/airport/console/overview",
    "SYSTEMS_INTEGRATION_HEALTH": "/api/v1/one/airport/console/systems-integration-health",
    "ASSETS_TOPOLOGY": "/api/v1/one/airport/console/assets-topology",
    "ALARMS_EVENTS": "/api/v1/one/airport/console/alarms-events",
    "FAULT_CASES": "/api/v1/one/airport/console/fault-cases",
    "MAINTENANCE_WORK_ORDERS": "/api/v1/one/airport/console/maintenance-work-orders",
    "EVIDENCE_INVESTIGATION": "/api/v1/one/airport/console/evidence-investigation",
    "REPORTS": "/api/v1/one/airport/console/reports",
}
EXPECTED_PAYLOAD_KEYS = {
    "platform",
    "industryProjection",
    "releaseCandidate",
    "endpointKey",
    "route",
    "method",
    "readOnly",
    "productionActivation",
    "runtimeActivation",
    "databaseAccess",
    "dbWrite",
    "approvalExecution",
    "customerIdentifierLeakage",
    "source",
    "summary",
    "data",
    "filters",
    "facets",
    "pagination",
}


class _Result:
    @classmethod
    def success(cls, data=None, message: str = "success"):
        return jsonify({"code": 200, "message": message, "data": data}), 200


def _load_isolated_ga_module():
    api_bp = Blueprint("api", __name__, url_prefix="/api")
    fake_src = types.ModuleType("src")
    fake_api = types.ModuleType("src.api")
    fake_api.api_bp = api_bp
    fake_common = types.ModuleType("src.common")
    fake_models = types.ModuleType("src.common.models")
    fake_response = types.ModuleType("src.common.models.response")
    fake_response.Result = _Result

    originals = {name: sys.modules.get(name) for name in ("src", "src.api", "src.common", "src.common.models", "src.common.models.response")}
    sys.modules.update(
        {
            "src": fake_src,
            "src.api": fake_api,
            "src.common": fake_common,
            "src.common.models": fake_models,
            "src.common.models.response": fake_response,
        }
    )
    module_path = BACKEND_SRC / "src/api/airport_ga_readonly/airport_ga_readonly_api.py"
    spec = importlib.util.spec_from_file_location("airport_ga_readonly_api_isolated", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    for name, original in originals.items():
        if original is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = original
    return module, api_bp


class AirportGaReadOnlyApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module, api_bp = _load_isolated_ga_module()
        app = Flask(__name__)
        app.register_blueprint(api_bp)
        cls.app = app
        cls.client = app.test_client()

    def test_a7_frozen_route_contracts_loaded(self) -> None:
        self.assertEqual(set(self.module.ROUTES), set(EXPECTED_ENDPOINTS))
        for endpoint_key, path in EXPECTED_ENDPOINTS.items():
            self.assertEqual(self.module.ROUTES[endpoint_key].path, path)

    def test_get_routes_return_projection_backed_envelope(self) -> None:
        for endpoint_key, path in EXPECTED_ENDPOINTS.items():
            with self.subTest(endpoint_key=endpoint_key):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.is_json)
                body = response.get_json()
                self.assertEqual(body["code"], 200)
                payload = body["data"]
                self.assertEqual(set(payload), EXPECTED_PAYLOAD_KEYS)
                self.assertEqual(payload["platform"], "VANTARIS ONE")
                self.assertEqual(payload["industryProjection"], "airport")
                self.assertEqual(payload["releaseCandidate"], self.module.RELEASE_CANDIDATE)
                self.assertEqual(payload["endpointKey"], endpoint_key)
                self.assertEqual(payload["route"], path)
                self.assertEqual(payload["method"], "GET")
                self.assertTrue(payload["readOnly"])
                self.assertFalse(payload["productionActivation"])
                self.assertFalse(payload["runtimeActivation"])
                self.assertFalse(payload["databaseAccess"])
                self.assertFalse(payload["dbWrite"])
                self.assertFalse(payload["approvalExecution"])
                self.assertFalse(payload["customerIdentifierLeakage"])
                self.assertEqual(payload["source"]["type"], "local_projection_artifact")
                self.assertEqual(payload["source"]["authority"], "A7_FROZEN_READ_ONLY_API_CONTRACT")
                self.assertNotIn("/Users/", json.dumps(payload["source"], sort_keys=True))
                self.assertIn("data", payload)
                self.assertIn("summary", payload)
                self.assertIn("filters", payload)
                self.assertIn("facets", payload)
                self.assertIn("pagination", payload)

    def test_non_get_methods_are_not_implemented(self) -> None:
        for path in EXPECTED_ENDPOINTS.values():
            with self.subTest(path=path):
                for method in ("post", "put", "patch", "delete"):
                    response = getattr(self.client, method)(path)
                    self.assertEqual(response.status_code, 405)

    def test_routes_are_get_only_in_flask_rule_table(self) -> None:
        frozen_paths = set(EXPECTED_ENDPOINTS.values())
        route_rules = [rule for rule in self.app.url_map.iter_rules() if rule.rule in frozen_paths]
        self.assertEqual(len(route_rules), 8)
        for rule in route_rules:
            declared_methods = set(rule.methods or set()) - {"HEAD", "OPTIONS"}
            self.assertEqual(declared_methods, {"GET"})

    def test_contract_source_mapping_matches_a7_skeleton(self) -> None:
        skeleton = json.loads(SKELETON.read_text(encoding="utf-8"))
        contracts = {item["endpointKey"]: item for item in skeleton["responseContracts"]}
        for endpoint_key, path in EXPECTED_ENDPOINTS.items():
            with self.subTest(endpoint_key=endpoint_key):
                payload = self.client.get(path).get_json()["data"]
                route = self.module.ROUTES[endpoint_key]
                self.assertEqual(payload["source"]["path"], contracts[endpoint_key]["sourceArtifactPath"])
                self.assertEqual(payload["source"]["rootKey"], contracts[endpoint_key]["projectionRootKey"])
                self.assertEqual(route.source_artifact_path, contracts[endpoint_key]["sourceArtifactPath"])
                self.assertEqual(route.root_key, contracts[endpoint_key]["projectionRootKey"])

    def test_ga_r1_report_route_list_matches_actual_routes(self) -> None:
        report = GA_R1_REPORT.read_text(encoding="utf-8")
        for path in EXPECTED_ENDPOINTS.values():
            self.assertIn(f"GET `{path}`", report)
        self.assertEqual(report.count("GET `/api/v1/one/airport/console/"), 8)

    def test_no_customer_identifier_leakage(self) -> None:
        serialized_responses = []
        for path in EXPECTED_ENDPOINTS.values():
            body = self.client.get(path).get_json()
            serialized_responses.append(json.dumps(body, sort_keys=True))
        serialized = "\n".join(serialized_responses)
        self.assertNotIn("customerAssetIdentifier", serialized)
        self.assertNotIn('"assetId"', serialized)
        self.assertNotIn('"deviceId"', serialized)


if __name__ == "__main__":
    unittest.main()
