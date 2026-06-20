"""Errors for read-only Operations Console Packages."""
from __future__ import annotations


class OperationsConsolePackageError(ValueError):
    """Raised when a read-only operations console package is invalid."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
