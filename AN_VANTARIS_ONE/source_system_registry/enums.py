"""Controlled enumerations for the generic source-system registry."""
from __future__ import annotations

from enum import Enum


class RegistryLifecycleState(str, Enum):
    CANDIDATE = "CANDIDATE"
    REGISTERED = "REGISTERED"
    SUSPENDED = "SUSPENDED"
    RETIRED = "RETIRED"


class RegistryApprovalState(str, Enum):
    DRAFT = "DRAFT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class DeclarationState(str, Enum):
    DECLARED = "DECLARED"
    UNDECLARED = "UNDECLARED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class VerificationState(str, Enum):
    NOT_VERIFIED = "NOT_VERIFIED"
    EVIDENCE_SUPPORTED = "EVIDENCE_SUPPORTED"
    VERIFIED = "VERIFIED"
    CONFLICTED = "CONFLICTED"


class IntegrationDirection(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"
    BIDIRECTIONAL = "BIDIRECTIONAL"
    UNDECLARED = "UNDECLARED"


GENERIC_SYSTEM_CATEGORIES = frozenset(
    {
        "VIDEO_SURVEILLANCE",
        "ACCESS_CONTROL",
        "PUBLIC_ADDRESS",
        "RADIO_COMMUNICATION",
        "TELECOMMUNICATION",
        "BUILDING_AUTOMATION",
        "ENERGY_MANAGEMENT",
        "SECURITY",
        "INSPECTION",
        "CUSTOMER_FEEDBACK",
        "MAINTENANCE_MANAGEMENT",
        "OTHER_CONTROLLED",
    }
)

FORBIDDEN_LIFECYCLE_STATES_FOR_CANDIDATES = frozenset({"ACTIVE"})
