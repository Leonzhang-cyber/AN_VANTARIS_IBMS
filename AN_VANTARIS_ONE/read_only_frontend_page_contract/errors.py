"""Errors for read-only frontend page contracts."""
from __future__ import annotations


class ReadOnlyFrontendPageContractError(ValueError):
    """Raised when a read-only frontend page contract violates frozen gates."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
