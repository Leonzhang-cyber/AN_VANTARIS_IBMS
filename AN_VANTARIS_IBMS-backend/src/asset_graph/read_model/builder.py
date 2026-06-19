"""Build ephemeral read model indexes from validated execution artifacts."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping

from ..compatibility import LegacyDeviceReadCompatibilityFacade
from ..compatibility.models import ProjectionContext
from ..models import AssetRelationship, Device, Point, Tag
from ..reconciliation.models import ReconciliationInput, ReconciliationRun, sha256_digest
from ..reconciliation.read_validation.material import materialize_reconciliation_run
from .activation import validate_activation
from .errors import ReadModelError
from .indexes import ReadModelIndexes
from .scope import ReadScope

MODEL_NAME = "VANTARIS ONE Ephemeral Asset Graph Read Model"
MODEL_VERSION = "1.0.0"
AUTHORITY = "ONE-A5-P1-16N"
WRITE_CUTOVER_STATUS = "NOT_READY_FOR_WRITE_CUTOVER"


def _source_system_for_object(item: Device | Point | Tag) -> str | None:
    identities = getattr(item, "source_identities", None)
    if identities:
        return str(identities[0].source_system_id)
    source_system_id = getattr(item, "source_system_id", None)
    return str(source_system_id) if source_system_id else None


def build_indexes_from_materialized_run(
    run: ReconciliationRun,
    reconciliation_input: ReconciliationInput,
    context: ProjectionContext,
) -> tuple[ReadModelIndexes, dict[str, int]]:
    facade = LegacyDeviceReadCompatibilityFacade()
    record_pairs = list(zip(reconciliation_input.devices, run.record_results))
    if len(record_pairs) != len(run.record_results):
        raise ReadModelError("reconciliation run record count mismatch")
    devices: dict[str, Device] = {}
    points: dict[str, Point] = {}
    tags: dict[str, Tag] = {}
    relationships: dict[str, AssetRelationship] = {}
    points_by_device: dict[str, list[str]] = defaultdict(list)
    rel_by_source: dict[str, list[str]] = defaultdict(list)
    rel_by_target: dict[str, list[str]] = defaultdict(list)
    duplicate_counts = {
        "duplicateDeviceCount": 0,
        "duplicatePointCount": 0,
        "duplicateRelationshipCount": 0,
        "duplicateRelationshipSuppressedCount": 0,
    }
    unresolved_relationship_evidence_count = 0
    seen_active_pairs: set[tuple[str, str, str]] = set()

    ordered_pairs = sorted(
        record_pairs,
        key=lambda pair: str(getattr(pair[0], "source_id", "")),
    )
    for source, record in ordered_pairs:
        source_id = str(getattr(source, "source_id", ""))
        fields = reconciliation_input.fields_by_device.get(source_id, ())
        projection = facade.project_device(source, context, fields)
        if record is None:
            continue
        unresolved_relationship_evidence_count += sum(
            1 for rel in record.relationship_results if rel.status == "REVIEW_REQUIRED"
        )
        if projection.canonical_device is None:
            continue
        device = projection.canonical_device
        device_key = str(device.global_id)
        if device_key in devices and devices[device_key] != device:
            duplicate_counts["duplicateDeviceCount"] += 1
        else:
            devices[device_key] = device

        for point in projection.canonical_points:
            point_key = str(point.global_id)
            if point_key in points and points[point_key] != point:
                duplicate_counts["duplicatePointCount"] += 1
                continue
            points[point_key] = point
            points_by_device[str(point.device_id)].append(point_key)

        for tag in projection.canonical_tags:
            tag_key = str(tag.tag_id)
            if tag_key in tags and tags[tag_key] != tag:
                continue
            tags[tag_key] = tag

        pass_keys = {
            (rel.relationship_type, rel.source_id, rel.target_id)
            for rel in record.relationship_results
            if rel.status == "PASS" and rel.source_id and rel.target_id
        }
        for relationship in projection.relationships:
            rel_key = (
                relationship.relationship_type,
                str(relationship.source_global_id),
                str(relationship.target_global_id),
            )
            if rel_key not in pass_keys:
                continue
            active_pair = rel_key
            if active_pair in seen_active_pairs:
                duplicate_counts["duplicateRelationshipSuppressedCount"] += 1
                continue
            seen_active_pairs.add(active_pair)
            relationship_id = str(relationship.relationship_id)
            if relationship_id in relationships and relationships[relationship_id] != relationship:
                duplicate_counts["duplicateRelationshipCount"] += 1
                continue
            if str(relationship.source_global_id) not in devices and str(relationship.source_global_id) not in points:
                duplicate_counts["duplicateRelationshipCount"] += 1
                continue
            if str(relationship.target_global_id) not in devices and str(relationship.target_global_id) not in points:
                duplicate_counts["duplicateRelationshipCount"] += 1
                continue
            relationships[relationship_id] = relationship
            rel_by_source[str(relationship.source_global_id)].append(relationship_id)
            rel_by_target[str(relationship.target_global_id)].append(relationship_id)

    indexes = ReadModelIndexes(
        devices_by_global_id=devices,
        points_by_global_id=points,
        tags_by_key=tags,
        relationships_by_global_id=relationships,
        points_by_device_global_id={key: tuple(sorted(set(values))) for key, values in points_by_device.items()},
        relationships_by_source_global_id={key: tuple(sorted(set(values))) for key, values in rel_by_source.items()},
        relationships_by_target_global_id={key: tuple(sorted(set(values))) for key, values in rel_by_target.items()},
    )
    stats = {
        **duplicate_counts,
        "unresolvedRelationshipEvidenceCount": unresolved_relationship_evidence_count,
        "tenantCount": len({str(item.tenant_id) for item in devices.values()}),
        "siteCount": len({str(item.site_id) for item in devices.values() if item.site_id}),
        "sourceSystemCount": len(
            {
                value
                for value in (_source_system_for_object(item) for item in devices.values())
                if value
            }
        ),
        "deviceCount": len(devices),
        "pointCount": len(points),
        "tagCount": len(tags),
        "canonicalRelationshipCount": len(relationships),
    }
    return indexes, stats


def build_read_model_summary(
    *,
    execution_result: Mapping[str, Any],
    indexes: ReadModelIndexes,
    stats: Mapping[str, int],
    scope_policy: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "modelName": MODEL_NAME,
        "modelVersion": MODEL_VERSION,
        "authority": AUTHORITY,
        "executionResultDigest": execution_result.get("resultDigest"),
        "evidenceDigest": execution_result.get("evidenceDigest"),
        "readinessResultDigest": execution_result.get("readinessResultDigest"),
        "tenantCount": stats.get("tenantCount", 0),
        "siteCount": stats.get("siteCount", 0),
        "sourceSystemCount": stats.get("sourceSystemCount", 0),
        "deviceCount": stats.get("deviceCount", 0),
        "pointCount": stats.get("pointCount", 0),
        "tagCount": stats.get("tagCount", 0),
        "canonicalRelationshipCount": stats.get("canonicalRelationshipCount", 0),
        "unresolvedRelationshipEvidenceCount": stats.get("unresolvedRelationshipEvidenceCount", 0),
        "duplicateDeviceCount": stats.get("duplicateDeviceCount", 0),
        "duplicatePointCount": stats.get("duplicatePointCount", 0),
        "duplicateRelationshipCount": stats.get("duplicateRelationshipCount", 0),
        "scopePolicy": dict(scope_policy),
        "writeCutoverStatus": WRITE_CUTOVER_STATUS,
    }
    payload["modelDigest"] = sha256_digest({key: value for key, value in payload.items() if key != "modelDigest"})
    return payload


def build_ephemeral_read_model_from_execution(
    *,
    execution_result: Mapping[str, Any],
    artifact_manifest: Mapping[str, Any],
    output_dir: Path,
    root: Path,
) -> tuple[ReadModelIndexes, dict[str, Any], ReconciliationRun, ReconciliationInput, ProjectionContext]:
    validate_activation(execution_result, artifact_manifest, output_dir)
    reconciliation = json.loads((output_dir / "reconciliation-report.json").read_text(encoding="utf-8"))
    input_path = root / reconciliation["inputPackage"]["path"]
    run, reconciliation_input, context = materialize_reconciliation_run(
        root=root,
        source_path=input_path,
        run_id=str(reconciliation.get("runId", execution_result.get("runId", ""))),
    )
    if reconciliation.get("resultDigest") != execution_result.get("evidenceDigest"):
        raise ReadModelError("materialized evidence digest mismatch")
    indexes, stats = build_indexes_from_materialized_run(run, reconciliation_input, context)
    allowed_sites = tuple(sorted(set(context.allowed_site_ids))) if context.allowed_site_ids else (
        (str(context.site_id),) if context.site_id else tuple()
    )
    if not allowed_sites and context.site_id:
        allowed_sites = (str(context.site_id),)
    summary = build_read_model_summary(
        execution_result=execution_result,
        indexes=indexes,
        stats=stats,
        scope_policy=ReadScope(
            tenant_id=str(context.tenant_id),
            allowed_site_ids=allowed_sites or ("__none__",),
            allowed_source_system_ids=(str(context.source_system_id),),
        ).serialize(),
    )
    return indexes, summary, run, reconciliation_input, context
