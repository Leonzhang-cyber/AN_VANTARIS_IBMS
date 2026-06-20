"""Errors for read-only UConsole projection validation."""
from __future__ import annotations


class UConsoleProjectionError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
