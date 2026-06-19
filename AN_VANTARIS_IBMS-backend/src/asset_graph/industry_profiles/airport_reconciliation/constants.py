"""Frozen constants for airport asset reconciliation profile."""
from __future__ import annotations

AUTHORITY = "ONE-AIRPORT-A1-04"
PROFILE_ID = "airport-asset-reconciliation-v1"
PROFILE_NAME = "VANTARIS ONE Airport Asset Reconciliation Profile"
PROFILE_VERSION = "1.0.0"
IMPLEMENTATION_MODE = "READ_ONLY_RECONCILIATION"

INTAKE_AUTHORITY = "ONE-AIRPORT-A1-01"
SPATIAL_AUTHORITY = "ONE-AIRPORT-A1-02"
CLASSIFICATION_AUTHORITY = "ONE-AIRPORT-A1-03"
COVERAGE_AUTHORITY = "ONE-AIRPORT-A1-03A"

COMPATIBLE_INTAKE_READINESS = frozenset(
    {"INTAKE_COMPLETE_WITH_REVIEWS", "READY_FOR_AIRPORT_ASSET_RECONCILIATION"}
)
COMPATIBLE_SPATIAL_READINESS = frozenset(
    {"SPATIAL_MAPPING_COMPLETE_WITH_REVIEWS", "READY_FOR_AIRPORT_ASSET_RECONCILIATION"}
)
COMPATIBLE_CLASSIFICATION_READINESS = frozenset(
    {"CLASSIFICATION_COMPLETE_WITH_REVIEWS", "READY_FOR_AIRPORT_ASSET_RECONCILIATION"}
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
        "RECONCILIATION_BLOCKED",
        "RECONCILIATION_COMPLETE_WITH_REVIEWS",
        "READY_FOR_CONTROLLED_CANONICAL_PROPOSAL_REVIEW",
    }
)

LABEL_NORMALIZATION_CANDIDATES: dict[str, dict[str, str]] = {
    "Electro Magnetic Lock": {
        "normalizedLabel": "Electromagnetic Lock",
        "classification": "LABEL_SEMANTIC_EQUIVALENCE_CANDIDATE",
        "deviceTypeCode": "EML/DC1",
    },
    "Electro Magnetic Lock ": {
        "normalizedLabel": "Electromagnetic Lock",
        "classification": "LABEL_SEMANTIC_EQUIVALENCE_CANDIDATE",
        "deviceTypeCode": "EML/DC1",
    },
}

LABEL_PREFIX_NORMALIZATIONS: tuple[tuple[str, str, str], ...] = (
    ("10 db Directional Coupler", "Directional Coupler", "10DC"),
    ("6 db Directional Coupler", "Directional Coupler", "6DC"),
    ("2-Way Splitter", "Two-Way Splitter", "2LS"),
    ("3-Way Splitter", "Three-Way Splitter", "3LS"),
)

SYSTEM_ALIAS_PROPOSALS: tuple[tuple[str, str, str], ...] = (
    ("CCT", "CCTV", "VIDEO_SURVEILLANCE"),
    ("PAS", "PA", "PUBLIC_ADDRESS"),
)

SOURCE_NAMESPACE_PROPOSALS: tuple[tuple[str, str], ...] = (("SCN", "SOURCE_NAMESPACE_SEMANTIC_REVIEW"),)

GATE_IDS = (
    "G01_INPUT_EVIDENCE_INTEGRITY",
    "G02_RECORD_COUNT_ALIGNMENT",
    "G03_SPATIAL_BINDING_COVERAGE",
    "G04_CLASSIFICATION_EVIDENCE_COVERAGE",
    "G05_DUPLICATE_IDENTITY_REVIEW",
    "G06_SYSTEM_ALIAS_APPROVAL",
    "G07_SOURCE_NAMESPACE_APPROVAL",
    "G08_DEVICE_LABEL_NORMALIZATION",
    "G09_LOCATION_RECONCILIATION",
    "G10_CONTEXT_APPROVAL",
    "G11_CANONICAL_PROPOSAL_COMPLETENESS",
    "G12_WRITE_BOUNDARY_ENFORCEMENT",
)
