# Canonical Object Model v1

Baseline object families for VANTARIS ONE platform contracts.

| Object | Purpose | Primary identifier | Owner domain | Consumers | Priority |
|--------|---------|--------------------|--------------|-----------|----------|
| Tenant | Multi-tenant boundary root | `tenantId` | Platform | EDGE, LINK, Code, DB, Console, NexusAI | P0 |
| Site | Facility/site scope | `siteId` | Platform | EDGE, LINK, Code, DB, Console, NexusAI | P0 |
| Building | Building structure context | `buildingId` | UFMS profile | EDGE, Code, DB, Console | P1 |
| Floor | Floor-level context | `floorId` | UFMS profile | Code, DB, Console | P1 |
| Space | Room/zone context | `spaceId` | UFMS profile | Code, DB, Console, NexusAI | P1 |
| Gateway | Edge gateway identity | `gatewayId` | EDGE/LINK profile | EDGE, LINK, Code, DB | P0 |
| Connector | Integration connector identity | `connectorId` | EDGE/LINK profile | EDGE, LINK, Code, DB, Console | P0 |
| SourceSystem | Upstream system reference | `sourceSystemId` | EDGE/LINK profile | EDGE, LINK, Code, DB, Console | P1 |
| Asset | Managed physical/logical asset | `assetId` | UFMS profile | EDGE, LINK, Code, DB, Console, NexusAI | P1 |
| Device | Device-level representation | `deviceId` | EDGE/LINK profile | EDGE, LINK, Code, DB, Console | P0 |
| Point | Sensor/point channel | `pointId` | EDGE/LINK profile | EDGE, LINK, Code, DB | P1 |
| Telemetry | Time-series measurement payload | `telemetryId` | EDGE/LINK profile | EDGE, LINK, Code, DB, NexusAI | P1 |
| Event | Operational/event signal | `eventId` | UFMS profile | EDGE, LINK, Code, DB, Console, NexusAI | P0 |
| Alarm | Alarm-specific event profile | `alarmId` | UFMS profile | LINK, Code, DB, Console, NexusAI | P0 |
| Evidence | Attachments/proof metadata | `evidenceId` | UFMS profile | Code, DB, Console, NexusAI | P1 |
| Health | Runtime/system health signal | `healthId` | Platform | EDGE, LINK, Code, DB, Console | P0 |
| Throughput | Pipeline throughput metrics | `throughputId` | Platform | LINK, Code, DB, Console, NexusAI | P2 |
| SyncBatch | Batch sync transaction | `syncBatchId` | Platform | LINK, Code, DB | P1 |
| Audit | Audit trail entry | `auditId` | Platform | Code, DB, Console | P1 |
| ConfigVersion | Configuration release snapshot | `configVersionId` | Platform | EDGE, LINK, Code, DB, Console | P0 |

## Notes

- P0 objects are prerequisites for transport and integration baseline.
- P1 objects support richer domain coverage and operations workflows.
- P2 objects are optimization/analytics-oriented and can follow later phases.

## Schema and Example Map

| Object | Schema file | Example file | Owner domain | Consumers | P1 status |
|--------|-------------|--------------|--------------|-----------|-----------|
| Tenant | `schemas/tenant-v1.schema.json` | `dto-examples/canonical/tenant.example.json` | Platform | EDGE, LINK, Code, DB, Console, NexusAI | COMPLETE |
| Site | `schemas/site-v1.schema.json` | `dto-examples/canonical/site.example.json` | Platform | EDGE, LINK, Code, DB, Console, NexusAI | COMPLETE |
| Building | `schemas/building-v1.schema.json` | `dto-examples/canonical/building.example.json` | UFMS profile | Code, DB, Console | COMPLETE |
| Floor | `schemas/floor-v1.schema.json` | `dto-examples/canonical/floor.example.json` | UFMS profile | Code, DB, Console | COMPLETE |
| Space | `schemas/space-v1.schema.json` | `dto-examples/canonical/space.example.json` | UFMS profile | Code, DB, Console, NexusAI | COMPLETE |
| Gateway | `schemas/gateway-v1.schema.json` | `dto-examples/canonical/gateway.example.json` | EDGE/LINK profile | EDGE, LINK, Code, DB | COMPLETE |
| Connector | `schemas/connector-v1.schema.json` | `dto-examples/canonical/connector.example.json` | EDGE/LINK profile | EDGE, LINK, Code, DB, Console | COMPLETE |
| SourceSystem | `schemas/source-system-v1.schema.json` | `dto-examples/canonical/source-system.example.json` | EDGE/LINK profile | EDGE, LINK, Code, DB, Console | COMPLETE |
| Asset | `schemas/asset-v1.schema.json` | `dto-examples/canonical/asset.example.json` | UFMS profile | EDGE, LINK, Code, DB, Console, NexusAI | COMPLETE |
| Device | `schemas/device-v1.schema.json` | `dto-examples/canonical/device.example.json` | EDGE/LINK profile | EDGE, LINK, Code, DB, Console | COMPLETE |
| Point | `schemas/point-v1.schema.json` | `dto-examples/canonical/point.example.json` | EDGE/LINK profile | EDGE, LINK, Code, DB | COMPLETE |
| Telemetry | `schemas/telemetry-v1.schema.json` | `dto-examples/canonical/telemetry.example.json` | EDGE/LINK profile | EDGE, LINK, Code, DB, NexusAI | COMPLETE |
| Event | `schemas/event-v1.schema.json` | `dto-examples/canonical/event.example.json` | UFMS profile | EDGE, LINK, Code, DB, Console, NexusAI | COMPLETE |
| Alarm | `schemas/alarm-v1.schema.json` | `dto-examples/canonical/alarm.example.json` | UFMS profile | LINK, Code, DB, Console, NexusAI | COMPLETE |
| Evidence | `schemas/evidence-v1.schema.json` | `dto-examples/canonical/evidence.example.json` | UFMS profile | Code, DB, Console, NexusAI | COMPLETE |
| Health | `schemas/health-v1.schema.json` | `dto-examples/canonical/health.example.json` | Platform | EDGE, LINK, Code, DB, Console | COMPLETE |
| Throughput | `schemas/throughput-v1.schema.json` | `dto-examples/canonical/throughput.example.json` | Platform | LINK, Code, DB, Console, NexusAI | COMPLETE |
| SyncBatch | `schemas/sync-batch-v1.schema.json` | `dto-examples/canonical/sync-batch.example.json` | Platform | LINK, Code, DB | COMPLETE |
| Audit | `schemas/audit-v1.schema.json` | `dto-examples/canonical/audit.example.json` | Platform | Code, DB, Console | COMPLETE |
| ConfigVersion | `schemas/config-version-v1.schema.json` | `dto-examples/canonical/config-version.example.json` | Platform | EDGE, LINK, Code, DB, Console | COMPLETE |
