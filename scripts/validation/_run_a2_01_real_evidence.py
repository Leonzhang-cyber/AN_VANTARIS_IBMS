#!/usr/bin/env python3
"""Real-evidence runner for A2-01 source-system registry validation."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from shutil import copy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "AN_VANTARIS_ONE"))

from industry_profiles.airport.candidate_projection import (  # noqa: E402
    compare_deterministic_outputs,
    run_airport_source_system_projection,
)


def main() -> int:
    profile = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/source-system-profile.v1.json"
    for run in ("run-1", "run-2"):
        evidence = Path(f"/tmp/one-airport-a2-01/{run}/evidence")
        evidence.mkdir(parents=True, exist_ok=True)
        copy(
            "/tmp/one-airport-a1-03/run-1/airport-device-classification-bindings.json",
            evidence / "airport-device-classification-bindings.json",
        )
        copy(
            "/tmp/one-airport-a1-04/run-1/airport-alias-approval-package.json",
            evidence / "airport-alias-approval-package.json",
        )
        run_airport_source_system_projection(
            evidence_dir=evidence,
            profile_path=profile,
            output_path=Path(f"/tmp/one-airport-a2-01/{run}/airport-source-system-candidates.json"),
        )

    ok, _ = compare_deterministic_outputs(
        Path("/tmp/one-airport-a2-01/run-1/airport-source-system-candidates.json"),
        Path("/tmp/one-airport-a2-01/run-2/airport-source-system-candidates.json"),
    )
    assert ok

    projection = json.loads(
        Path("/tmp/one-airport-a2-01/run-1/airport-source-system-candidates.json").read_text(encoding="utf-8")
    )
    summary = projection["summary"]
    assert summary["sourceSystemCandidateCount"] == 5
    assert summary["activeSystemCount"] == 0
    assert summary["registeredSystemCount"] == 0
    assert summary["approvedSystemCount"] == 0
    assert summary["exactEvidenceCandidateCount"] == 2
    assert summary["aliasReviewCandidateCount"] == 2
    assert summary["namespaceReviewCandidateCount"] == 1
    assert summary["totalEvidenceDeviceCount"] == 470
    assert projection["readinessOutcome"] == "SOURCE_SYSTEM_CANDIDATES_COMPLETE_WITH_PENDING_REVIEWS"
    assert projection["implementationStatus"] == "GENERIC_SOURCE_SYSTEM_REGISTRY_FOUNDATION_COMPLETE"
    assert "TE3-CCT" not in json.dumps(projection)

    candidates = projection["candidates"]
    cctv = next(item for item in candidates if item["sourceSystemKey"] == "CCTV")
    pa = next(item for item in candidates if item["sourceSystemKey"] == "PA")
    tel = next(item for item in candidates if item["sourceSystemKey"] == "TEL")
    assert cctv["airportConsumerMetadata"]["observedSourceValue"] == "CCT"
    assert cctv["airportConsumerMetadata"]["autoApproved"] is False
    assert pa["airportConsumerMetadata"]["observedSourceValue"] == "PAS"
    assert pa["airportConsumerMetadata"]["autoApproved"] is False
    assert tel["airportConsumerMetadata"]["sourceNamespaceCode"] == "SCN"
    assert tel["airportConsumerMetadata"]["namespaceReviewRequired"] is True
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
