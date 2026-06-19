"""Immutable persistence write commands."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Union

from ..reconciliation.models import sha256_digest
from .constants import REQUIRED_COMMAND_AUTHORITY
from .errors import PersistenceContractError


def _require_text(value: object, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise PersistenceContractError(f"{field} is required")
    return text


@dataclass(frozen=True)
class PersistenceCommandBase:
    command_id: str
    idempotency_key: str
    tenant_id: str
    site_id: str
    source_system_id: str
    mapping_version: str
    evidence_digest: str
    readiness_result_digest: str
    execution_result_digest: str
    canonical_global_id: str
    expected_version: int
    requested_operation: str
    requested_by_authority: str

    def __post_init__(self) -> None:
        if self.requested_by_authority != REQUIRED_COMMAND_AUTHORITY:
            raise PersistenceContractError("requestedByAuthority must be APPROVED_READ_MIGRATION_EXECUTION")

    def command_digest(self) -> str:
        return sha256_digest(self.digest_material())

    def idempotency_key_digest(self) -> str:
        return sha256_digest({"idempotencyKey": self.idempotency_key})

    def canonical_global_id_digest(self) -> str:
        return sha256_digest({"canonicalGlobalId": self.canonical_global_id})

    def digest_material(self) -> dict[str, Any]:
        return {
            "commandId": self.command_id,
            "idempotencyKeyDigest": self.idempotency_key_digest(),
            "tenantId": self.tenant_id,
            "siteId": self.site_id,
            "sourceSystemId": self.source_system_id,
            "mappingVersion": self.mapping_version,
            "evidenceDigest": self.evidence_digest,
            "readinessResultDigest": self.readiness_result_digest,
            "executionResultDigest": self.execution_result_digest,
            "canonicalGlobalIdDigest": self.canonical_global_id_digest(),
            "expectedVersion": self.expected_version,
            "requestedOperation": self.requested_operation,
            "requestedByAuthority": self.requested_by_authority,
            "commandType": self.command_type(),
        }

    def command_type(self) -> str:
        raise NotImplementedError

    def object_type(self) -> str:
        raise NotImplementedError

    def serialize(self) -> dict[str, Any]:
        payload = self.digest_material()
        payload["commandType"] = self.command_type()
        payload["objectType"] = self.object_type()
        payload["commandDigest"] = self.command_digest()
        return payload

    @classmethod
    def _base_from_mapping(cls, value: Mapping[str, Any], *, command_type: str, object_type: str) -> dict[str, Any]:
        return {
            "command_id": _require_text(value["commandId"], "commandId"),
            "idempotency_key": _require_text(value["idempotencyKey"], "idempotencyKey"),
            "tenant_id": _require_text(value["tenantId"], "tenantId"),
            "site_id": _require_text(value["siteId"], "siteId"),
            "source_system_id": _require_text(value["sourceSystemId"], "sourceSystemId"),
            "mapping_version": _require_text(value["mappingVersion"], "mappingVersion"),
            "evidence_digest": _require_text(value["evidenceDigest"], "evidenceDigest"),
            "readiness_result_digest": _require_text(value["readinessResultDigest"], "readinessResultDigest"),
            "execution_result_digest": _require_text(value["executionResultDigest"], "executionResultDigest"),
            "canonical_global_id": _require_text(value["canonicalGlobalId"], "canonicalGlobalId"),
            "expected_version": int(value["expectedVersion"]),
            "requested_operation": _require_text(value["requestedOperation"], "requestedOperation"),
            "requested_by_authority": _require_text(value["requestedByAuthority"], "requestedByAuthority"),
        }


@dataclass(frozen=True)
class CreateCanonicalDevice(PersistenceCommandBase):
    display_name: str = ""
    device_type: str = ""

    def command_type(self) -> str:
        return "CreateCanonicalDevice"

    def object_type(self) -> str:
        return "Device"

    def digest_material(self) -> dict[str, Any]:
        payload = super().digest_material()
        payload["displayName"] = self.display_name
        payload["deviceType"] = self.device_type
        return payload


@dataclass(frozen=True)
class UpdateCanonicalDevice(PersistenceCommandBase):
    display_name: str = ""

    def command_type(self) -> str:
        return "UpdateCanonicalDevice"

    def object_type(self) -> str:
        return "Device"

    def digest_material(self) -> dict[str, Any]:
        payload = super().digest_material()
        payload["displayName"] = self.display_name
        return payload


@dataclass(frozen=True)
class CreateCanonicalPoint(PersistenceCommandBase):
    device_global_id: str = ""
    point_type: str = ""

    def command_type(self) -> str:
        return "CreateCanonicalPoint"

    def object_type(self) -> str:
        return "Point"

    def digest_material(self) -> dict[str, Any]:
        payload = super().digest_material()
        payload["deviceGlobalIdDigest"] = sha256_digest({"deviceGlobalId": self.device_global_id})
        payload["pointType"] = self.point_type
        return payload


@dataclass(frozen=True)
class UpdateCanonicalPoint(PersistenceCommandBase):
    display_name: str = ""

    def command_type(self) -> str:
        return "UpdateCanonicalPoint"

    def object_type(self) -> str:
        return "Point"

    def digest_material(self) -> dict[str, Any]:
        payload = super().digest_material()
        payload["displayName"] = self.display_name
        return payload


@dataclass(frozen=True)
class CreateCanonicalTag(PersistenceCommandBase):
    tag_namespace: str = ""
    tag_value: str = ""

    def command_type(self) -> str:
        return "CreateCanonicalTag"

    def object_type(self) -> str:
        return "Tag"

    def digest_material(self) -> dict[str, Any]:
        payload = super().digest_material()
        payload["tagNamespace"] = self.tag_namespace
        payload["tagValueDigest"] = sha256_digest({"tagValue": self.tag_value})
        return payload


@dataclass(frozen=True)
class CreateCanonicalRelationship(PersistenceCommandBase):
    relationship_type: str = ""
    source_global_id: str = ""
    target_global_id: str = ""

    def command_type(self) -> str:
        return "CreateCanonicalRelationship"

    def object_type(self) -> str:
        return "AssetRelationship"

    def digest_material(self) -> dict[str, Any]:
        payload = super().digest_material()
        payload["relationshipType"] = self.relationship_type
        payload["sourceGlobalIdDigest"] = sha256_digest({"sourceGlobalId": self.source_global_id})
        payload["targetGlobalIdDigest"] = sha256_digest({"targetGlobalId": self.target_global_id})
        return payload


PersistenceCommand = Union[
    CreateCanonicalDevice,
    UpdateCanonicalDevice,
    CreateCanonicalPoint,
    UpdateCanonicalPoint,
    CreateCanonicalTag,
    CreateCanonicalRelationship,
]
