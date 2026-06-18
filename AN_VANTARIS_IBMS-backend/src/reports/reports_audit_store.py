"""Local JSONL audit store hardening for Reports foundation."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.reports.reports_integrity import canonical_json, sha256_hex


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_audit_store_path() -> Path:
    backend_root = Path(__file__).resolve().parents[2]
    return backend_root / "runtime" / "reports_audit" / "reports_audit.jsonl"


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_audit_record(record: Dict[str, Any]) -> Dict[str, Any]:
    data = record or {}
    return {
        "auditId": str(data.get("auditId") or uuid.uuid4()),
        "auditEventType": str(data.get("auditEventType", "")),
        "reportId": str(data.get("reportId", "")),
        "reportName": str(data.get("reportName", "")),
        "queryId": str(data.get("queryId", "")),
        "exportId": str(data.get("exportId", "")) if data.get("exportId") else None,
        "generatedAt": str(data.get("generatedAt", _utc_now_iso())),
        "persistedAt": str(data.get("persistedAt", _utc_now_iso())),
        "sourceSemantics": "ibms-neutral",
        "provider": str(data.get("provider", "local-mock-provider")),
        "runtimeMode": str(data.get("runtimeMode", "skeleton")),
        "mockData": bool(data.get("mockData", True)),
        "queryHash": str(data.get("queryHash", "")),
        "payloadHash": str(data.get("payloadHash", "")),
        "exportHash": str(data.get("exportHash", "")) if data.get("exportHash") else None,
        "previousAuditHash": str(data.get("previousAuditHash", "")) if data.get("previousAuditHash") else None,
        "auditRecordHash": str(data.get("auditRecordHash", "")) if data.get("auditRecordHash") else None,
        "hashAlgorithm": "SHA-256",
        "rowCount": max(_safe_int(data.get("rowCount"), 0), 0),
        "columnCount": max(_safe_int(data.get("columnCount"), 0), 0),
        "sourceReferences": data.get("sourceReferences") if isinstance(data.get("sourceReferences"), list) else [],
        "evidenceReferences": data.get("evidenceReferences")
        if isinstance(data.get("evidenceReferences"), list)
        else [],
        "permissionDecision": bool(data.get("permissionDecision", True)),
        "permissionMode": str(data.get("permissionMode", "placeholder-allow")),
        "certified": False,
        "iec62443Certified": False,
        "storageMode": "local-jsonl",
        "retentionClass": str(data.get("retentionClass", "audit-readiness-local")),
        "retentionPolicy": str(
            data.get("retentionPolicy", "local-jsonl-retain-until-manual-cleanup")
        ),
        "tamperEvidenceMode": str(data.get("tamperEvidenceMode", "hash-chain-local-jsonl")),
        "verificationStatus": str(data.get("verificationStatus", "not-verified")),
        "notes": str(
            data.get(
                "notes",
                "Local JSONL hash-chain foundation for audit readiness; not a formal certification proof.",
            )
        ),
    }


def _read_records_with_stats(path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    stats = {
        "totalLines": 0,
        "validRecords": 0,
        "corruptedLines": 0,
        "skippedLines": 0,
        "storePathMode": "local-jsonl",
    }
    if not path.exists():
        return [], stats

    records: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for raw in handle:
                stats["totalLines"] += 1
                line = raw.strip()
                if not line:
                    stats["skippedLines"] += 1
                    continue
                try:
                    parsed = json.loads(line)
                except json.JSONDecodeError:
                    stats["corruptedLines"] += 1
                    continue
                if not isinstance(parsed, dict):
                    stats["skippedLines"] += 1
                    continue
                records.append(normalize_audit_record(parsed))
                stats["validRecords"] += 1
    except Exception:
        return [], stats

    return records, stats


def get_last_audit_record() -> Optional[Dict[str, Any]]:
    path = get_audit_store_path()
    records, _stats = _read_records_with_stats(path)
    if not records:
        return None
    return records[-1]


def compute_audit_record_hash(record: Dict[str, Any]) -> str:
    normalized = normalize_audit_record(record)
    hash_seed = dict(normalized)
    hash_seed.pop("auditRecordHash", None)
    return sha256_hex(canonical_json(hash_seed))


def append_audit_record(record: Dict[str, Any]) -> Dict[str, Any]:
    path = get_audit_store_path()
    last_record = get_last_audit_record()
    previous_hash = None
    if isinstance(last_record, dict):
        previous_hash = last_record.get("auditRecordHash")

    prepared = dict(record or {})
    prepared["previousAuditHash"] = previous_hash
    prepared["persistedAt"] = _utc_now_iso()
    normalized = normalize_audit_record(prepared)
    normalized["auditRecordHash"] = compute_audit_record_hash(normalized)

    try:
        _ensure_parent_dir(path)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(normalized, ensure_ascii=False, default=str, separators=(",", ":")) + "\n")
        return {
            "auditId": normalized["auditId"],
            "persisted": True,
            "auditRecordHash": normalized.get("auditRecordHash"),
            "previousAuditHash": normalized.get("previousAuditHash"),
            "error": None,
        }
    except Exception as exc:  # pragma: no cover - defensive runtime guard
        return {
            "auditId": normalized["auditId"],
            "persisted": False,
            "auditRecordHash": None,
            "previousAuditHash": normalized.get("previousAuditHash"),
            "error": str(exc),
        }


def list_audit_records(
    limit: int = 50,
    event_type: Optional[str] = None,
    report_id: Optional[str] = None,
    verification_status: Optional[str] = None,
) -> Dict[str, Any]:
    path = get_audit_store_path()
    records, stats = _read_records_with_stats(path)
    if event_type:
        records = [item for item in records if str(item.get("auditEventType")) == str(event_type)]
    if report_id:
        records = [item for item in records if str(item.get("reportId")) == str(report_id)]
    if verification_status:
        records = [item for item in records if str(item.get("verificationStatus")) == str(verification_status)]
    try:
        safe_limit = max(1, min(int(limit), 200))
    except (TypeError, ValueError):
        safe_limit = 50
    return {"items": list(reversed(records))[:safe_limit], "readStats": stats}


def get_audit_record(audit_id: str) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    if not audit_id:
        return None, {
            "totalLines": 0,
            "validRecords": 0,
            "corruptedLines": 0,
            "skippedLines": 0,
            "storePathMode": "local-jsonl",
        }
    path = get_audit_store_path()
    records, stats = _read_records_with_stats(path)
    for item in reversed(records):
        if str(item.get("auditId")) == str(audit_id):
            return item, stats
    return None, stats


def build_audit_record(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(payload or {})
    data["auditEventType"] = event_type
    return normalize_audit_record(data)


def verify_audit_chain(limit: Optional[int] = None) -> Dict[str, Any]:
    path = get_audit_store_path()
    records, stats = _read_records_with_stats(path)
    if limit is not None:
        try:
            safe_limit = max(1, min(int(limit), 200))
            records = records[-safe_limit:]
        except (TypeError, ValueError):
            pass

    failures: List[Dict[str, Any]] = []
    previous_hash: Optional[str] = None
    for index, record in enumerate(records):
        expected_hash = compute_audit_record_hash(record)
        actual_hash = record.get("auditRecordHash")
        if str(actual_hash or "") != str(expected_hash):
            failures.append(
                {
                    "index": index,
                    "auditId": record.get("auditId"),
                    "reason": "auditRecordHash mismatch",
                }
            )
        expected_previous = previous_hash
        actual_previous = record.get("previousAuditHash")
        if actual_previous != expected_previous:
            failures.append(
                {
                    "index": index,
                    "auditId": record.get("auditId"),
                    "reason": "previousAuditHash mismatch",
                }
            )
        previous_hash = record.get("auditRecordHash")

    total_records = len(records)
    failed_records = len({(item.get("index"), item.get("auditId")) for item in failures})
    verified_records = max(total_records - failed_records, 0)
    return {
        "verified": len(failures) == 0,
        "verificationMode": "local-jsonl-hash-chain",
        "totalRecords": total_records,
        "verifiedRecords": verified_records,
        "failedRecords": failed_records,
        "failures": failures,
        "certified": False,
        "iec62443Certified": False,
        "readStats": stats,
    }


def get_reports_audit_retention_policy() -> Dict[str, Any]:
    return {
        "retentionMode": "placeholder-local-jsonl",
        "retentionClass": "audit-readiness-local",
        "defaultRetention": "manual-cleanup",
        "dbRetentionIntegrated": False,
        "legalHoldIntegrated": False,
        "redactionIntegrated": False,
        "certified": False,
        "iec62443Certified": False,
        "notes": "Retention policy placeholder only; no production retention enforcement in R10.",
    }

