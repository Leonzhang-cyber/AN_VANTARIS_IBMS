"""Runtime JSON store for asset import quality gate batches."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "AN_VANTARIS_IBMS-backend").is_dir() and (parent / "AN_VANTARIS_ONE").is_dir():
            return parent
    raise RuntimeError("VANTARIS ONE repository root not found")


class AssetImportRuntimeStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or repo_root() / "AN_VANTARIS_IBMS-backend" / "runtime" / "asset_import_batches"
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, batch_id: str) -> Path:
        safe = "".join(ch for ch in batch_id if ch.isalnum() or ch in {"-", "_"})
        return self.root / f"{safe}.json"

    def create_batch(self, batch: dict[str, Any]) -> dict[str, Any]:
        payload = deepcopy(batch)
        self._path(str(payload["import_batch_id"])).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return payload

    def list_batches(self) -> list[dict[str, Any]]:
        rows = []
        for path in sorted(self.root.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            summary = payload.get("summary", {})
            rows.append(
                {
                    "import_batch_id": payload.get("import_batch_id", ""),
                    "source_file_name": payload.get("source_file_name", ""),
                    "uploaded_at": payload.get("uploaded_at", ""),
                    "validated_at": payload.get("validated_at", ""),
                    "total_records": summary.get("total_records", 0),
                    "readiness": summary.get("readiness", ""),
                    "blocker_count": summary.get("blocker_count", 0),
                    "major_count": summary.get("major_count", 0),
                    "warning_count": summary.get("warning_count", 0),
                    "info_count": summary.get("info_count", 0),
                    "import_status": payload.get("import_status", "preview_ready"),
                }
            )
        return sorted(rows, key=lambda row: str(row.get("uploaded_at", "")), reverse=True)

    def get_batch(self, batch_id: str) -> dict[str, Any] | None:
        path = self._path(batch_id)
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def save_batch(self, batch: dict[str, Any]) -> dict[str, Any]:
        return self.create_batch(batch)
