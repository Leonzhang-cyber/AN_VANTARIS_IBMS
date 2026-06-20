"""Controlled states for WorkOrderIntent candidate projections."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "workorder-intent-candidate-projection.v1"


class WorkOrderIntentEligibilityState(str, Enum):
    ELIGIBLE_FOR_REVIEW = "ELIGIBLE_FOR_REVIEW"
    BLOCKED_BY_FAULTCASE_REVIEW = "BLOCKED_BY_FAULTCASE_REVIEW"
    BLOCKED_BY_RESOLUTION = "BLOCKED_BY_RESOLUTION"
    BLOCKED_BY_SOURCE_SYSTEM_REVIEW = "BLOCKED_BY_SOURCE_SYSTEM_REVIEW"
    BLOCKED_BY_POLICY = "BLOCKED_BY_POLICY"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


class ProposedWorkOrderIntentType(str, Enum):
    CORRECTIVE_MAINTENANCE = "CORRECTIVE_MAINTENANCE"
    INSPECTION_REQUEST = "INSPECTION_REQUEST"
    INVESTIGATION_REQUEST = "INVESTIGATION_REQUEST"
    OPERATOR_FOLLOWUP = "OPERATOR_FOLLOWUP"
    UNKNOWN = "UNKNOWN"


class ProposedMaintenanceType(str, Enum):
    CORRECTIVE = "CORRECTIVE"
    INSPECTION = "INSPECTION"
    INVESTIGATION = "INVESTIGATION"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"


class ProposedPriority(str, Enum):
    P1_CRITICAL = "P1_CRITICAL"
    P2_HIGH = "P2_HIGH"
    P3_MEDIUM = "P3_MEDIUM"
    P4_LOW = "P4_LOW"
    UNKNOWN = "UNKNOWN"


class ProposedTradeDiscipline(str, Enum):
    SECURITY = "SECURITY"
    ELV = "ELV"
    COMMUNICATION = "COMMUNICATION"
    MEP = "MEP"
    FACILITY = "FACILITY"
    UNKNOWN = "UNKNOWN"


class ProposedExecutionOwner(str, Enum):
    ONE_WORK_MANAGEMENT = "ONE_WORK_MANAGEMENT"
    UMMS = "UMMS"
    OPERATOR_REVIEW = "OPERATOR_REVIEW"
    UNASSIGNED = "UNASSIGNED"


class ProposedSlaClass(str, Enum):
    EMERGENCY = "EMERGENCY"
    URGENT = "URGENT"
    STANDARD = "STANDARD"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class DownstreamCreationState(str, Enum):
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    NOT_CREATED = "NOT_CREATED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
