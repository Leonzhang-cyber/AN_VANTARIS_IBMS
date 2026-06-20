"""Errors for International GA handoff notes."""
from __future__ import annotations


class InternationalGaHandoffNotesError(ValueError):
    """Raised when frozen International GA handoff notes violate release rules."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
