"""Errors for read-only frontend implementation release gates."""
from __future__ import annotations


class ReadOnlyFrontendReleaseGateError(ValueError):
    """Raised when a read-only frontend implementation release gate violates frozen rules."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
