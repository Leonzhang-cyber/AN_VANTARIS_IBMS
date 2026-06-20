"""Enums for read-only API mock route contracts."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "read-only-api-mock-route-contract.v1"


class RouteMode(str, Enum):
    MOCK_CONTRACT_ONLY = "MOCK_CONTRACT_ONLY"
    LOCAL_SMOKE_ONLY = "LOCAL_SMOKE_ONLY"
    PRODUCTION_DISABLED = "PRODUCTION_DISABLED"


class MockResponseShape(str, Enum):
    STANDARD_PROJECTION_ENVELOPE = "STANDARD_PROJECTION_ENVELOPE"
    PAGINATED_PROJECTION_ENVELOPE = "PAGINATED_PROJECTION_ENVELOPE"
    SUMMARY_PROJECTION_ENVELOPE = "SUMMARY_PROJECTION_ENVELOPE"
    STANDARD_ERROR_ENVELOPE = "STANDARD_ERROR_ENVELOPE"


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
