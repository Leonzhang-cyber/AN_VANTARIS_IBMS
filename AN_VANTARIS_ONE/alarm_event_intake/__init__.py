"""Canonical Alarm/Event Intake Foundation.

This package is contract-first, deterministic, read-only, and projection-only.
It does not provide production alarm runtime, UFMS FaultCase creation, work-order
creation, Evidence Center writes, database access, API routes, frontend code, or
connector execution.
"""

from .enums import CONTRACT_VERSION
from .models import (
    build_canonical_alarm_event_candidate,
    build_intake_envelope,
    build_projection,
)
from .normalization import normalize_intake_envelope
from .projection import build_facets, build_filters, paginate_candidates, sort_candidates
from .validation import validate_intake_envelope

__all__ = [
    "CONTRACT_VERSION",
    "build_canonical_alarm_event_candidate",
    "build_intake_envelope",
    "build_projection",
    "normalize_intake_envelope",
    "build_facets",
    "build_filters",
    "paginate_candidates",
    "sort_candidates",
    "validate_intake_envelope",
]
