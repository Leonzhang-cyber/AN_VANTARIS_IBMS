# CONTRACTS-C1-05 — LINK Audit / Evidence Chain Schema

Status: PASS
Scope: AN_VANTARIS_Contracts only
Date: 2026-06-20

## 1. Purpose

This evidence defines the shared LINK audit / evidence chain schema.

The schema promotes LINK audit event, evidence record, chain hash, tamper-evident
linkage, actor, target, result, and boundary evidence concepts from internal LINK
contracts into a shared, versioned contract under AN_VANTARIS_Contracts.

## 2. Schema Added

Added schema:

- AN_VANTARIS_Contracts/schemas/edge-link/link-audit-evidence-chain.v1.json

## 3. Coverage

The schema covers:

- chainId
- recordId
- recordType
- auditEvent
- audit event type
- actor
- machine identity reference
- target
- result
- evidenceId
- evidenceType
- evidence source
- evidence hash
- previousHash
- currentHash
- chainIndex
- tamperEvident=true
- verificationStatus
- delivery / retry / DLQ / diagnostics / health related references
- retention metadata
- containsSecretMaterial=false
- boundary flags

## 4. Boundary

This task does not modify LINK runtime.

This task does not modify EDGE runtime.

This task does not implement VANTARIS ONE, UMMS, UCDE, or UFMS runtime.

This task does not change DB/schema/migration/auth/login/credentials.

This task does not enable production delivery.

This task does not allow writeback.

This task does not allow direct UFMS DB access.

This task does not include secret material.

## 5. Result

CONTRACTS_C1_05_LINK_AUDIT_EVIDENCE_CHAIN_SCHEMA_PASS

Shared LINK audit / evidence chain schema is now defined.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
