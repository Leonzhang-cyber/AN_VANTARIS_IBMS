"""Errors for Airport read-only POC release gates."""
from __future__ import annotations


class AirportReadOnlyPocReleaseGateError(ValueError):
    """Raised when the final read-only POC release gate violates frozen rules."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
