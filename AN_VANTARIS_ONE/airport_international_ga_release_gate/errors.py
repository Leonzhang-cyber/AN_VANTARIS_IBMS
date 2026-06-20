"""Errors for Airport International GA release gates."""
from __future__ import annotations


class AirportInternationalGaReleaseGateError(ValueError):
    """Raised when the final International GA release gate violates frozen rules."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
