"""UCDE evidence center service (read-only runtime skeleton)."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from src.ucde.evidence_integrity import build_evidence_hash, build_traceability_hash
from src.ucde.evidence_provider import (
    get_evidence,
    get_evidence_health,
    get_evidence_relationships,
    get_evidence_summary,
    get_ucde_ga_r4_catalog,
    get_ucde_ga_r4_customer_preview,
    get_ucde_ga_r4_guardrails,
    get_ucde_ga_r4_uhmi_linkage,
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
            "UCDE R2 uses hash-only local evidence for traceability readiness.",
            "Not a certification proof in this stage.",
        ]
        return summary

    def get_evidence_relationships(
        self, evidence_id: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[int, str]]]:
        relationships = get_evidence_relationships(evidence_id)
        if not relationships:
            return None, (404, "evidenceId not found")
        return relationships, None

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
        source_reference_count = len(item.get("sourceReferences", []))
        evidence_reference_count = len(item.get("evidenceReferences", []))
        audit_reference_count = len(item.get("auditReferences", []))
        correlation_reference_count = len(item.get("correlationReferences", []))
        traceability_path_complete = bool(item.get("traceabilityPath", {}).get("complete"))
        return {
            "verified": bool(evidence_hash_matches and traceability_hash_matches),
            "verificationMode": "hash-only-local-evidence",
            "evidenceId": str(item.get("evidenceId", "")),
            "evidenceHashMatches": evidence_hash_matches,
            "traceabilityHashMatches": traceability_hash_matches,
            "evidenceHashExpected": expected_evidence_hash,
            "evidenceHashActual": actual_evidence_hash,
            "traceabilityHashExpected": expected_traceability_hash,
            "traceabilityHashActual": actual_traceability_hash,
            "sourceReferenceCount": source_reference_count,
            "evidenceReferenceCount": evidence_reference_count,
            "auditReferenceCount": audit_reference_count,
            "correlationReferenceCount": correlation_reference_count,
            "traceabilityPathComplete": traceability_path_complete,
            "verificationNotes": [
                "Hash verification is local and deterministic.",
                "Runtime source record validation is not integrated.",
                "No digital signature is applied in R2.",
            ],
            "limitations": [
                "no DB evidence store",
                "no digital signature",
                "no runtime source validation",
                "no formal immutable protocol",
                "no certification claim",
            ],
            "certified": False,
            "iec62443Certified": False,
        }, None

    def get_evidence_health(self) -> Dict[str, Any]:
        health = get_evidence_health()
        health["readOnly"] = True
        health["controlActionsEnabled"] = False
        return health

    def get_r4_evidence_center(self) -> Dict[str, Any]:
        return get_ucde_ga_r4_customer_preview()

    def get_r4_evidence_catalog(self) -> Dict[str, Any]:
        return get_ucde_ga_r4_catalog()

    def get_r4_evidence_records(self) -> Dict[str, Any]:
        catalog = get_ucde_ga_r4_catalog()
        return {
            "scope": catalog["scope"],
            "mode": catalog["mode"],
            "visualStyle": catalog["visualStyle"],
            "evidenceRecords": catalog["evidenceRecords"],
            "evidenceWrite": False,
            "dbWrite": False,
            "runtimeActivation": False,
            "deviceControl": False,
            "edgeCommandExecution": False,
            "linkCommandExecution": False,
        }

    def get_r4_evidence_links(self) -> Dict[str, Any]:
        return get_ucde_ga_r4_uhmi_linkage()

    def get_r4_uhmi_linkage(self) -> Dict[str, Any]:
        return get_ucde_ga_r4_uhmi_linkage()

    def get_r4_customer_preview(self) -> Dict[str, Any]:
        return get_ucde_ga_r4_customer_preview()

    def get_r4_guardrails(self) -> Dict[str, Any]:
        return get_ucde_ga_r4_guardrails()
