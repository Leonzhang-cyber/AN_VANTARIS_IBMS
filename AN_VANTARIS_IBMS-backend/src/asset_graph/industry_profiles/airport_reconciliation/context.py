"""Execution context for airport asset reconciliation."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AirportReconciliationContext:
    tenant_id: str
    site_id: str
    source_workbook_digest: str

    def serialize(self) -> dict[str, str]:
        return {
            "tenantId": self.tenant_id,
            "siteId": self.site_id,
            "sourceWorkbookDigest": self.source_workbook_digest,
        }
