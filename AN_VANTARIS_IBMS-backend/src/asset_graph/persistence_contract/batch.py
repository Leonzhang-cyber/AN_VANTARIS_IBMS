"""Batch boundary validation."""
from __future__ import annotations

from collections import Counter
from typing import Mapping, Sequence

from .commands import CreateCanonicalDevice, CreateCanonicalPoint, CreateCanonicalRelationship, CreateCanonicalTag, PersistenceCommand
from .errors import PersistenceBatchLimitError


def validate_batch_limits(commands: Sequence[PersistenceCommand], limits: Mapping[str, int]) -> None:
    if len(commands) > limits["maximumCommandsPerBatch"]:
        raise PersistenceBatchLimitError("command batch exceeds maximumCommandsPerBatch")
    device_count = sum(1 for command in commands if isinstance(command, CreateCanonicalDevice))
    if device_count > limits["maximumDevicesPerUnitOfWork"]:
        raise PersistenceBatchLimitError("device count exceeds maximumDevicesPerUnitOfWork")
    tag_count = sum(1 for command in commands if isinstance(command, CreateCanonicalTag))
    if tag_count > limits["maximumTagsPerUnitOfWork"]:
        raise PersistenceBatchLimitError("tag count exceeds maximumTagsPerUnitOfWork")
    relationship_count = sum(1 for command in commands if isinstance(command, CreateCanonicalRelationship))
    if relationship_count > limits["maximumRelationshipsPerUnitOfWork"]:
        raise PersistenceBatchLimitError("relationship count exceeds maximumRelationshipsPerUnitOfWork")
    points_by_device: Counter[str] = Counter()
    for command in commands:
        if isinstance(command, CreateCanonicalPoint):
            points_by_device[command.device_global_id] += 1
    if points_by_device and max(points_by_device.values()) > limits["maximumPointsPerDevice"]:
        raise PersistenceBatchLimitError("point count exceeds maximumPointsPerDevice")
