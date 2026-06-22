# EDGE C3-05 BACnet/IP Read-only Connector Foundation Report

## Scope

Introduce BACnet/IP read-only connector foundation with local-safe synthetic fixture processing only.

## Boundary

Changes are limited to `AN_VANTARIS_EDGE/**` and do not modify LINK, DB, Console, Code, Contracts, NexusAI, backend, or frontend modules.

## Read-only guarantees

- `networkEnabled=false` is enforced in config validation.
- `supportsWriteback=false` is enforced in config and plugin capability.
- no write property or write multiple operation is implemented.

## Synthetic fixture design

Fixture includes:

- connector and protocol metadata (`bacnet-ip-readonly`)
- synthetic device metadata
- point list with `objectType`, `objectInstance`, `propertyIdentifier`, `presentValue`-style readings, unit, status, and timestamp

## No real device / no UDP / no 47808 statement

- no UDP socket creation
- no bind/send path
- no real BACnet discovery
- no Who-Is broadcast implementation
- no I-Am listener implementation
- no real port 47808 access

## No LINK / DB / UFMS API statement

- plugin does not call LINK runtime
- plugin does not call DB/database client
- plugin does not call UFMS API

## Dry-run cases

- CASE 1 — bacnet config validation
- CASE 2 — safe host validation
- CASE 3 — network disabled validation
- CASE 4 — fixture path allowlist
- CASE 5 — fixture parse
- CASE 6 — malformed fixture handling
- CASE 7 — bacnet object mapping validation
- CASE 8 — bacnet plugin pollOnce
- CASE 9 — normalization pipeline
- CASE 10 — edge envelope builder
- CASE 11 — local buffer ingest
- CASE 12 — delivery preview
- CASE 13 — audit chain
- CASE 14 — no prohibited integration

## Smoke validation summary

Lightweight smoke validates only C3-05 BACnet/IP foundation files and markers, runs C3-05 dry-run once, checks `.runtime` git hygiene, and outputs readiness key.

## Readiness key

`UFMS_EDGE_C3_05_BACNET_IP_READONLY_CONNECTOR_FOUNDATION_PASS`
