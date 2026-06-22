# LINK-C1-04 — LINK Architecture Freeze

Status: PASS
Scope: AN_VANTARIS_LINK only
Date: 2026-06-20

## 1. Purpose

This evidence freezes the architectural role of AN_VANTARIS_LINK after
AN_VANTARIS_EDGE final handoff closure.

AN_VANTARIS_LINK is defined as the secure delivery gateway and integration
runtime between frozen EDGE output and upper-layer UFMS / Code / APP Layer APIs.

This freeze prevents LINK from drifting into device collection, protocol
adaptation, EDGE runtime ownership, UFMS business logic, or direct database
access.

## 2. LINK Product Role

AN_VANTARIS_LINK is:

- Secure Delivery Gateway
- Integration Runtime
- EDGE-to-UFMS transport boundary
- Queue / retry / DLQ / delivery orchestration layer
- Audit and evidence layer for data handoff
- Policy gate for approved endpoint delivery

AN_VANTARIS_LINK is not:

- A device collector
- A protocol adapter
- An EDGE connector registry
- A UFMS business service
- A database writer
- A replacement for UFMS APP Layer APIs
- A production enablement approval authority

## 3. System Boundary

Allowed LINK responsibilities:

- Receive EDGE normalized transport events
- Validate ingress security and transport headers
- Validate protocol version, gatewayId, timestamp, and signature
- Route events by partition
- Queue events
- Apply backpressure policy
- Perform delivery attempts to approved upper-layer APIs
- Apply retry policy
- Route exhausted or rejected events to DLQ
- Produce ACK / RETRY / DLQ delivery receipts
- Commit delivery offsets
- Produce local evidence and audit records
- Support diagnostics and deployment health checks in later stages

Prohibited LINK responsibilities:

- Direct UFMS database access
- EDGE adapter modification
- EDGE runtime modification
- EDGE connector registry modification
- EDGE package modification
- Writeback to OT / device / source system
- Unapproved production delivery
- Credential material storage in source code
- Bypassing UFMS APP Layer APIs
- Modifying UFMS schemas, migrations, auth, login, or credentials

## 4. EDGE Frozen State Preserved

LINK must preserve the following EDGE handoff state:

- EDGE Runtime: Not Enabled
- EDGE Pilot: Not Approved
- EDGE Production: Not Approved
- EDGE Writeback: Prohibited
- EDGE Direct UFMS DB Access: Prohibited
- EDGE LINK Bypass: Prohibited

Until a later controlled pilot enablement gate is approved, LINK behavior must
remain limited to dry-run, synthetic delivery, local validation, local queue,
local evidence, and non-production delivery mode.

## 5. Architecture Layers

LINK architecture is frozen into the following layers:

### Layer 1 — Ingress Security

Responsibilities:

- Zone 1 EDGE to Zone 2 LINK transition validation
- Header extraction
- Wire JSON parsing
- Protocol version validation
- Gateway identity validation
- Timestamp skew validation
- Signature validation
- Future EDGE handoff state validation

### Layer 2 — Handoff Contract

Responsibilities:

- Represent EDGE normalized read-only records
- Represent EDGE evidence metadata
- Represent EDGE blocked production state
- Represent endpoint approval reference
- Represent credential reference without storing secrets
- Represent traceId / correlationId / eventId / gatewayId

### Layer 3 — Partition and Queue

Responsibilities:

- Partition routing
- Partitioned queues
- Backpressure control
- Queue state tracking
- Future durable local queue
- Future queue recovery

### Layer 4 — Delivery Orchestration

Responsibilities:

- Approved target routing
- Single-attempt dispatch
- Idempotency support
- ACK mapping
- Offset commit
- Non-blocking retry scheduling

### Layer 5 — Retry and DLQ

Responsibilities:

- Retry decision
- Backoff recommendation
- Exhaustion handling
- DLQ movement
- DLQ reason taxonomy
- Future replay authorization

### Layer 6 — Evidence and Audit

Responsibilities:

- Delivery evidence
- Security rejection evidence
- Queue and DLQ evidence
- Offset commit evidence
- C-stage aggregate gates

### Layer 7 — Operations and Deployment

Responsibilities for later stages:

- Health CLI
- Ready CLI
- Queue summary CLI
- DLQ summary CLI
- Diagnostic bundle
- Offline install package
- Upgrade / rollback
- systemd service template
- package integrity validation

## 6. EDGE Matching Requirements

LINK development must match the frozen EDGE handoff concepts:

- normalized read-only records
- connector decision state
- adapter evidence reports
- blocked runtime state
- blocked pilot state
- blocked production state
- writeback prohibited state
- endpoint approval schema
- credential reference schema
- rollback plan schema
- operator authorization schema
- evidence collection schema

LINK must not require EDGE changes unless a confirmed blocking gap is found.

If a blocking EDGE gap is found, LINK work pauses and a controlled EDGE-C8 gap
patch task must be opened.

## 7. GA Deployment Requirements

Before International GA, LINK must prove:

- EDGE-compatible ingress contract
- security validation
- replay / timestamp / signature protection
- queue state model
- partition isolation
- durable queue or equivalent recovery plan
- retry and DLQ taxonomy
- ACK lifecycle
- idempotent delivery
- no direct DB access
- no credential leakage
- evidence and audit chain
- health and diagnostics
- offline deployment package
- rollback capability
- EDGE-LINK integration readiness

## 8. Development Route Freeze

LINK development route is frozen as:

1. LINK-C1 Baseline / Alignment / Architecture Freeze
2. LINK-C2 Ingress Contract & Security Alignment
3. LINK-C3 Queue / Partition / Durable State
4. LINK-C4 Delivery / ACK / Idempotency
5. LINK-C5 Retry / DLQ Taxonomy
6. LINK-C6 Audit / Evidence
7. LINK-C7 Runtime Operations
8. LINK-C8 Offline Deployment Package
9. LINK-C9 EDGE-LINK Integration Readiness

## 9. Current C1 Result

Completed before this freeze:

- LINK-C1-00 Baseline & Boundary Reconfirmation
- LINK-C1-01 EDGE Handoff Consumption Inventory
- LINK-C1-02 Source Readiness Inspection
- LINK-C1-03 EDGE Handoff Alignment Matrix

Current result:

- LINK can continue.
- EDGE remains frozen.
- No confirmed EDGE blocking gap exists at C1-04.
- LINK production delivery remains blocked.

## 10. Result

LINK_C1_04_LINK_ARCHITECTURE_FREEZE_PASS

LINK may continue to LINK-C1-05 C1 Aggregate Gate.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
