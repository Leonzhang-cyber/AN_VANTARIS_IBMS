"""Errors for read-only API skeletons."""
from __future__ import annotations


class ReadOnlyApiSkeletonError(ValueError):
    """Raised when a read-only API skeleton artifact is invalid."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
