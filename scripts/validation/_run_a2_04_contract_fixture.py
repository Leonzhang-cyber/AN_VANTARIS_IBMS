#!/usr/bin/env python3
"""Deterministic fixture runner for A2-04 Evidence Adapter Contract."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from shutil import copy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "AN_VANTARIS_ONE"))

from industry_profiles.airport.evidence_adapter_profile import (
    compare_deterministic_outputs,
    run_airport_evidence_adapter_projection,
)


def main() -> int:
    profile = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/source-system-profile.v1.json"
    target = (
        ROOT
        / "AN_VANTARIS_ONE/industry_profiles/airport/projections/"
        "airport-evidence-adapter-contract.v1.json"
    )

    for run in ("run-1", "run-2"):
        evidence = Path(f"/tmp/one-airport-a2-04/{run}/evidence")
        evidence.mkdir(parents=True, exist_ok=True)
        copy(
            "/tmp/one-airport-a1-03/run-1/airport-device-classification-bindings.json",
            evidence / "airport-device-classification-bindings.json",
        )
        copy(
            "/tmp/one-airport-a1-04/run-1/airport-alias-approval-package.json",
            evidence / "airport-alias-approval-package.json",
        )
        run_airport_evidence_adapter_projection(
            evidence_dir=evidence,
            profile_path=profile,
            output_path=Path(f"/tmp/one-airport-a2-04/{run}/airport-evidence-adapter-contract.json"),
        )

    first = Path("/tmp/one-airport-a2-04/run-1/airport-evidence-adapter-contract.json")
    second = Path("/tmp/one-airport-a2-04/run-2/airport-evidence-adapter-contract.json")
    ok, reason = compare_deterministic_outputs(first, second)
    assert ok, reason

    projection = json.loads(first.read_text(encoding="utf-8"))
    summary = projection["summary"]
    assert summary["sourceSystemCandidateCount"] == 5
    assert summary["evidenceEnvelopeCount"] == 5
    assert summary["acceptedAsEvidenceCount"] == 5
    assert summary["rejectedEnvelopeCount"] == 0
    assert summary["runtimeObservedSystemCount"] == 0
    assert summary["runtimeVerifiedSystemCount"] == 0
    assert summary["readinessOutcome"] == "EDGE_LINK_EVIDENCE_ADAPTER_CONTRACT_DEFINED_RUNTIME_PENDING"
    assert "TE3-CCT" not in json.dumps(projection)

    target.write_bytes(first.read_bytes())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
