"""Errors for airport review projection."""
from __future__ import annotations


class AirportReviewProjectionError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
