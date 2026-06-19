"""Generic Integration Health model builders."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import FindingSeverity, HealthState


def _value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def build_health_dimension(
    *,
    state: HealthState | str,
    severity: FindingSeverity | str = FindingSeverity.INFO,
    reason_codes: Sequence[str] = (),
    evidence_references: Sequence[Mapping[str, Any]] = (),
    runtime_observed: bool = False,
    review_required: bool = False,
    classification_state: str | None = None,
) -> dict[str, Any]:
    dimension = {
        "state": _value(state),
        "severity": _value(severity),
        "reasonCodes": sorted(set(reason_codes)),
        "evidenceReferences": list(evidence_references),
        "runtimeObserved": bool(runtime_observed),
        "reviewRequired": bool(review_required),
    }
    if classification_state:
        dimension["classificationState"] = classification_state
    dimension["deterministicDigest"] = sha256_digest(dimension)
    return dimension


def build_finding(
    *,
    finding_type: str,
    severity: FindingSeverity | str,
    reason_code: str,
    title: str,
    description: str,
    affected_dimension: str,
    decision_required: bool,
    affected_source_system_keys: Sequence[str],
    evidence_references: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    identity = {
        "findingType": finding_type,
        "reasonCode": reason_code,
        "affectedDimension": affected_dimension,
        "affectedSourceSystemKeys": sorted(set(affected_source_system_keys)),
    }
    finding = {
        "findingId": sha256_digest(identity),
        **identity,
        "severity": _value(severity),
        "title": title,
        "description": description,
        "decisionRequired": bool(decision_required),
        "evidenceReferences": list(evidence_references),
    }
    finding["deterministicDigest"] = sha256_digest(finding)
    return finding
