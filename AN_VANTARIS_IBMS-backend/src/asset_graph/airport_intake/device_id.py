"""Device ID parsing for airport asset Excel intake."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DeviceIdParseResult:
    device_id: str
    parsed_successfully: bool
    partially_parsed: bool
    unparseable: bool
    segments: dict[str, str]
    parse_pattern: str


def parse_device_id(device_id: str) -> DeviceIdParseResult:
    text = device_id.strip()
    if not text:
        return DeviceIdParseResult(
            device_id=text,
            parsed_successfully=False,
            partially_parsed=False,
            unparseable=True,
            segments={},
            parse_pattern="EMPTY",
        )
    parts = [part.strip() for part in text.split("-") if part.strip()]
    if len(parts) == 6:
        segments = {
            "buildingCode": parts[0],
            "embeddedSystemCode": parts[1],
            "levelCode": parts[2],
            "distributionAreaCode": parts[3],
            "deviceTypeCode": parts[4],
            "sequence": parts[5],
        }
        return DeviceIdParseResult(
            device_id=text,
            parsed_successfully=True,
            partially_parsed=False,
            unparseable=False,
            segments=segments,
            parse_pattern="BUILDING-SYSTEM-LEVEL-DA-TYPE-SEQ",
        )
    if len(parts) >= 3:
        segments = {
            "buildingCode": parts[0] if len(parts) > 0 else "",
            "embeddedSystemCode": parts[1] if len(parts) > 1 else "",
            "levelCode": parts[2] if len(parts) > 2 else "",
        }
        if len(parts) > 3:
            segments["distributionAreaCode"] = parts[3]
        if len(parts) > 4:
            segments["deviceTypeCode"] = parts[4]
        if len(parts) > 5:
            segments["sequence"] = parts[5]
        return DeviceIdParseResult(
            device_id=text,
            parsed_successfully=False,
            partially_parsed=True,
            unparseable=False,
            segments=segments,
            parse_pattern="PARTIAL_HYPHEN_SEGMENTS",
        )
    return DeviceIdParseResult(
        device_id=text,
        parsed_successfully=False,
        partially_parsed=False,
        unparseable=True,
        segments={},
        parse_pattern="UNPARSEABLE",
    )


def compare_parsed_to_columns(
    parse_result: DeviceIdParseResult,
    *,
    building: str,
    level: str,
    distribution_area: str,
    system: str,
) -> dict[str, str]:
    if parse_result.unparseable:
        return {"status": "UNPARSEABLE", "detail": "device id could not be parsed"}
    segments = parse_result.segments
    conflicts: list[str] = []
    agreements: list[str] = []
    checks = (
        ("buildingCode", building),
        ("levelCode", level),
        ("distributionAreaCode", distribution_area),
        ("embeddedSystemCode", system),
    )
    for segment_key, column_value in checks:
        segment_value = segments.get(segment_key, "")
        column_text = str(column_value or "").strip()
        if not segment_value or not column_text:
            continue
        if segment_value.upper() == column_text.upper():
            agreements.append(segment_key)
        else:
            conflicts.append(segment_key)
    if conflicts:
        return {"status": "COLUMN_CONFLICT", "detail": ",".join(conflicts)}
    if agreements:
        return {"status": "COLUMN_AGREEMENT", "detail": ",".join(agreements)}
    return {"status": "REVIEW_REQUIRED", "detail": "insufficient overlap"}
