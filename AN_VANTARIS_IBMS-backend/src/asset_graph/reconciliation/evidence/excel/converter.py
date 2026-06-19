"""Convert validated Excel rows into evidence package JSON."""
from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from src.asset_graph.compatibility.constants import MAPPING_VERSION
from src.asset_graph.reconciliation.evidence.runner import FORMAT_NAME, FORMAT_POLICY, FORMAT_VERSION

from .constants import (
    ASSESSMENT_TYPE,
    DEFAULT_SITES,
    DEFAULT_SOURCE_NAMESPACE,
    DEFAULT_SOURCE_SYSTEM,
    DEFAULT_TENANT,
    DEVICE_CONTROL_COLUMNS,
    FIELD_CONTROL_COLUMNS,
)
from .errors import ExcelIntakeError


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _parse_location(value: Any) -> Any:
    text = _clean(value)
    if not text:
        return None
    if text.startswith("{"):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ExcelIntakeError("INVALID_LOCATION_REFERENCE", "LocationReference must be valid JSON") from exc
        if not isinstance(parsed, dict):
            raise ExcelIntakeError("INVALID_LOCATION_REFERENCE", "LocationReference must be a JSON object")
        return parsed
    return {"zoneCode": text}


def _device_record(row: Mapping[str, Any]) -> dict[str, Any]:
    record: dict[str, Any] = {}
    source_id = _clean(row.get("SourceID"))
    if source_id:
        record["sourceId"] = source_id
    tenant = _clean(row.get("TenantID")) or DEFAULT_TENANT
    site = _clean(row.get("SiteID")) or DEFAULT_SITES[0]
    record["sourceNamespace"] = _clean(row.get("SourceNamespace")) or DEFAULT_SOURCE_NAMESPACE
    record["tenantId"] = tenant
    record["siteId"] = site
    name = _clean(row.get("DeviceName"))
    if name:
        record["name"] = name
    description = _clean(row.get("Description"))
    if description:
        record["description"] = description
    device_type = _clean(row.get("DeviceType"))
    if device_type:
        record["deviceType"] = device_type
    manufacturer = _clean(row.get("Manufacturer"))
    if manufacturer:
        record["manufacturer"] = manufacturer
    model = _clean(row.get("Model"))
    if model:
        record["model"] = model
    serial = _clean(row.get("SerialNumber"))
    if serial:
        record["serialNumber"] = serial
    lifecycle = _clean(row.get("LifecycleStatus"))
    if lifecycle:
        record["lifecycleStatus"] = lifecycle
    operational = _clean(row.get("OperationalStatus"))
    if operational:
        record["operationalStatus"] = operational
    tag = _clean(row.get("SourceTagName"))
    if tag:
        record["sourceTagName"] = tag
        record["code"] = tag
    location = _parse_location(row.get("LocationReference"))
    if location is not None:
        record["locationReference"] = location
    created = _clean(row.get("CreatedAt"))
    if created:
        record["createdAt"] = created
    updated = _clean(row.get("UpdatedAt"))
    if updated:
        record["updatedAt"] = updated
    metadata: dict[str, Any] = {"synthetic": True, "source": "excel-intake"}
    classification = _clean(row.get("MetadataClassification"))
    if classification:
        metadata["classification"] = classification
    scenario = _clean(row.get("Scenario"))
    if scenario:
        metadata["scenario"] = scenario
    scenario_class = _clean(row.get("ScenarioClass"))
    if scenario_class:
        metadata["scenarioClass"] = scenario_class
    row_id = _clean(row.get("RowID"))
    if row_id:
        metadata["rowId"] = row_id
    record["approvedMetadata"] = metadata
    return record


def _field_record(row: Mapping[str, Any]) -> dict[str, Any]:
    record: dict[str, Any] = {
        "sourceId": _clean(row.get("SourceID")),
        "deviceSourceId": _clean(row.get("DeviceSourceID")),
        "sourceNamespace": _clean(row.get("SourceNamespace")) or f"{DEFAULT_SOURCE_NAMESPACE}.standard-fields",
        "name": _clean(row.get("FieldName")),
        "displayName": _clean(row.get("DisplayName")) or _clean(row.get("FieldName")),
        "fieldType": _clean(row.get("FieldType")) or "string",
        "dataType": _clean(row.get("DataType")) or "STRING",
        "accessMode": _clean(row.get("AccessMode")) or "READ_ONLY",
        "lifecycleStatus": _clean(row.get("LifecycleStatus")) or "ACTIVE",
    }
    unit = row.get("Unit")
    if unit is not None and _clean(unit) != "":
        record["unit"] = _clean(unit)
    elif "Unit" in row:
        record["unit"] = ""
    tag = _clean(row.get("SourceTagName"))
    if tag:
        record["sourceTagName"] = tag
    metadata: dict[str, Any] = {"synthetic": True, "source": "excel-intake"}
    classification = _clean(row.get("ApprovedMetadata"))
    if classification:
        metadata["classification"] = classification
    scenario = _clean(row.get("Scenario"))
    if scenario:
        metadata["scenario"] = scenario
    scenario_class = _clean(row.get("ScenarioClass"))
    if scenario_class:
        metadata["scenarioClass"] = scenario_class
    row_id = _clean(row.get("RowID"))
    if row_id:
        metadata["rowId"] = row_id
    record["approvedMetadata"] = metadata
    return record


def _declared_allowed_sites(device_rows: Sequence[Mapping[str, Any]]) -> list[str]:
    declared = sorted({
        _clean(row.get("SiteID"))
        for row in device_rows
        if _clean(row.get("SiteID")) in DEFAULT_SITES
    })
    return declared if declared else list(DEFAULT_SITES)


def convert_workbook_rows(
    device_rows: Sequence[Mapping[str, Any]],
    field_rows: Sequence[Mapping[str, Any]],
    *,
    tenant_id: str | None = None,
    source_system_id: str | None = None,
) -> dict[str, Any]:
    tenant = tenant_id or DEFAULT_TENANT
    source_system = source_system_id or DEFAULT_SOURCE_SYSTEM
    devices = [_device_record(row) for row in device_rows]
    fields = [_field_record(row) for row in field_rows]
    devices.sort(key=lambda item: str(item.get("sourceId", "")))
    fields.sort(key=lambda item: (str(item.get("deviceSourceId", "")), str(item.get("sourceId", ""))))
    namespaces = sorted({str(row.get("SourceNamespace", "")).strip() for row in device_rows if _clean(row.get("SourceNamespace"))})
    allowed_sites = _declared_allowed_sites(device_rows)
    return {
        "formatName": FORMAT_NAME,
        "formatVersion": FORMAT_VERSION,
        "exportPolicy": FORMAT_POLICY,
        "assessmentType": ASSESSMENT_TYPE,
        "tenantContext": {
            "tenantId": tenant,
            "synthetic": True,
        },
        "siteContext": {
            "mode": "MULTI_SITE_DECLARED",
            "primarySiteId": DEFAULT_SITES[0],
            "allowedSiteIds": allowed_sites,
            "synthetic": True,
        },
        "sourceSystemContext": {
            "sourceSystemId": source_system,
            "sourceNamespace": namespaces[0] if namespaces else DEFAULT_SOURCE_NAMESPACE,
            "intakeSource": "SYNTHETIC_EXCEL_WORKBOOK",
        },
        "mappingVersion": MAPPING_VERSION,
        "devices": devices,
        "standardFields": fields,
        "declaredRedactions": [
            "no-real-customer-data",
            "no-credentials",
            "no-telemetry-values",
            "no-personal-information",
            "synthetic-representative-excel-intake-only",
        ],
        "sourceSummary": {
            "recordCount": len(devices) + len(fields),
            "deviceCount": len(devices),
            "standardFieldCount": len(fields),
            "notes": "Synthetic representative Excel intake package only. Not real customer evidence.",
        },
    }


def control_columns_for_sheet(sheet: str) -> frozenset[str]:
    if sheet == "Devices":
        return DEVICE_CONTROL_COLUMNS
    if sheet == "StandardFields":
        return FIELD_CONTROL_COLUMNS
    return frozenset()
