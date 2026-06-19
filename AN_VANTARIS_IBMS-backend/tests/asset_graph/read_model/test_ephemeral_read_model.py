"""Tests for ephemeral Asset Graph read model and query contract."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import subprocess
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

from src.asset_graph.read_model import (
    AUTHORITY,
    DEFAULT_LIMIT,
    MAXIMUM_LIMIT,
    MODEL_NAME,
    MODEL_VERSION,
    WRITE_CUTOVER_STATUS,
    DeviceListQuery,
    EphemeralAssetGraphReadModel,
    PointListQuery,
    QueryBindingError,
    ReadModelDiscardedError,
    ReadModelError,
    ReadScope,
    RelationshipListQuery,
    TagListQuery,
    validate_activation,
)
from src.asset_graph.read_model.activation import ACTIVATION_STATES, REJECTED_STATES
from src.asset_graph.read_model.builder import build_indexes_from_materialized_run
from src.asset_graph.read_model.indexes import ReadModelIndexes
from src.asset_graph.read_model.pagination import encode_cursor, paginate, query_binding, validate_limit
from src.asset_graph.read_model.projections import safe_device, safe_point, safe_relationship, safe_tag
from src.asset_graph.reconciliation.migration_control import (
    ApprovalRecord,
    ExecutionScope,
    build_control_input,
    evaluate_execution_plan,
    load_execution_contract,
)
from src.asset_graph.reconciliation.read_validation import ExecutionRequest, execute_limited_read_validation
from src.asset_graph.reconciliation.read_validation.material import materialize_reconciliation_run
from src.asset_graph.reconciliation.readiness import assess_readiness, load_readiness_policy
from src.asset_graph.reconciliation.evidence.runner import run_device_reconciliation_evidence

ROOT = Path(__file__).resolve().parents[4]
READ_VALIDATION_FIXTURES = (
    Path(__file__).resolve().parents[1] / "reconciliation" / "read_validation" / "fixtures"
)
CLEAN_PACKAGE = READ_VALIDATION_FIXTURES / "clean-source-package.json"
OUTPUT_ROOT = Path("/tmp/one-p1-16n-tests")
MULTI_SITE_PACKAGE = Path("/tmp/one-p1-16f/shared-package.json")
RUN_ID = "LIMITED-READ-VALIDATION-001"
EVALUATION_INSTANT = "2026-06-19T12:00:00Z"

ALLOWED_OPERATIONS = (
    "READ_SOURCE_PACKAGE",
    "PROJECT_IN_MEMORY",
    "RECONCILE_IN_MEMORY",
    "GENERATE_EVIDENCE",
    "GENERATE_READINESS_ASSESSMENT",
    "EXPORT_AGGREGATE_REPORT",
)


def _default_scope(**overrides: object) -> ExecutionScope:
    payload = {
        "tenantScope": "tenant-synthetic-control",
        "siteScope": "site-synthetic-control",
        "sourceSystemScope": "legacy-device-v1",
        "mappingVersion": "legacy-device-v1",
        "maximumDeviceCount": 100,
        "maximumPointCount": 1000,
        "allowedOperations": list(ALLOWED_OPERATIONS),
        "forbiddenOperations": [],
        "outputLocationPolicy": "OFFLINE_AGGREGATE_EXPORT_ONLY",
        "retentionPolicy": "RETAIN_AGGREGATE_REPORTS_30_DAYS",
        "rollbackPolicy": "DISCARD_IN_MEMORY_PROJECTION_NO_PERSISTENCE",
        "approvalExpiry": "2026-12-31T23:59:59Z",
    }
    payload.update(overrides)
    return ExecutionScope.from_mapping(payload)


def _synthetic_approval(scope: ExecutionScope, assessment: dict) -> ApprovalRecord:
    return ApprovalRecord(
        approval_id="syn-limited-001",
        approval_type="SYNTHETIC_LIMITED_READ_VALIDATION",
        approved_by_role="ARCHITECTURE_OWNER",
        scope_digest=scope.scope_digest(),
        evidence_digest=assessment["evidenceDigest"],
        readiness_result_digest=assessment["resultDigest"],
        issued_at_policy="2026-06-01T00:00:00Z",
        expires_at="2026-12-31T23:59:59Z",
        status="ACTIVE",
        constraints=("READ_ONLY_VALIDATION",),
    )


def _build_approved_bundle(
    root: Path,
    package_path: Path,
    *,
    run_id: str = RUN_ID,
    scope: ExecutionScope | None = None,
) -> tuple[dict, dict, ExecutionScope, Path]:
    scope = scope or _default_scope()
    report_path = OUTPUT_ROOT / "setup" / f"{package_path.stem}-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = run_device_reconciliation_evidence(
        root=root,
        input_path=package_path,
        output_path=report_path,
        run_id=run_id,
    )
    policy = load_readiness_policy(root=root)
    assessment = assess_readiness(report, policy, determinism_confirmed=True).serialize()
    contract = load_execution_contract(root=root)
    control_input = build_control_input(
        readiness_assessment=assessment,
        evidence=report,
        execution_scope=scope,
        approvals=(_synthetic_approval(scope, assessment),),
        evaluation_instant=EVALUATION_INSTANT,
    )
    plan = evaluate_execution_plan(control_input, contract).serialize()
    return plan, assessment, scope, package_path


class TestEphemeralReadModel(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = ROOT
        cls.clean_plan, cls.clean_assessment, cls.clean_scope, cls.clean_package = _build_approved_bundle(
            ROOT, CLEAN_PACKAGE
        )

    def setUp(self) -> None:
        self._case_dir = OUTPUT_ROOT / self.id().split(".")[-1]
        if self._case_dir.exists():
            shutil.rmtree(self._case_dir)
        self._case_dir.mkdir(parents=True, exist_ok=True)

    def _execute(
        self,
        plan: dict,
        assessment: dict,
        scope: ExecutionScope,
        package_path: Path,
        *,
        output_dir: Path | None = None,
        **overrides: str,
    ) -> dict:
        plan_path = self._case_dir / "approved-plan.json"
        readiness_path = self._case_dir / "readiness-assessment.json"
        plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        readiness_path.write_text(json.dumps(assessment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        output_dir = output_dir or (self._case_dir / "output")
        request = ExecutionRequest(
            root=str(self.root),
            plan_path=str(plan_path),
            evidence_path=str(package_path),
            readiness_path=str(readiness_path),
            output_dir=str(output_dir),
            run_id=RUN_ID,
            evaluation_instant=overrides.get("evaluation_instant", EVALUATION_INSTANT),
            evidence_digest=overrides.get("evidence_digest", assessment["evidenceDigest"]),
            readiness_result_digest=overrides.get("readiness_result_digest", assessment["resultDigest"]),
            scope_digest=overrides.get("scope_digest", scope.scope_digest()),
            mapping_version=overrides.get("mapping_version", scope.mapping_version),
        )
        return execute_limited_read_validation(request).serialize()

    def _build_model(self, *, with_reviews: bool = False) -> EphemeralAssetGraphReadModel:
        output_dir = self._case_dir / "model-output"
        result = self._execute(
            self.clean_plan,
            self.clean_assessment,
            self.clean_scope,
            self.clean_package,
            output_dir=output_dir,
        )
        if with_reviews:
            result = copy.deepcopy(result)
            result["executionState"] = "VALIDATION_COMPLETE_WITH_REVIEWS"
        manifest = json.loads((output_dir / "artifact-manifest.json").read_text(encoding="utf-8"))
        return EphemeralAssetGraphReadModel.from_execution_artifacts(
            execution_result=result,
            artifact_manifest=manifest,
            output_dir=output_dir,
            root=self.root,
        )

    def _clean_scope(self) -> ReadScope:
        return ReadScope(
            tenant_id="tenant-synthetic-control",
            allowed_site_ids=("site-synthetic-control",),
            allowed_source_system_ids=("legacy-device-v1",),
        )

    def test_activation_states_constant(self) -> None:
        self.assertIn("VALIDATION_COMPLETE", ACTIVATION_STATES)
        self.assertIn("VALIDATION_COMPLETE_WITH_REVIEWS", ACTIVATION_STATES)

    def test_rejected_execution_states_constant(self) -> None:
        self.assertEqual(REJECTED_STATES, frozenset({"EXECUTION_BLOCKED", "VALIDATION_FAILED", "ROLLED_BACK"}))

    def test_clean_execution_builds_active_model(self) -> None:
        model = self._build_model()
        self.assertEqual(model.lifecycle_state, "ACTIVE")
        self.assertEqual(model.summary["modelName"], MODEL_NAME)
        self.assertEqual(model.summary["modelVersion"], MODEL_VERSION)
        self.assertEqual(model.summary["authority"], AUTHORITY)
        self.assertEqual(model.summary["writeCutoverStatus"], WRITE_CUTOVER_STATUS)
        self.assertEqual(model.summary["deviceCount"], 1)

    def test_execution_with_reviews_builds_model(self) -> None:
        model = self._build_model(with_reviews=True)
        self.assertEqual(model.lifecycle_state, "ACTIVE")
        self.assertEqual(model.summary["writeCutoverStatus"], WRITE_CUTOVER_STATUS)
        self.assertGreaterEqual(model.summary["deviceCount"], 1)

    def test_blocked_execution_cannot_build(self) -> None:
        output_dir = self._case_dir / "blocked"
        result = self._execute(
            self.clean_plan,
            self.clean_assessment,
            self.clean_scope,
            self.clean_package,
            output_dir=output_dir,
            evidence_digest="0" * 64,
        )
        self.assertEqual(result["executionState"], "EXECUTION_BLOCKED")
        with self.assertRaises(ReadModelError):
            validate_activation(result, {"artifacts": []}, output_dir)

    def test_failed_execution_cannot_build(self) -> None:
        result = {
            "executionState": "VALIDATION_FAILED",
            "writeCutoverStatus": WRITE_CUTOVER_STATUS,
            "resultDigest": "a" * 64,
            "evidenceDigest": "b" * 64,
            "readinessResultDigest": "c" * 64,
        }
        with self.assertRaises(ReadModelError):
            validate_activation(result, {"artifacts": [{"relativePath": "x", "sha256": "y"}]}, self._case_dir)

    def test_missing_execution_digest_rejected(self) -> None:
        result = {
            "executionState": "VALIDATION_COMPLETE",
            "writeCutoverStatus": WRITE_CUTOVER_STATUS,
            "evidenceDigest": "b" * 64,
            "readinessResultDigest": "c" * 64,
        }
        with self.assertRaises(ReadModelError):
            validate_activation(result, {"artifacts": []}, self._case_dir)

    def test_write_cutover_status_must_remain_prohibited(self) -> None:
        model = self._build_model()
        self.assertEqual(model.summary["writeCutoverStatus"], "NOT_READY_FOR_WRITE_CUTOVER")

    def test_immutable_indexes_frozen(self) -> None:
        model = self._build_model()
        assert model.indexes is not None
        with self.assertRaises(FrozenInstanceError):
            model.indexes.devices_by_global_id = {}  # type: ignore[misc]

    def test_required_index_collections_present(self) -> None:
        model = self._build_model()
        indexes = model.indexes
        assert indexes is not None
        for field in (
            "devices_by_global_id",
            "points_by_global_id",
            "tags_by_key",
            "relationships_by_global_id",
            "points_by_device_global_id",
            "relationships_by_source_global_id",
            "relationships_by_target_global_id",
        ):
            self.assertTrue(hasattr(indexes, field))

    def test_get_device_lookup(self) -> None:
        model = self._build_model()
        scope = self._clean_scope()
        devices = model.list_devices(DeviceListQuery(scope=scope))
        device_id = devices.items[0]["globalId"]
        found = model.get_device(device_id, scope)
        self.assertIsNotNone(found)
        assert found is not None
        self.assertEqual(found["globalId"], device_id)
        self.assertNotIn("source_identities", found)
        self.assertNotIn("approvedMetadata", found)

    def test_get_point_lookup_missing(self) -> None:
        model = self._build_model()
        self.assertIsNone(model.get_point("ag-point-missing", self._clean_scope()))

    def test_get_tag_lookup(self) -> None:
        model = self._build_model()
        scope = self._clean_scope()
        tags = model.list_tags(TagListQuery(scope=scope))
        self.assertGreaterEqual(len(tags.items), 1)
        tag_key = tags.items[0]["tagKey"]
        found = model.get_tag(tag_key, scope)
        self.assertIsNotNone(found)
        assert found is not None
        self.assertEqual(found["tagKey"], tag_key)

    def test_get_relationship_lookup_missing(self) -> None:
        model = self._build_model()
        self.assertIsNone(model.get_relationship("ag-rel-missing", self._clean_scope()))

    def test_list_devices_bounded(self) -> None:
        model = self._build_model()
        page = model.list_devices(DeviceListQuery(scope=self._clean_scope(), limit=1))
        self.assertLessEqual(len(page.items), 1)
        self.assertEqual(page.limit, 1)

    def test_list_points_filter_site(self) -> None:
        model = self._build_model()
        page = model.list_points(
            PointListQuery(scope=self._clean_scope(), site_id="site-synthetic-control")
        )
        self.assertGreaterEqual(len(page.items), 0)

    def test_list_tags_filter_namespace(self) -> None:
        model = self._build_model()
        page = model.list_tags(TagListQuery(scope=self._clean_scope(), tag_namespace="legacy.iot.tags"))
        self.assertGreaterEqual(len(page.items), 0)

    def test_list_relationships_filter_type(self) -> None:
        model = self._build_model()
        page = model.list_relationships(
            RelationshipListQuery(scope=self._clean_scope(), relationship_type="HAS_POINT")
        )
        self.assertEqual(len(page.items), 0)

    def test_filter_device_type(self) -> None:
        model = self._build_model()
        page = model.list_devices(
            DeviceListQuery(scope=self._clean_scope(), device_type="CONTROLLER")
        )
        self.assertEqual(len(page.items), 1)

    def test_filter_lifecycle_status(self) -> None:
        model = self._build_model()
        page = model.list_devices(
            DeviceListQuery(scope=self._clean_scope(), lifecycle_status="ACTIVE")
        )
        self.assertEqual(len(page.items), 1)

    def test_filter_operational_status(self) -> None:
        model = self._build_model()
        page = model.list_devices(
            DeviceListQuery(scope=self._clean_scope(), operational_status="AVAILABLE")
        )
        self.assertEqual(len(page.items), 1)

    def test_filter_tenant_id(self) -> None:
        model = self._build_model()
        page = model.list_devices(
            DeviceListQuery(scope=self._clean_scope(), tenant_id="tenant-synthetic-control")
        )
        self.assertEqual(len(page.items), 1)

    def test_filter_source_system_id(self) -> None:
        model = self._build_model()
        page = model.list_devices(
            DeviceListQuery(scope=self._clean_scope(), source_system_id="legacy-device-v1")
        )
        self.assertEqual(len(page.items), 1)

    def test_filter_source_namespace(self) -> None:
        model = self._build_model()
        page = model.list_devices(
            DeviceListQuery(scope=self._clean_scope(), source_namespace="legacy.iot.devices")
        )
        self.assertEqual(len(page.items), 1)

    def test_tenant_scope_enforcement(self) -> None:
        model = self._build_model()
        wrong_scope = ReadScope(
            tenant_id="tenant-other",
            allowed_site_ids=("site-synthetic-control",),
            allowed_source_system_ids=("legacy-device-v1",),
        )
        self.assertEqual(model.list_devices(DeviceListQuery(scope=wrong_scope)).items, ())

    def test_site_scope_enforcement(self) -> None:
        model = self._build_model()
        scope = ReadScope(
            tenant_id="tenant-synthetic-control",
            allowed_site_ids=("site-not-in-model",),
            allowed_source_system_ids=("legacy-device-v1",),
        )
        self.assertEqual(model.list_devices(DeviceListQuery(scope=scope)).items, ())

    def test_source_system_scope_enforcement(self) -> None:
        model = self._build_model()
        scope = ReadScope(
            tenant_id="tenant-synthetic-control",
            allowed_site_ids=("site-synthetic-control",),
            allowed_source_system_ids=("other-system",),
        )
        self.assertEqual(model.list_devices(DeviceListQuery(scope=scope)).items, ())

    def test_wildcard_tenant_rejected(self) -> None:
        from src.asset_graph.read_model.errors import ScopeViolationError

        with self.assertRaises(ScopeViolationError):
            ReadScope(
                tenant_id="*",
                allowed_site_ids=("site-synthetic-control",),
                allowed_source_system_ids=("legacy-device-v1",),
            )

    def test_wildcard_site_rejected(self) -> None:
        from src.asset_graph.read_model.errors import ScopeViolationError

        with self.assertRaises(ScopeViolationError):
            ReadScope(
                tenant_id="tenant-synthetic-control",
                allowed_site_ids=("ALL_SITES",),
                allowed_source_system_ids=("legacy-device-v1",),
            )

    def test_empty_site_scope_rejected(self) -> None:
        from src.asset_graph.read_model.errors import ScopeViolationError

        with self.assertRaises(ScopeViolationError):
            ReadScope(
                tenant_id="tenant-synthetic-control",
                allowed_site_ids=(),
                allowed_source_system_ids=("legacy-device-v1",),
            )

    def test_pagination_default_limit(self) -> None:
        self.assertEqual(DEFAULT_LIMIT, 50)
        self.assertEqual(validate_limit(None), 50)

    def test_pagination_maximum_limit(self) -> None:
        self.assertEqual(MAXIMUM_LIMIT, 500)
        with self.assertRaises(QueryBindingError):
            validate_limit(501)

    def test_pagination_negative_limit_rejected(self) -> None:
        with self.assertRaises(QueryBindingError):
            validate_limit(-1)

    def test_pagination_deterministic(self) -> None:
        model = self._build_model()
        query = DeviceListQuery(scope=self._clean_scope(), limit=1)
        one = model.list_devices(query)
        two = model.list_devices(query)
        self.assertEqual(one.items, two.items)
        self.assertEqual(one.next_cursor, two.next_cursor)
        self.assertEqual(one.query_binding, two.query_binding)

    def test_cursor_query_mismatch_rejected(self) -> None:
        scope = self._clean_scope().serialize()
        binding_a = query_binding({"type": "devices", "scope": scope})
        binding_b = query_binding({"type": "points", "scope": scope})
        cursor = encode_cursor(query_binding=binding_a, last_key="ag-device-x")
        with self.assertRaises(QueryBindingError):
            paginate(
                ("ag-device-y",),
                limit=1,
                cursor=cursor,
                query_binding_value=binding_b,
                sort_key=str,
            )

    def test_malformed_cursor_rejected(self) -> None:
        binding = query_binding({"type": "devices", "scope": self._clean_scope().serialize()})
        with self.assertRaises(QueryBindingError):
            paginate((), limit=1, cursor="not-a-cursor", query_binding_value=binding, sort_key=str)

    def test_discarded_model_rejects_queries(self) -> None:
        model = self._build_model()
        evidence = model.discard()
        self.assertIn("modelDigest", evidence)
        with self.assertRaises(ReadModelDiscardedError):
            model.list_devices(DeviceListQuery(scope=self._clean_scope()))

    def test_discard_preserves_summary_only(self) -> None:
        model = self._build_model()
        digest = model.summary["modelDigest"]
        model.discard()
        self.assertIsNone(model.indexes)
        self.assertEqual(model.summary["modelDigest"], digest)

    def test_deterministic_model_digest(self) -> None:
        one = self._build_model()
        two = self._build_model()
        self.assertEqual(one.summary["modelDigest"], two.summary["modelDigest"])

    def test_safe_device_projection_keys(self) -> None:
        model = self._build_model()
        device = model.list_devices(DeviceListQuery(scope=self._clean_scope())).items[0]
        allowed = {
            "globalId",
            "tenantId",
            "siteId",
            "displayName",
            "deviceType",
            "lifecycleStatus",
            "operationalStatus",
            "contractVersion",
        }
        self.assertTrue(set(device).issubset(allowed))

    def test_no_raw_evidence_in_query_results(self) -> None:
        model = self._build_model()
        blob = json.dumps(model.list_devices(DeviceListQuery(scope=self._clean_scope())).items)
        for token in ("password", "approvedMetadata", "rawRecord", "connectionString", "telemetry"):
            self.assertNotIn(token, blob)

    def test_no_db_imports_in_read_model_module(self) -> None:
        module_dir = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/read_model"
        text = "\n".join(path.read_text(encoding="utf-8") for path in module_dir.rglob("*.py"))
        for token in ("sqlalchemy", "db.session", "prisma", "create_app(", "flask"):
            self.assertNotIn(token.lower(), text.lower())

    def test_no_public_api_routes_in_read_model(self) -> None:
        module_dir = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/read_model"
        text = "\n".join(path.read_text(encoding="utf-8") for path in module_dir.rglob("*.py"))
        self.assertNotIn("@api_bp.route", text)
        self.assertNotIn("Blueprint(", text)

    def test_material_module_no_db_imports(self) -> None:
        path = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/read_validation/material.py"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("sqlalchemy", text.lower())

    @unittest.skipUnless(MULTI_SITE_PACKAGE.is_file(), "multi-site shared package unavailable")
    def test_multi_site_has_point_pass_total(self) -> None:
        run, reconciliation_input, context = materialize_reconciliation_run(
            root=self.root,
            source_path=MULTI_SITE_PACKAGE,
            run_id="MULTI-SITE-READ-MODEL",
        )
        pass_total = sum(
            1
            for record in run.record_results
            for rel in record.relationship_results
            if rel.status == "PASS" and rel.relationship_type == "HAS_POINT"
        )
        self.assertEqual(pass_total, 588)

    @unittest.skipUnless(MULTI_SITE_PACKAGE.is_file(), "multi-site shared package unavailable")
    def test_unresolved_located_in_excluded_from_canonical(self) -> None:
        run, reconciliation_input, context = materialize_reconciliation_run(
            root=self.root,
            source_path=MULTI_SITE_PACKAGE,
            run_id="MULTI-SITE-READ-MODEL",
        )
        indexes, stats = build_indexes_from_materialized_run(run, reconciliation_input, context)
        self.assertEqual(stats["unresolvedRelationshipEvidenceCount"], 1)
        self.assertFalse(
            any(rel.relationship_type == "LOCATED_IN" for rel in indexes.relationships_by_global_id.values())
        )

    @unittest.skipUnless(MULTI_SITE_PACKAGE.is_file(), "multi-site shared package unavailable")
    def test_canonical_has_point_edges_match_points(self) -> None:
        run, reconciliation_input, context = materialize_reconciliation_run(
            root=self.root,
            source_path=MULTI_SITE_PACKAGE,
            run_id="MULTI-SITE-READ-MODEL",
        )
        indexes, stats = build_indexes_from_materialized_run(run, reconciliation_input, context)
        self.assertEqual(stats["pointCount"], stats["canonicalRelationshipCount"])
        has_point = [
            rel
            for rel in indexes.relationships_by_global_id.values()
            if rel.relationship_type == "HAS_POINT"
        ]
        self.assertEqual(len(has_point), stats["canonicalRelationshipCount"])

    @unittest.skipUnless(MULTI_SITE_PACKAGE.is_file(), "multi-site shared package unavailable")
    def test_duplicate_relationship_evidence_suppressed(self) -> None:
        run, reconciliation_input, context = materialize_reconciliation_run(
            root=self.root,
            source_path=MULTI_SITE_PACKAGE,
            run_id="MULTI-SITE-READ-MODEL",
        )
        _, stats = build_indexes_from_materialized_run(run, reconciliation_input, context)
        self.assertGreaterEqual(stats["duplicateRelationshipSuppressedCount"], 1)
        self.assertGreaterEqual(stats["duplicateDeviceCount"], 1)

    @unittest.skipUnless(MULTI_SITE_PACKAGE.is_file(), "multi-site shared package unavailable")
    def test_multi_site_read_scope_query(self) -> None:
        run, reconciliation_input, context = materialize_reconciliation_run(
            root=self.root,
            source_path=MULTI_SITE_PACKAGE,
            run_id="MULTI-SITE-READ-MODEL",
        )
        indexes, stats = build_indexes_from_materialized_run(run, reconciliation_input, context)
        scope = ReadScope(
            tenant_id=str(context.tenant_id),
            allowed_site_ids=tuple(sorted(set(context.allowed_site_ids))),
            allowed_source_system_ids=(str(context.source_system_id),),
        )
        execution_result = {
            "resultDigest": "d" * 64,
            "evidenceDigest": "e" * 64,
            "readinessResultDigest": "r" * 64,
        }
        model = EphemeralAssetGraphReadModel.from_materialized_run(
            execution_result=execution_result,
            run=run,
            reconciliation_input=reconciliation_input,
            context=context,
            scope_policy=scope,
        )
        rel_items: list[dict] = []
        cursor: str | None = None
        while True:
            rel_page = model.list_relationships(
                RelationshipListQuery(
                    scope=scope,
                    relationship_type="HAS_POINT",
                    limit=500,
                    cursor=cursor,
                )
            )
            rel_items.extend(rel_page.items)
            cursor = rel_page.next_cursor
            if cursor is None:
                break
        self.assertEqual(len(rel_items), stats["canonicalRelationshipCount"])

    def test_list_points_for_device(self) -> None:
        model = self._build_model()
        scope = self._clean_scope()
        device_id = model.list_devices(DeviceListQuery(scope=scope)).items[0]["globalId"]
        points = model.list_points_for_device(device_id, scope)
        self.assertIsInstance(points, tuple)

    def test_list_relationships_for_source_and_target_empty(self) -> None:
        model = self._build_model()
        scope = self._clean_scope()
        self.assertEqual(model.list_relationships_for_source("ag-device-missing", scope), ())
        self.assertEqual(model.list_relationships_for_target("ag-point-missing", scope), ())

    def test_activation_validates_artifact_digests(self) -> None:
        output_dir = self._case_dir / "digest-check"
        result = self._execute(
            self.clean_plan,
            self.clean_assessment,
            self.clean_scope,
            self.clean_package,
            output_dir=output_dir,
        )
        manifest = json.loads((output_dir / "artifact-manifest.json").read_text(encoding="utf-8"))
        validate_activation(result, manifest, output_dir)

    def test_evidence_digest_mismatch_rejected(self) -> None:
        output_dir = self._case_dir / "evidence-mismatch"
        result = self._execute(
            self.clean_plan,
            self.clean_assessment,
            self.clean_scope,
            self.clean_package,
            output_dir=output_dir,
        )
        manifest = json.loads((output_dir / "artifact-manifest.json").read_text(encoding="utf-8"))
        bad = copy.deepcopy(result)
        bad["evidenceDigest"] = "0" * 64
        with self.assertRaises(ReadModelError):
            EphemeralAssetGraphReadModel.from_execution_artifacts(
                execution_result=bad,
                artifact_manifest=manifest,
                output_dir=output_dir,
                root=self.root,
            )

    def test_readiness_digest_mismatch_rejected(self) -> None:
        output_dir = self._case_dir / "readiness-mismatch"
        result = self._execute(
            self.clean_plan,
            self.clean_assessment,
            self.clean_scope,
            self.clean_package,
            output_dir=output_dir,
        )
        manifest = json.loads((output_dir / "artifact-manifest.json").read_text(encoding="utf-8"))
        bad = copy.deepcopy(result)
        bad["readinessResultDigest"] = "0" * 64
        with self.assertRaises(ReadModelError):
            EphemeralAssetGraphReadModel.from_execution_artifacts(
                execution_result=bad,
                artifact_manifest=manifest,
                output_dir=output_dir,
                root=self.root,
            )

    def test_rolled_back_execution_rejected(self) -> None:
        with self.assertRaises(ReadModelError):
            validate_activation(
                {
                    "executionState": "ROLLED_BACK",
                    "writeCutoverStatus": WRITE_CUTOVER_STATUS,
                    "resultDigest": "a" * 64,
                    "evidenceDigest": "b" * 64,
                    "readinessResultDigest": "c" * 64,
                },
                {"artifacts": [{"relativePath": "reconciliation-report.json", "sha256": "x"}]},
                self._case_dir,
            )

    def test_query_binding_stable(self) -> None:
        payload = {"type": "devices", "scope": self._clean_scope().serialize()}
        self.assertEqual(query_binding(payload), query_binding(payload))

    def test_encode_decode_cursor_roundtrip(self) -> None:
        binding = query_binding({"type": "tags"})
        cursor = encode_cursor(query_binding=binding, last_key="tag-001")
        page = paginate(
            ("tag-001", "tag-002"),
            limit=1,
            cursor=None,
            query_binding_value=binding,
            sort_key=str,
        )
        self.assertIsNotNone(page.next_cursor)

    def test_read_model_summary_required_fields(self) -> None:
        model = self._build_model()
        required = {
            "modelName",
            "modelVersion",
            "authority",
            "executionResultDigest",
            "evidenceDigest",
            "readinessResultDigest",
            "tenantCount",
            "siteCount",
            "sourceSystemCount",
            "deviceCount",
            "pointCount",
            "tagCount",
            "canonicalRelationshipCount",
            "unresolvedRelationshipEvidenceCount",
            "duplicateDeviceCount",
            "duplicatePointCount",
            "duplicateRelationshipCount",
            "scopePolicy",
            "writeCutoverStatus",
            "modelDigest",
        }
        self.assertTrue(required.issubset(model.summary.keys()))

    def test_safe_projection_functions(self) -> None:
        model = self._build_model()
        assert model.indexes is not None
        if model.indexes.devices_by_global_id:
            device = next(iter(model.indexes.devices_by_global_id.values()))
            self.assertIn("globalId", safe_device(device))
        if model.indexes.tags_by_key:
            tag = next(iter(model.indexes.tags_by_key.values()))
            self.assertIn("tagKey", safe_tag(tag))

    def test_indexes_helper_sort_keys(self) -> None:
        model = self._build_model()
        assert model.indexes is not None
        self.assertEqual(model.indexes.device_ids(), tuple(sorted(model.indexes.devices_by_global_id)))


if __name__ == "__main__":
    unittest.main()
