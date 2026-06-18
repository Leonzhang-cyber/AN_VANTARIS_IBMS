"""UCDE local evidence provider (read-only skeleton)."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.ucde.evidence_integrity import build_evidence_hash, build_traceability_hash


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base_records() -> List[Dict[str, Any]]:
    now = _now_iso()
    common = {
        "provider": "local-ucde-provider",
        "runtimeMode": "skeleton",
        "sourceSemantics": "ibms-neutral",
        "mockData": True,
        "hashAlgorithm": "SHA-256",
        "tamperEvidenceMode": "hash-only-local-evidence",
        "certified": False,
        "iec62443Certified": False,
        "sourceReferences": [],
        "evidenceReferences": [],
        "auditReferences": [],
        "correlationReferences": [],
        "tags": [],
        "metadata": {},
    }
    return [
        {
            **common,
            "evidenceId": "reports-readiness-freeze",
            "evidenceType": "readiness-evidence",
            "evidenceName": "Reports Readiness Freeze Snapshot",
            "evidenceStatus": "foundation",
            "evidenceCategory": "module-readiness",
            "sourceSystem": "vantaris-one-platform",
            "sourceModuleId": "reports",
            "sourceRecordId": "reports-readiness-candidate",
            "sourceTimestamp": now,
            "capturedAt": now,
            "createdAt": now,
            "updatedAt": now,
            "sourceReferences": ["reports:readiness-candidate"],
            "evidenceReferences": ["reports:query-hash-foundation"],
            "auditReferences": ["reports:audit-readiness-foundation"],
            "correlationReferences": ["uconsole:readiness-registry"],
            "tags": ["reports", "readiness", "foundation"],
            "metadata": {"stage": "ucde-r1", "scope": "ibms-neutral"},
            "limitations": [
                "No runtime pull from Reports APIs in this stage.",
                "No DB persistence for evidence records.",
            ],
            "notes": "Local skeleton snapshot for readiness traceability.",
        },
        {
            **common,
            "evidenceId": "reports-audit-foundation",
            "evidenceType": "audit-readiness-evidence",
            "evidenceName": "Reports Audit Foundation Snapshot",
            "evidenceStatus": "foundation",
            "evidenceCategory": "audit-readiness",
            "sourceSystem": "vantaris-one-platform",
            "sourceModuleId": "reports",
            "sourceRecordId": "reports-audit-local-jsonl",
            "sourceTimestamp": now,
            "capturedAt": now,
            "createdAt": now,
            "updatedAt": now,
            "sourceReferences": ["reports:audit-local-jsonl"],
            "evidenceReferences": ["reports:export-manifest-hash"],
            "auditReferences": ["reports:verify-audit-chain"],
            "correlationReferences": ["ucde:evidence-center-foundation"],
            "tags": ["reports", "audit", "hash-only"],
            "metadata": {"stage": "ucde-r1", "mode": "hash-only-local-evidence"},
            "limitations": [
                "No signed evidence payload.",
                "No formal certification linkage in this stage.",
            ],
            "notes": "Audit readiness evidence in local hash-only mode.",
        },
        {
            **common,
            "evidenceId": "uconsole-readiness-registry",
            "evidenceType": "platform-readiness-evidence",
            "evidenceName": "UConsole Registry Foundation Snapshot",
            "evidenceStatus": "foundation",
            "evidenceCategory": "platform-readiness",
            "sourceSystem": "vantaris-one-platform",
            "sourceModuleId": "uconsole",
            "sourceRecordId": "uconsole-readiness-registry",
            "sourceTimestamp": now,
            "capturedAt": now,
            "createdAt": now,
            "updatedAt": now,
            "sourceReferences": ["uconsole:readiness-registry"],
            "evidenceReferences": ["uconsole:module-health-detail"],
            "auditReferences": [],
            "correlationReferences": ["uconsole:platform-operations-dashboard"],
            "tags": ["uconsole", "registry", "foundation"],
            "metadata": {"stage": "ucde-r1", "readOnly": True},
            "limitations": ["No runtime orchestration data is collected in this stage."],
            "notes": "Registry-derived evidence entry for platform operations.",
        },
        {
            **common,
            "evidenceId": "uconsole-score-foundation",
            "evidenceType": "score-evidence",
            "evidenceName": "Platform Readiness Score Foundation Snapshot",
            "evidenceStatus": "foundation",
            "evidenceCategory": "platform-readiness",
            "sourceSystem": "vantaris-one-platform",
            "sourceModuleId": "uconsole",
            "sourceRecordId": "platform-readiness-score",
            "sourceTimestamp": now,
            "capturedAt": now,
            "createdAt": now,
            "updatedAt": now,
            "sourceReferences": ["uconsole:readiness-score"],
            "evidenceReferences": ["uconsole:score-breakdown"],
            "auditReferences": [],
            "correlationReferences": ["uconsole:navigation-model"],
            "tags": ["uconsole", "score", "foundation"],
            "metadata": {"stage": "ucde-r1", "scoreMode": "registry-derived"},
            "limitations": ["Score is local registry-derived and not a certification result."],
            "notes": "Score evidence foundation for platform traceability readiness.",
        },
    ]


def _finalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    item = deepcopy(record)
    item["traceabilityHash"] = build_traceability_hash(item)
    item["evidenceHash"] = build_evidence_hash(item)
    return item


def _normalized_records() -> List[Dict[str, Any]]:
    return [_finalize_record(row) for row in _base_records()]


def list_evidence(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    values = filters or {}
    evidence_type = str(values.get("evidenceType", "")).strip()
    source_module_id = str(values.get("sourceModuleId", "")).strip()
    evidence_status = str(values.get("evidenceStatus", "")).strip()
    evidence_category = str(values.get("evidenceCategory", "")).strip()

    def _match(item: Dict[str, Any]) -> bool:
        if evidence_type and str(item.get("evidenceType", "")) != evidence_type:
            return False
        if source_module_id and str(item.get("sourceModuleId", "")) != source_module_id:
            return False
        if evidence_status and str(item.get("evidenceStatus", "")) != evidence_status:
            return False
        if evidence_category and str(item.get("evidenceCategory", "")) != evidence_category:
            return False
        return True

    return [item for item in _normalized_records() if _match(item)]


def get_evidence(evidence_id: str) -> Optional[Dict[str, Any]]:
    target = str(evidence_id or "").strip()
    if not target:
        return None
    for item in _normalized_records():
        if str(item.get("evidenceId")) == target:
            return item
    return None


def get_evidence_summary() -> Dict[str, Any]:
    items = _normalized_records()
    evidence_types = sorted({str(item.get("evidenceType", "")) for item in items})
    source_modules = sorted({str(item.get("sourceModuleId", "")) for item in items})
    readiness = [item for item in items if str(item.get("evidenceType")) == "readiness-evidence"]
    audit = [item for item in items if "audit" in str(item.get("evidenceType", ""))]
    platform = [item for item in items if "platform" in str(item.get("evidenceType", "")) or "score" in str(item.get("evidenceType", ""))]
    hash_ready = [item for item in items if bool(item.get("evidenceHash")) and bool(item.get("traceabilityHash"))]
    limitations: List[str] = sorted(
        {
            text
            for item in items
            for text in item.get("limitations", [])
            if isinstance(text, str) and text.strip()
        }
    )
    return {
        "totalEvidence": len(items),
        "readinessEvidence": len(readiness),
        "auditEvidence": len(audit),
        "platformEvidence": len(platform),
        "hashReadyEvidence": len(hash_ready),
        "signedEvidence": 0,
        "certifiedEvidence": 0,
        "iec62443CertifiedEvidence": 0,
        "sourceModules": source_modules,
        "evidenceTypes": evidence_types,
        "limitations": limitations,
    }


def get_evidence_health() -> Dict[str, Any]:
    summary = get_evidence_summary()
    return {
        "status": "ok",
        "provider": "local-ucde-provider",
        "runtimeMode": "skeleton",
        "sourceSemantics": "ibms-neutral",
        "evidenceChainMode": "hash-only-local-evidence",
        "totalEvidence": summary["totalEvidence"],
        "hashReadyEvidence": summary["hashReadyEvidence"],
        "certified": False,
        "iec62443Certified": False,
    }

