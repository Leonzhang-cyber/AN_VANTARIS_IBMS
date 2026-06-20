"""Errors for International GA release candidate packages."""
from __future__ import annotations


class InternationalGaReleasePackageError(ValueError):
    """Raised when the International GA package violates frozen release rules."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
