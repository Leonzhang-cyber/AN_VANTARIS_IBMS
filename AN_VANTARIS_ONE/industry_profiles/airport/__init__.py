"""Airport industry profile adapters for VANTARIS ONE platform services."""
from .candidate_projection import (
    compare_deterministic_outputs,
    run_airport_source_system_projection,
)
from .integration_health_projection import (
    compare_deterministic_outputs as compare_integration_health_deterministic_outputs,
    run_airport_integration_health_projection,
)
from .source_system_review_projection import (
    compare_deterministic_outputs as compare_review_deterministic_outputs,
    run_airport_source_system_review_projection,
)

__all__ = [
    "compare_deterministic_outputs",
    "compare_integration_health_deterministic_outputs",
    "compare_review_deterministic_outputs",
    "run_airport_integration_health_projection",
    "run_airport_source_system_projection",
    "run_airport_source_system_review_projection",
]
