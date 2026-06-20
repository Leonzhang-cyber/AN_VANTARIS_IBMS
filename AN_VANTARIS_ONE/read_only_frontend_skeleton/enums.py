"""Enums for read-only frontend skeleton contracts."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "read-only-frontend-skeleton.v1"


class FrontendImplementationState(str, Enum):
    SKELETON_DEFINED = "SKELETON_DEFINED"
    CONTRACT_ONLY = "CONTRACT_ONLY"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    BLOCKED = "BLOCKED"


class ComponentType(str, Enum):
    PAGE_CONTAINER = "PAGE_CONTAINER"
    SUMMARY_CARD = "SUMMARY_CARD"
    DATA_TABLE = "DATA_TABLE"
    REVIEW_QUEUE = "REVIEW_QUEUE"
    STATUS_PANEL = "STATUS_PANEL"
    FILTER_PANEL = "FILTER_PANEL"
    CHART_PLACEHOLDER = "CHART_PLACEHOLDER"
    REPORT_PANEL = "REPORT_PANEL"


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
