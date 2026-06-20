"""Read-only UConsole Alarm/Event Operations Projection foundation."""

from .enums import CONTRACT_VERSION
from .models import build_operations_card, build_operations_projection, build_operations_row
from .projection import build_facets, build_filters, paginate_rows, sort_rows
from .validation import validate_boundary, validate_operations_projection

__all__ = [
    "CONTRACT_VERSION",
    "build_operations_card",
    "build_operations_projection",
    "build_operations_row",
    "build_facets",
    "build_filters",
    "paginate_rows",
    "sort_rows",
    "validate_boundary",
    "validate_operations_projection",
]
