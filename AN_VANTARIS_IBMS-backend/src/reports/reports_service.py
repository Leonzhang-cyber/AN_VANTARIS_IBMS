"""Reports query service (IBMS-neutral runtime skeleton)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.reports.reports_audit_store import (
    append_audit_record,
    build_audit_record,
    get_reports_audit_retention_policy,
    get_audit_record,
    list_audit_records,
    verify_audit_chain,
)
from src.reports.reports_catalog import get_catalog_item, list_catalog
from src.reports.reports_integrity import (
    build_export_manifest,
    build_payload_hash,
    build_query_hash,
)
from src.reports.reports_permissions import evaluate_report_permission
from src.reports.reports_provider import get_mock_rows


class ReportsService:
    PROVIDER = "local-mock-provider"
    RUNTIME_MODE = "skeleton"
    SOURCE_SEMANTICS = "ibms-neutral"

    @staticmethod
    def list_catalog():
        return list_catalog()

    @staticmethod
    def get_catalog(report_id: str):
        return get_catalog_item(report_id)

    def query_report(self, payload: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[int, str]]]:
        report_id = (payload or {}).get("reportId")
        if not report_id:
            return None, (400, "reportId is required")

        catalog = get_catalog_item(report_id)
        if not catalog:
            return None, (404, "reportId not found")

        filters = (payload or {}).get("filters") or {}
        if not isinstance(filters, dict):
            return None, (400, "filters must be an object")

        limit = payload.get("limit", 20)
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            return None, (400, "limit must be an integer")

        if limit <= 0:
            limit = 20
        if limit > 100:
            limit = 100

        aggregation_level = payload.get("aggregationLevel") or filters.get("aggregationLevel") or "raw"

        mock = get_mock_rows(report_id=report_id, filters=filters, aggregation_level=aggregation_level, limit=limit)
        query_id = str(uuid.uuid4())
        generated_at = datetime.now(timezone.utc).isoformat()
        query_hash = build_query_hash(
            report_id=report_id,
            filters=filters,
            limit=limit,
            aggregation_level=aggregation_level,
        )
        payload_hash = build_payload_hash(
            columns=mock["columns"],
            rows=mock["rows"],
            summary=mock["summary"],
        )
        source_references = sorted(
            {
                str(row.get("sourceReferenceId")).strip()
                for row in mock["rows"]
                if isinstance(row, dict) and row.get("sourceReferenceId")
            }
        )
        evidence_references = sorted(
            {
                str(row.get("evidenceReferenceId")).strip()
                for row in mock["rows"]
                if isinstance(row, dict) and row.get("evidenceReferenceId")
            }
        )

        result = {
            "reportId": catalog["reportId"],
            "reportName": catalog["reportName"],
            "queryId": query_id,
            "generatedAt": generated_at,
            "filters": filters,
            "columns": mock["columns"],
            "rows": mock["rows"],
            "summary": mock["summary"],
            "source": self.PROVIDER,
            "runtimeMode": self.RUNTIME_MODE,
            "mockData": True,
            "provider": self.PROVIDER,
            "sourceSemantics": self.SOURCE_SEMANTICS,
            "integrity": {
                "queryHash": query_hash,
                "payloadHash": payload_hash,
                "hashAlgorithm": "SHA-256",
                "tamperEvidenceMode": "hash-only",
                "certified": False,
                "iec62443Certified": False,
            },
            "audit": {
                "queryId": query_id,
                "auditEventType": "report.query",
                "generatedAt": generated_at,
                "reportId": report_id,
                "sourceSemantics": self.SOURCE_SEMANTICS,
                "provider": self.PROVIDER,
                "mockData": True,
                "auditMode": "runtime-skeleton-local",
                "persisted": False,
            },
            "traceability": {
                "sourceReferences": source_references,
                "evidenceReferences": evidence_references,
                "sourceReferenceTypes": catalog.get("sourceReferenceTypes", []),
                "evidenceLinked": bool(catalog.get("evidenceLinked", False)),
            },
        }
        permission = evaluate_report_permission(action="query", report_id=report_id, context={"mode": "reports-r11"})
        record = build_audit_record(
            event_type="report.query",
            payload={
                "reportId": result["reportId"],
                "reportName": result["reportName"],
                "queryId": query_id,
                "generatedAt": generated_at,
                "provider": self.PROVIDER,
                "runtimeMode": self.RUNTIME_MODE,
                "mockData": True,
                "queryHash": query_hash,
                "payloadHash": payload_hash,
                "rowCount": len(mock["rows"]),
                "columnCount": len(mock["columns"]),
                "sourceReferences": source_references,
                "evidenceReferences": evidence_references,
                "permissionDecision": permission.get("allowed", True),
                "permissionMode": permission.get("permissionMode", "placeholder-allow"),
                "tamperEvidenceMode": "hash-only",
                "notes": "Query audit foundation in local JSONL store.",
            },
        )
        persist_result = append_audit_record(record)
        result["audit"]["auditId"] = persist_result.get("auditId") or record["auditId"]
        result["audit"]["persisted"] = bool(persist_result.get("persisted"))
        result["audit"]["storageMode"] = "local-jsonl"
        result["audit"]["permissionDecision"] = permission.get("allowed", True)
        result["audit"]["permissionMode"] = permission.get("permissionMode", "placeholder-allow")
        result["audit"]["auditRecordHash"] = persist_result.get("auditRecordHash")
        result["audit"]["previousAuditHash"] = persist_result.get("previousAuditHash")
        result["audit"]["retentionClass"] = "audit-readiness-local"
        result["audit"]["retentionPolicy"] = "local-jsonl-retain-until-manual-cleanup"
        result["audit"]["verificationStatus"] = "not-verified"
        result["permission"] = permission
        if persist_result.get("error"):
            result["audit"]["auditPersistError"] = str(persist_result.get("error"))
        return result, None

    def build_export_manifest_preview(
        self, payload: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[int, str]]]:
        report_id = str((payload or {}).get("reportId", "")).strip()
        if not report_id:
            return None, (400, "reportId is required")

        catalog = get_catalog_item(report_id)
        if not catalog:
            return None, (404, "reportId not found")

        columns = payload.get("columns")
        rows = payload.get("rows")
        summary = payload.get("summary")
        if not isinstance(columns, list) or not isinstance(rows, list) or not isinstance(summary, dict):
            return None, (400, "columns, rows, and summary are required")

        filters = payload.get("filters") if isinstance(payload.get("filters"), dict) else {}
        aggregation_level = str(payload.get("aggregationLevel") or filters.get("aggregationLevel") or "").strip()
        limit = payload.get("limit", len(rows))
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = len(rows)

        query_hash = build_query_hash(
            report_id=report_id,
            filters=filters,
            limit=limit,
            aggregation_level=aggregation_level,
        )
        payload_hash = build_payload_hash(columns=columns, rows=rows, summary=summary)

        manifest = build_export_manifest(
            {
                "reportId": report_id,
                "reportName": payload.get("reportName", catalog.get("reportName", report_id)),
                "queryId": payload.get("queryId"),
                "generatedAt": payload.get("generatedAt"),
                "filters": filters,
                "limit": limit,
                "aggregationLevel": aggregation_level,
                "columns": columns,
                "rows": rows,
                "summary": summary,
                "provider": payload.get("provider", self.PROVIDER),
                "runtimeMode": payload.get("runtimeMode", self.RUNTIME_MODE),
                "mockData": payload.get("mockData", True),
                "queryHash": query_hash,
                "payloadHash": payload_hash,
                "sourceReferenceTypes": catalog.get("sourceReferenceTypes", []),
                "evidenceLinked": catalog.get("evidenceLinked", False),
            }
        )
        permission = evaluate_report_permission(
            action="export_manifest", report_id=report_id, context={"mode": "reports-r11"}
        )
        record = build_audit_record(
            event_type="report.export_manifest",
            payload={
                "reportId": report_id,
                "reportName": manifest.get("reportName", ""),
                "queryId": manifest.get("queryId", ""),
                "exportId": manifest.get("exportId", ""),
                "generatedAt": manifest.get("generatedAt", ""),
                "provider": manifest.get("provider", self.PROVIDER),
                "runtimeMode": manifest.get("runtimeMode", self.RUNTIME_MODE),
                "mockData": manifest.get("mockData", True),
                "queryHash": manifest.get("queryHash", ""),
                "payloadHash": manifest.get("payloadHash", ""),
                "exportHash": manifest.get("exportHash", ""),
                "rowCount": manifest.get("rowCount", 0),
                "columnCount": manifest.get("columnCount", 0),
                "sourceReferences": manifest.get("sourceReferences", []),
                "evidenceReferences": manifest.get("evidenceReferences", []),
                "permissionDecision": permission.get("allowed", True),
                "permissionMode": permission.get("permissionMode", "placeholder-allow"),
                "tamperEvidenceMode": manifest.get("tamperEvidenceMode", "hash-only-local-manifest"),
                "notes": "Export manifest audit foundation in local JSONL store.",
            },
        )
        persist_result = append_audit_record(record)
        manifest["auditId"] = persist_result.get("auditId") or record["auditId"]
        manifest["auditPersisted"] = bool(persist_result.get("persisted"))
        manifest["storageMode"] = "local-jsonl"
        manifest["permissionDecision"] = permission.get("allowed", True)
        manifest["permissionMode"] = permission.get("permissionMode", "placeholder-allow")
        manifest["auditRecordHash"] = persist_result.get("auditRecordHash")
        manifest["previousAuditHash"] = persist_result.get("previousAuditHash")
        manifest["retentionClass"] = "audit-readiness-local"
        manifest["retentionPolicy"] = "local-jsonl-retain-until-manual-cleanup"
        manifest["verificationStatus"] = "not-verified"
        manifest["permission"] = permission
        if persist_result.get("error"):
            manifest["auditPersistError"] = str(persist_result.get("error"))
        return {"manifest": manifest}, None

    def list_audit(
        self,
        limit: int = 50,
        event_type: Optional[str] = None,
        report_id: Optional[str] = None,
        verification_status: Optional[str] = None,
    ) -> Dict[str, Any]:
        permission = evaluate_report_permission(action="view_audit", report_id=report_id or "*", context={})
        records_result = list_audit_records(
            limit=limit,
            event_type=event_type,
            report_id=report_id,
            verification_status=verification_status,
        )
        records: List[Dict[str, Any]] = records_result.get("items", [])
        return {
            "items": records,
            "total": len(records),
            "storageMode": "local-jsonl",
            "readStats": records_result.get("readStats", {}),
            "permissionMode": permission.get("permissionMode", "placeholder-allow"),
            "permissionDecision": permission.get("allowed", True),
            "permission": permission,
        }

    def get_audit_detail(self, audit_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[int, str]]]:
        permission = evaluate_report_permission(action="view_audit", report_id="*", context={"auditId": audit_id})
        record, read_stats = get_audit_record(audit_id)
        if not record:
            return None, (404, "auditId not found")
        return {
            "item": record,
            "storageMode": "local-jsonl",
            "readStats": read_stats,
            "permissionMode": permission.get("permissionMode", "placeholder-allow"),
            "permissionDecision": permission.get("allowed", True),
            "permission": permission,
        }, None

    def verify_audit(self, limit: Optional[int] = None) -> Dict[str, Any]:
        permission = evaluate_report_permission(action="verify_audit", report_id="*", context={"limit": limit})
        verification = verify_audit_chain(limit=limit)
        verification["permissionMode"] = permission.get("permissionMode", "placeholder-allow")
        verification["permissionDecision"] = permission.get("allowed", True)
        verification["permission"] = permission
        return verification

    def get_audit_retention_policy(self) -> Dict[str, Any]:
        permission = evaluate_report_permission(action="view_audit", report_id="*", context={"policy": "retention"})
        policy = get_reports_audit_retention_policy()
        policy["permissionMode"] = permission.get("permissionMode", "placeholder-allow")
        policy["permissionDecision"] = permission.get("allowed", True)
        policy["permission"] = permission
        return policy

