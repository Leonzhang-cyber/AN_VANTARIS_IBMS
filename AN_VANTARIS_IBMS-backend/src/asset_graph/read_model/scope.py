"""Bounded read scope enforcement."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .errors import ScopeViolationError

WILDCARD_TOKENS = frozenset({"*", "ALL", "ALL_SITES", "ANY", "ANY_SITE", "ANY_SOURCE_SYSTEM"})
MAX_SITES = 100
MAX_SOURCE_SYSTEMS = 50


@dataclass(frozen=True)
class ReadScope:
    tenant_id: str
    allowed_site_ids: Tuple[str, ...]
    allowed_source_system_ids: Tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.tenant_id or self.tenant_id.strip() in WILDCARD_TOKENS:
            raise ScopeViolationError("tenantId must be explicit")
        if not self.allowed_site_ids:
            raise ScopeViolationError("allowedSiteIds must not be empty")
        if not self.allowed_source_system_ids:
            raise ScopeViolationError("allowedSourceSystemIds must not be empty")
        if len(self.allowed_site_ids) > MAX_SITES:
            raise ScopeViolationError("allowedSiteIds exceeds maximum")
        if len(self.allowed_source_system_ids) > MAX_SOURCE_SYSTEMS:
            raise ScopeViolationError("allowedSourceSystemIds exceeds maximum")
        for site in self.allowed_site_ids:
            if site in WILDCARD_TOKENS:
                raise ScopeViolationError("wildcard site scope is prohibited")
        for source_system in self.allowed_source_system_ids:
            if source_system in WILDCARD_TOKENS:
                raise ScopeViolationError("wildcard source-system scope is prohibited")

    def allows(self, *, tenant_id: str, site_id: str | None, source_system_id: str | None) -> bool:
        if tenant_id != self.tenant_id:
            return False
        if site_id and site_id not in self.allowed_site_ids:
            return False
        if source_system_id and source_system_id not in self.allowed_source_system_ids:
            return False
        return True

    def serialize(self) -> dict[str, object]:
        return {
            "tenantId": self.tenant_id,
            "allowedSiteIds": list(self.allowed_site_ids),
            "allowedSourceSystemIds": list(self.allowed_source_system_ids),
        }
