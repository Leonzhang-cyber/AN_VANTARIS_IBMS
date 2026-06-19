"""Tests for generic Integration Health read model and airport projection."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from integration_health.enums import HealthState, ReadinessState
from integration_health.errors import IntegrationHealthError
from integration_health.evaluation import evaluate_static_binding
from integration_health.models import build_health_dimension
from integration_health.projection import build_facets, paginate_health_records, sort_health_records
from integration_health.validation import validate_health_record
from source_system_registry.digest import sha256_digest

from source_system_registry.errors import SourceSystemRegistryError

from industry_profiles.airport.integration_health_projection import (
    build_airport_integration_health_projection,
    compare_deterministic_outputs,
    run_airport_integration_health_projection,
)
from industry_profiles.airport.source_system_review_projection import run_airport_source_system_review_projection

REGISTRY = ROOT / "registries/integration-health-read-model.v1.json"
GENERIC_DIR = ROOT / "integration_health"
AIRPORT_PROFILE = ROOT / "industry_profiles/airport/source-system-profile.v1.json"
HEALTH_PROJECTION = ROOT / "industry_profiles/airport/projections/airport-integration-health.v1.json"


def _binding(
    *,
    source_system_key: str,
    registry_entry_id: str,
    evidence_type: str,
    count: int,
    review_reasons: list[str],
    approval_state: str = "DRAFT",
) -> dict:
    return {
        "registryEntryId": registry_entry_id,
        "sourceSystemKey": source_system_key,
        "evidenceType": evidence_type,
        "sourceRecordCount": count,
        "deviceEvidenceCount": count,
        "lifecycleState": "CANDIDATE",
        "approvalState": approval_state,
        "reviewReasons": review_reasons,
        "evidenceReferences": [{"evidenceType": "TEST", "evidenceId": registry_entry_id, "sourceRecordCount": count}],
    }


def _candidate(source_system_key: str, registry_entry_id: str) -> dict:
    return {
        "sourceSystemKey": source_system_key,
        "registryEntryId": registry_entry_id,
        "mappingVersion": "airport-source-system-v1",
        "schemaVersion": "1.0.0",
        "integrationDeclarations": [
            {
                "integrationMethod": "EVIDENCE_ONLY",
                "connectorReference": None,
                "edgeGatewayReference": None,
                "linkRouteReference": None,
            }
        ],
        "healthPolicy": {"policyKey": "EVIDENCE_ONLY_NO_RUNTIME_HEALTH"},
    }


def _synthetic_bindings() -> list[dict]:
    return [
        _binding(source_system_key="ACS", registry_entry_id="acs-id", evidence_type="exact", count=129, review_reasons=["REGISTRY_APPROVAL_REQUIRED"]),
        _binding(source_system_key="RAS", registry_entry_id="ras-id", evidence_type="exact", count=28, review_reasons=["REGISTRY_APPROVAL_REQUIRED"]),
        _binding(source_system_key="CCTV", registry_entry_id="cctv-id", evidence_type="alias_review", count=52, review_reasons=["ALIAS_APPROVAL_REQUIRED"], approval_state="REVIEW_REQUIRED"),
        _binding(source_system_key="PA", registry_entry_id="pa-id", evidence_type="alias_review", count=247, review_reasons=["ALIAS_APPROVAL_REQUIRED"], approval_state="REVIEW_REQUIRED"),
        _binding(source_system_key="TEL", registry_entry_id="tel-id", evidence_type="namespace_review", count=14, review_reasons=["NAMESPACE_INTERPRETATION_REQUIRED"], approval_state="REVIEW_REQUIRED"),
    ]


def _synthetic_review() -> dict:
    return {"evidenceBindings": _synthetic_bindings()}


def _synthetic_candidates() -> dict:
    return {
        "candidates": [
            _candidate("ACS", "acs-id"),
            _candidate("RAS", "ras-id"),
            _candidate("CCTV", "cctv-id"),
            _candidate("PA", "pa-id"),
            _candidate("TEL", "tel-id"),
        ]
    }


class TestGenericIntegrationHealth(unittest.TestCase):
    def test_registry_exists(self) -> None:
        self.assertTrue(REGISTRY.is_file())

    def test_registry_cross_industry(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertTrue(registry["crossIndustry"])
        self.assertFalse(registry["airportSpecific"])

    def test_valid_health_record(self) -> None:
        record = evaluate_static_binding(_synthetic_bindings()[0], candidate=_candidate("ACS", "acs-id"))
        validate_health_record(record)
        self.assertEqual(record["readinessState"], ReadinessState.RUNTIME_VERIFICATION_REQUIRED.value)

    def test_deterministic_health_id(self) -> None:
        first = evaluate_static_binding(_synthetic_bindings()[0], candidate=_candidate("ACS", "acs-id"))
        second = evaluate_static_binding(_synthetic_bindings()[0], candidate=_candidate("ACS", "acs-id"))
        self.assertEqual(first["integrationHealthId"], second["integrationHealthId"])

    def test_static_evidence_not_runtime_observed(self) -> None:
        record = evaluate_static_binding(_synthetic_bindings()[0], candidate=_candidate("ACS", "acs-id"))
        self.assertFalse(record["runtimeObservationHealth"]["runtimeObserved"])
        self.assertEqual(record["runtimeObservationHealth"]["classificationState"], "UNKNOWN")

    def test_no_runtime_means_unknown_or_not_applicable(self) -> None:
        record = evaluate_static_binding(_synthetic_bindings()[0], candidate=_candidate("ACS", "acs-id"))
        self.assertEqual(record["runtimeObservationHealth"]["state"], HealthState.UNKNOWN.value)
        self.assertEqual(record["freshnessHealth"]["state"], HealthState.NOT_APPLICABLE.value)

    def test_unapproved_cannot_be_verified_ready(self) -> None:
        record = evaluate_static_binding(_synthetic_bindings()[0], candidate=_candidate("ACS", "acs-id"))
        self.assertNotEqual(record["readinessState"], ReadinessState.VERIFIED_READY.value)
        record["readinessState"] = ReadinessState.VERIFIED_READY.value
        with self.assertRaises(IntegrationHealthError):
            validate_health_record(record)

    def test_declared_policy_not_evaluated(self) -> None:
        record = evaluate_static_binding(_synthetic_bindings()[0], candidate=_candidate("ACS", "acs-id"))
        self.assertEqual(record["policyHealth"]["classificationState"], "NOT_APPLICABLE")
        policy_findings = [item for item in record["findings"] if item["findingType"] == "HEALTH_POLICY_NOT_EVALUATED"]
        self.assertEqual(len(policy_findings), 1)

    def test_no_volatile_timestamp(self) -> None:
        record = evaluate_static_binding(_synthetic_bindings()[0], candidate=_candidate("ACS", "acs-id"))
        self.assertEqual(record["generatedAtPolicy"], "DETERMINISTIC_NO_VOLATILE_TIMESTAMP")
        self.assertNotIn("generatedAt", record)

    def test_invalid_record_missing_key_fails_closed(self) -> None:
        record = evaluate_static_binding(_synthetic_bindings()[0], candidate=_candidate("ACS", "acs-id"))
        record["sourceSystemKey"] = ""
        with self.assertRaises(IntegrationHealthError):
            validate_health_record(record)

    def test_no_db_imports(self) -> None:
        forbidden = ("sqlalchemy", "flask", "psycopg", "pymongo")
        for path in GENERIC_DIR.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text)

    def test_repeated_generation_identical(self) -> None:
        first = evaluate_static_binding(_synthetic_bindings()[0], candidate=_candidate("ACS", "acs-id"))
        second = evaluate_static_binding(_synthetic_bindings()[0], candidate=_candidate("ACS", "acs-id"))
        self.assertEqual(first, second)


class TestAirportIntegrationHealthProjection(unittest.TestCase):
    def _projection(self) -> dict:
        return build_airport_integration_health_projection(
            _synthetic_review(),
            candidates=_synthetic_candidates(),
        )

    def test_five_health_records(self) -> None:
        projection = self._projection()
        self.assertEqual(len(projection["healthRecords"]), 5)

    def test_total_evidence_470(self) -> None:
        projection = self._projection()
        self.assertEqual(projection["summary"]["totalEvidenceDeviceCount"], 470)

    def test_system_counts(self) -> None:
        projection = self._projection()
        records = {item["sourceSystemKey"]: item for item in projection["healthRecords"]}
        self.assertEqual(records["ACS"]["deviceEvidenceCount"], 129)
        self.assertEqual(records["RAS"]["deviceEvidenceCount"], 28)
        self.assertEqual(records["CCTV"]["deviceEvidenceCount"], 52)
        self.assertEqual(records["PA"]["deviceEvidenceCount"], 247)
        self.assertEqual(records["TEL"]["deviceEvidenceCount"], 14)

    def test_zero_runtime_observed(self) -> None:
        projection = self._projection()
        self.assertEqual(projection["summary"]["runtimeObservedSystemCount"], 0)
        self.assertEqual(projection["summary"]["runtimeVerifiedSystemCount"], 0)
        self.assertEqual(projection["summary"]["healthySystemCount"], 0)

    def test_zero_active_registered_approved(self) -> None:
        projection = self._projection()
        summary = projection["summary"]
        self.assertEqual(summary["activeSystemCount"], 0)
        self.assertEqual(summary["registeredSystemCount"], 0)
        self.assertEqual(summary["approvedSystemCount"], 0)

    def test_readiness_by_system(self) -> None:
        projection = self._projection()
        records = {item["sourceSystemKey"]: item for item in projection["healthRecords"]}
        self.assertEqual(records["ACS"]["readinessState"], "RUNTIME_VERIFICATION_REQUIRED")
        self.assertEqual(records["RAS"]["readinessState"], "RUNTIME_VERIFICATION_REQUIRED")
        self.assertEqual(records["CCTV"]["readinessState"], "REVIEW_REQUIRED")
        self.assertEqual(records["PA"]["readinessState"], "REVIEW_REQUIRED")
        self.assertEqual(records["TEL"]["readinessState"], "REVIEW_REQUIRED")

    def test_pending_review_counts(self) -> None:
        projection = self._projection()
        summary = projection["summary"]
        self.assertEqual(summary["registryApprovalPendingCount"], 2)
        self.assertEqual(summary["aliasApprovalPendingCount"], 2)
        self.assertEqual(summary["namespaceReviewPendingCount"], 1)
        self.assertEqual(summary["runtimeVerificationRequiredCount"], 5)

    def test_alias_and_namespace_findings(self) -> None:
        projection = self._projection()
        finding_types = {item["findingType"] for item in projection["findings"]}
        self.assertIn("ALIAS_APPROVAL_PENDING", finding_types)
        self.assertIn("NAMESPACE_INTERPRETATION_PENDING", finding_types)
        self.assertNotIn("SCN_AS_TEL_ALIAS", finding_types)

    def test_declaration_reference_findings(self) -> None:
        projection = self._projection()
        finding_types = {item["findingType"] for item in projection["findings"]}
        self.assertIn("CONNECTOR_REFERENCE_UNDECLARED", finding_types)
        self.assertIn("EDGE_GATEWAY_REFERENCE_UNDECLARED", finding_types)
        self.assertIn("LINK_ROUTE_REFERENCE_UNDECLARED", finding_types)

    def test_no_device_id_leakage(self) -> None:
        projection = self._projection()
        text = json.dumps(projection)
        self.assertNotIn("TE3-", text)
        self.assertNotIn("deviceCode", text)

    def test_deterministic_ordering(self) -> None:
        first = self._projection()
        second = self._projection()
        self.assertEqual(first["healthRecords"], second["healthRecords"])

    def test_deterministic_pagination(self) -> None:
        projection = self._projection()
        first = paginate_health_records(projection["healthRecords"], page_size=25)
        second = paginate_health_records(projection["healthRecords"], page_size=25)
        self.assertEqual(first, second)

    def test_deterministic_facets(self) -> None:
        projection = self._projection()
        first = build_facets(projection["healthRecords"])
        second = build_facets(projection["healthRecords"])
        self.assertEqual(first, second)

    def test_invalid_binding_count_fails_closed(self) -> None:
        with self.assertRaises(SourceSystemRegistryError):
            build_airport_integration_health_projection(
                {"evidenceBindings": _synthetic_bindings()[:4]},
                candidates=_synthetic_candidates(),
            )

    def test_overall_readiness(self) -> None:
        projection = self._projection()
        self.assertEqual(
            projection["readinessOutcome"],
            "INTEGRATION_HEALTH_DECLARATION_COMPLETE_RUNTIME_EVIDENCE_PENDING",
        )


class TestAirportIntegrationHealthArtifact(unittest.TestCase):
    def test_artifact_exists(self) -> None:
        self.assertTrue(HEALTH_PROJECTION.is_file())


class TestRealEvidenceIntegrationHealth(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.real_available = Path("/tmp/one-airport-a1-03/run-1/airport-device-classification-bindings.json").is_file()

    def test_real_deterministic_runs(self) -> None:
        if not self.real_available:
            self.skipTest("real A1 evidence unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for run in ("run-1", "run-2"):
                evidence = base / run / "evidence"
                evidence.mkdir(parents=True)
                copy("/tmp/one-airport-a1-03/run-1/airport-device-classification-bindings.json", evidence / "airport-device-classification-bindings.json")
                copy("/tmp/one-airport-a1-04/run-1/airport-alias-approval-package.json", evidence / "airport-alias-approval-package.json")
                run_airport_integration_health_projection(
                    evidence_dir=evidence,
                    profile_path=AIRPORT_PROFILE,
                    output_path=base / run / "projection.json",
                )
            ok, _ = compare_deterministic_outputs(base / "run-1/projection.json", base / "run-2/projection.json")
            self.assertTrue(ok)


class TestBoundaryIsolation(unittest.TestCase):
    def test_no_edge_or_link_imports(self) -> None:
        text = (GENERIC_DIR / "evaluation.py").read_text(encoding="utf-8")
        text += (ROOT / "industry_profiles/airport/integration_health_projection.py").read_text(encoding="utf-8")
        self.assertNotIn("AN_VANTARIS_EDGE", text)
        self.assertNotIn("AN_VANTARIS_LINK", text)

    def test_no_fake_runtime_metrics(self) -> None:
        for path in (GENERIC_DIR / "evaluation.py", GENERIC_DIR / "projection.py", GENERIC_DIR / "models.py"):
            text = path.read_text(encoding="utf-8")
            for token in ("heartbeatAt", "latencyMs", "uptimePercent", "packetLossPercent", "throughputBps"):
                self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
