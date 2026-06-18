"""UCDE evidence integrity helpers (hash-only local foundation)."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def sha256_hex(value: Any) -> str:
    if isinstance(value, (dict, list)):
        payload = canonical_json(value)
    else:
        payload = str(value)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_evidence_hash(evidence: Dict[str, Any]) -> str:
    data = dict(evidence or {})
    data.pop("evidenceHash", None)
    return sha256_hex(data)


def build_traceability_hash(evidence: Dict[str, Any]) -> str:
    data = evidence or {}
    traceability_payload = {
        "sourceReferences": data.get("sourceReferences", []),
        "evidenceReferences": data.get("evidenceReferences", []),
        "auditReferences": data.get("auditReferences", []),
        "correlationReferences": data.get("correlationReferences", []),
    }
    return sha256_hex(traceability_payload)

