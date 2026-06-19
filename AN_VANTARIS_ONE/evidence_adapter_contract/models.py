"""Evidence Adapter Contract model builders."""
from __future__ import annotations

from typing import Any, Mapping

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def build_envelope_id(*, producer_type: str, producer_id: str, source_system_key: str, evidence_kind: str) -> str:
    return sha256_digest(
        {
            "contractVersion": CONTRACT_VERSION,
            "producerType": producer_type,
            "producerId": producer_id,
            "sourceSystemKey": source_system_key,
            "evidenceKind": evidence_kind,
        }
    )


def build_evidence_adapter_envelope(
    *,
    producer_type: str,
    producer_id: str,
    source_system_key: str,
    registry_entry_id: str,
    evidence_kind: str,
    evidence_scope: str,
    payload: Mapping[str, Any],
    provenance: str,
    validation_state: str,
    rejection_reasons: list[str] | None = None,
    observed_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
) -> dict[str, Any]:
    payload_digest = sha256_digest(payload)
    envelope_id = build_envelope_id(
        producer_type=producer_type,
        producer_id=producer_id,
        source_system_key=source_system_key,
        evidence_kind=evidence_kind,
    )
    envelope = {
        "envelopeId": envelope_id,
        "contractVersion": CONTRACT_VERSION,
        "producerType": producer_type,
        "producerId": producer_id,
        "sourceSystemKey": source_system_key,
        "registryEntryId": registry_entry_id,
        "evidenceKind": evidence_kind,
        "evidenceScope": evidence_scope,
        "observedAtPolicy": observed_at_policy,
        "payloadDigest": payload_digest,
        "payload": dict(payload),
        "provenance": provenance,
        "validationState": validation_state,
        "rejectionReasons": sorted(rejection_reasons or []),
    }
    envelope["deterministicDigest"] = sha256_digest(
        {k: v for k, v in envelope.items() if k != "deterministicDigest"}
    )
    return envelope
