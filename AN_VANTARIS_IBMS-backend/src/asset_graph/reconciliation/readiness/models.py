"""Immutable readiness assessment result models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Tuple

from ..models import sha256_digest


@dataclass(frozen=True)
class GateResult:
    gate_code: str
    status: str
    severity: str
    observed_value: str
    required_value: str
    blocking: bool
    remediation_category: str

    def serialize(self) -> dict[str, Any]:
        return {
            "gateCode": self.gate_code,
            "status": self.status,
            "severity": self.severity,
            "observedValue": self.observed_value,
            "requiredValue": self.required_value,
            "blocking": self.blocking,
            "remediationCategory": self.remediation_category,
        }


@dataclass(frozen=True)
class ReadinessAssessment:
    assessment_name: str
    assessment_version: str
    authority: str
    policy_version: str
    evidence_digest: str
    evidence_classification: str
    decision: str
    hard_blocker_count: int
    review_count: int
    warning_count: int
    passed_gate_count: int
    failed_gate_count: int
    gate_results: Tuple[GateResult, ...]
    coverage_summary: Mapping[str, Any]
    identity_summary: Mapping[str, Any]
    scope_summary: Mapping[str, Any]
    relationship_summary: Mapping[str, Any]
    required_remediations: Tuple[str, ...]
    write_cutover_status: str
    result_digest: str = ""

    def serialize(self) -> dict[str, Any]:
        payload = {
            "assessmentName": self.assessment_name,
            "assessmentVersion": self.assessment_version,
            "authority": self.authority,
            "policyVersion": self.policy_version,
            "evidenceDigest": self.evidence_digest,
            "evidenceClassification": self.evidence_classification,
            "decision": self.decision,
            "hardBlockerCount": self.hard_blocker_count,
            "reviewCount": self.review_count,
            "warningCount": self.warning_count,
            "passedGateCount": self.passed_gate_count,
            "failedGateCount": self.failed_gate_count,
            "gateResults": [item.serialize() for item in self.gate_results],
            "coverageSummary": dict(self.coverage_summary),
            "identitySummary": dict(self.identity_summary),
            "scopeSummary": dict(self.scope_summary),
            "relationshipSummary": dict(self.relationship_summary),
            "requiredRemediations": list(self.required_remediations),
            "writeCutoverStatus": self.write_cutover_status,
        }
        payload["resultDigest"] = self.result_digest or sha256_digest(payload)
        return payload
