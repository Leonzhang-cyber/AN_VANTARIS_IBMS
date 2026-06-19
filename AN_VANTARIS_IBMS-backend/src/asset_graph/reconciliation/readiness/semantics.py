"""Gate semantics and operator explanation helpers."""
from __future__ import annotations

from typing import Any, Mapping

from .evidence import EvidenceSnapshot, _parse_percent
from .models import GateResult

APPROVED_AGGREGATIONS = frozenset({
    "MINIMUM_PER_RECORD",
    "MAXIMUM_PER_RECORD",
    "PACKAGE_TOTAL",
    "PACKAGE_RATIO",
    "EXACT_PARITY",
    "ZERO_TOLERANCE",
    "BOUNDED_TOTAL",
    "BOOLEAN_ASSERTION",
})

NUMERIC_GATE_CODES = (
    "REQUIRED_FIELD_COVERAGE_GATE",
    "SAFE_SOURCE_COVERAGE_GATE",
    "UNRESOLVED_RELATIONSHIP_GATE",
    "DUPLICATE_RELATIONSHIP_GATE",
    "REVIEW_RATIO_GATE",
    "WARNING_RATIO_GATE",
    "HAS_POINT_PARITY_GATE",
    "TENANT_SCOPE_GATE",
    "SITE_SCOPE_GATE",
)

RAW_IDENTIFIER_MARKERS = ("SYNTH-DEV-", "ag-device-", "ag-point-")

APPROVED_PERCENTAGE_SCALES = frozenset({
    "0_TO_100",
    "NONE",
})


class GateSemanticsError(ValueError):
    """Invalid gate semantics in readiness policy."""


def validate_gate_semantics(policy: Mapping[str, Any]) -> None:
    semantics = policy.get("gateSemantics")
    if not isinstance(semantics, Mapping):
        raise GateSemanticsError("gateSemantics must be an object")
    approved = set(policy.get("approvedAggregationLabels", ()))
    if not approved:
        raise GateSemanticsError("approvedAggregationLabels must be declared")
    for gate_code in NUMERIC_GATE_CODES:
        if gate_code not in semantics:
            raise GateSemanticsError(f"missing gate semantics for {gate_code}")
        entry = semantics[gate_code]
        aggregation = entry.get("aggregation")
        if aggregation not in APPROVED_AGGREGATIONS:
            raise GateSemanticsError(f"unsupported aggregation label for {gate_code}: {aggregation}")
        if aggregation not in approved:
            raise GateSemanticsError(f"aggregation not approved by policy for {gate_code}: {aggregation}")
        scale = entry.get("percentageScale", "NONE")
        if scale not in APPROVED_PERCENTAGE_SCALES:
            raise GateSemanticsError(f"unsupported percentage scale for {gate_code}: {scale}")
    for gate_code, entry in semantics.items():
        aggregation = entry.get("aggregation")
        if aggregation not in APPROVED_AGGREGATIONS:
            raise GateSemanticsError(f"unsupported aggregation label for {gate_code}: {aggregation}")
        if aggregation not in approved:
            raise GateSemanticsError(f"aggregation not approved by policy for {gate_code}: {aggregation}")


def build_coverage_statistics(evidence: Mapping[str, Any], policy: Mapping[str, Any]) -> dict[str, Any]:
    rows = [row for row in evidence.get("fieldCoverage", ()) if isinstance(row, Mapping)]
    required_values = [_parse_percent(row.get("requiredFieldCoverage")) for row in rows]
    safe_values = [_parse_percent(row.get("safeSourceFieldCoverage")) for row in rows]
    threshold = float(policy["coverageThresholds"]["safeSourceFieldCoverageMinimumPercent"])
    safe_count = len(safe_values)
    return {
        "requiredCoverageMinimumPercent": min(required_values) if required_values else 0.0,
        "requiredCoverageAveragePercent": round(sum(required_values) / len(required_values), 2) if required_values else 0.0,
        "safeSourceCoverageMinimumPercent": min(safe_values) if safe_values else 0.0,
        "safeSourceCoverageAveragePercent": round(sum(safe_values) / len(safe_values), 2) if safe_values else 0.0,
        "safeSourceCoverageMaximumPercent": max(safe_values) if safe_values else 0.0,
        "safeSourceRecordsBelowThreshold": sum(1 for value in safe_values if value < threshold),
        "safeSourceRecordCount": safe_count,
    }


def build_gate_semantics_index(policy: Mapping[str, Any]) -> dict[str, Any]:
    return dict(policy.get("gateSemantics", {}))


def _explanation_for_gate(
    gate: GateResult,
    semantics: Mapping[str, Any],
    coverage_stats: Mapping[str, Any],
    snapshot: EvidenceSnapshot,
) -> str:
    entry = semantics.get(gate.gate_code, {})
    template = str(entry.get("explanation", "")).strip()
    if gate.gate_code == "SAFE_SOURCE_COVERAGE_GATE":
        if gate.status == "PASS":
            return (
                "All Device-scoped fieldCoverage rows meet the safe-source policy floor; "
                "package average and modal coverage are informational only."
            )
        below = int(coverage_stats.get("safeSourceRecordsBelowThreshold", 0))
        average = coverage_stats.get("safeSourceCoverageAveragePercent", 0.0)
        return (
            f"{below} Device coverage record(s) are below the policy floor; "
            f"package average ({average:.2f}%) does not override a record-level failure."
        )
    if gate.gate_code == "REQUIRED_FIELD_COVERAGE_GATE":
        if gate.status == "PASS":
            return "All Device-scoped fieldCoverage rows meet the required-field policy floor."
        return "At least one Device coverage record is below the required-field policy floor."
    if gate.gate_code == "UNRESOLVED_RELATIONSHIP_GATE":
        if gate.status == "PASS":
            return "Unresolved relationship count is within the bounded total allowed for limited validation."
        return "Unresolved relationship count exceeds the bounded total allowed for read-migration candidate paths."
    if gate.gate_code == "DUPLICATE_RELATIONSHIP_GATE":
        if gate.status == "PASS":
            return "No duplicate canonical relationship evidence exceeds zero tolerance."
        return "Duplicate canonical relationship evidence exceeds zero tolerance and remains blocking."
    if gate.gate_code == "REVIEW_RATIO_GATE":
        return template or "Review ratio is computed as reviewCount divided by totalRecords."
    if gate.gate_code == "WARNING_RATIO_GATE":
        return template or "Warning ratio is computed as warningCount divided by totalRecords."
    if gate.gate_code == "HAS_POINT_PARITY_GATE":
        if gate.status == "PASS":
            return "Projected Point count exactly matches PASS HAS_POINT relationship count."
        return "Projected Point count does not exactly match PASS HAS_POINT relationship count."
    if gate.gate_code == "TENANT_SCOPE_GATE":
        return "Tenant scope blockers must be absent for readiness approval." if gate.status == "PASS" else "Tenant scope blockers are present."
    if gate.gate_code == "SITE_SCOPE_GATE":
        return "Site scope blockers must be absent for readiness approval." if gate.status == "PASS" else "Site scope blockers are present."
    return template or f"{gate.gate_code} evaluated using policy-defined semantics."


def enrich_gate_result(
    gate: GateResult,
    policy: Mapping[str, Any],
    coverage_stats: Mapping[str, Any],
    snapshot: EvidenceSnapshot,
) -> dict[str, Any]:
    semantics = policy.get("gateSemantics", {})
    entry = semantics.get(gate.gate_code, {})
    payload = gate.serialize()
    payload["comparisonMetric"] = str(entry.get("comparisonMetric", gate.gate_code))
    payload["aggregation"] = str(entry.get("aggregation", "BOOLEAN_ASSERTION"))
    payload["comparisonScale"] = str(entry.get("percentageScale", "NONE"))
    payload["explanation"] = _explanation_for_gate(gate, semantics, coverage_stats, snapshot)
    return payload
