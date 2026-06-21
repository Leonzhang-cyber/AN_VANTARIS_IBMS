from __future__ import annotations

import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path

from flask import Blueprint, Flask, jsonify


ROOT = Path(__file__).resolve().parents[3]
BACKEND_SRC = ROOT / "AN_VANTARIS_IBMS-backend"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

EXPECTED_ENDPOINTS = {
    "/api/v1/one/umms/package-entry",
    "/api/v1/one/umms/stakeholder-review",
    "/api/v1/one/umms/readiness-summary",
    "/api/v1/one/umms/customer-core-functions",
    "/api/v1/one/umms/safety-posture",
}
COMMON_GUARD = {
    "readOnly": True,
    "runtimeEnabled": False,
    "productionEnabled": False,
    "dbWriteEnabled": False,
    "workflowEnabled": False,
    "approvalEnabled": False,
    "writeActionsEnabled": False,
    "edgeRuntimeCall": False,
    "linkRuntimeCall": False,
    "oneAdapterIntroduced": False,
}
CUSTOMER_FUNCTIONS = {
    "Work Order Management, auto + manual",
    "Asset Registry, full lifecycle tracking",
    "Preventive Maintenance Scheduler",
    "Spare Parts / Inventory Management",
    "Vendor / Contract Management",
    "Graphics HMI to locate Equipment",
    "Existing system onboarding",
    "Engineer commissioning diagnostics",
    "Remote overseas deployment",
    "Distributed independent installation",
}


class _Result:
    @classmethod
    def success(cls, data=None, message: str = "success"):
        return jsonify({"code": 200, "message": message, "data": data}), 200

    @classmethod
    def error(cls, code: int = 500, message: str = "error", data=None):
        return jsonify({"code": code, "message": message, "data": data}), code


def _load_isolated_umms_module():
    api_bp = Blueprint("api", __name__, url_prefix="/api")
    fake_src = types.ModuleType("src")
    fake_src.__path__ = [str(BACKEND_SRC / "src")]
    fake_api = types.ModuleType("src.api")
    fake_api.api_bp = api_bp
    fake_common = types.ModuleType("src.common")
    fake_common.__path__ = [str(BACKEND_SRC / "src/common")]
    fake_models = types.ModuleType("src.common.models")
    fake_response = types.ModuleType("src.common.models.response")
    fake_response.Result = _Result

    module_names = ("src", "src.api", "src.common", "src.common.models", "src.common.models.response")
    originals = {name: sys.modules.get(name) for name in module_names}
    sys.modules.update(
        {
            "src": fake_src,
            "src.api": fake_api,
            "src.common": fake_common,
            "src.common.models": fake_models,
            "src.common.models.response": fake_response,
        }
    )
    module_path = BACKEND_SRC / "src/api/umms/umms_api.py"
    spec = importlib.util.spec_from_file_location("umms_api_r11_isolated", module_path)
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


class UmmsR11ReadOnlyApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module, api_bp = _load_isolated_umms_module()
        app = Flask(__name__)
        app.register_blueprint(api_bp)
        cls.app = app
        cls.client = app.test_client()

    def test_expected_get_routes_exist(self) -> None:
        rules = {rule.rule for rule in self.app.url_map.iter_rules()}
        self.assertTrue(EXPECTED_ENDPOINTS.issubset(rules))

    def test_routes_are_get_only(self) -> None:
        for rule in self.app.url_map.iter_rules():
            if rule.rule in EXPECTED_ENDPOINTS:
                declared_methods = set(rule.methods or set()) - {"HEAD", "OPTIONS"}
                self.assertEqual(declared_methods, {"GET"})

    def test_non_get_methods_are_not_implemented(self) -> None:
        for path in EXPECTED_ENDPOINTS:
            with self.subTest(path=path):
                for method in ("post", "put", "patch", "delete"):
                    response = getattr(self.client, method)(path)
                    self.assertEqual(response.status_code, 405)

    def test_each_endpoint_returns_common_readonly_guard(self) -> None:
        for path in EXPECTED_ENDPOINTS:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                body = response.get_json()
                self.assertEqual(body["code"], 200)
                payload = body["data"]
                for key, expected in COMMON_GUARD.items():
                    self.assertEqual(payload[key], expected)
                self.assertEqual(payload["platform"], "VANTARIS ONE")
                self.assertEqual(payload["module"], "UMMS")
                self.assertEqual(payload["source"]["type"], "local_projection_registry")
                self.assertNotIn("/Users/", json.dumps(payload["source"], sort_keys=True))

    def test_package_entry_response_contract(self) -> None:
        payload = self.client.get("/api/v1/one/umms/package-entry").get_json()["data"]
        self.assertEqual(payload["packageId"], "umms")
        self.assertEqual(payload["packageName"], "Unified Maintenance Management System")
        self.assertEqual(payload["packageDisplayName"], "UMMS")
        self.assertEqual(payload["packageStatus"], "stakeholder_review_ready")
        self.assertEqual(payload["entryMode"], "read_only_stakeholder_review")
        self.assertEqual(payload["latestTag"], "umms-package-uconsole-stakeholder-entry-readiness-local-freeze-20260621")
        self.assertEqual(payload["stakeholderReviewPackage"], "ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE.md")

    def test_customer_core_functions_response_contract(self) -> None:
        payload = self.client.get("/api/v1/one/umms/customer-core-functions").get_json()["data"]
        functions = payload["customerCoreFunctions"]
        self.assertEqual({item["function"] for item in functions}, CUSTOMER_FUNCTIONS)
        self.assertTrue(all(item["runtimeEnabled"] is False for item in functions))
        self.assertEqual(payload["totalFunctions"], 10)

    def test_safety_posture_response_contract(self) -> None:
        payload = self.client.get("/api/v1/one/umms/safety-posture").get_json()["data"]
        safety = payload["safetyPosture"]
        self.assertTrue(safety["readOnly"])
        for key in (
            "productionActivation",
            "runtimeActivation",
            "dbWrite",
            "approvalExecution",
            "workflowExecution",
            "workOrderRuntimeExecution",
            "pmExecution",
            "inventoryTransaction",
            "vendorContractSlaRuntime",
            "evidenceClosureExecution",
            "hmiRuntimeExecution",
            "deviceConnection",
            "connectorExecution",
            "edgeRuntimeCall",
            "linkRuntimeCall",
            "oneAdapterIntroduced",
        ):
            self.assertFalse(safety[key])


if __name__ == "__main__":
    unittest.main()

