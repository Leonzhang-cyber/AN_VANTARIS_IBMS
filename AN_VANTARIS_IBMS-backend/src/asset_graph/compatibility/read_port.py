"""Narrow READ_ONLY legacy Device source port."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .models import LegacyDeviceSnapshot, LegacyFieldSnapshot


@dataclass(frozen=True)
class LegacyReadQuery:
    tenant_id: str
    site_id: Optional[str] = None
    limit: int = 50
    cursor: Optional[str] = None


class LegacyDeviceReadPort(ABC):
    @abstractmethod
    def get_legacy_device_by_id(
        self, source_id: str, tenant_id: str, site_id: Optional[str] = None,
    ) -> Optional[LegacyDeviceSnapshot]: ...

    @abstractmethod
    def list_legacy_devices(self, query: LegacyReadQuery) -> Tuple[LegacyDeviceSnapshot, ...]: ...

    @abstractmethod
    def list_legacy_fields_for_device(
        self, source_id: str, tenant_id: str, site_id: Optional[str] = None,
    ) -> Tuple[LegacyFieldSnapshot, ...]: ...


class FixtureLegacyDeviceReadPort(LegacyDeviceReadPort):
    """Deterministic test fixture. It has no write or mutation methods."""

    def __init__(
        self,
        devices: Tuple[LegacyDeviceSnapshot, ...] = (),
        fields: Optional[Dict[str, Tuple[LegacyFieldSnapshot, ...]]] = None,
    ) -> None:
        self._devices = tuple(sorted(devices, key=lambda item: item.source_id))
        self._fields = {
            key: tuple(sorted(value, key=lambda item: item.source_id))
            for key, value in (fields or {}).items()
        }

    def get_legacy_device_by_id(self, source_id, tenant_id, site_id=None):
        del tenant_id, site_id
        return next((item for item in self._devices if item.source_id == source_id), None)

    def list_legacy_devices(self, query):
        if not query.tenant_id:
            raise ValueError("tenant_id is required")
        if query.limit < 1 or query.limit > 100:
            raise ValueError("limit must be between 1 and 100")
        start = int(query.cursor or "0")
        return self._devices[start:start + query.limit]

    def list_legacy_fields_for_device(self, source_id, tenant_id, site_id=None):
        del tenant_id, site_id
        return self._fields.get(source_id, ())
