"""Evidence verification for airport classification profile."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .constants import (
    COMPATIBLE_INTAKE_AUTHORITY,
    COMPATIBLE_INTAKE_EVIDENCE_VERSION,
    COMPATIBLE_INTAKE_EXECUTION_MODE,
    COMPATIBLE_INTAKE_READINESS,
    COMPATIBLE_SPATIAL_AUTHORITY,
    COMPATIBLE_SPATIAL_READINESS,
    FORBIDDEN_READINESS,
)
from .errors import AirportClassificationProfileError


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise AirportClassificationProfileError("EVIDENCE_NOT_FOUND", f"evidence file was not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_intake_evidence(
    evidence: Mapping[str, Any],
    *,
    expected_workbook_digest: str | None = None,
    expected_result_digest: str | None = None,
) -> dict[str, str]:
    authority = str(evidence.get("authority", ""))
    if authority != COMPATIBLE_INTAKE_AUTHORITY:
        raise AirportClassificationProfileError("INTAKE_AUTHORITY_MISMATCH", "intake evidence authority mismatch")
    version = str(evidence.get("evidenceVersion", ""))
    if version != COMPATIBLE_INTAKE_EVIDENCE_VERSION:
        raise AirportClassificationProfileError("INTAKE_VERSION_MISMATCH", "intake evidence version mismatch")
    if str(evidence.get("executionMode", "")) != COMPATIBLE_INTAKE_EXECUTION_MODE:
        raise AirportClassificationProfileError("INTAKE_EXECUTION_MODE_MISMATCH", "intake execution mode mismatch")
    readiness = str(evidence.get("readinessSummary", {}).get("outcome", ""))
    if readiness in FORBIDDEN_READINESS:
        raise AirportClassificationProfileError("INTAKE_READINESS_FORBIDDEN", "intake readiness outcome is forbidden")
    if readiness not in COMPATIBLE_INTAKE_READINESS:
        raise AirportClassificationProfileError("INTAKE_READINESS_INCOMPATIBLE", "intake readiness incompatible")

    workbook = evidence.get("sourceWorkbook", {})
    digest = str(workbook.get("sha256", ""))
    if expected_workbook_digest and digest != expected_workbook_digest:
        raise AirportClassificationProfileError("INTAKE_WORKBOOK_DIGEST_MISMATCH", "source workbook digest mismatch")
    result_digest = str(evidence.get("resultDigest", ""))
    if expected_result_digest and result_digest != expected_result_digest:
        raise AirportClassificationProfileError("INTAKE_RESULT_DIGEST_MISMATCH", "intake result digest mismatch")

    return {
        "authority": authority,
        "evidenceVersion": version,
        "executionMode": str(evidence.get("executionMode", "")),
        "readinessOutcome": readiness,
        "sourceWorkbookDigest": digest,
        "resultDigest": result_digest,
    }


def verify_spatial_result(
    spatial: Mapping[str, Any],
    *,
    expected_result_digest: str | None = None,
    expected_intake_result_digest: str | None = None,
) -> dict[str, str]:
    authority = str(spatial.get("authority", ""))
    if authority != COMPATIBLE_SPATIAL_AUTHORITY:
        raise AirportClassificationProfileError("SPATIAL_AUTHORITY_MISMATCH", "spatial result authority mismatch")
    readiness = str(spatial.get("readinessOutcome", ""))
    if readiness in FORBIDDEN_READINESS:
        raise AirportClassificationProfileError("SPATIAL_READINESS_FORBIDDEN", "spatial readiness outcome is forbidden")
    if readiness not in COMPATIBLE_SPATIAL_READINESS:
        raise AirportClassificationProfileError("SPATIAL_READINESS_INCOMPATIBLE", "spatial readiness incompatible")

    result_digest = str(spatial.get("resultDigest", ""))
    if expected_result_digest and result_digest != expected_result_digest:
        raise AirportClassificationProfileError("SPATIAL_RESULT_DIGEST_MISMATCH", "spatial result digest mismatch")

    intake_meta = spatial.get("intakeEvidence", {})
    intake_digest = str(intake_meta.get("resultDigest", ""))
    if expected_intake_result_digest and intake_digest != expected_intake_result_digest:
        raise AirportClassificationProfileError(
            "SPATIAL_INTAKE_DIGEST_MISMATCH",
            "spatial intake evidence digest mismatch",
        )

    return {
        "authority": authority,
        "readinessOutcome": readiness,
        "resultDigest": result_digest,
        "intakeResultDigest": intake_digest,
    }


def load_spatial_bindings(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise AirportClassificationProfileError("SPATIAL_BINDINGS_NOT_FOUND", "spatial bindings file was not found")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    bindings = payload.get("bindings")
    if isinstance(bindings, list):
        return bindings
    raise AirportClassificationProfileError("SPATIAL_BINDINGS_INVALID", "spatial bindings payload invalid")
