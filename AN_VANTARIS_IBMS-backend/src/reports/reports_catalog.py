"""In-memory IBMS-neutral report catalog registry."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


CatalogItem = Dict[str, Any]


REPORTS_CATALOG: List[CatalogItem] = [
    {
        "reportId": "incident-summary",
        "reportName": "Incident Summary Report",
        "groupId": "incident-event-reports",
        "groupName": "Incident & Event Reports",
        "sourceModules": ["source-reference", "evidence-reference", "module-status"],
        "sourceReferenceTypes": ["incident", "evidence", "status"],
        "supportedFilters": [
            "timeRange",
            "siteId",
            "moduleId",
            "severity",
            "status",
            "category",
        ],
        "defaultFilters": {"timeRange": "last_24h"},
        "aggregationLevels": ["raw", "hourly", "daily"],
        "exportFormats": ["view-only"],
        "evidenceLinked": True,
        "scheduleEligible": False,
        "status": "runtime-skeleton",
    },
    {
        "reportId": "event-trend",
        "reportName": "Event Trend Report",
        "groupId": "incident-event-reports",
        "groupName": "Incident & Event Reports",
        "sourceModules": ["source-reference", "evidence-reference"],
        "sourceReferenceTypes": ["event", "evidence"],
        "supportedFilters": ["timeRange", "siteId", "moduleId", "category", "severity"],
        "defaultFilters": {"timeRange": "last_7d"},
        "aggregationLevels": ["hourly", "daily", "weekly"],
        "exportFormats": ["view-only"],
        "evidenceLinked": True,
        "scheduleEligible": False,
        "status": "runtime-skeleton",
    },
    {
        "reportId": "maintenance-work-summary",
        "reportName": "Maintenance Work Summary Report",
        "groupId": "maintenance-reports",
        "groupName": "Maintenance Reports",
        "sourceModules": ["maintenance-reference", "incident-reference", "evidence-reference"],
        "sourceReferenceTypes": ["maintenance", "incident", "evidence"],
        "supportedFilters": ["timeRange", "siteId", "assetId", "status", "category"],
        "defaultFilters": {"timeRange": "last_30d"},
        "aggregationLevels": ["daily", "weekly", "monthly"],
        "exportFormats": ["view-only"],
        "evidenceLinked": True,
        "scheduleEligible": False,
        "status": "runtime-skeleton",
    },
    {
        "reportId": "energy-consumption",
        "reportName": "Energy Consumption Report",
        "groupId": "energy-sustainability-reports",
        "groupName": "Energy & Sustainability Reports",
        "sourceModules": ["energy-reference", "operations-reference", "evidence-reference"],
        "sourceReferenceTypes": ["energy", "operations", "evidence"],
        "supportedFilters": ["timeRange", "siteId", "deviceId", "category", "status"],
        "defaultFilters": {"timeRange": "last_30d"},
        "aggregationLevels": ["daily", "weekly", "monthly"],
        "exportFormats": ["view-only"],
        "evidenceLinked": True,
        "scheduleEligible": False,
        "status": "runtime-skeleton",
    },
    {
        "reportId": "evidence-traceability",
        "reportName": "Evidence Traceability Report",
        "groupId": "evidence-audit-reports",
        "groupName": "Evidence & Audit Reports",
        "sourceModules": ["evidence-reference"],
        "sourceReferenceTypes": ["evidence"],
        "supportedFilters": ["timeRange", "moduleId", "evidenceReferenceId", "status"],
        "defaultFilters": {"timeRange": "last_7d"},
        "aggregationLevels": ["raw", "daily"],
        "exportFormats": ["view-only"],
        "evidenceLinked": True,
        "scheduleEligible": False,
        "status": "runtime-skeleton",
    },
    {
        "reportId": "data-operations-summary",
        "reportName": "Data Operations Summary Report",
        "groupId": "data-operations-reports",
        "groupName": "Data Operations Reports",
        "sourceModules": ["data-operations-reference", "operations-reference", "evidence-reference"],
        "sourceReferenceTypes": ["data-operations", "operations", "evidence"],
        "supportedFilters": ["timeRange", "siteId", "moduleId", "status", "category"],
        "defaultFilters": {"timeRange": "last_7d"},
        "aggregationLevels": ["daily", "weekly"],
        "exportFormats": ["view-only"],
        "evidenceLinked": True,
        "scheduleEligible": False,
        "status": "runtime-skeleton",
    },
    {
        "reportId": "operations-summary",
        "reportName": "Operations Summary Report",
        "groupId": "operations-summary-reports",
        "groupName": "Operations Summary Reports",
        "sourceModules": [
            "operations-reference",
            "incident-reference",
            "maintenance-reference",
            "energy-reference",
            "data-operations-reference",
        ],
        "sourceReferenceTypes": ["operations", "incident", "maintenance", "energy", "data-operations"],
        "supportedFilters": ["timeRange", "siteId", "moduleId", "status", "severity", "category"],
        "defaultFilters": {"timeRange": "last_24h"},
        "aggregationLevels": ["hourly", "daily"],
        "exportFormats": ["view-only"],
        "evidenceLinked": False,
        "scheduleEligible": False,
        "status": "runtime-skeleton",
    },
    {
        "reportId": "module-readiness",
        "reportName": "Module Readiness Report",
        "groupId": "module-status-reports",
        "groupName": "Module Status Reports",
        "sourceModules": ["module-status-reference"],
        "sourceReferenceTypes": ["module-status"],
        "supportedFilters": ["timeRange", "moduleId", "status", "category"],
        "defaultFilters": {"timeRange": "last_24h"},
        "aggregationLevels": ["raw", "daily"],
        "exportFormats": ["view-only"],
        "evidenceLinked": False,
        "scheduleEligible": False,
        "status": "runtime-skeleton",
    },
]


def list_catalog() -> List[CatalogItem]:
    return REPORTS_CATALOG


def get_catalog_item(report_id: str) -> Optional[CatalogItem]:
    for item in REPORTS_CATALOG:
        if item.get("reportId") == report_id:
            return item
    return None

