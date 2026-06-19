"""Persistence contract errors."""
from __future__ import annotations


class PersistenceContractError(ValueError):
    """Invalid persistence contract registry or evaluation input."""


class PersistenceAuthorizationError(PersistenceContractError):
    """Write authorization rejected."""


class PersistenceConflictError(PersistenceContractError):
    """Canonical persistence conflict."""


class PersistenceBatchLimitError(PersistenceContractError):
    """Batch exceeds contract limits."""


class PersistenceUnitOfWorkError(PersistenceContractError):
    """Unit of Work staging or commit contract violation."""


class PersistenceAuditError(PersistenceContractError):
    """Required audit obligation could not be fulfilled."""
