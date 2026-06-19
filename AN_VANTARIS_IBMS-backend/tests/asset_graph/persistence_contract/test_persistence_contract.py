"""Tests for canonical Asset Graph persistence contract."""
from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from src.asset_graph.persistence_contract import (
    AUTHORIZATION_APPROVED_VALIDATION,
    AUTHORIZATION_DENIED,
    AUTHORIZATION_WAITING_PERSISTENCE_APPROVAL,
    AUTHORIZATION_WAITING_READINESS,
    AUTHORIZATION_WAITING_REAL_EVIDENCE,
    CONTRACT_AUTHORITY,
    CONTRACT_NAME,
    CONTRACT_VERSION,
    IMPLEMENTATION_STATUS,
    WRITE_CUTOVER_STATUS,
    AssetGraphPersistenceCoordinator,
    CanonicalDeviceProvider,
    CanonicalPointProvider,
    CanonicalRelationshipProvider,
    CanonicalTagProvider,
    CanonicalVersionMetadata,
    ContractUnitOfWork,
    CreateCanonicalDevice,
    CreateCanonicalPoint,
    CreateCanonicalRelationship,
    CreateCanonicalTag,
    IdempotencyLedger,
    PersistenceAuthorizationInput,
    PersistenceBatchLimitError,
    PersistenceContractError,
    PersistenceCoordinatorInput,
    PersistenceUnitOfWorkError,
    UpdateCanonicalDevice,
    batch_limits,
    build_rollback_result,
    conflict_result,
    default_provider_capabilities,
    enabled_validation_provider_capabilities,
    evaluate_canonical_identity,
    evaluate_persistence_authorization,
    evaluate_update_version,
    load_persistence_contract,
    validate_batch_limits,
    validate_persistence_contract,
)
from src.asset_graph.persistence_contract.results import PersistenceCommandResult
from src.asset_graph.persistence_contract.constants import CONFLICT_CODES, FORBIDDEN_AUTHORIZATION_DECISIONS
from src.asset_graph.persistence_contract.identity import validate_identity_immutability
from src.asset_graph.reconciliation.readiness import assess_readiness, load_readiness_policy
from src.governance.audit.in_memory import InMemoryAuditProvider

ROOT = Path(__file__).resolve().parents[4]
READINESS_FIXTURES = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/readiness/fixtures"
CLEAN = READINESS_FIXTURES / "clean-synthetic-evidence-report.json"
REAL = READINESS_FIXTURES / "real-sanitized-evidence-report.json"
DIGEST_A = "a" * 64
DIGEST_B = "b" * 64
DIGEST_C = "c" * 64


def _command_base(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "command_id": "cmd-001",
        "idempotency_key": "idem-001",
        "tenant_id": "tenant-real-001",
        "site_id": "site-real-001",
        "source_system_id": "legacy-device-v1",
        "mapping_version": "legacy-device-v1",
        "evidence_digest": DIGEST_A,
        "readiness_result_digest": DIGEST_B,
        "execution_result_digest": DIGEST_C,
        "canonical_global_id": "ag-device-00000000000000000000000000000001",
        "expected_version": 0,
        "requested_operation": "Create",
        "requested_by_authority": "APPROVED_READ_MIGRATION_EXECUTION",
    }
    payload.update(overrides)
    return payload


def _command(**overrides: object) -> CreateCanonicalDevice:
    extra = {"display_name": "Chiller", "device_type": "CONTROLLER"}
    extra.update(overrides)
    return CreateCanonicalDevice(**_command_base(**extra))


def _command_result(command: CreateCanonicalDevice, **overrides: object) -> PersistenceCommandResult:
    payload = {
        "command_id": command.command_id,
        "idempotency_key_digest": command.idempotency_key_digest(),
        "object_type": "Device",
        "canonical_global_id_digest": command.canonical_global_id_digest(),
        "status": "ACCEPTED",
        "conflict_code": None,
        "previous_version": None,
        "new_version": 1,
        "transaction_id": "tx-1",
        "audit_record_id": "audit-1",
        "rollback_required": False,
        "retryable": False,
    }
    payload.update(overrides)
    return PersistenceCommandResult(**payload)


def _auth_input(**overrides: object) -> PersistenceAuthorizationInput:
    provider = overrides.pop("provider_capabilities", default_provider_capabilities())
    payload = {
        "evidence_classification": "SYNTHETIC_REPRESENTATIVE_ONLY",
        "readiness_decision": "NOT_READY",
        "hard_blocker_count": 0,
        "evidence_digest": DIGEST_A,
        "readiness_result_digest": DIGEST_B,
        "execution_result_digest": DIGEST_C,
        "tenant_scope": "tenant-real-001",
        "site_scope": "site-real-001",
        "source_system_scope": "legacy-device-v1",
        "mapping_version": "legacy-device-v1",
        "requested_evidence_digest": DIGEST_A,
        "requested_readiness_result_digest": DIGEST_B,
        "requested_execution_result_digest": DIGEST_C,
        "requested_tenant_id": "tenant-real-001",
        "requested_site_id": "site-real-001",
        "requested_source_system_id": "legacy-device-v1",
        "requested_mapping_version": "legacy-device-v1",
        "persistence_approval_granted": False,
        "approved_execution_contract_present": True,
        "provider_capabilities": provider,
    }
    payload.update(overrides)
    return PersistenceAuthorizationInput(**payload)


class TestPersistenceContract(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = load_persistence_contract(root=ROOT)
        cls.policy = load_readiness_policy(root=ROOT)
        cls.clean_evidence = json.loads(CLEAN.read_text(encoding="utf-8"))
        cls.real_evidence = json.loads(REAL.read_text(encoding="utf-8"))
        cls.clean_assessment = assess_readiness(
            cls.clean_evidence, cls.policy, determinism_confirmed=True
        ).serialize()
        cls.real_assessment = assess_readiness(
            cls.real_evidence, cls.policy, determinism_confirmed=True
        ).serialize()

    def test_registry_loads(self) -> None:
        self.assertEqual(self.contract["contractName"], CONTRACT_NAME)
        self.assertEqual(self.contract["contractVersion"], CONTRACT_VERSION)
        self.assertEqual(self.contract["authority"], CONTRACT_AUTHORITY)

    def test_registry_implementation_status(self) -> None:
        self.assertEqual(self.contract["implementationStatus"], IMPLEMENTATION_STATUS)

    def test_registry_write_cutover_status(self) -> None:
        self.assertEqual(self.contract["writeCutoverStatus"], WRITE_CUTOVER_STATUS)

    def test_registry_batch_limits(self) -> None:
        limits = batch_limits(self.contract)
        self.assertEqual(limits["maximumDevicesPerUnitOfWork"], 100)
        self.assertEqual(limits["maximumPointsPerDevice"], 5000)
        self.assertEqual(limits["maximumRelationshipsPerUnitOfWork"], 10000)
        self.assertEqual(limits["maximumTagsPerUnitOfWork"], 1000)
        self.assertEqual(limits["maximumCommandsPerBatch"], 20000)

    def test_registry_conflict_codes_complete(self) -> None:
        self.assertTrue(CONFLICT_CODES.issubset(set(self.contract["conflictCodes"])))

    def test_registry_forbidden_authorization_decisions(self) -> None:
        self.assertTrue(
            FORBIDDEN_AUTHORIZATION_DECISIONS.issubset(set(self.contract["forbiddenAuthorizationDecisions"]))
        )

    def test_validate_registry_rejects_bad_status(self) -> None:
        bad = dict(self.contract)
        bad["implementationStatus"] = "IMPLEMENTED"
        with self.assertRaises(PersistenceContractError):
            validate_persistence_contract(bad)

    def test_device_provider_is_abstract(self) -> None:
        self.assertTrue(inspect.isabstract(CanonicalDeviceProvider))

    def test_point_provider_is_abstract(self) -> None:
        self.assertTrue(inspect.isabstract(CanonicalPointProvider))

    def test_tag_provider_is_abstract(self) -> None:
        self.assertTrue(inspect.isabstract(CanonicalTagProvider))

    def test_relationship_provider_is_abstract(self) -> None:
        self.assertTrue(inspect.isabstract(CanonicalRelationshipProvider))

    def test_provider_ports_define_required_operations(self) -> None:
        for provider in (
            CanonicalDeviceProvider,
            CanonicalPointProvider,
            CanonicalTagProvider,
        ):
            for method in ("get_by_global_id", "get_by_source_identity", "list_bounded", "stage_create"):
                self.assertTrue(hasattr(provider, method))
        for method in ("get_by_global_id", "list_bounded", "stage_relationship_create"):
            self.assertTrue(hasattr(CanonicalRelationshipProvider, method))

    def test_default_provider_writes_disabled(self) -> None:
        caps = default_provider_capabilities()
        self.assertFalse(caps.enabled_for_canonical_writes)

    def test_command_requires_migration_execution_authority(self) -> None:
        with self.assertRaises(PersistenceContractError):
            _command(requested_by_authority="INVALID")

    def test_command_digest_deterministic(self) -> None:
        one = _command()
        two = _command()
        self.assertEqual(one.command_digest(), two.command_digest())

    def test_command_does_not_expose_raw_idempotency_in_serialize(self) -> None:
        payload = _command().serialize()
        self.assertNotIn("idem-001", json.dumps(payload))
        self.assertIn("idempotencyKeyDigest", payload)

    def test_create_point_command_object_type(self) -> None:
        command = CreateCanonicalPoint(
            **_command_base()
            | {
                "device_global_id": "ag-device-parent",
                "point_type": "ANALOG",
            }
        )
        self.assertEqual(command.object_type(), "Point")

    def test_create_tag_command(self) -> None:
        command = CreateCanonicalTag(
            **_command_base() | {"tag_namespace": "legacy.tags", "tag_value": "value-a"}
        )
        self.assertEqual(command.command_type(), "CreateCanonicalTag")

    def test_create_relationship_command(self) -> None:
        command = CreateCanonicalRelationship(
            **_command_base()
            | {
                "relationship_type": "HAS_POINT",
                "source_global_id": "ag-device-1",
                "target_global_id": "ag-point-1",
            }
        )
        self.assertEqual(command.object_type(), "AssetRelationship")

    def test_synthetic_evidence_denied(self) -> None:
        result = evaluate_persistence_authorization(_auth_input())
        self.assertEqual(result.decision, AUTHORIZATION_DENIED)

    def test_missing_real_evidence_waiting(self) -> None:
        result = evaluate_persistence_authorization(
            _auth_input(evidence_classification="UNKNOWN")
        )
        self.assertEqual(result.decision, AUTHORIZATION_WAITING_REAL_EVIDENCE)

    def test_real_evidence_not_ready_waiting(self) -> None:
        result = evaluate_persistence_authorization(
            _auth_input(
                evidence_classification="REAL_SANITIZED_EVIDENCE",
                readiness_decision="NOT_READY",
            )
        )
        self.assertEqual(result.decision, AUTHORIZATION_WAITING_READINESS)

    def test_real_candidate_without_persistence_approval(self) -> None:
        result = evaluate_persistence_authorization(
            _auth_input(
                evidence_classification="REAL_SANITIZED_EVIDENCE",
                readiness_decision="READY_FOR_READ_MIGRATION_CANDIDATE",
            )
        )
        self.assertEqual(result.decision, AUTHORIZATION_WAITING_PERSISTENCE_APPROVAL)

    def test_matching_real_candidate_with_abstract_approval(self) -> None:
        result = evaluate_persistence_authorization(
            _auth_input(
                evidence_classification="REAL_SANITIZED_EVIDENCE",
                readiness_decision="READY_FOR_READ_MIGRATION_CANDIDATE",
                persistence_approval_granted=True,
                provider_capabilities=enabled_validation_provider_capabilities(),
            )
        )
        self.assertEqual(result.decision, AUTHORIZATION_APPROVED_VALIDATION)

    def test_provider_writes_disabled_denied(self) -> None:
        result = evaluate_persistence_authorization(
            _auth_input(
                evidence_classification="REAL_SANITIZED_EVIDENCE",
                readiness_decision="READY_FOR_READ_MIGRATION_CANDIDATE",
                persistence_approval_granted=True,
            )
        )
        self.assertEqual(result.decision, AUTHORIZATION_DENIED)

    def test_tenant_scope_mismatch(self) -> None:
        result = evaluate_persistence_authorization(
            _auth_input(
                evidence_classification="REAL_SANITIZED_EVIDENCE",
                readiness_decision="READY_FOR_READ_MIGRATION_CANDIDATE",
                persistence_approval_granted=True,
                provider_capabilities=enabled_validation_provider_capabilities(),
                requested_tenant_id="tenant-other",
            )
        )
        self.assertEqual(result.conflict_code, "TENANT_SCOPE_CONFLICT")

    def test_site_scope_mismatch(self) -> None:
        result = evaluate_persistence_authorization(
            _auth_input(
                evidence_classification="REAL_SANITIZED_EVIDENCE",
                readiness_decision="READY_FOR_READ_MIGRATION_CANDIDATE",
                persistence_approval_granted=True,
                provider_capabilities=enabled_validation_provider_capabilities(),
                requested_site_id="site-other",
            )
        )
        self.assertEqual(result.conflict_code, "SITE_SCOPE_CONFLICT")

    def test_evidence_digest_conflict(self) -> None:
        result = evaluate_persistence_authorization(
            _auth_input(
                evidence_classification="REAL_SANITIZED_EVIDENCE",
                readiness_decision="READY_FOR_READ_MIGRATION_CANDIDATE",
                persistence_approval_granted=True,
                provider_capabilities=enabled_validation_provider_capabilities(),
                requested_evidence_digest="0" * 64,
            )
        )
        self.assertEqual(result.conflict_code, "EVIDENCE_DIGEST_CONFLICT")

    def test_idempotency_replay(self) -> None:
        ledger = IdempotencyLedger()
        command = _command()
        first = ledger.evaluate(command)
        ledger.record(command, _command_result(command))
        second = ledger.evaluate(command)
        self.assertEqual(second.status, "IDEMPOTENT_REPLAY")

    def test_idempotency_conflict(self) -> None:
        ledger = IdempotencyLedger()
        command = _command()
        ledger.record(command, _command_result(command))
        other = _command(display_name="Different")
        evaluation = ledger.evaluate(other)
        self.assertEqual(evaluation.status, "IDEMPOTENCY_CONFLICT")

    def test_canonical_identity_already_applied(self) -> None:
        digest = "d" * 64
        result = evaluate_canonical_identity(
            canonical_global_id_digest=digest,
            existing_content_digest=digest,
            incoming_content_digest=digest,
        )
        self.assertEqual(result.status, "ALREADY_APPLIED")

    def test_canonical_identity_conflict(self) -> None:
        result = evaluate_canonical_identity(
            canonical_global_id_digest="x" * 64,
            existing_content_digest="a" * 64,
            incoming_content_digest="b" * 64,
        )
        self.assertEqual(result.conflict_code, "CANONICAL_IDENTITY_CONFLICT")

    def test_stale_expected_version(self) -> None:
        current = CanonicalVersionMetadata(version=2, created_revision="r1", updated_revision="r2")
        self.assertEqual(evaluate_update_version(current=current, expected_version=1), "VERSION_CONFLICT")

    def test_update_version_not_found(self) -> None:
        self.assertEqual(evaluate_update_version(current=None, expected_version=1), "NOT_FOUND")

    def test_identity_immutability_tenant(self) -> None:
        outcome = validate_identity_immutability(
            object_type="Device",
            existing={"tenantId": "tenant-a"},
            incoming={"tenantId": "tenant-b"},
        )
        self.assertEqual(outcome, "IDENTITY_IMMUTABLE")

    def test_point_parent_immutability(self) -> None:
        outcome = validate_identity_immutability(
            object_type="Point",
            existing={"deviceGlobalId": "ag-device-1"},
            incoming={"deviceGlobalId": "ag-device-2"},
        )
        self.assertEqual(outcome, "IDENTITY_IMMUTABLE")

    def test_batch_limit_commands(self) -> None:
        commands = tuple(_command(command_id=f"cmd-{index}") for index in range(20001))
        with self.assertRaises(PersistenceBatchLimitError):
            validate_batch_limits(commands, batch_limits(self.contract))

    def test_uow_device_before_point(self) -> None:
        uow = ContractUnitOfWork(transaction_id="tx-1", tenant_id="tenant-real-001", site_id="site-real-001")
        point = CreateCanonicalPoint(
            **_command_base()
            | {
                "device_global_id": "ag-device-parent",
                "point_type": "ANALOG",
            }
        )
        with self.assertRaises(PersistenceUnitOfWorkError):
            uow.stage(point)

    def test_uow_commit_device_then_point(self) -> None:
        uow = ContractUnitOfWork(transaction_id="tx-1", tenant_id="tenant-real-001", site_id="site-real-001")
        uow.stage(_command())
        uow.stage(
            CreateCanonicalPoint(
                **_command_base()
                | {
                    "device_global_id": "ag-device-parent",
                    "point_type": "ANALOG",
                    "command_id": "cmd-point-1",
                }
            )
        )
        payload = uow.commit()
        self.assertEqual(payload["status"], "COMMITTED")

    def test_dependent_point_failure_requires_rollback(self) -> None:
        coordinator = AssetGraphPersistenceCoordinator(audit_port=InMemoryAuditProvider())
        device = _command(command_id="cmd-device")
        point = CreateCanonicalPoint(
            **_command_base()
            | {
                "device_global_id": "ag-device-parent",
                "point_type": "ANALOG",
                "command_id": "cmd-point",
                "idempotency_key": "idem-point",
            }
        )
        result = coordinator.execute_batch(
            PersistenceCoordinatorInput(
                authorization=_auth_input(
                    evidence_classification="REAL_SANITIZED_EVIDENCE",
                    readiness_decision="READY_FOR_READ_MIGRATION_CANDIDATE",
                    persistence_approval_granted=True,
                    provider_capabilities=enabled_validation_provider_capabilities(),
                ),
                commands=(device, point),
                contract=self.contract,
                simulate_point_failure=True,
            )
        )
        self.assertEqual(result.status, "ROLLED_BACK")
        self.assertTrue(result.rollback_required)

    def test_audit_failure_fails_closed(self) -> None:
        coordinator = AssetGraphPersistenceCoordinator(audit_port=InMemoryAuditProvider())
        result = coordinator.execute_batch(
            PersistenceCoordinatorInput(
                authorization=_auth_input(
                    evidence_classification="REAL_SANITIZED_EVIDENCE",
                    readiness_decision="READY_FOR_READ_MIGRATION_CANDIDATE",
                    persistence_approval_granted=True,
                    provider_capabilities=enabled_validation_provider_capabilities(),
                ),
                commands=(_command(),),
                contract=self.contract,
                audit_should_fail=True,
            )
        )
        self.assertEqual(result.status, "FAILED")
        self.assertTrue(result.rollback_required)

    def test_conflict_result_safe_message(self) -> None:
        conflict = conflict_result(
            conflict_code="VERSION_CONFLICT",
            object_type="Device",
            safe_message="Expected version does not match current canonical version.",
        )
        payload = conflict.serialize()
        self.assertNotIn("password", json.dumps(payload))
        self.assertTrue(payload["blocking"])

    def test_rollback_result_guarantees(self) -> None:
        rollback = build_rollback_result(
            transaction_id="tx-rollback",
            trigger="auditFailure",
            idempotency_reservations_released=1,
        )
        self.assertIn("noPartialCanonicalGraph", rollback.guarantees)

    def test_authorization_result_digest_deterministic(self) -> None:
        one = evaluate_persistence_authorization(_auth_input()).serialize()
        two = evaluate_persistence_authorization(_auth_input()).serialize()
        self.assertEqual(one, two)

    def test_command_result_no_raw_idempotency_key(self) -> None:
        coordinator = AssetGraphPersistenceCoordinator(audit_port=InMemoryAuditProvider())
        result = coordinator.execute_batch(
            PersistenceCoordinatorInput(
                authorization=_auth_input(
                    evidence_classification="REAL_SANITIZED_EVIDENCE",
                    readiness_decision="READY_FOR_READ_MIGRATION_CANDIDATE",
                    persistence_approval_granted=True,
                    provider_capabilities=enabled_validation_provider_capabilities(),
                ),
                commands=(_command(),),
                contract=self.contract,
            )
        )
        blob = json.dumps(result.serialize())
        self.assertNotIn("idem-001", blob)

    def test_no_db_imports_in_module(self) -> None:
        module_dir = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/persistence_contract"
        text = "\n".join(path.read_text(encoding="utf-8") for path in module_dir.rglob("*.py"))
        for token in ("sqlalchemy", "db.session", "CREATE TABLE", "INSERT INTO", "prisma"):
            self.assertNotIn(token.lower(), text.lower())

    def test_no_public_api_routes(self) -> None:
        module_dir = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/persistence_contract"
        text = "\n".join(path.read_text(encoding="utf-8") for path in module_dir.rglob("*.py"))
        self.assertNotIn("@api_bp.route", text)

    def test_write_cutover_unavailable_in_results(self) -> None:
        result = evaluate_persistence_authorization(_auth_input())
        self.assertEqual(result.write_cutover_status, "NOT_READY_FOR_WRITE_CUTOVER")

    def test_real_readiness_assessment_candidate(self) -> None:
        self.assertEqual(self.real_assessment["decision"], "READY_FOR_READ_MIGRATION_CANDIDATE")

    def test_clean_synthetic_not_candidate(self) -> None:
        self.assertNotEqual(self.clean_assessment["decision"], "READY_FOR_READ_MIGRATION_CANDIDATE")

    def test_update_device_command(self) -> None:
        command = UpdateCanonicalDevice(**_command_base() | {"requested_operation": "Update", "expected_version": 1, "display_name": "Updated"})
        self.assertEqual(command.command_type(), "UpdateCanonicalDevice")

    def test_uow_version_conflict_on_update(self) -> None:
        uow = ContractUnitOfWork(transaction_id="tx-1", tenant_id="tenant-real-001", site_id="site-real-001")
        uow.stage(_command())
        uow.commit()
        uow2 = ContractUnitOfWork(transaction_id="tx-2", tenant_id="tenant-real-001", site_id="site-real-001")
        uow2.stage(
            UpdateCanonicalDevice(
                **_command_base()
                | {"requested_operation": "Update", "expected_version": 99, "display_name": "Updated"}
            )
        )
        errors = uow2.validate_staged()
        self.assertTrue(errors)

    def test_coordinator_rejects_unauthorized_synthetic(self) -> None:
        coordinator = AssetGraphPersistenceCoordinator(audit_port=InMemoryAuditProvider())
        result = coordinator.execute_batch(
            PersistenceCoordinatorInput(
                authorization=_auth_input(),
                commands=(_command(),),
                contract=self.contract,
            )
        )
        self.assertEqual(result.status, "REJECTED")

    def test_provider_capability_serialization(self) -> None:
        caps = default_provider_capabilities().serialize()
        self.assertFalse(caps["enabledForCanonicalWrites"])

    def test_relationship_endpoint_integrity_conflict_code_present(self) -> None:
        self.assertIn("RELATIONSHIP_ENDPOINT_CONFLICT", CONFLICT_CODES)

    def test_mapping_version_conflict(self) -> None:
        result = evaluate_persistence_authorization(
            _auth_input(
                evidence_classification="REAL_SANITIZED_EVIDENCE",
                readiness_decision="READY_FOR_READ_MIGRATION_CANDIDATE",
                persistence_approval_granted=True,
                provider_capabilities=enabled_validation_provider_capabilities(),
                requested_mapping_version="unsupported",
            )
        )
        self.assertEqual(result.conflict_code, "MAPPING_VERSION_CONFLICT")

    def test_readiness_digest_conflict(self) -> None:
        result = evaluate_persistence_authorization(
            _auth_input(
                evidence_classification="REAL_SANITIZED_EVIDENCE",
                readiness_decision="READY_FOR_READ_MIGRATION_CANDIDATE",
                persistence_approval_granted=True,
                provider_capabilities=enabled_validation_provider_capabilities(),
                requested_readiness_result_digest="0" * 64,
            )
        )
        self.assertEqual(result.conflict_code, "READINESS_DIGEST_CONFLICT")

    def test_execution_digest_conflict(self) -> None:
        result = evaluate_persistence_authorization(
            _auth_input(
                evidence_classification="REAL_SANITIZED_EVIDENCE",
                readiness_decision="READY_FOR_READ_MIGRATION_CANDIDATE",
                persistence_approval_granted=True,
                provider_capabilities=enabled_validation_provider_capabilities(),
                requested_execution_result_digest="0" * 64,
            )
        )
        self.assertEqual(result.conflict_code, "EXECUTION_DIGEST_CONFLICT")

    def test_tag_namespace_conflict_code_present(self) -> None:
        self.assertIn("TAG_NAMESPACE_CONFLICT", CONFLICT_CODES)

    def test_transaction_result_deterministic(self) -> None:
        coordinator = AssetGraphPersistenceCoordinator(audit_port=InMemoryAuditProvider())
        auth = _auth_input(
            evidence_classification="REAL_SANITIZED_EVIDENCE",
            readiness_decision="READY_FOR_READ_MIGRATION_CANDIDATE",
            persistence_approval_granted=True,
            provider_capabilities=enabled_validation_provider_capabilities(),
        )
        payload = PersistenceCoordinatorInput(authorization=auth, commands=(_command(),), contract=self.contract)
        one = coordinator.execute_batch(payload).serialize()
        two = AssetGraphPersistenceCoordinator(audit_port=InMemoryAuditProvider()).execute_batch(payload).serialize()
        self.assertEqual(one["resultDigest"], two["resultDigest"])


if __name__ == "__main__":
    unittest.main()
