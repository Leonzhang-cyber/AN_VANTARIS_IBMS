"""Errors for Operations Console Handoff Gates."""
from __future__ import annotations


class OperationsConsoleHandoffGateError(ValueError):
    """Raised when an operations console handoff gate is invalid."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
