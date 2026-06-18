"""Reports query service (IBMS-neutral runtime skeleton)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from src.reports.reports_catalog import get_catalog_item, list_catalog
from src.reports.reports_integrity import (
    build_export_manifest,
    build_payload_hash,
    build_query_hash,
)
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
        return {"manifest": manifest}, None

