"""Errors for API / Frontend implementation readiness gates."""
from __future__ import annotations


class ApiFrontendImplementationGateError(ValueError):
    """Raised when an API / Frontend implementation readiness gate is invalid."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
