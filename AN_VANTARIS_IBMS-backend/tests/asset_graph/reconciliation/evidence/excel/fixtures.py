#!/usr/bin/env python3
"""Create the representative synthetic Excel workbook fixture."""
from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

TENANT = "SYNTH-TENANT-001"
SITES = ("SYNTH-SITE-001", "SYNTH-SITE-002", "SYNTH-SITE-003")
NS = (
    "legacy.synth.excel.devices.ns1",
    "legacy.synth.excel.devices.ns2",
    "legacy.synth.excel.devices.ns3",
)
TS = "2026-06-01T00:00:00Z"
POINTS = (
    "supply_temperature", "return_temperature", "fan_speed", "damper_position",
    "coil_valve", "humidity", "pressure", "flow_rate", "power_draw", "runtime_hours",
)


def _device_headers() -> list[str]:
    return [
        "RowID", "ScenarioClass", "Scenario", "TenantID", "SiteID", "SourceNamespace",
        "SourceID", "DeviceName", "Description", "DeviceType", "Manufacturer", "Model",
        "SerialNumber", "LifecycleStatus", "OperationalStatus", "SourceTagName",
        "LocationReference", "CreatedAt", "UpdatedAt", "MetadataClassification",
        "ReviewNotes", "BlockerNotes",
    ]


def _field_headers() -> list[str]:
    return [
        "RowID", "ScenarioClass", "Scenario", "TenantID", "SiteID", "SourceNamespace",
        "SourceID", "DeviceSourceID", "FieldName", "DisplayName", "FieldType", "DataType",
        "Unit", "AccessMode", "LifecycleStatus", "SourceTagName", "ApprovedMetadata",
        "ReviewNotes", "BlockerNotes",
    ]


def _append_sheet(wb: Workbook, title: str, headers: list[str], rows: list[list]) -> None:
    ws = wb.create_sheet(title)
    ws.append(headers)
    for row in rows:
        ws.append(row)


def build_devices() -> list[list]:
    rows: list[list] = []
    for idx in range(48):
        source_id = f"SYNTH-DEV-CLEAN-{idx + 1:03d}"
        device_type = "CONTROLLER" if idx % 2 == 0 else "SENSOR"
        rows.append([
            f"D-C-{idx + 1:03d}", "CLEAN", "VALID_DEVICE", TENANT, SITES[idx % 3], NS[idx % 3],
            source_id, f"Synthetic {device_type.title()} {idx + 1:03d}",
            f"Synthetic {device_type.lower()} for excel intake.", device_type,
            "SynthCorp", f"SIM-{100 + idx % 4}", f"SYNTH-SN-{idx + 1:04d}",
            "ACTIVE", "AVAILABLE", f"SYN-{idx + 1:03d}",
            f'{{"zoneCode":"ZONE-{idx + 1:03d}"}}', TS, TS, "operational", "", "",
        ])
    review_specs = (
        ("SYNTH-DEV-REV-LIFE", "UNKNOWN_STATUS", "UNKNOWN", "ACTIVE", '{"zoneCode":"ZONE-REV-01"}'),
        ("SYNTH-DEV-REV-PARENT", "UNRESOLVED_PARENT", "AVAILABLE", "ACTIVE", '{"parentSourceId":"SYNTH-PARENT-UNRESOLVED"}'),
        ("SYNTH-DEV-REV-STAT", "UNKNOWN_OPERATIONAL", "AVAILABLE", "UNKNOWN", '{"zoneCode":"ZONE-REV-03"}'),
        ("SYNTH-DEV-REV-UNIT", "MISSING_UNIT", "AVAILABLE", "ACTIVE", '{"zoneCode":"ZONE-REV-04"}'),
        ("SYNTH-DEV-REV-JSON", "AMBIGUOUS_JSON", "AVAILABLE", "ACTIVE", '{"zoneCode":"ZONE-REV-05"}'),
        ("SYNTH-DEV-REV-ACCESS", "REVIEW_ACCESS", "AVAILABLE", "ACTIVE", '{"zoneCode":"ZONE-REV-06"}'),
    )
    for ridx, (source_id, scenario, op, life, loc) in enumerate(review_specs):
        rows.append([
            f"D-R-{ridx + 1:03d}", "REVIEW", scenario, TENANT, SITES[ridx % 3], NS[ridx % 3],
            source_id, f"Synthetic Review Device {ridx + 1:03d}", "Synthetic review device.",
            "CONTROLLER", "SynthCorp", "SIM-REV", f"SYNTH-SN-REV-{ridx + 1:02d}",
            life, op, f"SYN-REV-{ridx + 1:03d}", loc, TS, TS, "operational", scenario, "",
        ])
    blockers = [
        ["D-B-001", "BLOCKER", "DUPLICATE_IDENTITY_A", TENANT, SITES[0], NS[0], "SYNTH-DEV-DUP-001",
         "Synthetic Duplicate A", "Duplicate identity A.", "CONTROLLER", "SynthCorp", "SIM-BLK",
         "SYNTH-SN-DUP-A", "ACTIVE", "AVAILABLE", "SYN-BLK-DUP-A", '{"zoneCode":"ZONE-BLK-01"}', TS, TS, "blocker", "", "duplicate"],
        ["D-B-002", "BLOCKER", "DUPLICATE_IDENTITY_B", TENANT, SITES[0], NS[0], "SYNTH-DEV-DUP-001",
         "Synthetic Duplicate B", "Duplicate identity B.", "CONTROLLER", "SynthCorp", "SIM-BLK",
         "SYNTH-SN-DUP-B", "ACTIVE", "AVAILABLE", "SYN-BLK-DUP-B", '{"zoneCode":"ZONE-BLK-02"}', TS, TS, "blocker", "", "duplicate"],
        ["D-B-003", "BLOCKER", "MISSING_SOURCE_ID", TENANT, SITES[0], NS[0], "",
         "Synthetic Missing Source Id", "Missing stable source id.", "CONTROLLER", "SynthCorp", "SIM-BLK",
         "SYNTH-SN-NOSRC", "ACTIVE", "AVAILABLE", "SYN-BLK-NOSRC", '{"zoneCode":"ZONE-BLK-03"}', TS, TS, "blocker", "", "missing-source-id"],
        ["D-B-004", "BLOCKER", "TENANT_MISMATCH", "SYNTH-TENANT-MISMATCH", SITES[0], NS[0], "SYNTH-DEV-BLK-TENANT",
         "Synthetic Tenant Mismatch", "Tenant mismatch.", "CONTROLLER", "SynthCorp", "SIM-BLK",
         "SYNTH-SN-TEN", "ACTIVE", "AVAILABLE", "SYN-BLK-TENANT", '{"zoneCode":"ZONE-BLK-04"}', TS, TS, "blocker", "", "tenant"],
        ["D-B-005", "BLOCKER", "SITE_MISMATCH", TENANT, "SYNTH-SITE-MISMATCH", NS[0], "SYNTH-DEV-BLK-SITE",
         "Synthetic Site Mismatch", "Site mismatch.", "CONTROLLER", "SynthCorp", "SIM-BLK",
         "SYNTH-SN-SITE", "ACTIVE", "AVAILABLE", "SYN-BLK-SITE", '{"zoneCode":"ZONE-BLK-05"}', TS, TS, "blocker", "", "site"],
        ["D-B-006", "BLOCKER", "TAG_COLLISION", TENANT, SITES[0], NS[0], "SYNTH-DEV-BLK-TAG-A",
         "Synthetic Tag Collision", "Shared source tag.", "CONTROLLER", "SynthCorp", "SIM-BLK",
         "SYNTH-SN-TAG", "ACTIVE", "AVAILABLE", "SYN-TAG-COLLISION", '{"zoneCode":"ZONE-BLK-06"}', TS, TS, "blocker", "", "tag-collision"],
    ]
    rows.extend(blockers)
    return rows


def build_fields(devices: list[list]) -> list[list]:
    rows: list[list] = []
    clean_devices = [row[6] for row in devices if row[1] == "CLEAN" and row[6]]
    review_devices = [row[6] for row in devices if row[1] == "REVIEW" and row[6]]
    blocker_devices = [row[6] for row in devices if row[1] == "BLOCKER" and row[6]]
    field_idx = 1
    for d_idx, device_id in enumerate(clean_devices):
        for p_idx, pname in enumerate(POINTS):
            rows.append([
                f"F-C-{field_idx:04d}", "CLEAN", "VALID_POINT", TENANT, SITES[d_idx % 3], NS[d_idx % 3],
                f"SYNTH-FLD-CLEAN-{field_idx:04d}", device_id, pname, pname.replace("_", " ").title(),
                "float", "NUMBER", "Cel", "READ_ONLY", "ACTIVE", f"{device_id}:{pname}", "operational", "", "",
            ])
            field_idx += 1
    review_field_specs = (
        ("ambient_temperature", "float", "NUMBER", "", "READ_ONLY"),
        ("raw_json_payload", "json", "JSON", "", "READ_ONLY"),
        ("writable_setpoint", "float", "NUMBER", "Cel", "REVIEW_REQUIRED_MODE"),
    )
    for r_idx, device_id in enumerate(review_devices):
        for p_idx, pname in enumerate(POINTS):
            if r_idx == 1 and p_idx == 0:
                pname, ftype, dtype, unit, access = review_field_specs[1]
            elif r_idx == 3 and p_idx == 0:
                pname, ftype, dtype, unit, access = review_field_specs[0]
            elif r_idx == 5 and p_idx == 0:
                pname, ftype, dtype, unit, access = review_field_specs[2]
            else:
                pname = POINTS[p_idx]
                ftype, dtype, unit, access = "float", "NUMBER", "Cel", "READ_ONLY"
            rows.append([
                f"F-R-{field_idx:04d}", "REVIEW", "REVIEW_POINT", TENANT, SITES[r_idx % 3], NS[r_idx % 3],
                f"SYNTH-FLD-REV-{field_idx:04d}", device_id, pname, pname.replace("_", " ").title(),
                ftype, dtype, unit, access, "ACTIVE", f"{device_id}:{pname}", "operational", "review", "",
            ])
            field_idx += 1
    for device_id in blocker_devices[:5]:
        for p_idx in range(10):
            rows.append([
                f"F-B-{field_idx:04d}", "BLOCKER", "BLOCKER_POINT", TENANT, SITES[0], NS[0],
                f"SYNTH-FLD-BLK-{field_idx:04d}", device_id, POINTS[p_idx], POINTS[p_idx].replace("_", " ").title(),
                "float", "NUMBER", "Cel", "READ_ONLY", "ACTIVE", f"{device_id}:{POINTS[p_idx]}", "blocker", "", "blocker",
            ])
            field_idx += 1
    for p_idx in range(10):
        rows.append([
            f"F-B-{field_idx:04d}", "BLOCKER", "ORPHAN_POINT", TENANT, SITES[0], NS[0],
            f"SYNTH-FLD-ORPHAN-{p_idx + 1:02d}", "SYNTH-DEV-NOT-EXISTS", POINTS[p_idx], POINTS[p_idx].replace("_", " ").title(),
            "float", "NUMBER", "Cel", "READ_ONLY", "ACTIVE", f"SYNTH-DEV-NOT-EXISTS:{POINTS[p_idx]}", "blocker", "", "orphan",
        ])
        field_idx += 1
    return rows


def build_rejected_samples() -> list[list]:
    return [
        [1, "CREDENTIAL_FIELD", "Devices", "password", "SYNTHETIC_PASSWORD_SHOULD_BE_REJECTED", "credential rejection test"],
        [2, "TELEMETRY_FIELD", "StandardFields", "current_value", "SYNTHETIC_TELEMETRY_SHOULD_BE_REJECTED", "telemetry rejection test"],
        [3, "PRIVATE_MATERIAL", "Devices", "private_key", "SYNTHETIC_PRIVATE_KEY_SHOULD_BE_REJECTED", "private material rejection test"],
        [4, "CONNECTION_STRING", "Devices", "connection_string", "SYNTHETIC_CONNECTION_STRING_SHOULD_BE_REJECTED", "connection string rejection test"],
        [5, "CREDENTIAL_FIELD", "StandardFields", "api_key", "SYNTHETIC_PASSWORD_SHOULD_BE_REJECTED", "field credential rejection test"],
        [6, "TELEMETRY_FIELD", "Devices", "telemetry", "SYNTHETIC_TELEMETRY_SHOULD_BE_REJECTED", "device telemetry rejection test"],
    ]


def write_workbook(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    wb.remove(wb.active)
    devices = build_devices()
    fields = build_fields(devices)
    assert len(devices) == 60, len(devices)
    assert len(fields) == 600, len(fields)
    _append_sheet(wb, "Summary", ["Key", "Value"], [
        ["AssessmentType", "SYNTHETIC_REPRESENTATIVE_ONLY"],
        ["DeviceRows", len(devices)],
        ["StandardFieldRows", len(fields)],
        ["Sites", len(SITES)],
        ["SourceNamespaces", len(NS)],
    ])
    _append_sheet(wb, "Devices", _device_headers(), devices)
    _append_sheet(wb, "StandardFields", _field_headers(), fields)
    _append_sheet(wb, "ScenarioCatalog", ["ScenarioClass", "Scenario", "Description"], [
        ["CLEAN", "VALID_DEVICE", "Valid synthetic device"],
        ["REVIEW", "UNKNOWN_STATUS", "Unknown operational status review"],
        ["BLOCKER", "DUPLICATE_IDENTITY_A", "Duplicate source identity"],
    ])
    _append_sheet(wb, "RejectedSamples", ["RowID", "Category", "TargetSheet", "FieldName", "SampleValue", "Notes"], build_rejected_samples())
    _append_sheet(wb, "README", ["Section", "Content"], [
        ["Purpose", "Synthetic representative Excel intake fixture only."],
        ["RealData", "No real customer data included."],
    ])
    wb.save(path)


if __name__ == "__main__":
    import sys
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/VANTARIS_ONE_Representative_Synthetic_Device_Dataset.xlsx")
    write_workbook(target)
    print(f"WORKBOOK_WRITTEN={target}")
