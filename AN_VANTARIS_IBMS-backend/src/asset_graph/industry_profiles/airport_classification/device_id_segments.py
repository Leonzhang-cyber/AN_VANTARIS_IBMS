"""Device ID segment parsing for airport classification."""
from __future__ import annotations

from dataclasses import dataclass

from .constants import DEVICE_TYPE_DEFINITIONS, EMBEDDED_SYSTEM_ALIAS_CANDIDATES, KNOWN_SOURCE_NAMESPACES


@dataclass(frozen=True)
class DeviceIdSegmentParse:
    building_code: str
    source_namespace_code: str
    embedded_system_code: str
    level_code: str
    distribution_area_code: str
    device_type_code: str
    sequence_code: str
    parse_pattern: str
    parse_status: str


def _segment2_role(segment: str) -> tuple[str, str, str]:
    upper = segment.strip().upper()
    if upper in KNOWN_SOURCE_NAMESPACES:
        return upper, "", "SOURCE_NAMESPACE"
    if upper in EMBEDDED_SYSTEM_ALIAS_CANDIDATES:
        return "", upper, "EMBEDDED_ALIAS"
    if upper in DEVICE_TYPE_DEFINITIONS:
        return "", upper, "EMBEDDED_DEVICE_TYPE"
    return "", upper, "EMBEDDED_SYSTEM"


def parse_device_id_segments(device_id: str) -> DeviceIdSegmentParse:
    text = device_id.strip()
    if not text:
        return DeviceIdSegmentParse(
            building_code="",
            source_namespace_code="",
            embedded_system_code="",
            level_code="",
            distribution_area_code="",
            device_type_code="",
            sequence_code="",
            parse_pattern="EMPTY",
            parse_status="UNPARSEABLE",
        )

    parts = [part.strip() for part in text.split("-") if part.strip()]
    if len(parts) == 6:
        namespace, embedded, role = _segment2_role(parts[1])
        device_type = parts[4].upper()
        if role == "EMBEDDED_DEVICE_TYPE":
            return DeviceIdSegmentParse(
                building_code=parts[0].upper(),
                source_namespace_code="",
                embedded_system_code=embedded,
                level_code=parts[2].upper(),
                distribution_area_code=parts[3].upper(),
                device_type_code=embedded,
                sequence_code=parts[5].upper(),
                parse_pattern="NON_STANDARD_SIX_SEGMENT",
                parse_status="NON_STANDARD_PATTERN",
            )
        status = "FULLY_PARSED"
        if role == "SOURCE_NAMESPACE":
            status = "REVIEW_REQUIRED"
        return DeviceIdSegmentParse(
            building_code=parts[0].upper(),
            source_namespace_code=namespace,
            embedded_system_code=embedded,
            level_code=parts[2].upper(),
            distribution_area_code=parts[3].upper(),
            device_type_code=device_type,
            sequence_code=parts[5].upper(),
            parse_pattern="BUILDING-NAMESPACE_OR_SYSTEM-LEVEL-DA-TYPE-SEQ",
            parse_status=status,
        )

    if len(parts) == 3:
        namespace, embedded, role = _segment2_role(parts[1])
        device_type = embedded if role == "EMBEDDED_DEVICE_TYPE" else parts[1].upper()
        return DeviceIdSegmentParse(
            building_code=parts[0].upper(),
            source_namespace_code=namespace,
            embedded_system_code="" if role == "EMBEDDED_DEVICE_TYPE" else embedded,
            level_code="",
            distribution_area_code="",
            device_type_code=device_type,
            sequence_code=parts[2].upper(),
            parse_pattern="SHORT-NON_STANDARD",
            parse_status="NON_STANDARD_PATTERN",
        )

    if len(parts) >= 4:
        namespace, embedded, role = _segment2_role(parts[1])
        device_type = parts[4].upper() if len(parts) > 4 else ""
        return DeviceIdSegmentParse(
            building_code=parts[0].upper(),
            source_namespace_code=namespace,
            embedded_system_code=embedded,
            level_code=parts[2].upper() if len(parts) > 2 else "",
            distribution_area_code=parts[3].upper() if len(parts) > 3 else "",
            device_type_code=device_type,
            sequence_code=parts[5].upper() if len(parts) > 5 else "",
            parse_pattern="PARTIAL_HYPHEN_SEGMENTS",
            parse_status="PARTIALLY_PARSED",
        )

    return DeviceIdSegmentParse(
        building_code=parts[0].upper() if parts else "",
        source_namespace_code="",
        embedded_system_code=parts[1].upper() if len(parts) > 1 else "",
        level_code="",
        distribution_area_code="",
        device_type_code="",
        sequence_code="",
        parse_pattern="UNPARSEABLE",
        parse_status="UNPARSEABLE",
    )
