"""Errors for alarm/event resolution review projection."""
from __future__ import annotations


class AlarmEventResolutionError(ValueError):
    """Raised when a resolution review projection is invalid."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
