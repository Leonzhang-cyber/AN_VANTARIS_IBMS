"""Errors for read-only API response contracts."""
from __future__ import annotations


class ReadOnlyApiResponseContractError(ValueError):
    """Raised when a read-only API response contract is invalid."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
