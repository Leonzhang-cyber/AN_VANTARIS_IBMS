"""Envelope input normalization."""
from __future__ import annotations

from typing import Any, Mapping

from .enums import EvidenceKind, EvidenceScope, ProducerType


def normalize_envelope_input(raw: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "producerType": str(raw.get("producerType", ProducerType.UNKNOWN.value)).strip().upper(),
        "producerId": str(raw.get("producerId", "")).strip(),
        "sourceSystemKey": str(raw.get("sourceSystemKey", "")).strip().upper(),
        "registryEntryId": str(raw.get("registryEntryId", "")).strip(),
        "evidenceKind": str(raw.get("evidenceKind", EvidenceKind.UNKNOWN.value)).strip().upper(),
        "evidenceScope": str(raw.get("evidenceScope", EvidenceScope.UNKNOWN.value)).strip().upper(),
        "payload": dict(raw.get("payload", {})),
        "provenance": str(raw.get("provenance", "")).strip(),
        "observedAtPolicy": str(raw.get("observedAtPolicy", "DETERMINISTIC_NO_VOLATILE_TIMESTAMP")).strip(),
    }
