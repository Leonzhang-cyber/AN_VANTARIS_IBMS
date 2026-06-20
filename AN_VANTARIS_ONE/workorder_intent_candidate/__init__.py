"""Read-only WorkOrderIntent candidate projection foundation."""

from .enums import CONTRACT_VERSION
from .models import build_review_card, build_workorder_intent_candidate, build_workorder_intent_projection
from .projection import build_facets, build_filters, paginate_candidates, sort_candidates
from .validation import validate_boundary, validate_workorder_intent_projection

__all__ = [
    "CONTRACT_VERSION",
    "build_review_card",
    "build_workorder_intent_candidate",
    "build_workorder_intent_projection",
    "build_facets",
    "build_filters",
    "paginate_candidates",
    "sort_candidates",
    "validate_boundary",
    "validate_workorder_intent_projection",
]
