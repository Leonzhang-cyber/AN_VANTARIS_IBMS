"""Materialize in-memory reconciliation runs for validated read-model construction."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Tuple

from ...compatibility import LegacyDeviceReadCompatibilityFacade
from ...compatibility.models import ProjectionContext
from ..constants import MAX_RECONCILIATION_BATCH_SIZE
from ..engine import DeviceProjectionReconciliationService
from ..evidence.runner import (
    EvidencePackageError,
    SAFE_ID,
    _build_context,
    _ensure_safe_identifier,
    _normalize_devices,
    _normalize_standard_fields,
    _record_prohibited_scan,
    _validate_top_level,
)
from ..models import ReconciliationInput, ReconciliationRun


def materialize_reconciliation_run(
    *,
    root: Path,
    source_path: Path,
    run_id: str,
) -> Tuple[ReconciliationRun, ReconciliationInput, ProjectionContext]:
    if not run_id or not SAFE_ID.match(run_id):
        raise EvidencePackageError("INVALID_RUN_ID", "run-id is required and must be a safe identifier")
    package = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(package, Mapping):
        raise EvidencePackageError("INVALID_PACKAGE", "input package must be a JSON object")
    _validate_top_level(package)
    devices_raw = package["devices"]
    fields_raw = package["standardFields"]
    _record_prohibited_scan(devices_raw, fields_raw)
    context = _build_context(package)
    mapping_version = str(package.get("mappingVersion", "")).strip()
    _ensure_safe_identifier(mapping_version, "mappingVersion")
    if len(devices_raw) > MAX_RECONCILIATION_BATCH_SIZE:
        raise EvidencePackageError("BATCH_LIMIT_EXCEEDED", "device batch exceeds allowed maximum")
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    devices, _ = _normalize_devices(package, context, now)
    fields_by_device, _ = _normalize_standard_fields(package, context)
    reconciliation_input = ReconciliationInput(
        devices=tuple(devices),
        fields_by_device=fields_by_device,
        context=context,
        mapping_version=mapping_version,
        projection_configuration=tuple(),
    )
    service = DeviceProjectionReconciliationService(facade=LegacyDeviceReadCompatibilityFacade())
    run = service.reconcile_batch(run_id=run_id, reconciliation_input=reconciliation_input)
    return run, reconciliation_input, context
