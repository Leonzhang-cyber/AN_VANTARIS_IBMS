"""Local mock provider for Reports runtime skeleton."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_mock_rows(report_id: str, filters: Dict[str, Any], aggregation_level: str, limit: int) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for idx in range(limit):
        rows.append(
            {
                "recordId": f"{report_id}-row-{idx + 1}",
                "sourceType": "reference",
                "sourceReferenceId": f"ref-{idx + 1:04d}",
                "sourceModuleId": filters.get("moduleId", "source-reference"),
                "status": filters.get("status", "open"),
                "severity": filters.get("severity", "medium"),
                "category": filters.get("category", "general"),
                "timestamp": _utc_now_iso(),
                "evidenceReferenceId": filters.get("evidenceReferenceId", f"ev-{idx + 1:04d}"),
                "summary": f"Mock summary for {report_id} #{idx + 1}",
                "count": idx + 1,
                "trendValue": round((idx + 1) * 1.25, 2),
                "aggregationLevel": aggregation_level,
            }
        )

    columns = [
        "recordId",
        "sourceType",
        "sourceReferenceId",
        "sourceModuleId",
        "status",
        "severity",
        "category",
        "timestamp",
        "evidenceReferenceId",
        "summary",
        "count",
        "trendValue",
        "aggregationLevel",
    ]

    summary = {
        "rowCount": len(rows),
        "aggregationLevel": aggregation_level,
        "timeRange": filters.get("timeRange", "unspecified"),
    }

    return {"columns": columns, "rows": rows, "summary": summary}

