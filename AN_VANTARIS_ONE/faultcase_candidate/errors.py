"""Errors for UFMS FaultCase candidate projection validation."""
from __future__ import annotations


class FaultCaseCandidateError(ValueError):
    """Raised when a FaultCase candidate projection is invalid."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
