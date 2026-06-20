"""Errors for canonical alarm/event intake validation."""
from __future__ import annotations


class AlarmEventIntakeError(ValueError):
    """Raised when an intake candidate cannot be validated or projected."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
