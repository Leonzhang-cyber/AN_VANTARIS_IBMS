"""Write deterministic read validation output artifacts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Tuple

from .models import ArtifactEntry


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def build_aggregate_summary(
    *,
    execution_result: Mapping[str, Any],
    readiness_assessment: Mapping[str, Any],
    reconciliation_report: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "summaryName": "VANTARIS ONE Offline Limited Read Validation Aggregate Summary",
        "summaryVersion": "1.0.0",
        "runId": execution_result["runId"],
        "validationOutcome": execution_result["validationOutcome"],
        "readinessDecision": readiness_assessment.get("decision"),
        "evidenceClassification": readiness_assessment.get("evidenceClassification"),
        "sourceCounts": execution_result.get("sourceCounts"),
        "projectionCounts": execution_result.get("projectionCounts"),
        "relationshipMetrics": execution_result.get("relationshipMetrics"),
        "reviewCount": readiness_assessment.get("reviewCount", 0),
        "warningCount": readiness_assessment.get("warningCount", 0),
        "hardBlockerCount": readiness_assessment.get("hardBlockerCount", 0),
        "containsRawRecords": False,
        "reconciliationStatus": reconciliation_report.get("status"),
    }


def write_output_artifacts(
    output_dir: Path,
    *,
    execution_result: Mapping[str, Any],
    reconciliation_report: Mapping[str, Any],
    readiness_assessment: Mapping[str, Any],
    retention_class: str,
) -> Tuple[ArtifactEntry, ...]:
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "execution-result.json": execution_result,
        "reconciliation-report.json": reconciliation_report,
        "readiness-assessment.json": readiness_assessment,
        "aggregate-summary.json": build_aggregate_summary(
            execution_result=execution_result,
            readiness_assessment=readiness_assessment,
            reconciliation_report=reconciliation_report,
        ),
    }
    entries: list[ArtifactEntry] = []
    for name, payload in files.items():
        path = output_dir / name
        write_json(path, payload)
        entries.append(
            ArtifactEntry(
                artifact_type=name.replace(".json", "").replace("-", "_").upper(),
                relative_path=name,
                sha256=_sha256_file(path),
                contains_raw_records=False,
                retention_class=retention_class,
            )
        )
    manifest = {
        "manifestName": "VANTARIS ONE Offline Limited Read Validation Artifact Manifest",
        "manifestVersion": "1.0.0",
        "runId": execution_result["runId"],
        "artifacts": [item.serialize() for item in entries],
    }
    manifest_path = output_dir / "artifact-manifest.json"
    write_json(manifest_path, manifest)
    entries.append(
        ArtifactEntry(
            artifact_type="ARTIFACT_MANIFEST",
            relative_path="artifact-manifest.json",
            sha256=_sha256_file(manifest_path),
            contains_raw_records=False,
            retention_class=retention_class,
        )
    )
    return tuple(entries)
