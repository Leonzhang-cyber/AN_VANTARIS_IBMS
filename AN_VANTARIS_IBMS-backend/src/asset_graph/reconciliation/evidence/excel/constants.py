"""Frozen constants for synthetic Excel evidence intake."""
from __future__ import annotations

from src.asset_graph.compatibility.constants import MAPPING_VERSION
from src.asset_graph.reconciliation.evidence.runner import (
    FORMAT_NAME,
    FORMAT_POLICY,
    FORMAT_VERSION,
)

AUTHORITY = "ONE-A5-P1-16D"
ASSESSMENT_TYPE = "SYNTHETIC_REPRESENTATIVE_ONLY"
MAX_READ_MIGRATION = "READY_FOR_SYNTHETIC_READ_VALIDATION"
WRITE_CUTOVER_STATUS = "NOT_READY_FOR_WRITE_CUTOVER"

REQUIRED_SHEETS = (
    "Summary",
    "Devices",
    "StandardFields",
    "ScenarioCatalog",
    "RejectedSamples",
    "README",
)
BUSINESS_SHEETS = ("Devices", "StandardFields")
METADATA_SHEETS = ("Summary", "ScenarioCatalog", "README")

DEVICES_REQUIRED_COLUMNS = (
    "RowID",
    "ScenarioClass",
    "Scenario",
    "TenantID",
    "SiteID",
    "SourceNamespace",
    "SourceID",
    "DeviceName",
    "Description",
    "DeviceType",
    "Manufacturer",
    "Model",
    "SerialNumber",
    "LifecycleStatus",
    "OperationalStatus",
    "SourceTagName",
    "LocationReference",
    "CreatedAt",
    "UpdatedAt",
    "MetadataClassification",
    "ReviewNotes",
    "BlockerNotes",
)

STANDARD_FIELDS_REQUIRED_COLUMNS = (
    "RowID",
    "ScenarioClass",
    "Scenario",
    "TenantID",
    "SiteID",
    "SourceNamespace",
    "SourceID",
    "DeviceSourceID",
    "FieldName",
    "DisplayName",
    "FieldType",
    "DataType",
    "Unit",
    "AccessMode",
    "LifecycleStatus",
    "SourceTagName",
    "ApprovedMetadata",
    "ReviewNotes",
    "BlockerNotes",
)

REJECTED_SAMPLES_REQUIRED_COLUMNS = (
    "RowID",
    "Category",
    "TargetSheet",
    "FieldName",
    "SampleValue",
    "Notes",
)

DEVICE_CONTROL_COLUMNS = frozenset({"RowID", "ScenarioClass", "Scenario", "ReviewNotes", "BlockerNotes"})
FIELD_CONTROL_COLUMNS = frozenset({"RowID", "ScenarioClass", "Scenario", "ReviewNotes", "BlockerNotes"})

SCENARIO_CLASSES = frozenset({"CLEAN", "REVIEW", "BLOCKER"})
REJECTED_CATEGORIES = frozenset({
    "CREDENTIAL_FIELD",
    "PRIVATE_MATERIAL",
    "CONNECTION_STRING",
    "TELEMETRY_FIELD",
})

EXPECTED_PROFILE = {
    "device_rows": 60,
    "standard_field_rows": 600,
    "device_clean": 48,
    "device_review": 6,
    "device_blocker": 6,
    "field_clean": 480,
    "field_review": 60,
    "field_blocker": 60,
    "sites": 3,
    "namespaces_min": 2,
    "namespaces_max": 3,
    "rejected_samples": 6,
    "device_rows_min": 50,
    "device_rows_max": 100,
    "field_rows_min": 500,
    "field_rows_max": 1000,
}

DEFAULT_TENANT = "SYNTH-TENANT-001"
DEFAULT_SITES = ("SYNTH-SITE-001", "SYNTH-SITE-002", "SYNTH-SITE-003")
DEFAULT_SOURCE_SYSTEM = "synth-excel-legacy-ibms"
DEFAULT_SOURCE_NAMESPACE = "legacy.synth.excel.devices.ns1"

PROHIBITED_VALUE_MARKERS = (
    "SYNTHETIC_PASSWORD_SHOULD_BE_REJECTED",
    "SYNTHETIC_TELEMETRY_SHOULD_BE_REJECTED",
    "SYNTHETIC_PRIVATE_KEY_SHOULD_BE_REJECTED",
    "SYNTHETIC_CONNECTION_STRING_SHOULD_BE_REJECTED",
)
