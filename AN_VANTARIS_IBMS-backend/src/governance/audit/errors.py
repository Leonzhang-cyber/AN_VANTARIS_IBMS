"""Safe error types for audit validation and provider operations."""


class AuditValidationError(ValueError):
    """Audit input is invalid; messages never contain submitted secret values."""


class AuditProviderError(RuntimeError):
    """Provider operation failed without exposing provider internals."""
