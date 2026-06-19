"""Offline read-only evidence runner for device reconciliation."""

from .runner import (
    EVIDENCE_NAME,
    EVIDENCE_VERSION,
    EvidencePackageError,
    compare_evidence_reports,
    run_device_reconciliation_evidence,
)

try:
    from .excel import ExcelIntakeError, ExcelWorkbook, run_excel_evidence_intake
except ImportError:  # pragma: no cover
    ExcelIntakeError = None  # type: ignore
    ExcelWorkbook = None  # type: ignore
    run_excel_evidence_intake = None  # type: ignore

__all__ = [
    "EVIDENCE_NAME",
    "EVIDENCE_VERSION",
    "EvidencePackageError",
    "compare_evidence_reports",
    "run_device_reconciliation_evidence",
    "ExcelIntakeError",
    "ExcelWorkbook",
    "run_excel_evidence_intake",
]
