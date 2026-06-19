"""Execution context for airport classification profile."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AirportClassificationContext:
    tenant_id: str
    site_id: str
    source_workbook_digest: str
    expected_intake_result_digest: str | None = None
    expected_spatial_result_digest: str | None = None

    def serialize(self) -> dict[str, str | None]:
        return {
            "tenantId": self.tenant_id,
            "siteId": self.site_id,
            "sourceWorkbookDigest": self.source_workbook_digest,
            "expectedIntakeResultDigest": self.expected_intake_result_digest,
            "expectedSpatialResultDigest": self.expected_spatial_result_digest,
        }
