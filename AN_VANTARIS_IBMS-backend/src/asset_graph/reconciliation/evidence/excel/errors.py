"""Excel evidence intake error types."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExcelIntakeError(Exception):
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"
