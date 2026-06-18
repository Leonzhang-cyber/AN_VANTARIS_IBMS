"""UCDE local evidence provider (read-only skeleton)."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.ucde.evidence_integrity import build_evidence_hash, build_traceability_hash


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _source_reference(
    reference_id: str,
    source_module_id: str,
    source_record_id: str,
    source_record_type: str,
    relationship: str,
    source_timestamp: str,
) -> Dict[str, Any]:
    return {
        "referenceId": reference_id,
        "sourceModuleId": source_module_id,
        "sourceRecordId": source_record_id,
        "sourceRecordType": source_record_type,
        "relationship": relationship,
        "sourceTimestamp": source_timestamp,
        "runtimeLinked": False,
        "notes": "Local skeleton reference only; no runtime call.",
    }


def _evidence_reference(reference_id: str, evidence_id: str, relationship: str) -> Dict[str, Any]:
    return {
        "referenceId": reference_id,
        "evidenceId": evidence_id,
        "relationship": relationship,
        "runtimeLinked": False,
        "notes": "Local skeleton evidence relationship.",
    }


def _audit_reference(
    reference_id: str,
    audit_id: str,
    audit_event_type: str,
    source_module_id: str,
    relationship: str,
) -> Dict[str, Any]:
    return {
        "referenceId": reference_id,
        "auditId": audit_id,
        "auditEventType": audit_event_type,
        "sourceModuleId": source_module_id,
        "relationship": relationship,
        "runtimeLinked": False,
        "notes": "Audit reference placeholder; no Reports audit runtime read.",
    }


def _correlation_reference(
    reference_id: str,
    correlation_type: str,
    related_module_ids: List[str],
) -> Dict[str, Any]:
    return {
        "referenceId": reference_id,
        "correlationType": correlation_type,
        "relatedModuleIds": related_module_ids,
        "relationship": "correlates-with",
        "runtimeLinked": False,
        "notes": "Correlation placeholder only.",
    }


def _traceability_path(
    path_id: str,
    source_module_id: str,
    source_record_id: str,
    evidence_id: str,
    source_reference_id: str,
    evidence_reference_id: str,
    verification_reference_id: str,
) -> Dict[str, Any]:
    return {
        "pathId": path_id,
        "pathMode": "local-skeleton-traceability",
        "sourceModuleId": source_module_id,
        "sourceRecordId": source_record_id,
        "evidenceId": evidence_id,
        "steps": [
            {
                "stepOrder": 1,
                "stepType": "source-record",
                "label": "Source Record",
                "referenceId": source_reference_id,
                "runtimeLinked": False,
            },
            {
                "stepOrder": 2,
                "stepType": "evidence-record",
                "label": "Evidence Record",
                "referenceId": evidence_reference_id,
                "runtimeLinked": False,
            },
            {
                "stepOrder": 3,
                "stepType": "hash-verification",
                "label": "Hash Verification",
                "referenceId": verification_reference_id,
                "runtimeLinked": False,
            },
        ],
        "complete": False,
        "completionReason": "R2 local skeleton path only; runtime source linkage is not integrated.",
        "certified": False,
        "iec62443Certified": False,
    }


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
            "sourceReferences": [
                _source_reference(
                    reference_id="src-reports-readiness",
                    source_module_id="reports",
                    source_record_id="reports-readiness-candidate",
                    source_record_type="readiness-record",
                    relationship="originated-from",
                    source_timestamp=now,
                )
            ],
            "evidenceReferences": [
                _evidence_reference(
                    reference_id="evref-reports-audit-foundation",
                    evidence_id="reports-audit-foundation",
                    relationship="supports",
                )
            ],
            "auditReferences": [
                _audit_reference(
                    reference_id="audit-reports-query-foundation",
                    audit_id="reports-audit-readiness-foundation",
                    audit_event_type="report.query",
                    source_module_id="reports",
                    relationship="records-generation",
                )
            ],
            "correlationReferences": [
                _correlation_reference(
                    reference_id="corr-module-readiness",
                    correlation_type="module-readiness",
                    related_module_ids=["reports", "uconsole", "ucde"],
                )
            ],
            "traceabilityPath": _traceability_path(
                path_id="trace-reports-readiness-freeze",
                source_module_id="reports",
                source_record_id="reports-readiness-candidate",
                evidence_id="reports-readiness-freeze",
                source_reference_id="src-reports-readiness",
                evidence_reference_id="evref-reports-audit-foundation",
                verification_reference_id="verify-reports-readiness-freeze",
            ),
            "tags": ["reports", "readiness", "foundation"],
            "metadata": {"stage": "ucde-r2", "scope": "ibms-neutral"},
            "limitations": [
                "No runtime source validation is integrated.",
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
            "sourceReferences": [
                _source_reference(
                    reference_id="src-reports-audit",
                    source_module_id="reports",
                    source_record_id="reports-audit-local-jsonl",
                    source_record_type="audit-record",
                    relationship="originated-from",
                    source_timestamp=now,
                )
            ],
            "evidenceReferences": [
                _evidence_reference(
                    reference_id="evref-reports-readiness-freeze",
                    evidence_id="reports-readiness-freeze",
                    relationship="related-to",
                ),
                _evidence_reference(
                    reference_id="evref-uconsole-score-foundation",
                    evidence_id="uconsole-score-foundation",
                    relationship="supports",
                ),
            ],
            "auditReferences": [
                _audit_reference(
                    reference_id="audit-reports-export-manifest",
                    audit_id="reports-export-manifest-foundation",
                    audit_event_type="report.export_manifest",
                    source_module_id="reports",
                    relationship="audits",
                )
            ],
            "correlationReferences": [
                _correlation_reference(
                    reference_id="corr-audit-readiness",
                    correlation_type="audit-readiness",
                    related_module_ids=["reports", "ucde"],
                )
            ],
            "traceabilityPath": _traceability_path(
                path_id="trace-reports-audit-foundation",
                source_module_id="reports",
                source_record_id="reports-audit-local-jsonl",
                evidence_id="reports-audit-foundation",
                source_reference_id="src-reports-audit",
                evidence_reference_id="evref-reports-readiness-freeze",
                verification_reference_id="verify-reports-audit-foundation",
            ),
            "tags": ["reports", "audit", "hash-only"],
            "metadata": {"stage": "ucde-r2", "mode": "hash-only-local-evidence"},
            "limitations": [
                "No digital signature integration.",
                "Runtime source validation is not integrated.",
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
            "sourceReferences": [
                _source_reference(
                    reference_id="src-uconsole-registry",
                    source_module_id="uconsole",
                    source_record_id="uconsole-readiness-registry",
                    source_record_type="readiness-record",
                    relationship="summarizes",
                    source_timestamp=now,
                )
            ],
            "evidenceReferences": [
                _evidence_reference(
                    reference_id="evref-uconsole-score-foundation",
                    evidence_id="uconsole-score-foundation",
                    relationship="derived-from",
                )
            ],
            "auditReferences": [
                _audit_reference(
                    reference_id="audit-platform-readiness",
                    audit_id="platform-readiness-foundation",
                    audit_event_type="platform.readiness",
                    source_module_id="uconsole",
                    relationship="records-generation",
                )
            ],
            "correlationReferences": [
                _correlation_reference(
                    reference_id="corr-platform-readiness",
                    correlation_type="platform-readiness",
                    related_module_ids=["uconsole", "reports", "ucde"],
                )
            ],
            "traceabilityPath": _traceability_path(
                path_id="trace-uconsole-readiness-registry",
                source_module_id="uconsole",
                source_record_id="uconsole-readiness-registry",
                evidence_id="uconsole-readiness-registry",
                source_reference_id="src-uconsole-registry",
                evidence_reference_id="evref-uconsole-score-foundation",
                verification_reference_id="verify-uconsole-readiness-registry",
            ),
            "tags": ["uconsole", "registry", "foundation"],
            "metadata": {"stage": "ucde-r2", "readOnly": True},
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
            "sourceReferences": [
                _source_reference(
                    reference_id="src-uconsole-score",
                    source_module_id="uconsole",
                    source_record_id="platform-readiness-score",
                    source_record_type="score-record",
                    relationship="derived-from",
                    source_timestamp=now,
                )
            ],
            "evidenceReferences": [
                _evidence_reference(
                    reference_id="evref-uconsole-readiness-registry",
                    evidence_id="uconsole-readiness-registry",
                    relationship="related-to",
                )
            ],
            "auditReferences": [
                _audit_reference(
                    reference_id="audit-platform-readiness-score",
                    audit_id="platform-readiness-score-foundation",
                    audit_event_type="platform.readiness",
                    source_module_id="uconsole",
                    relationship="records-verification",
                )
            ],
            "correlationReferences": [
                _correlation_reference(
                    reference_id="corr-hash-verification",
                    correlation_type="hash-verification",
                    related_module_ids=["uconsole", "ucde"],
                )
            ],
            "traceabilityPath": _traceability_path(
                path_id="trace-uconsole-score-foundation",
                source_module_id="uconsole",
                source_record_id="platform-readiness-score",
                evidence_id="uconsole-score-foundation",
                source_reference_id="src-uconsole-score",
                evidence_reference_id="evref-uconsole-readiness-registry",
                verification_reference_id="verify-uconsole-score-foundation",
            ),
            "tags": ["uconsole", "score", "foundation"],
            "metadata": {"stage": "ucde-r2", "scoreMode": "registry-derived"},
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


def _reference_count(records: List[Dict[str, Any]], key: str) -> int:
    return sum(len(row.get(key, [])) for row in records)


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


def get_evidence_relationships(evidence_id: str) -> Optional[Dict[str, Any]]:
    item = get_evidence(evidence_id)
    if not item:
        return None

    root_node_id = f"node-evidence-{item['evidenceId']}"
    nodes: List[Dict[str, Any]] = [
        {
            "nodeId": root_node_id,
            "nodeType": "evidence",
            "label": str(item.get("evidenceName", item["evidenceId"])),
            "moduleId": str(item.get("sourceModuleId", "")),
            "runtimeLinked": False,
        }
    ]
    edges: List[Dict[str, Any]] = []

    for source in item.get("sourceReferences", []):
        node_id = f"node-source-{source.get('referenceId', '')}"
        nodes.append(
            {
                "nodeId": node_id,
                "nodeType": "source",
                "label": str(source.get("sourceRecordId", source.get("referenceId", ""))),
                "moduleId": str(source.get("sourceModuleId", "")),
                "runtimeLinked": False,
            }
        )
        edges.append(
            {
                "edgeId": f"edge-source-{source.get('referenceId', '')}",
                "from": node_id,
                "to": root_node_id,
                "relationship": str(source.get("relationship", "originated-from")),
                "runtimeLinked": False,
            }
        )

    for evidence in item.get("evidenceReferences", []):
        node_id = f"node-evidence-ref-{evidence.get('referenceId', '')}"
        nodes.append(
            {
                "nodeId": node_id,
                "nodeType": "evidence",
                "label": str(evidence.get("evidenceId", evidence.get("referenceId", ""))),
                "moduleId": str(item.get("sourceModuleId", "")),
                "runtimeLinked": False,
            }
        )
        edges.append(
            {
                "edgeId": f"edge-evidence-{evidence.get('referenceId', '')}",
                "from": root_node_id,
                "to": node_id,
                "relationship": str(evidence.get("relationship", "supports")),
                "runtimeLinked": False,
            }
        )

    for audit in item.get("auditReferences", []):
        node_id = f"node-audit-{audit.get('referenceId', '')}"
        nodes.append(
            {
                "nodeId": node_id,
                "nodeType": "audit",
                "label": str(audit.get("auditEventType", audit.get("referenceId", ""))),
                "moduleId": str(audit.get("sourceModuleId", "")),
                "runtimeLinked": False,
            }
        )
        edges.append(
            {
                "edgeId": f"edge-audit-{audit.get('referenceId', '')}",
                "from": root_node_id,
                "to": node_id,
                "relationship": str(audit.get("relationship", "audits")),
                "runtimeLinked": False,
            }
        )

    for correlation in item.get("correlationReferences", []):
        node_id = f"node-correlation-{correlation.get('referenceId', '')}"
        nodes.append(
            {
                "nodeId": node_id,
                "nodeType": "correlation",
                "label": str(correlation.get("correlationType", correlation.get("referenceId", ""))),
                "moduleId": ",".join(correlation.get("relatedModuleIds", [])),
                "runtimeLinked": False,
            }
        )
        edges.append(
            {
                "edgeId": f"edge-correlation-{correlation.get('referenceId', '')}",
                "from": root_node_id,
                "to": node_id,
                "relationship": str(correlation.get("relationship", "correlates-with")),
                "runtimeLinked": False,
            }
        )

    return {
        "evidenceId": str(item.get("evidenceId", "")),
        "graphMode": "local-skeleton-relationships",
        "nodes": nodes,
        "edges": edges,
        "certified": False,
        "iec62443Certified": False,
        "notes": "Local relationship graph skeleton; no runtime evidence chain.",
    }


def get_evidence_summary() -> Dict[str, Any]:
    items = _normalized_records()
    evidence_types = sorted({str(item.get("evidenceType", "")) for item in items})
    source_modules = sorted({str(item.get("sourceModuleId", "")) for item in items})
    readiness = [item for item in items if str(item.get("evidenceType")) == "readiness-evidence"]
    audit = [item for item in items if "audit" in str(item.get("evidenceType", ""))]
    platform = [item for item in items if "platform" in str(item.get("evidenceType", "")) or "score" in str(item.get("evidenceType", ""))]
    hash_ready = [item for item in items if bool(item.get("evidenceHash")) and bool(item.get("traceabilityHash"))]
    path_count = sum(1 for item in items if isinstance(item.get("traceabilityPath"), dict))
    complete_paths = sum(
        1 for item in items if isinstance(item.get("traceabilityPath"), dict) and bool(item.get("traceabilityPath", {}).get("complete"))
    )
    skeleton_paths = path_count - complete_paths
    total_source_references = _reference_count(items, "sourceReferences")
    total_evidence_references = _reference_count(items, "evidenceReferences")
    total_audit_references = _reference_count(items, "auditReferences")
    total_correlation_references = _reference_count(items, "correlationReferences")
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
        "totalSourceReferences": total_source_references,
        "totalEvidenceReferences": total_evidence_references,
        "totalAuditReferences": total_audit_references,
        "totalCorrelationReferences": total_correlation_references,
        "traceabilityPathCount": path_count,
        "runtimeLinkedReferences": 0,
        "completeTraceabilityPaths": complete_paths,
        "skeletonTraceabilityPaths": skeleton_paths,
        "relationshipGraphReady": True,
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

