#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from shutil import copy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "AN_VANTARIS_ONE"))

from industry_profiles.airport.integration_health_projection import (
    compare_deterministic_outputs,
    run_airport_integration_health_projection,
)


def main() -> int:
    profile = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/source-system-profile.v1.json"

    for run in ("run-1", "run-2"):
        evidence = Path(f"/tmp/one-airport-a2-03/{run}/evidence")
        evidence.mkdir(parents=True, exist_ok=True)

        copy(
            "/tmp/one-airport-a1-03/run-1/airport-device-classification-bindings.json",
            evidence / "airport-device-classification-bindings.json",
        )
        copy(
            "/tmp/one-airport-a1-04/run-1/airport-alias-approval-package.json",
            evidence / "airport-alias-approval-package.json",
        )

        run_airport_integration_health_projection(
            evidence_dir=evidence,
            profile_path=profile,
            output_path=Path(
                f"/tmp/one-airport-a2-03/{run}/airport-integration-health.json"
            ),
        )

    first = Path("/tmp/one-airport-a2-03/run-1/airport-integration-health.json")
    second = Path("/tmp/one-airport-a2-03/run-2/airport-integration-health.json")
    ok, reason = compare_deterministic_outputs(first, second)
    assert ok, reason

    projection = json.loads(first.read_text(encoding="utf-8"))
    summary = projection["summary"]

    assert summary["integrationHealthRecordCount"] == 5
    assert summary["runtimeObservedSystemCount"] == 0
    assert summary["runtimeVerifiedSystemCount"] == 0
    assert summary["healthySystemCount"] == 0
    assert summary["activeSystemCount"] == 0
    assert summary["registeredSystemCount"] == 0
    assert summary["approvedSystemCount"] == 0
    assert summary["registryApprovalPendingCount"] == 2
    assert summary["aliasApprovalPendingCount"] == 2
    assert summary["namespaceReviewPendingCount"] == 1
    assert summary["runtimeVerificationRequiredCount"] == 5
    assert summary["totalEvidenceDeviceCount"] == 470

    records = {item["sourceSystemKey"]: item for item in projection["healthRecords"]}
    assert records["ACS"]["deviceEvidenceCount"] == 129
    assert records["RAS"]["deviceEvidenceCount"] == 28
    assert records["CCTV"]["deviceEvidenceCount"] == 52
    assert records["PA"]["deviceEvidenceCount"] == 247
    assert records["TEL"]["deviceEvidenceCount"] == 14
    assert records["ACS"]["readinessState"] == "RUNTIME_VERIFICATION_REQUIRED"
    assert records["RAS"]["readinessState"] == "RUNTIME_VERIFICATION_REQUIRED"
    assert records["CCTV"]["readinessState"] == "REVIEW_REQUIRED"
    assert records["PA"]["readinessState"] == "REVIEW_REQUIRED"
    assert records["TEL"]["readinessState"] == "REVIEW_REQUIRED"
    assert all(
        not item["runtimeObservationHealth"]["runtimeObserved"]
        for item in records.values()
    )

    assert (
        projection["readinessOutcome"]
        == "INTEGRATION_HEALTH_DECLARATION_COMPLETE_RUNTIME_EVIDENCE_PENDING"
    )

    serialized = json.dumps(projection)
    assert "TE3-CCT" not in serialized
    assert "Device ID" not in serialized

    target = (
        ROOT
        / "AN_VANTARIS_ONE/industry_profiles/airport/projections/"
        "airport-integration-health.v1.json"
    )
    target.write_bytes(first.read_bytes())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
