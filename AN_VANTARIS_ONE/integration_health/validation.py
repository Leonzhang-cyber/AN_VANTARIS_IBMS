"""Fail-closed validation for Integration Health records."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import IntegrationHealthError


def validate_health_record(record: Mapping[str, Any]) -> None:
    required = (
        "integrationHealthId",
        "registryEntryId",
        "sourceSystemKey",
        "lifecycleState",
        "approvalState",
        "readinessState",
    )
    for key in required:
        if not str(record.get(key, "")).strip():
            raise IntegrationHealthError("MISSING_REQUIRED_FIELD", f"missing required field: {key}")

    if record.get("runtimeObservationHealth", {}).get("runtimeObserved") is not False:
        raise IntegrationHealthError(
            "RUNTIME_EVIDENCE_NOT_AUTHORIZED",
            "A2-03 static projection cannot contain runtime observations",
        )

    if record.get("readinessState") == "VERIFIED_READY":
        raise IntegrationHealthError(
            "VERIFIED_READY_NOT_AUTHORIZED",
            "A2-03 cannot produce VERIFIED_READY",
        )

    if record.get("lifecycleState") == "ACTIVE":
        raise IntegrationHealthError(
            "ACTIVE_STATE_NOT_AUTHORIZED",
            "A2-03 cannot activate source systems",
        )

    for dimension_key in (
        "declarationHealth",
        "evidenceHealth",
        "configurationHealth",
        "runtimeObservationHealth",
        "freshnessHealth",
        "capabilityHealth",
        "policyHealth",
    ):
        dimension = record.get(dimension_key, {})
        if dimension.get("state") == "HEALTHY" and not dimension.get("runtimeObserved"):
            raise IntegrationHealthError(
                "HEALTHY_WITHOUT_RUNTIME",
                "static projection cannot classify runtime health as HEALTHY",
            )

    forbidden_fields = (
        "generatedAt",
        "lastSeen",
        "heartbeatAt",
        "latencyMs",
        "uptimePercent",
        "throughputBps",
        "packetLossPercent",
    )
    for token in forbidden_fields:
        if token in record:
            raise IntegrationHealthError(
                "VOLATILE_RUNTIME_METRIC",
                f"volatile or runtime metric field not allowed: {token}",
            )
