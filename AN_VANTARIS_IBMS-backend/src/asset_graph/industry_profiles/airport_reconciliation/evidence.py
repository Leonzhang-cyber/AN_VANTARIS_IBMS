"""Input artifact verification for airport asset reconciliation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .constants import (
    CLASSIFICATION_AUTHORITY,
    COMPATIBLE_CLASSIFICATION_READINESS,
    COMPATIBLE_INTAKE_READINESS,
    COMPATIBLE_SPATIAL_READINESS,
    COVERAGE_AUTHORITY,
    FORBIDDEN_READINESS,
    INTAKE_AUTHORITY,
    SPATIAL_AUTHORITY,
)
from .errors import AirportReconciliationProfileError


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise AirportReconciliationProfileError("ARTIFACT_NOT_FOUND", f"artifact not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_input_bundle(
    *,
    intake: Mapping[str, Any],
    spatial_result: Mapping[str, Any],
    spatial_bindings: list[Mapping[str, Any]],
    system_classification: Mapping[str, Any],
    device_type_classification: Mapping[str, Any],
    classification_bindings: list[Mapping[str, Any]],
    classification_reviews: list[Mapping[str, Any]],
    classification_summary: Mapping[str, Any],
    coverage_analysis: Mapping[str, Any],
    context_workbook_digest: str | None = None,
) -> dict[str, Any]:
    if str(intake.get("authority", "")) != INTAKE_AUTHORITY:
        raise AirportReconciliationProfileError("INTAKE_AUTHORITY_MISMATCH", "intake authority mismatch")
    if str(intake.get("evidenceVersion", "")) != "1.0.0":
        raise AirportReconciliationProfileError("INTAKE_VERSION_MISMATCH", "intake version mismatch")
    intake_readiness = str(intake.get("readinessSummary", {}).get("outcome", ""))
    if intake_readiness in FORBIDDEN_READINESS or intake_readiness not in COMPATIBLE_INTAKE_READINESS:
        raise AirportReconciliationProfileError("INTAKE_READINESS_INCOMPATIBLE", "intake readiness incompatible")

    workbook_digest = str(intake.get("sourceWorkbook", {}).get("sha256", ""))
    if context_workbook_digest and workbook_digest != context_workbook_digest:
        raise AirportReconciliationProfileError("WORKBOOK_DIGEST_MISMATCH", "workbook digest mismatch")

    if str(spatial_result.get("authority", "")) != SPATIAL_AUTHORITY:
        raise AirportReconciliationProfileError("SPATIAL_AUTHORITY_MISMATCH", "spatial authority mismatch")
    spatial_readiness = str(spatial_result.get("readinessOutcome", ""))
    if spatial_readiness in FORBIDDEN_READINESS or spatial_readiness not in COMPATIBLE_SPATIAL_READINESS:
        raise AirportReconciliationProfileError("SPATIAL_READINESS_INCOMPATIBLE", "spatial readiness incompatible")

    spatial_intake_digest = str(spatial_result.get("intakeEvidence", {}).get("resultDigest", ""))
    intake_digest = str(intake.get("resultDigest", ""))
    if spatial_intake_digest and intake_digest and spatial_intake_digest != intake_digest:
        raise AirportReconciliationProfileError("SPATIAL_INTAKE_DIGEST_MISMATCH", "spatial intake digest mismatch")

    for doc, authority in (
        (system_classification, CLASSIFICATION_AUTHORITY),
        (device_type_classification, CLASSIFICATION_AUTHORITY),
        (classification_summary, CLASSIFICATION_AUTHORITY),
    ):
        if str(doc.get("authority", "")) != authority:
            raise AirportReconciliationProfileError("CLASSIFICATION_AUTHORITY_MISMATCH", "classification authority mismatch")
    class_readiness = str(classification_summary.get("readinessOutcome", ""))
    if class_readiness in FORBIDDEN_READINESS or class_readiness not in COMPATIBLE_CLASSIFICATION_READINESS:
        raise AirportReconciliationProfileError("CLASSIFICATION_READINESS_INCOMPATIBLE", "classification readiness incompatible")

    if str(coverage_analysis.get("authority", "")) != COVERAGE_AUTHORITY:
        raise AirportReconciliationProfileError("COVERAGE_AUTHORITY_MISMATCH", "coverage authority mismatch")

    device_count = len(intake.get("deviceCandidates", []))
    if len(spatial_bindings) != device_count:
        raise AirportReconciliationProfileError("SPATIAL_BINDING_COUNT_MISMATCH", "spatial binding count mismatch")
    if len(classification_bindings) != device_count:
        raise AirportReconciliationProfileError("CLASSIFICATION_BINDING_COUNT_MISMATCH", "classification binding count mismatch")

    coverage = coverage_analysis.get("coverage", {})
    if int(coverage.get("totalDeviceCandidates", -1)) != device_count:
        raise AirportReconciliationProfileError("COVERAGE_COUNT_MISMATCH", "coverage device count mismatch")
    if int(classification_summary.get("deviceCandidateCount", -1)) != device_count:
        raise AirportReconciliationProfileError("SUMMARY_COUNT_MISMATCH", "classification summary count mismatch")

    return {
        "intakeAuthority": INTAKE_AUTHORITY,
        "spatialAuthority": SPATIAL_AUTHORITY,
        "classificationAuthority": CLASSIFICATION_AUTHORITY,
        "coverageAuthority": COVERAGE_AUTHORITY,
        "sourceWorkbookDigest": workbook_digest,
        "intakeResultDigest": intake_digest,
        "spatialResultDigest": str(spatial_result.get("resultDigest", "")),
        "classificationSummaryDigest": str(classification_summary.get("resultDigest", "")),
        "coverageResultDigest": str(coverage_analysis.get("resultDigest", "")),
        "deviceCandidateCount": device_count,
        "intakeReadinessOutcome": intake_readiness,
        "spatialReadinessOutcome": spatial_readiness,
        "classificationReadinessOutcome": class_readiness,
        "coverageMetrics": {
            "evidenceClassifiedDeviceCount": int(coverage.get("evidenceClassifiedDeviceCount", 0)),
            "reconciliationEligibleDeviceCount": int(coverage.get("reconciliationEligibleDeviceCount", 0)),
            "fullyApprovedDeviceCount": int(coverage.get("fullyApprovedDeviceCount", 0)),
            "reviewRequiredDeviceCount": int(coverage.get("reviewRequiredDeviceCount", 0)),
            "unmappedDeviceCount": int(coverage.get("unmappedDeviceCount", 0)),
        },
    }
