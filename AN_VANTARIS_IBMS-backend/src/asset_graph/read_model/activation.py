"""Execution activation and artifact verification."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .errors import ReadModelError

ACTIVATION_STATES = frozenset({"VALIDATION_COMPLETE", "VALIDATION_COMPLETE_WITH_REVIEWS"})
REJECTED_STATES = frozenset({"EXECUTION_BLOCKED", "VALIDATION_FAILED", "ROLLED_BACK"})
WRITE_CUTOVER_STATUS = "NOT_READY_FOR_WRITE_CUTOVER"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_activation(
    execution_result: Mapping[str, Any],
    artifact_manifest: Mapping[str, Any],
    output_dir: Path,
) -> None:
    state = str(execution_result.get("executionState", ""))
    if state in REJECTED_STATES:
        raise ReadModelError(f"execution state {state} cannot activate read model")
    if state not in ACTIVATION_STATES:
        raise ReadModelError(f"execution state {state} is not activation-eligible")
    if execution_result.get("writeCutoverStatus") != WRITE_CUTOVER_STATUS:
        raise ReadModelError("write cutover status must remain NOT_READY_FOR_WRITE_CUTOVER")
    if not execution_result.get("resultDigest"):
        raise ReadModelError("execution result digest is required")
    if not execution_result.get("evidenceDigest"):
        raise ReadModelError("evidence digest is required")
    if not execution_result.get("readinessResultDigest"):
        raise ReadModelError("readiness result digest is required")

    artifacts = artifact_manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ReadModelError("artifact manifest must list generated artifacts")

    manifest_path = output_dir / "artifact-manifest.json"
    if not manifest_path.is_file():
        raise ReadModelError("artifact manifest file missing from output directory")

    for entry in artifacts:
        relative = str(entry.get("relativePath", ""))
        if relative in {"execution-result.json", "artifact-manifest.json"}:
            continue
        expected = str(entry.get("sha256", ""))
        path = output_dir / relative
        if not path.is_file():
            raise ReadModelError(f"missing artifact: {relative}")
        if _sha256_file(path) != expected:
            raise ReadModelError(f"artifact digest mismatch: {relative}")

    reconciliation_path = output_dir / "reconciliation-report.json"
    readiness_path = output_dir / "readiness-assessment.json"
    if not reconciliation_path.is_file() or not readiness_path.is_file():
        raise ReadModelError("required validation artifacts missing")

    reconciliation = json.loads(reconciliation_path.read_text(encoding="utf-8"))
    readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
    if reconciliation.get("resultDigest") != execution_result.get("evidenceDigest"):
        raise ReadModelError("evidence digest mismatch against reconciliation report")
    if readiness.get("resultDigest") != execution_result.get("readinessResultDigest"):
        raise ReadModelError("readiness digest mismatch against readiness assessment")
