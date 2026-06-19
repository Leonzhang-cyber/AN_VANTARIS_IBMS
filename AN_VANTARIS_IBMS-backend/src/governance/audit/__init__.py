"""Governance Audit Provider foundation.

This package owns the AuditRecord persistence abstraction. The included
InMemoryAuditProvider is explicitly non-production.
"""

from .constants import (
    ActorType,
    AuditFailurePolicy,
    AuditOutcome,
    MetadataClassification,
)
from .errors import AuditProviderError, AuditValidationError
from .in_memory import InMemoryAuditProvider
from .models import AuditEmissionResult, AuditQuery, AuditQueryResult, AuditRecord
from .provider import AuditProvider
from .service import AuditService
from .validation import validate_audit_record, validate_query

__all__ = [
    "ActorType",
    "AuditEmissionResult",
    "AuditFailurePolicy",
    "AuditOutcome",
    "AuditProvider",
    "AuditProviderError",
    "AuditQuery",
    "AuditQueryResult",
    "AuditRecord",
    "AuditService",
    "AuditValidationError",
    "InMemoryAuditProvider",
    "MetadataClassification",
    "validate_audit_record",
    "validate_query",
]
