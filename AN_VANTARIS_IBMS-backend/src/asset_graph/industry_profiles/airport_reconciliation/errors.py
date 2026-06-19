"""Errors for airport asset reconciliation profile."""
from __future__ import annotations


class AirportReconciliationProfileError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
