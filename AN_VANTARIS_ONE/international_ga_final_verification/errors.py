"""Errors for International GA final local verification."""
from __future__ import annotations


class InternationalGaFinalVerificationError(ValueError):
    """Raised when final local verification violates frozen rules."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
