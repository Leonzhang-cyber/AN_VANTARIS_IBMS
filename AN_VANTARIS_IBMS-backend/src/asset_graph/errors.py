"""Safe Asset Graph errors."""


class AssetGraphValidationError(ValueError):
    """Canonical input is invalid without exposing sensitive values."""
