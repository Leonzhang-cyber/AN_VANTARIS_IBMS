# EDGE C3-06 OPC UA Read-only Connector Foundation Report

## Scope

Introduce OPC UA read-only connector foundation with local-safe synthetic fixture processing only.

## Shared EDGE Foundation boundary

Changes are limited to `AN_VANTARIS_EDGE/**` and do not modify LINK, DB, Console, Code, Contracts, NexusAI, backend, or frontend modules.

## Synthetic fixture design

Fixture defines:

- `connectorId`, `protocol`, `networkEnabled`
- `endpointUrl`, `securityMode=None`, `securityPolicy=None`
- `namespaceUri`, `serverApplicationUri`
- `nodes` with point metadata and typed values

## Read-only guarantees

- `networkEnabled=false` is enforced.
- `supportsWriteback=false` is enforced.
- no write service logic is implemented.

## No real OPC UA connection

- no real server connection path
- no secure channel creation
- no session creation
- no subscription or monitored item creation

## No port 4840 access

Endpoint values are treated as configuration data only. No network access is executed for port 4840.

## No endpoint discovery/session/subscription

No endpoint discovery and no runtime session/subscription lifecycle code are included in C3-06.

## No Write service

No `WriteRequest`, `session.write`, `writeSingleNode`, `writeMultipleNodes`, or method invocation path is present.

## No LINK/DB/UFMS API

No LINK delivery, DB write, or UFMS API call is implemented by the C3-06 connector foundation.

## Dry-run cases

- CASE 1 — opc ua config validation
- CASE 2 — safe endpoint validation
- CASE 3 — network disabled validation
- CASE 4 — fixture path allowlist
- CASE 5 — fixture parse
- CASE 6 — malformed fixture handling
- CASE 7 — opc ua node mapping validation
- CASE 8 — opc ua plugin pollOnce
- CASE 9 — normalization pipeline
- CASE 10 — edge envelope builder
- CASE 11 — local buffer ingest
- CASE 12 — delivery preview
- CASE 13 — audit chain
- CASE 14 — no prohibited integration

## Lightweight smoke result

Lightweight smoke validates only C3-06 OPC UA files and markers, runs C3-06 dry-run once, checks `.runtime` git hygiene, and prints readiness key.

## Readiness key

`UFMS_EDGE_C3_06_OPC_UA_READONLY_CONNECTOR_FOUNDATION_PASS`
