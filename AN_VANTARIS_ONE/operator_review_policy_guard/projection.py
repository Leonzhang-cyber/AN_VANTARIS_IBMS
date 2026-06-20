"""Projection helpers for Operator Review Policy Guards."""
from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

FILTER_FIELDS = (
    "decisionType",
    "decisionScope",
    "queueType",
    "sourceStage",
    "sourceSystemKey",
    "guardState",
    "eligibilityState",
    "policyResult",
    "writeAllowed",
    "approvalAllowed",
    "runtimeActivationAllowed",
    "productionActivationAllowed",
)


def sort_guard_results(results: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        (dict(result) for result in results),
        key=lambda result: (result["decisionType"], result.get("sourceSystemKey") or "", result["decisionItemId"], result["guardResultId"]),
    )


def build_filters(results: Sequence[Mapping[str, Any]], previews: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    filters: dict[str, Any] = {}
    for field in FILTER_FIELDS:
        filters[field] = {"field": field, "options": sorted({result.get(field) for result in results if result.get(field) is not None})}
    filters["auditPreviewState"] = {"field": "auditPreviewState", "options": sorted({p["auditPreviewState"] for p in previews})}
    filters["reasonCode"] = {"field": "reasonCode", "options": sorted({code for result in results for code in result.get("reasonCodes", [])})}
    return filters


def build_facets(results: Sequence[Mapping[str, Any]], previews: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    facets: dict[str, Any] = {}
    for field in FILTER_FIELDS:
        counts = Counter(result.get(field) for result in results if result.get(field) is not None)
        facets[field] = {str(key): counts[key] for key in sorted(counts, key=lambda value: str(value))}
    preview_counts = Counter(p["auditPreviewState"] for p in previews)
    facets["auditPreviewState"] = {str(key): preview_counts[key] for key in sorted(preview_counts)}
    reason_counts = Counter(code for result in results for code in result.get("reasonCodes", []))
    facets["reasonCode"] = {str(key): reason_counts[key] for key in sorted(reason_counts)}
    return facets


def paginate_guard_results(results: Sequence[Mapping[str, Any]], *, page_size: int = 25) -> dict[str, Any]:
    ordered = sort_guard_results(results)
    page = ordered[:page_size]
    token = sha256_digest({"pageSize": page_size, "returnedIds": [r["guardResultId"] for r in page]})
    next_token = None
    if len(ordered) > page_size:
        next_token = sha256_digest({"nextOffset": page_size, "totalCount": len(ordered)})
    return {
        "pageSize": page_size,
        "items": page,
        "continuationToken": token,
        "nextContinuationToken": next_token,
        "totalCount": len(ordered),
        "returnedCount": len(page),
        "deterministicDigest": sha256_digest({"token": token, "next": next_token, "count": len(page)}),
    }
