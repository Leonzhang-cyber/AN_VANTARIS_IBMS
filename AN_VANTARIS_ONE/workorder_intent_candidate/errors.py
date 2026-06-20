"""Errors for WorkOrderIntent candidate projection validation."""
from __future__ import annotations


class WorkOrderIntentCandidateError(ValueError):
    """Raised when a WorkOrderIntent candidate projection is invalid."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
