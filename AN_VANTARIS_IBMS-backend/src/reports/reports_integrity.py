"""Hash-only integrity helpers for Reports audit readiness."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def sha256_hex(value: Any) -> str:
    if isinstance(value, (dict, list, tuple)):
        payload = canonical_json(value)
    else:
        payload = str(value)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_query_hash(report_id: str, filters: Dict[str, Any], limit: int, aggregation_level: str) -> str:
    seed = {
        "reportId": report_id,
        "filters": filters or {},
        "limit": int(limit),
        "aggregationLevel": aggregation_level or "",
    }
    return sha256_hex(seed)


def build_payload_hash(columns: List[str], rows: List[Dict[str, Any]], summary: Dict[str, Any]) -> str:
    seed = {
        "columns": columns or [],
        "rows": rows or [],
        "summary": summary or {},
    }
    return sha256_hex(seed)


def _collect_string_refs(rows: Iterable[Dict[str, Any]], key: str) -> List[str]:
    refs = set()
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        value = row.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            refs.add(text)
    return sorted(refs)


def build_export_manifest(payload: Dict[str, Any]) -> Dict[str, Any]:
    report_id = str(payload.get("reportId", "")).strip()
    report_name = str(payload.get("reportName", "")).strip() or report_id or "Report"
    query_id = str(payload.get("queryId", "")).strip() or str(uuid.uuid4())
    generated_at = str(payload.get("generatedAt", "")).strip() or utc_now_iso()
    exported_at = utc_now_iso()
    filters = payload.get("filters") if isinstance(payload.get("filters"), dict) else {}
    raw_limit = payload.get("limit", payload.get("rowCount", 0))
    try:
        limit = int(raw_limit or 0)
    except (TypeError, ValueError):
        limit = 0
    aggregation_level = str(payload.get("aggregationLevel", "")).strip() or str(
        filters.get("aggregationLevel", "")
    ).strip()

    columns = payload.get("columns") if isinstance(payload.get("columns"), list) else []
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}

    query_hash = str(payload.get("queryHash", "")).strip() or build_query_hash(
        report_id=report_id,
        filters=filters,
        limit=limit,
        aggregation_level=aggregation_level,
    )
    payload_hash = str(payload.get("payloadHash", "")).strip() or build_payload_hash(
        columns=columns,
        rows=rows,
        summary=summary,
    )

    source_references = payload.get("sourceReferences")
    if not isinstance(source_references, list):
        source_references = _collect_string_refs(rows, "sourceReferenceId")

    evidence_references = payload.get("evidenceReferences")
    if not isinstance(evidence_references, list):
        evidence_references = _collect_string_refs(rows, "evidenceReferenceId")

    manifest_seed = {
        "manifestVersion": "reports-export-manifest-v1",
        "exportId": str(payload.get("exportId", "")).strip() or str(uuid.uuid4()),
        "queryId": query_id,
        "reportId": report_id,
        "reportName": report_name,
        "generatedAt": generated_at,
        "exportedAt": exported_at,
        "sourceSemantics": "ibms-neutral",
        "provider": str(payload.get("provider", "local-mock-provider")),
        "runtimeMode": str(payload.get("runtimeMode", "skeleton")),
        "mockData": bool(payload.get("mockData", True)),
        "queryHash": query_hash,
        "payloadHash": payload_hash,
        "rowCount": len(rows),
        "columnCount": len(columns),
        "sourceReferences": source_references,
        "evidenceReferences": evidence_references,
        "sourceReferenceTypes": payload.get("sourceReferenceTypes")
        if isinstance(payload.get("sourceReferenceTypes"), list)
        else [],
        "evidenceLinked": bool(payload.get("evidenceLinked", False)),
        "hashAlgorithm": "SHA-256",
        "tamperEvidenceMode": "hash-only-local-manifest",
        "certified": False,
        "iec62443Certified": False,
        "notes": "Hash-only local manifest for audit readiness; not a formal certified evidence protocol.",
    }
    manifest_seed["exportHash"] = sha256_hex(manifest_seed)
    return manifest_seed

