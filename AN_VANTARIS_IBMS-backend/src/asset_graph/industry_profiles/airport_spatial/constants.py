"""Frozen constants for airport spatial hierarchy profile."""
from __future__ import annotations

AUTHORITY = "ONE-AIRPORT-A1-02"
PROFILE_ID = "airport-spatial-v1"
PROFILE_NAME = "VANTARIS ONE Airport Spatial Hierarchy Profile"
MAPPING_VERSION = "airport-spatial-v1"
IMPLEMENTATION_MODE = "READ_ONLY_MAPPING"

COMPATIBLE_INTAKE_AUTHORITY = "ONE-AIRPORT-A1-01"
COMPATIBLE_INTAKE_EVIDENCE_VERSION = "1.0.0"
COMPATIBLE_INTAKE_EXECUTION_MODE = "OFFLINE_READ_ONLY"
COMPATIBLE_INTAKE_READINESS = frozenset(
    {
        "INTAKE_COMPLETE_WITH_REVIEWS",
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

WILDCARD_TOKENS = frozenset({"*", "ALL", "ALL_SITES", "ANY_SITE", "ANY", "WILDCARD"})

MAX_TERMINALS = 50
MAX_BUILDINGS = 500
MAX_LEVELS = 5000
MAX_ZONES = 10000
MAX_DISTRIBUTION_AREAS = 10000

PLACEHOLDER_AIRPORT = "AIRPORT-CONTEXT-REQUIRED"
PLACEHOLDER_TERMINAL = "TERMINAL-CONTEXT-REQUIRED"

GENERIC_TO_AIRPORT = {
    "Airport": {"genericTarget": "Site", "alternateGenericTarget": "SiteGroup"},
    "Terminal": {"genericTarget": "Facility", "alternateGenericTarget": "BuildingGroup"},
    "Building": {"genericTarget": "Building"},
    "Level": {"genericTarget": "Level"},
    "AirportZone": {"genericTarget": "Zone"},
    "DistributionArea": {"genericTarget": "ZoneExtension", "alternateGenericTarget": "SpatialGrouping"},
    "Location": {"genericTarget": "Space", "alternateGenericTarget": "Location"},
    "Device": {"genericTarget": "Device"},
}

GENERIC_RELATIONSHIP_SEMANTICS = frozenset({"CONTAINS", "LOCATED_IN", "ASSIGNED_TO", "BELONGS_TO"})

SHEET_ZONE_HINTS = {
    "Zone-1": "Z1",
    "Zone-2": "Z2",
}

READINESS_OUTCOMES = frozenset(
    {
        "SPATIAL_MAPPING_BLOCKED",
        "SPATIAL_MAPPING_COMPLETE_WITH_REVIEWS",
        "READY_FOR_AIRPORT_ASSET_RECONCILIATION",
    }
)
