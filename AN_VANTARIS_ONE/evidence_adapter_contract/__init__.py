"""VANTARIS ONE generic Evidence Adapter Contract."""
from __future__ import annotations

from .errors import EvidenceAdapterContractError
from .models import build_evidence_adapter_envelope
from .normalization import normalize_envelope_input
from .projection import build_contract_projection, sort_envelopes
from .validation import validate_envelope

__all__ = [
    "EvidenceAdapterContractError",
    "build_contract_projection",
    "build_evidence_adapter_envelope",
    "normalize_envelope_input",
    "sort_envelopes",
    "validate_envelope",
]
