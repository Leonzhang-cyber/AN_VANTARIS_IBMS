#!/usr/bin/env python3
"""Synthetic intake evidence fixtures for airport spatial profile tests."""
from __future__ import annotations

import json
from pathlib import Path

from src.asset_graph.reconciliation.models import sha256_digest

AUTHORITY = "ONE-AIRPORT-A1-01"
WORKBOOK_DIGEST = "synthetic-workbook-digest-for-spatial-tests"


def _device(
    source_id: str,
    *,
    worksheet: str = "Zone-1",
    row: int = 2,
    building: str = "TE3",
    level: str = "BAS",
    zone: str = "Z1",
    da: str = "DA21",
    location: str = "FIRE EXIT CORRIDOR",
    system: str = "CCT",
) -> dict:
    normalized = location.strip().upper()
    return {
        "sourceId": source_id,
        "deviceCode": source_id,
        "buildingCode": building,
        "levelCode": level,
        "zoneCode": zone,
        "distributionAreaCode": da,
        "sourceSystemCode": system,
        "locationName": location,
        "normalizedLocation": normalized,
        "sourceWorksheet": worksheet,
        "sourceRowNumber": row,
    }


def build_intake_evidence(*, devices: list[dict] | None = None) -> dict:
    device_list = devices or [
        _device("SYNTH-DEV-001"),
        _device("SYNTH-DEV-002", worksheet="Zone-2", row=3, level="GRD", zone="Z2", da="DA31", location="LOBBY A"),
        _device("SYNTH-DEV-003", location="FIRE EXIT CORRIDOR DOOR"),
    ]
    spatial = {
        "airport": ["AIRPORT-CONTEXT-REQUIRED"],
        "terminal": ["TERMINAL-CONTEXT-REQUIRED"],
        "building": sorted({d["buildingCode"].upper() for d in device_list if str(d.get("buildingCode", "")).strip()}),
        "level": sorted({d["levelCode"].upper() for d in device_list}),
        "zone": sorted({d["zoneCode"].upper() for d in device_list}),
        "distributionArea": sorted({d["distributionAreaCode"].upper() for d in device_list}),
        "location": sorted({d["normalizedLocation"] for d in device_list if d.get("normalizedLocation")}),
    }
    payload = {
        "authority": AUTHORITY,
        "evidenceVersion": "1.0.0",
        "executionMode": "OFFLINE_READ_ONLY",
        "sourceWorkbook": {"sha256": WORKBOOK_DIGEST},
        "readinessSummary": {"outcome": "INTAKE_COMPLETE_WITH_REVIEWS"},
        "spatialCandidates": spatial,
        "deviceCandidates": device_list,
    }
    payload["resultDigest"] = sha256_digest({k: v for k, v in payload.items() if k != "resultDigest"})
    return payload


def write_intake_evidence(path: Path, *, devices: list[dict] | None = None) -> dict:
    payload = build_intake_evidence(devices=devices)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def default_context_kwargs() -> dict:
    return {
        "tenant_id": "SYNTH-TENANT-001",
        "site_id": "SYNTH-SITE-001",
        "airport_context_id": "AIRPORT-CONTEXT-REQUIRED",
        "terminal_context_id": "TERMINAL-CONTEXT-REQUIRED",
        "source_workbook_digest": WORKBOOK_DIGEST,
        "allowed_terminal_codes": ["TERMINAL-CONTEXT-REQUIRED"],
        "allowed_building_codes": ["TE3"],
        "allowed_level_codes": ["BAS", "GRD", "1ST", "2ND", "ROF"],
        "allowed_zone_codes": ["Z1", "Z2"],
        "allowed_distribution_area_codes": ["DA21", "DA31"],
    }


def _device_with_type(
    source_id: str,
    *,
    worksheet: str = "Zone-1",
    row: int = 2,
    building: str = "TE3",
    level: str = "BAS",
    zone: str = "Z1",
    da: str = "DA21",
    location: str = "FIRE EXIT CORRIDOR",
    system: str = "CCTV",
    device_type: str = "Fixed Camera",
) -> dict:
    device = _device(
        source_id,
        worksheet=worksheet,
        row=row,
        building=building,
        level=level,
        zone=zone,
        da=da,
        location=location,
        system=system,
    )
    device["sourceDeviceType"] = device_type
    return device


def build_spatial_result(*, intake_digest: str) -> dict:
    payload = {
        "authority": "ONE-AIRPORT-A1-02",
        "profileName": "VANTARIS ONE Airport Spatial Hierarchy Profile",
        "profileId": "airport-spatial-v1",
        "implementationMode": "READ_ONLY_MAPPING",
        "platformCoreAirportized": False,
        "runId": "synthetic-spatial-run",
        "intakeEvidence": {
            "authority": AUTHORITY,
            "evidenceVersion": "1.0.0",
            "executionMode": "OFFLINE_READ_ONLY",
            "readinessOutcome": "INTAKE_COMPLETE_WITH_REVIEWS",
            "resultDigest": intake_digest,
            "sourceWorkbookDigest": WORKBOOK_DIGEST,
        },
        "readinessOutcome": "SPATIAL_MAPPING_COMPLETE_WITH_REVIEWS",
        "candidates": [],
        "relationshipCandidates": [],
    }
    payload["resultDigest"] = sha256_digest({k: v for k, v in payload.items() if k != "resultDigest"})
    return payload


def build_spatial_bindings(devices: list[dict]) -> list[dict]:
    bindings: list[dict] = []
    for device in devices:
        bindings.append(
            {
                "sourceDeviceDigest": sha256_digest({"sourceId": device["sourceId"]}),
                "sourceWorksheet": device["sourceWorksheet"],
                "sourceRowNumber": device["sourceRowNumber"],
                "bindingStatus": "BOUND",
                "siteId": "SYNTH-SITE-001",
                "buildingCandidateKey": "synthetic-building-key",
                "levelCandidateKey": "synthetic-level-key",
                "zoneCandidateKey": "synthetic-zone-key",
                "distributionAreaCandidateKey": "synthetic-da-key",
                "locationCandidateKey": "synthetic-location-key",
            }
        )
    return bindings


def classification_context_kwargs(intake_digest: str) -> dict:
    return {
        "tenant_id": "SYNTH-TENANT-001",
        "site_id": "SYNTH-SITE-001",
        "source_workbook_digest": WORKBOOK_DIGEST,
        "expected_intake_result_digest": intake_digest,
    }
