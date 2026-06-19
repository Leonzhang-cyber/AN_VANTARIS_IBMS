"""Fail-closed validation for Evidence Adapter Contract envelopes."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .enums import (
    FIXTURE_EVIDENCE_KINDS,
    RUNTIME_EVIDENCE_KINDS,
    RUNTIME_PRODUCER_TYPES,
    ValidationState,
)
from .errors import EvidenceAdapterContractError

FORBIDDEN_PAYLOAD_KEYS = frozenset(
    {
        "heartbeatAt",
        "lastSeen",
        "latencyMs",
        "uptimePercent",
        "availabilityPercent",
        "throughputBps",
        "packetLossPercent",
        "connectorOnline",
        "gatewayOnline",
        "routeOnline",
        "deviceId",
        "deviceCode",
        "sourceId",
    }
)


def validate_envelope(
    envelope: Mapping[str, Any],
    *,
    allowed_source_system_keys: Sequence[str] | None = None,
) -> None:
    required = (
        "envelopeId",
        "producerType",
        "producerId",
        "sourceSystemKey",
        "registryEntryId",
        "evidenceKind",
        "evidenceScope",
        "payloadDigest",
        "validationState",
    )
    for key in required:
        if not str(envelope.get(key, "")).strip():
            raise EvidenceAdapterContractError("MISSING_REQUIRED_FIELD", f"missing required field: {key}")

    if not str(envelope.get("producerId", "")).strip():
        raise EvidenceAdapterContractError("MISSING_PRODUCER_ID", "producerId is required")

    source_key = str(envelope.get("sourceSystemKey", ""))
    if not source_key:
        raise EvidenceAdapterContractError("MISSING_SOURCE_SYSTEM_KEY", "sourceSystemKey is required")
    if allowed_source_system_keys and source_key not in allowed_source_system_keys:
        raise EvidenceAdapterContractError("UNKNOWN_SOURCE_SYSTEM_KEY", f"unknown sourceSystemKey: {source_key}")

    if not str(envelope.get("evidenceKind", "")).strip():
        raise EvidenceAdapterContractError("MISSING_EVIDENCE_KIND", "evidenceKind is required")

    if not str(envelope.get("payloadDigest", "")).strip():
        raise EvidenceAdapterContractError("MISSING_PAYLOAD_DIGEST", "payloadDigest is required")

    producer_type = str(envelope.get("producerType", ""))
    evidence_kind = str(envelope.get("evidenceKind", ""))
    validation_state = str(envelope.get("validationState", ""))

    if producer_type in RUNTIME_PRODUCER_TYPES and evidence_kind in RUNTIME_EVIDENCE_KINDS:
        raise EvidenceAdapterContractError(
            "RUNTIME_EVIDENCE_NOT_AUTHORIZED",
            "A2-04 contract validation does not accept live runtime evidence",
        )

    if validation_state == ValidationState.ACCEPTED_AS_EVIDENCE.value:
        if producer_type in RUNTIME_PRODUCER_TYPES:
            raise EvidenceAdapterContractError(
                "RUNTIME_PRODUCER_NOT_AUTHORIZED",
                "runtime producers cannot be accepted in fixture-only contract mode",
            )

    payload = envelope.get("payload", {})
    if isinstance(payload, dict):
        for key in payload:
            if key in FORBIDDEN_PAYLOAD_KEYS:
                raise EvidenceAdapterContractError(
                    "FORBIDDEN_PAYLOAD_FIELD",
                    f"forbidden payload field: {key}",
                )

    if "generatedAt" in envelope or "observedAt" in envelope:
        raise EvidenceAdapterContractError("VOLATILE_TIMESTAMP", "volatile timestamps are forbidden")

    if evidence_kind in RUNTIME_EVIDENCE_KINDS and producer_type == "OFFLINE_FIXTURE":
        raise EvidenceAdapterContractError(
            "FIXTURE_RUNTIME_KIND_MISMATCH",
            "offline fixtures cannot use runtime evidence kinds",
        )

    if evidence_kind not in FIXTURE_EVIDENCE_KINDS and producer_type == "OFFLINE_FIXTURE":
        if validation_state == ValidationState.ACCEPTED_AS_EVIDENCE.value:
            raise EvidenceAdapterContractError(
                "UNSUPPORTED_FIXTURE_KIND",
                f"unsupported fixture evidence kind: {evidence_kind}",
            )
