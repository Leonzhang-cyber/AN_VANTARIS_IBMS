"""Alarm/Event asset, point, and location resolution review projection.

This package is deterministic, read-only, and projection-only. It does not
write Asset Graph records, UFMS FaultCases, WorkOrderIntents, databases, APIs,
frontends, or connector runtime state.
"""

from .enums import CONTRACT_VERSION
from .models import build_resolution_projection, build_resolution_row, build_review_card
from .projection import build_facets, build_filters, paginate_rows, sort_rows
from .validation import validate_projection_boundary, validate_resolution_projection

__all__ = [
    "CONTRACT_VERSION",
    "build_resolution_projection",
    "build_resolution_row",
    "build_review_card",
    "build_facets",
    "build_filters",
    "paginate_rows",
    "sort_rows",
    "validate_projection_boundary",
    "validate_resolution_projection",
]
