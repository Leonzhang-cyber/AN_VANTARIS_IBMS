"""Enums for read-only API skeleton contracts."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "read-only-api-skeleton.v1"


class ApiImplementationState(str, Enum):
    SKELETON_DEFINED = "SKELETON_DEFINED"
    CONTRACT_ONLY = "CONTRACT_ONLY"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    BLOCKED = "BLOCKED"


class AuthPolicy(str, Enum):
    AUTH_REQUIRED = "AUTH_REQUIRED"
    ROLE_POLICY_REQUIRED = "ROLE_POLICY_REQUIRED"
    NOT_DEFINED = "NOT_DEFINED"


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
