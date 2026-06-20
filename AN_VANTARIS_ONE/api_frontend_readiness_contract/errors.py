"""Errors for API / Frontend readiness contracts."""
from __future__ import annotations


class ApiFrontendReadinessContractError(ValueError):
    """Raised when an API / Frontend readiness contract is invalid."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
