"""Validation rules for canonical AuditRecord and bounded AuditQuery inputs."""
from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Mapping, Set

from .constants import (
    ActorType,
    AuditOutcome,
    EVENT_CLASS_POLICIES,
    MAX_IDENTIFIER_LENGTH,
    MAX_QUERY_LIMIT,
    MAX_RECORD_SERIALIZED_BYTES,
    MetadataClassification,
)
from .errors import AuditValidationError
from .models import AuditQuery, AuditRecord

SECRET_KEY_PATTERN = re.compile(
    r"(password|passwd|private[_-]?key|seed[_-]?phrase|bearer|authorization|"
    r"access[_-]?token|refresh[_-]?token|jwt|credential|secret|full[_-]?request[_-]?body)",
    re.IGNORECASE,
)
DIGEST_PATTERN = re.compile(r"^(?:sha(?:256|384|512):)?[A-Fa-f0-9]{32,128}$")


def validate_mapping_keys(value: Mapping[str, Any], allowed_keys: Set[str]) -> None:
    for key in value:
        if SECRET_KEY_PATTERN.search(str(key)):
            raise AuditValidationError(f"prohibited secret-like field: {key}")
        if key not in allowed_keys:
            raise AuditValidationError(f"unknown AuditRecord field: {key}")


def _identifier(name: str, value: Any, required: bool = False) -> None:
    if value is None:
        if required:
            raise AuditValidationError(f"{name} is required")
        return
    if not isinstance(value, str) or not value.strip():
        raise AuditValidationError(f"{name} must be a non-empty string")
    if len(value) > MAX_IDENTIFIER_LENGTH:
        raise AuditValidationError(f"{name} exceeds the maximum identifier length")
    if SECRET_KEY_PATTERN.search(value):
        raise AuditValidationError(f"{name} contains prohibited secret-like content")
    if "\r" in value or "\n" in value:
        raise AuditValidationError(f"{name} must not contain control lines")


def _digest(name: str, value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, str) or not DIGEST_PATTERN.fullmatch(value):
        raise AuditValidationError(f"{name} must contain a digest, not raw state")


def _aware(name: str, value: Any) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise AuditValidationError(f"{name} must be timezone-aware")


def validate_audit_record(record: AuditRecord) -> None:
    _identifier("audit_id", record.audit_id, required=True)
    _identifier("action", record.action, required=True)
    _aware("occurred_at", record.occurred_at)
    if record.event_class not in EVENT_CLASS_POLICIES:
        raise AuditValidationError("event_class is not recognized by the frozen audit contract")
    if record.actor_type not in {item.value for item in ActorType}:
        raise AuditValidationError("actor_type is not recognized")
    if record.outcome not in {item.value for item in AuditOutcome}:
        raise AuditValidationError("outcome is not recognized")
    if record.metadata_classification not in {item.value for item in MetadataClassification}:
        raise AuditValidationError("metadata_classification is not recognized")
    if record.actor_type == ActorType.USER.value:
        _identifier("actor_id", record.actor_id, required=True)
    elif record.actor_type == ActorType.SERVICE_IDENTITY.value:
        _identifier("service_identity_id", record.service_identity_id, required=True)
    elif record.actor_type == ActorType.SYSTEM.value:
        if not record.actor_id and not record.service_identity_id:
            raise AuditValidationError("SYSTEM actor requires actor_id or service_identity_id")
    elif record.actor_type == ActorType.ANONYMOUS.value:
        if record.actor_id or record.service_identity_id:
            raise AuditValidationError("ANONYMOUS actor must not include an identity")
    tenant_required, site_required, _policy = EVENT_CLASS_POLICIES[record.event_class]
    _identifier("tenant_id", record.tenant_id, required=tenant_required)
    _identifier("site_id", record.site_id, required=site_required)
    for name in (
        "actor_id", "service_identity_id", "subject_type", "subject_id",
        "target_type", "target_id", "route_id", "request_id", "trace_id",
        "correlation_id", "permission", "package_id", "denial_code", "reason_code",
        "source_ip_class", "user_agent_class", "contract_version",
    ):
        _identifier(name, getattr(record, name), required=name in {
            "request_id", "trace_id", "correlation_id", "contract_version",
        })
    _digest("previous_state_digest", record.previous_state_digest)
    _digest("resulting_state_digest", record.resulting_state_digest)
    if not isinstance(record.evidence_reference_ids, tuple):
        raise AuditValidationError("evidence_reference_ids must be an immutable tuple")
    for reference in record.evidence_reference_ids:
        _identifier("evidence_reference_id", reference, required=True)
    size = len(record.serialize().encode("utf-8"))
    if size > MAX_RECORD_SERIALIZED_BYTES:
        raise AuditValidationError("AuditRecord exceeds the bounded metadata size")
    serialized = json.dumps(record.to_dict(), sort_keys=True)
    if SECRET_KEY_PATTERN.search(serialized):
        raise AuditValidationError("AuditRecord contains prohibited secret-like content")


def validate_query(query: AuditQuery) -> None:
    if not query.platform_query and not query.tenant_id:
        raise AuditValidationError("tenant_id is required unless platform_query is explicit")
    if query.limit < 1 or query.limit > MAX_QUERY_LIMIT:
        raise AuditValidationError(f"limit must be between 1 and {MAX_QUERY_LIMIT}")
    if query.event_class is not None and query.event_class not in EVENT_CLASS_POLICIES:
        raise AuditValidationError("query event_class is not recognized")
    if query.outcome is not None and query.outcome not in {item.value for item in AuditOutcome}:
        raise AuditValidationError("query outcome is not recognized")
    for name in (
        "tenant_id", "site_id", "actor_id", "service_identity_id", "action",
        "target_type", "target_id", "package_id", "correlation_id", "trace_id", "cursor",
    ):
        _identifier(name, getattr(query, name))
    if query.occurred_from is not None:
        _aware("occurred_from", query.occurred_from)
    if query.occurred_to is not None:
        _aware("occurred_to", query.occurred_to)
    if query.occurred_from and query.occurred_to and query.occurred_from > query.occurred_to:
        raise AuditValidationError("occurred_from must not be after occurred_to")
