"""Frozen constants for airport classification profile."""
from __future__ import annotations

AUTHORITY = "ONE-AIRPORT-A1-03"
PROFILE_ID = "airport-classification-v1"
PROFILE_NAME = "VANTARIS ONE Airport System and Device Classification Profile"
PROFILE_VERSION = "1.0.0"
IMPLEMENTATION_MODE = "READ_ONLY_CLASSIFICATION"

COMPATIBLE_INTAKE_AUTHORITY = "ONE-AIRPORT-A1-01"
COMPATIBLE_INTAKE_EVIDENCE_VERSION = "1.0.0"
COMPATIBLE_INTAKE_EXECUTION_MODE = "OFFLINE_READ_ONLY"
COMPATIBLE_INTAKE_READINESS = frozenset(
    {
        "INTAKE_COMPLETE_WITH_REVIEWS",
        "READY_FOR_AIRPORT_ASSET_RECONCILIATION",
    }
)

COMPATIBLE_SPATIAL_AUTHORITY = "ONE-AIRPORT-A1-02"
COMPATIBLE_SPATIAL_READINESS = frozenset(
    {
        "SPATIAL_MAPPING_COMPLETE_WITH_REVIEWS",
        "READY_FOR_AIRPORT_ASSET_RECONCILIATION",
    }
)

FORBIDDEN_READINESS = frozenset(
    {
        "READY_FOR_DATABASE_IMPORT",
        "READY_FOR_CANONICAL_WRITE",
        "READY_FOR_WRITE_CUTOVER",
    }
)

READINESS_OUTCOMES = frozenset(
    {
        "CLASSIFICATION_BLOCKED",
        "CLASSIFICATION_COMPLETE_WITH_REVIEWS",
        "READY_FOR_AIRPORT_ASSET_RECONCILIATION",
    }
)

KNOWN_SOURCE_NAMESPACES = frozenset({"SCN"})

EMBEDDED_SYSTEM_ALIAS_CANDIDATES: dict[str, str] = {
    "CCT": "CCTV",
    "PAS": "PA",
}

APPROVED_EMBEDDED_ALIASES: dict[str, str] = {}

INDUSTRY_TO_GENERIC: dict[str, tuple[str, str]] = {
    "CCTV": ("CCTV", "VIDEO_SURVEILLANCE"),
    "PA": ("PA", "PUBLIC_ADDRESS"),
    "ACS": ("ACS", "ACCESS_CONTROL"),
    "RAS": ("RAS", "RADIO_COMMUNICATION"),
    "TEL": ("TEL", "TELECOMMUNICATION"),
}

EXACT_INDUSTRY_CODES = frozenset(INDUSTRY_TO_GENERIC)

DEVICE_TYPE_DEFINITIONS: dict[str, dict[str, str]] = {
    "FCT": {"label": "Fixed Camera", "genericDeviceClass": "CAMERA"},
    "PCT": {"label": "PTZ Camera", "genericDeviceClass": "CAMERA"},
    "TEL": {"label": "IP Telephone", "genericDeviceClass": "TELEPHONE"},
    "ANT": {"label": "Radio Antenna", "genericDeviceClass": "ANTENNA"},
    "10DC": {"label": "Directional Coupler", "genericDeviceClass": "COUPLER"},
    "6DC": {"label": "Directional Coupler", "genericDeviceClass": "COUPLER"},
    "2LS": {"label": "Two-Way Splitter", "genericDeviceClass": "SPLITTER"},
    "3LS": {"label": "Three-Way Splitter", "genericDeviceClass": "SPLITTER"},
    "ADCP": {"label": "Intelligent Controller", "genericDeviceClass": "CONTROLLER"},
    "DC1": {"label": "Electromagnetic Lock", "genericDeviceClass": "LOCK"},
    "DC2": {"label": "Electromagnetic Lock", "genericDeviceClass": "LOCK"},
    "EML/DC1": {"label": "Electromagnetic Lock", "genericDeviceClass": "LOCK"},
    "EML/DC2": {"label": "Electromagnetic Lock", "genericDeviceClass": "LOCK"},
    "BG": {"label": "Emergency Break Glass", "genericDeviceClass": "BREAK_GLASS"},
    "PB": {"label": "Push Button", "genericDeviceClass": "PUSH_BUTTON"},
    "INCR": {"label": "In Card Reader", "genericDeviceClass": "CARD_READER"},
    "OTCR": {"label": "Out Card Reader", "genericDeviceClass": "CARD_READER"},
    "HSP": {"label": "Horn Speaker", "genericDeviceClass": "SPEAKER"},
    "PSP": {"label": "Projection Speaker", "genericDeviceClass": "SPEAKER"},
    "CSP": {"label": "Ceiling Speaker", "genericDeviceClass": "SPEAKER"},
    "BSP": {"label": "Box Speaker", "genericDeviceClass": "SPEAKER"},
    "ONI": {"label": "Omneo Interface", "genericDeviceClass": "INTERFACE"},
    "NCO": {"label": "Network Controller", "genericDeviceClass": "NETWORK_CONTROLLER"},
    "AMP": {"label": "Amplifier", "genericDeviceClass": "AMPLIFIER"},
    "NOS": {"label": "Noise Sensor", "genericDeviceClass": "SENSOR"},
    "STAMP": {"label": "Standby Amplifier", "genericDeviceClass": "AMPLIFIER"},
    "LTV": {"label": "IPTV Endpoint", "genericDeviceClass": "ENDPOINT"},
    "OUT": {"label": "Outlet", "genericDeviceClass": "OUTLET"},
}

SYSTEM_DEVICE_COMPATIBILITY: dict[str, frozenset[str]] = {
    "VIDEO_SURVEILLANCE": frozenset({"FCT", "PCT"}),
    "ACCESS_CONTROL": frozenset({"ADCP", "DC1", "DC2", "EML/DC1", "EML/DC2", "BG", "PB", "INCR", "OTCR"}),
    "PUBLIC_ADDRESS": frozenset({"HSP", "PSP", "CSP", "BSP", "ONI", "NCO", "AMP", "NOS", "STAMP"}),
    "TELECOMMUNICATION": frozenset({"TEL"}),
    "RADIO_COMMUNICATION": frozenset({"ANT", "10DC", "6DC", "2LS", "3LS"}),
}

DEVICE_TYPE_ALIASES: dict[str, str] = {}
