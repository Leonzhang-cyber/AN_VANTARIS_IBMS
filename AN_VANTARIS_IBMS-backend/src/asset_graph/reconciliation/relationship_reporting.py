"""Aggregate-only relationship evidence metrics for reconciliation reports."""
from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

CANONICAL_RELATIONSHIP_MESSAGE = "canonical relationship projected"
UNRESOLVED_RELATIONSHIP_MESSAGE = "canonical target global ID unavailable"
RELATIONSHIP_RESULT_COUNT_SEMANTICS = (
    "all relationship result rows, including unresolved/review results"
)


def _status_bucket(status: str) -> str:
    if status == "PASS":
        return "pass"
    if status == "REVIEW_REQUIRED":
        return "review"
    return "blocker"


def _is_canonical(rel: Any) -> bool:
    return rel.status == "PASS" and rel.message == CANONICAL_RELATIONSHIP_MESSAGE


def _is_unresolved(rel: Any) -> bool:
    return rel.status == "REVIEW_REQUIRED"


def _type_metrics(rels: Sequence[Any]) -> dict[str, int]:
    return {
        "resultCount": len(rels),
        "passCount": sum(1 for rel in rels if rel.status == "PASS"),
        "reviewCount": sum(1 for rel in rels if rel.status == "REVIEW_REQUIRED"),
        "blockerCount": sum(
            1 for rel in rels if rel.status not in {"PASS", "REVIEW_REQUIRED"} or rel.cutover_blocking
        ),
    }


def collect_relationship_metrics(run: Any, blockers: Sequence[str]) -> dict[str, Any]:
    all_results = [
        rel
        for record in run.record_results
        for rel in record.relationship_results
    ]
    canonical = [rel for rel in all_results if _is_canonical(rel)]
    unresolved = [rel for rel in all_results if _is_unresolved(rel)]
    pass_results = [rel for rel in all_results if rel.status == "PASS"]
    review_results = [rel for rel in all_results if rel.status == "REVIEW_REQUIRED"]
    blocker_results = [
        rel for rel in all_results
        if rel.status not in {"PASS", "REVIEW_REQUIRED"} or rel.cutover_blocking
    ]

    canonical_keys = Counter(
        (rel.relationship_type, rel.source_id or "", rel.target_id or "")
        for rel in canonical
    )
    unique_canonical_count = len(canonical_keys)
    duplicate_canonical_count = len(canonical) - unique_canonical_count

    has_point_results = [rel for rel in all_results if rel.relationship_type == "HAS_POINT"]
    has_point_pass = [rel for rel in has_point_results if rel.status == "PASS"]
    has_point_pairs = Counter((rel.source_id or "", rel.target_id or "") for rel in has_point_pass)
    duplicate_has_point_pair_count = sum(count - 1 for count in has_point_pairs.values() if count > 1)

    located_results = [rel for rel in all_results if rel.relationship_type == "LOCATED_IN"]
    located_unresolved = [
        rel for rel in located_results
        if _is_unresolved(rel) and rel.message == UNRESOLVED_RELATIONSHIP_MESSAGE
    ]

    has_point_metrics = _type_metrics(has_point_results)
    has_point_metrics["uniquePairCount"] = len(has_point_pairs)
    has_point_metrics["duplicatePairCount"] = duplicate_has_point_pair_count

    located_metrics = _type_metrics(located_results)
    located_metrics["unresolvedCount"] = len(located_unresolved)

    duplicate_blocker_present = any("DUPLICATE" in blocker for blocker in blockers)

    return {
        "relationshipResultCount": len(all_results),
        "relationshipResultCountSemantics": RELATIONSHIP_RESULT_COUNT_SEMANTICS,
        "canonicalRelationshipCount": len(canonical),
        "passRelationshipCount": len(pass_results),
        "reviewRelationshipCount": len(review_results),
        "blockerRelationshipCount": len(blocker_results),
        "unresolvedRelationshipCount": len(unresolved),
        "uniqueCanonicalRelationshipCount": unique_canonical_count,
        "duplicateCanonicalRelationshipCount": duplicate_canonical_count,
        "duplicateHasPointPairCount": duplicate_has_point_pair_count,
        "duplicateRelationshipBlockerPresent": duplicate_blocker_present,
        "relationshipTypeCounts": {
            "HAS_POINT": has_point_metrics,
            "LOCATED_IN": located_metrics,
        },
    }
