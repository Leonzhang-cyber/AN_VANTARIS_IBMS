"""Execution context for airport review projection."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AirportReviewProjectionContext:
    tenant_id: str
    site_id: str
    source_workbook_digest: str
    reconciliation_result_digest: str | None = None
    page_size: int = 50

    def serialize(self) -> dict[str, str | int | None]:
        return {
            "tenantId": self.tenant_id,
            "siteId": self.site_id,
            "sourceWorkbookDigest": self.source_workbook_digest,
            "reconciliationResultDigest": self.reconciliation_result_digest,
            "pageSize": self.page_size,
        }
