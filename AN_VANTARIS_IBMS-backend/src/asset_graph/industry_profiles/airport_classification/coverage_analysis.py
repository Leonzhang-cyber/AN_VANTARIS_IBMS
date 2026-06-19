"""Write classification coverage analysis artifacts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .coverage_metrics import build_coverage_analysis


def write_classification_coverage_analysis(
    *,
    bindings: Sequence[Mapping[str, Any]],
    output_path: Path,
    source_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_coverage_analysis(bindings, source_summary=source_summary)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def load_bindings_from_classification_output(classification_dir: Path) -> list[dict[str, Any]]:
    bindings_path = classification_dir / "airport-device-classification-bindings.json"
    if not bindings_path.is_file():
        raise FileNotFoundError(f"classification bindings not found: {bindings_path}")
    payload = json.loads(bindings_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("classification bindings payload must be a list")
    return payload
