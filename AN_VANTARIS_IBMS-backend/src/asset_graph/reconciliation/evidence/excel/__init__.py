"""Synthetic Excel evidence intake adapter."""

from .constants import (
    ASSESSMENT_TYPE,
    AUTHORITY,
    MAX_READ_MIGRATION,
    WRITE_CUTOVER_STATUS,
)
from .errors import ExcelIntakeError
from .intake import (
    compare_deterministic_outputs,
    run_excel_evidence_intake,
    validate_rejected_samples,
)
from .workbook import ExcelWorkbook

__all__ = [
    "ASSESSMENT_TYPE",
    "AUTHORITY",
    "ExcelIntakeError",
    "ExcelWorkbook",
    "MAX_READ_MIGRATION",
    "WRITE_CUTOVER_STATUS",
    "compare_deterministic_outputs",
    "run_excel_evidence_intake",
    "validate_rejected_samples",
]
