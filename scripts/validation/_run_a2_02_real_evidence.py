#!/usr/bin/env python3
"""Real-evidence runner for A2-02 airport source-system review projection validation."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from shutil import copy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "AN_VANTARIS_ONE"))

from industry_profiles.airport.source_system_review_projection import (  # noqa: E402
    compare_deterministic_outputs,
    run_airport_source_system_review_projection,
)


def main() -> int:
    profile = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/source-system-profile.v1.json"
    for run in ("run-1", "run-2"):
        evidence = Path(f"/tmp/one-airport-a2-02/{run}/evidence")
        evidence.mkdir(parents=True, exist_ok=True)
        copy(
            "/tmp/one-airport-a1-03/run-1/airport-device-classification-bindings.json",
            evidence / "airport-device-classification-bindings.json",
        )
        copy(
            "/tmp/one-airport-a1-04/run-1/airport-alias-approval-package.json",
            evidence / "airport-alias-approval-package.json",
        )
        run_airport_source_system_review_projection(
            evidence_dir=evidence,
            profile_path=profile,
            output_path=Path(f"/tmp/one-airport-a2-02/{run}/airport-source-system-review.json"),
        )

    ok, _ = compare_deterministic_outputs(
        Path("/tmp/one-airport-a2-02/run-1/airport-source-system-review.json"),
        Path("/tmp/one-airport-a2-02/run-2/airport-source-system-review.json"),
    )
    assert ok

    projection = json.loads(
        Path("/tmp/one-airport-a2-02/run-1/airport-source-system-review.json").read_text(encoding="utf-8")
    )
    summary = projection["summary"]
    assert summary["sourceSystemEvidenceBindingCount"] == 5
    assert summary["totalBoundDeviceEvidenceCount"] == 470
    assert summary["aliasReviewCardCount"] == 2
    assert summary["namespaceReviewCardCount"] == 1
    assert summary["registryApprovalReviewCardCount"] == 2
    assert summary["pendingDecisionCount"] == 5
    assert summary["activeSystemCount"] == 0
    assert summary["registeredSystemCount"] == 0
    assert summary["approvedSystemCount"] == 0
    assert projection["readinessOutcome"] == "SOURCE_SYSTEM_REVIEW_PROJECTION_COMPLETE_WITH_PENDING_DECISIONS"
    assert "TE3-CCT" not in json.dumps(projection)

    bindings = {item["sourceSystemKey"]: item for item in projection["evidenceBindings"]}
    assert bindings["ACS"]["deviceEvidenceCount"] == 129
    assert bindings["RAS"]["deviceEvidenceCount"] == 28
    assert bindings["CCTV"]["deviceEvidenceCount"] == 52
    assert bindings["PA"]["deviceEvidenceCount"] == 247
    assert bindings["TEL"]["deviceEvidenceCount"] == 14
    assert bindings["CCTV"]["observedSourceValues"] == ["CCT"]
    assert bindings["PA"]["observedSourceValues"] == ["PAS"]
    assert bindings["TEL"]["evidenceType"] == "namespace_review"

    cards = projection["reviewCards"]
    assert len(cards) == 5
    assert sum(1 for item in cards if item["reviewType"] == "ALIAS_APPROVAL") == 2
    assert sum(1 for item in cards if item["reviewType"] == "NAMESPACE_INTERPRETATION") == 1
    assert sum(1 for item in cards if item["reviewType"] == "REGISTRY_APPROVAL") == 2
    assert all(item["currentDecision"] == "PENDING" for item in cards)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
