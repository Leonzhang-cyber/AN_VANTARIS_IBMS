"""Enums for read-only frontend page contracts."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "read-only-frontend-page-contract.v1"


class LayoutType(str, Enum):
    DASHBOARD = "DASHBOARD"
    TABLE_WORKSPACE = "TABLE_WORKSPACE"
    REVIEW_QUEUE = "REVIEW_QUEUE"
    EVIDENCE_WORKSPACE = "EVIDENCE_WORKSPACE"
    REPORT_WORKSPACE = "REPORT_WORKSPACE"


class UiStateType(str, Enum):
    LOADING = "LOADING"
    EMPTY = "EMPTY"
    ERROR = "ERROR"
    READY = "READY"
    FILTERED_EMPTY = "FILTERED_EMPTY"
    PERMISSION_REQUIRED = "PERMISSION_REQUIRED"


class InteractionType(str, Enum):
    FILTER = "FILTER"
    FACET = "FACET"
    PAGINATION = "PAGINATION"
    SORT = "SORT"
    SEARCH = "SEARCH"
    VIEW_DETAILS = "VIEW_DETAILS"
    EXPORT_DISABLED = "EXPORT_DISABLED"
    APPROVAL_DISABLED = "APPROVAL_DISABLED"


class GateStatus(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
