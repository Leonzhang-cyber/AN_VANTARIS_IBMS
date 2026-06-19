"""Intake evidence verification for airport spatial mapping."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .constants import (
    COMPATIBLE_INTAKE_AUTHORITY,
    COMPATIBLE_INTAKE_EVIDENCE_VERSION,
    COMPATIBLE_INTAKE_EXECUTION_MODE,
    COMPATIBLE_INTAKE_READINESS,
    FORBIDDEN_READINESS,
)
from .errors import AirportSpatialProfileError


def load_intake_evidence(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise AirportSpatialProfileError("INTAKE_EVIDENCE_NOT_FOUND", "intake evidence file was not found")
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def verify_intake_evidence(
    evidence: Mapping[str, Any],
    *,
    expected_workbook_digest: str | None = None,
    expected_result_digest: str | None = None,
) -> dict[str, str]:
    authority = str(evidence.get("authority", ""))
    if authority != COMPATIBLE_INTAKE_AUTHORITY:
        raise AirportSpatialProfileError("INTAKE_AUTHORITY_MISMATCH", "intake evidence authority mismatch")
    version = str(evidence.get("evidenceVersion", ""))
    if version != COMPATIBLE_INTAKE_EVIDENCE_VERSION:
        raise AirportSpatialProfileError("INTAKE_VERSION_MISMATCH", "intake evidence version mismatch")
    if str(evidence.get("executionMode", "")) != COMPATIBLE_INTAKE_EXECUTION_MODE:
        raise AirportSpatialProfileError("INTAKE_EXECUTION_MODE_MISMATCH", "intake execution mode mismatch")
    readiness = str(evidence.get("readinessSummary", {}).get("outcome", ""))
    if readiness in FORBIDDEN_READINESS:
        raise AirportSpatialProfileError("INTAKE_READINESS_FORBIDDEN", "intake readiness outcome is forbidden")
    if readiness not in COMPATIBLE_INTAKE_READINESS:
        raise AirportSpatialProfileError("INTAKE_READINESS_INCOMPATIBLE", "intake readiness incompatible with spatial mapping")

    workbook = evidence.get("sourceWorkbook", {})
    digest = str(workbook.get("sha256", ""))
    if expected_workbook_digest and digest != expected_workbook_digest:
        raise AirportSpatialProfileError("INTAKE_WORKBOOK_DIGEST_MISMATCH", "source workbook digest mismatch")
    result_digest = str(evidence.get("resultDigest", ""))
    if expected_result_digest and result_digest != expected_result_digest:
        raise AirportSpatialProfileError("INTAKE_RESULT_DIGEST_MISMATCH", "intake result digest mismatch")

    return {
        "authority": authority,
        "evidenceVersion": version,
        "executionMode": str(evidence.get("executionMode", "")),
        "readinessOutcome": readiness,
        "sourceWorkbookDigest": digest,
        "resultDigest": result_digest,
    }
