"""Foundation Diagnostics GA R1 read-only service."""

from __future__ import annotations

from typing import Any, Dict

from src.foundation_diagnostics.provider import section, workspace


class FoundationDiagnosticsService:
    def workspace(self) -> Dict[str, Any]:
        return workspace()

    def section(self, name: str) -> Dict[str, Any]:
        return section(name)
