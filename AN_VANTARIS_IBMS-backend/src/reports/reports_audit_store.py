"""Local JSONL audit store for Reports foundation."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_audit_store_path() -> Path:
    backend_root = Path(__file__).resolve().parents[2]
    return backend_root / "runtime" / "reports_audit" / "reports_audit.jsonl"


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def append_audit_record(record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    path = get_audit_store_path()
    try:
        _ensure_parent_dir(path)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, default=str, separators=(",", ":")) + "\n")
        return True, None
    except Exception as exc:  # pragma: no cover - defensive runtime guard
        return False, str(exc)


def _read_records(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                records.append(parsed)
    return records


def list_audit_records(
    limit: int = 50, event_type: Optional[str] = None, report_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    path = get_audit_store_path()
    records = _read_records(path)
    if event_type:
        records = [item for item in records if str(item.get("auditEventType")) == str(event_type)]
    if report_id:
        records = [item for item in records if str(item.get("reportId")) == str(report_id)]
    try:
        safe_limit = max(1, min(int(limit), 500))
    except (TypeError, ValueError):
        safe_limit = 50
    return list(reversed(records))[:safe_limit]


def get_audit_record(audit_id: str) -> Optional[Dict[str, Any]]:
    if not audit_id:
        return None
    path = get_audit_store_path()
    for item in reversed(_read_records(path)):
        if str(item.get("auditId")) == str(audit_id):
            return item
    return None


def build_audit_record(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    data = payload or {}
    return {
        "auditId": str(data.get("auditId") or uuid.uuid4()),
        "auditEventType": str(event_type),
        "reportId": str(data.get("reportId", "")),
        "reportName": str(data.get("reportName", "")),
        "queryId": str(data.get("queryId", "")),
        "exportId": str(data.get("exportId", "")) if data.get("exportId") else None,
        "generatedAt": str(data.get("generatedAt", _utc_now_iso())),
        "persistedAt": _utc_now_iso(),
        "sourceSemantics": "ibms-neutral",
        "provider": str(data.get("provider", "local-mock-provider")),
        "runtimeMode": str(data.get("runtimeMode", "skeleton")),
        "mockData": bool(data.get("mockData", True)),
        "queryHash": str(data.get("queryHash", "")),
        "payloadHash": str(data.get("payloadHash", "")),
        "exportHash": str(data.get("exportHash", "")) if data.get("exportHash") else None,
        "rowCount": int(data.get("rowCount", 0) or 0),
        "columnCount": int(data.get("columnCount", 0) or 0),
        "sourceReferences": data.get("sourceReferences") if isinstance(data.get("sourceReferences"), list) else [],
        "evidenceReferences": data.get("evidenceReferences")
        if isinstance(data.get("evidenceReferences"), list)
        else [],
        "permissionDecision": bool(data.get("permissionDecision", True)),
        "permissionMode": str(data.get("permissionMode", "placeholder-allow")),
        "certified": False,
        "iec62443Certified": False,
        "storageMode": "local-jsonl",
        "tamperEvidenceMode": str(data.get("tamperEvidenceMode", "hash-only")),
        "notes": str(
            data.get(
                "notes",
                "Local JSONL audit store foundation; not a formal certified evidence protocol.",
            )
        ),
    }

