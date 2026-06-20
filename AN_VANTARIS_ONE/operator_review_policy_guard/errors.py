"""Errors for Operator Review Policy Guard projections."""
from __future__ import annotations


class OperatorReviewPolicyGuardError(ValueError):
    """Raised when policy guard projection validation fails."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
