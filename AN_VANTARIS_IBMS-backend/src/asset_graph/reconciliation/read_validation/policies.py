"""Output location and retention policy checks."""
from __future__ import annotations

from pathlib import Path


class OutputPolicyError(ValueError):
    """Output directory violates execution policy."""


def validate_output_directory(output_dir: Path, *, output_location_policy: str) -> None:
    resolved = output_dir.resolve()
    if output_location_policy == "OFFLINE_AGGREGATE_EXPORT_ONLY":
        parts = {part.lower() for part in resolved.parts}
        if ".git" in parts:
            raise OutputPolicyError("output directory must remain outside Git workspace")
        if str(resolved).startswith(str(Path.home() / "Desktop" / "AN_VANTARIS_IBMS")):
            raise OutputPolicyError("output directory must not write inside repository tree")
    if not output_location_policy:
        raise OutputPolicyError("output location policy is required")
