# Canonical Schema Index v1

## 1. Purpose

Provide a single index for VANTARIS ONE canonical JSON schemas and examples used by UFMS/EDGE/LINK/Code/DB/Console/NexusAI.

## 2. Object families

- Hierarchy: tenant, site, building, floor, space
- Integration: gateway, connector, source-system
- Asset graph: asset, device, point
- Runtime signals: telemetry, event, alarm, evidence, health, throughput
- Operations/governance: sync-batch, audit, config-version

## 3. Schema list

- `schemas/common-identifiers-v1.schema.json`
- `schemas/common-trace-context-v1.schema.json`
- `schemas/common-audit-fields-v1.schema.json`
- `schemas/common-health-status-v1.schema.json`
- `schemas/tenant-v1.schema.json`
- `schemas/site-v1.schema.json`
- `schemas/building-v1.schema.json`
- `schemas/floor-v1.schema.json`
- `schemas/space-v1.schema.json`
- `schemas/gateway-v1.schema.json`
- `schemas/connector-v1.schema.json`
- `schemas/source-system-v1.schema.json`
- `schemas/asset-v1.schema.json`
- `schemas/device-v1.schema.json`
- `schemas/point-v1.schema.json`
- `schemas/telemetry-v1.schema.json`
- `schemas/event-v1.schema.json`
- `schemas/alarm-v1.schema.json`
- `schemas/evidence-v1.schema.json`
- `schemas/health-v1.schema.json`
- `schemas/throughput-v1.schema.json`
- `schemas/sync-batch-v1.schema.json`
- `schemas/audit-v1.schema.json`
- `schemas/config-version-v1.schema.json`

## 4. Example list

Canonical examples are under `dto-examples/canonical/` with one file per object.

## 5. Consumer guidance

- EDGE/LINK consume canonical IDs and trace fields via generated consumers and protocol schemas.
- Code uses canonical objects for normalization, orchestration, and persistence boundaries.
- DB maps canonical objects to implementation tables without redefining canonical meaning.
- Console and NexusAI consume canonical shapes via Code-facing contracts.

## 6. Contract rule

Runtime packages must not redefine canonical identifiers independently. Canonical identifiers are authoritative in `AN_VANTARIS_Contracts`.
