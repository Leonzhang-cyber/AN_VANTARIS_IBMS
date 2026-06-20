"""Errors for A4 readiness release gates."""
from __future__ import annotations


class A4ReadinessGateError(ValueError):
    """Raised when an A4 readiness release gate violates the contract."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
