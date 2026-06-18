"""Reports query service (IBMS-neutral runtime skeleton)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from src.reports.reports_catalog import get_catalog_item, list_catalog
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

        result = {
            "reportId": catalog["reportId"],
            "reportName": catalog["reportName"],
            "queryId": str(uuid.uuid4()),
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "filters": filters,
            "columns": mock["columns"],
            "rows": mock["rows"],
            "summary": mock["summary"],
            "source": self.PROVIDER,
            "runtimeMode": self.RUNTIME_MODE,
            "mockData": True,
            "provider": self.PROVIDER,
            "sourceSemantics": self.SOURCE_SEMANTICS,
        }
        return result, None

