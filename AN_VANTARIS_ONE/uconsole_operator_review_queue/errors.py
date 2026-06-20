"""Errors for UConsole Operator Review Queue projections."""
from __future__ import annotations


class UConsoleOperatorReviewQueueError(ValueError):
    """Raised when a UConsole operator review queue projection violates its contract."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
