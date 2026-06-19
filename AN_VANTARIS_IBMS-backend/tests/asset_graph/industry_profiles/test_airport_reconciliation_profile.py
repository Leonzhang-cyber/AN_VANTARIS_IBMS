"""Tests for airport asset reconciliation and readiness gate."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BACKEND = ROOT / "AN_VANTARIS_IBMS-backend"
sys.path.insert(0, str(BACKEND))

from src.asset_graph.constants import RelationshipType
from src.asset_graph.industry_profiles.airport_reconciliation import (
    AirportReconciliationProfileError,
    compare_deterministic_outputs,
    run_airport_asset_reconciliation,
)
from src.asset_graph.industry_profiles.airport_reconciliation.constants import AUTHORITY, GATE_IDS
from src.asset_graph.industry_profiles.airport_reconciliation.context import AirportReconciliationContext
from src.asset_graph.industry_profiles.airport_reconciliation.decisions import (
    canonical_proposal_decision,
    classification_decision,
    classify_label,
    evaluate_duplicate_group,
    identity_decision,
)
from src.asset_graph.industry_profiles.airport_reconciliation.gates import evaluate_readiness_gates
from src.asset_graph.reconciliation.models import sha256_digest

FIXTURES = Path(__file__).resolve().parent / "fixtures.py"
_spec = importlib.util.spec_from_file_location("reconciliation_fixtures", FIXTURES)
_fx = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_fx)

REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/airport-asset-reconciliation-profile.v1.json"
MODELS = BACKEND / "src/asset_graph/models.py"
MODULE_DIR = BACKEND / "src/asset_graph/industry_profiles/airport_reconciliation"


def _write_bundle(base: Path, devices: list[dict]) -> None:
    base.mkdir(parents=True, exist_ok=True)
    intake = _fx.build_intake_evidence(devices=devices)
    (base / "intake.json").write_text(json.dumps(intake, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    spatial = _fx.build_spatial_result(intake_digest=intake["resultDigest"])
    spatial["spatialContext"] = {"contextPlaceholdersPresent": False}
    (base / "spatial.json").write_text(json.dumps(spatial, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (base / "spatial-bindings.json").write_text(
        json.dumps(_fx.build_spatial_bindings(devices), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (base / "system-classification.json").write_text(
        json.dumps(_fx.build_system_classification_doc(intake["resultDigest"]), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (base / "device-type-classification.json").write_text(
        json.dumps(_fx.build_system_classification_doc(intake["resultDigest"]), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (base / "classification-bindings.json").write_text(
        json.dumps(_fx.build_classification_bindings(devices), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (base / "classification-reviews.json").write_text("[]\n", encoding="utf-8")
    (base / "classification-summary.json").write_text(
        json.dumps(_fx.build_classification_summary(device_count=len(devices)), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (base / "coverage-analysis.json").write_text(
        json.dumps(_fx.build_coverage_analysis(device_count=len(devices)), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _run_reconciliation(base: Path, devices: list[dict]) -> dict:
    _write_bundle(base, devices)
    context = AirportReconciliationContext(**_fx.reconciliation_context_kwargs())
    return run_airport_asset_reconciliation(
        intake_evidence_path=base / "intake.json",
        spatial_result_path=base / "spatial.json",
        spatial_bindings_path=base / "spatial-bindings.json",
        system_classification_path=base / "system-classification.json",
        device_type_classification_path=base / "device-type-classification.json",
        classification_bindings_path=base / "classification-bindings.json",
        classification_reviews_path=base / "classification-reviews.json",
        classification_summary_path=base / "classification-summary.json",
        coverage_analysis_path=base / "coverage-analysis.json",
        output_dir=base / "out",
        context=context,
        run_id="test-run",
    )


class TestAirportAssetReconciliationProfile(unittest.TestCase):
    def test_registry_exists(self) -> None:
        self.assertTrue(REGISTRY.is_file())

    def test_registry_industry_profile(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(registry["profileType"], "INDUSTRY_PROFILE")

    def test_registry_read_only(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(registry["implementationMode"], "READ_ONLY_RECONCILIATION")
        self.assertFalse(registry["canonicalWriteEnabled"])
        self.assertFalse(registry["databaseAccessEnabled"])

    def test_generic_models_not_airportized(self) -> None:
        text = MODELS.read_text(encoding="utf-8")
        self.assertNotIn("SCN", text)
        for code in ("CCT", "PAS", "TE3"):
            self.assertNotIn(code, text)

    def test_customer_codes_not_in_generic_enums(self) -> None:
        values = {item.value for item in RelationshipType}
        for code in ("CCT", "PAS", "SCN"):
            self.assertNotIn(code, values)

    def test_no_db_imports(self) -> None:
        forbidden = ("sqlalchemy", "flask", "psycopg", "pymongo")
        for path in MODULE_DIR.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text)

    def test_no_provider_writes(self) -> None:
        text = " ".join(path.read_text(encoding="utf-8") for path in MODULE_DIR.rglob("*.py"))
        self.assertNotIn("InMemoryAssetGraphProvider", text)

    def test_all_records_reconciled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [
                _fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV"),
                _fx._device_with_type("TE3-PAS-BAS-DA21-HSP-002", row=3, system="PA", device_type="Horn Speaker"),
            ]
            result = _run_reconciliation(base, devices)
            summary = result["summary"]
            self.assertEqual(summary["sourceRecordCount"], 2)
            self.assertEqual(summary["reconciliationRecordCount"], 2)

    def test_record_count_alignment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            result = _run_reconciliation(base, devices)
            summary = result["summary"]
            self.assertEqual(summary["evidenceClassifiedDeviceCount"], summary["sourceRecordCount"])

    def test_outputs_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_reconciliation(base, devices)
            out = base / "out"
            for name in (
                "airport-asset-reconciliation-result.json",
                "airport-canonical-proposal-candidates.json",
                "airport-duplicate-reconciliation-groups.json",
                "airport-alias-approval-package.json",
                "airport-location-reconciliation-groups.json",
                "airport-asset-reconciliation-summary.json",
                "airport-asset-reconciliation-review-findings.json",
                "airport-asset-readiness-gates.json",
                "artifact-manifest.json",
            ):
                self.assertTrue((out / name).is_file())

    def test_digest_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _write_bundle(base, devices)
            context = AirportReconciliationContext(
                tenant_id="SYNTH-TENANT-001",
                site_id="SYNTH-SITE-001",
                source_workbook_digest="wrong-digest",
            )
            with self.assertRaises(AirportReconciliationProfileError):
                run_airport_asset_reconciliation(
                    intake_evidence_path=base / "intake.json",
                    spatial_result_path=base / "spatial.json",
                    spatial_bindings_path=base / "spatial-bindings.json",
                    system_classification_path=base / "system-classification.json",
                    device_type_classification_path=base / "device-type-classification.json",
                    classification_bindings_path=base / "classification-bindings.json",
                    classification_reviews_path=base / "classification-reviews.json",
                    classification_summary_path=base / "classification-summary.json",
                    coverage_analysis_path=base / "coverage-analysis.json",
                    output_dir=base / "out",
                    context=context,
                    run_id="run",
                )

    def test_duplicate_group_created(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [
                _fx._device_with_type("DUP-DEV-001", system="PA", device_type="Horn Speaker"),
                _fx._device_with_type("DUP-DEV-001", worksheet="Zone-2", row=3, system="PA", device_type="Horn Speaker"),
            ]
            _run_reconciliation(base, devices)
            groups = json.loads((base / "out" / "airport-duplicate-reconciliation-groups.json").read_text(encoding="utf-8"))
            self.assertEqual(len(groups), 1)
            self.assertTrue(groups[0]["requiresCanonicalWinnerDecision"])

    def test_no_automatic_winner_selected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [
                _fx._device_with_type("DUP-DEV-001", system="PA"),
                _fx._device_with_type("DUP-DEV-001", worksheet="Zone-2", row=3, system="PA"),
            ]
            _run_reconciliation(base, devices)
            result = json.loads((base / "out" / "airport-asset-reconciliation-result.json").read_text(encoding="utf-8"))
            for record in result["records"]:
                self.assertNotIn("canonicalWinnerDigest", record)
                self.assertIn("CANONICAL_WINNER_REQUIRED", record.get("reviewReasons", []))

    def test_cct_cctv_alias_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_reconciliation(base, devices)
            package = json.loads((base / "out" / "airport-alias-approval-package.json").read_text(encoding="utf-8"))
            aliases = [item for item in package if item["proposalType"] == "SYSTEM_ALIAS"]
            self.assertTrue(any(item["targetValue"] == "CCTV" for item in aliases))
            self.assertEqual(aliases[0]["decisionStatus"], "APPROVAL_REQUIRED")

    def test_pas_pa_alias_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-PAS-BAS-DA21-HSP-001", system="PA", device_type="Horn Speaker")]
            _run_reconciliation(base, devices)
            package = json.loads((base / "out" / "airport-alias-approval-package.json").read_text(encoding="utf-8"))
            self.assertTrue(any(item.get("targetValue") == "PA" for item in package))

    def test_scn_namespace_proposal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-SCN-BAS-DA31-TEL-001", system="TEL", device_type="IP Telephone")]
            bindings = _fx.build_classification_bindings(devices)
            bindings[0]["sourceNamespaceCode"] = "SCN"
            bindings[0]["systemMappingStatus"] = "REVIEW_REQUIRED"
            bindings[0]["reviewReasons"] = ["SCN_SEMANTIC_REVIEW_REQUIRED"]
            _write_bundle(base, devices)
            (base / "classification-bindings.json").write_text(json.dumps(bindings, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            context = AirportReconciliationContext(**_fx.reconciliation_context_kwargs())
            run_airport_asset_reconciliation(
                intake_evidence_path=base / "intake.json",
                spatial_result_path=base / "spatial.json",
                spatial_bindings_path=base / "spatial-bindings.json",
                system_classification_path=base / "system-classification.json",
                device_type_classification_path=base / "device-type-classification.json",
                classification_bindings_path=base / "classification-bindings.json",
                classification_reviews_path=base / "classification-reviews.json",
                classification_summary_path=base / "classification-summary.json",
                coverage_analysis_path=base / "coverage-analysis.json",
                output_dir=base / "out",
                context=context,
                run_id="test-run",
            )
            package = json.loads((base / "out" / "airport-alias-approval-package.json").read_text(encoding="utf-8"))
            self.assertTrue(any(item["proposalType"] == "SOURCE_NAMESPACE" for item in package))

    def test_label_normalization_proposal(self) -> None:
        status, normalized = classify_label("Electro Magnetic Lock", "EML/DC1")
        self.assertEqual(status, "LABEL_SEMANTIC_EQUIVALENCE_CANDIDATE")
        self.assertEqual(normalized, "Electromagnetic Lock")

    def test_label_conflict_remains_mapped(self) -> None:
        decision = classification_decision(
            classification_binding={
                "systemMappingStatus": "EXACT_MATCH",
                "deviceTypeMappingStatus": "DEVICE_TYPE_COLUMN_CONFLICT",
                "genericSystemCategory": "ACCESS_CONTROL",
                "genericDeviceClass": "LOCK",
                "embeddedSystemCode": "",
                "sourceNamespaceCode": "",
                "reviewReasons": [],
            },
            label_status="LABEL_SEMANTIC_EQUIVALENCE_CANDIDATE",
        )
        self.assertEqual(decision, "CLASSIFICATION_LABEL_CONFLICT_REVIEW")

    def test_legacy_unclassified_not_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _write_bundle(base, devices)
            summary = _fx.build_classification_summary(device_count=1)
            summary["unclassifiedDeviceCount"] = 1
            (base / "classification-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            context = AirportReconciliationContext(**_fx.reconciliation_context_kwargs())
            result = run_airport_asset_reconciliation(
                intake_evidence_path=base / "intake.json",
                spatial_result_path=base / "spatial.json",
                spatial_bindings_path=base / "spatial-bindings.json",
                system_classification_path=base / "system-classification.json",
                device_type_classification_path=base / "device-type-classification.json",
                classification_bindings_path=base / "classification-bindings.json",
                classification_reviews_path=base / "classification-reviews.json",
                classification_summary_path=base / "classification-summary.json",
                coverage_analysis_path=base / "coverage-analysis.json",
                output_dir=base / "out",
                context=context,
                run_id="test-run",
            )
            self.assertFalse(result["summary"]["legacyUnclassifiedCountUsedAsBlocker"])
            gates = json.loads((base / "out" / "airport-asset-readiness-gates.json").read_text(encoding="utf-8"))
            g04 = next(item for item in gates if item["gateId"] == "G04_CLASSIFICATION_EVIDENCE_COVERAGE")
            self.assertNotEqual(g04["status"], "BLOCKED")

    def test_reconciliation_eligibility_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            result = _run_reconciliation(base, devices)
            self.assertEqual(result["summary"]["reconciliationEligibleDeviceCount"], 1)

    def test_canonical_proposals_are_evidence_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_reconciliation(base, devices)
            proposals = json.loads((base / "out" / "airport-canonical-proposal-candidates.json").read_text(encoding="utf-8"))
            self.assertEqual(len(proposals), 1)
            self.assertNotIn("databasePrimaryKey", proposals[0])

    def test_gate_g12_write_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_reconciliation(base, devices)
            gates = json.loads((base / "out" / "airport-asset-readiness-gates.json").read_text(encoding="utf-8"))
            g12 = next(item for item in gates if item["gateId"] == "G12_WRITE_BOUNDARY_ENFORCEMENT")
            self.assertEqual(g12["status"], "PASS")

    def test_all_twelve_gates_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_reconciliation(base, devices)
            gates = json.loads((base / "out" / "airport-asset-readiness-gates.json").read_text(encoding="utf-8"))
            self.assertEqual(len(gates), len(GATE_IDS))

    def test_aggregate_excludes_identifiers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_reconciliation(base, devices)
            summary = json.loads((base / "out" / "airport-asset-reconciliation-summary.json").read_text(encoding="utf-8"))
            self.assertFalse(summary["containsCustomerAssetIdentifiers"])
            self.assertNotIn("TE3-CCT", json.dumps(summary))

    def test_deterministic_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_reconciliation(base / "run1", devices)
            _run_reconciliation(base / "run2", devices)
            first = base / "run1" / "out" / "airport-asset-reconciliation-summary.json"
            second = base / "run2" / "out" / "airport-asset-reconciliation-summary.json"
            matched, status = compare_deterministic_outputs(first, second)
            self.assertTrue(matched, status)

    def test_forbidden_readiness_not_returned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            result = _run_reconciliation(base, devices)
            self.assertNotIn(
                result["readinessOutcome"],
                {"READY_FOR_DATABASE_IMPORT", "READY_FOR_CANONICAL_WRITE", "READY_FOR_WRITE_CUTOVER"},
            )

    def test_duplicate_spatial_conflict_detection(self) -> None:
        members = [
            {
                "normalizedLocation": "LOCATION-A",
                "locationCandidateKey": "loc-a",
                "systemMappingStatus": "ALIAS_CANDIDATE",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericSystemCategory": "PUBLIC_ADDRESS",
                "genericDeviceClass": "SPEAKER",
                "maintenanceExtensionFieldCount": 0,
                "sourceWorksheet": "Zone-1",
            },
            {
                "normalizedLocation": "LOCATION-B",
                "locationCandidateKey": "loc-b",
                "systemMappingStatus": "ALIAS_CANDIDATE",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericSystemCategory": "PUBLIC_ADDRESS",
                "genericDeviceClass": "SPEAKER",
                "maintenanceExtensionFieldCount": 0,
                "sourceWorksheet": "Zone-2",
            },
        ]
        status, reasons = evaluate_duplicate_group(members)
        self.assertEqual(status, "DUPLICATE_GROUP_SPATIAL_CONFLICT")

    def test_duplicate_agreement_identical(self) -> None:
        members = [
            {
                "normalizedLocation": "SAME",
                "locationCandidateKey": "loc-a",
                "systemMappingStatus": "ALIAS_CANDIDATE",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericSystemCategory": "PUBLIC_ADDRESS",
                "genericDeviceClass": "SPEAKER",
                "maintenanceExtensionFieldCount": 0,
                "sourceWorksheet": "Zone-1",
            },
            {
                "normalizedLocation": "SAME",
                "locationCandidateKey": "loc-a",
                "systemMappingStatus": "ALIAS_CANDIDATE",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericSystemCategory": "PUBLIC_ADDRESS",
                "genericDeviceClass": "SPEAKER",
                "maintenanceExtensionFieldCount": 0,
                "sourceWorksheet": "Zone-2",
            },
        ]
        status, _ = evaluate_duplicate_group(members)
        self.assertEqual(status, "DUPLICATE_GROUP_IDENTICAL")

    def test_identity_unique(self) -> None:
        self.assertEqual(identity_decision(source_id="DEV-1", group_size=1, group_status="UNIQUE"), "SOURCE_IDENTITY_UNIQUE")

    def test_compatibility_not_approval(self) -> None:
        proposal = canonical_proposal_decision(
            identity_decision_value="SOURCE_IDENTITY_UNIQUE",
            spatial_decision_value="SPATIAL_MAPPING_VALID",
            classification_decision_value="CLASSIFICATION_ALIAS_APPROVAL_REQUIRED",
            duplicate_group_status=None,
            context_placeholders_present=False,
        )
        self.assertEqual(proposal, "CANONICAL_PROPOSAL_READY_WITH_REVIEW")

    def test_review_aggregation_group_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [
                _fx._device_with_type("DUP-DEV-001", system="PA"),
                _fx._device_with_type("DUP-DEV-001", worksheet="Zone-2", row=3, system="PA"),
            ]
            _run_reconciliation(base, devices)
            summary = json.loads((base / "out" / "airport-asset-reconciliation-summary.json").read_text(encoding="utf-8"))
            self.assertLess(summary["groupLevelReviewCount"], summary["recordLevelReviewCount"])

    def test_gate_legacy_unclassified_blocked_when_used(self) -> None:
        gates = evaluate_readiness_gates(
            verification={"deviceCandidateCount": 1, "coverageMetrics": {"evidenceClassifiedDeviceCount": 1, "reconciliationEligibleDeviceCount": 1, "fullyApprovedDeviceCount": 0, "reviewRequiredDeviceCount": 1, "unmappedDeviceCount": 0}},
            duplicate_groups=[],
            alias_proposals=[],
            location_summary={"expectedSharedLocationGroupCount": 0, "locationTextCollisionGroupCount": 0},
            context_placeholders_present=False,
            canonical_proposals=[{"proposalStatus": "CANONICAL_PROPOSAL_READY_WITH_REVIEW"}],
            unmapped_device_count=0,
            legacy_unclassified_used_as_blocker=True,
        )
        g04 = next(item for item in gates if item["gateId"] == "G04_CLASSIFICATION_EVIDENCE_COVERAGE")
        self.assertEqual(g04["status"], "BLOCKED")

    def test_authority_constant(self) -> None:
        self.assertEqual(AUTHORITY, "ONE-AIRPORT-A1-04")

    def test_reconciliation_record_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_reconciliation(base, devices)
            result = json.loads((base / "out" / "airport-asset-reconciliation-result.json").read_text(encoding="utf-8"))
            record = result["records"][0]
            for field in (
                "reconciliationRecordId",
                "deviceCandidateDigest",
                "sourceIdentityDigest",
                "identityDecision",
                "spatialDecision",
                "classificationDecision",
                "canonicalProposalDecision",
                "resultDigest",
            ):
                self.assertIn(field, record)

    def test_shared_location_not_per_device_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [
                _fx._device_with_type("TE3-PAS-BAS-DA21-HSP-001", system="PA", location="LOBBY"),
                _fx._device_with_type("TE3-PAS-BAS-DA21-HSP-002", row=3, system="PA", location="LOBBY"),
            ]
            _run_reconciliation(base, devices)
            groups = json.loads((base / "out" / "airport-location-reconciliation-groups.json").read_text(encoding="utf-8"))
            shared = [group for group in groups if group["memberCount"] > 1]
            self.assertTrue(shared)
            self.assertEqual(shared[0]["locationReconciliationStatus"], "EXPECTED_SHARED_LOCATION")

    def test_coupler_label_normalization_candidate(self) -> None:
        status, normalized = classify_label("10 db Directional Coupler", "10DC")
        self.assertEqual(status, "LABEL_NORMALIZATION_CANDIDATE")
        self.assertEqual(normalized, "Directional Coupler")

    def test_scn_not_auto_mapped_in_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-SCN-BAS-DA31-TEL-001", system="TEL")]
            bindings = _fx.build_classification_bindings(devices)
            bindings[0]["sourceNamespaceCode"] = "SCN"
            bindings[0]["systemMappingStatus"] = "REVIEW_REQUIRED"
            _write_bundle(base, devices)
            (base / "classification-bindings.json").write_text(json.dumps(bindings, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            context = AirportReconciliationContext(**_fx.reconciliation_context_kwargs())
            run_airport_asset_reconciliation(
                intake_evidence_path=base / "intake.json",
                spatial_result_path=base / "spatial.json",
                spatial_bindings_path=base / "spatial-bindings.json",
                system_classification_path=base / "system-classification.json",
                device_type_classification_path=base / "device-type-classification.json",
                classification_bindings_path=base / "classification-bindings.json",
                classification_reviews_path=base / "classification-reviews.json",
                classification_summary_path=base / "classification-summary.json",
                coverage_analysis_path=base / "coverage-analysis.json",
                output_dir=base / "out",
                context=context,
                run_id="test-run",
            )
            result = json.loads((base / "out" / "airport-asset-reconciliation-result.json").read_text(encoding="utf-8"))
            self.assertEqual(result["records"][0]["classificationDecision"], "CLASSIFICATION_NAMESPACE_REVIEW_REQUIRED")

    def test_unmapped_device_count_zero_gate_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            result = _run_reconciliation(base, devices)
            self.assertEqual(result["summary"]["unmappedDeviceCount"], 0)


class TestAirportReconciliationDecisions(unittest.TestCase):
    def test_classification_fully_approved(self) -> None:
        decision = classification_decision(
            classification_binding={
                "systemMappingStatus": "EXACT_MATCH",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericSystemCategory": "ACCESS_CONTROL",
                "genericDeviceClass": "CONTROLLER",
                "embeddedSystemCode": "ACS",
                "sourceNamespaceCode": "",
                "reviewReasons": [],
            },
            label_status="LABEL_EXACT",
        )
        self.assertEqual(decision, "CLASSIFICATION_FULLY_APPROVED")

    def test_classification_alias_required(self) -> None:
        decision = classification_decision(
            classification_binding={
                "systemMappingStatus": "ALIAS_CANDIDATE",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericSystemCategory": "VIDEO_SURVEILLANCE",
                "genericDeviceClass": "CAMERA",
                "embeddedSystemCode": "CCT",
                "sourceNamespaceCode": "",
                "reviewReasons": [],
            },
            label_status="LABEL_EXACT",
        )
        self.assertEqual(decision, "CLASSIFICATION_ALIAS_APPROVAL_REQUIRED")

    def test_classification_unmapped(self) -> None:
        decision = classification_decision(
            classification_binding={
                "systemMappingStatus": "UNMAPPED_SOURCE_CODE",
                "deviceTypeMappingStatus": "UNKNOWN_DEVICE_TYPE_CODE",
                "genericSystemCategory": "",
                "genericDeviceClass": "",
                "embeddedSystemCode": "",
                "sourceNamespaceCode": "",
                "reviewReasons": [],
            },
            label_status="LABEL_EXACT",
        )
        self.assertEqual(decision, "CLASSIFICATION_UNMAPPED")

    def test_canonical_proposal_blocked_on_unmapped(self) -> None:
        decision = canonical_proposal_decision(
            identity_decision_value="SOURCE_IDENTITY_UNIQUE",
            spatial_decision_value="SPATIAL_MAPPING_VALID",
            classification_decision_value="CLASSIFICATION_UNMAPPED",
            duplicate_group_status=None,
            context_placeholders_present=False,
        )
        self.assertEqual(decision, "CANONICAL_PROPOSAL_BLOCKED")

    def test_canonical_proposal_duplicate_review(self) -> None:
        decision = canonical_proposal_decision(
            identity_decision_value="SOURCE_IDENTITY_DUPLICATE_COMPATIBLE",
            spatial_decision_value="SPATIAL_MAPPING_VALID",
            classification_decision_value="CLASSIFICATION_RECONCILIATION_ELIGIBLE",
            duplicate_group_status="DUPLICATE_GROUP_CANONICAL_WINNER_REQUIRED",
            context_placeholders_present=False,
        )
        self.assertEqual(decision, "CANONICAL_PROPOSAL_DUPLICATE_REVIEW")

    def test_canonical_proposal_context_required(self) -> None:
        decision = canonical_proposal_decision(
            identity_decision_value="SOURCE_IDENTITY_UNIQUE",
            spatial_decision_value="SPATIAL_CONTEXT_PLACEHOLDER",
            classification_decision_value="CLASSIFICATION_FULLY_APPROVED",
            duplicate_group_status=None,
            context_placeholders_present=True,
        )
        self.assertEqual(decision, "CANONICAL_PROPOSAL_CONTEXT_REQUIRED")

    def test_label_exact_for_matching_label(self) -> None:
        status, normalized = classify_label("Fixed Camera", "FCT")
        self.assertEqual(status, "LABEL_EXACT")
        self.assertIsNone(normalized)

    def test_label_normalization_splitter(self) -> None:
        status, normalized = classify_label("2-Way Splitter", "2LS")
        self.assertEqual(status, "LABEL_NORMALIZATION_CANDIDATE")
        self.assertEqual(normalized, "Two-Way Splitter")

    def test_label_normalization_three_way_splitter(self) -> None:
        status, normalized = classify_label("3-Way Splitter", "3LS")
        self.assertEqual(status, "LABEL_NORMALIZATION_CANDIDATE")

    def test_label_normalization_six_db_coupler(self) -> None:
        status, normalized = classify_label("6 db Directional Coupler", "6DC")
        self.assertEqual(status, "LABEL_NORMALIZATION_CANDIDATE")

    def test_duplicate_system_conflict(self) -> None:
        members = [
            {
                "normalizedLocation": "SAME",
                "locationCandidateKey": "loc-a",
                "systemMappingStatus": "EXACT_MATCH",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericSystemCategory": "ACCESS_CONTROL",
                "genericDeviceClass": "LOCK",
                "maintenanceExtensionFieldCount": 0,
                "sourceWorksheet": "Zone-1",
            },
            {
                "normalizedLocation": "SAME",
                "locationCandidateKey": "loc-a",
                "systemMappingStatus": "ALIAS_CANDIDATE",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericSystemCategory": "PUBLIC_ADDRESS",
                "genericDeviceClass": "SPEAKER",
                "maintenanceExtensionFieldCount": 0,
                "sourceWorksheet": "Zone-2",
            },
        ]
        status, _ = evaluate_duplicate_group(members)
        self.assertEqual(status, "DUPLICATE_GROUP_SYSTEM_CONFLICT")

    def test_duplicate_device_type_conflict(self) -> None:
        members = [
            {
                "normalizedLocation": "SAME",
                "locationCandidateKey": "loc-a",
                "systemMappingStatus": "EXACT_MATCH",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericSystemCategory": "ACCESS_CONTROL",
                "genericDeviceClass": "LOCK",
                "maintenanceExtensionFieldCount": 0,
                "sourceWorksheet": "Zone-1",
            },
            {
                "normalizedLocation": "SAME",
                "locationCandidateKey": "loc-a",
                "systemMappingStatus": "EXACT_MATCH",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericSystemCategory": "ACCESS_CONTROL",
                "genericDeviceClass": "SPEAKER",
                "maintenanceExtensionFieldCount": 0,
                "sourceWorksheet": "Zone-2",
            },
        ]
        status, _ = evaluate_duplicate_group(members)
        self.assertEqual(status, "DUPLICATE_GROUP_DEVICE_TYPE_CONFLICT")

    def test_duplicate_maintenance_conflict(self) -> None:
        members = [
            {
                "normalizedLocation": "SAME",
                "locationCandidateKey": "loc-a",
                "systemMappingStatus": "EXACT_MATCH",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericSystemCategory": "ACCESS_CONTROL",
                "genericDeviceClass": "LOCK",
                "maintenanceExtensionFieldCount": 0,
                "sourceWorksheet": "Zone-1",
            },
            {
                "normalizedLocation": "SAME",
                "locationCandidateKey": "loc-a",
                "systemMappingStatus": "EXACT_MATCH",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericSystemCategory": "ACCESS_CONTROL",
                "genericDeviceClass": "LOCK",
                "maintenanceExtensionFieldCount": 2,
                "sourceWorksheet": "Zone-2",
            },
        ]
        status, _ = evaluate_duplicate_group(members)
        self.assertEqual(status, "DUPLICATE_GROUP_MAINTENANCE_CONFLICT")

    def test_identity_duplicate_conflict(self) -> None:
        self.assertEqual(
            identity_decision(source_id="DUP", group_size=2, group_status="DUPLICATE_GROUP_SPATIAL_CONFLICT"),
            "SOURCE_IDENTITY_DUPLICATE_CONFLICT",
        )

    def test_identity_duplicate_identical(self) -> None:
        self.assertEqual(
            identity_decision(source_id="DUP", group_size=2, group_status="DUPLICATE_GROUP_IDENTICAL"),
            "SOURCE_IDENTITY_DUPLICATE_IDENTICAL",
        )

    def test_gate_g01_pass(self) -> None:
        gates = evaluate_readiness_gates(
            verification={"deviceCandidateCount": 2, "coverageMetrics": {"evidenceClassifiedDeviceCount": 2, "reconciliationEligibleDeviceCount": 2, "fullyApprovedDeviceCount": 1, "reviewRequiredDeviceCount": 1, "unmappedDeviceCount": 0}},
            duplicate_groups=[],
            alias_proposals=[],
            location_summary={"expectedSharedLocationGroupCount": 1, "locationTextCollisionGroupCount": 0},
            context_placeholders_present=False,
            canonical_proposals=[{"proposalStatus": "CANONICAL_PROPOSAL_READY_WITH_REVIEW"}],
            unmapped_device_count=0,
            legacy_unclassified_used_as_blocker=False,
        )
        self.assertEqual(gates[0]["gateId"], "G01_INPUT_EVIDENCE_INTEGRITY")

    def test_gate_g02_blocked_on_mismatch(self) -> None:
        gates = evaluate_readiness_gates(
            verification={"deviceCandidateCount": 2, "coverageMetrics": {"evidenceClassifiedDeviceCount": 1, "reconciliationEligibleDeviceCount": 1, "fullyApprovedDeviceCount": 0, "reviewRequiredDeviceCount": 1, "unmappedDeviceCount": 0}},
            duplicate_groups=[],
            alias_proposals=[],
            location_summary={"expectedSharedLocationGroupCount": 0, "locationTextCollisionGroupCount": 0},
            context_placeholders_present=False,
            canonical_proposals=[],
            unmapped_device_count=0,
            legacy_unclassified_used_as_blocker=False,
        )
        g02 = next(item for item in gates if item["gateId"] == "G02_RECORD_COUNT_ALIGNMENT")
        self.assertEqual(g02["status"], "BLOCKED")

    def test_gate_g06_alias_review(self) -> None:
        gates = evaluate_readiness_gates(
            verification={"deviceCandidateCount": 1, "coverageMetrics": {"evidenceClassifiedDeviceCount": 1, "reconciliationEligibleDeviceCount": 1, "fullyApprovedDeviceCount": 0, "reviewRequiredDeviceCount": 1, "unmappedDeviceCount": 0}},
            duplicate_groups=[],
            alias_proposals=[{"proposalType": "SYSTEM_ALIAS"}],
            location_summary={"expectedSharedLocationGroupCount": 0, "locationTextCollisionGroupCount": 0},
            context_placeholders_present=False,
            canonical_proposals=[],
            unmapped_device_count=0,
            legacy_unclassified_used_as_blocker=False,
        )
        g06 = next(item for item in gates if item["gateId"] == "G06_SYSTEM_ALIAS_APPROVAL")
        self.assertEqual(g06["status"], "PASS_WITH_REVIEW")

    def test_gate_g07_namespace_review(self) -> None:
        gates = evaluate_readiness_gates(
            verification={"deviceCandidateCount": 1, "coverageMetrics": {"evidenceClassifiedDeviceCount": 1, "reconciliationEligibleDeviceCount": 1, "fullyApprovedDeviceCount": 0, "reviewRequiredDeviceCount": 1, "unmappedDeviceCount": 0}},
            duplicate_groups=[],
            alias_proposals=[{"proposalType": "SOURCE_NAMESPACE"}],
            location_summary={"expectedSharedLocationGroupCount": 0, "locationTextCollisionGroupCount": 0},
            context_placeholders_present=False,
            canonical_proposals=[],
            unmapped_device_count=0,
            legacy_unclassified_used_as_blocker=False,
        )
        g07 = next(item for item in gates if item["gateId"] == "G07_SOURCE_NAMESPACE_APPROVAL")
        self.assertEqual(g07["status"], "PASS_WITH_REVIEW")

    def test_gate_g08_label_review(self) -> None:
        gates = evaluate_readiness_gates(
            verification={"deviceCandidateCount": 1, "coverageMetrics": {"evidenceClassifiedDeviceCount": 1, "reconciliationEligibleDeviceCount": 1, "fullyApprovedDeviceCount": 0, "reviewRequiredDeviceCount": 1, "unmappedDeviceCount": 0}},
            duplicate_groups=[],
            alias_proposals=[{"proposalType": "DEVICE_LABEL_NORMALIZATION"}],
            location_summary={"expectedSharedLocationGroupCount": 0, "locationTextCollisionGroupCount": 0},
            context_placeholders_present=False,
            canonical_proposals=[],
            unmapped_device_count=0,
            legacy_unclassified_used_as_blocker=False,
        )
        g08 = next(item for item in gates if item["gateId"] == "G08_DEVICE_LABEL_NORMALIZATION")
        self.assertEqual(g08["status"], "PASS_WITH_REVIEW")

    def test_gate_g10_context_review(self) -> None:
        gates = evaluate_readiness_gates(
            verification={"deviceCandidateCount": 1, "coverageMetrics": {"evidenceClassifiedDeviceCount": 1, "reconciliationEligibleDeviceCount": 1, "fullyApprovedDeviceCount": 0, "reviewRequiredDeviceCount": 1, "unmappedDeviceCount": 0}},
            duplicate_groups=[],
            alias_proposals=[],
            location_summary={"expectedSharedLocationGroupCount": 0, "locationTextCollisionGroupCount": 0},
            context_placeholders_present=True,
            canonical_proposals=[],
            unmapped_device_count=0,
            legacy_unclassified_used_as_blocker=False,
        )
        g10 = next(item for item in gates if item["gateId"] == "G10_CONTEXT_APPROVAL")
        self.assertEqual(g10["status"], "PASS_WITH_REVIEW")

    def test_gate_g05_duplicate_review(self) -> None:
        gates = evaluate_readiness_gates(
            verification={"deviceCandidateCount": 2, "coverageMetrics": {"evidenceClassifiedDeviceCount": 2, "reconciliationEligibleDeviceCount": 2, "fullyApprovedDeviceCount": 0, "reviewRequiredDeviceCount": 2, "unmappedDeviceCount": 0}},
            duplicate_groups=[{"requiresCanonicalWinnerDecision": True, "duplicateGroupStatus": "DUPLICATE_GROUP_CANONICAL_WINNER_REQUIRED"}],
            alias_proposals=[],
            location_summary={"expectedSharedLocationGroupCount": 0, "locationTextCollisionGroupCount": 0},
            context_placeholders_present=False,
            canonical_proposals=[],
            unmapped_device_count=0,
            legacy_unclassified_used_as_blocker=False,
        )
        g05 = next(item for item in gates if item["gateId"] == "G05_DUPLICATE_IDENTITY_REVIEW")
        self.assertEqual(g05["status"], "PASS_WITH_REVIEW")

    def test_classification_reconciliation_eligible(self) -> None:
        decision = classification_decision(
            classification_binding={
                "systemMappingStatus": "ALIAS_CANDIDATE",
                "deviceTypeMappingStatus": "EXACT_TYPE_MATCH",
                "genericSystemCategory": "PUBLIC_ADDRESS",
                "genericDeviceClass": "SPEAKER",
                "embeddedSystemCode": "PAS",
                "sourceNamespaceCode": "",
                "reviewReasons": [],
            },
            label_status="LABEL_EXACT",
        )
        self.assertEqual(decision, "CLASSIFICATION_ALIAS_APPROVAL_REQUIRED")

    def test_binding_count_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _write_bundle(base, devices)
            (base / "spatial-bindings.json").write_text("[]\n", encoding="utf-8")
            context = AirportReconciliationContext(**_fx.reconciliation_context_kwargs())
            with self.assertRaises(AirportReconciliationProfileError):
                run_airport_asset_reconciliation(
                    intake_evidence_path=base / "intake.json",
                    spatial_result_path=base / "spatial.json",
                    spatial_bindings_path=base / "spatial-bindings.json",
                    system_classification_path=base / "system-classification.json",
                    device_type_classification_path=base / "device-type-classification.json",
                    classification_bindings_path=base / "classification-bindings.json",
                    classification_reviews_path=base / "classification-reviews.json",
                    classification_summary_path=base / "classification-summary.json",
                    coverage_analysis_path=base / "coverage-analysis.json",
                    output_dir=base / "out",
                    context=context,
                    run_id="run",
                )

    def test_readiness_complete_with_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            result = _run_reconciliation(base, devices)
            self.assertEqual(result["readinessOutcome"], "RECONCILIATION_COMPLETE_WITH_REVIEWS")

    def test_alias_not_auto_approved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_reconciliation(base, devices)
            package = json.loads((base / "out" / "airport-alias-approval-package.json").read_text(encoding="utf-8"))
            for proposal in package:
                self.assertNotEqual(proposal["decisionStatus"], "APPROVED")

    def test_proposal_dependencies_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_reconciliation(base, devices)
            proposals = json.loads((base / "out" / "airport-canonical-proposal-candidates.json").read_text(encoding="utf-8"))
            self.assertTrue(proposals[0]["reviewDependencies"])

    def test_no_public_api_in_module(self) -> None:
        text = " ".join(path.read_text(encoding="utf-8") for path in MODULE_DIR.rglob("*.py"))
        self.assertNotIn("blueprint", text.lower())

    def test_platform_core_not_airportized_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_reconciliation(base, devices)
            result = json.loads((base / "out" / "airport-asset-reconciliation-result.json").read_text(encoding="utf-8"))
            self.assertFalse(result["platformCoreAirportized"])

    def test_evidence_classified_equals_source_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [
                _fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV"),
                _fx._device_with_type("TE3-PAS-BAS-DA21-HSP-002", row=3, system="PA"),
            ]
            result = _run_reconciliation(base, devices)
            self.assertEqual(result["summary"]["evidenceClassifiedDeviceCount"], 2)

    def test_unique_review_cause_less_than_record_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [
                _fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV"),
                _fx._device_with_type("TE3-PAS-BAS-DA21-HSP-002", row=3, system="PA"),
            ]
            result = _run_reconciliation(base, devices)
            self.assertLessEqual(result["summary"]["uniqueReviewCauseCount"], result["summary"]["recordLevelReviewCount"])

    def test_canonical_write_disabled_in_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_reconciliation(base, devices)
            result = json.loads((base / "out" / "airport-asset-reconciliation-result.json").read_text(encoding="utf-8"))
            self.assertFalse(result["canonicalWriteEnabled"])
            self.assertFalse(result["databaseAccessEnabled"])


if __name__ == "__main__":
    unittest.main()
