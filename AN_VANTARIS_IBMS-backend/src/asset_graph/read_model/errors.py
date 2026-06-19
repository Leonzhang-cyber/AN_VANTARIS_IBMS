"""Read model errors."""
from __future__ import annotations


class ReadModelError(ValueError):
    """Invalid read model activation or query."""


class ReadModelDiscardedError(ReadModelError):
    """Read model has been discarded."""


class ScopeViolationError(ReadModelError):
    """Query scope rejected or object outside scope."""


class QueryBindingError(ReadModelError):
    """Cursor does not match query binding."""
