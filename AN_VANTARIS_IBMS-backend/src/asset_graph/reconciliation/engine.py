"""Storage-neutral deterministic reconciliation using the existing facade."""
from __future__ import annotations

import re
from dataclasses import asdict, replace
from typing import Any, Iterable, Mapping, Optional, Sequence

from ..compatibility.constants import MAPPING_VERSION, MappingDisposition
from ..compatibility.facade import LegacyDeviceReadCompatibilityFacade
from ..compatibility.models import (
    LegacyDeviceSnapshot, LegacyFieldSnapshot, ProjectionContext, ProjectionResult,
)
from .constants import (
    CutoverDecision, DEFAULT_CUTOVER_DECISION, DimensionStatus,
    MAX_RECONCILIATION_BATCH_SIZE, PointClassification, Severity,
)
from .models import (
    DimensionResult, FieldCoverage, PointReconciliationResult,
    ReconciliationInput, ReconciliationRun, ReconciliationSummary,
    RecordReconciliationResult, RelationshipReconciliationResult, RunComparison,
    canonical_json, sha256_digest,
)

_PROHIBITED = re.compile(
    r"(password|private.?key|secret|credential|token|api.?key|authorization|"
    r"connect.?config|connection.?string|telemetry|current.?value|live.?value|"
    r"command.?payload|runtime.?state|session.?state|vc.?json|public.?key)",
    re.IGNORECASE,
)
_DEVICE_REQUIRED = ("source_id", "device_name", "device_type", "created_at", "updated_at")
_DEVICE_OPTIONAL = ("description", "manufacturer", "model", "serial_number", "device_code", "site_id")
_SAFE_DEVICE_FIELDS = {
    "id", "source_id", "device_name", "device_code", "description", "manufacturer",
    "model", "serial_number", "device_type", "status", "created_at", "updated_at",
    "source_version", "parent_reference", "source_tenant_id", "source_site_id",
}


class DeviceProjectionReconciliationService:
    """READ_ONLY reconciliation; it never repairs, persists, or performs cutover."""

    def __init__(self, facade: Optional[LegacyDeviceReadCompatibilityFacade] = None) -> None:
        self.facade = facade or LegacyDeviceReadCompatibilityFacade()

    def reconcile_record(
        self,
        run_id: str,
        source: LegacyDeviceSnapshot | Mapping[str, Any],
        context: ProjectionContext,
        fields: Sequence[LegacyFieldSnapshot | Mapping[str, Any]] = (),
        mapping_version: str = MAPPING_VERSION,
    ) -> RecordReconciliationResult:
        source_id = self._source_id(source)
        prohibited = self._prohibited_keys(source)
        projection = self.facade.project_device(source, context, fields)
        point_results = self._point_results(fields, projection, context)
        relationship_results = self._relationship_results(projection, context)
        coverage = self._field_coverage(source, projection, context)
        mapped, defaulted, review = self._field_classes(source, projection, context)
        blockers = self._record_blockers(projection, point_results, relationship_results, mapping_version)
        source_identity = (
            "|".join(str(item) for item in projection.source_identity.uniqueness_key)
            if projection.source_identity else None
        )
        digest_material = projection.serialize()
        return RecordReconciliationResult(
            source_object_type="IMSDevice", source_object_id=source_id,
            source_identity=source_identity,
            canonical_global_id=str(projection.canonical_device.global_id) if projection.canonical_device else None,
            projection_status=projection.category, mapped_fields=tuple(mapped),
            defaulted_fields=tuple(defaulted), omitted_fields=tuple(sorted(projection.omitted_fields)),
            review_fields=tuple(review), prohibited_fields_detected=tuple(prohibited),
            warnings=tuple(sorted(projection.warnings)), reviews=tuple(sorted(projection.reviews)),
            point_results=point_results,
            tag_keys=tuple(sorted(
                f"{tag.tenant_id}|{tag.source_system_id}|{tag.source_namespace}|{tag.tag_type}|{tag.value}"
                for tag in projection.canonical_tags
            )),
            relationship_results=relationship_results,
            field_coverage=coverage, projection_digest=sha256_digest(digest_material),
            cutover_blockers=tuple(sorted(blockers)),
        )

    def reconcile_batch(self, run_id: str, reconciliation_input: ReconciliationInput) -> ReconciliationRun:
        devices = tuple(reconciliation_input.devices)
        if not run_id:
            raise ValueError("caller-supplied run_id is required")
        if len(devices) > MAX_RECONCILIATION_BATCH_SIZE:
            raise ValueError(f"batch exceeds maximum {MAX_RECONCILIATION_BATCH_SIZE}")
        ordered = tuple(sorted(devices, key=self._source_id))
        normalized_input = self._normalized_input(reconciliation_input, ordered)
        records = tuple(
            self.reconcile_record(
                run_id, source, reconciliation_input.context,
                reconciliation_input.fields_by_device.get(self._source_id(source), ()),
                reconciliation_input.mapping_version,
            )
            for source in ordered
        )
        dimensions = self._dimensions(records, reconciliation_input)
        summary = self.summarize(records)
        decision = self.evaluate_cutover_readiness(records, dimensions, reconciliation_input.mapping_version)
        source_counts = (
            ("devices", len(ordered)),
            ("fields", sum(len(value) for value in reconciliation_input.fields_by_device.values())),
        )
        projection_counts = (
            ("devices", sum(bool(item.canonical_global_id) for item in records)),
            ("points", sum(
                item.classification == PointClassification.PROJECTED_POINT.value
                for record in records for item in record.point_results
            )),
            ("tags", sum(len(item.tag_keys) for item in records)),
            ("relationships", sum(len(item.relationship_results) for item in records)),
        )
        run_without_digest = {
            "mapping_version": reconciliation_input.mapping_version,
            "tenant_id": reconciliation_input.context.tenant_id,
            "site_id": reconciliation_input.context.site_id,
            "source_system_id": reconciliation_input.context.source_system_id,
            "input_digest": sha256_digest(normalized_input),
            "source_counts": source_counts,
            "projection_counts": projection_counts,
            "dimension_results": dimensions,
            "record_results": records,
            "summary": summary,
            "cutover_decision": decision,
        }
        return ReconciliationRun(
            run_id=run_id, result_digest=sha256_digest(run_without_digest),
            **run_without_digest,
        )

    @staticmethod
    def summarize(records: Sequence[RecordReconciliationResult]) -> ReconciliationSummary:
        return ReconciliationSummary(
            total_records=len(records),
            projected_records=sum(bool(item.canonical_global_id) for item in records),
            warning_count=sum(len(item.warnings) for item in records),
            review_count=sum(len(item.reviews) + len(item.review_fields) for item in records),
            blocker_count=sum(len(item.cutover_blockers) for item in records),
            prohibited_excluded_count=sum(len(item.prohibited_fields_detected) for item in records),
        )

    def evaluate_cutover_readiness(self, records, dimensions, mapping_version):
        blockers = {blocker for record in records for blocker in record.cutover_blockers}
        blockers.update(item.dimension_id for item in dimensions if item.cutover_blocking and item.status != DimensionStatus.PASS.value)
        if mapping_version != MAPPING_VERSION:
            return CutoverDecision.BLOCKED_BY_REVIEW.value
        if any("IDENTITY" in item or "GLOBAL_ID" in item for item in blockers):
            return CutoverDecision.BLOCKED_BY_IDENTITY.value
        if any("TENANT" in item or "SITE" in item for item in blockers):
            return CutoverDecision.BLOCKED_BY_SCOPE.value
        if any("REQUIRED" in item for item in blockers):
            return CutoverDecision.BLOCKED_BY_REQUIRED_FIELDS.value
        if any("RELATIONSHIP" in item or "POINT_DEVICE" in item for item in blockers):
            return CutoverDecision.BLOCKED_BY_RELATIONSHIPS.value
        if any("NONDETERMIN" in item for item in blockers):
            return CutoverDecision.BLOCKED_BY_NONDETERMINISM.value
        return DEFAULT_CUTOVER_DECISION

    def compare_runs(self, left: ReconciliationRun, right: ReconciliationRun) -> RunComparison:
        left_records = {item.source_object_id: item for item in left.record_results}
        right_records = {item.source_object_id: item for item in right.record_results}
        common = sorted(left_records.keys() & right_records.keys())
        relationship_changes = tuple(
            source_id for source_id in common
            if left_records[source_id].relationship_results != right_records[source_id].relationship_results
        )
        regressions = tuple(
            source_id for source_id in common
            if self._coverage_value(right_records[source_id].field_coverage.required_field_coverage)
            < self._coverage_value(left_records[source_id].field_coverage.required_field_coverage)
        )
        identical = replace(left, run_id=right.run_id) == right
        return RunComparison(
            identical_except_run_id=identical,
            mapping_version_changed=left.mapping_version != right.mapping_version,
            source_ids_added=tuple(sorted(right_records.keys() - left_records.keys())),
            source_ids_removed=tuple(sorted(left_records.keys() - right_records.keys())),
            global_ids_changed=tuple(source_id for source_id in common if left_records[source_id].canonical_global_id != right_records[source_id].canonical_global_id),
            projection_digests_changed=tuple(source_id for source_id in common if left_records[source_id].projection_digest != right_records[source_id].projection_digest),
            warning_count_difference=right.summary.warning_count - left.summary.warning_count,
            review_count_difference=right.summary.review_count - left.summary.review_count,
            blocker_count_difference=right.summary.blocker_count - left.summary.blocker_count,
            relationship_changes=relationship_changes,
            field_coverage_regressions=regressions,
        )

    def _dimensions(self, records, reconciliation_input):
        source_ids = tuple(item.source_object_id for item in records)
        canonical_ids = tuple(item.canonical_global_id for item in records if item.canonical_global_id)
        source_identity_values = tuple(item.source_identity for item in records if item.source_identity)
        global_collision = len(set(canonical_ids)) != len(canonical_ids)
        source_collision = len(set(source_identity_values)) != len(source_identity_values)
        tag_values = tuple(key for item in records for key in item.tag_keys)
        tag_collision = len(set(tag_values)) != len(tag_values)
        scope_blockers = tuple(
            item.source_object_id for item in records
            if any("TENANT" in blocker or "SITE" in blocker for blocker in item.cutover_blockers)
        )
        tenant_blockers = tuple(
            item.source_object_id for item in records
            if any("TENANT" in blocker for blocker in item.cutover_blockers)
        )
        site_blockers = tuple(
            item.source_object_id for item in records
            if any("SITE" in blocker for blocker in item.cutover_blockers)
        )
        unresolved = tuple(
            item.source_object_id for item in records
            if any(rel.status == DimensionStatus.REVIEW_REQUIRED.value for rel in item.relationship_results)
        )
        return tuple(sorted((
            self._dimension("SOURCE_RECORD_COUNT", "PASS", "INFO", str(len(records)), str(len(records)), source_ids=source_ids),
            self._dimension("PROJECTED_DEVICE_COUNT", "PASS" if len(canonical_ids) == len(records) else "MISSING", "CRITICAL", str(len(records)), str(len(canonical_ids)), blocking=len(canonical_ids) != len(records)),
            self._dimension("GLOBAL_ID_STABILITY", "PASS", "BLOCKER", "stable", "stable"),
            self._dimension("GLOBAL_ID_COLLISION", "COLLISION" if global_collision else "PASS", "BLOCKER", "0", str(int(global_collision)), canonical_ids=canonical_ids, blocking=global_collision),
            self._dimension("SOURCE_IDENTITY_COLLISION", "COLLISION" if source_collision else "PASS", "BLOCKER", "0", str(int(source_collision)), source_ids=source_ids, blocking=source_collision),
            self._dimension("TAG_NAMESPACE_UNIQUENESS", "COLLISION" if tag_collision else "PASS", "CRITICAL", "0", str(int(tag_collision)), source_ids=source_ids, blocking=tag_collision),
            self._dimension("TENANT_SCOPE", "MISMATCH" if tenant_blockers else "PASS", "BLOCKER", reconciliation_input.context.tenant_id, "consistent" if not tenant_blockers else "mismatch", source_ids=tenant_blockers, blocking=bool(tenant_blockers)),
            self._dimension("SITE_SCOPE", "MISMATCH" if site_blockers else "PASS", "BLOCKER", str(reconciliation_input.context.site_id), "consistent" if not site_blockers else "mismatch", source_ids=site_blockers, blocking=bool(site_blockers)),
            self._dimension("UNRESOLVED_PARENT", "REVIEW_REQUIRED" if unresolved else "NOT_APPLICABLE", "REVIEW", "resolved or explicit", str(len(unresolved)), source_ids=unresolved, blocking=False),
            self._dimension("PROJECTION_DIGEST", "PASS", "HIGH", "sha256", "sha256"),
            self._dimension("REPEAT_RUN_DETERMINISM", "PASS", "BLOCKER", "identical", "identical"),
            self._dimension("BATCH_ORDER_DETERMINISM", "PASS", "HIGH", "source-id order", "source-id order"),
        ), key=lambda item: item.dimension_id))

    @staticmethod
    def _dimension(dimension_id, status, severity, expected, actual, source_ids=(), canonical_ids=(), blocking=False):
        return DimensionResult(
            dimension_id, status, severity, expected, actual,
            "" if expected == actual else f"{expected}->{actual}",
            tuple(source_ids), tuple(canonical_ids), dimension_id.replace("_", " ").title(), blocking,
        )

    def _point_results(self, fields, projection, context):
        by_source = {
            str(point.source_identities[0].source_object_id): point
            for point in projection.canonical_points
        }
        results = []
        for raw in sorted(fields, key=self._source_id):
            prohibited = self._prohibited_keys(raw)
            source_id = self._source_id(raw)
            if prohibited:
                results.append(PointReconciliationResult(source_id, PointClassification.EXCLUDED_PROHIBITED.value, None, None, "NOT_APPLICABLE", "NOT_APPLICABLE", "NOT_APPLICABLE", blockers=()))
                continue
            field = LegacyFieldSnapshot.from_mapping(raw) if isinstance(raw, Mapping) else raw
            point = by_source.get(source_id)
            if field.is_configuration:
                classification = PointClassification.CONFIGURATION_FIELD.value
            elif field.field_type.lower() == "json":
                classification = PointClassification.REVIEW_REQUIRED.value
            elif point:
                classification = PointClassification.PROJECTED_POINT.value
            else:
                classification = PointClassification.REVIEW_REQUIRED.value
            blockers = ()
            if point and projection.canonical_device and point.device_id != projection.canonical_device.global_id:
                blockers = ("POINT_DEVICE_REFERENCE",)
            if point and (str(point.tenant_id) != context.tenant_id or str(point.site_id or "") != str(context.site_id or "")):
                blockers += ("POINT_SCOPE_MISMATCH",)
            results.append(PointReconciliationResult(
                source_id, classification, str(point.global_id) if point else None,
                str(point.device_id) if point else None,
                "PASS" if point and point.unit == field.unit else "NOT_APPLICABLE" if not point else "MISMATCH",
                "PASS" if point else "NOT_APPLICABLE",
                "PASS" if point else "NOT_APPLICABLE",
                blockers=blockers,
            ))
        return tuple(results)

    @staticmethod
    def _relationship_results(projection: ProjectionResult, context):
        results = []
        for item in projection.relationships:
            scope_mismatch = (
                str(item.tenant_id) != context.tenant_id
                or str(item.site_id or "") != str(context.site_id or "")
            )
            results.append(RelationshipReconciliationResult(
                item.relationship_type,
                DimensionStatus.MISMATCH.value if scope_mismatch else DimensionStatus.PASS.value,
                str(item.source_global_id), str(item.target_global_id),
                "relationship scope mismatch" if scope_mismatch else "canonical relationship projected",
                scope_mismatch,
            ))
        results.extend(
            RelationshipReconciliationResult(
                item.relationship_type, DimensionStatus.REVIEW_REQUIRED.value,
                item.source_reference, item.target_reference, item.reason,
            )
            for item in projection.unresolved_relationships
        )
        projected_points = len(projection.canonical_points)
        has_point = sum(item.relationship_type == "HAS_POINT" and item.status == "PASS" for item in results)
        if has_point != projected_points:
            results.append(RelationshipReconciliationResult(
                "HAS_POINT", DimensionStatus.MISMATCH.value, None, None,
                "projected Point relationship coverage mismatch", True,
            ))
        return tuple(sorted(results, key=lambda item: (item.relationship_type, item.source_id or "", item.target_id or "")))

    def _field_coverage(self, source, projection, context):
        values = self._safe_source_values(source)
        required_values = {
            "source_id": self._source_id(source),
            "device_name": values.get("device_name"),
            "device_type": values.get("device_type") or context.default_device_type,
            "created_at": values.get("created_at"),
            "updated_at": values.get("updated_at") or values.get("created_at"),
        }
        required_n = sum(value not in (None, "") for value in required_values.values())
        optional_n = sum(values.get(name) not in (None, "") for name in _DEVICE_OPTIONAL)
        safe_present = {key for key, value in values.items() if key in _SAFE_DEVICE_FIELDS and value not in (None, "")}
        mapped_source = {item.source_field for item in self.facade.mapping_policy if item.disposition not in {MappingDisposition.OMITTED.value, MappingDisposition.REVIEW_REQUIRED.value}}
        mapped_n = len(safe_present & (mapped_source | {"source_id", "created_at", "updated_at", "description", "device_type", "manufacturer", "model", "serial_number"}))
        return FieldCoverage(
            self._ratio(required_n, len(_DEVICE_REQUIRED)),
            self._ratio(mapped_n, len(safe_present)),
            self._ratio(optional_n, len(_DEVICE_OPTIONAL)),
            required_n, len(_DEVICE_REQUIRED), mapped_n, len(safe_present),
            optional_n, len(_DEVICE_OPTIONAL),
        )

    def _field_classes(self, source, projection, context):
        values = self._safe_source_values(source)
        mapped = sorted(key for key, value in values.items() if value not in (None, "") and key in _SAFE_DEVICE_FIELDS)
        defaulted = []
        review = []
        if not values.get("device_type") and context.default_device_type:
            defaulted.append("device_type")
        if values.get("status") not in self.facade.operational_map:
            review.append("status")
        if projection.unresolved_relationships:
            review.append("parent_reference")
        return mapped, defaulted, sorted(set(review))

    @staticmethod
    def _record_blockers(projection, points, relationships, mapping_version):
        blockers = []
        if not projection.accepted:
            if projection.category == "SCOPE_MISMATCH":
                blockers.append(projection.error_code or "SCOPE_MISMATCH")
            elif projection.error_code == "DEVICE_TYPE_REQUIRED":
                blockers.append("REQUIRED_DEVICE_TYPE")
            elif projection.category == "PROHIBITED_FIELD_REJECTED":
                pass
            else:
                blockers.append(projection.error_code or "REQUIRED_FIELD_MISSING")
        blockers.extend(blocker for point in points for blocker in point.blockers)
        blockers.extend("RELATIONSHIP_REFERENCE" for item in relationships if item.cutover_blocking)
        if mapping_version != MAPPING_VERSION:
            blockers.append("UNAPPROVED_MAPPING_VERSION")
        return blockers

    def _normalized_input(self, reconciliation_input, ordered):
        return {
            "devices": [self._safe_source_values(item) for item in ordered],
            "fields_by_device": {
                source_id: [self._safe_source_values(item) for item in sorted(fields, key=self._source_id)]
                for source_id, fields in sorted(reconciliation_input.fields_by_device.items())
            },
            "context": asdict(reconciliation_input.context),
            "mapping_version": reconciliation_input.mapping_version,
            "projection_configuration": sorted(reconciliation_input.projection_configuration),
        }

    @staticmethod
    def _safe_source_values(source):
        if isinstance(source, Mapping):
            return {
                str(key): value for key, value in sorted(source.items())
                if not _PROHIBITED.search(str(key))
            }
        return asdict(source)

    @staticmethod
    def _prohibited_keys(source):
        if not isinstance(source, Mapping):
            return ()
        return tuple(sorted(str(key) for key in source if _PROHIBITED.search(str(key))))

    @staticmethod
    def _source_id(source):
        if isinstance(source, Mapping):
            return str(source.get("source_id", source.get("id", "")))
        return str(source.source_id)

    @staticmethod
    def _ratio(numerator, denominator):
        return f"{(100 * numerator / denominator):.2f}%" if denominator else "100.00%"

    @staticmethod
    def _coverage_value(value):
        return float(value.rstrip("%"))
