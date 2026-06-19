"""Structured errors for source-system registry validation."""
from __future__ import annotations


class SourceSystemRegistryError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
