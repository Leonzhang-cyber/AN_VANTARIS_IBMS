"""Thin audit application service; authorization remains outside this package."""
from __future__ import annotations

from .constants import EVENT_CLASS_POLICIES
from .errors import AuditValidationError
from .models import AuditEmissionResult, AuditQuery, AuditQueryResult, AuditRecord
from .provider import AuditProvider
from .validation import validate_audit_record, validate_query


class AuditService:
    def __init__(self, provider: AuditProvider) -> None:
        self._provider = provider

    def emit(self, record: AuditRecord) -> AuditEmissionResult:
        validate_audit_record(record)
        failure_policy = EVENT_CLASS_POLICIES[record.event_class][2].value
        try:
            result = self._provider.emit(record, failure_policy)
        except Exception:
            return AuditEmissionResult(
                audit_id=record.audit_id,
                accepted=False,
                duplicate=False,
                provider_status="AUDIT_PROVIDER_UNAVAILABLE",
                failure_policy=failure_policy,
                error_code="AUDIT_PROVIDER_FAILURE",
            )
        return result

    def get_by_id(self, audit_id: str) -> AuditRecord | None:
        if not audit_id:
            raise AuditValidationError("audit_id is required")
        return self._provider.get_by_id(audit_id)

    def query(self, query_spec: AuditQuery) -> AuditQueryResult:
        validate_query(query_spec)
        return self._provider.query(query_spec)
