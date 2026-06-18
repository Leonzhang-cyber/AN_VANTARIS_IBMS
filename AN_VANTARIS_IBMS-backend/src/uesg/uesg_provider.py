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
    if metric_category == "energy":
        assumptions = ["Energy uses local mock kWh value in this stage."]
    elif metric_category == "carbon":
        assumptions = ["Carbon uses estimated value without external carbon factor database."]
    elif metric_category == "water":
        assumptions = ["Water uses local mock consumption value in this stage."]
    elif metric_category == "waste":
        assumptions = ["Waste uses local mock quantity in this stage."]
    else:
        assumptions = ["Indoor environment uses local mock score in this stage."]
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
        "calculationDetail": {
            "calculationMode": "local-skeleton-estimate",
            "formulaMode": "placeholder",
            "inputReferences": [],
            "assumptions": assumptions,
            "dataQuality": data_quality,
            "calculationReady": False,
            "runtimeLinked": False,
            "carbonFactorDatabaseIntegrated": False,
            "meterIntegrationEnabled": False,
            "notes": "Calculation detail is local skeleton only; no certified calculation method is applied.",
            "certified": False,
            "greenMarkCertified": False,
            "griCertified": False,
            "isoCertified": False,
        },
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
            data_quality="manual",
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
        "categoryDetailReady": True,
        "calculationDetailReady": True,
        "associationDetailReady": True,
        "dataQualityReady": True,
        "trendPlaceholderReady": True,
        "runtimeLinkedMetrics": 0,
        "meterLinkedMetrics": 0,
        "carbonFactorLinkedMetrics": 0,
        "reportReadyMetrics": 0,
        "complianceCertifiedMetrics": 0,
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


def get_esg_category_details() -> Dict[str, Any]:
    items = _normalized_metrics()
    categories = sorted({str(item.get("metricCategory", "")) for item in items if str(item.get("metricCategory", "")).strip()})
    names = {
        "energy": "Energy",
        "carbon": "Carbon",
        "water": "Water",
        "waste": "Waste",
        "environment": "Indoor Environment",
    }

    def _quality_summary(rows: List[Dict[str, Any]]) -> Dict[str, int]:
        summary = {"estimated": 0, "measured": 0, "manual": 0, "unknown": 0}
        for row in rows:
            quality = str(row.get("dataQuality", "")).strip().lower()
            if quality in summary:
                summary[quality] += 1
            else:
                summary["unknown"] += 1
        return summary

    result_items = []
    for category in categories:
        rows = [item for item in items if str(item.get("metricCategory", "")) == category]
        unit_values: Dict[str, float] = {}
        for row in rows:
            unit = str(row.get("unit", "")).strip() or "unitless"
            unit_values[unit] = float(unit_values.get(unit, 0.0)) + float(row.get("value", 0.0))
        primary_unit = max(unit_values, key=unit_values.get) if unit_values else ""
        total_value = float(unit_values.get(primary_unit, 0.0)) if primary_unit else 0.0
        result_items.append(
            {
                "categoryId": category,
                "categoryName": names.get(category, category.title()),
                "categoryMode": "local-skeleton-category",
                "metricCount": len(rows),
                "metrics": [
                    {
                        "metricId": str(row.get("metricId", "")),
                        "metricName": str(row.get("metricName", "")),
                        "unit": str(row.get("unit", "")),
                        "value": float(row.get("value", 0.0)),
                        "dataQuality": str(row.get("dataQuality", "")),
                    }
                    for row in rows
                ],
                "primaryUnit": primary_unit,
                "units": sorted(unit_values.keys()),
                "totalValue": total_value,
                "dataQualitySummary": _quality_summary(rows),
                "calculationModes": ["local-skeleton-estimate"],
                "runtimeLinked": False,
                "meterIntegrationEnabled": False,
                "carbonFactorDatabaseIntegrated": False,
                "certified": False,
                "greenMarkCertified": False,
                "griCertified": False,
                "isoCertified": False,
                "limitations": [
                    "Local skeleton category only.",
                    "No real meter integration.",
                    "No certification reporting.",
                ],
            }
        )
    return {
        "categoryMode": "local-skeleton-category",
        "items": result_items,
        "runtimeLinked": False,
        "certified": False,
        "greenMarkCertified": False,
        "griCertified": False,
        "isoCertified": False,
        "notes": "Category details are local skeleton readiness only.",
    }


def get_metric_calculation(metric_id: str) -> Optional[Dict[str, Any]]:
    metric = get_metric(metric_id)
    if not metric:
        return None
    return {
        "metricId": str(metric.get("metricId", "")),
        "metricName": str(metric.get("metricName", "")),
        "metricCategory": str(metric.get("metricCategory", "")),
        "calculationDetail": deepcopy(metric.get("calculationDetail", {})),
        "runtimeLinked": False,
        "certified": False,
        "greenMarkCertified": False,
        "griCertified": False,
        "isoCertified": False,
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


def get_esg_site_system_associations() -> Dict[str, Any]:
    items = _normalized_metrics()
    site_index: Dict[str, Dict[str, Any]] = {}
    system_index: Dict[str, Dict[str, Any]] = {}

    for item in items:
        site_id = str(item.get("siteId", "")).strip()
        site_name = str(item.get("siteName", "")).strip()
        system_id = str(item.get("systemId", "")).strip()
        system_name = str(item.get("systemName", "")).strip()
        metric_id = str(item.get("metricId", "")).strip()
        metric_category = str(item.get("metricCategory", "")).strip()

        if site_id:
            record = site_index.setdefault(
                site_id,
                {
                    "siteId": site_id,
                    "siteName": site_name,
                    "metricIds": [],
                    "metricCategories": set(),
                    "runtimeLinked": False,
                },
            )
            record["metricIds"].append(metric_id)
            record["metricCategories"].add(metric_category)

        if system_id:
            record = system_index.setdefault(
                system_id,
                {
                    "systemId": system_id,
                    "systemName": system_name,
                    "metricIds": [],
                    "metricCategories": set(),
                    "runtimeLinked": False,
                },
            )
            record["metricIds"].append(metric_id)
            record["metricCategories"].add(metric_category)

    site_rows = []
    for item in site_index.values():
        site_rows.append(
            {
                "siteId": item["siteId"],
                "siteName": item["siteName"],
                "metricIds": sorted(set(item["metricIds"])),
                "metricCategories": sorted(item["metricCategories"]),
                "runtimeLinked": False,
            }
        )
    system_rows = []
    for item in system_index.values():
        system_rows.append(
            {
                "systemId": item["systemId"],
                "systemName": item["systemName"],
                "metricIds": sorted(set(item["metricIds"])),
                "metricCategories": sorted(item["metricCategories"]),
                "runtimeLinked": False,
            }
        )

    return {
        "associationMode": "local-skeleton-association-detail",
        "associationSummary": {
            "siteAssociationCount": len(site_rows),
            "systemAssociationCount": len(system_rows),
            "runtimeLinkedAssociations": 0,
            "assetRuntimeIntegrated": False,
        },
        "siteAssociations": site_rows,
        "systemAssociations": system_rows,
        "runtimeLinked": False,
        "certified": False,
        "greenMarkCertified": False,
        "griCertified": False,
        "isoCertified": False,
        "limitations": [
            "No Assets runtime integration.",
            "No DB-backed site/system mapping.",
            "No real meter mapping.",
        ],
    }


def get_data_quality_summary() -> Dict[str, Any]:
    rows = _normalized_metrics()
    counts = {"estimated": 0, "manual": 0, "measured": 0, "unknown": 0}
    for row in rows:
        key = str(row.get("dataQuality", "")).strip().lower()
        if key in counts:
            counts[key] += 1
        else:
            counts["unknown"] += 1
    return {
        "qualityMode": "local-skeleton-quality",
        "totalMetrics": len(rows),
        "qualityCounts": counts,
        "runtimeLinked": False,
        "certified": False,
        "greenMarkCertified": False,
        "griCertified": False,
        "isoCertified": False,
        "limitations": [
            "No data quality governance workflow.",
            "No runtime data source validation.",
            "No DB-backed quality audit trail.",
        ],
    }


def get_trend_placeholder() -> Dict[str, Any]:
    return {
        "trendMode": "local-skeleton-trend",
        "periods": ["current-month"],
        "trendCalculated": False,
        "periodComparisonReady": False,
        "series": [],
        "runtimeLinked": False,
        "limitations": [
            "No historical ESG store.",
            "No meter integration.",
            "No scheduled collection.",
        ],
        "certified": False,
        "greenMarkCertified": False,
        "griCertified": False,
        "isoCertified": False,
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

