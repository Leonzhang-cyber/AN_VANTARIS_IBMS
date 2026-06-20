"""Enums for read-only API response contracts."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "read-only-api-response-contract.v1"


class ResponseShape(str, Enum):
    STANDARD_PROJECTION_ENVELOPE = "STANDARD_PROJECTION_ENVELOPE"
    PAGINATED_PROJECTION_ENVELOPE = "PAGINATED_PROJECTION_ENVELOPE"
    SUMMARY_PROJECTION_ENVELOPE = "SUMMARY_PROJECTION_ENVELOPE"


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
