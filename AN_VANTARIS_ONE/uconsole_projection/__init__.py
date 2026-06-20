"""VANTARIS ONE read-only UConsole projection foundation."""
from __future__ import annotations

from .errors import UConsoleProjectionError
from .models import (
    build_dashboard_card,
    build_source_artifact_reference,
    build_source_system_row,
    build_uconsole_projection_shell,
)
from .projection import (
    build_row_facets,
    build_row_filters,
    paginate_source_system_rows,
    sort_dashboard_cards,
    sort_source_system_rows,
)
from .validation import validate_projection

__all__ = [
    "UConsoleProjectionError",
    "build_dashboard_card",
    "build_row_facets",
    "build_row_filters",
    "build_source_artifact_reference",
    "build_source_system_row",
    "build_uconsole_projection_shell",
    "paginate_source_system_rows",
    "sort_dashboard_cards",
    "sort_source_system_rows",
    "validate_projection",
]
