"""Tests for generic Evidence Adapter Contract and airport fixtures."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from evidence_adapter_contract.enums import (
    EvidenceKind,
    EvidenceScope,
    ProducerType,
    ValidationState,
)
from evidence_adapter_contract.errors import EvidenceAdapterContractError
from evidence_adapter_contract.models import build_evidence_adapter_envelope
from evidence_adapter_contract.projection import build_contract_projection, sort_envelopes
from evidence_adapter_contract.validation import validate_envelope

from industry_profiles.airport.evidence_adapter_profile import (
    build_airport_evidence_adapter_projection,
    build_airport_fixture_envelope,
    compare_deterministic_outputs,
    run_airport_evidence_adapter_projection,
)

REGISTRY = ROOT / "registries/evidence-adapter-contract.v1.json"
GENERIC_DIR = ROOT / "evidence_adapter_contract"
AIRPORT_PROFILE = ROOT / "industry_profiles/airport/source-system-profile.v1.json"
CONTRACT_PROJECTION = ROOT / "industry_profiles/airport/projections/airport-evidence-adapter-contract.v1.json"

ALLOWED_KEYS = ["ACS", "CCTV", "PA", "RAS", "TEL"]


def _candidate(source_key: str) -> dict:
    return {
        "sourceSystemKey": source_key,
        "registryEntryId": f"registry-{source_key.lower()}",
        "mappingVersion": "airport-source-system-v1",
        "schemaVersion": "1.0.0",
        "systemCategory": "ACCESS_CONTROL" if source_key == "ACS" else "OTHER_CONTROLLED",
    }


def _valid_envelope(**overrides: object) -> dict:
    payload = {
        "fixtureOnly": True,
        "declarationType": EvidenceKind.CONFIG_DECLARATION.value,
        "contractMode": "OFFLINE_FIXTURE_VALIDATION",
    }
    base = build_evidence_adapter_envelope(
        producer_type=ProducerType.OFFLINE_FIXTURE.value,
        producer_id="fixture-producer-acs",
        source_system_key="ACS",
        registry_entry_id="registry-acs",
        evidence_kind=EvidenceKind.CONFIG_DECLARATION.value,
        evidence_scope=EvidenceScope.SOURCE_SYSTEM.value,
        payload=payload,
        provenance="test-fixture",
        validation_state=ValidationState.NOT_RUNTIME_EVIDENCE.value,
    )
    base.update(overrides)
    if "payload" in overrides:
        base["payloadDigest"] = __import__(
            "source_system_registry.digest", fromlist=["sha256_digest"]
        ).sha256_digest(base["payload"])
        base["deterministicDigest"] = __import__(
            "source_system_registry.digest", fromlist=["sha256_digest"]
        ).sha256_digest({k: v for k, v in base.items() if k != "deterministicDigest"})
    return base


def _synthetic_candidates() -> list[dict]:
    return [_candidate(key) for key in ALLOWED_KEYS]


class TestGenericEvidenceAdapterContract(unittest.TestCase):
    def test_registry_exists(self) -> None:
        self.assertTrue(REGISTRY.is_file())

    def test_valid_envelope_accepted(self) -> None:
        envelope = _valid_envelope()
        validate_envelope(envelope, allowed_source_system_keys=ALLOWED_KEYS)
        self.assertEqual(envelope["validationState"], ValidationState.NOT_RUNTIME_EVIDENCE.value)

    def test_missing_producer_id_rejected(self) -> None:
        envelope = _valid_envelope(producerId="")
        with self.assertRaises(EvidenceAdapterContractError):
            validate_envelope(envelope, allowed_source_system_keys=ALLOWED_KEYS)

    def test_missing_source_system_key_rejected(self) -> None:
        envelope = _valid_envelope(sourceSystemKey="")
        with self.assertRaises(EvidenceAdapterContractError):
            validate_envelope(envelope, allowed_source_system_keys=ALLOWED_KEYS)

    def test_unknown_source_system_key_rejected(self) -> None:
        envelope = _valid_envelope(sourceSystemKey="UNKNOWN_SYS")
        with self.assertRaises(EvidenceAdapterContractError):
            validate_envelope(envelope, allowed_source_system_keys=ALLOWED_KEYS)

    def test_missing_evidence_kind_rejected(self) -> None:
        envelope = _valid_envelope(evidenceKind="")
        with self.assertRaises(EvidenceAdapterContractError):
            validate_envelope(envelope, allowed_source_system_keys=ALLOWED_KEYS)

    def test_missing_payload_digest_rejected(self) -> None:
        envelope = _valid_envelope(payloadDigest="")
        with self.assertRaises(EvidenceAdapterContractError):
            validate_envelope(envelope, allowed_source_system_keys=ALLOWED_KEYS)

    def test_deterministic_envelope_id(self) -> None:
        first = _valid_envelope()
        second = _valid_envelope()
        self.assertEqual(first["envelopeId"], second["envelopeId"])

    def test_deterministic_digest(self) -> None:
        first = _valid_envelope()
        second = _valid_envelope()
        self.assertEqual(first["deterministicDigest"], second["deterministicDigest"])

    def test_fixture_not_runtime_observation(self) -> None:
        envelope = _valid_envelope()
        self.assertEqual(envelope["producerType"], ProducerType.OFFLINE_FIXTURE.value)
        self.assertNotEqual(envelope["validationState"], ValidationState.ACCEPTED_AS_EVIDENCE.value)

    def test_no_volatile_timestamp(self) -> None:
        envelope = _valid_envelope()
        self.assertEqual(envelope["observedAtPolicy"], "DETERMINISTIC_NO_VOLATILE_TIMESTAMP")
        self.assertNotIn("observedAt", envelope)

    def test_unsupported_runtime_kind_for_fixture(self) -> None:
        envelope = _valid_envelope(evidenceKind=EvidenceKind.HEARTBEAT.value)
        with self.assertRaises(EvidenceAdapterContractError):
            validate_envelope(envelope, allowed_source_system_keys=ALLOWED_KEYS)

    def test_no_db_imports(self) -> None:
        forbidden = ("sqlalchemy", "flask", "psycopg", "pymongo")
        for path in GENERIC_DIR.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text)


class TestAirportEvidenceAdapterFixture(unittest.TestCase):
    def test_five_candidates_covered(self) -> None:
        projection = build_airport_evidence_adapter_projection(_synthetic_candidates())
        keys = {item["sourceSystemKey"] for item in projection["envelopes"]}
        self.assertEqual(keys, set(ALLOWED_KEYS))

    def test_evidence_envelope_count(self) -> None:
        projection = build_airport_evidence_adapter_projection(_synthetic_candidates())
        self.assertEqual(projection["summary"]["evidenceEnvelopeCount"], 5)

    def test_accepted_as_evidence_count(self) -> None:
        projection = build_airport_evidence_adapter_projection(_synthetic_candidates())
        self.assertEqual(projection["summary"]["acceptedAsEvidenceCount"], 5)

    def test_rejected_count_zero(self) -> None:
        projection = build_airport_evidence_adapter_projection(_synthetic_candidates())
        self.assertEqual(projection["summary"]["rejectedEnvelopeCount"], 0)

    def test_runtime_observed_zero(self) -> None:
        projection = build_airport_evidence_adapter_projection(_synthetic_candidates())
        self.assertEqual(projection["summary"]["runtimeObservedSystemCount"], 0)
        self.assertEqual(projection["summary"]["runtimeVerifiedSystemCount"], 0)

    def test_system_specific_fixtures(self) -> None:
        for key in ALLOWED_KEYS:
            envelope = build_airport_fixture_envelope(_candidate(key))
            self.assertEqual(envelope["sourceSystemKey"], key)
            self.assertEqual(envelope["validationState"], ValidationState.NOT_RUNTIME_EVIDENCE.value)

    def test_no_device_id_leakage(self) -> None:
        projection = build_airport_evidence_adapter_projection(_synthetic_candidates())
        text = json.dumps(projection)
        self.assertNotIn("TE3-", text)
        self.assertNotIn("deviceCode", text)
        self.assertNotIn("deviceId", text)

    def test_deterministic_ordering(self) -> None:
        first = build_airport_evidence_adapter_projection(_synthetic_candidates())
        second = build_airport_evidence_adapter_projection(_synthetic_candidates())
        self.assertEqual(first["envelopes"], second["envelopes"])

    def test_repeated_generation_byte_identical(self) -> None:
        first = json.dumps(build_airport_evidence_adapter_projection(_synthetic_candidates()), sort_keys=True)
        second = json.dumps(build_airport_evidence_adapter_projection(_synthetic_candidates()), sort_keys=True)
        self.assertEqual(first, second)

    def test_readiness_outcome(self) -> None:
        projection = build_airport_evidence_adapter_projection(_synthetic_candidates())
        self.assertEqual(
            projection["summary"]["readinessOutcome"],
            "EDGE_LINK_EVIDENCE_ADAPTER_CONTRACT_DEFINED_RUNTIME_PENDING",
        )


class TestAirportContractArtifact(unittest.TestCase):
    def test_projection_artifact_exists(self) -> None:
        self.assertTrue(CONTRACT_PROJECTION.is_file())


class TestRealEvidenceContractFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.real_available = Path("/tmp/one-airport-a1-03/run-1/airport-device-classification-bindings.json").is_file()

    def test_real_deterministic_runs(self) -> None:
        if not self.real_available:
            self.skipTest("real A1 evidence unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for run in ("run-1", "run-2"):
                evidence = base / run / "evidence"
                evidence.mkdir(parents=True)
                copy("/tmp/one-airport-a1-03/run-1/airport-device-classification-bindings.json", evidence / "airport-device-classification-bindings.json")
                copy("/tmp/one-airport-a1-04/run-1/airport-alias-approval-package.json", evidence / "airport-alias-approval-package.json")
                run_airport_evidence_adapter_projection(
                    evidence_dir=evidence,
                    profile_path=AIRPORT_PROFILE,
                    output_path=base / run / "projection.json",
                )
            ok, _ = compare_deterministic_outputs(base / "run-1/projection.json", base / "run-2/projection.json")
            self.assertTrue(ok)


class TestBoundaryIsolation(unittest.TestCase):
    def test_no_edge_or_link_imports(self) -> None:
        text = (ROOT / "industry_profiles/airport/evidence_adapter_profile.py").read_text(encoding="utf-8")
        self.assertNotIn("AN_VANTARIS_EDGE", text)
        self.assertNotIn("AN_VANTARIS_LINK", text)

    def test_no_fake_runtime_metrics(self) -> None:
        for path in GENERIC_DIR.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in ("heartbeatAt", "latencyMs", "uptimePercent", "packetLossPercent"):
                if path.name == "validation.py" and token in text:
                    continue
                self.assertNotIn(token, text.replace("FORBIDDEN_PAYLOAD_KEYS", ""))


if __name__ == "__main__":
    unittest.main()
