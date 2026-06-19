"""Input verification for airport review projection."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .constants import RECONCILIATION_AUTHORITY, RECONCILIATION_PROFILE_VERSION
from .errors import AirportReviewProjectionError


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise AirportReviewProjectionError("ARTIFACT_NOT_FOUND", f"artifact not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_reconciliation_bundle(
    *,
    reconciliation_dir: Path,
    expected_workbook_digest: str | None = None,
    expected_reconciliation_digest: str | None = None,
) -> dict[str, Any]:
    reconciliation_dir = reconciliation_dir.resolve()
    manifest_path = reconciliation_dir / "artifact-manifest.json"
    manifest = load_json(manifest_path)
    if str(manifest.get("authority", "")) != RECONCILIATION_AUTHORITY:
        raise AirportReviewProjectionError("RECONCILIATION_AUTHORITY_MISMATCH", "reconciliation authority mismatch")

    artifact_paths = {
        "reconciliationResult": reconciliation_dir / "airport-asset-reconciliation-result.json",
        "canonicalProposals": reconciliation_dir / "airport-canonical-proposal-candidates.json",
        "duplicateGroups": reconciliation_dir / "airport-duplicate-reconciliation-groups.json",
        "aliasPackage": reconciliation_dir / "airport-alias-approval-package.json",
        "locationGroups": reconciliation_dir / "airport-location-reconciliation-groups.json",
        "summary": reconciliation_dir / "airport-asset-reconciliation-summary.json",
        "reviewFindings": reconciliation_dir / "airport-asset-reconciliation-review-findings.json",
        "readinessGates": reconciliation_dir / "airport-asset-readiness-gates.json",
    }

    loaded: dict[str, Any] = {}
    for key, path in artifact_paths.items():
        loaded[key] = load_json(path)

    for entry in manifest.get("artifacts", []):
        relative = str(entry.get("relativePath", ""))
        expected_hash = str(entry.get("sha256", ""))
        file_path = reconciliation_dir / relative
        if expected_hash and file_path.is_file() and _sha256_file(file_path) != expected_hash:
            raise AirportReviewProjectionError("ARTIFACT_HASH_MISMATCH", f"artifact hash mismatch: {relative}")

    result = loaded["reconciliationResult"]
    if str(result.get("authority", "")) != RECONCILIATION_AUTHORITY:
        raise AirportReviewProjectionError("RESULT_AUTHORITY_MISMATCH", "result authority mismatch")
    if str(result.get("profileVersion", "")) != RECONCILIATION_PROFILE_VERSION:
        raise AirportReviewProjectionError("RESULT_VERSION_MISMATCH", "result profile version mismatch")

    summary = loaded["summary"]
    records = list(result.get("records", []))
    proposals = list(loaded["canonicalProposals"])
    duplicate_groups = list(loaded["duplicateGroups"])
    alias_package = list(loaded["aliasPackage"])

    record_count = len(records)
    if int(summary.get("reconciliationRecordCount", -1)) != record_count:
        raise AirportReviewProjectionError("RECORD_COUNT_MISMATCH", "reconciliation record count mismatch")
    if len(proposals) != record_count:
        raise AirportReviewProjectionError("PROPOSAL_COUNT_MISMATCH", "proposal count mismatch")

    workbook_digest = str(records[0].get("sourceWorkbookDigest", "")) if records else ""
    if expected_workbook_digest and workbook_digest != expected_workbook_digest:
        raise AirportReviewProjectionError("WORKBOOK_DIGEST_MISMATCH", "workbook digest mismatch")

    result_digest = str(summary.get("resultDigest", ""))
    if expected_reconciliation_digest and result_digest != expected_reconciliation_digest:
        raise AirportReviewProjectionError("RECONCILIATION_DIGEST_MISMATCH", "reconciliation digest mismatch")

    return {
        "reconciliationAuthority": RECONCILIATION_AUTHORITY,
        "sourceWorkbookDigest": workbook_digest,
        "reconciliationResultDigest": str(result.get("resultDigest", "")),
        "summaryResultDigest": result_digest,
        "recordCount": record_count,
        "proposalCount": len(proposals),
        "duplicateGroupCount": len(duplicate_groups),
        "aliasProposalCount": len(alias_package),
        "gateCount": len(loaded["readinessGates"]),
        "loaded": loaded,
    }
