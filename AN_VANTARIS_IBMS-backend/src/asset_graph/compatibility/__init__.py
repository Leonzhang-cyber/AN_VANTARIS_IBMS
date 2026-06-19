"""READ_ONLY legacy Device compatibility facade exports."""
from .constants import (
    MAPPING_VERSION, MAX_BATCH_SIZE, MappingDisposition, ProjectionCategory,
    READ_ONLY_COMPATIBILITY_FACADE, TEMPORARY_LEGACY_SOURCE,
)
from .facade import LegacyDeviceReadCompatibilityFacade
from .models import (
    BatchProjectionResult, LegacyDeviceSnapshot, LegacyFieldSnapshot,
    MappingDecision, ProjectionAuditMetadata, ProjectionContext,
    ProjectionResult, UnresolvedRelationship,
)
from .read_port import FixtureLegacyDeviceReadPort, LegacyDeviceReadPort, LegacyReadQuery

__all__ = [
    "BatchProjectionResult", "FixtureLegacyDeviceReadPort",
    "LegacyDeviceReadCompatibilityFacade", "LegacyDeviceReadPort",
    "LegacyDeviceSnapshot", "LegacyFieldSnapshot", "LegacyReadQuery",
    "MAPPING_VERSION", "MAX_BATCH_SIZE", "MappingDecision",
    "MappingDisposition", "ProjectionAuditMetadata", "ProjectionCategory",
    "ProjectionContext", "ProjectionResult", "READ_ONLY_COMPATIBILITY_FACADE",
    "TEMPORARY_LEGACY_SOURCE", "UnresolvedRelationship",
]
