"""Airport system and device classification profile."""
from .coverage_analysis import load_bindings_from_classification_output, write_classification_coverage_analysis
from .coverage_metrics import METRIC_DEFINITIONS, build_coverage_analysis, compute_device_coverage
from .mapper import compare_deterministic_outputs, run_airport_classification
from .errors import AirportClassificationProfileError

__all__ = [
    "AirportClassificationProfileError",
    "METRIC_DEFINITIONS",
    "build_coverage_analysis",
    "compare_deterministic_outputs",
    "compute_device_coverage",
    "load_bindings_from_classification_output",
    "run_airport_classification",
    "write_classification_coverage_analysis",
]
