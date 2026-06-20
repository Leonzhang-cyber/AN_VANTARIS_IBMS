"""Enums for International GA final local verification."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "international-ga-final-local-verification.v1"


class VerificationStatus(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class FinalDecisionState(str, Enum):
    INTERNATIONAL_GA_LOCAL_VERIFICATION_PASS = "INTERNATIONAL_GA_LOCAL_VERIFICATION_PASS"
    INTERNATIONAL_GA_LOCAL_VERIFICATION_PASS_WITH_WARNINGS = "INTERNATIONAL_GA_LOCAL_VERIFICATION_PASS_WITH_WARNINGS"
    BLOCKED = "BLOCKED"
    NOT_READY = "NOT_READY"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
