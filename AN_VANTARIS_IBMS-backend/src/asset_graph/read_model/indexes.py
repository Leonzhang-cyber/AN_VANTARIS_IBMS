"""Immutable read model indexes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Tuple

from ..models import AssetRelationship, Device, Point, Tag


@dataclass(frozen=True)
class ReadModelIndexes:
    devices_by_global_id: Mapping[str, Device]
    points_by_global_id: Mapping[str, Point]
    tags_by_key: Mapping[str, Tag]
    relationships_by_global_id: Mapping[str, AssetRelationship]
    points_by_device_global_id: Mapping[str, Tuple[str, ...]]
    relationships_by_source_global_id: Mapping[str, Tuple[str, ...]]
    relationships_by_target_global_id: Mapping[str, Tuple[str, ...]]

    def device_ids(self) -> Tuple[str, ...]:
        return tuple(sorted(self.devices_by_global_id))

    def point_ids(self) -> Tuple[str, ...]:
        return tuple(sorted(self.points_by_global_id))

    def tag_keys(self) -> Tuple[str, ...]:
        return tuple(sorted(self.tags_by_key))

    def relationship_ids(self) -> Tuple[str, ...]:
        return tuple(sorted(self.relationships_by_global_id))
