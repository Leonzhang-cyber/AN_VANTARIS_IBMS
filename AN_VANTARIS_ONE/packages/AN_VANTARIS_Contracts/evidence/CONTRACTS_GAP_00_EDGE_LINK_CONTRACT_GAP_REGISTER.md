# CONTRACTS-GAP-00 — EDGE / LINK Contract Gap Register

Status: PASS_WITH_GAPS
Scope: AN_VANTARIS_EDGE / AN_VANTARIS_LINK / AN_VANTARIS_Contracts only
Date: 2026-06-20

## 1. Purpose

This evidence records the contract completeness assessment for EDGE and LINK after:

- EDGE P0 Reliability and Diagnostics Aggregate Gate
- LINK C7 Runtime Operations / Diagnostics Aggregate Gate

The goal is to determine which contracts are complete as internal module contracts,
which contracts should be promoted to shared AN_VANTARIS_Contracts, and which
airport scenario contracts remain to be added.

This task does not implement VANTARIS ONE, UMMS, UCDE, UFMS backend/frontend,
database schema, authentication, login, credentials, or production runtime.

## 2. Current Allowed Scope

Allowed scope:

- AN_VANTARIS_EDGE/**
- AN_VANTARIS_LINK/**
- AN_VANTARIS_Contracts/**

Forbidden scope:

- VANTARIS ONE runtime or UI
- UMMS runtime or UI
- UCDE runtime or UI
- UFMS backend/frontend
- DB/schema/migration
- auth/login/credentials
- production delivery enablement
- EDGE runtime enablement
- writeback to OT/device/source system

## 3. Current EDGE Internal Contract Coverage

EDGE internal contracts currently cover:

- stable value suppression
- change detection
- deadband
- heartbeatDue
- suppressedCount
- EDGE outbox reliability
- streamId
- sequenceNumber
- ACK tracking
- retry / replay request
- heartbeat / LINK liveness
- health snapshot
- diagnostics bundle

Assessment:

- EDGE P0 reliability contracts: COMPLETE for internal foundation
- EDGE runtime enablement: NOT ENABLED
- EDGE production use: NOT APPROVED
- EDGE airport-specific source-system contracts: GAP
- EDGE shared external schemas: GAP

## 4. Current LINK Internal Contract Coverage

LINK internal contracts currently cover:

- ingress intake
- security taxonomy
- production state guard
- queue state
- queue item
- partition / priority
- durable queue / recovery
- delivery target
- EDGE-LINK reliability
- delivery idempotency
- delivery attempt / receipt
- production delivery block guard
- retry policy
- retry decision
- DLQ taxonomy
- DLQ movement
- audit event
- evidence chain
- runtime health snapshot
- runtime diagnostics bundle

Assessment:

- LINK internal GA foundation contracts: COMPLETE through C7
- LINK production delivery: BLOCKED
- LINK offline deployment package: GAP
- LINK EDGE-LINK integration readiness: GAP
- LINK shared external schemas: GAP
- LINK airport-specific envelope contracts: GAP

## 5. Shared Contract Gap Register

The following shared contracts should be added to AN_VANTARIS_Contracts before
external consumers or engineering teams rely on the interfaces.

| Gap ID | Contract | Current status | Required action |
|---|---|---|---|
| CONTRACT-GAP-001 | EDGE-LINK Canonical Handoff Envelope | Internal only | Promote shared schema |
| CONTRACT-GAP-002 | EDGE-LINK ACK / Replay / Reliability Schema | Internal only | Promote shared schema |
| CONTRACT-GAP-003 | EDGE Heartbeat / Health / Diagnostics Schema | Internal only | Promote shared schema |
| CONTRACT-GAP-004 | LINK Delivery / Idempotency / Receipt Schema | Internal only | Promote shared schema |
| CONTRACT-GAP-005 | LINK Audit / Evidence Chain Schema | Internal only | Promote shared schema |
| CONTRACT-GAP-006 | Airport Source System Profile Schema | Missing | Add airport shared schema |
| CONTRACT-GAP-007 | Airport ELV Connector Matrix Schema | Missing | Add airport shared schema |
| CONTRACT-GAP-008 | Airport Tag Mapping / Normalization Schema | Missing | Add airport shared schema |
| CONTRACT-GAP-009 | Airport Asset / Location / HMI Locator Metadata Schema | Missing | Add airport shared schema |
| CONTRACT-GAP-010 | Existing System Onboarding Packet Schema | Missing | Add airport shared schema |
| CONTRACT-GAP-011 | Work Order Trigger Envelope Boundary | Missing | Add boundary only; no UMMS implementation |
| CONTRACT-GAP-012 | VANTARIS ONE Airport Projection Boundary | Missing | Add boundary only; no ONE implementation |
| CONTRACT-GAP-013 | UCDE Evidence Review Package Boundary | Missing | Add boundary only; no UCDE implementation |
| CONTRACT-GAP-014 | UFMS APP API Delivery Boundary | Missing | Add boundary only; no UFMS runtime change |

## 6. Airport Scenario Contract Requirements

Airport scenario should be used only as a validation input for EDGE / LINK.

Required airport-facing contracts:

- airport source-system profile
- airport ELV connector matrix
- existing system onboarding packet
- tag mapping / normalization
- asset / location reference
- HMI locator metadata
- source system health summary
- work-order trigger envelope boundary
- evidence review package boundary

These contracts must not implement VANTARIS ONE, UMMS, UCDE, or UFMS runtime.

## 7. Contract Layering Decision

Contracts must be separated into three layers:

### 7.1 Internal Module Contracts

Location:

- AN_VANTARIS_EDGE/src/runtime/contracts/**
- AN_VANTARIS_LINK/src/link/contracts/**

Purpose:

- Module implementation and validation
- Internal type safety
- Local validation harnesses

### 7.2 Shared Foundation Contracts

Location:

- AN_VANTARIS_Contracts/**

Purpose:

- Stable EDGE-LINK shared schemas
- External engineering alignment
- Vendor / airport integration documentation
- Future package-level compatibility

### 7.3 Future Consumer Boundary Contracts

Location:

- AN_VANTARIS_Contracts/**

Purpose:

- Define future consumer expectations only
- No VANTARIS ONE implementation
- No UMMS implementation
- No UCDE implementation
- No UFMS runtime changes

## 8. Recommended Next Tasks

Recommended sequence:

1. CONTRACTS-C1-01 EDGE-LINK Canonical Handoff Envelope Schema
2. CONTRACTS-C1-02 EDGE-LINK Reliability / ACK / Replay Schema
3. CONTRACTS-C1-03 EDGE Heartbeat / Health / Diagnostics Schema
4. CONTRACTS-C1-04 LINK Delivery / Idempotency / Receipt Schema
5. CONTRACTS-C1-05 LINK Audit / Evidence Chain Schema
6. EDGE-AIRPORT-E1 EDGE Airport Source-System Connector Matrix
7. EDGE-AIRPORT-E2 EDGE Existing System Onboarding Contract
8. EDGE-AIRPORT-E3 EDGE Tag Mapping / Normalization Contract

## 9. Boundary Decision

This register does not authorize work outside EDGE, LINK, or Contracts.

Airport project context is used only to validate and improve EDGE/LINK contracts.

No VANTARIS ONE, UMMS, UCDE, or UFMS runtime work is included.

## 10. Result

CONTRACTS_GAP_00_EDGE_LINK_CONTRACT_GAP_REGISTER_PASS_WITH_GAPS

Contracts are not yet fully complete for external/shared GA use.

Internal EDGE/LINK contracts are strong.

Shared AN_VANTARIS_Contracts schemas must be added before external consumers rely
on the interfaces.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
