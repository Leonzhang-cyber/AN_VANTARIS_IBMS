"""Errors for Evidence Investigation projection validation."""
from __future__ import annotations


class EvidenceInvestigationProjectionError(ValueError):
    """Raised when an Evidence Investigation projection is invalid."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
