"""Enums for API / Frontend readiness contracts."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "api-frontend-readiness-contract.v1"


class ContractState(str, Enum):
    FROZEN_FOR_PLANNING = "FROZEN_FOR_PLANNING"
    READY_FOR_IMPLEMENTATION_PLANNING = "READY_FOR_IMPLEMENTATION_PLANNING"
    BLOCKED = "BLOCKED"
    NOT_READY = "NOT_READY"


class ImplementationPermission(str, Enum):
    NOT_ALLOWED_IN_THIS_TASK = "NOT_ALLOWED_IN_THIS_TASK"
    FUTURE_TASK_REQUIRED = "FUTURE_TASK_REQUIRED"
    BLOCKED = "BLOCKED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


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
