"""Immutable machine-readable reconciliation inputs and results."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional, Tuple

from ..compatibility.models import LegacyDeviceSnapshot, LegacyFieldSnapshot, ProjectionContext
from .constants import DEFAULT_CUTOVER_DECISION


def _json_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    if hasattr(value, "serialize"):
        return json.loads(value.serialize())
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    return value


def canonical_json(value: Any) -> str:
    if hasattr(value, "__dataclass_fields__"):
        value = asdict(value)
    return json.dumps(_json_value(value), sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def sha256_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ReconciliationInput:
    devices: Tuple[LegacyDeviceSnapshot | Mapping[str, Any], ...]
    fields_by_device: Mapping[str, Tuple[LegacyFieldSnapshot | Mapping[str, Any], ...]]
    context: ProjectionContext
    mapping_version: str
    projection_configuration: Tuple[Tuple[str, str], ...] = ()


@dataclass(frozen=True)
class FieldCoverage:
    required_field_coverage: str
    safe_source_field_coverage: str
    optional_field_coverage: str
    required_numerator: int
    required_denominator: int
    safe_source_numerator: int
    safe_source_denominator: int
    optional_numerator: int
    optional_denominator: int


@dataclass(frozen=True)
class RelationshipReconciliationResult:
    relationship_type: str
    status: str
    source_id: Optional[str]
    target_id: Optional[str]
    message: str
    cutover_blocking: bool = False


@dataclass(frozen=True)
class PointReconciliationResult:
    source_object_id: str
    classification: str
    canonical_global_id: Optional[str]
    device_global_id: Optional[str]
    unit_status: str
    data_type_status: str
    access_mode_status: str
    warnings: Tuple[str, ...] = ()
    blockers: Tuple[str, ...] = ()


@dataclass(frozen=True)
class DimensionResult:
    dimension_id: str
    status: str
    severity: str
    expected: str
    actual: str
    difference: str
    source_ids: Tuple[str, ...] = ()
    canonical_ids: Tuple[str, ...] = ()
    message: str = ""
    cutover_blocking: bool = False


@dataclass(frozen=True)
class RecordReconciliationResult:
    source_object_type: str
    source_object_id: str
    source_identity: Optional[str]
    canonical_global_id: Optional[str]
    projection_status: str
    mapped_fields: Tuple[str, ...]
    defaulted_fields: Tuple[str, ...]
    omitted_fields: Tuple[str, ...]
    review_fields: Tuple[str, ...]
    prohibited_fields_detected: Tuple[str, ...]
    warnings: Tuple[str, ...]
    reviews: Tuple[str, ...]
    point_results: Tuple[PointReconciliationResult, ...]
    tag_keys: Tuple[str, ...]
    relationship_results: Tuple[RelationshipReconciliationResult, ...]
    field_coverage: FieldCoverage
    projection_digest: str
    cutover_blockers: Tuple[str, ...]


@dataclass(frozen=True)
class ReconciliationSummary:
    total_records: int
    projected_records: int
    warning_count: int
    review_count: int
    blocker_count: int
    prohibited_excluded_count: int


@dataclass(frozen=True)
class ReconciliationRun:
    run_id: str
    mapping_version: str
    tenant_id: str
    site_id: Optional[str]
    source_system_id: str
    input_digest: str
    result_digest: str
    source_counts: Tuple[Tuple[str, int], ...]
    projection_counts: Tuple[Tuple[str, int], ...]
    dimension_results: Tuple[DimensionResult, ...]
    record_results: Tuple[RecordReconciliationResult, ...]
    summary: ReconciliationSummary
    cutover_decision: str = DEFAULT_CUTOVER_DECISION

    def serialize(self) -> str:
        return canonical_json(self)


@dataclass(frozen=True)
class RunComparison:
    identical_except_run_id: bool
    mapping_version_changed: bool
    source_ids_added: Tuple[str, ...]
    source_ids_removed: Tuple[str, ...]
    global_ids_changed: Tuple[str, ...]
    projection_digests_changed: Tuple[str, ...]
    warning_count_difference: int
    review_count_difference: int
    blocker_count_difference: int
    relationship_changes: Tuple[str, ...]
    field_coverage_regressions: Tuple[str, ...]
