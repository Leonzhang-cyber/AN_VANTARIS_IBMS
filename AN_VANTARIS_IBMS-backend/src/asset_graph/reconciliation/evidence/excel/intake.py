"""Synthetic Excel evidence intake orchestration."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Optional

from src.asset_graph.reconciliation.evidence import (
    EvidencePackageError,
    run_device_reconciliation_evidence,
)

from .constants import (
    ASSESSMENT_TYPE,
    AUTHORITY,
    WRITE_CUTOVER_STATUS,
)
from .converter import convert_workbook_rows
from .errors import ExcelIntakeError
from .validator import validate_workbook
from .workbook import ExcelWorkbook


def _base_package_template() -> dict[str, Any]:
    return {
        "formatName": "VANTARIS ONE Legacy Device Reconciliation Evidence Package",
        "formatVersion": "1.0.0",
        "exportPolicy": "SANITIZED_OFFLINE_READ_ONLY",
        "tenantContext": {"tenantId": "SYNTH-TENANT-001"},
        "siteContext": {"siteId": "SYNTH-SITE-001"},
        "sourceSystemContext": {
            "sourceSystemId": "synth-excel-legacy-ibms",
            "sourceNamespace": "legacy.synth.excel.devices.ns1",
        },
        "mappingVersion": "legacy-device-v1",
        "devices": [],
        "standardFields": [],
        "declaredRedactions": ["synthetic-negative-test-only"],
        "sourceSummary": {
            "recordCount": 1,
            "deviceCount": 1,
            "standardFieldCount": 0,
            "notes": "Synthetic rejected sample isolation package.",
        },
    }


def _negative_device_package(field_name: str, sample_value: str) -> dict[str, Any]:
    package = _base_package_template()
    package["devices"] = [
        {
            "sourceId": "SYNTH-REJECT-DEVICE-001",
            "sourceNamespace": "legacy.synth.excel.devices.ns1",
            "tenantId": "SYNTH-TENANT-001",
            "siteId": "SYNTH-SITE-001",
            "name": "Synthetic Rejected Sample Device",
            "code": "SYN-REJECT-001",
            "deviceType": "CONTROLLER",
            "operationalStatus": "AVAILABLE",
            "createdAt": "2026-06-01T00:00:00Z",
            "updatedAt": "2026-06-01T00:00:00Z",
            field_name: sample_value,
            "approvedMetadata": {"synthetic": True},
        }
    ]
    return package


def _negative_field_package(field_name: str, sample_value: str) -> dict[str, Any]:
    package = _base_package_template()
    package["devices"] = [
        {
            "sourceId": "SYNTH-REJECT-DEVICE-001",
            "sourceNamespace": "legacy.synth.excel.devices.ns1",
            "tenantId": "SYNTH-TENANT-001",
            "siteId": "SYNTH-SITE-001",
            "name": "Synthetic Rejected Sample Device",
            "code": "SYN-REJECT-001",
            "deviceType": "CONTROLLER",
            "operationalStatus": "AVAILABLE",
            "createdAt": "2026-06-01T00:00:00Z",
            "updatedAt": "2026-06-01T00:00:00Z",
            "approvedMetadata": {"synthetic": True},
        }
    ]
    package["standardFields"] = [
        {
            "sourceId": "SYNTH-REJECT-FIELD-001",
            "deviceSourceId": "SYNTH-REJECT-DEVICE-001",
            "sourceNamespace": "legacy.synth.excel.standard-fields",
            "name": "safe_placeholder",
            "displayName": "Safe Placeholder",
            "fieldType": "float",
            "dataType": "NUMBER",
            "unit": "Cel",
            "accessMode": "READ_ONLY",
            "lifecycleStatus": "ACTIVE",
            field_name: sample_value,
            "approvedMetadata": {"synthetic": True},
        }
    ]
    package["sourceSummary"]["standardFieldCount"] = 1
    package["sourceSummary"]["recordCount"] = 2
    return package


def validate_rejected_samples(
    rejected_rows: list[Mapping[str, Any]],
    *,
    temp_dir: Path,
) -> list[dict[str, str]]:
    from src.asset_graph.reconciliation.evidence.runner import run_device_reconciliation_evidence as _run

    results: list[dict[str, str]] = []
    temp_dir.mkdir(parents=True, exist_ok=True)
    for index, row in enumerate(rejected_rows, start=1):
        category = str(row.get("Category", "")).strip().upper()
        target = str(row.get("TargetSheet", "Devices")).strip()
        field_name = str(row.get("FieldName", "")).strip()
        sample_value = str(row.get("SampleValue", "")).strip()
        if target == "StandardFields":
            package = _negative_field_package(field_name, sample_value)
        else:
            package = _negative_device_package(field_name, sample_value)
        input_path = temp_dir / f"rejected-sample-{index:02d}.json"
        output_path = temp_dir / f"rejected-sample-{index:02d}-out.json"
        input_path.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        try:
            _run(
                root=temp_dir,
                input_path=input_path,
                output_path=output_path,
                run_id=f"REJECTED-SAMPLE-{index:03d}",
            )
            status = "UNEXPECTED_ACCEPT"
        except EvidencePackageError:
            status = "REJECTED"
        results.append(
            {
                "category": category,
                "fieldName": field_name,
                "rejectionStatus": status,
                "packagePath": str(input_path),
            }
        )
        if status != "REJECTED":
            raise ExcelIntakeError("REJECTED_SAMPLE_NOT_BLOCKED", f"rejected sample row {index} was not blocked")
    return results


def run_excel_evidence_intake(
    *,
    root: Path,
    input_path: Path,
    json_output: Path,
    report_output: Optional[Path] = None,
    run_id: str,
    rejected_temp_dir: Optional[Path] = None,
    enforce_fixture_profile: bool = True,
    fail_on_blocker: bool = False,
    fail_on_review: bool = False,
) -> dict[str, Any]:
    with ExcelWorkbook.open(input_path) as book:
        profile = validate_workbook(book, enforce_fixture_profile=enforce_fixture_profile)
        device_rows = book.rows("Devices")
        field_rows = book.rows("StandardFields")
        rejected_rows = book.rows("RejectedSamples")
    package = convert_workbook_rows(device_rows, field_rows)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(package, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    rejected_results: list[dict[str, str]] = []
    if rejected_rows:
        rejected_results = validate_rejected_samples(
            rejected_rows,
            temp_dir=rejected_temp_dir or json_output.parent / "rejected-samples",
        )
    report_path = report_output or json_output.with_name(json_output.stem + "-report.json")
    report = run_device_reconciliation_evidence(
        root=root,
        input_path=json_output,
        output_path=report_path,
        run_id=run_id,
        fail_on_blocker=fail_on_blocker,
        fail_on_review=fail_on_review,
    )
    cutover = report.get("cutoverDecision", WRITE_CUTOVER_STATUS)
    if cutover == "READY_FOR_WRITE_CUTOVER":
        cutover = WRITE_CUTOVER_STATUS
    return {
        "authority": AUTHORITY,
        "assessmentType": ASSESSMENT_TYPE,
        "syntheticAssessment": "PERFORMED",
        "realDataAssessment": "NOT_PERFORMED",
        "writeCutoverStatus": WRITE_CUTOVER_STATUS,
        "workbookProfile": profile,
        "rejectedSampleResults": rejected_results,
        "evidencePackagePath": str(json_output),
        "reconciliationReportPath": str(report_path),
        "reconciliationSummary": report.get("reconciliationSummary"),
        "projectionSummary": report.get("projectionSummary"),
        "blockers": report.get("blockers"),
        "reviews": report.get("reviews"),
        "cutoverDecision": cutover,
        "resultDigest": report.get("resultDigest"),
    }


def compare_deterministic_outputs(first: Path, second: Path) -> tuple[bool, str]:
    if not first.is_file() or not second.is_file():
        return False, "MISSING_OUTPUT"
    if first.read_bytes() == second.read_bytes():
        return True, "MATCH"
    return False, "MISMATCH"
