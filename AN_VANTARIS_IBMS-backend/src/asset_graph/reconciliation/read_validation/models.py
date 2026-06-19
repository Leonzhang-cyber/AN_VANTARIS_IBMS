"""Immutable offline read validation result models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Tuple

from ..models import sha256_digest


EXECUTION_NAME = "VANTARIS ONE Offline Limited Read Validation Execution"
EXECUTION_VERSION = "1.0.0"
AUTHORITY = "ONE-A5-P1-16M"
ACCEPTED_PLAN_STATE = "APPROVED_FOR_LIMITED_READ_VALIDATION"
WRITE_CUTOVER_STATUS = "NOT_READY_FOR_WRITE_CUTOVER"

ALLOWED_VALIDATION_OUTCOMES = frozenset({
    "VALIDATION_COMPLETE",
    "VALIDATION_COMPLETE_WITH_REVIEWS",
    "VALIDATION_FAILED",
    "EXECUTION_BLOCKED",
})

REJECTED_PLAN_STATES = frozenset({
    "DRAFT",
    "WAITING_FOR_EVIDENCE",
    "WAITING_FOR_READINESS",
    "WAITING_FOR_APPROVAL",
    "EXECUTION_BLOCKED",
    "VALIDATION_FAILED",
    "ROLLED_BACK",
})


@dataclass(frozen=True)
class ExecutionRequest:
    root: str
    plan_path: str
    evidence_path: str
    readiness_path: str
    output_dir: str
    run_id: str
    evaluation_instant: str
    evidence_digest: str
    readiness_result_digest: str
    scope_digest: str
    mapping_version: str


@dataclass(frozen=True)
class PreExecutionGateResult:
    gate_code: str
    status: str
    blocking: bool
    observed_value: str
    required_value: str

    def serialize(self) -> dict[str, Any]:
        return {
            "gateCode": self.gate_code,
            "status": self.status,
            "blocking": self.blocking,
            "observedValue": self.observed_value,
            "requiredValue": self.required_value,
        }


@dataclass(frozen=True)
class ArtifactEntry:
    artifact_type: str
    relative_path: str
    sha256: str
    contains_raw_records: bool
    retention_class: str

    def serialize(self) -> dict[str, Any]:
        return {
            "artifactType": self.artifact_type,
            "relativePath": self.relative_path,
            "sha256": self.sha256,
            "containsRawRecords": self.contains_raw_records,
            "retentionClass": self.retention_class,
        }


@dataclass(frozen=True)
class RollbackEvidence:
    rollback_required: bool
    rollback_reason: str
    in_memory_state_discarded: bool
    source_data_unchanged: bool
    canonical_data_unchanged: bool
    artifacts_retained_or_removed: str

    def serialize(self) -> dict[str, Any]:
        return {
            "rollbackRequired": self.rollback_required,
            "rollbackReason": self.rollback_reason,
            "inMemoryStateDiscarded": self.in_memory_state_discarded,
            "sourceDataUnchanged": self.source_data_unchanged,
            "canonicalDataUnchanged": self.canonical_data_unchanged,
            "artifactsRetainedOrRemoved": self.artifacts_retained_or_removed,
        }


@dataclass(frozen=True)
class ExecutionResult:
    execution_name: str
    execution_version: str
    authority: str
    contract_version: str
    plan_digest: str
    scope_digest: str
    evidence_digest: str
    readiness_result_digest: str
    mapping_version: str
    run_id: str
    execution_state: str
    pre_execution_gate_results: Tuple[PreExecutionGateResult, ...]
    source_counts: Mapping[str, Any]
    projection_counts: Mapping[str, Any]
    relationship_metrics: Mapping[str, Any]
    readiness_decision: str
    validation_outcome: str
    output_artifacts: Tuple[ArtifactEntry, ...]
    retention_disposition: str
    rollback_disposition: Mapping[str, Any]
    write_cutover_status: str
    result_digest: str = ""

    def serialize(self) -> dict[str, Any]:
        payload = {
            "executionName": self.execution_name,
            "executionVersion": self.execution_version,
            "authority": self.authority,
            "contractVersion": self.contract_version,
            "planDigest": self.plan_digest,
            "scopeDigest": self.scope_digest,
            "evidenceDigest": self.evidence_digest,
            "readinessResultDigest": self.readiness_result_digest,
            "mappingVersion": self.mapping_version,
            "runId": self.run_id,
            "executionState": self.execution_state,
            "preExecutionGateResults": [item.serialize() for item in self.pre_execution_gate_results],
            "sourceCounts": dict(self.source_counts),
            "projectionCounts": dict(self.projection_counts),
            "relationshipMetrics": dict(self.relationship_metrics),
            "readinessDecision": self.readiness_decision,
            "validationOutcome": self.validation_outcome,
            "outputArtifacts": [item.serialize() for item in self.output_artifacts],
            "retentionDisposition": self.retention_disposition,
            "rollbackDisposition": dict(self.rollback_disposition),
            "writeCutoverStatus": self.write_cutover_status,
        }
        payload["resultDigest"] = self.result_digest or sha256_digest(payload)
        return payload
