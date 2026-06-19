"""Generic deterministic Integration Health projection helpers."""
from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

PAGE_SIZE_OPTIONS = (25, 50, 100)
MAX_PAGE_SIZE = 200


def sort_health_records(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [dict(item) for item in records],
        key=lambda item: (str(item["sourceSystemKey"]), str(item["integrationHealthId"])),
    )


def paginate_health_records(
    records: Sequence[Mapping[str, Any]],
    *,
    page_size: int = 25,
    continuation_token: str | None = None,
) -> dict[str, Any]:
    size = min(max(int(page_size), 1), MAX_PAGE_SIZE)
    if size not in PAGE_SIZE_OPTIONS:
        size = min(PAGE_SIZE_OPTIONS, key=lambda value: abs(value - size))

    offset = 0
    if continuation_token:
        try:
            prefix, raw_offset = continuation_token.split(":", 1)
            if prefix == "v1":
                offset = int(raw_offset)
        except (TypeError, ValueError):
            offset = 0

    ordered = sort_health_records(records)
    items = ordered[offset : offset + size]
    next_offset = offset + len(items)
    next_token = f"v1:{next_offset}" if next_offset < len(ordered) else None

    result = {
        "pageSize": size,
        "offset": offset,
        "totalCount": len(ordered),
        "items": items,
        "continuationToken": next_token,
    }
    result["deterministicDigest"] = sha256_digest(result)
    return result


def build_facets(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    counters: dict[str, Counter[str]] = {
        "readinessState": Counter(str(item["readinessState"]) for item in records),
        "approvalState": Counter(str(item["approvalState"]) for item in records),
        "lifecycleState": Counter(str(item["lifecycleState"]) for item in records),
        "runtimeObserved": Counter(
            str(bool(item["runtimeObservationHealth"]["runtimeObserved"])).lower()
            for item in records
        ),
        "configurationReview": Counter(
            str(bool(item["configurationHealth"]["reviewRequired"])).lower()
            for item in records
        ),
        "runtimeVerificationRequired": Counter(
            str(item["readinessState"] == "RUNTIME_VERIFICATION_REQUIRED").lower()
            for item in records
        ),
    }

    findings = [finding for item in records for finding in item.get("findings", [])]
    counters["findingSeverity"] = Counter(str(item["severity"]) for item in findings)
    counters["findingType"] = Counter(str(item["findingType"]) for item in findings)

    facets: list[dict[str, Any]] = []
    for facet_key in sorted(counters):
        for value in sorted(counters[facet_key]):
            facets.append(
                {
                    "facetKey": facet_key,
                    "optionValue": value,
                    "count": counters[facet_key][value],
                    "optionDigest": sha256_digest({"facetKey": facet_key, "optionValue": value}),
                }
            )
    return facets
