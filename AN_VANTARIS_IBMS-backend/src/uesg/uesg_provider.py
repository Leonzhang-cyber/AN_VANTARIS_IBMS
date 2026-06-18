"""UESG local provider (read-only skeleton)."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _metric(
    *,
    metric_id: str,
    metric_name: str,
    metric_category: str,
    metric_scope: str,
    metric_period: str,
    site_id: str,
    site_name: str,
    system_id: str,
    system_name: str,
    value: float,
    unit: str,
    data_quality: str,
    source_record_id: str,
    tags: List[str],
    metadata: Dict[str, Any],
    limitations: List[str],
) -> Dict[str, Any]:
    now = _now_iso()
    return {
        "metricId": metric_id,
        "metricName": metric_name,
        "metricCategory": metric_category,
        "metricScope": metric_scope,
        "metricPeriod": metric_period,
        "siteId": site_id,
        "siteName": site_name,
        "systemId": system_id,
        "systemName": system_name,
        "value": value,
        "unit": unit,
        "dataQuality": data_quality,
        "sourceSystem": "vantaris-one-platform",
        "sourceRecordId": source_record_id,
        "provider": "local-uesg-provider",
        "runtimeMode": "skeleton",
        "sourceSemantics": "ibms-neutral",
        "mockData": True,
        "readOnly": True,
        "controlActionsEnabled": False,
        "meterIntegrationEnabled": False,
        "edgeRuntimeIntegrated": False,
        "linkRuntimeIntegrated": False,
        "carbonFactorDatabaseIntegrated": False,
        "createdAt": now,
        "updatedAt": now,
        "tags": tags,
        "metadata": metadata,
        "limitations": limitations,
        "runtimeLinked": False,
        "certified": False,
        "iec62443Certified": False,
        "greenMarkCertified": False,
        "griCertified": False,
        "isoCertified": False,
    }


def _base_metrics() -> List[Dict[str, Any]]:
    base_limitations = [
        "No DB ESG store.",
        "No real meter integration.",
        "No carbon factor database.",
        "No EDGE/LINK runtime integration.",
        "No certification reporting.",
    ]
    return [
        _metric(
            metric_id="energy-electricity-monthly",
            metric_name="Monthly Electricity Usage",
            metric_category="energy",
            metric_scope="site",
            metric_period="monthly",
            site_id="site-main",
            site_name="Main Site",
            system_id="",
            system_name="",
            value=12850.4,
            unit="kWh",
            data_quality="estimated",
            source_record_id="uesg-energy-electricity-monthly",
            tags=["energy", "electricity", "monthly"],
            metadata={"stage": "uesg-r1"},
            limitations=base_limitations,
        ),
        _metric(
            metric_id="energy-chiller-electricity",
            metric_name="Chiller Electricity Usage",
            metric_category="energy",
            metric_scope="system",
            metric_period="monthly",
            site_id="site-main",
            site_name="Main Site",
            system_id="system-mechanical",
            system_name="Mechanical System",
            value=6320.8,
            unit="kWh",
            data_quality="estimated",
            source_record_id="uesg-energy-chiller-electricity",
            tags=["energy", "chiller", "hvac"],
            metadata={"stage": "uesg-r1"},
            limitations=base_limitations,
        ),
        _metric(
            metric_id="carbon-location-estimate",
            metric_name="Location-Based Carbon Estimate",
            metric_category="carbon",
            metric_scope="site",
            metric_period="monthly",
            site_id="site-main",
            site_name="Main Site",
            system_id="",
            system_name="",
            value=5.42,
            unit="tCO2e",
            data_quality="estimated",
            source_record_id="uesg-carbon-location-estimate",
            tags=["carbon", "location-based", "estimate"],
            metadata={"stage": "uesg-r1"},
            limitations=base_limitations,
        ),
        _metric(
            metric_id="water-consumption-monthly",
            metric_name="Monthly Water Consumption",
            metric_category="water",
            metric_scope="site",
            metric_period="monthly",
            site_id="site-main",
            site_name="Main Site",
            system_id="",
            system_name="",
            value=322.1,
            unit="m3",
            data_quality="estimated",
            source_record_id="uesg-water-consumption-monthly",
            tags=["water", "monthly"],
            metadata={"stage": "uesg-r1"},
            limitations=base_limitations,
        ),
        _metric(
            metric_id="waste-general-monthly",
            metric_name="Monthly General Waste",
            metric_category="waste",
            metric_scope="site",
            metric_period="monthly",
            site_id="site-main",
            site_name="Main Site",
            system_id="",
            system_name="",
            value=1.9,
            unit="ton",
            data_quality="estimated",
            source_record_id="uesg-waste-general-monthly",
            tags=["waste", "monthly"],
            metadata={"stage": "uesg-r1"},
            limitations=base_limitations,
        ),
        _metric(
            metric_id="indoor-environment-score",
            metric_name="Indoor Environment Score",
            metric_category="environment",
            metric_scope="zone",
            metric_period="monthly",
            site_id="site-main",
            site_name="Main Site",
            system_id="zone-plant-room",
            system_name="Plant Room",
            value=82.0,
            unit="score",
            data_quality="derived",
            source_record_id="uesg-indoor-environment-score",
            tags=["environment", "score"],
            metadata={"stage": "uesg-r1"},
            limitations=base_limitations,
        ),
    ]


def _normalized_metrics() -> List[Dict[str, Any]]:
    return [deepcopy(row) for row in _base_metrics()]


def list_metrics(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    values = filters or {}
    metric_category = str(values.get("metricCategory", "")).strip()
    metric_scope = str(values.get("metricScope", "")).strip()
    metric_period = str(values.get("metricPeriod", "")).strip()
    site_id = str(values.get("siteId", "")).strip()
    system_id = str(values.get("systemId", "")).strip()
    data_quality = str(values.get("dataQuality", "")).strip()

    def _match(item: Dict[str, Any]) -> bool:
        if metric_category and str(item.get("metricCategory", "")) != metric_category:
            return False
        if metric_scope and str(item.get("metricScope", "")) != metric_scope:
            return False
        if metric_period and str(item.get("metricPeriod", "")) != metric_period:
            return False
        if site_id and str(item.get("siteId", "")) != site_id:
            return False
        if system_id and str(item.get("systemId", "")) != system_id:
            return False
        if data_quality and str(item.get("dataQuality", "")) != data_quality:
            return False
        return True

    return [item for item in _normalized_metrics() if _match(item)]


def get_metric(metric_id: str) -> Optional[Dict[str, Any]]:
    target = str(metric_id or "").strip()
    if not target:
        return None
    for item in _normalized_metrics():
        if str(item.get("metricId", "")) == target:
            return item
    return None


def get_metrics_summary() -> Dict[str, Any]:
    items = _normalized_metrics()
    categories = sorted({str(item.get("metricCategory", "")) for item in items if str(item.get("metricCategory", "")).strip()})
    scopes = sorted({str(item.get("metricScope", "")) for item in items if str(item.get("metricScope", "")).strip()})
    periods = sorted({str(item.get("metricPeriod", "")) for item in items if str(item.get("metricPeriod", "")).strip()})
    quality = sorted({str(item.get("dataQuality", "")) for item in items if str(item.get("dataQuality", "")).strip()})
    limitations = sorted(
        {
            text
            for item in items
            for text in item.get("limitations", [])
            if isinstance(text, str) and text.strip()
        }
    )
    return {
        "totalMetrics": len(items),
        "energyMetrics": len([item for item in items if str(item.get("metricCategory", "")) == "energy"]),
        "carbonMetrics": len([item for item in items if str(item.get("metricCategory", "")) == "carbon"]),
        "waterMetrics": len([item for item in items if str(item.get("metricCategory", "")) == "water"]),
        "wasteMetrics": len([item for item in items if str(item.get("metricCategory", "")) == "waste"]),
        "environmentMetrics": len([item for item in items if str(item.get("metricCategory", "")) == "environment"]),
        "mockMetrics": len([item for item in items if bool(item.get("mockData"))]),
        "runtimeLinkedMetrics": 0,
        "certifiedMetrics": 0,
        "iec62443CertifiedMetrics": 0,
        "greenMarkCertifiedMetrics": 0,
        "griCertifiedMetrics": 0,
        "isoCertifiedMetrics": 0,
        "metricCategories": categories,
        "metricScopes": scopes,
        "metricPeriods": periods,
        "dataQualityLevels": quality,
        "limitations": limitations,
    }


def get_metrics_breakdown() -> Dict[str, Any]:
    items = _normalized_metrics()
    categories = sorted({str(item.get("metricCategory", "")) for item in items if str(item.get("metricCategory", "")).strip()})
    category_items = []
    for category in categories:
        rows = [item for item in items if str(item.get("metricCategory", "")) == category]
        category_items.append(
            {
                "category": category,
                "count": len(rows),
                "scopes": sorted({str(row.get("metricScope", "")) for row in rows if str(row.get("metricScope", "")).strip()}),
                "periods": sorted({str(row.get("metricPeriod", "")) for row in rows if str(row.get("metricPeriod", "")).strip()}),
                "runtimeLinked": False,
            }
        )
    return {
        "breakdownMode": "local-skeleton-breakdown",
        "items": category_items,
        "runtimeLinked": False,
        "certified": False,
        "iec62443Certified": False,
        "greenMarkCertified": False,
        "griCertified": False,
        "isoCertified": False,
        "notes": "Local skeleton ESG breakdown only; no runtime meter or carbon factor integration.",
    }


def get_associations() -> Dict[str, Any]:
    items = _normalized_metrics()
    associations = [
        {
            "associationId": f"assoc-{item['metricId']}",
            "metricId": item["metricId"],
            "siteId": item["siteId"],
            "systemId": item["systemId"],
            "associationType": "site-system-mapping",
            "runtimeLinked": False,
            "notes": "Association skeleton only; no external runtime binding.",
        }
        for item in items
    ]
    return {
        "associationMode": "local-skeleton-associations",
        "items": associations,
        "runtimeLinked": False,
        "certified": False,
        "iec62443Certified": False,
        "greenMarkCertified": False,
        "griCertified": False,
        "isoCertified": False,
        "notes": "Local ESG associations skeleton; no runtime metering contracts.",
    }


def get_uesg_health() -> Dict[str, Any]:
    summary = get_metrics_summary()
    return {
        "status": "ok",
        "provider": "local-uesg-provider",
        "runtimeMode": "skeleton",
        "sourceSemantics": "ibms-neutral",
        "mockData": True,
        "readOnly": True,
        "controlActionsEnabled": False,
        "meterIntegrationEnabled": False,
        "edgeRuntimeIntegrated": False,
        "linkRuntimeIntegrated": False,
        "carbonFactorDatabaseIntegrated": False,
        "totalMetrics": summary["totalMetrics"],
        "runtimeLinkedMetrics": summary["runtimeLinkedMetrics"],
        "certified": False,
        "iec62443Certified": False,
        "greenMarkCertified": False,
        "griCertified": False,
        "isoCertified": False,
    }

