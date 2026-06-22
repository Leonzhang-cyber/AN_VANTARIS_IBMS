# EDGE C3-00 Real Protocol Readiness Gate

## A. Scope

C3-00 is a pre-implementation readiness gate for real protocol introduction. This phase defines policy, boundaries, validation gates, and rollout order. It is not a real protocol implementation phase.

## B. Current C2 foundation baseline

The C2 baseline is frozen with the following milestones completed:

- C2-01 Connector Manager
- C2-02 Protocol Plugin Runtime
- C2-03 Normalization and Edge Envelope Pipeline
- C2-04 Local Buffer Staging
- C2-05 Local Delivery Orchestrator
- C2-06 Delivery Audit Chain
- C2-07 Foundation Freeze Report
- C2-08 Validation Tooling Hygiene

## C. C2 commit baseline

- `4a17d05` C2-01
- `ee674d2` C2-02
- `8571666` C2-03
- `123bf73` C2-04
- `c487c78` C2-05
- `2f78b17` C2-06
- `b1850ac` C2-07
- `28f0c8b` C2-08

## D. Real protocol candidate list

- SNMP
- Modbus TCP
- BACnet/IP
- OPC UA
- OPC TCP/IP
- HTTP polling
- File import connector
- Simulator remains reference plugin

## E. Recommended protocol introduction order

1. File import connector
2. HTTP polling connector
3. SNMP read-only
4. Modbus TCP read-only
5. BACnet/IP read-only
6. OPC UA read-only
7. OPC TCP/IP read-only

Rationale:

- File/HTTP first validates real input paths without requiring field device dependencies.
- SNMP is the first recommended OT/network read-only protocol gate.
- Modbus/BACnet/OPC UA/OPC TCP all start as read-only.
- Writeback is disabled by default.

## F. Protocol dependency policy

- Each real protocol dependency must pass an independent gate.
- Introducing multiple protocol libraries in one change is prohibited.
- Each protocol must have a dedicated feature flag.
- Each protocol must be fully disable-able.
- Each protocol must keep simulator fallback available.
- All real protocols default to read-only mode.
- Default write control/writeback is prohibited.
- Hardcoded customer IP/port/token/username/password is prohibited.
- Default smoke must not connect to real devices.
- CI/smoke must not depend on field network availability.

## G. Runtime boundary policy

All real protocol runtime paths in C3 must remain inside the established chain:

Protocol Plugin Runtime
→ Normalization Pipeline
→ Edge Envelope
→ Local Buffer
→ Local Delivery Orchestrator
→ Audit Chain

Bypass is prohibited for:

- `connector-manager`
- `normalization-pipeline`
- `edge-envelope-builder`
- `local-buffer-store`
- `delivery-audit-chain`

## H. Security gate

- read-only first
- least privilege
- no credential commit
- no customer data commit
- no raw secret in logs
- no real endpoint in example config
- protocol timeout required
- retry/backoff required
- audit event required
- device connection failure must not crash runtime
- failed connector must go quarantine/failed state

## I. Validation matrix

Every real protocol stage must pass:

- typecheck edge/link/edge-link
- validate-edge-package
- edge-boundary-scan
- validate-ufms-ibms-isolation
- C2 foundation freeze smoke
- protocol-specific dry-run
- protocol-specific smoke
- no `.runtime` tracked
- no forbidden package modifications
- no credential leak scan

## J. C3 phase plan

- C3-01 File Import Connector Foundation
- C3-02 HTTP Polling Connector Foundation
- C3-03 SNMP Read-only Connector Gate
- C3-04 SNMP Read-only Runtime
- C3-05 Modbus TCP Read-only Gate
- C3-06 Modbus TCP Read-only Runtime
- C3-07 BACnet/IP Read-only Gate
- C3-08 OPC UA Read-only Gate
- C3-09 Protocol Integration Freeze

## K. Not included in C3-00

- no real protocol library
- no real device connection
- no LINK delivery
- no DB write
- no UFMS API call
- no credential handling implementation
- no production deployment change
- no config schema migration
- no frontend/backend changes

## L. Final readiness key

`UFMS_EDGE_C3_00_REAL_PROTOCOL_READINESS_GATE_PASS`
