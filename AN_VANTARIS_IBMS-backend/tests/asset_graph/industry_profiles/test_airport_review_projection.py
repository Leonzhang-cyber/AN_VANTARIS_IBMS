"""Tests for airport reconciled asset review projection."""
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
from src.asset_graph.industry_profiles.airport_reconciliation import run_airport_asset_reconciliation
from src.asset_graph.industry_profiles.airport_reconciliation.context import AirportReconciliationContext
from src.asset_graph.industry_profiles.airport_review_projection import (
    AirportReviewProjectionError,
    compare_deterministic_outputs,
    run_airport_review_projection,
)
from src.asset_graph.industry_profiles.airport_review_projection.constants import (
    AUTHORITY,
    DISPLAY_STATUS_PRIORITY,
    FORBIDDEN_READINESS,
    GATE_IDS,
    IMPLEMENTATION_MODE,
    INFORMATIONAL_LOCATION_STATUSES,
    MAX_PAGE_SIZE,
    PAGE_SIZE_OPTIONS,
    PROFILE_VERSION,
)
from src.asset_graph.industry_profiles.airport_review_projection.context import AirportReviewProjectionContext
from src.asset_graph.industry_profiles.airport_review_projection.projection import (
    build_context_review_card,
    build_duplicate_review_card,
    build_facets,
    display_status_for_record,
    paginate_rows,
    primary_display_status,
    sort_review_rows,
)
from src.asset_graph.reconciliation.models import sha256_digest

FIXTURES = Path(__file__).resolve().parent / "fixtures.py"
_spec = importlib.util.spec_from_file_location("review_fixtures", FIXTURES)
_fx = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_fx)

REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/airport-asset-review-projection.v1.json"
MODELS = BACKEND / "src/asset_graph/models.py"
MODULE_DIR = BACKEND / "src/asset_graph/industry_profiles/airport_review_projection"
REAL_RECON = Path("/tmp/one-airport-a1-04/run-1")
REAL_WORKBOOK_DIGEST = "60eac97282b1cae4d1697ad1b0505d66f530a638b3de3d095f9e5f9c620a3d48"

ROW_FIELDS = (
    "reconciliationRecordId",
    "sourceIdentityDigest",
    "deviceCandidateDigest",
    "spatialBindingDigest",
    "classificationBindingDigest",
    "canonicalProposalDigest",
    "systemCategory",
    "deviceClass",
    "spatialStatus",
    "classificationStatus",
    "duplicateStatus",
    "proposalStatus",
    "reviewCauseIds",
    "blockerCauseIds",
    "warningCauseIds",
    "displayStatus",
    "resultDigest",
)

OUTPUT_ARTIFACTS = (
    "airport-asset-review-rows.json",
    "airport-review-groups.json",
    "airport-review-dashboard.json",
    "airport-review-facets.json",
    "airport-review-readiness-cards.json",
    "airport-review-summary.json",
    "artifact-manifest.json",
)


def _write_reconciliation_bundle(base: Path, devices: list[dict]) -> dict:
    base.mkdir(parents=True, exist_ok=True)
    intake = _fx.build_intake_evidence(devices=devices)
    (base / "intake.json").write_text(json.dumps(intake, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    spatial = _fx.build_spatial_result(intake_digest=intake["resultDigest"])
    spatial["spatialContext"] = {"contextPlaceholdersPresent": True}
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
        output_dir=base / "recon-out",
        context=context,
        run_id="test-run",
    )


def _run_projection(base: Path, devices: list[dict], *, page_size: int = 50) -> dict:
    recon = _write_reconciliation_bundle(base, devices)
    summary_path = base / "recon-out" / "airport-asset-reconciliation-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    context = AirportReviewProjectionContext(
        **_fx.review_projection_context_kwargs(reconciliation_result_digest=summary["resultDigest"]),
        page_size=page_size,
    )
    return run_airport_review_projection(
        reconciliation_dir=base / "recon-out",
        output_dir=base / "review-out",
        context=context,
        run_id="test-run",
    )


class TestAirportReviewProjectionRegistry(unittest.TestCase):
    def test_registry_exists(self) -> None:
        self.assertTrue(REGISTRY.is_file())

    def test_registry_industry_projection(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(registry["profileType"], "INDUSTRY_PROJECTION")

    def test_registry_read_only_projection(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(registry["implementationMode"], "READ_ONLY_PROJECTION")
        self.assertFalse(registry["canonicalWriteEnabled"])
        self.assertFalse(registry["decisionWriteEnabled"])
        self.assertFalse(registry["databaseAccessEnabled"])
        self.assertFalse(registry["platformCoreAirportized"])

    def test_registry_authority(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(registry["authority"], AUTHORITY)
        self.assertEqual(registry["profileVersion"], PROFILE_VERSION)

    def test_forbidden_readiness_in_registry(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        for outcome in FORBIDDEN_READINESS:
            self.assertIn(outcome, registry["forbiddenReadinessOutcomes"])


class TestAirportReviewProjectionBoundaries(unittest.TestCase):
    def test_generic_models_not_airportized(self) -> None:
        text = MODELS.read_text(encoding="utf-8")
        for code in ("SCN", "CCT", "PAS", "TE3"):
            self.assertNotIn(code, text)

    def test_customer_codes_not_in_generic_enums(self) -> None:
        values = {item.value for item in RelationshipType}
        for code in ("CCT", "PAS", "SCN"):
            self.assertNotIn(code, values)

    def test_no_db_imports(self) -> None:
        forbidden = ("sqlalchemy", "flask", "psycopg", "pymongo", "InMemoryAssetGraphProvider")
        for path in MODULE_DIR.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text)

    def test_no_public_api_routes(self) -> None:
        text = " ".join(path.read_text(encoding="utf-8") for path in MODULE_DIR.rglob("*.py"))
        self.assertNotIn("blueprint", text.lower())
        self.assertNotIn("@app.route", text)

    def test_no_frontend_paths(self) -> None:
        frontend = ROOT / "AN_VANTARIS_IBMS-frontend"
        if frontend.is_dir():
            self.assertNotIn("airport_review_projection", " ".join(str(p) for p in frontend.rglob("*.tsx")))

    def test_implementation_mode_constant(self) -> None:
        self.assertEqual(IMPLEMENTATION_MODE, "READ_ONLY_PROJECTION")

    def test_module_exports(self) -> None:
        from src.asset_graph.industry_profiles import run_airport_review_projection as exported

        self.assertIsNotNone(exported)

    def test_no_decision_write_helpers(self) -> None:
        text = " ".join(path.read_text(encoding="utf-8") for path in MODULE_DIR.rglob("*.py"))
        for token in ("approve_alias", "select_winner", "write_decision", "canonical_write"):
            self.assertNotIn(token, text)


class TestDisplayStatusPrecedence(unittest.TestCase):
    def test_primary_display_status_blocked_wins(self) -> None:
        status = primary_display_status(["READY_FOR_REVIEW", "BLOCKED", "CONTEXT_REQUIRED"])
        self.assertEqual(status, "BLOCKED")

    def test_primary_display_status_duplicate_before_context(self) -> None:
        status = primary_display_status(["CONTEXT_REQUIRED", "DUPLICATE_DECISION_REQUIRED"])
        self.assertEqual(status, "DUPLICATE_DECISION_REQUIRED")

    def test_primary_display_status_context_before_alias(self) -> None:
        status = primary_display_status(["ALIAS_APPROVAL_REQUIRED", "CONTEXT_REQUIRED"])
        self.assertEqual(status, "CONTEXT_REQUIRED")

    def test_display_status_priority_order(self) -> None:
        self.assertEqual(DISPLAY_STATUS_PRIORITY[0], "BLOCKED")
        self.assertEqual(DISPLAY_STATUS_PRIORITY[-1], "EVIDENCE_COMPLETE")

    def test_display_status_blocked_from_blocker_reasons(self) -> None:
        record = {"blockerReasons": ["GATE_BLOCKED"], "reviewReasons": []}
        proposal = {"proposalStatus": "CANONICAL_PROPOSAL_READY_WITH_REVIEW"}
        status = display_status_for_record(
            record=record,
            proposal=proposal,
            has_duplicate=False,
            has_namespace=False,
            has_alias=False,
            has_label=False,
            has_location_conflict=False,
            context_pending=False,
        )
        self.assertEqual(status, "BLOCKED")

    def test_display_status_duplicate(self) -> None:
        record = {"blockerReasons": [], "reviewReasons": []}
        proposal = {"proposalStatus": "CANONICAL_PROPOSAL_DUPLICATE_REVIEW"}
        status = display_status_for_record(
            record=record,
            proposal=proposal,
            has_duplicate=True,
            has_namespace=False,
            has_alias=False,
            has_label=False,
            has_location_conflict=False,
            context_pending=False,
        )
        self.assertEqual(status, "DUPLICATE_DECISION_REQUIRED")

    def test_display_status_namespace(self) -> None:
        record = {"blockerReasons": [], "reviewReasons": []}
        proposal = {"proposalStatus": "CANONICAL_PROPOSAL_READY_WITH_REVIEW"}
        status = display_status_for_record(
            record=record,
            proposal=proposal,
            has_duplicate=False,
            has_namespace=True,
            has_alias=False,
            has_label=False,
            has_location_conflict=False,
            context_pending=False,
        )
        self.assertEqual(status, "NAMESPACE_REVIEW_REQUIRED")

    def test_display_status_alias(self) -> None:
        record = {"blockerReasons": [], "reviewReasons": []}
        proposal = {"proposalStatus": "CANONICAL_PROPOSAL_READY_WITH_REVIEW"}
        status = display_status_for_record(
            record=record,
            proposal=proposal,
            has_duplicate=False,
            has_namespace=False,
            has_alias=True,
            has_label=False,
            has_location_conflict=False,
            context_pending=False,
        )
        self.assertEqual(status, "ALIAS_APPROVAL_REQUIRED")


class TestReviewProjectionIntegration(unittest.TestCase):
    def test_outputs_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [
                _fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV"),
                _fx._device_with_type("TE3-PAS-BAS-DA21-HSP-002", row=3, system="PA", device_type="Horn Speaker"),
            ]
            _run_projection(base, devices)
            out = base / "review-out"
            for name in OUTPUT_ARTIFACTS:
                self.assertTrue((out / name).is_file(), name)

    def test_all_records_projected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [
                _fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV"),
                _fx._device_with_type("TE3-PAS-BAS-DA21-HSP-002", row=3, system="PA", device_type="Horn Speaker"),
            ]
            result = _run_projection(base, devices)
            summary = result["summary"]
            self.assertEqual(summary["assetReviewRowCount"], 2)
            self.assertEqual(summary["affectedRecordCount"], 2)

    def test_review_row_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_projection(base, devices)
            rows = json.loads((base / "review-out" / "airport-asset-review-rows.json").read_text(encoding="utf-8"))
            for field in ROW_FIELDS:
                self.assertIn(field, rows[0])

    def test_one_context_review_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_projection(base, devices)
            groups = json.loads((base / "review-out" / "airport-review-groups.json").read_text(encoding="utf-8"))
            context_cards = [item for item in groups if item.get("cardType") == "ContextReviewCard"]
            self.assertEqual(len(context_cards), 1)
            self.assertEqual(context_cards[0]["affectedRecordCount"], len(devices))

    def test_duplicate_group_creates_duplicate_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [
                _fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV"),
                _fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", row=3, system="CCTV"),
            ]
            _run_projection(base, devices)
            groups = json.loads((base / "review-out" / "airport-review-groups.json").read_text(encoding="utf-8"))
            dup_cards = [item for item in groups if item.get("cardType") == "DuplicateReviewCard"]
            self.assertGreaterEqual(len(dup_cards), 1)
            self.assertTrue(dup_cards[0]["winnerRequired"])

    def test_no_duplicate_winner_auto_selected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [
                _fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV"),
                _fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", row=3, system="CCTV"),
            ]
            _run_projection(base, devices)
            groups_text = (base / "review-out" / "airport-review-groups.json").read_text(encoding="utf-8")
            self.assertNotIn("canonicalWinnerDigest", groups_text)
            self.assertNotIn("winnerDigest", groups_text)

    def test_alias_cards_pending_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_projection(base, devices)
            groups = json.loads((base / "review-out" / "airport-review-groups.json").read_text(encoding="utf-8"))
            alias_cards = [item for item in groups if item.get("cardType") == "AliasReviewCard"]
            self.assertGreaterEqual(len(alias_cards), 1)
            self.assertEqual(alias_cards[0]["decisionState"], "APPROVAL_REQUIRED")

    def test_namespace_card_not_auto_mapped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-SCN-BAS-DA21-FCT-001", system="SCN")]
            _run_projection(base, devices)
            groups = json.loads((base / "review-out" / "airport-review-groups.json").read_text(encoding="utf-8"))
            ns_cards = [item for item in groups if item.get("cardType") == "NamespaceReviewCard"]
            if ns_cards:
                self.assertEqual(ns_cards[0]["decisionState"], "APPROVAL_REQUIRED")

    def test_label_normalization_cards(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-EML-001", system="CCTV", device_type="Electro Magnetic Lock")]
            _run_projection(base, devices)
            groups = json.loads((base / "review-out" / "airport-review-groups.json").read_text(encoding="utf-8"))
            label_cards = [item for item in groups if item.get("cardType") == "LabelNormalizationReviewCard"]
            if label_cards:
                self.assertIn("sourceValueDigest", label_cards[0])
                self.assertIn("proposedLabel", label_cards[0])

    def test_informational_location_not_pending(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_projection(base, devices)
            groups = json.loads((base / "review-out" / "airport-review-groups.json").read_text(encoding="utf-8"))
            informational = [
                item
                for item in groups
                if item.get("cardType") == "LocationReviewCard"
                and item.get("locationReconciliationStatus") in INFORMATIONAL_LOCATION_STATUSES
            ]
            for card in informational:
                self.assertTrue(card.get("informationalOnly"))
                self.assertEqual(card.get("decisionState"), "RESOLVED_BY_EXISTING_AUTHORITY")

    def test_readiness_outcome_not_forbidden(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            result = _run_projection(base, devices)
            self.assertNotIn(result["readinessOutcome"], FORBIDDEN_READINESS)

    def test_deterministic_synthetic_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_projection(base, devices)
            out1 = base / "review-out"
            _run_projection(base / "run2", devices)
            out2 = base / "run2" / "review-out"
            for name in OUTPUT_ARTIFACTS:
                ok, _ = compare_deterministic_outputs(out1 / name, out2 / name)
                self.assertTrue(ok, name)

    def test_workbook_digest_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _write_reconciliation_bundle(base, devices)
            summary = json.loads(
                (base / "recon-out" / "airport-asset-reconciliation-summary.json").read_text(encoding="utf-8")
            )
            context = AirportReviewProjectionContext(
                tenant_id="SYNTH-TENANT-001",
                site_id="SYNTH-SITE-001",
                source_workbook_digest="wrong-digest",
                reconciliation_result_digest=summary["resultDigest"],
            )
            with self.assertRaises(AirportReviewProjectionError):
                run_airport_review_projection(
                    reconciliation_dir=base / "recon-out",
                    output_dir=base / "review-out",
                    context=context,
                    run_id="run",
                )

    def test_aggregate_outputs_exclude_customer_identifiers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_projection(base, devices)
            out = base / "review-out"
            for name in (
                "airport-review-groups.json",
                "airport-review-dashboard.json",
                "airport-review-summary.json",
                "airport-review-facets.json",
            ):
                text = (out / name).read_text(encoding="utf-8")
                self.assertNotIn("TE3-CCT", text)
                self.assertNotIn("deviceCode", text)


class TestFacetsPaginationReadiness(unittest.TestCase):
    def _sample_rows(self) -> list[dict]:
        return [
            {
                "displayStatus": "CONTEXT_REQUIRED",
                "systemCategory": "VIDEO_SURVEILLANCE",
                "deviceClass": "CAMERA",
                "spatialStatus": "SPATIAL_CONTEXT_PLACEHOLDER",
                "classificationStatus": "CLASSIFICATION_ALIAS_APPROVAL_REQUIRED",
                "duplicateStatus": "DUPLICATE_NONE",
                "proposalStatus": "CANONICAL_PROPOSAL_CONTEXT_REQUIRED",
                "sourceIdentityDigest": "a",
                "reconciliationRecordId": "1",
            },
            {
                "displayStatus": "DUPLICATE_DECISION_REQUIRED",
                "systemCategory": "PUBLIC_ADDRESS",
                "deviceClass": "SPEAKER",
                "spatialStatus": "SPATIAL_BOUND",
                "classificationStatus": "CLASSIFICATION_FULLY_APPROVED",
                "duplicateStatus": "DUPLICATE_REVIEW_REQUIRED",
                "proposalStatus": "CANONICAL_PROPOSAL_DUPLICATE_REVIEW",
                "sourceIdentityDigest": "b",
                "reconciliationRecordId": "2",
            },
        ]

    def test_facets_have_required_fields(self) -> None:
        facets = build_facets(self._sample_rows())
        for facet in facets:
            for field in ("facetKey", "optionDigest", "recordCount", "reviewCount", "blockerCount"):
                self.assertIn(field, facet)

    def test_facets_deterministic_order(self) -> None:
        rows = self._sample_rows()
        first = build_facets(rows)
        second = build_facets(rows)
        self.assertEqual(first, second)

    def test_stable_row_ordering(self) -> None:
        rows = self._sample_rows()
        sorted_once = sort_review_rows(rows)
        sorted_twice = sort_review_rows(rows)
        self.assertEqual(sorted_once, sorted_twice)
        self.assertEqual(sorted_once[0]["displayStatus"], "DUPLICATE_DECISION_REQUIRED")

    def test_pagination_page_sizes(self) -> None:
        rows = [{"reconciliationRecordId": str(i), "displayStatus": "REVIEW_REQUIRED"} for i in range(30)]
        digest = sha256_digest({"count": 30})
        for size in PAGE_SIZE_OPTIONS:
            page = paginate_rows(rows, page_size=size, projection_state_digest=digest)
            self.assertEqual(page["pageSize"], size)
            self.assertLessEqual(page["returnedCount"], size)

    def test_pagination_continuation_token_deterministic(self) -> None:
        rows = [{"reconciliationRecordId": str(i), "displayStatus": "REVIEW_REQUIRED"} for i in range(100)]
        digest = sha256_digest({"count": 100})
        first = paginate_rows(rows, page_size=25, projection_state_digest=digest)
        second = paginate_rows(rows, page_size=25, projection_state_digest=digest)
        self.assertEqual(first["continuationToken"], second["continuationToken"])
        self.assertTrue(first["continuationToken"].startswith("v1:"))

    def test_pagination_respects_max_page_size(self) -> None:
        rows = [{"reconciliationRecordId": str(i), "displayStatus": "REVIEW_REQUIRED"} for i in range(5)]
        digest = sha256_digest({"count": 5})
        page = paginate_rows(rows, page_size=500, projection_state_digest=digest)
        self.assertLessEqual(page["pageSize"], MAX_PAGE_SIZE)

    def test_readiness_gate_cards_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_projection(base, devices)
            cards = json.loads(
                (base / "review-out" / "airport-review-readiness-cards.json").read_text(encoding="utf-8")
            )
            self.assertEqual(len(cards), len(GATE_IDS))

    def test_g12_write_boundary_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_projection(base, devices)
            cards = json.loads(
                (base / "review-out" / "airport-review-readiness-cards.json").read_text(encoding="utf-8")
            )
            g12 = next(item for item in cards if item["gateId"] == "G12_WRITE_BOUNDARY_ENFORCEMENT")
            self.assertFalse(g12["canonicalWriteEnabled"])
            self.assertFalse(g12["databaseAccessEnabled"])
            self.assertFalse(g12["writeCutoverPerformed"])

    def test_dashboard_no_customer_identifiers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_projection(base, devices)
            dashboard = json.loads(
                (base / "review-out" / "airport-review-dashboard.json").read_text(encoding="utf-8")
            )
            self.assertFalse(dashboard["containsCustomerAssetIdentifiers"])


class TestReviewCardBuilders(unittest.TestCase):
    def test_context_card_fields(self) -> None:
        card = build_context_review_card(affected_record_count=470, affected_proposal_count=470)
        self.assertTrue(card["airportContextPending"])
        self.assertTrue(card["terminalContextPending"])
        self.assertEqual(card["affectedRecordCount"], 470)

    def test_duplicate_card_sanitized_fields(self) -> None:
        group = {"duplicateGroupDigest": "group-digest", "memberCount": 2, "requiresCanonicalWinnerDecision": True}
        members = [
            {"spatialDecision": "A", "locationCandidateDigest": "loc1", "classificationDecision": "C1", "sourceRowDigest": "r1"},
            {"spatialDecision": "B", "locationCandidateDigest": "loc2", "classificationDecision": "C2", "sourceRowDigest": "r2"},
        ]
        card = build_duplicate_review_card(group=group, members=members)
        for field in (
            "spatialAgreementStatus",
            "locationAgreementStatus",
            "classificationAgreementStatus",
            "maintenanceAgreementStatus",
            "sourceProvenanceCount",
            "winnerRequired",
            "recommendedNextAction",
        ):
            self.assertIn(field, card)
        self.assertNotIn("sourceId", card)

    def test_duplicate_recommendation_allowed_values(self) -> None:
        allowed = {
            "CONFIRM_SAME_PHYSICAL_DEVICE",
            "KEEP_AS_SEPARATE_DEVICES",
            "CORRECT_SOURCE_ID",
            "CORRECT_LOCATION",
            "DEFER_FOR_SITE_VERIFICATION",
        }
        group = {"duplicateGroupDigest": "g", "memberCount": 2}
        members = [{"spatialDecision": "A", "locationCandidateDigest": "l1", "classificationDecision": "C", "sourceRowDigest": "r1"}]
        card = build_duplicate_review_card(group=group, members=members)
        self.assertIn(card["recommendedNextAction"], allowed)


class TestRealEvidenceReviewProjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.real_available = REAL_RECON.is_dir() and (REAL_RECON / "artifact-manifest.json").is_file()

    def test_real_470_review_rows(self) -> None:
        if not self.real_available:
            self.skipTest("real A1-04 artifacts unavailable")
        rows = json.loads((REAL_RECON.parent.parent / "one-airport-a1-05/run-1/airport-asset-review-rows.json").read_text())
        self.assertEqual(len(rows), 470)

    def test_real_summary_metrics(self) -> None:
        if not self.real_available:
            self.skipTest("real A1-04 artifacts unavailable")
        summary_path = Path("/tmp/one-airport-a1-05/run-1/airport-review-summary.json")
        if not summary_path.is_file():
            self.skipTest("real A1-05 projection not run")
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual(summary["assetReviewRowCount"], 470)
        self.assertEqual(summary["duplicateReviewCardCount"], 4)
        self.assertEqual(summary["contextReviewCardCount"], 1)
        self.assertEqual(summary["aliasReviewCardCount"], 2)
        self.assertEqual(summary["namespaceReviewCardCount"], 1)
        self.assertEqual(summary["locationReviewCardCount"], 4)
        self.assertEqual(summary["informationalLocationGroupCount"], 67)
        self.assertEqual(summary["aggregateCustomerIdentifierCount"], 0)
        self.assertEqual(summary["readinessOutcome"], "REVIEW_PROJECTION_COMPLETE_WITH_PENDING_DECISIONS")

    def test_real_context_card_470_records(self) -> None:
        if not self.real_available:
            self.skipTest("real A1-04 artifacts unavailable")
        groups_path = Path("/tmp/one-airport-a1-05/run-1/airport-review-groups.json")
        if not groups_path.is_file():
            self.skipTest("real A1-05 projection not run")
        groups = json.loads(groups_path.read_text(encoding="utf-8"))
        context_cards = [item for item in groups if item.get("cardType") == "ContextReviewCard"]
        self.assertEqual(len(context_cards), 1)
        self.assertEqual(context_cards[0]["affectedRecordCount"], 470)
        self.assertEqual(context_cards[0]["affectedProposalCount"], 470)

    def test_real_determinism(self) -> None:
        if not self.real_available:
            self.skipTest("real A1-04 artifacts unavailable")
        run1 = Path("/tmp/one-airport-a1-05/run-1")
        run2 = Path("/tmp/one-airport-a1-05/run-2")
        if not run1.is_dir() or not run2.is_dir():
            self.skipTest("real A1-05 runs unavailable")
        for name in OUTPUT_ARTIFACTS:
            ok, _ = compare_deterministic_outputs(run1 / name, run2 / name)
            self.assertTrue(ok, name)

    def test_real_rows_reference_shared_context_cause(self) -> None:
        if not self.real_available:
            self.skipTest("real A1-04 artifacts unavailable")
        rows_path = Path("/tmp/one-airport-a1-05/run-1/airport-asset-review-rows.json")
        groups_path = Path("/tmp/one-airport-a1-05/run-1/airport-review-groups.json")
        if not rows_path.is_file() or not groups_path.is_file():
            self.skipTest("real A1-05 projection not run")
        rows = json.loads(rows_path.read_text(encoding="utf-8"))
        groups = json.loads(groups_path.read_text(encoding="utf-8"))
        context_id = next(item["reviewCauseId"] for item in groups if item.get("cardType") == "ContextReviewCard")
        self.assertTrue(all(context_id in row["reviewCauseIds"] for row in rows))


    def test_real_rows_have_detail_projection(self) -> None:
        if not self.real_available:
            self.skipTest("real A1-04 artifacts unavailable")
        rows_path = Path("/tmp/one-airport-a1-05/run-1/airport-asset-review-rows.json")
        if not rows_path.is_file():
            self.skipTest("real A1-05 projection not run")
        rows = json.loads(rows_path.read_text(encoding="utf-8"))
        detail = rows[0]["detailProjection"]
        for key in (
            "assetEvidenceSummary",
            "spatialEvidenceSummary",
            "classificationEvidenceSummary",
            "duplicateComparisonSummary",
            "canonicalProposalSummary",
            "readinessImpact",
            "provenanceDigests",
        ):
            self.assertIn(key, detail)

    def test_real_duplicate_display_status_count(self) -> None:
        if not self.real_available:
            self.skipTest("real A1-04 artifacts unavailable")
        rows_path = Path("/tmp/one-airport-a1-05/run-1/airport-asset-review-rows.json")
        if not rows_path.is_file():
            self.skipTest("real A1-05 projection not run")
        rows = json.loads(rows_path.read_text(encoding="utf-8"))
        dup_rows = [row for row in rows if row["displayStatus"] == "DUPLICATE_DECISION_REQUIRED"]
        self.assertEqual(len(dup_rows), 8)

    def test_real_readiness_gate_g12(self) -> None:
        if not self.real_available:
            self.skipTest("real A1-04 artifacts unavailable")
        cards_path = Path("/tmp/one-airport-a1-05/run-1/airport-review-readiness-cards.json")
        if not cards_path.is_file():
            self.skipTest("real A1-05 projection not run")
        cards = json.loads(cards_path.read_text(encoding="utf-8"))
        g12 = next(item for item in cards if item["gateId"] == "G12_WRITE_BOUNDARY_ENFORCEMENT")
        self.assertFalse(g12["canonicalWriteEnabled"])
        self.assertFalse(g12["databaseAccessEnabled"])
        self.assertFalse(g12["writeCutoverPerformed"])

    def test_real_facets_no_raw_customer_values(self) -> None:
        if not self.real_available:
            self.skipTest("real A1-04 artifacts unavailable")
        facets_path = Path("/tmp/one-airport-a1-05/run-1/airport-review-facets.json")
        if not facets_path.is_file():
            self.skipTest("real A1-05 projection not run")
        text = facets_path.read_text(encoding="utf-8")
        self.assertNotIn("TE3-", text)
        self.assertNotIn("FIRE EXIT", text)


class TestReviewCauseAndManifest(unittest.TestCase):
    def test_manifest_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_projection(base, devices)
            manifest = json.loads((base / "review-out" / "artifact-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["authority"], AUTHORITY)

    def test_manifest_hashes_match_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            import hashlib

            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_projection(base, devices)
            manifest = json.loads((base / "review-out" / "artifact-manifest.json").read_text(encoding="utf-8"))
            for entry in manifest["artifacts"]:
                path = base / "review-out" / entry["relativePath"]
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertEqual(entry["sha256"], digest)

    def test_review_cause_ids_on_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_projection(base, devices)
            rows = json.loads((base / "review-out" / "airport-asset-review-rows.json").read_text(encoding="utf-8"))
            self.assertTrue(all(row["reviewCauseIds"] for row in rows))

    def test_no_timestamps_in_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_projection(base, devices)
            text = (base / "review-out" / "airport-review-summary.json").read_text(encoding="utf-8")
            for token in ("timestamp", "createdAt", "updatedAt", "generatedAt"):
                self.assertNotIn(token, text)

    def test_reconciliation_digest_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _write_reconciliation_bundle(base, devices)
            context = AirportReviewProjectionContext(
                **_fx.review_projection_context_kwargs(reconciliation_result_digest="wrong-digest"),
            )
            with self.assertRaises(AirportReviewProjectionError):
                run_airport_review_projection(
                    reconciliation_dir=base / "recon-out",
                    output_dir=base / "review-out",
                    context=context,
                    run_id="run",
                )

    def test_location_conflict_cards_not_informational(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [
                _fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV"),
                _fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", row=3, system="CCTV"),
            ]
            _run_projection(base, devices)
            groups = json.loads((base / "review-out" / "airport-review-groups.json").read_text(encoding="utf-8"))
            conflicts = [
                item
                for item in groups
                if item.get("cardType") == "LocationReviewCard" and not item.get("informationalOnly")
            ]
            for card in conflicts:
                self.assertEqual(card["decisionState"], "APPROVAL_REQUIRED")

    def test_unique_review_cause_count_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            result = _run_projection(base, devices)
            self.assertGreater(result["summary"]["uniqueReviewCauseCount"], 0)

    def test_pagination_preview_in_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            devices = [_fx._device_with_type("TE3-CCT-BAS-DA21-FCT-001", system="CCTV")]
            _run_projection(base, devices)
            dashboard = json.loads(
                (base / "review-out" / "airport-review-dashboard.json").read_text(encoding="utf-8")
            )
            preview = dashboard["paginationPreview"]
            self.assertIn("continuationToken", preview)
            self.assertEqual(preview["totalCount"], 1)


if __name__ == "__main__":
    unittest.main()
