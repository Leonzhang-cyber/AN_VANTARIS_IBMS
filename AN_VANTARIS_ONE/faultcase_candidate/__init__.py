"""Read-only UFMS FaultCase candidate projection foundation.

This package creates review candidates only. It does not create real UFMS
FaultCases, WorkOrderIntents, WorkOrders, Evidence Center records, Asset Graph
writes, database writes, API routes, frontend UI, or connector runtime state.
"""

from .enums import CONTRACT_VERSION
from .models import build_faultcase_candidate, build_faultcase_projection, build_review_card
from .projection import build_facets, build_filters, paginate_candidates, sort_candidates
from .validation import validate_boundary, validate_faultcase_projection

__all__ = [
    "CONTRACT_VERSION",
    "build_faultcase_candidate",
    "build_faultcase_projection",
    "build_review_card",
    "build_facets",
    "build_filters",
    "paginate_candidates",
    "sort_candidates",
    "validate_boundary",
    "validate_faultcase_projection",
]
