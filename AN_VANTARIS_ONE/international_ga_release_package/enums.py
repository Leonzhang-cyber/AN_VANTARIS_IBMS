"""Enums for International GA release candidate packages."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "international-ga-release-candidate-package.v1"


class PackageStatus(str, Enum):
    INTERNATIONAL_GA_RELEASE_PACKAGE_READY = "INTERNATIONAL_GA_RELEASE_PACKAGE_READY"
    READY_WITH_WARNINGS = "READY_WITH_WARNINGS"
    BLOCKED = "BLOCKED"
    NOT_READY = "NOT_READY"


class GateStatus(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ReleaseDecisionState(str, Enum):
    INTERNATIONAL_GA_RELEASE_PACKAGE_PASS = "INTERNATIONAL_GA_RELEASE_PACKAGE_PASS"
    INTERNATIONAL_GA_RELEASE_PACKAGE_PASS_WITH_WARNINGS = "INTERNATIONAL_GA_RELEASE_PACKAGE_PASS_WITH_WARNINGS"
    BLOCKED = "BLOCKED"
    NOT_READY = "NOT_READY"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
