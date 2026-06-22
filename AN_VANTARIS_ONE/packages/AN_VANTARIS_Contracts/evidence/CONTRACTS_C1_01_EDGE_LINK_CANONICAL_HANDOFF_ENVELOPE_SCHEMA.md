# CONTRACTS-C1-01 — EDGE-LINK Canonical Handoff Envelope Schema

Status: PASS
Scope: AN_VANTARIS_Contracts only
Date: 2026-06-20

## 1. Purpose

This evidence defines the shared EDGE-LINK canonical handoff envelope schema.

The schema promotes the core EDGE-to-LINK handoff shape from internal module
contracts into a shared, versioned contract under AN_VANTARIS_Contracts.

## 2. Schema Added

Added schema:

- AN_VANTARIS_Contracts/schemas/edge-link/edge-link-canonical-handoff-envelope.v1.json

## 3. Coverage

The schema covers:

- schemaVersion
- envelopeId
- recordType
- trace
- source
- asset reference
- location reference
- reliability
- streamId
- sequenceNumber
- payloadHash
- dedupeKey
- stable suppression metadata
- normalized payload
- production state
- evidenceRefs
- boundary flags

## 4. Boundary

This task does not modify EDGE runtime.

This task does not modify LINK runtime.

This task does not implement VANTARIS ONE, UMMS, UCDE, or UFMS runtime.

This task does not change DB/schema/migration/auth/login/credentials.

This task does not enable production delivery.

This task does not enable EDGE runtime.

## 5. Result

CONTRACTS_C1_01_EDGE_LINK_CANONICAL_HANDOFF_ENVELOPE_SCHEMA_PASS

Shared EDGE-LINK canonical handoff envelope schema is now defined.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
