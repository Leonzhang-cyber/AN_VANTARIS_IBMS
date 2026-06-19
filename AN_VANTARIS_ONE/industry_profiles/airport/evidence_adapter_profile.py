"""Airport offline fixture builder for the Evidence Adapter Contract."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from evidence_adapter_contract.enums import (
    EvidenceKind,
    EvidenceScope,
    ProducerType,
    ValidationState,
)
from evidence_adapter_contract.models import build_evidence_adapter_envelope
from evidence_adapter_contract.projection import build_contract_projection, sort_envelopes
from evidence_adapter_contract.validation import validate_envelope
from source_system_registry.digest import sha256_digest

from .candidate_projection import run_airport_source_system_projection
from .source_system_review_projection import compare_deterministic_outputs

AUTHORITY = "ONE-AIRPORT-A2-04"
IMPLEMENTATION_STATUS = "EDGE_LINK_EVIDENCE_ADAPTER_CONTRACT_COMPLETE"
READINESS_OUTCOME = "EDGE_LINK_EVIDENCE_ADAPTER_CONTRACT_DEFINED_RUNTIME_PENDING"

FIXTURE_KIND_BY_SYSTEM = {
    "ACS": EvidenceKind.CONFIG_DECLARATION.value,
    "RAS": EvidenceKind.MAPPING_VERSION.value,
    "CCTV": EvidenceKind.SCHEMA_VERSION.value,
    "PA": EvidenceKind.CAPABILITY_OBSERVATION.value,
    "TEL": EvidenceKind.DELIVERY_EVIDENCE.value,
}


def build_fixture_payload(*, candidate: Mapping[str, Any], evidence_kind: str) -> dict[str, Any]:
    return {
        "fixtureOnly": True,
        "declarationType": evidence_kind,
        "sourceSystemKey": str(candidate.get("sourceSystemKey", "")),
        "mappingVersion": str(candidate.get("mappingVersion", "")),
        "schemaVersion": str(candidate.get("schemaVersion", "")),
        "systemCategory": str(candidate.get("systemCategory", "")),
        "contractMode": "OFFLINE_FIXTURE_VALIDATION",
    }


def build_airport_fixture_envelope(candidate: Mapping[str, Any]) -> dict[str, Any]:
    source_key = str(candidate["sourceSystemKey"])
    evidence_kind = FIXTURE_KIND_BY_SYSTEM[source_key]
    payload = build_fixture_payload(candidate=candidate, evidence_kind=evidence_kind)
    envelope = build_evidence_adapter_envelope(
        producer_type=ProducerType.OFFLINE_FIXTURE.value,
        producer_id=sha256_digest({"fixture": source_key, "authority": AUTHORITY}),
        source_system_key=source_key,
        registry_entry_id=str(candidate["registryEntryId"]),
        evidence_kind=evidence_kind,
        evidence_scope=EvidenceScope.SOURCE_SYSTEM.value,
        payload=payload,
        provenance="ONE-AIRPORT-A2-04 offline fixture validation",
        validation_state=ValidationState.NOT_RUNTIME_EVIDENCE.value,
    )
    validate_envelope(envelope, allowed_source_system_keys=sorted(FIXTURE_KIND_BY_SYSTEM))
    return envelope


def build_airport_evidence_adapter_projection(
    candidates: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if len(candidates) != 5:
        raise ValueError("expected exactly five airport source-system candidates")

    envelopes = sort_envelopes([build_airport_fixture_envelope(candidate) for candidate in candidates])
    return build_contract_projection(
        envelopes=envelopes,
        source_system_candidate_count=len(candidates),
        readiness_outcome=READINESS_OUTCOME,
        implementation_status=IMPLEMENTATION_STATUS,
    )


def run_airport_evidence_adapter_projection(
    *,
    evidence_dir: Path,
    profile_path: Path,
    output_path: Path | None = None,
) -> dict[str, Any]:
    candidate_projection = run_airport_source_system_projection(
        evidence_dir=evidence_dir,
        profile_path=profile_path,
        output_path=None,
    )
    candidates = list(candidate_projection.get("candidates", []))
    projection = build_airport_evidence_adapter_projection(candidates)
    projection["authority"] = AUTHORITY
    projection["resultDigest"] = sha256_digest({k: v for k, v in projection.items() if k != "resultDigest"})

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return projection


__all__ = [
    "build_airport_evidence_adapter_projection",
    "build_airport_fixture_envelope",
    "compare_deterministic_outputs",
    "run_airport_evidence_adapter_projection",
]
