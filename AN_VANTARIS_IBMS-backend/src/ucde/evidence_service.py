"""UCDE evidence center service (read-only runtime skeleton)."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from src.ucde.evidence_integrity import build_evidence_hash, build_traceability_hash
from src.ucde.evidence_provider import (
    get_evidence,
    get_evidence_health,
    get_evidence_summary,
    list_evidence,
)


class UcdeEvidenceService:
    MODULE_ID = "ucde"
    MODULE_NAME = "UCDE Evidence Center"
    RUNTIME_MODE = "skeleton"
    PROVIDER = "local-ucde-provider"
    SOURCE_SEMANTICS = "ibms-neutral"

    def get_ucde_health(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "moduleId": self.MODULE_ID,
            "moduleName": self.MODULE_NAME,
            "runtimeMode": self.RUNTIME_MODE,
            "provider": self.PROVIDER,
            "sourceSemantics": self.SOURCE_SEMANTICS,
            "readOnly": True,
            "controlActionsEnabled": False,
            "certified": False,
            "iec62443Certified": False,
            "evidenceChainMode": "hash-only-local-evidence",
            "signatureIntegrated": False,
            "dbPersistenceIntegrated": False,
            "ucdeRuntimeIntegrated": False,
        }

    def list_evidence(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        active_filters = {
            "evidenceType": str((filters or {}).get("evidenceType", "")).strip(),
            "sourceModuleId": str((filters or {}).get("sourceModuleId", "")).strip(),
            "evidenceStatus": str((filters or {}).get("evidenceStatus", "")).strip(),
            "evidenceCategory": str((filters or {}).get("evidenceCategory", "")).strip(),
        }
        items = list_evidence(active_filters)
        return {
            "items": items,
            "total": len(items),
            "filters": active_filters,
            "summary": self.get_evidence_summary(),
            "provider": self.PROVIDER,
            "runtimeMode": self.RUNTIME_MODE,
            "sourceSemantics": self.SOURCE_SEMANTICS,
            "mockData": True,
            "readOnly": True,
            "certified": False,
            "iec62443Certified": False,
        }

    def get_evidence_detail(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        return get_evidence(evidence_id)

    def get_evidence_summary(self) -> Dict[str, Any]:
        summary = get_evidence_summary()
        summary["limitations"] = summary.get("limitations", []) + [
            "UCDE R1 uses hash-only local evidence for traceability readiness.",
            "Not a certification proof in this stage.",
        ]
        return summary

    def verify_evidence_record(
        self, evidence_id: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[int, str]]]:
        item = get_evidence(evidence_id)
        if not item:
            return None, (404, "evidenceId not found")

        expected_evidence_hash = build_evidence_hash(item)
        expected_traceability_hash = build_traceability_hash(item)
        actual_evidence_hash = str(item.get("evidenceHash", ""))
        actual_traceability_hash = str(item.get("traceabilityHash", ""))
        evidence_hash_matches = actual_evidence_hash == expected_evidence_hash
        traceability_hash_matches = actual_traceability_hash == expected_traceability_hash
        return {
            "verified": bool(evidence_hash_matches and traceability_hash_matches),
            "verificationMode": "hash-only-local-evidence",
            "evidenceId": str(item.get("evidenceId", "")),
            "evidenceHashMatches": evidence_hash_matches,
            "traceabilityHashMatches": traceability_hash_matches,
            "certified": False,
            "iec62443Certified": False,
        }, None

    def get_evidence_health(self) -> Dict[str, Any]:
        health = get_evidence_health()
        health["readOnly"] = True
        health["controlActionsEnabled"] = False
        return health

