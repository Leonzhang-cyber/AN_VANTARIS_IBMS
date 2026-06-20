"""Errors for read-only API mock route contracts."""
from __future__ import annotations


class ReadOnlyApiMockRouteContractError(ValueError):
    """Raised when a read-only API mock route contract violates frozen gates."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
