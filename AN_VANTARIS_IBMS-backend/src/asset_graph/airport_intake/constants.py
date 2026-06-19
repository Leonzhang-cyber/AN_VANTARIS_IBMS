"""Frozen constants for airport asset Excel intake profile."""
from __future__ import annotations

AUTHORITY = "ONE-AIRPORT-A1-01"
EVIDENCE_NAME = "VANTARIS ONE Airport Asset Excel Intake Evidence"
EVIDENCE_VERSION = "1.0.0"
EVIDENCE_CLASSIFICATION = "REAL_CUSTOMER_ASSET_DATA_SANITIZED_ASSESSMENT"
EXECUTION_MODE = "OFFLINE_READ_ONLY"

REQUIRED_WORKSHEETS = ("Zone-1", "Zone-2")
BUSINESS_WORKSHEETS = REQUIRED_WORKSHEETS

ASSET_MASTER_COLUMNS = (
    "SL",
    "Device ID",
    "Building",
    "Level",
    "Zone",
    "DA",
    "System",
    "Area",
    "Location",
    "Device Type",
)

MAINTENANCE_EXTENSION_COLUMNS = (
    "Day",
    "Keys Number",
    "Scissor Lift",
    "Mobile Scaffold",
    "Last Done",
    "Due Date",
    "Status",
    "Overdue",
    "Remarks",
)

ALL_KNOWN_COLUMNS = ASSET_MASTER_COLUMNS + MAINTENANCE_EXTENSION_COLUMNS

CANONICAL_HEADER_MAP = {
    "sl": "SL",
    "device id": "Device ID",
    "building": "Building",
    "level": "Level",
    "zone": "Zone",
    "da": "DA",
    "system": "System",
    "area": "Area",
    "location": "Location",
    "device type": "Device Type",
    "day": "Day",
    "keys number": "Keys Number",
    "scissor lift": "Scissor Lift",
    "mobile scaffold": "Mobile Scaffold",
    "last done": "Last Done",
    "due date": "Due Date",
    "status": "Status",
    "overdue": "Overdue",
    "remarks": "Remarks",
}

REQUIRED_ASSET_COLUMNS = ASSET_MASTER_COLUMNS
OPTIONAL_MAINTENANCE_COLUMNS = MAINTENANCE_EXTENSION_COLUMNS

MAX_SOURCE_ROWS = 10000

EXPECTED_SOURCE_PROFILE = {
    "assetRowsApprox": 470,
    "worksheetDistribution": {
        "Zone-1": 183,
        "Zone-2": 287,
    },
    "expectedSystems": ("PA", "ACS", "CCTV", "RAS", "TEL"),
    "expectedBuildings": ("TE3",),
    "expectedLevels": ("BAS", "GRD", "1ST", "2ND"),
    "expectedZones": ("Z1", "Z2"),
    "expectedDistributionAreas": ("DA21", "DA31"),
}

KNOWN_SYSTEM_ALIASES = {
    "CCT": "CCTV",
    "CCTV": "CCTV",
    "PAS": "PA",
    "PA": "PA",
    "ACS": "ACS",
    "RAS": "RAS",
    "TEL": "TEL",
}

WEEKDAY_TOKENS = frozenset(
    {
        "MON",
        "MONDAY",
        "TUE",
        "TUESDAY",
        "WED",
        "WEDNESDAY",
        "THU",
        "THURSDAY",
        "FRI",
        "FRIDAY",
        "SAT",
        "SATURDAY",
        "SUN",
        "SUNDAY",
    }
)

READINESS_OUTCOMES = frozenset(
    {
        "INPUT_REJECTED",
        "INTAKE_BLOCKED",
        "INTAKE_COMPLETE_WITH_REVIEWS",
        "READY_FOR_AIRPORT_ASSET_RECONCILIATION",
    }
)

FORBIDDEN_READINESS_OUTCOMES = frozenset(
    {
        "READY_FOR_DATABASE_IMPORT",
        "READY_FOR_CANONICAL_WRITE",
        "READY_FOR_WRITE_CUTOVER",
    }
)

PRIVACY_PATTERNS = (
    ("CREDENTIAL", r"(?i)(password|passwd|pwd\s*[:=]|api[_-]?key|secret[_-]?key|token\s*[:=])"),
    ("PRIVATE_KEY", r"(?i)-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ("CONNECTION_STRING", r"(?i)(jdbc:|mongodb(\+srv)?:|postgres(ql)?://|mysql://|Server=.*;Database=)"),
    ("EMAIL", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    ("PHONE", r"(?i)(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}"),
    ("TELEMETRY_PAYLOAD", r"(?i)(telemetry|live_value|point_value|tag_value)\s*[:=]"),
    ("COMMAND_PAYLOAD", r"(?i)(exec\s*\(|system\s*\(|subprocess|shell\s*command)"),
)

PLACEHOLDER_AIRPORT = "AIRPORT-CONTEXT-REQUIRED"
PLACEHOLDER_TERMINAL = "TERMINAL-CONTEXT-REQUIRED"
