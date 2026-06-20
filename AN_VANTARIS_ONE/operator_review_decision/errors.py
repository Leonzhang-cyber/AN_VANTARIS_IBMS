"""Errors for the Operator Review Decision Layer."""
from __future__ import annotations


class OperatorReviewDecisionError(ValueError):
    """Raised when an operator review decision projection violates the contract."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
