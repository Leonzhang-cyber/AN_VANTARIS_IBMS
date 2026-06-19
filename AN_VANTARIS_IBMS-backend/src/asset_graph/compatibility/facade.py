"""READ_ONLY legacy Device to canonical Asset Graph projection."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Iterable, Mapping, Optional, Sequence

from ..constants import LifecycleStatus, OperationalStatus, PointAccessMode, RelationshipType, TagType
from ..models import (
    AssetRelationship, Device, GlobalId, Point, SiteId, SourceIdentity,
    SourceObjectId, SourceSystemId, Tag, TenantId,
)
from .constants import (
    CONTRACT_VERSION, MAPPING_VERSION, MAX_BATCH_SIZE, MappingDisposition,
    ProjectionCategory, READ_ONLY_COMPATIBILITY_FACADE, TEMPORARY_LEGACY_SOURCE,
)
from .models import (
    BatchProjectionResult, LegacyDeviceSnapshot, LegacyFieldSnapshot,
    MappingDecision, ProjectionContext, ProjectionResult, ProhibitedSourceField,
    UnresolvedRelationship, aware, safe_label,
)


class LegacyDeviceReadCompatibilityFacade:
    """Pure READ_ONLY projection; never queries ORM or writes any provider."""

    boundary = READ_ONLY_COMPATIBILITY_FACADE
    source_ownership = TEMPORARY_LEGACY_SOURCE
    mapping_version = MAPPING_VERSION

    mapping_policy = (
        MappingDecision("id", "source_identity", MappingDisposition.NORMALIZED.value, "namespace-qualified"),
        MappingDecision("device_name", "display_name", MappingDisposition.DIRECT.value, "required"),
        MappingDecision("device_code", "source tag", MappingDisposition.NORMALIZED.value, "non-secret only"),
        MappingDecision("status", "operational_status", MappingDisposition.NORMALIZED.value, "explicit table"),
        MappingDecision("status", "lifecycle_status", MappingDisposition.DEFAULTED.value, "legacy status is not lifecycle"),
        MappingDecision("protocol", "Device", MappingDisposition.OMITTED.value, "EDGE runtime concern"),
        MappingDecision("connect_config", "Device", MappingDisposition.OMITTED.value, "prohibited runtime configuration"),
        MappingDecision("manufacturer/model/serial", "Device", MappingDisposition.REVIEW_REQUIRED.value, "not on IMSDevice"),
    )

    lifecycle_map = {0: LifecycleStatus.ACTIVE.value, 1: LifecycleStatus.ACTIVE.value, 2: LifecycleStatus.ACTIVE.value}
    operational_map = {
        0: OperationalStatus.UNAVAILABLE.value,
        1: OperationalStatus.AVAILABLE.value,
        2: OperationalStatus.DEGRADED.value,
    }
    field_type_map = {
        "float": "NUMBER", "double": "NUMBER", "decimal": "NUMBER", "int": "INTEGER",
        "integer": "INTEGER", "bool": "BOOLEAN", "boolean": "BOOLEAN",
        "string": "STRING", "json": "JSON",
    }

    @staticmethod
    def _id(kind: str, context: ProjectionContext, source_id: str) -> GlobalId:
        material = "\x1f".join((
            MAPPING_VERSION, context.tenant_id, context.source_system_id,
            context.source_namespace, kind, source_id,
        ))
        return GlobalId(f"ag-{kind.lower()}-{hashlib.sha256(material.encode()).hexdigest()[:32]}")

    def build_source_identity(self, record: LegacyDeviceSnapshot, context: ProjectionContext) -> SourceIdentity:
        if not record.source_id or not str(record.source_id).strip():
            raise ValueError("missing stable source ID")
        if not context.tenant_id or not context.tenant_id.strip():
            raise ValueError("missing tenant context")
        if not context.source_namespace or not context.source_namespace.strip():
            raise ValueError("missing source namespace")
        if not safe_label(record.device_code):
            raise ProhibitedSourceField("external tag contains prohibited material")
        return SourceIdentity(
            SourceSystemId(context.source_system_id), SourceObjectId(str(record.source_id)),
            "IMSDevice", context.source_namespace, record.device_code, record.source_version,
        )

    @staticmethod
    def _timestamps(record: LegacyDeviceSnapshot) -> tuple[datetime, datetime]:
        created = aware(record.created_at)
        updated = aware(record.updated_at)
        if created is None and updated is None:
            raise ValueError("created_at or updated_at is required")
        created = created or updated
        updated = updated or created
        if updated < created:
            raise ValueError("updated_at precedes created_at")
        return created, updated

    def project_device(
        self,
        legacy_record: LegacyDeviceSnapshot | Mapping,
        context: ProjectionContext,
        field_records: Sequence[LegacyFieldSnapshot | Mapping] = (),
    ) -> ProjectionResult:
        try:
            record = (
                LegacyDeviceSnapshot.from_mapping(legacy_record)
                if isinstance(legacy_record, Mapping) else legacy_record
            )
            if not context.tenant_id:
                return self._failure(ProjectionCategory.INVALID_SOURCE, "MISSING_TENANT")
            if record.source_tenant_id and record.source_tenant_id != context.tenant_id:
                return self._failure(ProjectionCategory.SCOPE_MISMATCH, "TENANT_SCOPE_MISMATCH")
            if record.source_site_id and not context.allows_record_site(record.source_site_id):
                return self._failure(ProjectionCategory.SCOPE_MISMATCH, "SITE_SCOPE_MISMATCH")
            identity = self.build_source_identity(record, context)
            created, updated = self._timestamps(record)
            device_type = record.device_type or context.default_device_type
            if not device_type:
                return self._failure(ProjectionCategory.REVIEW_REQUIRED, "DEVICE_TYPE_REQUIRED")
            status_unknown = record.status not in self.operational_map
            lifecycle = self.lifecycle_map.get(record.status, LifecycleStatus.ACTIVE.value)
            operational = self.operational_map.get(record.status, OperationalStatus.UNKNOWN.value)
            device_id = self._id("device", context, record.source_id)
            effective_site = record.source_site_id or context.site_id or context.primary_site_id
            site_id = SiteId(effective_site) if effective_site else None
            device = Device(
                global_id=device_id, tenant_id=TenantId(context.tenant_id), site_id=site_id,
                asset_id=GlobalId(context.parent_asset_id) if context.parent_asset_id else None,
                display_name=record.device_name, description=record.description,
                device_type=device_type, manufacturer=record.manufacturer, model=record.model,
                serial_number=record.serial_number, lifecycle_status=lifecycle,
                operational_status=operational, classification_ids=(),
                source_identities=(identity,), created_at=created, updated_at=updated,
                contract_version=CONTRACT_VERSION,
                metadata_classification=context.metadata_classification,
            )
            points, point_reviews = self._project_points(record, device, identity, context, field_records)
            tags, tag_reviews = self.project_tags(record, device, context)
            relationships, unresolved = self.build_relationships(record, device, points, context)
            reviews = tuple(point_reviews + tag_reviews)
            warnings = ("UNKNOWN_LEGACY_STATUS",) if status_unknown else ()
            category = (
                ProjectionCategory.REVIEW_REQUIRED.value if reviews or unresolved
                else ProjectionCategory.PROJECTED_WITH_WARNINGS.value if warnings
                else ProjectionCategory.PROJECTED.value
            )
            return ProjectionResult(
                accepted=True, category=category, canonical_device=device,
                canonical_points=points, canonical_tags=tags, relationships=relationships,
                unresolved_relationships=unresolved, warnings=warnings, reviews=reviews,
                omitted_fields=("public_key", "private_key", "vc_json", "protocol", "connect_config", "extra"),
                source_identity=identity,
            )
        except ProhibitedSourceField:
            return self._failure(ProjectionCategory.PROHIBITED_FIELD_REJECTED, "PROHIBITED_FIELD")
        except (TypeError, ValueError) as exc:
            return self._failure(ProjectionCategory.INVALID_SOURCE, self._safe_error(exc))

    def _project_points(self, record, device, device_identity, context, fields):
        del device_identity
        points = []
        reviews = []
        seen_source_identities = set()
        for raw in sorted(fields, key=lambda item: str(item.get("id", item.get("source_id", ""))) if isinstance(item, Mapping) else item.source_id):
            try:
                field = LegacyFieldSnapshot.from_mapping(raw) if isinstance(raw, Mapping) else raw
            except ProhibitedSourceField:
                reviews.append("PROHIBITED_FIELD_REJECTED")
                continue
            if field.is_configuration or field.field_type.lower() == "json":
                reviews.append(f"AMBIGUOUS_FIELD:{field.source_id}")
                continue
            point_identity = SourceIdentity(
                SourceSystemId(context.source_system_id), SourceObjectId(field.source_id),
                "IMSStandardField", f"{context.source_namespace}.standard-fields",
                field.field_code, field.source_version,
            )
            if point_identity.uniqueness_key in seen_source_identities:
                reviews.append(f"POINT_SOURCE_IDENTITY_CONFLICT:{field.source_id}")
                continue
            seen_source_identities.add(point_identity.uniqueness_key)
            created = aware(field.created_at) or device.created_at
            updated = aware(field.updated_at) or device.updated_at
            access = field.access_mode or PointAccessMode.READ_ONLY.value
            if access not in {item.value for item in PointAccessMode}:
                reviews.append(f"AMBIGUOUS_ACCESS_MODE:{field.source_id}")
                continue
            points.append(Point(
                global_id=self._id("point", context, field.source_id),
                tenant_id=device.tenant_id, site_id=device.site_id, device_id=device.global_id,
                display_name=field.field_name, point_type=field.field_code.upper(),
                unit=field.unit, data_type=self.field_type_map.get(field.field_type.lower(), "STRING"),
                access_mode=access, lifecycle_status=LifecycleStatus.ACTIVE.value,
                classification_ids=(), source_identities=(point_identity,),
                created_at=created, updated_at=updated, contract_version=CONTRACT_VERSION,
                metadata_classification=context.metadata_classification,
            ))
        return tuple(points), reviews

    def project_tags(self, record, device, context):
        candidates = []
        reviews = []
        if record.device_code:
            if safe_label(record.device_code):
                candidates.append((TagType.SOURCE_TAG_NAME.value, record.device_code))
            else:
                reviews.append("CREDENTIAL_LIKE_TAG_REJECTED")
        candidates.append((TagType.EXTERNAL_REFERENCE.value, record.source_id))
        unique = sorted(set(candidates))
        tags = tuple(
            Tag(
                tag_id=self._id("tag", context, f"{kind}:{value}"),
                tenant_id=device.tenant_id, site_id=device.site_id,
                canonical_object_id=device.global_id, tag_type=kind, value=value,
                source_system_id=SourceSystemId(context.source_system_id),
                source_namespace=context.source_namespace, contract_version=CONTRACT_VERSION,
            )
            for kind, value in unique
        )
        return tags, reviews

    def build_relationships(self, record, device, points, context):
        relationships = [
            AssetRelationship(
                relationship_id=self._id("relationship", context, f"{device.global_id}:HAS_POINT:{point.global_id}"),
                tenant_id=device.tenant_id, site_id=device.site_id,
                relationship_type=RelationshipType.HAS_POINT.value,
                source_global_id=device.global_id, target_global_id=point.global_id,
                lifecycle_status=LifecycleStatus.ACTIVE.value, valid_from=device.created_at,
                valid_to=None, contract_version=CONTRACT_VERSION,
            )
            for point in points
        ]
        unresolved = []
        parent = context.parent_asset_id or record.parent_reference
        if parent:
            if context.parent_asset_id:
                relationships.append(AssetRelationship(
                    relationship_id=self._id("relationship", context, f"{device.global_id}:LOCATED_IN:{parent}"),
                    tenant_id=device.tenant_id, site_id=device.site_id,
                    relationship_type=RelationshipType.LOCATED_IN.value,
                    source_global_id=device.global_id, target_global_id=GlobalId(parent),
                    lifecycle_status=LifecycleStatus.ACTIVE.value, valid_from=device.created_at,
                    valid_to=None, contract_version=CONTRACT_VERSION,
                ))
            else:
                unresolved.append(UnresolvedRelationship(
                    RelationshipType.LOCATED_IN.value, str(device.global_id), str(parent),
                    "canonical target global ID unavailable",
                ))
        return tuple(sorted(relationships, key=lambda item: str(item.relationship_id))), tuple(unresolved)

    def project_devices(self, records: Iterable, context: ProjectionContext) -> BatchProjectionResult:
        rows = tuple(records)
        if len(rows) > MAX_BATCH_SIZE:
            raise ValueError(f"batch exceeds maximum {MAX_BATCH_SIZE}")
        ordered = sorted(rows, key=self._source_sort_key)
        seen = set()
        results = []
        for raw in ordered:
            try:
                record = LegacyDeviceSnapshot.from_mapping(raw) if isinstance(raw, Mapping) else raw
                key = (context.tenant_id, context.source_system_id, context.source_namespace, record.source_id)
                if key in seen:
                    results.append(self._failure(ProjectionCategory.IDENTITY_CONFLICT, "DUPLICATE_SOURCE_IDENTITY"))
                    continue
                seen.add(key)
                results.append(self.project_device(record, context))
            except (ProhibitedSourceField, TypeError, ValueError) as exc:
                category = (
                    ProjectionCategory.PROHIBITED_FIELD_REJECTED
                    if isinstance(exc, ProhibitedSourceField) else ProjectionCategory.INVALID_SOURCE
                )
                results.append(self._failure(category, self._safe_error(exc)))
        return BatchProjectionResult(tuple(results))

    @staticmethod
    def _source_sort_key(raw):
        if isinstance(raw, Mapping):
            return str(raw.get("source_id", raw.get("id", "")))
        return str(raw.source_id)

    @staticmethod
    def _safe_error(exc: Exception) -> str:
        text = str(exc).upper().replace(" ", "_")
        return text[:80] or "INVALID_SOURCE"

    @staticmethod
    def _failure(category, error_code):
        return ProjectionResult(False, category.value, error_code=error_code)
