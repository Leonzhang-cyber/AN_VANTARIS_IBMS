"""Enums for International GA handoff notes."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "international-ga-handoff-notes.v1"


class HandoffStatus(str, Enum):
    HANDOFF_NOTES_FROZEN = "HANDOFF_NOTES_FROZEN"
    READY_FOR_HANDOFF = "READY_FOR_HANDOFF"
    READY_WITH_WARNINGS = "READY_WITH_WARNINGS"
    BLOCKED = "BLOCKED"


class Audience(str, Enum):
    PRODUCT_OWNER = "PRODUCT_OWNER"
    ENGINEERING = "ENGINEERING"
    API_TEAM = "API_TEAM"
    FRONTEND_TEAM = "FRONTEND_TEAM"
    QA_VALIDATION = "QA_VALIDATION"
    DEPLOYMENT_TEAM = "DEPLOYMENT_TEAM"
    CUSTOMER_TECHNICAL_REVIEW = "CUSTOMER_TECHNICAL_REVIEW"


class WarningSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class GateStatus(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"
