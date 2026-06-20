"""Tests for read-only UConsole Integration Health projection."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from uconsole_projection.enums import GENERATED_AT_POLICY, CardType
from uconsole_projection.errors import UConsoleProjectionError
from uconsole_projection.models import build_dashboard_card, build_source_system_row, build_uconsole_projection_shell
from uconsole_projection.projection import build_row_facets, paginate_source_system_rows
from uconsole_projection.validation import validate_projection

from industry_profiles.airport.uconsole_integration_health_projection import (
    build_airport_uconsole_from_committed_artifacts,
    build_airport_uconsole_integration_health_projection,
    compare_deterministic_outputs,
    run_airport_uconsole_integration_health_projection,
)

REGISTRY = ROOT / "registries/uconsole-integration-health-projection.v1.json"
GENERIC_DIR = ROOT / "uconsole_projection"
PROJECTIONS_DIR = ROOT / "industry_profiles/airport/projections"
UCONSOLE_PROJECTION = PROJECTIONS_DIR / "airport-uconsole-integration-health.v1.json"
AIRPORT_MODULE = ROOT / "industry_profiles/airport/uconsole_integration_health_projection.py"

EXPECTED_COUNTS = {"ACS": 129, "RAS": 28, "CCTV": 52, "PA": 247, "TEL": 14}


def _load(name: str) -> dict:
    return json.loads((PROJECTIONS_DIR / name).read_text(encoding="utf-8"))


def _minimal_projection(**summary_overrides: object) -> dict:
    rows = [
        build_source_system_row(
            source_system_key=key,
            registry_entry_id=f"registry-{key.lower()}",
            lifecycle_state="CANDIDATE",
            approval_state="DRAFT",
            readiness_state="RUNTIME_VERIFICATION_REQUIRED",
            integration_health_state="RUNTIME_VERIFICATION_REQUIRED",
            review_state="REGISTRY_APPROVAL_PENDING",
            evidence_contract_state="NOT_RUNTIME_EVIDENCE",
            runtime_observed=False,
            runtime_verified=False,
            device_evidence_count=1,
            pending_decision_count=1,
            finding_count=1,
        )
        for key in ("ACS",)
    ]
    for row in rows:
        row["decisionRequired"] = True
    card = build_dashboard_card(
        card_type=CardType.SOURCE_SYSTEM_SUMMARY.value,
        title="ACS source system",
        severity="LOW",
        status="RUNTIME_PENDING",
        value=1,
        unit="devices",
        affected_source_system_keys=["ACS"],
        decision_required=True,
        card_key={"sourceSystemKey": "ACS"},
    )
    summary = {
        "uConsoleIntegrationProjectionCount": 1,
        "sourceSystemRowCount": 1,
        "dashboardCardCount": 1,
        "healthSummaryCardCount": 0,
        "reviewQueueCardCount": 0,
        "evidenceContractCardCount": 0,
        "totalEvidenceDeviceCount": 1,
        "pendingDecisionCount": 1,
        "runtimeObservedSystemCount": 0,
        "runtimeVerifiedSystemCount": 0,
        "healthySystemCount": 0,
        "activeSystemCount": 0,
        "registeredSystemCount": 0,
        "approvedSystemCount": 0,
        "aliasApprovalPendingCount": 0,
        "namespaceReviewPendingCount": 0,
        "registryApprovalPendingCount": 1,
        "evidenceEnvelopeCount": 1,
        "acceptedAsEvidenceCount": 1,
        "rejectedEnvelopeCount": 0,
        "runtimeConnectorExecutionEnabled": False,
        "databaseAccessEnabled": False,
        "productionActivationEnabled": False,
        "frontendEnabled": False,
        "apiEnabled": False,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
    }
    summary.update(summary_overrides)
    projection = build_uconsole_projection_shell(
        authority="TEST",
        profile_id="test-profile",
        implementation_status="TEST",
        readiness_outcome="TEST",
        summary=summary,
        dashboard_cards=[card],
        health_summary_cards=[],
        review_queue_cards=[],
        evidence_contract_cards=[],
        source_system_rows=rows,
        filters=[],
        facets=[],
        default_page=paginate_source_system_rows(rows),
        source_artifact_references=[],
    )
    return projection


class TestGenericUConsoleProjection(unittest.TestCase):
    def test_registry_exists(self) -> None:
        self.assertTrue(REGISTRY.is_file())

    def test_valid_projection_builds(self) -> None:
        projection = _minimal_projection()
        validate_projection(projection)

    def test_invalid_projection_fails(self) -> None:
        projection = _minimal_projection()
        del projection["projectionId"]
        with self.assertRaises(UConsoleProjectionError):
            validate_projection(projection)

    def test_deterministic_projection_id(self) -> None:
        first = _minimal_projection()
        second = _minimal_projection()
        self.assertEqual(first["projectionId"], second["projectionId"])

    def test_deterministic_row_id(self) -> None:
        first = build_source_system_row(
            source_system_key="ACS",
            registry_entry_id="registry-acs",
            lifecycle_state="CANDIDATE",
            approval_state="DRAFT",
            readiness_state="RUNTIME_VERIFICATION_REQUIRED",
            integration_health_state="RUNTIME_VERIFICATION_REQUIRED",
            review_state="REGISTRY_APPROVAL_PENDING",
            evidence_contract_state="NOT_RUNTIME_EVIDENCE",
            runtime_observed=False,
            runtime_verified=False,
            device_evidence_count=129,
            pending_decision_count=1,
            finding_count=5,
        )
        second = build_source_system_row(
            source_system_key="ACS",
            registry_entry_id="registry-acs",
            lifecycle_state="CANDIDATE",
            approval_state="DRAFT",
            readiness_state="RUNTIME_VERIFICATION_REQUIRED",
            integration_health_state="RUNTIME_VERIFICATION_REQUIRED",
            review_state="REGISTRY_APPROVAL_PENDING",
            evidence_contract_state="NOT_RUNTIME_EVIDENCE",
            runtime_observed=False,
            runtime_verified=False,
            device_evidence_count=129,
            pending_decision_count=1,
            finding_count=5,
        )
        self.assertEqual(first["rowId"], second["rowId"])

    def test_deterministic_card_id(self) -> None:
        kwargs = dict(
            card_type=CardType.HEALTH_SUMMARY.value,
            title="Health",
            severity="INFO",
            status="RUNTIME_PENDING",
            value=0,
            unit="runtimeObserved",
            affected_source_system_keys=["ACS"],
            decision_required=False,
            card_key={"cardType": "HEALTH_SUMMARY"},
        )
        self.assertEqual(
            build_dashboard_card(**kwargs)["cardId"],
            build_dashboard_card(**kwargs)["cardId"],
        )

    def test_deterministic_facets(self) -> None:
        projection = build_airport_uconsole_from_committed_artifacts(PROJECTIONS_DIR)
        first = projection["facets"]
        second = build_airport_uconsole_from_committed_artifacts(PROJECTIONS_DIR)["facets"]
        self.assertEqual(first, second)

    def test_deterministic_pagination(self) -> None:
        projection = build_airport_uconsole_from_committed_artifacts(PROJECTIONS_DIR)
        page = projection["defaultPage"]
        self.assertEqual(page["pageSize"], 25)
        self.assertEqual(page["totalCount"], 5)
        self.assertIsNone(page["continuationToken"])

    def test_repeated_output_byte_identical(self) -> None:
        first = json.dumps(build_airport_uconsole_from_committed_artifacts(PROJECTIONS_DIR), sort_keys=True)
        second = json.dumps(build_airport_uconsole_from_committed_artifacts(PROJECTIONS_DIR), sort_keys=True)
        self.assertEqual(first, second)

    def test_no_volatile_timestamp(self) -> None:
        projection = build_airport_uconsole_from_committed_artifacts(PROJECTIONS_DIR)
        self.assertEqual(projection["generatedAtPolicy"], GENERATED_AT_POLICY)
        self.assertNotIn("generatedAt", projection)

    def test_no_api_frontend_flags(self) -> None:
        projection = build_airport_uconsole_from_committed_artifacts(PROJECTIONS_DIR)
        summary = projection["summary"]
        self.assertFalse(summary["frontendEnabled"])
        self.assertFalse(summary["apiEnabled"])


class TestAirportUConsoleProjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.projection = build_airport_uconsole_integration_health_projection(
            review_projection=_load("airport-source-system-review.v1.json"),
            health_projection=_load("airport-integration-health.v1.json"),
            evidence_contract_projection=_load("airport-evidence-adapter-contract.v1.json"),
        )

    def test_five_source_system_rows(self) -> None:
        self.assertEqual(len(self.projection["sourceSystemRows"]), 5)

    def test_five_dashboard_cards(self) -> None:
        self.assertEqual(len(self.projection["dashboardCards"]), 5)
        self.assertEqual(self.projection["summary"]["dashboardCardCount"], 5)

    def test_summary_cards(self) -> None:
        self.assertEqual(len(self.projection["healthSummaryCards"]), 1)
        self.assertEqual(len(self.projection["reviewQueueCards"]), 1)
        self.assertEqual(len(self.projection["evidenceContractCards"]), 1)

    def test_total_evidence_count(self) -> None:
        self.assertEqual(self.projection["summary"]["totalEvidenceDeviceCount"], 470)

    def test_system_device_counts(self) -> None:
        counts = {row["sourceSystemKey"]: row["deviceEvidenceCount"] for row in self.projection["sourceSystemRows"]}
        self.assertEqual(counts, EXPECTED_COUNTS)

    def test_pending_decisions(self) -> None:
        self.assertEqual(self.projection["summary"]["pendingDecisionCount"], 5)

    def test_review_breakdown(self) -> None:
        summary = self.projection["summary"]
        self.assertEqual(summary["aliasApprovalPendingCount"], 2)
        self.assertEqual(summary["namespaceReviewPendingCount"], 1)
        self.assertEqual(summary["registryApprovalPendingCount"], 2)

    def test_evidence_contract_counts(self) -> None:
        summary = self.projection["summary"]
        self.assertEqual(summary["evidenceEnvelopeCount"], 5)
        self.assertEqual(summary["acceptedAsEvidenceCount"], 5)
        self.assertEqual(summary["rejectedEnvelopeCount"], 0)

    def test_zero_runtime_and_activation(self) -> None:
        summary = self.projection["summary"]
        self.assertEqual(summary["runtimeObservedSystemCount"], 0)
        self.assertEqual(summary["runtimeVerifiedSystemCount"], 0)
        self.assertEqual(summary["healthySystemCount"], 0)
        self.assertEqual(summary["activeSystemCount"], 0)
        self.assertEqual(summary["registeredSystemCount"], 0)
        self.assertEqual(summary["approvedSystemCount"], 0)

    def test_no_device_id_leakage(self) -> None:
        text = json.dumps(self.projection)
        self.assertNotIn("TE3-", text)
        self.assertNotIn("deviceCode", text)
        self.assertNotIn("deviceId", text)

    def test_readiness_outcome(self) -> None:
        self.assertEqual(
            self.projection["readinessOutcome"],
            "UCONSOLE_INTEGRATION_HEALTH_READ_ONLY_PROJECTION_COMPLETE_RUNTIME_PENDING",
        )


class TestAirportProjectionArtifact(unittest.TestCase):
    def test_projection_artifact_exists(self) -> None:
        self.assertTrue(UCONSOLE_PROJECTION.is_file())


class TestRealEvidenceUConsoleProjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.real_available = Path("/tmp/one-airport-a1-03/run-1/airport-device-classification-bindings.json").is_file()

    def test_real_deterministic_runs(self) -> None:
        if not self.real_available:
            self.skipTest("real A1 evidence unavailable")
        profile = ROOT / "industry_profiles/airport/source-system-profile.v1.json"
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for run in ("run-1", "run-2"):
                evidence = base / run / "evidence"
                evidence.mkdir(parents=True)
                copy("/tmp/one-airport-a1-03/run-1/airport-device-classification-bindings.json", evidence / "airport-device-classification-bindings.json")
                copy("/tmp/one-airport-a1-04/run-1/airport-alias-approval-package.json", evidence / "airport-alias-approval-package.json")
                run_airport_uconsole_integration_health_projection(
                    evidence_dir=evidence,
                    profile_path=profile,
                    output_path=base / run / "projection.json",
                )
            ok, _ = compare_deterministic_outputs(base / "run-1/projection.json", base / "run-2/projection.json")
            self.assertTrue(ok)


class TestBoundaryIsolation(unittest.TestCase):
    def test_no_edge_or_link_imports(self) -> None:
        text = AIRPORT_MODULE.read_text(encoding="utf-8")
        self.assertNotIn("AN_VANTARIS_EDGE", text)
        self.assertNotIn("AN_VANTARIS_LINK", text)

    def test_no_db_imports(self) -> None:
        forbidden = ("sqlalchemy", "flask", "psycopg", "pymongo")
        for path in GENERIC_DIR.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text)

    def test_no_fake_runtime_metrics(self) -> None:
        for path in list(GENERIC_DIR.rglob("*.py")) + [AIRPORT_MODULE]:
            text = path.read_text(encoding="utf-8")
            for token in ("heartbeatAt", "latencyMs", "uptimePercent", "lastSeen"):
                self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
