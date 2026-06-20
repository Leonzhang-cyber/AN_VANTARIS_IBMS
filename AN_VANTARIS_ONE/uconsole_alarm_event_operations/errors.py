"""Errors for UConsole Alarm/Event Operations projection validation."""
from __future__ import annotations


class UConsoleAlarmEventOperationsError(ValueError):
    """Raised when a UConsole operations projection is invalid."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
