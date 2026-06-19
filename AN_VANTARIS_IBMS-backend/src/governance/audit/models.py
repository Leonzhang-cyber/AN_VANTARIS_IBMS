"""Immutable application models for canonical AuditRecord handling."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timezone
from typing import Any, Mapping, Optional, Tuple

from .constants import DEFAULT_QUERY_LIMIT
from .errors import AuditValidationError


@dataclass(frozen=True)
class AuditRecord:
    audit_id: str
    event_class: str
    action: str
    occurred_at: datetime
    actor_type: str
    actor_id: Optional[str]
    service_identity_id: Optional[str]
    tenant_id: Optional[str]
    site_id: Optional[str]
    subject_type: Optional[str]
    subject_id: Optional[str]
    target_type: Optional[str]
    target_id: Optional[str]
    route_id: Optional[str]
    request_id: str
    trace_id: str
    correlation_id: str
    permission: Optional[str]
    package_id: Optional[str]
    outcome: str
    denial_code: Optional[str]
    reason_code: Optional[str]
    previous_state_digest: Optional[str]
    resulting_state_digest: Optional[str]
    source_ip_class: Optional[str]
    user_agent_class: Optional[str]
    contract_version: str
    metadata_classification: str
    evidence_reference_ids: Tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "AuditRecord":
        from .validation import validate_mapping_keys

        validate_mapping_keys(value, {field.name for field in fields(cls)})
        data = dict(value)
        references = data.get("evidence_reference_ids", ())
        if not isinstance(references, (list, tuple)):
            raise AuditValidationError("evidence_reference_ids must be a list or tuple")
        data["evidence_reference_ids"] = tuple(references)
        record = cls(**data)
        from .validation import validate_audit_record

        validate_audit_record(record)
        return record

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        occurred = self.occurred_at.astimezone(timezone.utc)
        value["occurred_at"] = occurred.isoformat(timespec="microseconds").replace("+00:00", "Z")
        value["evidence_reference_ids"] = list(self.evidence_reference_ids)
        return value

    def serialize(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )


@dataclass(frozen=True)
class AuditQuery:
    tenant_id: Optional[str] = None
    site_id: Optional[str] = None
    actor_id: Optional[str] = None
    service_identity_id: Optional[str] = None
    event_class: Optional[str] = None
    action: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    package_id: Optional[str] = None
    outcome: Optional[str] = None
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    occurred_from: Optional[datetime] = None
    occurred_to: Optional[datetime] = None
    limit: int = DEFAULT_QUERY_LIMIT
    cursor: Optional[str] = None
    platform_query: bool = False


@dataclass(frozen=True)
class AuditQueryResult:
    records: Tuple[AuditRecord, ...]
    next_cursor: Optional[str]
    provider_status: str


@dataclass(frozen=True)
class AuditEmissionResult:
    audit_id: str
    accepted: bool
    duplicate: bool
    provider_status: str
    failure_policy: str
    error_code: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
