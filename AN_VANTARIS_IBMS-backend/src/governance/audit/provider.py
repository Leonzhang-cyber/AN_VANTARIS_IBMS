"""Audit provider abstraction owned by Governance and Security."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from .models import AuditEmissionResult, AuditQuery, AuditQueryResult, AuditRecord


class AuditProvider(ABC):
    @abstractmethod
    def emit(self, record: AuditRecord, failure_policy: str) -> AuditEmissionResult:
        """Store one immutable AuditRecord and return a stable result."""

    @abstractmethod
    def get_by_id(self, audit_id: str) -> Optional[AuditRecord]:
        """Return one immutable record without exposing persistence internals."""

    @abstractmethod
    def query(self, query_spec: AuditQuery) -> AuditQueryResult:
        """Execute one bounded provider-neutral query."""
