"""Errors for read-only frontend skeleton contracts."""
from __future__ import annotations


class ReadOnlyFrontendSkeletonError(ValueError):
    """Raised when a read-only frontend skeleton violates frozen gates."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
