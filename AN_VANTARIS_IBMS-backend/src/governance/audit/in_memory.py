"""NON_PRODUCTION_IN_MEMORY_PROVIDER for tests and local contract validation."""
from __future__ import annotations

import base64
import json
from threading import RLock
from typing import Dict, Optional

from .models import AuditEmissionResult, AuditQuery, AuditQueryResult, AuditRecord
from .provider import AuditProvider
from .validation import validate_audit_record, validate_query


class InMemoryAuditProvider(AuditProvider):
    """NON_PRODUCTION_IN_MEMORY_PROVIDER with no filesystem or database writes."""

    PROVIDER_STATUS = "NON_PRODUCTION_IN_MEMORY_PROVIDER"

    def __init__(self) -> None:
        self._records: Dict[str, AuditRecord] = {}
        self._serialized: Dict[str, str] = {}
        self._lock = RLock()

    def emit(self, record: AuditRecord, failure_policy: str) -> AuditEmissionResult:
        validate_audit_record(record)
        serialized = record.serialize()
        with self._lock:
            existing = self._serialized.get(record.audit_id)
            if existing is not None:
                if existing == serialized:
                    return AuditEmissionResult(
                        audit_id=record.audit_id,
                        accepted=True,
                        duplicate=True,
                        provider_status=self.PROVIDER_STATUS,
                        failure_policy=failure_policy,
                    )
                return AuditEmissionResult(
                    audit_id=record.audit_id,
                    accepted=False,
                    duplicate=True,
                    provider_status=self.PROVIDER_STATUS,
                    failure_policy=failure_policy,
                    error_code="AUDIT_ID_CONFLICT",
                )
            self._records[record.audit_id] = record
            self._serialized[record.audit_id] = serialized
        return AuditEmissionResult(
            audit_id=record.audit_id,
            accepted=True,
            duplicate=False,
            provider_status=self.PROVIDER_STATUS,
            failure_policy=failure_policy,
        )

    def get_by_id(self, audit_id: str) -> Optional[AuditRecord]:
        with self._lock:
            return self._records.get(audit_id)

    @staticmethod
    def _encode_cursor(record: AuditRecord) -> str:
        payload = json.dumps(
            [record.occurred_at.isoformat(), record.audit_id],
            separators=(",", ":"),
        ).encode("utf-8")
        return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")

    @staticmethod
    def _decode_cursor(cursor: str) -> tuple[str, str]:
        padded = cursor + "=" * (-len(cursor) % 4)
        occurred_at, audit_id = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))
        return str(occurred_at), str(audit_id)

    def query(self, query_spec: AuditQuery) -> AuditQueryResult:
        validate_query(query_spec)
        with self._lock:
            records = list(self._records.values())
        records.sort(key=lambda item: (item.occurred_at, item.audit_id))
        filters = (
            ("tenant_id", query_spec.tenant_id),
            ("site_id", query_spec.site_id),
            ("actor_id", query_spec.actor_id),
            ("service_identity_id", query_spec.service_identity_id),
            ("event_class", query_spec.event_class),
            ("action", query_spec.action),
            ("target_type", query_spec.target_type),
            ("target_id", query_spec.target_id),
            ("package_id", query_spec.package_id),
            ("outcome", query_spec.outcome),
            ("correlation_id", query_spec.correlation_id),
            ("trace_id", query_spec.trace_id),
        )
        for field, expected in filters:
            if expected is not None:
                records = [record for record in records if getattr(record, field) == expected]
        if query_spec.occurred_from:
            records = [record for record in records if record.occurred_at >= query_spec.occurred_from]
        if query_spec.occurred_to:
            records = [record for record in records if record.occurred_at <= query_spec.occurred_to]
        if query_spec.cursor:
            cursor_key = self._decode_cursor(query_spec.cursor)
            records = [
                record for record in records
                if (record.occurred_at.isoformat(), record.audit_id) > cursor_key
            ]
        page = records[:query_spec.limit]
        next_cursor = None
        if len(records) > query_spec.limit and page:
            next_cursor = self._encode_cursor(page[-1])
        return AuditQueryResult(
            records=tuple(page),
            next_cursor=next_cursor,
            provider_status=self.PROVIDER_STATUS,
        )

    def clear_for_test(self) -> None:
        """Explicit test utility; no global singleton is used."""
        with self._lock:
            self._records.clear()
            self._serialized.clear()
